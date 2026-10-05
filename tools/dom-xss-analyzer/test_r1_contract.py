"""Acceptance checks for R1; execution and verified auth intentionally unsupported."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import MagicMock

import pytest
import dxa_evidence as evidence
import dxa_attempts
import dxadom
import dxadyn
import dxa
import dxa2dyn


def observation():
    return {"finding_id": "finding-one", "canary_id": "cid-one", "attempt_id": "attempt-one",
            "target": "http://lab.test/submit", "field": "body", "submission_method": "POST",
            "check_url": "http://lab.test/read", "sink_identity": "element:article-1:innerHTML",
            "context": "body", "content_type": "text/html", "session_role": "editor",
            "reflection": "unencoded", "evidence_level": "reflection", "variant": "body"}


@pytest.mark.parametrize("field,value", [
    ("session_role", "admin"), ("sink_identity", "element:article-2:innerHTML"),
    ("check_url", "http://lab.test/other"), ("context", "title"), ("field", "title"),
    ("target", "http://lab.test/other-submit"), ("attempt_id", "attempt-two"),
    ("submission_method", "PUT"), ("evidence_level", "resource-callback"),
])
def test_dedup_preserves_security_relevant_boundaries(field, value):
    a, b = observation(), observation()
    b[field] = value
    assert len(dxadyn.dedupe_findings([a, b])) == 2


def test_exact_group_preserves_raw_observations_and_does_not_mutate():
    a, b = observation(), observation()
    b.update(finding_id="finding-two", check_status=201)
    before = deepcopy([a, b])
    grouped = dxadyn.dedupe_findings([a, b])
    assert len(grouped) == 1
    assert grouped[0]["observations"] == before
    assert grouped[0]["duplicates"] == [b]
    assert [a, b] == before
    assert dxadyn.dedupe_findings(grouped) == grouped


def test_unknown_sink_is_never_assumed_identical():
    a = observation()
    a.pop("sink_identity")
    assert len(dxadyn.dedupe_findings([a, a])) == 2


def test_unknown_role_is_not_assumed_identical():
    a = observation()
    a.pop("session_role")
    assert len(dxadyn.dedupe_findings([a, a])) == 2


@pytest.mark.parametrize("mode", ["--flow", "--auth-flow"])
def test_invalid_flow_input_still_writes_error_report(monkeypatch, tmp_path, mode):
    out, page = tmp_path / "error.json", tmp_path / "error.html"
    monkeypatch.setattr(sys, "argv", ["dxadyn.py", mode, str(tmp_path / "missing.json"),
                                    "--json-out", str(out), "--html", str(page)])
    with pytest.raises(SystemExit) as exc:
        dxadyn.main()
    assert exc.value.code == 2
    document = json.loads(out.read_text())
    assert document["findings"] == []
    assert document["events"][0]["kind"] == "error"
    assert document["events"][0]["event_id"] in page.read_text()


@pytest.mark.parametrize("field,value", [
    ("evidence_level", "execution-confirmed"), ("role_verified", True),
    ("triage", "confirmed-vulnerability"), ("observations", ["untyped"]),
    ("evidence_links", [123]), ("canary_id", 123),
])
def test_contract_rejects_invalid_or_unearned_claims(field, value):
    row = observation()
    row[field] = value
    with pytest.raises(ValueError):
        evidence.normalize(row)


def test_exports_redact_credentials_without_destroying_input(tmp_path, monkeypatch):
    row = observation()
    row.update(target="http://alice:PASSWORD@lab.test/submit?token=QUERYSECRET#FRAGMENT",
               headers={"Authorization": "Bearer HEADERSECRET"}, cookies={"sid": "COOKIESECRET"})
    grouped = dxadyn.dedupe_findings([row, deepcopy(row)])
    event = evidence.ReportEvent("http", "skip", "forbidden", row["target"], 403)
    monkeypatch.setattr(dxadyn, "REPORT_EVENTS", [event])
    path = tmp_path / "report.json"
    dxadyn.write_json_report(path, grouped, "stored")
    page = dxadyn.render_html(grouped, row["target"], "stored")
    serialized = path.read_text(encoding="utf-8")
    for secret in ("PASSWORD", "QUERYSECRET", "FRAGMENT", "HEADERSECRET", "COOKIESECRET"):
        assert secret not in serialized + page
    document = json.loads(serialized)
    assert document["events"][0]["event_id"] in page
    assert document["findings"][0]["finding_id"] in page
    assert len(document["findings"][0]["observations"]) == 2
    assert row["headers"]["Authorization"] == "Bearer HEADERSECRET"


def test_empty_report_retains_network_error_and_rejection(tmp_path, monkeypatch):
    monkeypatch.setattr(dxadyn, "REPORT_EVENTS", [])
    dxadyn.record_response_event("http", "http://lab.test/", None, "TimeoutError")
    dxadyn.record_response_event("http", "http://lab.test/", 401)
    path = tmp_path / "empty.json"
    dxadyn.write_json_report(path, [], "reflected")
    document = json.loads(path.read_text())
    assert document["findings"] == []
    assert {e["kind"] for e in document["events"]} == {"error", "skip"}
    page = dxadyn.render_html([], "local", "reflected")
    assert all(e["event_id"] in page for e in document["events"])


def run_dom_cli(monkeypatch, tmp_path, summary=None, available=True):
    if summary is not None:
        browser = MagicMock()
        browser.__enter__.return_value.visit.return_value = summary
        monkeypatch.setattr(dxadom, "BrowserSession", lambda: browser)
    monkeypatch.setattr(dxadom, "is_available", lambda: (available, "fixture"))
    monkeypatch.setattr(dxadom, "summarize_availability", lambda: "fixture")
    out, page = tmp_path / "dom.json", tmp_path / "dom.html"
    monkeypatch.setattr(sys, "argv", ["dxadyn.py", "http://127.0.0.1/", "--dom",
                                    "--json-out", str(out), "--html", str(page), "--session-role", "editor"])
    with pytest.raises(SystemExit) as exc:
        dxadyn.main()
    return exc.value.code, json.loads(out.read_text()), page.read_text(encoding="utf-8")


def test_dom_adapter_reports_observations_and_errors_without_auth_leak(monkeypatch, tmp_path):
    summary = {"url": "http://127.0.0.1/", "status": 200, "title": "fixture", "body_len": 0,
               "sinks": [{"sink": "innerHTML", "arg": "SINKSECRET"}],
               "dialogs": [{"type": "alert", "message": "DIALOGSECRET"}],
               "auth_headers": {"Authorization": "Bearer AUTHSECRET"},
               "console": [], "errors": ["ERRORSECRET"]}
    code, document, page = run_dom_cli(monkeypatch, tmp_path, summary)
    assert code == 1
    assert {f["evidence_level"] for f in document["findings"]} == {"sink-observed", "candidate"}
    assert all(f["session_role"] == "editor" and not f["role_verified"] for f in document["findings"])
    for secret in ("SINKSECRET", "DIALOGSECRET", "AUTHSECRET", "ERRORSECRET"):
        assert secret not in json.dumps(document) + page
    assert all(f["finding_id"] in page for f in document["findings"])
    assert document["events"][0]["event_id"] in page


def test_dom_unavailable_is_skip_report(monkeypatch, tmp_path):
    code, document, page = run_dom_cli(monkeypatch, tmp_path, available=False)
    assert code == 2
    assert document["events"][0]["kind"] == "skip"
    assert "browser unavailable" in page


def test_journal_and_http_share_contract_and_callback_error_is_separate():
    row = dxa_attempts.candidate("cid", "blind-img", "http://lab.test/", "body", "post")
    row.update(callback_state="query-error", submission_state="error")
    document = dxa_attempts.journal_report([row])
    assert document["findings"][0]["attempt_id"] == row["attempt_id"]
    assert document["findings"][0]["evidence_level"] == "candidate"
    assert {e["stage"] for e in document["events"]} == {"callback", "submission"}
    assert "query-error" in evidence.render_report(document)


def test_real_chrome_bare_dialog_uses_common_report(monkeypatch, tmp_path):
    chrome = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
    if not chrome.exists():
        pytest.skip("explicit local Chrome not available")
    class Page(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b'<div id="x"></div><script>document.getElementById("x").innerHTML="plain";alert("normal dialog")</script>')
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(("127.0.0.1", 0), Page)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setattr(dxadom, "find_chromium_executable", lambda: str(chrome))
    out, page = tmp_path / "chrome.json", tmp_path / "chrome.html"
    monkeypatch.setattr(sys, "argv", ["dxadyn.py", f"http://127.0.0.1:{server.server_port}/", "--dom",
                                    "--json-out", str(out), "--html", str(page)])
    try:
        with pytest.raises(SystemExit) as exc:
            dxadyn.main()
        assert exc.value.code == 0
        document = json.loads(out.read_text())
        assert any(f["severity"] == "observed-dialog" for f in document["findings"])
        assert all(f["evidence_level"] in {"candidate", "sink-observed"} for f in document["findings"])
        assert all(f["finding_id"] in page.read_text() for f in document["findings"])
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_static_cli_common_reports_share_ids_and_keep_candidate(monkeypatch, tmp_path):
    source = tmp_path / "demo.js"
    source.write_text('document.body.innerHTML = location.hash; // SOURCESECRET')
    out, page = tmp_path / "static.json", tmp_path / "static.html"
    monkeypatch.setattr(sys, "argv", ["dxa.py", str(source), "--json-out", str(out), "--html", str(page)])
    with pytest.raises(SystemExit) as exc:
        dxa.main()
    assert exc.value.code == 1
    document = json.loads(out.read_text())
    assert document["findings"]
    assert all(f["evidence_level"] == "candidate" for f in document["findings"])
    assert all(f["finding_id"] in page.read_text() for f in document["findings"])
    assert "SOURCESECRET" not in out.read_text() + page.read_text()


def test_static_missing_input_is_error_not_clean(monkeypatch, tmp_path):
    out = tmp_path / "static.json"
    monkeypatch.setattr(sys, "argv", ["dxa.py", str(tmp_path / "absent"), "--json-out", str(out)])
    with pytest.raises(SystemExit) as exc:
        dxa.main()
    assert exc.value.code == 2
    document = json.loads(out.read_text())
    assert document["findings"] == []
    assert document["events"][0]["kind"] == "error"


def test_static_guided_json_echo_uses_http_evidence(monkeypatch):
    monkeypatch.setattr(dxadyn, "make_canary", lambda: ("dxaC", "dxaC<dXsS>"))
    monkeypatch.setattr(dxadyn, "fetch", lambda *a, **k: (200, "local", 'dxaC<dXsS>', "application/json"))
    row = dxa2dyn.probe_hints("http://lab.test", ["q"])[0]
    assert row["severity"] == "json-only"
    assert row["evidence_level"] == "reflection"
