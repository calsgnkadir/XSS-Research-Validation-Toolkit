"""Independent E05 textarea parse-tree oracle; no JavaScript execution claim.

The browser inspects actual marker element placement rather than trusting the
scanner's reflection/context labels. All HTTP is a disposable loopback fixture.
"""
from __future__ import annotations

from contextlib import contextmanager
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import sys
import threading
from urllib.parse import parse_qs, urlencode, urlsplit

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "dom-xss-analyzer"))
import dxadyn


@pytest.fixture(scope="module")
def browser_page():
    required = os.environ.get("DXA_REQUIRE_BROWSER") == "1"
    if required:
        from playwright.sync_api import sync_playwright
    else:
        sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    browser_path = os.environ.get("DXA_BROWSER")
    chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if not browser_path and chrome.is_file():
        browser_path = str(chrome)
    with sync_playwright() as pw:
        if not browser_path and not Path(pw.chromium.executable_path).is_file():
            if required:
                pytest.fail("required E05 browser is missing")
            pytest.skip("install Playwright Chromium or set DXA_BROWSER")
        options = {"headless": True}
        if browser_path:
            options["executable_path"] = browser_path
        browser = pw.chromium.launch(**options)
        try:
            context = browser.new_context(service_workers="block", java_script_enabled=False)
            page = context.new_page()
            yield page
        finally:
            browser.close()


@contextmanager
def textarea_reflector():
    class Reflector(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            parsed = urlsplit(self.path)
            if parsed.path not in {"/raw", "/escaped"}:
                self.send_error(404)
                return
            value = parse_qs(parsed.query).get("q", [""])[0]
            if parsed.path == "/escaped":
                value = html.escape(value)
            body = ('<!doctype html><meta charset="utf-8">'
                    '<textarea id="source">' + value + '</textarea>').encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Reflector)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        assert not thread.is_alive()


def test_legacy_families_and_mutations_leave_marker_inert_in_textarea(browser_page, monkeypatch):
    """A whole-registry baseline measures parser coverage, not string diversity."""
    monkeypatch.setattr(dxadyn, "REPORT_EVENTS", [])
    legacy = [name for name in dxadyn.PAYLOAD_VARIANTS if name != "textarea-breakout"]
    generated = list(dxadyn.make_canaries_for(legacy, waf_bypass=True))
    assert generated and len(generated) == len(legacy) * (1 + len(dxadyn._WAF_MUTATIONS))
    # DOMParser creates inert documents: historical event/media-shaped strings
    # cannot execute handlers or load their resources. This measures HTML trees.
    counts = browser_page.evaluate("""values => values.map(value => {
        const doc = new DOMParser().parseFromString(
            '<!doctype html><textarea id="source">' + value + '</textarea>', 'text/html');
        return doc.querySelectorAll('dxss').length;
    })""", [canary for _, _, canary, _ in generated])
    unexpected = [name for (name, _, _, _), count in zip(generated, counts) if count]
    assert unexpected == [], unexpected


@pytest.mark.parametrize("variant,path,expected_nodes", [
    ("textarea-breakout", "/raw", 1),
    ("textarea-breakout", "/escaped", 0),
    ("body", "/raw", 0),
    ("title-breakout", "/raw", 0),
    ("textarea-onfocus-breakout", "/raw", 0),
])
def test_loopback_response_marker_placement(browser_page, variant, path, expected_nodes):
    """Native browser placement is independent of raw-reflection classification."""
    _, cid, canary, _ = next(dxadyn.make_canaries_for([variant]))
    with textarea_reflector() as origin:
        response = browser_page.goto(origin + path + "?" + urlencode({"q": canary}),
                                     wait_until="load", timeout=5000)
        assert response and response.status == 200
        assert browser_page.locator("dxss").count() == expected_nodes
        assert browser_page.locator("#source").count() == 1
        assert cid in browser_page.locator("#source").input_value()
        if expected_nodes:
            assert browser_page.locator("textarea dxss").count() == 0
            assert browser_page.locator("dxss").evaluate("node => node.parentElement.tagName") == "BODY"
        assert browser_page.locator("script, [onerror], [onload], [onfocus]").count() == 0
