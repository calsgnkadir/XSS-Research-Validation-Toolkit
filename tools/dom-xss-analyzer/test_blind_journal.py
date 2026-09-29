"""Regression cases for invisible submissions and deferred network evidence."""
import concurrent.futures
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

import dxa_attempts
import dxa_callback
import dxadyn


@pytest.fixture
def callback(monkeypatch):
    server = dxa_callback.CallbackServer(port=0, db_path=":memory:")
    server.start()
    base = f"http://127.0.0.1:{server.port}"
    monkeypatch.setattr(dxadyn, "BLIND_CALLBACK", base)
    try:
        yield server, base
    finally:
        server.stop()


def new_row(cid="dxaONE"):
    return dxa_attempts.candidate(cid, "blind-img", "https://lab.test/submit", "body", "post")


@pytest.mark.parametrize("auto", [False, True])
def test_all_invisible_blind_submits_survive(tmp_path, monkeypatch, callback, auto):
    _, base = callback
    journal = dxa_attempts.AttemptJournal(tmp_path / "attempts.db", base, "editor")
    monkeypatch.setattr(dxadyn, "PARALLEL_WORKERS", 4)
    def submit(*args, **kwargs):
        # The prepared row must already be durable when submission starts.
        assert journal.records()
        return 403, "https://lab.test/"
    monkeypatch.setattr(dxadyn, "_do_submit", submit)
    monkeypatch.setattr(dxadyn, "fetch", lambda url: (200, url, "Nothing reflected", "text/html"))
    probe = dxadyn.probe_stored_auto if auto else dxadyn.probe_stored
    result = probe("https://lab.test/submit", "body", {}, ["https://lab.test/"],
                   variants=list(dxadyn.BLIND_VARIANTS), attempt_journal=journal)
    findings = result[0]
    assert len(findings) == 5
    assert len({r["canary_id"] for r in findings}) == 5
    assert all(r["evidence_level"] == "candidate" for r in findings)
    assert all(r["sub_status"] == 403 for r in findings)
    reopened = dxa_attempts.AttemptJournal(journal.path, base, existing=True)
    assert len(reopened.records(journal.run_id)) == 5
    assert all(r["session_role"] == "editor" for r in reopened.records())
    assert "candidate" in dxadyn.render_html(findings, "local", "stored", {})


def test_submit_exception_is_durable(tmp_path, monkeypatch, callback):
    _, base = callback
    journal = dxa_attempts.AttemptJournal(tmp_path / "attempts.db", base)
    def fail(*args, **kwargs):
        raise OSError("request failed")
    monkeypatch.setattr(dxadyn, "_do_submit", fail)
    with pytest.raises(OSError):
        dxadyn.probe_stored("https://lab.test", "body", {}, [],
                            variants=["blind-img"], attempt_journal=journal)
    assert journal.records()[0]["submission_state"] == "error"


def test_live_invisible_callback_is_also_persistent(tmp_path, monkeypatch, callback):
    server, base = callback
    journal = dxa_attempts.AttemptJournal(tmp_path / "attempts.db", base)
    def submit(*args, **kwargs):
        row = journal.records()[0]
        server.db.record(row["canary_id"], "GET", "/c/" + row["canary_id"],
                         None, None, None, None)
        return 200, "https://lab.test/"
    monkeypatch.setattr(dxadyn, "_do_submit", submit)
    findings, _ = dxadyn.probe_stored("https://lab.test", "body", {}, [],
                                     variants=["blind-img"], attempt_journal=journal)
    count, findings = dxadyn.correlate_blind_findings(findings, timeout=1,
                                                    attempt_journal=journal)
    assert count == 1
    assert findings[0]["evidence_level"] == "resource-callback"
    assert journal.records()[0]["evidence_level"] == "resource-callback"


def test_malformed_callback_response_is_error(tmp_path, monkeypatch):
    import io
    journal = dxa_attempts.AttemptJournal(tmp_path / "attempts.db", "http://localhost:9999")
    journal.begin(new_row())
    monkeypatch.setattr(dxa_attempts.urllib.request, "urlopen",
                        lambda *a, **k: io.StringIO('{"hits": "invalid"}'))
    assert journal.reconcile()[0]["callback_state"] == "query-error"


def test_reports_escape_operator_metadata():
    row = new_row()
    row["session_role"] = "<script>alert(1)</script>"
    report = dxa_attempts.render_report([row])
    assert "<script>" not in report
    assert "&lt;script&gt;" in report


def test_cli_rejects_output_overwriting_journal(tmp_path):
    path = tmp_path / "attempts.db"
    journal = dxa_attempts.AttemptJournal(path, "http://localhost:9999")
    journal.begin(new_row())
    with pytest.raises(SystemExit) as exc:
        dxa_attempts.main(["--journal", str(path), "--blind-callback", journal.callback,
                           "--json-out", str(path)])
    assert exc.value.code == 2
    assert len(journal.records()) == 1


