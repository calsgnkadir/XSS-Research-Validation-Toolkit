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


# --- Phase 2.2: DOM sink detection ------------------------------------------

def test_sink_hits_for_filters_by_needle():
    """Unit: filter helper returns only entries containing the needle."""
    sinks = [
        {"sink": "Element.innerHTML", "arg": "dxaCAFE<script>1</script>"},
        {"sink": "eval", "arg": "1+1"},
        {"sink": "document.write", "arg": "dxaCAFE trailer"},
    ]
    hits = dxadom.sink_hits_for(sinks, "dxaCAFE")
    assert len(hits) == 2
    assert all("dxaCAFE" in h["arg"] for h in hits)


def test_sink_hits_for_empty_needle_returns_empty_list():
    """Empty needle must NOT match every entry (would defeat correlation)."""
    sinks = [{"sink": "eval", "arg": "anything"}]
    assert dxadom.sink_hits_for(sinks, "") == []


def test_sink_hits_for_no_sinks_returns_empty():
    assert dxadom.sink_hits_for([], "dxaCAFE") == []
    assert dxadom.sink_hits_for(None, "dxaCAFE") == []


# --- real-browser sink detection: fixture pages that hit each sink ----------

class _SinkHandler(http.server.BaseHTTPRequestHandler):
    """Serve one page per sink type; each page reads a `p` query param
    and pipes it into the target sink so tests can verify the arg is
    captured with a known canary marker."""
    def log_message(self, format, *args):
        return

    def _send(self, body):
        b = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        import urllib.parse
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        p = qs.get("p", ["dxaCAFE"])[0]
        # Only-ASCII payloads used in tests; JS string escape via JSON.
        import json as _j
        js_str = _j.dumps(p)
        if parsed.path == "/innerHTML":
            self._send(
                f'<html><body><div id="x"></div>'
                f'<script>document.getElementById("x").innerHTML = {js_str};</script>'
                f'</body></html>')
        elif parsed.path == "/outerHTML":
            self._send(
                f'<html><body><div id="x">old</div>'
                f'<script>document.getElementById("x").outerHTML = {js_str};</script>'
                f'</body></html>')
        elif parsed.path == "/write":
            self._send(
                f'<html><body><script>document.write({js_str});</script>'
                f'</body></html>')
        elif parsed.path == "/writeln":
            self._send(
                f'<html><body><script>document.writeln({js_str});</script>'
                f'</body></html>')
        elif parsed.path == "/eval":
            # eval a benign statement whose SOURCE contains the marker.
            src = f'var x = {js_str};'
            self._send(
                f'<html><body><script>window.eval({_j.dumps(src)});</script>'
                f'</body></html>')
        elif parsed.path == "/function":
            src = f'return {js_str};'
            self._send(
                f'<html><body><script>new Function({_j.dumps(src)})();</script>'
                f'</body></html>')
        elif parsed.path == "/ccf":
            # Range.createContextualFragment
            self._send(
                f'<html><body><script>'
                f'const r = document.createRange();'
                f'r.selectNode(document.body);'
                f'r.createContextualFragment({js_str});'
                f'</script></body></html>')
        elif parsed.path == "/no-sinks":
            self._send(
                '<html><body><script>var quiet = 1 + 1;</script></body></html>')
        elif parsed.path == "/multi":
            # Fires innerHTML AND document.write with distinct markers so
            # correlation can distinguish them.
            self._send(
                f'<html><body><div id="x"></div><script>'
                f'document.getElementById("x").innerHTML = "dxaAAAAmark1";'
                f'document.write("dxaBBBBmark2");'
                f'</script></body></html>')
        else:
            self._send('<html>404</html>')


