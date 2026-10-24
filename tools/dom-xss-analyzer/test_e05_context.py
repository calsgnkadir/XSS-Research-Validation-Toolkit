"""E05 textarea marker transport; browser parser reach has an independent QA oracle.

The new probe is inert. A returned closing tag remains HTTP reflection evidence,
even when the independent browser test observes a marker element outside RCDATA.
"""

import html
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import pytest

import dxadyn


VARIANT = "textarea-breakout"


def test_textarea_probe_does_not_silently_fall_back_to_body():
    cid, canary = dxadyn.make_canary(VARIANT)
    # make_canary accepts unknown names by falling back to body; exercise the
    # production generator rather than just checking registry membership.
    assert canary == cid + "</textarea><dXsS>"
    assert dxadyn.PAYLOAD_VARIANTS[VARIANT][1] == "</textarea><dXsS>"


def test_textarea_mutations_preserve_cid_and_close_tag_marker_pair():
    rows = list(dxadyn.make_canaries_for([VARIANT], waf_bypass=True))
    assert rows[0][0] == VARIANT
    assert len({cid for _, cid, _, _ in rows}) == len(rows)
    for name, cid, canary, marker in rows:
        assert name.split("/", 1)[0] == VARIANT
        assert canary.startswith(cid + "</textarea>")
        assert marker.startswith("</textarea>")
        assert dxadyn.verdict(cid, "<textarea>" + canary + "</textarea>", marker) == "unencoded"
        assert dxadyn.verdict(cid, "<textarea>" + html.escape(canary) + "</textarea>", marker) == "encoded"


@pytest.fixture
def textarea_reflector(monkeypatch):
    """One raw and one escaped textarea; only synthetic values on loopback."""
    seen = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            request = urlsplit(self.path)
            value = parse_qs(request.query).get("q", [""])[0]
            seen.append((request.path, value))
            returned = html.escape(value) if request.path == "/escaped" else value
            body = ("<!doctype html><textarea id=field>" + returned + "</textarea>").encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    monkeypatch.setattr(dxadyn, "OPENER", dxadyn._opener())
    monkeypatch.setattr(dxadyn, "EXTRA_HEADERS", {})
    thread.start()
    try:
        yield "http://127.0.0.1:" + str(server.server_port), seen
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        assert not thread.is_alive()


def test_textarea_probe_over_http_keeps_reflection_semantics(textarea_reflector):
    origin, seen = textarea_reflector
    raw = dxadyn.probe_link(origin + "/raw?q=seed", variants=[VARIANT])
    escaped = dxadyn.probe_link(origin + "/escaped?q=seed", variants=[VARIANT])
    assert len(raw) == 1
    assert escaped == []
    row = raw[0]
    assert row["variant"] == VARIANT
    assert row["context"] == "textarea"  # CID precedes the close tag.
    assert row["reflection"] == "unencoded"
    assert row["severity"] == "html-reflection"
    assert row["evidence_level"] == "reflection"
    assert row["triage"] == "unreviewed"
    assert [path for path, _ in seen] == ["/raw", "/escaped"]
    assert all(value.endswith("</textarea><dXsS>") for _, value in seen)
    rendered = dxadyn.render_html(raw, origin, "E05 textarea marker")
    assert "execution-confirmed" not in rendered
    assert "EXECUTABLE" not in rendered


@pytest.mark.parametrize("content_type,context,severity", [
    ("text/html", "textarea", "html-reflection"),
    ("application/json", "json-body", "json-only"),
    ("text/plain", "response-body", "non-html-reflection"),
])
def test_textarea_variant_does_not_upgrade_response_evidence(content_type, context, severity):
    cid, canary = dxadyn.make_canary(VARIANT)
    body = "<textarea>" + canary + "</textarea>"
    marker = dxadyn.PAYLOAD_VARIANTS[VARIANT][1]
    row = dxadyn._finding("http://127.0.0.1/", "GET", "q",
                          dxadyn.verdict(cid, body, marker), 200,
                          dxadyn.find_context(cid, body), cid, content_type, VARIANT)
    assert row["context"] == context
    assert row["severity"] == severity
    assert row["evidence_level"] == "reflection"
    assert row["triage"] == "unreviewed"
