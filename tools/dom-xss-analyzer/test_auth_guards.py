"""R2 negative auth controls against a loopback HTTP fixture."""
import http.cookiejar
import http.server
import json
import threading
import urllib.request

import pytest
import dxadyn


@pytest.fixture
def auth_server(monkeypatch):
    calls = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            calls.append(self.path)
            status = int(self.path[1:]) if self.path[1:].isdigit() else 200
            token = {"/null": None, "/empty": "", "/space": " ",
                     "/object": {}, "/list": [], "/bool": False}.get(self.path, "valid-token")
            body = json.dumps({} if self.path == "/missing" else {"token": token}).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            if self.path == "/cookie":
                self.send_header("Set-Cookie", "session=new; Path=/")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    jar = http.cookiejar.CookieJar()
    monkeypatch.setattr(dxadyn, "OPENER", urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar)))
    monkeypatch.setattr(dxadyn, "EXTRA_HEADERS", {})
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", calls
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def flow(base, path):
    return {"steps": [{"url": base + path, "save": {"token": "$.token"}}],
            "auth": {"header": "Authorization", "value": "Bearer {token}"}}


@pytest.mark.parametrize("status", [401, 403, 429, 500])
def test_auth_error_stops_before_later_steps_and_header(auth_server, status):
    base, calls = auth_server
    spec = flow(base, f"/{status}")
    spec["steps"].append({"url": base + "/should-not-run"})
    result = dxadyn.run_auth_flow(spec)
    assert not result["authenticated"] and result["error"]
    assert calls == [f"/{status}"]
    assert "Authorization" not in dxadyn.EXTRA_HEADERS


@pytest.mark.parametrize("path", ["/missing", "/null", "/empty", "/space", "/object", "/list", "/bool"])
def test_invalid_extracted_token_is_not_installed(auth_server, path):
    base, _ = auth_server
    result = dxadyn.run_auth_flow(flow(base, path))
    assert not result["authenticated"] and result["error"]
    assert result["auth_header"] is None
    assert "Authorization" not in dxadyn.EXTRA_HEADERS


def test_existing_cookie_does_not_prove_new_login(auth_server):
    base, _ = auth_server
    assert dxadyn.run_auth_flow({"steps": [{"url": base + "/cookie"}]})["authenticated"]
    result = dxadyn.run_auth_flow({"steps": [{"url": base + "/ok"}]})
    assert not result["authenticated"] and result["error"]


@pytest.mark.parametrize("status", [401, 403])
def test_form_error_redirect_is_not_success(monkeypatch, status):
    responses = iter([(200, "http://local/login", "", "text/html"),
                      (status, "http://local/error", "", "text/html")])
    monkeypatch.setattr(dxadyn, "fetch", lambda *a, **kw: next(responses))
    assert not dxadyn.login("http://local/login", "user", "bad", csrf_field=None)


def test_failed_form_login_stops_cli_with_error_report(monkeypatch, tmp_path):
    import sys
    report = tmp_path / "failure.json"
    monkeypatch.setattr(sys, "argv", ["dxadyn", "--login", "http://local/login",
                        "--user", "u", "--pass", "p", "http://local/?q=x",
                        "--json-out", str(report)])
    monkeypatch.setattr(dxadyn, "login", lambda *a, **kw: False)
    with pytest.raises(SystemExit) as exc:
        dxadyn.main()
    assert exc.value.code == 2
    data = json.loads(report.read_text())
    assert data["findings"] == []
    assert data["events"]