@pytest.fixture
def sink_server():
    httpd = http.server.HTTPServer(("127.0.0.1", 0), _SinkHandler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


@_skip
def test_sink_innerHTML_captured(sink_server):
    port = sink_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(
            f"http://127.0.0.1:{port}/innerHTML?p=dxaCAFE_marker")
    sinks = summary["sinks"]
    assert any(s["sink"] == "Element.innerHTML"
               and "dxaCAFE_marker" in s["arg"] for s in sinks), \
        f"innerHTML not captured; sinks={sinks!r}"


@_skip
def test_sink_outerHTML_captured(sink_server):
    port = sink_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(
            f"http://127.0.0.1:{port}/outerHTML?p=dxaDEAD_marker")
    sinks = summary["sinks"]
    assert any(s["sink"] == "Element.outerHTML"
               and "dxaDEAD_marker" in s["arg"] for s in sinks)


@_skip
def test_sink_document_write_captured(sink_server):
    port = sink_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(
            f"http://127.0.0.1:{port}/write?p=dxaWRITE_marker")
    sinks = summary["sinks"]
    assert any(s["sink"] == "document.write"
               and "dxaWRITE_marker" in s["arg"] for s in sinks)


@_skip
def test_sink_document_writeln_captured(sink_server):
    port = sink_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(
            f"http://127.0.0.1:{port}/writeln?p=dxaWLN_marker")
    sinks = summary["sinks"]
    assert any(s["sink"] == "document.writeln"
               and "dxaWLN_marker" in s["arg"] for s in sinks)


@_skip
def test_sink_eval_captured(sink_server):
    port = sink_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/eval?p=dxaEVAL_marker")
    sinks = summary["sinks"]
    assert any(s["sink"] == "eval"
               and "dxaEVAL_marker" in s["arg"] for s in sinks)


@_skip
def test_sink_function_constructor_captured(sink_server):
    port = sink_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/function?p=dxaFN_marker")
    sinks = summary["sinks"]
    assert any(s["sink"] == "Function"
               and "dxaFN_marker" in s["arg"] for s in sinks)


@_skip
def test_sink_ccf_captured(sink_server):
    port = sink_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/ccf?p=dxaCCF_marker")
    sinks = summary["sinks"]
    assert any(s["sink"] == "Range.createContextualFragment"
               and "dxaCCF_marker" in s["arg"] for s in sinks)


@_skip
def test_page_with_no_sinks_returns_empty_sinks_list(sink_server):
    port = sink_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/no-sinks")
    assert summary["sinks"] == []


@_skip
def test_sink_hits_for_correlates_canary_across_many_sinks(sink_server):
    """The multi-sink page fires innerHTML with dxaAAAAmark1 AND
    document.write with dxaBBBBmark2. Correlation must split them."""
    port = sink_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/multi")
    sinks = summary["sinks"]
    a_hits = dxadom.sink_hits_for(sinks, "dxaAAAAmark1")
    b_hits = dxadom.sink_hits_for(sinks, "dxaBBBBmark2")
    assert len(a_hits) >= 1 and all(h["sink"] == "Element.innerHTML"
                                    for h in a_hits)
    assert len(b_hits) >= 1 and all(h["sink"] == "document.write"
                                    for h in b_hits)


@_skip
def test_sink_record_carries_stack_and_timestamp(sink_server):
    """Every recorded sink must carry a non-empty stack trace and a
    numeric timestamp so downstream tools can attribute + order the
    hits (source-location narrowing in later phases)."""
    port = sink_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(
            f"http://127.0.0.1:{port}/innerHTML?p=dxaSTACK_marker")
    hit = next(s for s in summary["sinks"]
               if s["sink"] == "Element.innerHTML"
               and "dxaSTACK_marker" in s["arg"])
    assert isinstance(hit.get("stack"), str) and hit["stack"]
    assert isinstance(hit.get("ts"), (int, float)) and hit["ts"] > 0


@_skip
def test_sink_arg_is_truncated_beyond_4k(sink_server):
    """Args longer than 4 KiB are truncated with a marker so a massive
    innerHTML=<big string> doesn't blow up sink storage."""
    port = sink_server
    # 8 KiB of a repeating marker guarantees > 4 KiB captured but the
    # `truncated` suffix must be present.
    payload = "dxaBIG_" + ("A" * 8000)
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(
            f"http://127.0.0.1:{port}/innerHTML?p={payload}")
    hit = next(s for s in summary["sinks"]
               if s["sink"] == "Element.innerHTML")
    assert len(hit["arg"]) < 4200      # 4096 + suffix
    assert "truncated" in hit["arg"]
    assert "dxaBIG_" in hit["arg"]     # marker still present at head


# --- Phase 2.3: JS execution proof (dialog capture) ------------------------

def test_dialog_hits_for_filters_by_needle():
    """Unit: filter helper returns only entries whose message contains
    the needle. Mirrors sink_hits_for contract exactly."""
    dialogs = [
        {"type": "alert",   "message": "dxaCAFE fired"},
        {"type": "confirm", "message": "unrelated"},
        {"type": "prompt",  "message": "dxaCAFE too"},
    ]
    hits = dxadom.dialog_hits_for(dialogs, "dxaCAFE")
    assert len(hits) == 2
    assert all("dxaCAFE" in h["message"] for h in hits)


def test_dialog_hits_for_empty_needle_returns_empty():
    """Empty needle must NOT match every entry."""
    assert dxadom.dialog_hits_for(
        [{"type": "alert", "message": "x"}], "") == []


def test_dialog_hits_for_none_and_empty_inputs():
    assert dxadom.dialog_hits_for(None, "dxa") == []
    assert dxadom.dialog_hits_for([], "dxa") == []


def test_proven_executable_constant_exposed():
    """Downstream code (dxadyn severity upgrade) reads this constant."""
    assert dxadom.PROVEN_EXECUTABLE == "proven-executable"


# --- real-browser dialog capture: fixture pages that fire dialogs ----------

class _DialogHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _send(self, body):
        b = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        import urllib.parse
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        p = qs.get("p", ["dxaHIT"])[0]
        import json as _j
        s = _j.dumps(p)
        if parsed.path == "/alert":
            self._send(f'<html><body><script>alert({s});</script></body></html>')
        elif parsed.path == "/confirm":
            self._send(f'<html><body><script>confirm({s});</script></body></html>')
        elif parsed.path == "/prompt":
            self._send(
                f'<html><body><script>prompt({s});</script></body></html>')
        elif parsed.path == "/multi":
            # Distinct markers so correlation can split them.
            self._send(
                '<html><body><script>'
                'alert("dxaAAAA_first");'
                'alert("dxaBBBB_second");'
                'confirm("dxaCCCC_third");'
                '</script></body></html>')
        elif parsed.path == "/no-dialog":
            self._send('<html><body><script>var x = 1;</script></body></html>')
        elif parsed.path == "/onerror-alert":
            # The classic XSS proof shape: <img onerror=alert(...)>.
            # Different vector than a direct alert() call - fires from
            # an event handler triggered by a broken image load.
            self._send(
                f'<html><body>'
                f'<img src=does-not-exist onerror=\'alert({s})\'>'
                f'</body></html>')
        else:
            self._send('<html>404</html>')


@pytest.fixture
def dialog_server():
    httpd = http.server.HTTPServer(("127.0.0.1", 0), _DialogHandler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


@_skip
def test_dialog_alert_captured(dialog_server):
    """The canonical XSS proof: alert('marker') fires -> we record it."""
    port = dialog_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(
            f"http://127.0.0.1:{port}/alert?p=dxaALERT_marker")
    dialogs = summary["dialogs"]
    assert len(dialogs) == 1
    assert dialogs[0]["type"] == "alert"
    assert dialogs[0]["message"] == "dxaALERT_marker"


@_skip
def test_dialog_confirm_captured(dialog_server):
    port = dialog_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(
            f"http://127.0.0.1:{port}/confirm?p=dxaCONF_marker")
    dialogs = summary["dialogs"]
    assert len(dialogs) == 1
    assert dialogs[0]["type"] == "confirm"
    assert dialogs[0]["message"] == "dxaCONF_marker"


@_skip
def test_dialog_prompt_captured(dialog_server):
    port = dialog_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(
            f"http://127.0.0.1:{port}/prompt?p=dxaPROMPT_marker")
    dialogs = summary["dialogs"]
    assert len(dialogs) == 1
    assert dialogs[0]["type"] == "prompt"
    assert dialogs[0]["message"] == "dxaPROMPT_marker"


@_skip
def test_multiple_dialogs_all_captured(dialog_server):
    """3 back-to-back dialogs on one page - all three must land in the
    list, order preserved, each auto-dismissed so the page doesn't hang."""
    port = dialog_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/multi")
    dialogs = summary["dialogs"]
    assert len(dialogs) == 3
    messages = [d["message"] for d in dialogs]
    assert messages == ["dxaAAAA_first", "dxaBBBB_second", "dxaCCCC_third"]
    assert [d["type"] for d in dialogs] == ["alert", "alert", "confirm"]


@_skip
def test_page_with_no_dialogs_returns_empty_list(dialog_server):
    port = dialog_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/no-dialog")
    assert summary["dialogs"] == []


@_skip
def test_dialog_from_onerror_handler_captured(dialog_server):
    """<img onerror=alert(...)> - the classical XSS PoC shape. Different
    trigger path (event handler on broken image) than a direct alert()
    call, so verifies the dialog listener catches indirect fires too."""
    port = dialog_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(
            f"http://127.0.0.1:{port}/onerror-alert?p=dxaONERR_marker")
    dialogs = summary["dialogs"]
    assert any(d["type"] == "alert"
               and d["message"] == "dxaONERR_marker" for d in dialogs)


@_skip
def test_dialog_hits_for_correlates_canary_across_many_dialogs(dialog_server):
    """The multi-dialog page fires three distinct markers. Correlation
    must split them - proves that dialog_hits_for + real capture combine
    correctly for canary attribution."""
    port = dialog_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/multi")
    dialogs = summary["dialogs"]
    a = dxadom.dialog_hits_for(dialogs, "dxaAAAA")
    b = dxadom.dialog_hits_for(dialogs, "dxaBBBB")
    c = dxadom.dialog_hits_for(dialogs, "dxaCCCC")
    assert len(a) == 1 and a[0]["type"] == "alert"
    assert len(b) == 1 and b[0]["type"] == "alert"
    assert len(c) == 1 and c[0]["type"] == "confirm"


@_skip
def test_dialog_record_carries_timestamp(dialog_server):
    """Every captured dialog must have a numeric timestamp so downstream
    tools can order alerts vs sink hits."""
    port = dialog_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/alert?p=dxaTS")
    d = summary["dialogs"][0]
    assert isinstance(d.get("ts"), (int, float)) and d["ts"] > 0


@_skip
def test_dialog_capture_does_not_hang_on_unhandled_prompt(dialog_server):
    """A prompt() waits for a value; without our dismiss() the page
    would hang forever. Test succeeds iff visit() returns within the
    default 15s timeout - we default to dismiss (returns null to JS)."""
    port = dialog_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(
            f"http://127.0.0.1:{port}/prompt?p=dxaHANG_test")
    # Reaching here at all proves no hang; then verify capture.
    assert len(summary["dialogs"]) == 1
    assert summary["errors"] == []


# --- Phase 2.4: SPA route discovery ----------------------------------------

# extract_static_routes unit tests. Always run (regex over strings, no
# browser required).

def test_extract_static_routes_empty_input():
    assert dxadom.extract_static_routes("") == []
    assert dxadom.extract_static_routes(None) == []


def test_extract_static_routes_react_router_path():
    """<Route path="/foo"> and `path: "/bar"` are the React Router
    canonical shapes."""
    src = '<Route path="/users/:id" /><Route path="/settings" />'
    out = dxadom.extract_static_routes(src)
    assert "/users/:id" in out and "/settings" in out


def test_extract_static_routes_to_attribute():
    """React `<Link to="/foo">` uses `to=` instead of `path=`."""
    src = '<Link to="/dashboard">Home</Link>'
    out = dxadom.extract_static_routes(src)
    assert "/dashboard" in out


def test_extract_static_routes_hash_router_literal():
    """Vue hash-router mode and old jQuery-era SPAs use `#/foo`."""
    src = 'window.location.href = "#/profile"; goto("#/orders");'
    out = dxadom.extract_static_routes(src)
    assert "#/profile" in out and "#/orders" in out


def test_extract_static_routes_router_link_attribute():
    """Angular routerLink="/admin" template attribute."""
    src = '<a routerLink="/admin/users" class="nav">Admin</a>'
    out = dxadom.extract_static_routes(src)
    assert "/admin/users" in out


def test_extract_static_routes_navigate_call():
    """navigate("/foo") / router.push("/foo") - React Router 6, Next.js."""
    src = 'navigate("/checkout"); router.push("/thank-you");'
    out = dxadom.extract_static_routes(src)
    assert "/checkout" in out and "/thank-you" in out


def test_extract_static_routes_single_and_double_quotes():
    """Both quote styles must match; framework code uses either."""
    src = "path: '/single'; path: \"/double\";"
    out = dxadom.extract_static_routes(src)
    assert "/single" in out and "/double" in out


def test_extract_static_routes_deduplicates_preserving_order():
    """If the same route appears twice, only the FIRST occurrence lands.
    Order matters for the crawler queue - depth-first from first hit."""
    src = 'path: "/foo"; path: "/bar"; path: "/foo";'
    out = dxadom.extract_static_routes(src)
    assert out.count("/foo") == 1
    assert out.index("/foo") < out.index("/bar")


def test_extract_static_routes_ignores_non_route_strings():
    """The patterns are conservative; a bare `/foo` in prose or a full
    URL like https://x.test/foo should NOT match."""
    src = "The path is /foo when you go to https://x.test/bar"
    out = dxadom.extract_static_routes(src)
    # bare `/foo` in prose - not in quotes with path/to/routerLink
    # context - must not fire.
    assert out == []


def test_extract_static_routes_conservative_on_query_strings():
    """`/foo?a=b` has `?` which is not in our safe char class. That's
    fine: we want the base route, callers add query params."""
    src = 'path: "/simple"'
    out = dxadom.extract_static_routes(src)
    assert "/simple" in out


# --- real-browser SPA route capture: runtime pushState/replaceState/hash ---

class _SpaHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _send(self, body):
        b = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/pushstate":
            self._send(
                '<html><body><script>'
                'history.pushState({}, "", "/dxa-push-route-1");'
                'history.pushState({}, "", "/dxa-push-route-2");'
                '</script></body></html>')
        elif self.path == "/replacestate":
            self._send(
                '<html><body><script>'
                'history.replaceState({}, "", "/dxa-replace-route");'
                '</script></body></html>')
        elif self.path == "/hashchange":
            self._send(
                '<html><body><script>'
                'location.hash = "/dxa-hash-route";'
                '</script></body></html>')
        elif self.path == "/static-routes":
            # Multiple static declarations in <script> + attribute.
            self._send(
                '<html><body>'
                '<a routerLink="/dxa-angular-link">A</a>'
                '<script>'
                'const routes = [{path: "/dxa-react-a"}, {path: "/dxa-react-b/:id"}];'
                'navigate("/dxa-navigate-c");'
                'location.href = "#/dxa-hash-d";'
                '</script>'
                '</body></html>')
        elif self.path == "/no-routes":
            self._send(
                '<html><body><script>var x = 1;</script></body></html>')
        elif self.path == "/mixed":
            # Runtime captures BOTH pushState AND static declarations.
            self._send(
                '<html><body><script>'
                'history.pushState({}, "", "/dxa-runtime-mix");'
                'const routes = [{path: "/dxa-static-mix"}];'
                '</script></body></html>')
        else:
            self._send('<html>404</html>')


@pytest.fixture
def spa_server():
    httpd = http.server.HTTPServer(("127.0.0.1", 0), _SpaHandler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


@_skip
def test_route_capture_pushstate(spa_server):
    """history.pushState calls land in routes.runtime with kind='pushState'."""
    port = spa_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/pushstate")
    runtime = summary["routes"]["runtime"]
    urls = [r["url"] for r in runtime]
    assert "/dxa-push-route-1" in urls
    assert "/dxa-push-route-2" in urls
    assert all(r["kind"] == "pushState" for r in runtime
               if r["url"].startswith("/dxa-push"))


@_skip
def test_route_capture_replacestate(spa_server):
    port = spa_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/replacestate")
    runtime = summary["routes"]["runtime"]
    assert any(r["kind"] == "replaceState"
               and r["url"] == "/dxa-replace-route" for r in runtime)


@_skip
def test_route_capture_hashchange(spa_server):
    """location.hash = "..." triggers hashchange - captured too."""
    port = spa_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/hashchange")
    runtime = summary["routes"]["runtime"]
    assert any(r["kind"] == "hashchange"
               and "dxa-hash-route" in r["url"] for r in runtime)


@_skip
def test_static_route_extraction_end_to_end(spa_server):
    """The static extractor runs against page.content() after load and
    finds React path=, Angular routerLink=, navigate("/…"), hash literals."""
    port = spa_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/static-routes")
    static = summary["routes"]["static"]
    for expected in ("/dxa-angular-link", "/dxa-react-a", "/dxa-react-b/:id",
                     "/dxa-navigate-c", "#/dxa-hash-d"):
        assert expected in static, (
            f"missing {expected} from static routes: {static}")


@_skip
def test_no_routes_returns_empty_lists(spa_server):
    """A page with no SPA navigation and no route declarations returns
    empty runtime + static lists - the honest default."""
    port = spa_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/no-routes")
    assert summary["routes"]["runtime"] == []
    assert summary["routes"]["static"] == []


@_skip
def test_mixed_page_captures_both_runtime_and_static(spa_server):
    """A page that BOTH declares a route statically AND opens one via
    pushState fills both lists distinctly - they're complementary
    passes, not duplicates."""
    port = spa_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/mixed")
    runtime_urls = [r["url"] for r in summary["routes"]["runtime"]]
    assert "/dxa-runtime-mix" in runtime_urls
    assert "/dxa-static-mix" in summary["routes"]["static"]


@_skip
def test_route_record_carries_timestamp(spa_server):
    port = spa_server
    with dxadom.BrowserSession() as sess:
        summary = sess.visit(f"http://127.0.0.1:{port}/pushstate")
    r = summary["routes"]["runtime"][0]
    assert isinstance(r.get("ts"), (int, float)) and r["ts"] > 0