def test_deferred_callback_is_network_evidence_and_idempotent(tmp_path, callback):
    server, base = callback
    journal = dxa_attempts.AttemptJournal(tmp_path / "attempts.db", base)
    row = new_row()
    journal.begin(row)
    assert journal.reconcile()[0]["callback_state"] == "no-hit"
    server.db.record(row["canary_id"], "GET", "/c/dxaONE", user_agent="test",
                     remote_ip="127.0.0.1", referer=None, body_preview="secret")
    for _ in range(2):
        records = journal.reconcile()
        assert len(records) == 1
        assert records[0]["evidence_level"] == "resource-callback"
        assert records[0]["callback_state"] == "matched"
        assert "secret" not in json.dumps(records)
        assert "execution-confirmed" not in json.dumps(records)


def test_query_error_preserves_earlier_evidence(tmp_path, monkeypatch, callback):
    server, base = callback
    journal = dxa_attempts.AttemptJournal(tmp_path / "attempts.db", base)
    journal.begin(new_row())
    server.db.record("dxaONE", "GET", "/c/dxaONE", None, None, None, None)
    assert journal.reconcile()[0]["evidence_level"] == "resource-callback"
    def fail(*args, **kwargs):
        raise OSError("offline")
    monkeypatch.setattr(dxa_attempts.urllib.request, "urlopen", fail)
    record = journal.reconcile()[0]
    assert record["callback_state"] == "query-error"
    assert record["evidence_level"] == "resource-callback"


@pytest.mark.parametrize("hit", [
    {"cid": "wrong", "ts": time.time()},
    {"cid": "dxaONE", "ts": 1},
    {"cid": "dxaONE", "ts": float("inf")},
])
def test_wrong_or_stale_hit_is_not_correlated(tmp_path, monkeypatch, hit):
    import io
    journal = dxa_attempts.AttemptJournal(tmp_path / "attempts.db", "http://localhost:9999")
    journal.begin(new_row())
    monkeypatch.setattr(dxa_attempts.urllib.request, "urlopen",
                        lambda *a, **k: io.StringIO(json.dumps({"hits": [hit]})))
    assert journal.reconcile()[0]["evidence_level"] == "candidate"


def test_parallel_unique_records_and_private_url(tmp_path):
    journal = dxa_attempts.AttemptJournal(tmp_path / "attempts.db", "http://localhost:9999")
    def insert(i):
        row = dxa_attempts.candidate(f"dxa{i}", "blind-img",
                                    "http://user:password@lab.test/post?token=SECRET#PRIVATE",
                                    "body", "post")
        journal.begin(row)
        journal.submission(row, 201, "response-received")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(insert, range(30)))
    records = journal.records()
    assert len(records) == 30
    assert not any(s in json.dumps(records) for s in ("password", "SECRET", "PRIVATE"))
    with pytest.raises(sqlite3.IntegrityError):
        journal.begin(new_row("dxa0"))
    assert journal.records("other-run") == []
    other = dxa_attempts.AttemptJournal(journal.path, "http://localhost:9998", existing=True)
    assert other.records() == []


@pytest.mark.parametrize("url", ["file:///tmp/a", "https://u:p@lab.test", "https://lab.test?key=secret"])
def test_callback_rejects_credentials_or_invalid_endpoint(tmp_path, url):
    with pytest.raises(ValueError):
        dxa_attempts.AttemptJournal(tmp_path / "attempts.db", url)


def test_missing_journal_does_not_create_empty_success(tmp_path):
    path = tmp_path / "missing.db"
    with pytest.raises(ValueError):
        dxa_attempts.AttemptJournal(path, "http://localhost", existing=True)
    assert not path.exists()


def test_cli_survives_process_exit_without_resubmitting(tmp_path, callback):
    server, base = callback
    class Target(BaseHTTPRequestHandler):
        posts = 0
        def do_POST(self):
            Target.posts += 1
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self.do_GET()
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"No reflection")
        def log_message(self, *args):
            pass
    target = ThreadingHTTPServer(("127.0.0.1", 0), Target)
    thread = threading.Thread(target=target.serve_forever, daemon=True)
    thread.start()
    here = Path(__file__).parent
    path = tmp_path / "attempts.db"
    url = f"http://127.0.0.1:{target.server_port}/"
    try:
        scan = subprocess.run([sys.executable, str(here / "dxadyn.py"), "--stored",
                               "--target", url, "--target-field", "body", "--check", url,
                               "--csrf-field", "", "--variants", "blind-img",
                               "--blind-callback", base, "--blind-journal", str(path)],
                              capture_output=True, text=True, timeout=30)
        assert scan.returncode == 0, scan.stdout + scan.stderr
        journal = dxa_attempts.AttemptJournal(path, base, existing=True)
        row = journal.records()[0]
        with dxa_attempts.urllib.request.urlopen(base + "/c/" + row["canary_id"], timeout=2) as response:
            assert response.status == 200
        report, page = tmp_path / "result.json", tmp_path / "result.html"
        reconcile = subprocess.run([sys.executable, str(here / "dxa_attempts.py"),
                                    "--journal", str(path), "--blind-callback", base,
                                    "--json-out", str(report), "--html", str(page)],
                                   capture_output=True, text=True, timeout=30)
        assert reconcile.returncode == 0, reconcile.stderr
        observed = json.loads(report.read_text())["attempts"][0]
        assert observed["attempt_id"] == row["attempt_id"]
        assert observed["evidence_level"] == "resource-callback"
        assert observed["attempt_id"] in page.read_text()
        assert Target.posts == 1
    finally:
        target.shutdown()
        target.server_close()
        thread.join(timeout=5)
