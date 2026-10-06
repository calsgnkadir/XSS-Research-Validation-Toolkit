"""R2 acceptance: session identity, fractional rate, rotating single-use CSRF."""
import concurrent.futures
import http.server
import json
import threading
import time
import urllib.parse

import pytest
import dxadyn


@pytest.fixture(autouse=True)
def isolated(monkeypatch):
    for name, value in {"OPENER": dxadyn._opener(), "EXTRA_HEADERS": {},
                        "CSRF_REFRESH_URL": "", "CSRF_HEADER_NAME": "",
                        "REPORT_EVENTS": [], "_RATE_LIMITER": None,
                        "SESSION_CHECK": "not-requested", "SESSION_ROLE": "reader",
                        "PARALLEL_WORKERS": 4}.items():
        monkeypatch.setattr(dxadyn, name, value)


def test_fractional_rate_progresses_with_fake_clock(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(dxadyn.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(dxadyn.time, "sleep", lambda delay: clock.__setitem__(0, clock[0] + delay))
    bucket = dxadyn._TokenBucket(0.5)
    bucket.take()
    bucket.take()
    assert clock[0] == pytest.approx(2)


@pytest.mark.parametrize("rate", [0, -1, float("nan"), float("inf")])
def test_bucket_rejects_invalid_rate(rate):
    with pytest.raises(ValueError):
        dxadyn._TokenBucket(rate)


@pytest.fixture
def site():
    state = {"token": 0, "used": False, "value": "", "posts": 0, "order": []}

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, body, ct="text/html"):
            self.send_response(status)
            self.send_header("Content-Type", ct)
            self.end_headers()
            self.wfile.write(body.encode())

        def do_GET(self):
            if self.path == "/protected":
                if self.headers.get("Authorization") != "Bearer valid":
                    return self.reply(401, "login required")
                return self.reply(200, '{"user":"alice","role":"reader"}', "application/json")
            if self.path == "/token":
                return self.reply(200, '{"token":"valid"}', "application/json")
            if self.path == "/me":
                return self.reply(200, '{"user":"alice","role":"reader"}', "application/json")
            if self.path == "/login":
                return self.reply(200, "login form")
            if self.path in ("/401", "/403", "/429", "/500"):
                return self.reply(int(self.path[1:]), "blocked")
            if self.path == "/form":
                state["token"] += 1
                state["used"] = False
                return self.reply(200, f'<input name="tokenCSRF" value="{state["token"]}">')
            state["order"].append("read")
            self.reply(200, state["value"])

        def do_POST(self):
            fields = urllib.parse.parse_qs(self.rfile.read(int(self.headers["Content-Length"])).decode())
            token = self.headers.get("X-CSRF") or fields.get("tokenCSRF", [""])[0]
            if token != str(state["token"]) or state["used"]:
                return self.reply(403, "stale")
            state["used"] = True
            state["posts"] += 1
            state["order"].append("submit")
            state["value"] = fields.get("q", [""])[0]
            self.reply(200, "saved")

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", state
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.parametrize("path,expect,passed", [
    ("/me", {"$.user": "alice", "$.role": "reader"}, True),
    ("/me", {"$.user": "bob"}, False),
    ("/me", {"$.role": "admin"}, False),
    ("/me", {"$.missing": "reader"}, False),
    ("/login", {"$.user": "alice"}, False),
    ("/401", {"$.user": "alice"}, False),
])
def test_target_session_contract(site, path, expect, passed, tmp_path):
    base, _ = site
    assert dxadyn.verify_session({"url": base + path, "expect": expect}) is passed
    report = tmp_path / "report.json"
    dxadyn.write_json_report(report, [], "auth-check")
    data = json.loads(report.read_text())
    assert data["meta"]["session_check"] == ("passed" if passed else "failed")
    assert data["meta"]["session_role"] == "reader"
    assert "alice" not in report.read_text()
    assert bool(data["events"]) is (not passed)


def test_parallel_single_use_header_refresh_submit(site, monkeypatch):
    base, state = site
    monkeypatch.setattr(dxadyn, "CSRF_REFRESH_URL", base + "/form")
    monkeypatch.setattr(dxadyn, "CSRF_HEADER_NAME", "X-CSRF")
    original = dxadyn.refresh_csrf_token
    def refresh(*args):
        token = original(*args)
        time.sleep(0.01)  # expose refresh/submit interleaving without the transaction lock
        return token
    monkeypatch.setattr(dxadyn, "refresh_csrf_token", refresh)
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        results = list(pool.map(lambda i: dxadyn.fetch(base + "/form", data={"q": str(i)})[0], range(8)))
    assert results == [200] * 8
    assert state["posts"] == 8


@pytest.mark.parametrize("auto", [False, True])
def test_stored_submit_read_preserves_each_overwritten_canary(site, auto):
    base, state = site
    probe = dxadyn.probe_stored_auto if auto else dxadyn.probe_stored
    result = probe(base + "/form", "q", {}, [base + "/view"], variants=["body", "title-breakout"])
    assert state["posts"] == 2
    assert len({row["canary_id"] for row in result[0]}) == 2
    order = state["order"]
    submits = [i for i, value in enumerate(order) if value == "submit"]
    assert "read" in order[submits[0] + 1:submits[1]]


def test_missing_csrf_stops_submission(site, monkeypatch):
    base, state = site
    monkeypatch.setattr(dxadyn, "CSRF_REFRESH_URL", base + "/login")
    monkeypatch.setattr(dxadyn, "CSRF_HEADER_NAME", "X-CSRF")
    assert dxadyn.fetch(base + "/form", data={"q": "x"})[0] is None
    assert state["posts"] == 0
    assert any(e.reason == "csrf-token-unavailable" for e in dxadyn.REPORT_EVENTS)


@pytest.mark.parametrize("status", [401, 403, 429, 500])
def test_http_rejection_is_reported_separately(site, status):
    base, _ = site
    dxadyn.fetch(base + f"/{status}")
    assert dxadyn.REPORT_EVENTS[-1].status == status


def test_timeout_is_error_event(monkeypatch):
    def timeout(*a, **kw):
        raise TimeoutError("private-token")
    monkeypatch.setattr(dxadyn.OPENER, "open", timeout)
    assert dxadyn.fetch("http://local/")[0] is None
    assert dxadyn.REPORT_EVENTS[-1].reason == "TimeoutError"


def test_auth_flow_then_target_identity_check(site):
    base, _ = site
    spec = {"url": base + "/protected", "expect": {"$.user": "alice", "$.role": "reader"}}
    assert not dxadyn.verify_session(spec)
    auth = dxadyn.run_auth_flow({"steps": [{"url": base + "/token", "save": {"token": "$.token"}}],
                                "auth": {"header": "Authorization", "value": "Bearer {token}"}})
    assert auth["authenticated"]
    assert dxadyn.verify_session(spec)


def test_flow_uses_single_use_csrf_header(site, monkeypatch):
    base, state = site
    monkeypatch.setattr(dxadyn, "CSRF_REFRESH_URL", base + "/form")
    monkeypatch.setattr(dxadyn, "CSRF_HEADER_NAME", "X-CSRF")
    result = dxadyn.run_flow({"steps": [{"url": base + "/form", "method": "POST", "body": {"q": "test"}}] * 2})
    assert not result["error"]
    assert state["posts"] == 2


def test_explicit_form_csrf_missing_is_reported(site):
    base, state = site
    status, _ = dxadyn._submit_form(base + "/login", "q", {}, "test")
    assert status is None and state["posts"] == 0
    assert dxadyn.REPORT_EVENTS[-1].reason == "csrf-token-unavailable"


@pytest.mark.parametrize("rate", ["-1", "nan", "inf"])
def test_cli_rejects_invalid_rate(monkeypatch, rate):
    import sys
    monkeypatch.setattr(sys, "argv", ["dxadyn", "--rate", rate])
    with pytest.raises(SystemExit) as exc:
        dxadyn.main()
    assert exc.value.code == 2


def test_cli_zero_rate_means_unlimited(monkeypatch):
    import sys
    monkeypatch.setattr(sys, "argv", ["dxadyn", "--rate", "0"])
    try:
        dxadyn.main()
    except SystemExit:
        pass
    assert dxadyn._RATE_LIMITER is None


def test_cli_failed_session_check_stops_scan(site, tmp_path, monkeypatch):
    import sys
    base, state = site
    config, report = tmp_path / "check.json", tmp_path / "report.json"
    config.write_text(json.dumps({"url": base + "/protected", "expect": {"$.user": "alice"}}))
    monkeypatch.setattr(sys, "argv", ["dxadyn", base + "/form", "--auth-check", str(config), "--json-out", str(report)])
    with pytest.raises(SystemExit) as exc:
        dxadyn.main()
    assert exc.value.code == 2
    assert state["token"] == 0 and state["posts"] == 0
    data = json.loads(report.read_text())
    assert data["meta"]["session_check"] == "failed"
    assert data["events"] and data["findings"] == []


@pytest.mark.parametrize("args", [
    ["--dom", "--auth-check", "check.json"],
    ["--stored", "--csrf-header", "X-CSRF", "--csrf-refresh", "http://local/form"],
])
def test_cli_rejects_unsupported_session_combinations(monkeypatch, args):
    import sys
    monkeypatch.setattr(sys, "argv", ["dxadyn"] + args)
    with pytest.raises(SystemExit) as exc:
        dxadyn.main()
    assert exc.value.code == 2
