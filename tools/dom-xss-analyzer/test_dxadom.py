"""Phase 2.1: browser harness tests. Every test that needs a real
browser skips gracefully when playwright + chromium aren't available,
so this file is safe to include in CI that hasn't installed the
optional browser extra.
"""
from __future__ import annotations
import http.server
import pathlib
import sys
import threading
from unittest import mock

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import dxadom  # noqa: E402


# --- unit tests: availability + binary discovery ---------------------------
#
# These do NOT require a real browser install and always run.

def test_find_chromium_executable_returns_path_or_none():
    """Never raises, always returns str or None."""
    result = dxadom.find_chromium_executable()
    assert result is None or isinstance(result, str)


def test_find_chromium_executable_skips_missing_hints(monkeypatch):
    """If none of the hint paths exist, function returns None cleanly."""
    monkeypatch.setattr(dxadom, "_CHROMIUM_HINTS",
                        ["/does/not/exist/*/chrome"])
    assert dxadom.find_chromium_executable() is None


def test_find_chromium_executable_prefers_newest_version(tmp_path, monkeypatch):
    """When multiple versioned dirs exist, glob-sort picks the highest."""
    (tmp_path / "chromium-1000" / "chrome-linux").mkdir(parents=True)
    (tmp_path / "chromium-2000" / "chrome-linux").mkdir(parents=True)
    old = tmp_path / "chromium-1000" / "chrome-linux" / "chrome"
    new = tmp_path / "chromium-2000" / "chrome-linux" / "chrome"
    old.write_text("old")
    new.write_text("new")
    monkeypatch.setattr(dxadom, "_CHROMIUM_HINTS",
                        [str(tmp_path / "chromium-*" / "chrome-linux" / "chrome")])
    assert dxadom.find_chromium_executable() == str(new)


def test_is_available_returns_tuple():
    """(ok: bool, reason: str) - reason is non-empty either way."""
    ok, reason = dxadom.is_available()
    assert isinstance(ok, bool)
    assert isinstance(reason, str) and reason


def test_is_available_reports_missing_playwright(monkeypatch):
    """When playwright import fails, is_available says so with a hint."""
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) \
        else __builtins__.__import__

    def _fail(name, *args, **kwargs):
        if name == "playwright":
            raise ImportError("no playwright here")
        return real_import(name, *args, **kwargs)

    with mock.patch("builtins.__import__", side_effect=_fail):
        ok, reason = dxadom.is_available()
    assert ok is False
    assert "playwright" in reason.lower()


def test_is_available_reports_missing_chromium(monkeypatch):
    """When playwright is installed but no chromium binary is found on
    disk, is_available flags it with an install hint."""
    monkeypatch.setattr(dxadom, "find_chromium_executable", lambda: None)
    ok, reason = dxadom.is_available()
    assert ok is False
    assert "chromium" in reason.lower()


def test_summarize_availability_prefix():
    """Startup line begins with either 'OK' or 'UNAVAILABLE' - stable
    prefix so shell wrappers can grep."""
    line = dxadom.summarize_availability()
    assert line.startswith("[dxadom] OK") or line.startswith("[dxadom] UNAVAILABLE")


# --- real-browser tests: skip gracefully when unavailable ------------------

_real_available, _real_reason = dxadom.is_available()
_skip = pytest.mark.skipif(not _real_available, reason=_real_reason)


class _StaticHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    _PAGES = {
        "/hello": ('<html><head><title>hi from test</title></head>'
                   '<body><h1>hello</h1></body></html>'),
        "/console-log": ('<html><body>'
                         '<script>console.log("marker-123")</script>'
                         '</body></html>'),
        "/pageerror": ('<html><body>'
                       '<script>throw new Error("boom-in-page")</script>'
                       '</body></html>'),
    }

    def do_GET(self):
        body = self._PAGES.get(self.path, "<html>404</html>")
        payload = body.encode()
        self.send_response(200 if self.path in self._PAGES else 404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


@pytest.fixture
def static_server():
    httpd = http.server.HTTPServer(("127.0.0.1", 0), _StaticHandler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


@_skip
def test_browser_session_visits_a_page(static_server):
    port = static_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/hello")
    assert summary["status"] == 200
    assert summary["title"] == "hi from test"
    assert summary["body_len"] > 0
    assert summary["errors"] == []


@_skip
def test_browser_session_captures_console_log(static_server):
    port = static_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/console-log")
    joined = " ".join(summary["console"])
    assert "marker-123" in joined


@_skip
def test_browser_session_captures_page_error(static_server):
    """A page that throws surfaces via `errors`, not `console`."""
    port = static_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/pageerror")
    joined = " ".join(summary["errors"])
    assert "boom-in-page" in joined


@_skip
def test_browser_session_records_unreachable_target():
    """A dead URL sets an error entry, not an exception."""
    with dxadom.BrowserSession() as sess:
        summary = sess.visit("http://127.0.0.1:1/does-not-exist")
    assert summary["errors"]
    assert summary["status"] in (None, 0)


@_skip
def test_browser_session_reuses_browser_across_visits(static_server):
    """Two visit() calls under one context share the browser - each
    creates its own page (state isolation) but the browser process
    isn't relaunched. Measured indirectly: both calls succeed and
    the second one has independent console state."""
    port = static_server
    with dxadom.BrowserSession() as sess:
        a = sess.visit(f"http://127.0.0.1:{port}/console-log")
        b = sess.visit(f"http://127.0.0.1:{port}/hello")
    assert " ".join(a["console"]).find("marker-123") >= 0
    # /hello does NOT have console.log so console shouldn't inherit
    # /console-log's messages - state must be per-page, not per-session.
    assert " ".join(b["console"]).find("marker-123") < 0
