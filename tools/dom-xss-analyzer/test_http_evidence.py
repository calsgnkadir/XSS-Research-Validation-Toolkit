"""Response evidence must agree across HTTP modes and never assert execution."""
import json
from pathlib import Path
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

import pytest
import dxadyn


@pytest.mark.parametrize("content_type,expected", [
    ("text/html", "html-reflection"),
    ("Text/HTML; charset=UTF-8", "html-reflection"),
    ("application/json", "json-only"),
    ("Application/Problem+JSON; charset=utf-8", "json-only"),
    ("text/plain", "non-html-reflection"),
    ("text/xml", "non-html-reflection"),
    ("", "unknown-type-reflection"),
])
def test_identical_response_has_identical_evidence_in_all_http_modes(monkeypatch, content_type, expected):
    cid, marker = "dxaFIXED", "<dXsS>"
    canary = cid + marker
    body = '<title>' + canary + '</title>'
    monkeypatch.setattr(dxadyn, "make_canaries_for", lambda *a, **k: iter([("body", cid, canary, marker)]))
    monkeypatch.setattr(dxadyn, "fetch", lambda url, **kwargs: (200, url, body, content_type))
    monkeypatch.setattr(dxadyn, "_do_submit", lambda *a, **k: (201, "http://lab.test/"))
    monkeypatch.setattr(dxadyn, "_fetch_flow_step", lambda *a, **k: (200, body, content_type, None))
    reflected = dxadyn.probe_link("http://lab.test/?q=value")[0]
    stored = dxadyn.probe_stored("http://lab.test/", "q", {}, ["http://lab.test/"])[0][0]
    auto = dxadyn.probe_stored_auto("http://lab.test/", "q", {}, ["http://lab.test/"])[0][0]
    header = dxadyn.probe_headers("http://lab.test/", ["X-Test"])[0]
    flow = dxadyn.run_flow({"steps": [{"url": "http://lab.test/", "verdict": True}]},
                           cid=cid, canary=canary, marker=marker)["verdicts"][0]
    findings = [reflected, stored, auto, header, flow]
    assert len({row["finding_id"] for row in findings}) == 5
    for row in findings:
        assert row["severity"] == expected
        assert row["evidence_level"] == "reflection"
        assert row["triage"] == "unreviewed"
        assert row["schema_version"] == 1
        assert row["content_type"] == content_type
        assert row["context"] == reflected["context"]
    report = dxadyn.render_html(findings, "http://lab.test/", "test")
    assert "EXECUTABLE" not in report
    assert "runs as-is" not in report
    assert "<th>evidence</th>" in report


@pytest.mark.parametrize("variant,body", [
    ("title-breakout", '<textarea>{canary}</textarea>'),
    ("attr-breakout", "<div title='{canary}'>text</div>"),
    ("script-breakout", '<!-- {canary} -->'),
])
def test_marker_in_wrong_context_does_not_prove_escape(variant, body):
    cid, canary = dxadyn.make_canary(variant)
    marker = dxadyn.PAYLOAD_VARIANTS[variant][1]
    response = body.format(canary=canary)
    verdict = dxadyn.verdict(cid, response, marker)
    assert verdict == "unencoded"  # Negative control: raw marker genuinely exists.
    finding = dxadyn._finding("http://lab.test/", "GET", "q", verdict, 200,
                              dxadyn.find_context(cid, response), cid, "text/html", variant)
    assert finding["severity"] == "html-reflection"
    assert finding["evidence_level"] == "reflection"


def test_encoded_flow_is_not_reflection_evidence(monkeypatch):
    monkeypatch.setattr(dxadyn, "_fetch_flow_step",
                        lambda *a, **k: (200, "dxaFIXED&lt;dXsS&gt;", "text/html", None))
    finding = dxadyn.run_flow({"steps": [{"url": "http://lab.test/", "verdict": True}]},
                              cid="dxaFIXED", canary="dxaFIXED<dXsS>", marker="<dXsS>")["verdicts"][0]
    assert finding["evidence_level"] == "candidate"
    assert finding["confidence"] == "none"


def test_flow_cli_json_echo_never_prints_executable(tmp_path):
    class Echo(BaseHTTPRequestHandler):
        def do_POST(self):
            data = parse_qs(self.rfile.read(int(self.headers["Content-Length"])).decode())
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"echo": data["q"][0]}).encode())
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(("127.0.0.1", 0), Echo)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    spec = tmp_path / "flow.json"
    spec.write_text(json.dumps({"steps": [{"url": f"http://127.0.0.1:{server.server_port}/",
                                          "method": "POST", "body": {"q": "{CANARY}"},
                                          "verdict": True}]}))
    try:
        report, page = tmp_path / "result.json", tmp_path / "result.html"
        result = subprocess.run([sys.executable, str(Path(dxadyn.__file__)), "--flow", str(spec),
                                 "--json-out", str(report), "--html", str(page)],
                                capture_output=True, text=True, timeout=20)
        assert result.returncode == 0, result.stderr
        assert "[JSON-ONLY]" in result.stdout
        assert "EXECUTABLE" not in result.stdout
        assert "evidence=reflection" in result.stdout
        record = json.loads(report.read_text(encoding="utf-8"))["findings"][0]
        assert record["severity"] == "json-only"
        assert record["evidence_level"] == "reflection"
        assert "JSON-ONLY" in page.read_text(encoding="utf-8")
        assert record["finding_id"] in page.read_text(encoding="utf-8")
        assert "EXECUTABLE" not in page.read_text(encoding="utf-8")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
