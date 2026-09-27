"""Tests for dxadyn (dynamic reflection verifier). Run from this directory: pytest -q

Covers the detection core (raw vs encoded vs absent), input discovery, and one
end-to-end run against a throwaway local reflector that echoes one field raw
(vulnerable) and one HTML-escaped (safe) - proving dxadyn flags the first and
ignores the second, with no false positive on the encoded one.
"""

import html
import threading

import pytest
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import dxadyn


# --- detection core ---------------------------------------------------------

def test_verdict_unencoded():
    assert dxadyn.verdict("dxaAAAA", 'x dxaAAAA"<dXsS> y') == "unencoded"


def test_verdict_unencoded_even_if_quote_encoded():
    # the tag survived raw even though the quote was escaped -> still HTML injection
    assert dxadyn.verdict("dxaAAAA", 'x dxaAAAA&quot;<dXsS> y') == "unencoded"


def test_verdict_encoded_is_safe():
    assert dxadyn.verdict("dxaBBBB", 'x dxaBBBB&quot;&lt;dXsS&gt; y') == "encoded"


def test_verdict_attr_only_quote_breakout():
    assert dxadyn.verdict("dxaDDDD", 'value="dxaDDDD" more') == "attr-only"


def test_verdict_absent():
    assert dxadyn.verdict("dxaCCCC", "nothing reflected here") == "absent"


def test_make_canary_is_unique_and_shaped():
    c1, v1 = dxadyn.make_canary()
    c2, v2 = dxadyn.make_canary()
    assert c1.startswith("dxa") and c1 != c2
    assert c1 in v1 and dxadyn.MARKUP in v1


# --- input discovery --------------------------------------------------------

def test_discover_finds_form_and_param_link():
    body = ('<form action="/r" method="get"><input name="q"></form>'
            '<a href="/x?id=1&amp;y=2">l</a>')
    forms, links = dxadyn.discover("http://h/", body)
    assert forms and forms[0]["action"].endswith("/r")
    assert forms[0]["method"] == "get" and "q" in forms[0]["fields"]
    assert any("id=1" in l for l in links)


def test_discover_skips_submit_buttons():
    body = '<form action="/a"><input name="q"><input type="submit" name="go"></form>'
    forms, _ = dxadyn.discover("http://h/", body)
    assert "q" in forms[0]["fields"] and "go" not in forms[0]["fields"]


# --- end-to-end against a throwaway reflector -------------------------------

_INDEX = ('<form action="/r" method="get"><input name="q"></form>'
          '<form action="/rs" method="get"><input name="q"></form>')


class _Reflector(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query).get("q", [""])[0]
        if u.path == "/r":
            body = f"<div>{q}</div>"                    # RAW echo = vulnerable
        elif u.path == "/rs":
            body = f"<div>{html.escape(q)}</div>"       # escaped = safe
        else:
            body = _INDEX
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body.encode())


def test_end_to_end_flags_raw_not_escaped():
    srv = HTTPServer(("127.0.0.1", 0), _Reflector)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        findings = dxadyn.crawl(f"http://127.0.0.1:{port}/", 0)
    finally:
        srv.shutdown()

    flagged = {(f["url"].rsplit("/", 1)[1], f["reflection"]) for f in findings}
    assert ("r", "unencoded") in flagged          # the raw form is caught
    assert not any(url == "rs" for url, _ in flagged)   # the escaped form is not


# --- v2: auth + stored ------------------------------------------------------

def test_parse_kv_list():
    assert dxadyn._parse_kv_list("a=1,b=hi,c=") == {"a": "1", "b": "hi", "c": ""}
    assert dxadyn._parse_kv_list("") == {}
    # invalid pairs (no =) are skipped, not crashed on
    assert dxadyn._parse_kv_list("bogus,a=1") == {"a": "1"}


def test_extract_csrf_both_orders():
    body_a = '<input type="hidden" name="tokenCSRF" value="abc123">'
    body_b = '<input type="hidden" value="xyz789" name="tokenCSRF">'
    assert dxadyn._extract_csrf(body_a, "tokenCSRF") == "abc123"
    assert dxadyn._extract_csrf(body_b, "tokenCSRF") == "xyz789"
    assert dxadyn._extract_csrf("no token here", "tokenCSRF") is None


# --- End-to-end: stored XSS through an authenticated form -------------------
# Fixture mirrors the Bludit-shaped flow (in miniature): a login-protected
# /new POST stores a `tags` value; the public /view/<id> page renders it RAW
# (vulnerable), the /viewsafe/<id> page HTML-escapes it (safe). dxadyn --stored
# with --login must flag the raw view and skip the escaped one.

_TAGS_DB = {}
_TAGS_COOKIE = "dxa_session=ok"


def _sluggy(s):
    import re as _re
    return _re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-') or "x"


class _StoredApp(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _authed(self):
        return _TAGS_COOKIE in (self.headers.get("Cookie") or "")

    def _send(self, code, body, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", "text/html")
        if extra:
            for k, v in extra:
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        p = urlparse(self.path)
        if p.path == "/login":
            body = ('<form method="post" action="/login">'
                    '<input type="hidden" name="tokenCSRF" value="TOK123">'
                    '<input name="username"><input name="password">'
                    '<input type="submit"></form>')
            return self._send(200, body)
        if p.path == "/new":
            if not self._authed():
                return self._send(403, "login required")
            body = ('<form method="post" action="/new">'
                    '<input type="hidden" name="tokenCSRF" value="TOK123">'
                    '<input name="title"><input name="tags"><input type="submit"></form>')
            return self._send(200, body)
        if p.path.startswith("/view/"):
            key = p.path.split("/", 2)[2]
            return self._send(200, f"<h1>tag: {_TAGS_DB.get(key, '(none)')}</h1>")   # RAW
        if p.path.startswith("/viewsafe/"):
            key = p.path.split("/", 2)[2]
            return self._send(200, f"<h1>tag: {html.escape(_TAGS_DB.get(key, ''))}</h1>")
        return self._send(404, "nope")

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        fields = parse_qs(self.rfile.read(length).decode(), keep_blank_values=True)
        if self.path == "/login":
            u = fields.get("username", [""])[0]
            p = fields.get("password", [""])[0]
            if u == "admin" and p == "labpass" and \
                    fields.get("tokenCSRF", [""])[0] == "TOK123":
                return self._send(302, "", extra=[("Location", "/dashboard"),
                                                  ("Set-Cookie", _TAGS_COOKIE + "; Path=/")])
            return self._send(401, "no")
        if self.path == "/new":
            if not self._authed() or fields.get("tokenCSRF", [""])[0] != "TOK123":
                return self._send(403, "csrf/auth")
            tag = fields.get("tags", [""])[0]
            _TAGS_DB[_sluggy(tag)] = tag
            return self._send(302, "", extra=[("Location", "/dashboard")])
        return self._send(404, "nope")


# --- v3.1: cookie / header injection ----------------------------------------

class _EchoHeaders(BaseHTTPRequestHandler):
    """Reflects the incoming Cookie + selected headers so tests can assert them."""
    def log_message(self, *a):
        pass

    def do_GET(self):
        cookie = self.headers.get("Cookie") or ""
        bearer = self.headers.get("Authorization") or ""
        csrf = self.headers.get("X-CSRF-Token") or ""
        body = f"cookie={cookie}|auth={bearer}|csrf={csrf}"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(body.encode())


def test_apply_cookie_rides_every_request():
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.apply_cookie("sid=abc123; csrf=xyz")
    srv = HTTPServer(("127.0.0.1", 0), _EchoHeaders)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        _, _, body, _ = dxadyn.fetch(f"http://127.0.0.1:{port}/anywhere")
    finally:
        srv.shutdown()
        dxadyn.EXTRA_HEADERS.clear()
    assert "cookie=sid=abc123; csrf=xyz" in body


def test_apply_header_parses_name_value_and_rejects_junk():
    dxadyn.EXTRA_HEADERS.clear()
    assert dxadyn.apply_header("Authorization: Bearer eyJabc.def")
    assert dxadyn.apply_header("X-CSRF-Token: tok-42")
    assert not dxadyn.apply_header("no-colon-here")
    assert not dxadyn.apply_header(": nokey")
    srv = HTTPServer(("127.0.0.1", 0), _EchoHeaders)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        _, _, body, _ = dxadyn.fetch(f"http://127.0.0.1:{port}/")
    finally:
        srv.shutdown()
        dxadyn.EXTRA_HEADERS.clear()
    assert "auth=Bearer eyJabc.def" in body
    assert "csrf=tok-42" in body


# --- v3.3 bonus: header-injection probe (Bludit Finding #8 shape) -----------

class _HeaderEcho(BaseHTTPRequestHandler):
    """Echoes X-Forwarded-For raw (vuln), Referer HTML-escaped (safe)."""
    def log_message(self, *a):
        pass

    def do_GET(self):
        xff = self.headers.get("X-Forwarded-For", "")
        ref = self.headers.get("Referer", "")
        body = f"<p>ip={xff}</p><p>ref={html.escape(ref)}</p>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body.encode())


def test_probe_headers_flags_raw_and_ignores_escaped():
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.OPENER = dxadyn._opener()
    srv = HTTPServer(("127.0.0.1", 0), _HeaderEcho)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        findings = dxadyn.probe_headers(
            f"http://127.0.0.1:{port}/", ["X-Forwarded-For", "Referer"])
    finally:
        srv.shutdown()
    flagged = {(f["param"], f["reflection"]) for f in findings}
    assert ("header:X-Forwarded-For", "unencoded") in flagged
    assert not any(p == "header:Referer" for p, _ in flagged)


def test_probe_headers_leaves_no_lingering_headers():
    """Regression: EXTRA_HEADERS must not keep the last canary header set."""
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.OPENER = dxadyn._opener()
    srv = HTTPServer(("127.0.0.1", 0), _HeaderEcho)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        dxadyn.probe_headers(f"http://127.0.0.1:{port}/", ["X-Forwarded-For"])
    finally:
        srv.shutdown()
    assert "X-Forwarded-For" not in dxadyn.EXTRA_HEADERS


# --- v3.7: Content-Type gate (JSON API false-positive squelch) -------------

def test_is_html_response_defaults():
    assert dxadyn._is_html_response("text/html; charset=utf-8")
    assert dxadyn._is_html_response("application/xhtml+xml")
    assert dxadyn._is_html_response("image/svg+xml")
    assert dxadyn._is_html_response("")                       # empty -> lean HTML
    assert dxadyn._is_html_response("text/xml")               # text/* default HTML
    # non-HTML
    assert not dxadyn._is_html_response("application/json")
    assert not dxadyn._is_html_response("application/json; charset=utf-8")
    assert not dxadyn._is_html_response("application/ld+json")
    assert not dxadyn._is_html_response("text/plain")
    assert not dxadyn._is_html_response("text/csv")


def test_ct_gate_downgrades_json_body_to_json_only():
    ctx, sev = dxadyn._apply_ct_gate("unencoded", "body", "application/json")
    assert ctx == "json-body"
    assert sev == "json-only"


def test_ct_gate_leaves_html_body_as_executable():
    ctx, sev = dxadyn._apply_ct_gate("unencoded", "body", "text/html")
    assert ctx == "body"
    assert sev == "executable"


def test_ct_gate_html_title_is_still_breakout_req():
    ctx, sev = dxadyn._apply_ct_gate("unencoded", "title", "text/html")
    assert ctx == "title"
    assert sev == "breakout-req"


class _JsonReflector(BaseHTTPRequestHandler):
    """Reflects the ?q= value RAW in a JSON body with Content-Type json.
    The bot's older behaviour flagged this as [EXECUTABLE] context=body;
    v3.7 must classify it as [JSON-ONLY] context=json-body."""
    def log_message(self, *a):
        pass
    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query).get("q", [""])[0]
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(('{"echoed":"' + q + '"}').encode())


def test_reflected_probe_marks_json_response_as_json_only():
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.OPENER = dxadyn._opener()
    srv = HTTPServer(("127.0.0.1", 0), _JsonReflector)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        findings = dxadyn.probe_link(f"http://127.0.0.1:{port}/api?q=x")
    finally:
        srv.shutdown()
    assert findings, "must still record the raw reflection"
    f = findings[0]
    assert f["severity"] == "json-only", "must NOT be executable on JSON"
    assert f["context"] == "json-body"
    assert "application/json" in f["content_type"]


# --- v3.6: PUT/PATCH/DELETE method support ----------------------------------

class _MethodEcho(BaseHTTPRequestHandler):
    """Records the request method + JSON body for the last request; responds
    with a page that reflects whatever was sent so verdict can grade."""
    last = {"method": None, "body": None, "path": None}
    def log_message(self, *a):
        pass
    def _handle(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode() if length else ""
        self.__class__.last = {"method": self.command, "body": raw,
                               "path": self.path}
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        # echo raw body inside <body> so verdict + context detection can run
        self.wfile.write(f"<body>echoed: {raw}</body>".encode())
    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = _handle


def test_fetch_supports_put_and_delete_methods():
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.OPENER = dxadyn._opener()
    srv = HTTPServer(("127.0.0.1", 0), _MethodEcho)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        dxadyn.fetch(f"http://127.0.0.1:{port}/x", data=b"raw", method="PUT")
        assert _MethodEcho.last["method"] == "PUT"
        assert _MethodEcho.last["body"] == "raw"
        dxadyn.fetch(f"http://127.0.0.1:{port}/x", data=b"", method="DELETE")
        assert _MethodEcho.last["method"] == "DELETE"
    finally:
        srv.shutdown()


def test_submit_json_uses_put_when_asked():
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.OPENER = dxadyn._opener()
    srv = HTTPServer(("127.0.0.1", 0), _MethodEcho)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        # Call _submit_json directly so we can inspect the method it dispatched
        # (going through probe_stored would follow up with a GET check that
        # would overwrite _MethodEcho.last).
        st, _ = dxadyn._submit_json(
            f"http://127.0.0.1:{port}/api/thing",
            '{"name":"{CANARY}"}', "dxaTEST", method="PUT")
    finally:
        srv.shutdown()
    assert _MethodEcho.last["method"] == "PUT"
    assert '"name":"dxaTEST"' in _MethodEcho.last["body"]


def test_submit_form_dispatches_patch():
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.OPENER = dxadyn._opener()
    srv = HTTPServer(("127.0.0.1", 0), _MethodEcho)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        st, _ = dxadyn._submit_form(
            f"http://127.0.0.1:{port}/api/thing", "name",
            {}, "dxaTEST", method="PATCH", csrf_field="")
    finally:
        srv.shutdown()
    assert _MethodEcho.last["method"] == "PATCH"
    assert "name=dxaTEST" in _MethodEcho.last["body"]


# --- v3.5: sink-context awareness + dedup -----------------------------------

def test_find_context_body_is_free_markup():
    body = "<html><body><div>xxx dxaAAAA\"<dXsS> yyy</div></body></html>"
    assert dxadyn.find_context("dxaAAAA", body) == "body"


def test_find_context_title_needs_breakout():
    body = "<html><head><title>results for dxaAAAA\"<dXsS></title>rest</head>"
    assert dxadyn.find_context("dxaAAAA", body) == "title"


def test_find_context_script_context():
    body = '<html><head><script>var q = "dxaAAAA\\"<dXsS>";</script></head>'
    assert dxadyn.find_context("dxaAAAA", body) == "script"


def test_find_context_url_attribute():
    body = '<html><body><a href="/search?q=dxaAAAA">l</a></body></html>'
    assert dxadyn.find_context("dxaAAAA", body) == "url-attr:href"


def test_find_context_generic_attribute():
    body = '<html><body><input type="text" value="dxaAAAA"></body></html>'
    assert dxadyn.find_context("dxaAAAA", body) == "attr:value"


def test_context_executes_only_body_and_unknown():
    assert dxadyn.context_executes("body")
    assert dxadyn.context_executes("unknown")
    assert not dxadyn.context_executes("title")
    assert not dxadyn.context_executes("script")
    assert not dxadyn.context_executes("attr:value")
    assert not dxadyn.context_executes("url-attr:href")


def test_severity_labels():
    assert dxadyn._severity("unencoded", "body") == "executable"
    assert dxadyn._severity("unencoded", "title") == "breakout-req"
    assert dxadyn._severity("unencoded", "attr:value") == "breakout-req"
    assert dxadyn._severity("attr-only", "body") == "attr-breakout"
    assert dxadyn._severity("encoded", "body") == "-"


def test_dedupe_collapses_same_bug_across_pages():
    findings = [
        {"canary_id": "dxaXX", "reflection": "unencoded", "context": "body",
         "check_url": "http://x/a", "confidence": "high"},
        {"canary_id": "dxaXX", "reflection": "unencoded", "context": "body",
         "check_url": "http://x/b", "confidence": "high"},
        {"canary_id": "dxaXX", "reflection": "unencoded", "context": "body",
         "check_url": "http://x/c", "confidence": "high"},
        {"canary_id": "dxaYY", "reflection": "attr-only", "context": "attr:value",
         "check_url": "http://x/other", "confidence": "medium"},
    ]
    out = dxadyn.dedupe_findings(findings)
    assert len(out) == 2                          # 2 unique bugs
    body_bug = next(f for f in out if f["canary_id"] == "dxaXX")
    assert body_bug["check_url"] == "http://x/a"  # first kept
    assert body_bug["duplicates"] == ["http://x/b", "http://x/c"]


def test_dedupe_leaves_singletons_alone():
    findings = [{"canary_id": "dxaXX", "reflection": "unencoded",
                 "context": "body", "check_url": "http://x/a"}]
    out = dxadyn.dedupe_findings(findings)
    assert out == findings                        # unchanged


# --- v3.10: payload variants ------------------------------------------------

def test_payload_variants_registered():
    """The variant library must include the five documented shapes."""
    assert set(dxadyn.PAYLOAD_VARIANTS) >= {
        "body", "title-breakout", "attr-breakout",
        "script-breakout", "url-scheme",
    }


def test_make_canary_variant_default_matches_historical():
    """Backwards compat: make_canary() with no arg = old body shape."""
    cid, canary = dxadyn.make_canary()
    assert canary == cid + '"<dXsS>'


def test_make_canary_variant_title_breakout():
    cid, canary = dxadyn.make_canary("title-breakout")
    assert canary == cid + '</title><dXsS>'


def test_make_canary_variant_attr_breakout():
    cid, canary = dxadyn.make_canary("attr-breakout")
    assert canary == cid + '"><dXsS>'


def test_make_canaries_for_yields_per_variant():
    out = list(dxadyn.make_canaries_for(["body", "title-breakout"]))
    assert len(out) == 2
    assert out[0][0] == "body" and out[1][0] == "title-breakout"
    # Each variant has its own cid (different random hex)
    assert out[0][1] != out[1][1]
    # And its own marker
    assert out[0][3] == '<dXsS>'
    assert out[1][3] == '</title><dXsS>'


def test_verdict_marker_parameter_body_default():
    body = '<div>xxx dxaAAAA"<dXsS> yyy</div>'
    assert dxadyn.verdict("dxaAAAA", body) == "unencoded"


def test_verdict_marker_parameter_title_variant():
    """title-breakout variant's marker is </title><dXsS>; the plain <dXsS>
    marker (default) wouldn't fire alone if only the breakout survived."""
    body = '<title>results dxaAAAA</title><dXsS></title><rest>'
    # with default marker (<dXsS>): unencoded (marker present after cid)
    assert dxadyn.verdict("dxaAAAA", body) == "unencoded"
    # with the title-breakout marker: still unencoded (full string survives)
    assert dxadyn.verdict("dxaAAAA", body, marker='</title><dXsS>') == "unencoded"


def test_verdict_marker_absent_when_only_partial_survives():
    body = '<title>results dxaAAAA&lt;/title&gt;&lt;dXsS&gt;</title>'
    # variant marker </title><dXsS> is HTML-escaped -> not raw
    assert dxadyn.verdict("dxaAAAA", body, marker='</title><dXsS>') == "encoded"


def test_ct_gate_breakout_variant_upgrades_to_executable():
    """v3.10 semantic: a -breakout variant that survived raw in an HTML
    response is treated as executable even if the CID landed inside title/
    attr/script - the breakout marker escaped the surrounding context."""
    ctx, sev = dxadyn._apply_ct_gate("unencoded", "title", "text/html",
                                     variant="title-breakout")
    assert ctx == "title" and sev == "executable"
    ctx, sev = dxadyn._apply_ct_gate("unencoded", "attr:value", "text/html",
                                     variant="attr-breakout")
    assert sev == "executable"


def test_ct_gate_breakout_variant_does_not_bypass_json_downgrade():
    """The JSON downgrade still wins - a breakout variant on JSON response
    doesn't execute in the browser either."""
    ctx, sev = dxadyn._apply_ct_gate("unencoded", "body", "application/json",
                                     variant="title-breakout")
    assert sev == "json-only"


def test_ct_gate_plain_body_variant_unchanged():
    ctx, sev = dxadyn._apply_ct_gate("unencoded", "title", "text/html",
                                     variant="body")
    # body variant + title context = still breakout-req (no marker escape claim)
    assert sev == "breakout-req"


# --- v3.10 late: WAF-bypass mutations + reflected variants ------------------

def test_waf_mutations_return_named_triples():
    """_waf_mutations() must return (name, canary_str, marker_str) triples;
    the v3.10 originals plus the Phase 1.2 additions must all be present."""
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    names = [t[0] for t in triples]
    # v3.10 originals still first, in original order
    assert names[:4] == ["case", "split-cmt", "whitespace", "url-encode"]
    # Phase 1.2 additions all present (order-independent)
    assert set(names[4:]) >= {"tab-in-tag", "newline-in-tag",
                              "slash-separator", "double-url-encode"}
    # each mutation transforms both the canary and the marker
    for name, canary, marker in triples:
        assert marker != '<dXsS>', f"{name} marker must differ from base"
        assert canary.startswith('dxaAAAA')


def test_make_canaries_for_waf_bypass_multiplies_by_full_library():
    """One base variant + N mutations = 1+N canary tuples. Number grows with
    the library; this test asserts the invariant, not a hardcoded count."""
    out = list(dxadyn.make_canaries_for(["body"], waf_bypass=True))
    expected = 1 + len(dxadyn._WAF_MUTATIONS)
    assert len(out) == expected
    # first is the base
    assert out[0][0] == "body"
    # every follow-on is named `body/<mutation>`
    for name, _, _, _ in out[1:]:
        assert name.startswith("body/")
    # every canary has its OWN cid (no reuse)
    cids = {t[1] for t in out}
    assert len(cids) == expected


def test_make_canaries_for_waf_bypass_across_multiple_variants():
    """N variants × (1 + M mutations) = N*(1+M) canary tuples."""
    variants = ["body", "title-breakout"]
    out = list(dxadyn.make_canaries_for(variants, waf_bypass=True))
    expected = len(variants) * (1 + len(dxadyn._WAF_MUTATIONS))
    assert len(out) == expected
    # both bases present
    names = [t[0] for t in out]
    assert "body" in names and "title-breakout" in names
    # a v3.10 mutation and a Phase 1.2 mutation are both wired per variant
    assert "title-breakout/case" in names
    assert "body/tab-in-tag" in names


def test_make_canaries_for_no_waf_bypass_stays_single_shape():
    """Default (waf_bypass=False) still yields exactly one tuple per variant."""
    out = list(dxadyn.make_canaries_for(["body", "attr-breakout"]))
    assert len(out) == 2


# --- Phase 1.2: expanded variant library -----------------------------------

def test_phase_1_2_variant_library_has_expected_size():
    """After Phase 1.2 first milestone, library must include at least the
    12+ documented shapes across event-handler / HTML5 / quote-style / JS."""
    # Baseline (v3.10) five + Phase 1.2 additions -> >= 12
    assert len(dxadyn.PAYLOAD_VARIANTS) >= 12
    assert set(dxadyn.PAYLOAD_VARIANTS) >= {
        # v3.10 originals
        "body", "title-breakout", "attr-breakout",
        "script-breakout", "url-scheme",
        # Phase 1.2 event-handler tags
        "svg-breakout", "img-breakout",
        "body-onload-breakout", "details-toggle-breakout",
        "input-autofocus-breakout",
        # HTML5 sanitizer bypass
        "iframe-srcdoc-breakout", "video-source-breakout",
        # quote-style
        "attr-squote-breakout", "attr-backtick-breakout",
        # JS/template
        "template-literal-breakout", "html-comment-breakout",
    }


def test_phase_1_2_svg_breakout_payload_shape():
    """svg-breakout must contain a real <svg onload=...> tag whose survival
    proves executability, not just the <dXsS> grep-marker."""
    cid, canary = dxadyn.make_canary("svg-breakout")
    assert canary.startswith(cid)
    assert '<svg onload=1>' in canary
    assert '<dXsS>' in canary
    # marker embeds the tag itself
    _, marker = dxadyn.PAYLOAD_VARIANTS["svg-breakout"]
    assert '<svg onload=1>' in marker


def test_phase_1_2_img_breakout_payload_shape():
    cid, canary = dxadyn.make_canary("img-breakout")
    assert '<img src=x onerror=1>' in canary


def test_phase_1_2_details_toggle_payload_shape():
    cid, canary = dxadyn.make_canary("details-toggle-breakout")
    assert '<details open ontoggle=1>' in canary


def test_phase_1_2_iframe_srcdoc_payload_shape():
    cid, canary = dxadyn.make_canary("iframe-srcdoc-breakout")
    assert '<iframe srcdoc=' in canary


def test_phase_1_2_attr_squote_uses_single_quote():
    """Single-quote-context attribute breakout (many templates use ')."""
    cid, canary = dxadyn.make_canary("attr-squote-breakout")
    assert "'>" in canary


def test_phase_1_2_attr_backtick_uses_backtick():
    """Backtick-quoted attributes (some framework template contexts)."""
    cid, canary = dxadyn.make_canary("attr-backtick-breakout")
    assert '`>' in canary


def test_phase_1_2_template_literal_uses_dollar_brace():
    """JS template-literal context breakout (Vue/React inline scripts)."""
    cid, canary = dxadyn.make_canary("template-literal-breakout")
    assert '${' in canary


def test_phase_1_2_html_comment_breakout_closes_comment():
    """HTML-comment-context breakout: `-->` closes the surrounding comment."""
    cid, canary = dxadyn.make_canary("html-comment-breakout")
    assert '-->' in canary


def test_phase_1_2_all_new_variants_upgrade_to_executable_on_html():
    """Every -breakout name (existing + new) must upgrade to executable
    severity when reflected unencoded in an HTML response. This is the
    invariant that ties naming to CT-gate behavior."""
    for vname in dxadyn.PAYLOAD_VARIANTS:
        if not vname.endswith("-breakout"):
            continue
        _, sev = dxadyn._apply_ct_gate("unencoded", "body", "text/html",
                                        variant=vname)
        assert sev == "executable", f"{vname} did not upgrade to executable"


def test_phase_1_2_all_new_variants_still_downgrade_on_json():
    """Even -breakout variants stay `json-only` on a JSON Content-Type -
    the CT gate is the hard boundary."""
    for vname in dxadyn.PAYLOAD_VARIANTS:
        if not vname.endswith("-breakout"):
            continue
        _, sev = dxadyn._apply_ct_gate("unencoded", "body", "application/json",
                                        variant=vname)
        assert sev == "json-only", f"{vname} incorrectly executed on JSON"


# --- Phase 1.2: expanded WAF mutation library -------------------------------

def test_phase_1_2_tab_in_tag_mutation_shape():
    """HTML5 permits tab as whitespace inside a tag; verify the mutation
    produces `<dXsS\\t>` in both canary and marker."""
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    tab = [t for t in triples if t[0] == "tab-in-tag"][0]
    _, canary, marker = tab
    assert '<dXsS\t>' in canary
    assert '<dXsS\t>' in marker


def test_phase_1_2_newline_in_tag_mutation_shape():
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    nl = [t for t in triples if t[0] == "newline-in-tag"][0]
    assert '<dXsS\n>' in nl[1] and '<dXsS\n>' in nl[2]


def test_phase_1_2_slash_separator_mutation_shape():
    """`<tag/attr>` uses slash as HTML5-legal whitespace-like separator;
    bypasses WAFs anchored on space after tag name."""
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    sl = [t for t in triples if t[0] == "slash-separator"][0]
    assert '<dXsS/>' in sl[1] and '<dXsS/>' in sl[2]


def test_phase_1_2_double_url_encode_mutation_shape():
    """Double URL-encode: single-decode WAF sees `%253C`; double-decode
    backend sees `<`."""
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    du = [t for t in triples if t[0] == "double-url-encode"][0]
    assert '%253CdXsS%253E' in du[1]
    assert '%253CdXsS%253E' in du[2]


def test_phase_1_2_total_shape_count_grew():
    """The whole point of Phase 1.2 first milestone: --variants all
    --waf-bypass fans out to more shapes than the v3.10 baseline of 25."""
    all_variants = list(dxadyn.PAYLOAD_VARIANTS)
    out = list(dxadyn.make_canaries_for(all_variants, waf_bypass=True))
    # v3.10 baseline: 5 × 5 = 25. Post-1.2-milestone: at least 12 × 5 = 60.
    assert len(out) >= 60
    # And more concretely: every variant has its own base + every mutation
    per_variant = 1 + len(dxadyn._WAF_MUTATIONS)
    assert len(out) == len(dxadyn.PAYLOAD_VARIANTS) * per_variant


# --- Phase 1.2 milestone 2: 12 -> 25+ variants, 8 -> 13+ mutations ---------

def test_phase_1_2_m2_variant_library_reached_25():
    """Milestone 2 doubles the variant library. Full DoD is ~50."""
    assert len(dxadyn.PAYLOAD_VARIANTS) >= 25
    assert set(dxadyn.PAYLOAD_VARIANTS) >= {
        "svg-script-nested-breakout", "math-mtext-breakout",
        "object-data-breakout", "embed-src-breakout",
        "marquee-onstart-breakout", "select-onfocus-breakout",
        "textarea-onfocus-breakout", "form-formaction-breakout",
        "iframe-data-uri-breakout", "js-double-string-breakout",
        "anchor-href-javascript-breakout",
        "noscript-breakout", "style-tag-breakout",
    }


def test_phase_1_2_m2_svg_script_nested_bypasses_top_level_script_strip():
    """svg-script-nested: sanitizers that strip <script> at top level
    often forget SVG foreign content."""
    cid, canary = dxadyn.make_canary("svg-script-nested-breakout")
    assert '<svg><script>' in canary
    assert '</script></svg>' in canary


def test_phase_1_2_m2_math_mtext_uses_mglyph_sink():
    """MathML foreign-content surface. mglyph is a rare-audit sink."""
    cid, canary = dxadyn.make_canary("math-mtext-breakout")
    assert '<math>' in canary and '<mglyph' in canary


def test_phase_1_2_m2_object_data_uses_data_uri():
    cid, canary = dxadyn.make_canary("object-data-breakout")
    assert '<object data=data:text/html,' in canary


def test_phase_1_2_m2_embed_src_uses_data_uri():
    cid, canary = dxadyn.make_canary("embed-src-breakout")
    assert '<embed src=data:text/html,' in canary


def test_phase_1_2_m2_marquee_onstart_present():
    cid, canary = dxadyn.make_canary("marquee-onstart-breakout")
    assert '<marquee onstart=1>' in canary


def test_phase_1_2_m2_select_and_textarea_variants_use_autofocus():
    """Both need `autofocus onfocus=` since the browser only fires
    focus events on the currently-focused element."""
    for vname in ("select-onfocus-breakout", "textarea-onfocus-breakout"):
        cid, canary = dxadyn.make_canary(vname)
        assert 'autofocus' in canary and 'onfocus=1' in canary


def test_phase_1_2_m2_form_formaction_override():
    """HTML5 formaction attribute overrides the parent form's action."""
    cid, canary = dxadyn.make_canary("form-formaction-breakout")
    assert '<form>' in canary
    assert 'formaction=javascript:1' in canary


def test_phase_1_2_m2_iframe_data_uri_payload():
    cid, canary = dxadyn.make_canary("iframe-data-uri-breakout")
    assert '<iframe src=data:text/html,' in canary


def test_phase_1_2_m2_js_double_string_complements_script_breakout():
    """script-breakout uses ' quote; js-double-string uses ". Together
    they cover both JS string-quote conventions."""
    _, single = dxadyn.PAYLOAD_VARIANTS["script-breakout"]
    _, double = dxadyn.PAYLOAD_VARIANTS["js-double-string-breakout"]
    # both share the <dXsS> marker but use opposite quotes to break out
    _, single_suffix = dxadyn.make_canary("script-breakout")
    _, double_suffix = dxadyn.make_canary("js-double-string-breakout")
    assert "';" in single_suffix
    assert '";' in double_suffix


def test_phase_1_2_m2_anchor_href_javascript_present():
    cid, canary = dxadyn.make_canary("anchor-href-javascript-breakout")
    assert '<a href=javascript:1>' in canary


def test_phase_1_2_m2_noscript_breakout_closes_noscript():
    """The <noscript> parser scope is un-sanitized by some libraries."""
    cid, canary = dxadyn.make_canary("noscript-breakout")
    assert '<noscript>' in canary and '</noscript>' in canary


def test_phase_1_2_m2_style_tag_breakout_uses_import():
    cid, canary = dxadyn.make_canary("style-tag-breakout")
    assert '<style>' in canary and '@import' in canary


def test_phase_1_2_m2_waf_mutation_library_reached_13():
    """Milestone 2 grows the mutation library from 8 to 13+."""
    assert len(dxadyn._WAF_MUTATIONS) >= 13
    names = {name for name, _ in dxadyn._WAF_MUTATIONS}
    assert names >= {
        "cr-in-tag", "form-feed-in-tag", "crlf-in-tag",
        "null-byte-tag", "backslash-tag",
    }


def test_phase_1_2_m2_cr_in_tag_uses_carriage_return():
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    cr = [t for t in triples if t[0] == "cr-in-tag"][0]
    assert '<dXsS\r>' in cr[1] and '<dXsS\r>' in cr[2]


def test_phase_1_2_m2_form_feed_in_tag_uses_form_feed():
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    ff = [t for t in triples if t[0] == "form-feed-in-tag"][0]
    assert '<dXsS\f>' in ff[1] and '<dXsS\f>' in ff[2]


def test_phase_1_2_m2_crlf_in_tag_uses_both_line_terminators():
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    crlf = [t for t in triples if t[0] == "crlf-in-tag"][0]
    assert '<dXsS\r\n>' in crlf[1] and '<dXsS\r\n>' in crlf[2]


def test_phase_1_2_m2_null_byte_tag_uses_percent_00():
    """Null byte is transported as %00 so it survives URL/form encoding."""
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    nb = [t for t in triples if t[0] == "null-byte-tag"][0]
    assert '<dXsS%00>' in nb[1] and '<dXsS%00>' in nb[2]


def test_phase_1_2_m2_backslash_tag_present():
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    bs = [t for t in triples if t[0] == "backslash-tag"][0]
    assert '<dXsS\\>' in bs[1] and '<dXsS\\>' in bs[2]


def test_phase_1_2_m2_all_new_variants_still_upgrade_to_executable():
    """All 13 new variants use the -breakout naming convention and must
    auto-upgrade to executable severity on HTML unencoded reflection."""
    new_names = {
        "svg-script-nested-breakout", "math-mtext-breakout",
        "object-data-breakout", "embed-src-breakout",
        "marquee-onstart-breakout", "select-onfocus-breakout",
        "textarea-onfocus-breakout", "form-formaction-breakout",
        "iframe-data-uri-breakout", "js-double-string-breakout",
        "anchor-href-javascript-breakout",
        "noscript-breakout", "style-tag-breakout",
    }
    for vname in new_names:
        _, sev = dxadyn._apply_ct_gate("unencoded", "body", "text/html",
                                        variant=vname)
        assert sev == "executable", f"{vname} did not upgrade to executable"


def test_phase_1_2_m2_shape_count_now_matches_full_matrix():
    """Post-milestone-2: 25+ variants x 13+ mutations grows the total
    canary shape space significantly beyond milestone-1."""
    all_variants = list(dxadyn.PAYLOAD_VARIANTS)
    out = list(dxadyn.make_canaries_for(all_variants, waf_bypass=True))
    # milestone 2 floor: 25 * (1 + 13) = 350
    assert len(out) >= 25 * (1 + 13)


def test_phase_1_2_m2_variant_library_is_diverse():
    """Sanity: even though a few variants may share the plain `<dXsS>`
    marker (body, script-breakout, js-double-string-breakout all rely on
    the same raw grep-marker after their respective string escapes), the
    library as a whole must have many distinct marker shapes -- otherwise
    the WAF-bypass fan-out collapses to duplicates."""
    markers = [m for _, m in dxadyn.PAYLOAD_VARIANTS.values()]
    unique = set(markers)
    # At least 75% distinct markers keeps the diversity claim honest.
    assert len(unique) >= int(0.75 * len(markers)), (
        f"only {len(unique)}/{len(markers)} distinct markers - "
        "variants are collapsing into the same shape"
    )


def test_phase_1_2_m2_every_variant_yields_unique_cid_per_call():
    """Regression guard: verdict ambiguity is prevented by CID uniqueness,
    not marker uniqueness. Each canary generation must produce a fresh cid
    so a shared marker (e.g. `<dXsS>`) never causes cross-variant matches."""
    all_variants = list(dxadyn.PAYLOAD_VARIANTS)
    out = list(dxadyn.make_canaries_for(all_variants, waf_bypass=True))
    cids = [t[1] for t in out]
    assert len(cids) == len(set(cids)), "duplicate cid across canaries"


# --- Phase 1.2 milestone 3: 25 -> 40+ variants, 13 -> 18+ mutations --------

_M3_NEW_VARIANTS = {
    # CSS-context
    "style-value-breakout", "css-comment-breakout", "css-import-breakout",
    # HTML5 dialog
    "dialog-onbeforetoggle-breakout", "dialog-oncancel-breakout",
    # Attribute-list injection (stays inside tag)
    "attr-inject-onerror-breakout", "attr-inject-onmouseover-breakout",
    # URL/navigation hijack
    "base-href-javascript-breakout", "meta-refresh-breakout",
    # SVG animation + audio complement
    "svg-animate-onbegin-breakout", "audio-onerror-breakout",
    # Legacy pre-formatted text
    "xmp-breakout",
    # JS complements
    "js-regex-breakout", "js-comment-close-breakout",
    # Web Components
    "template-shadow-breakout",
}

_M3_NEW_MUTATIONS = {
    "space-tab-mix", "triple-url-encode", "percent-lowercase",
    "split-cmt-suffix", "cr-space-mix",
}


def test_phase_1_2_m3_variant_library_reached_40():
    """Milestone 3 pushes the variant library past 40. Full DoD is ~50."""
    assert len(dxadyn.PAYLOAD_VARIANTS) >= 40
    assert set(dxadyn.PAYLOAD_VARIANTS) >= _M3_NEW_VARIANTS


def test_phase_1_2_m3_style_value_breakout_uses_url_function():
    """CSS style-attr value context: `; background:url(<dXsS>);` closes
    the current property and opens a new one that carries the marker."""
    cid, canary = dxadyn.make_canary("style-value-breakout")
    assert 'background:url(' in canary and '<dXsS>' in canary


def test_phase_1_2_m3_css_comment_breakout_closes_comment():
    """CSS multi-line comment closer: `*/` returns to declaration ctx."""
    cid, canary = dxadyn.make_canary("css-comment-breakout")
    assert canary.startswith(cid) and '*/' in canary


def test_phase_1_2_m3_css_import_breakout_closes_paren():
    """CSS url(): `);` closes the url() function so the next token can
    start a new declaration."""
    cid, canary = dxadyn.make_canary("css-import-breakout")
    assert ');' in canary and '<dXsS>' in canary


def test_phase_1_2_m3_dialog_variants_use_open_attr():
    """Both dialog variants must include `open` so the event fires without
    a call to .showModal()."""
    for vname in ("dialog-onbeforetoggle-breakout", "dialog-oncancel-breakout"):
        cid, canary = dxadyn.make_canary(vname)
        assert '<dialog open' in canary
        assert 'on' in canary  # onbeforetoggle / oncancel


def test_phase_1_2_m3_attr_inject_variants_stay_inside_tag():
    """attr-inject variants inject a handler WITHOUT closing the tag
    (bare `"` + handler + `//` swallow-comment, no `>` escape). This is
    a distinct mechanism from attr-breakout (which uses `">` to escape)."""
    for vname in ("attr-inject-onerror-breakout",
                  "attr-inject-onmouseover-breakout"):
        cid, canary = dxadyn.make_canary(vname)
        assert '"' in canary and '=1//' in canary
        # explicitly NOT closing the tag
        assert '">' not in canary


def test_phase_1_2_m3_base_href_javascript_present():
    """<base href=javascript:> rewrites every subsequent relative URL to
    javascript: context - one of the highest-impact single-tag XSS."""
    cid, canary = dxadyn.make_canary("base-href-javascript-breakout")
    assert '<base href=javascript:' in canary


def test_phase_1_2_m3_meta_refresh_uses_javascript_url():
    cid, canary = dxadyn.make_canary("meta-refresh-breakout")
    assert '<meta http-equiv=refresh' in canary
    assert 'javascript:' in canary


def test_phase_1_2_m3_svg_animate_uses_onbegin():
    """<svg><animate onbegin=1> fires without user interaction."""
    cid, canary = dxadyn.make_canary("svg-animate-onbegin-breakout")
    assert '<animate onbegin=1>' in canary


def test_phase_1_2_m3_audio_onerror_complements_video():
    cid, canary = dxadyn.make_canary("audio-onerror-breakout")
    assert '<audio><source onerror=1>' in canary


def test_phase_1_2_m3_xmp_breakout_closes_xmp():
    """<xmp> holds pre-formatted text; </xmp> resumes normal parsing."""
    cid, canary = dxadyn.make_canary("xmp-breakout")
    assert canary.startswith(cid) and '</xmp>' in canary


def test_phase_1_2_m3_js_regex_breakout_uses_slash_terminator():
    """JS regex literal terminator + semicolon returns to statement ctx."""
    cid, canary = dxadyn.make_canary("js-regex-breakout")
    assert '/;' in canary and '<dXsS>' in canary


def test_phase_1_2_m3_js_comment_close_uses_star_slash():
    cid, canary = dxadyn.make_canary("js-comment-close-breakout")
    assert '*/' in canary


def test_phase_1_2_m3_template_shadow_carries_script():
    """<template shadowrootmode=open> declarative shadow DOM; some
    sanitizers stop at the template boundary and leave inner script alive."""
    cid, canary = dxadyn.make_canary("template-shadow-breakout")
    assert 'shadowrootmode' in canary and '<script>' in canary


def test_phase_1_2_m3_all_new_variants_still_upgrade_to_executable():
    """Every m3 -breakout must ride the CT gate to executable severity."""
    for vname in _M3_NEW_VARIANTS:
        _, sev = dxadyn._apply_ct_gate("unencoded", "body", "text/html",
                                        variant=vname)
        assert sev == "executable", f"{vname} did not upgrade to executable"


def test_phase_1_2_m3_waf_mutation_library_reached_18():
    """Milestone 3 grows the mutation library from 13 to 18."""
    assert len(dxadyn._WAF_MUTATIONS) >= 18
    names = {name for name, _ in dxadyn._WAF_MUTATIONS}
    assert names >= _M3_NEW_MUTATIONS


def test_phase_1_2_m3_space_tab_mix_shape():
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    st = [t for t in triples if t[0] == "space-tab-mix"][0]
    assert '<dXsS \t>' in st[1] and '<dXsS \t>' in st[2]


def test_phase_1_2_m3_triple_url_encode_shape():
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    tu = [t for t in triples if t[0] == "triple-url-encode"][0]
    assert '%25253CdXsS%25253E' in tu[1] and '%25253CdXsS%25253E' in tu[2]


def test_phase_1_2_m3_percent_lowercase_uses_lowercase_hex():
    """RFC allows lowercase %-hex; some WAFs anchor uppercase only."""
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    pl = [t for t in triples if t[0] == "percent-lowercase"][0]
    assert '%3cdXsS%3e' in pl[1] and '%3cdXsS%3e' in pl[2]
    # explicitly NOT the uppercase form (which the existing url-encode uses)
    assert '%3CdXsS%3E' not in pl[1]


def test_phase_1_2_m3_split_cmt_suffix_shape():
    """Comment split AFTER the tag content, not inside the tag name."""
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    scs = [t for t in triples if t[0] == "split-cmt-suffix"][0]
    assert '<dXsS<!---->>' in scs[1] and '<dXsS<!---->>' in scs[2]


def test_phase_1_2_m3_cr_space_mix_shape():
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    cs = [t for t in triples if t[0] == "cr-space-mix"][0]
    assert '<dXsS\r >' in cs[1] and '<dXsS\r >' in cs[2]


def test_phase_1_2_m3_shape_count_reached_760():
    """Post-milestone-3: 40 variants x 18 mutations grows to 40 x 19 = 760
    canary shapes with --variants all --waf-bypass."""
    all_variants = list(dxadyn.PAYLOAD_VARIANTS)
    out = list(dxadyn.make_canaries_for(all_variants, waf_bypass=True))
    # milestone 3 floor: 40 * (1 + 18) = 760
    assert len(out) >= 760


def test_phase_1_2_m3_marker_diversity_stays_healthy():
    """After 40 variants some intentional marker sharing exists (bare
    <dXsS> across body/script-breakout/js-double-string/js-regex; */<dXsS>
    across css-comment/js-comment-close) - keep the invariant at >= 75%."""
    markers = [m for _, m in dxadyn.PAYLOAD_VARIANTS.values()]
    unique = set(markers)
    assert len(unique) >= int(0.75 * len(markers)), (
        f"only {len(unique)}/{len(markers)} distinct markers"
    )


# --- Phase 1.2 milestone 4: 44 -> 50 variants (Phase 1.2 complete) ---------

_M4_NEW_VARIANTS = {
    "link-onerror-breakout",
    "frame-onload-breakout",
    "track-onerror-breakout",
    "input-onauxclick-breakout",
    "button-formtarget-breakout",
    "input-onfocusin-breakout",
}


def test_phase_1_2_m4_variant_library_reached_50():
    """Milestone 4 closes Phase 1.2 with the variant library at 50.
    Mutation library stays at 18 (honest ceiling for transform-both-
    compatible shapes; entity-encoded families need Phase 2 browser
    detection which uses a different marker/canary transform)."""
    assert len(dxadyn.PAYLOAD_VARIANTS) >= 50
    assert set(dxadyn.PAYLOAD_VARIANTS) >= _M4_NEW_VARIANTS


def test_phase_1_2_m4_link_onerror_present():
    """<link rel=stylesheet href=x onerror=1>. Sanitizers focused on
    script/img often miss <link> event handlers."""
    cid, canary = dxadyn.make_canary("link-onerror-breakout")
    assert '<link rel=stylesheet href=x onerror=1>' in canary


def test_phase_1_2_m4_frame_onload_wraps_in_frameset():
    """<frameset>...</frameset> is mandatory scope for <frame>."""
    cid, canary = dxadyn.make_canary("frame-onload-breakout")
    assert '<frameset>' in canary and '<frame onload=1>' in canary
    assert '</frameset>' in canary


def test_phase_1_2_m4_track_onerror_uses_video_wrapper():
    """<track> needs a <video>/<audio> parent to be parsed."""
    cid, canary = dxadyn.make_canary("track-onerror-breakout")
    assert '<video>' in canary and '<track src=x onerror=1>' in canary


def test_phase_1_2_m4_input_onauxclick_present():
    """Middle/right-click event handler - rarely blocked by name."""
    cid, canary = dxadyn.make_canary("input-onauxclick-breakout")
    assert '<input onauxclick=1' in canary


def test_phase_1_2_m4_button_formtarget_opens_new_tab():
    """formtarget=_blank distinguishes this from form-formaction-breakout:
    the exploit fires in a new tab, defeating iframe-sandbox."""
    cid, canary = dxadyn.make_canary("button-formtarget-breakout")
    assert 'formaction=javascript:1' in canary
    assert 'formtarget=_blank' in canary


def test_phase_1_2_m4_input_onfocusin_uses_autofocus():
    """onfocusin bubbles; combined with autofocus fires without user
    interaction, same trigger as input-autofocus-breakout but different
    event handler name so blocklists focused on `onfocus` slip."""
    cid, canary = dxadyn.make_canary("input-onfocusin-breakout")
    assert 'onfocusin=1' in canary and 'autofocus' in canary


def test_phase_1_2_m4_all_new_variants_upgrade_to_executable():
    """All m4 -breakout variants must ride the CT gate to executable."""
    for vname in _M4_NEW_VARIANTS:
        _, sev = dxadyn._apply_ct_gate("unencoded", "body", "text/html",
                                        variant=vname)
        assert sev == "executable", f"{vname} did not upgrade to executable"


def test_phase_1_2_m4_shape_count_reached_full_dod():
    """Post-m4: 50 variants x (1 + 18 mutations) = 950 canary shapes with
    --variants all --waf-bypass. This closes the Phase 1.2 DoD.

    Mutation library stopped at 18 by design - see the roadmap note on
    transform-both saturation. Entity-encoded families arrive in Phase
    2 where the browser detects the client-side double-decode."""
    all_variants = list(dxadyn.PAYLOAD_VARIANTS)
    out = list(dxadyn.make_canaries_for(all_variants, waf_bypass=True))
    # DoD floor: 50 * (1 + 18) = 950
    assert len(out) >= 950
    assert len(dxadyn._WAF_MUTATIONS) == 18, (
        "Mutation library grew past the documented ceiling of 18 - if this "
        "was intentional, update the ceiling note in dxadyn.py"
    )


def test_phase_1_2_m4_marker_diversity_still_healthy_at_50():
    """Same 75% floor across the wider library."""
    markers = [m for _, m in dxadyn.PAYLOAD_VARIANTS.values()]
    unique = set(markers)
    assert len(unique) >= int(0.75 * len(markers)), (
        f"only {len(unique)}/{len(markers)} distinct markers at 50 variants"
    )


# --- probe_form / probe_link now accept variants + waf_bypass ---------------

def test_probe_form_variants_kwarg_fan_out():
    """probe_form runs each variant × each field: two variants + one field
    with a raw-echoing form should produce two findings, one per variant."""
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.OPENER = dxadyn._opener()
    srv = HTTPServer(("127.0.0.1", 0), _Reflector)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        # /r form (see fixture at top of file) echoes q raw in body context
        form = {"action": f"http://127.0.0.1:{port}/r", "method": "get",
                "fields": {"q": ""}}
        findings = dxadyn.probe_form(form, variants=["body", "attr-breakout"])
    finally:
        srv.shutdown()
    variants_seen = {f["variant"] for f in findings}
    assert "body" in variants_seen
    assert "attr-breakout" in variants_seen


def test_probe_link_variants_kwarg_fan_out():
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.OPENER = dxadyn._opener()
    srv = HTTPServer(("127.0.0.1", 0), _Reflector)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        findings = dxadyn.probe_link(f"http://127.0.0.1:{port}/r?q=x",
                                     variants=["body", "attr-breakout"])
    finally:
        srv.shutdown()
    variants_seen = {f["variant"] for f in findings}
    assert "body" in variants_seen
    assert "attr-breakout" in variants_seen


def test_probe_headers_variants_kwarg_fan_out():
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.OPENER = dxadyn._opener()
    srv = HTTPServer(("127.0.0.1", 0), _HeaderEcho)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        findings = dxadyn.probe_headers(
            f"http://127.0.0.1:{port}/", ["X-Forwarded-For"],
            variants=["body", "attr-breakout"])
    finally:
        srv.shutdown()
    variants_seen = {f["variant"] for f in findings}
    assert "body" in variants_seen
    assert "attr-breakout" in variants_seen


# --- crawl(): variant-aware dedup key ---------------------------------------

def test_crawl_dedup_key_is_variant_aware():
    """Two variants that both fire on the same param must NOT collapse into
    one row after crawl()'s dedup step - the dedup key includes variant now."""
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.OPENER = dxadyn._opener()
    srv = HTTPServer(("127.0.0.1", 0), _Reflector)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        # crawl on the fixture index (has /r + /rs forms). Two variants on /r's q.
        findings = dxadyn.crawl(f"http://127.0.0.1:{port}/", 1,
                                variants=["body", "attr-breakout"])
    finally:
        srv.shutdown()
    # collect findings on /r's q param
    r_q = [f for f in findings if f["url"].endswith("/r") and f["param"] == "q"]
    variants = {f["variant"] for f in r_q}
    assert "body" in variants
    assert "attr-breakout" in variants


# --- _finding() picks up variant into severity via CT gate ------------------

def test_finding_helper_variant_upgrades_severity_on_html():
    """A title-breakout variant reflection on text/html gets severity=executable
    via the CT gate variant-aware upgrade path."""
    f = dxadyn._finding("http://x/", "GET", "q", "unencoded", 200,
                        context="title", canary_id="dxaXX",
                        content_type="text/html", variant="title-breakout")
    assert f["severity"] == "executable"
    assert f["variant"] == "title-breakout"


def test_finding_helper_default_variant_stays_body_breakout_req():
    """No variant kwarg -> defaults to 'body'; title context stays breakout-req."""
    f = dxadyn._finding("http://x/", "GET", "q", "unencoded", 200,
                        context="title", canary_id="dxaXX",
                        content_type="text/html")
    assert f["variant"] == "body"
    assert f["severity"] == "breakout-req"


def test_probe_stored_multi_variant_produces_findings_per_variant():
    """When two variants both reflect raw, we get one finding per variant
    (not deduped - different cids)."""
    _V34_DB["json"] = None
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.OPENER = dxadyn._opener()
    srv = HTTPServer(("127.0.0.1", 0), _V34App)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        # _V34App stores json body and reflects raw on /viewj
        # Both body and attr-breakout variants should be flagged
        findings, cid = dxadyn.probe_stored(
            f"http://127.0.0.1:{port}/api/tags", target_field="",
            extra_fields={}, check_urls=[f"http://127.0.0.1:{port}/viewj"],
            json_body='{"tags":"{CANARY}"}', csrf_field="",
            variants=["body", "attr-breakout"])
    finally:
        srv.shutdown()
    variants_seen = {f["variant"] for f in findings}
    assert "body" in variants_seen
    assert "attr-breakout" in variants_seen


# --- HTML report ------------------------------------------------------------

def test_render_html_empty_produces_valid_page():
    out = dxadyn.render_html([], "http://x/", "reflected", {"depth": "0"})
    assert "<title>dxadyn report" in out
    assert "No unencoded reflections found" in out
    assert "http://x/" in out


def test_render_html_with_findings_shows_row_and_badges():
    findings = [
        {"url": "http://x/", "method": "GET", "param": "q",
         "reflection": "unencoded", "confidence": "high", "status": 200,
         "origin": "reflected"},
        {"check_url": "http://x/tag/z", "field": "tags",
         "reflection": "attr-only", "confidence": "medium",
         "sub_status": 200, "check_status": 200, "auto_discovered": True},
    ]
    out = dxadyn.render_html(findings, "http://x/", "stored-auto",
                             {"canary_id": "dxa12345"})
    assert "unencoded" in out and "attr-only" in out
    assert "reflected" in out and "stored-auto" in out
    assert "dxa12345" in out
    # header row and both data rows
    assert out.count("<tr>") >= 3


# --- v3.4: JSON body + stored header target ---------------------------------

_V34_DB = {"json": None, "hdr": None}


class _V34App(BaseHTTPRequestHandler):
    """Two 'stored' surfaces:
      POST /api/tags {"tags": "..."}  stores json -> renders RAW on /viewj
      GET /  with X-Forwarded-Fake header  stores hdr -> renders RAW on /viewh
    """
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        p = urlparse(self.path)
        if p.path == "/log":
            xff = self.headers.get("X-Forwarded-Fake")
            if xff:
                _V34_DB["hdr"] = xff
            return self._send(200, "logged")
        if p.path == "/viewj":
            return self._send(200, f"<h1>tag: {_V34_DB['json']}</h1>")
        if p.path == "/viewh":
            return self._send(200, f"<p>lastIP: {_V34_DB['hdr']}</p>")
        if p.path == "/":
            return self._send(200, '<a href="/viewj">j</a><a href="/viewh">h</a>')
        return self._send(404, "?")

    def do_POST(self):
        import json as _json
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode()
        if self.path == "/api/tags":
            try:
                obj = _json.loads(raw)
                _V34_DB["json"] = obj.get("tags")
                return self._send(200, "{\"ok\":true}", "application/json")
            except Exception:                                # noqa: BLE001
                return self._send(400, "bad json")
        return self._send(404, "?")


def test_submit_json_stores_canary_and_view_reflects_raw():
    _V34_DB["json"] = None
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.OPENER = dxadyn._opener()
    srv = HTTPServer(("127.0.0.1", 0), _V34App)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        findings, cid = dxadyn.probe_stored(
            f"http://127.0.0.1:{port}/api/tags", target_field="",
            extra_fields={}, check_urls=[f"http://127.0.0.1:{port}/viewj"],
            json_body='{"tags":"{CANARY}"}', csrf_field="")
    finally:
        srv.shutdown()
    assert findings, "json-body stored XSS must be detected via /viewj"
    assert findings[0]["reflection"] == "unencoded"
    assert findings[0]["field"] == "json"
    assert _V34_DB["json"] == cid + '"<dXsS>'


def test_submit_header_target_stores_canary_and_view_reflects():
    _V34_DB["hdr"] = None
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.OPENER = dxadyn._opener()
    srv = HTTPServer(("127.0.0.1", 0), _V34App)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        findings, cid = dxadyn.probe_stored(
            f"http://127.0.0.1:{port}/log", target_field="",
            extra_fields={}, check_urls=[f"http://127.0.0.1:{port}/viewh"],
            method="get", header_target="X-Forwarded-Fake", csrf_field="")
    finally:
        srv.shutdown()
    assert findings, "header-target stored XSS must be detected via /viewh"
    assert findings[0]["reflection"] == "unencoded"
    assert findings[0]["field"] == "header:X-Forwarded-Fake"
    # header must not leak into EXTRA_HEADERS after the submit
    assert "X-Forwarded-Fake" not in dxadyn.EXTRA_HEADERS


def test_submit_json_escapes_quote_in_canary_correctly():
    """The canary contains a raw `"` — the json_body template must remain
    valid JSON after {CANARY} substitution."""
    tmpl = '{"tags":"{CANARY}"}'
    fake_cid = 'dxa12345678'
    fake_canary = fake_cid + '"<dXsS>'
    # simulate what _submit_json does internally
    safe = tmpl.replace("{CANARY}", fake_canary
        .replace("\\", "\\\\").replace('"', '\\"'))
    import json as _json
    obj = _json.loads(safe)                                  # must not raise
    assert obj["tags"] == fake_canary


# --- v3.2: auto-discover (crawl-after-submit) -------------------------------

_AUTO_DB = {}


class _AutoApp(BaseHTTPRequestHandler):
    """Bludit-shaped: POST /post stores by slug; homepage has a link to
    /tag/<slug> which renders the stored value raw. Auto-check must find it
    from the homepage crawl - no explicit --check URL given."""
    def log_message(self, *a):
        pass

    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        p = urlparse(self.path)
        if p.path == "/":
            links = "".join(f'<a href="/tag/{k}">{k}</a> ' for k in _AUTO_DB)
            return self._send(200, f"<html><body>home {links}</body></html>")
        if p.path == "/post":
            return self._send(200, '<form method="post" action="/post">'
                                   '<input name="tag"><input type="submit"></form>')
        if p.path.startswith("/tag/"):
            key = p.path.split("/", 2)[2]
            return self._send(200, f"<h1>tag: {_AUTO_DB.get(key, '(?)')}</h1>")
        return self._send(404, "nope")

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        fields = parse_qs(self.rfile.read(length).decode(), keep_blank_values=True)
        if self.path == "/post":
            tag = fields.get("tag", [""])[0]
            key = _sluggy(tag)
            _AUTO_DB[key] = tag                              # store raw
            return self._send(200, f"stored key={key}")
        return self._send(404, "nope")


def test_auto_check_discovers_and_flags_stored_reflection():
    _AUTO_DB.clear()
    dxadyn.OPENER = dxadyn._opener()
    dxadyn.EXTRA_HEADERS.clear()
    srv = HTTPServer(("127.0.0.1", 0), _AutoApp)
    port = srv.server_address[1]
    base = f"http://127.0.0.1:{port}"
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        findings, cid, meta = dxadyn.probe_stored_auto(
            base + "/post", "tag", extra_fields={},
            seed_urls=[base + "/"], csrf_field=""     # this fixture has no CSRF
        )
    finally:
        srv.shutdown()

    # exactly one page (the /tag/<slug>) should carry the canary raw
    assert findings, "auto-check must locate the /tag page carrying the canary"
    assert findings[0]["reflection"] == "unencoded"
    assert "/tag/" in findings[0]["check_url"]
    assert findings[0]["auto_discovered"] is True
    assert meta["candidates"] >= 2                            # home + at least the tag page


def test_all_links_skips_junk_and_dedupes():
    body = '<a href="/a">A</a><a href="/a">A2</a><a href="mailto:x">M</a>' \
           '<a href="javascript:1">J</a><a href="#top">T</a><a href="/b?x=1">B</a>'
    got = dxadyn._all_links("http://h/", body)
    assert got == ["http://h/a", "http://h/b?x=1"]


def test_stored_mode_auth_and_verdict():
    _TAGS_DB.clear()
    # fresh cookie jar per test so state doesn't bleed
    dxadyn.OPENER = dxadyn._opener()
    srv = HTTPServer(("127.0.0.1", 0), _StoredApp)
    port = srv.server_address[1]
    base = f"http://127.0.0.1:{port}"
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        ok = dxadyn.login(base + "/login", "admin", "wrongpw")
        assert not ok, "wrong password must not authenticate"
        ok = dxadyn.login(base + "/login", "admin", "labpass")
        assert ok, "correct credentials should authenticate on the fixture"

        # RAW view page: must flag unencoded
        findings, cid = dxadyn.probe_stored(
            base + "/new", "tags",
            extra_fields={"title": "t"},
            check_urls=[base + "/view/{CID}-dxss"],
        )
        assert findings, "stored XSS must be detected on the raw /view page"
        assert findings[0]["reflection"] == "unencoded"
        assert cid in findings[0]["check_url"]

        # SAFE view page: no finding
        findings2, _ = dxadyn.probe_stored(
            base + "/new", "tags",
            extra_fields={"title": "t"},
            check_urls=[base + "/viewsafe/{CID}-dxss"],
        )
        assert not findings2, "escaped page must not be flagged"
    finally:
        srv.shutdown()


# --- Phase 0.2: false-negative discipline (2026-09-26) ----------------------
#
# Tests below verify SKIPPED_SUBMITS + _classify_response so that a scan
# which finds "no reflections" can be distinguished from a scan whose
# submits were actively blocked by 403 / 429 / WAF-flavoured 4xx.

def _reset_skip_state():
    dxadyn.SKIPPED_SUBMITS.clear()
    dxadyn.VERBOSE = False
    dxadyn.WAF_LOG_FILE = None


def test_classify_response_forbidden_bare():
    """Bare 403 with no WAF-language body -> classified as forbidden."""
    was, reason = dxadyn._classify_response(403, "")
    assert was is True
    assert reason == "forbidden"


def test_classify_response_waf_403():
    """403 with a WAF/Cloudflare-style body -> classified as waf-403."""
    was, reason = dxadyn._classify_response(
        403, "<html><body>Access denied by Cloudflare (Incident ID 12).</body>")
    assert was is True
    assert reason == "waf-403"


def test_classify_response_waf_400():
    """400 with WAF-language body -> waf-400. Plain 400 (validation error)
    does NOT trip the skip - that response might still echo the canary."""
    assert dxadyn._classify_response(400, "field required")[0] is False
    assert dxadyn._classify_response(400, "blocked by security policy")[1] == "waf-400"


def test_classify_response_rate_limit_and_server_error():
    assert dxadyn._classify_response(429, "")[1] == "rate-limit"
    assert dxadyn._classify_response(502, "bad gateway")[1] == "server-error"
    assert dxadyn._classify_response(None, "")[1] == "connection-error"


def test_classify_response_healthy_200():
    """200 (or any 2xx / 3xx) is NEVER a skip."""
    was, reason = dxadyn._classify_response(200, "welcome")
    assert was is False and reason is None
    assert dxadyn._classify_response(301, "")[0] is False


def test_record_skip_appends_and_respects_verbose(capsys):
    _reset_skip_state()
    dxadyn._record_skip("dxa123", "http://x/", "post", "body",
                        403, "waf-403", canary='dxa123"<dXsS>')
    assert len(dxadyn.SKIPPED_SUBMITS) == 1
    e = dxadyn.SKIPPED_SUBMITS[0]
    assert e["reason"] == "waf-403"
    assert e["method"] == "POST"
    assert e["variant"] == "body"

    # VERBOSE=False = nothing printed to stderr
    assert "skip" not in capsys.readouterr().err

    dxadyn.VERBOSE = True
    dxadyn._record_skip("dxa456", "http://x/", "get", "body",
                        429, "rate-limit")
    err = capsys.readouterr().err
    assert "[skip]" in err and "rate-limit" in err and "dxa456" in err
    _reset_skip_state()


def test_maybe_record_skip_short_circuits_on_reflection():
    """If verdict was 'unencoded' / 'attr-only', we DO NOT record a skip
    even if the response status was WAF-shaped. A finding trumps skip."""
    _reset_skip_state()
    dxadyn._maybe_record_skip("unencoded", "dxaZZ", "http://x/", "post",
                              "body", 403, "blocked", canary='dxaZZ"<dXsS>')
    assert dxadyn.SKIPPED_SUBMITS == []
    dxadyn._maybe_record_skip("absent", "dxaYY", "http://x/", "post",
                              "body", 403, "blocked", canary='dxaYY"<dXsS>')
    assert len(dxadyn.SKIPPED_SUBMITS) == 1
    _reset_skip_state()


class _WafReflector(BaseHTTPRequestHandler):
    """Mock endpoint that returns 403 with a Cloudflare-shaped body when the
    canary is in the query, otherwise reflects raw. Used to check that a
    probe_link run records skips instead of silently reporting nothing."""
    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query).get("q", [""])[0]
        if "dxa" in q:                                # canary detected -> block
            self.send_response(403)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"Access denied by Cloudflare firewall.")
        else:
            body = f"<div>{q}</div>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(body.encode())


def test_probe_link_records_waf_skip_when_all_submits_blocked():
    """A hostile-target reflector 403s every canary. Result: 0 findings AND
    SKIPPED_SUBMITS full - which is the whole point of Phase 0.2."""
    _reset_skip_state()
    srv = HTTPServer(("127.0.0.1", 0), _WafReflector)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        findings = dxadyn.probe_link(
            f"http://127.0.0.1:{port}/?q=x",
            variants=["body", "attr-breakout"])
    finally:
        srv.shutdown()
    assert findings == [], "should be silent on findings"
    assert len(dxadyn.SKIPPED_SUBMITS) == 2                # 1 per variant
    for e in dxadyn.SKIPPED_SUBMITS:
        assert e["status"] == 403
        assert e["reason"] == "waf-403"
    _reset_skip_state()


def test_probe_form_records_skip_on_blocked_submit():
    """A form-mode probe against a WAF-shaped 403 backend also records skips."""
    _reset_skip_state()
    srv = HTTPServer(("127.0.0.1", 0), _WafReflector)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        form = {"action": f"http://127.0.0.1:{port}/", "method": "get",
                "fields": {"q": ""}}
        findings = dxadyn.probe_form(form, variants=["body"])
    finally:
        srv.shutdown()
    assert findings == []
    assert len(dxadyn.SKIPPED_SUBMITS) == 1
    assert dxadyn.SKIPPED_SUBMITS[0]["reason"] == "waf-403"
    _reset_skip_state()


def test_waf_log_file_written(tmp_path):
    """--waf-log FILE persists rejected canaries as tab-separated rows."""
    _reset_skip_state()
    log_path = tmp_path / "waf.log"
    dxadyn.WAF_LOG_FILE = str(log_path)
    dxadyn._record_skip("dxaLOG", "http://x/", "post", "body",
                        403, "waf-403", canary='dxaLOG"<dXsS>')
    content = log_path.read_text(encoding="utf-8")
    assert "waf-403" in content and "dxaLOG" in content
    fields = content.strip().split("\t")
    assert fields[0] == "waf-403"
    assert fields[2] == "dxaLOG"
    _reset_skip_state()


# --- Phase 1.1: concurrency + rate limit + jitter (2026-09-27) --------------
#
# These tests exercise the module-level primitives and the parallel paths in
# probe_form / probe_headers. Wall-clock is asserted with generous slack so
# the tests stay reliable on slower CI runners.

import time as _time


def _reset_concurrency_state():
    dxadyn.PARALLEL_WORKERS = 1
    dxadyn._RATE_LIMITER = None
    dxadyn.JITTER_MS_MIN = 0
    dxadyn.JITTER_MS_MAX = 0


def test_parallel_map_sequential_matches_input_order():
    """PARALLEL_WORKERS=1 -> results in input order (no thread pool spawned)."""
    _reset_concurrency_state()
    out = dxadyn._parallel_map(lambda x: x * 10, [1, 2, 3, 4])
    assert out == [10, 20, 30, 40]


def test_parallel_map_parallel_preserves_input_order():
    """PARALLEL_WORKERS>1 -> pool.map still returns in INPUT order even when
    tasks finish out of arrival order. This is the property downstream code
    relies on for variant ordering in the finding list."""
    _reset_concurrency_state()
    dxadyn.PARALLEL_WORKERS = 4
    def _slow_reversed(x):
        # earlier x sleeps longer -> without ordered map, output would be reversed
        _time.sleep(0.05 * (5 - x))
        return x * 10
    try:
        out = dxadyn._parallel_map(_slow_reversed, [1, 2, 3, 4])
    finally:
        _reset_concurrency_state()
    assert out == [10, 20, 30, 40]


def test_parallel_map_wall_clock_beats_sequential():
    """Parallel-4 on 4x 0.15s sleeps should finish nearer 0.15s than 0.60s.
    Assertion has slack (< 0.40s) so CI flakiness doesn't fail it."""
    _reset_concurrency_state()
    dxadyn.PARALLEL_WORKERS = 4
    try:
        t0 = _time.monotonic()
        dxadyn._parallel_map(lambda _: _time.sleep(0.15), [None] * 4)
        elapsed = _time.monotonic() - t0
    finally:
        _reset_concurrency_state()
    assert elapsed < 0.40, f"expected parallel < 0.40s, got {elapsed:.2f}s"


def test_token_bucket_rate_gates_bursts():
    """A 5/s bucket must NOT let 10 immediate takes through in under
    ~1 second. Assertion: at least 5 tokens/second average."""
    b = dxadyn._TokenBucket(5)
    t0 = _time.monotonic()
    for _ in range(6):                  # 6 tokens against a 5/s (5 capacity) bucket
        b.take()
    elapsed = _time.monotonic() - t0
    # first 5 tokens are free (capacity), 6th needs ~0.2s refill
    assert elapsed >= 0.15, (
        f"6 takes on a 5/s bucket should take >= 0.15s, got {elapsed:.3f}s")


def test_jitter_gate_respects_bounds():
    """JITTER_MS_MIN..MAX bounds the per-request sleep. Set 50-80 ms, run
    fetch through mock, check that 3 runs each waited >= 50 ms."""
    _reset_concurrency_state()
    dxadyn.JITTER_MS_MIN = 50
    dxadyn.JITTER_MS_MAX = 80
    try:
        for _ in range(3):
            t0 = _time.monotonic()
            dxadyn._jitter_gate()
            slept_ms = (_time.monotonic() - t0) * 1000
            assert 45 <= slept_ms <= 120, (
                f"jitter sleep out of expected bounds: {slept_ms:.1f}ms")
    finally:
        _reset_concurrency_state()


def test_fetch_extra_header_injects_per_request_no_global_leak():
    """fetch(extra={'X-Custom': 'v'}) sends the header for THIS call only;
    the module-level EXTRA_HEADERS stays empty afterwards. This is what
    makes probe_headers thread-safe under --parallel."""
    dxadyn.EXTRA_HEADERS.clear()
    srv = HTTPServer(("127.0.0.1", 0), _HeaderEcho)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        st, _, body, _ct = dxadyn.fetch(
            f"http://127.0.0.1:{port}/", extra={"X-Forwarded-For": "SENTINEL42"})
        assert "SENTINEL42" in body
        assert dxadyn.EXTRA_HEADERS == {}, "extra= must not leak to globals"
    finally:
        srv.shutdown()


def test_probe_headers_parallel_still_produces_correct_findings():
    """probe_headers under PARALLEL_WORKERS > 1 must produce the same
    findings as the sequential baseline (order-independent set of variants).
    Uses ThreadingHTTPServer - the default HTTPServer is single-threaded
    on the SERVER side, so parallel client threads would just queue there."""
    _reset_concurrency_state()
    dxadyn.EXTRA_HEADERS.clear()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _HeaderEcho)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        dxadyn.PARALLEL_WORKERS = 1
        seq = dxadyn.probe_headers(
            f"http://127.0.0.1:{port}/", ["X-Forwarded-For", "Referer"],
            variants=["body", "attr-breakout"])
        dxadyn.PARALLEL_WORKERS = 6
        par = dxadyn.probe_headers(
            f"http://127.0.0.1:{port}/", ["X-Forwarded-For", "Referer"],
            variants=["body", "attr-breakout"])
    finally:
        srv.shutdown()
        _reset_concurrency_state()
    # same variant set + same param set irrespective of order.
    # _HeaderEcho reflects X-Forwarded-For raw but HTML-escapes Referer
    # (safe endpoint by design), so we only expect findings on X-Forwarded-For.
    def _fingerprint(fs):
        return sorted((f["param"], f["variant"], f["reflection"]) for f in fs)
    assert _fingerprint(seq) == _fingerprint(par)
    assert len(par) == 2                # 1 vuln header x 2 variants
    assert {f["param"] for f in par} == {"header:X-Forwarded-For"}


def test_probe_form_parallel_wall_clock_faster_than_sequential():
    """The concrete Phase 1.1 wall-clock win: 8-shape probe on a mock server
    that sleeps 100 ms per request. Sequential ~ 0.8s; parallel-8 should
    beat 0.35s (2x floor)."""
    _reset_concurrency_state()

    class _SlowReflector(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass
        def do_GET(self):
            _time.sleep(0.1)                          # slow endpoint
            u = urlparse(self.path)
            q = parse_qs(u.query).get("q", [""])[0]
            body = f"<div>{q}</div>".encode()
            self.send_response(200); self.send_header("Content-Type", "text/html")
            self.end_headers(); self.wfile.write(body)

    # ThreadingHTTPServer so the server can actually serve requests
    # concurrently - the whole point of the parallel-speedup assertion.
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _SlowReflector)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    form = {"action": f"http://127.0.0.1:{port}/r", "method": "get",
            "fields": {"q": ""}}
    try:
        # sequential baseline: 8 variants x 100 ms = ~0.8s
        dxadyn.PARALLEL_WORKERS = 1
        t0 = _time.monotonic()
        seq = dxadyn.probe_form(form, variants=["body", "attr-breakout"],
                                waf_bypass=True)          # 2 * (1+4) = 10 tasks; but 1 field
        seq_t = _time.monotonic() - t0
        # parallel-8: same 10 tasks concurrent -> should beat 0.35s
        dxadyn.PARALLEL_WORKERS = 8
        t0 = _time.monotonic()
        par = dxadyn.probe_form(form, variants=["body", "attr-breakout"],
                                waf_bypass=True)
        par_t = _time.monotonic() - t0
    finally:
        srv.shutdown()
        _reset_concurrency_state()
    # both runs saw the reflection on every shape
    assert len(seq) == len(par)
    # parallel should be a lot faster than sequential
    assert par_t < seq_t * 0.6, (
        f"expected parallel much faster; seq={seq_t:.2f}s par={par_t:.2f}s")


def test_parallel_map_short_circuits_for_single_item():
    """A one-item list must not spawn a thread pool - keeps overhead 0 for
    the common (single-field, single-variant) case."""
    _reset_concurrency_state()
    dxadyn.PARALLEL_WORKERS = 8
    try:
        # if it tried to spawn workers on a 0-item list it would blow up
        assert dxadyn._parallel_map(lambda x: x, []) == []
        # one-item skips the pool
        assert dxadyn._parallel_map(lambda x: x * 2, [7]) == [14]
    finally:
        _reset_concurrency_state()


# --- Phase 3.2: blind XSS payload family ------------------------------------

_BLIND_VARIANT_NAMES = {
    "blind-img", "blind-script", "blind-fetch",
    "blind-svg-onload", "blind-iframe",
}


@pytest.fixture(autouse=False)
def _blind_callback_set():
    """Set BLIND_CALLBACK for the duration of a test and restore on exit."""
    old = dxadyn.BLIND_CALLBACK
    dxadyn.BLIND_CALLBACK = "http://cb.test:9999"
    try:
        yield "http://cb.test:9999"
    finally:
        dxadyn.BLIND_CALLBACK = old


def test_phase_3_2_blind_variants_registered():
    """The blind family has five documented shapes."""
    assert set(dxadyn.BLIND_VARIANTS) == _BLIND_VARIANT_NAMES


def test_phase_3_2_blind_variants_are_not_in_payload_variants():
    """Blind variants are opt-in via BLIND_VARIANTS; they must NOT leak
    into PAYLOAD_VARIANTS or `--variants all` would fire them without
    a callback configured."""
    for name in _BLIND_VARIANT_NAMES:
        assert name not in dxadyn.PAYLOAD_VARIANTS


def test_phase_3_2_blind_templates_carry_both_placeholders():
    """Every blind variant's suffix must contain both {CALLBACK} and
    {CID} placeholders - otherwise the substitution is malformed."""
    for name, (suffix, marker) in dxadyn.BLIND_VARIANTS.items():
        assert "{CALLBACK}" in suffix, f"{name}: no {{CALLBACK}} in suffix"
        assert "{CID}" in suffix, f"{name}: no {{CID}} in suffix"
        assert "{CALLBACK}" in marker, f"{name}: no {{CALLBACK}} in marker"
        assert "{CID}" in marker, f"{name}: no {{CID}} in marker"


def test_phase_3_2_make_canary_substitutes_placeholders(_blind_callback_set):
    cid, canary = dxadyn.make_canary("blind-img")
    assert cid.startswith("dxa") and len(cid) == 11
    assert "http://cb.test:9999" in canary
    assert cid in canary
    # Templates gone - no unresolved placeholder in the sent shape.
    assert "{CALLBACK}" not in canary and "{CID}" not in canary


def test_phase_3_2_make_canary_cid_is_inside_url_not_prepended(_blind_callback_set):
    """Blind payloads embed cid IN the URL rather than prepending it.
    Prepending would produce `dxaCAFE"><img src=...>` where the leading
    dxaCAFE lands as text in the DOM - noise, not signal."""
    cid, canary = dxadyn.make_canary("blind-img")
    # cid must NOT appear at position 0 of the canary (that would mean
    # it was prepended before the payload)
    assert not canary.startswith(cid)
    # But it must appear inside the URL after /c/
    assert f"/c/{cid}" in canary


def test_phase_3_2_make_canaries_for_yields_blind_with_callback(_blind_callback_set):
    """make_canaries_for(['blind-img']) yields exactly one tuple with
    both placeholders substituted."""
    out = list(dxadyn.make_canaries_for(["blind-img"]))
    assert len(out) == 1
    vname, cid, canary, marker = out[0]
    assert vname == "blind-img"
    assert cid in canary
    assert "http://cb.test:9999" in canary
    assert "http://cb.test:9999" in marker


def test_phase_3_2_make_canaries_for_skips_blind_without_callback():
    """No BLIND_CALLBACK set -> blind variants are silently skipped so
    a `--variants all` run doesn't blow up on the missing config."""
    dxadyn.BLIND_CALLBACK = ""
    out = list(dxadyn.make_canaries_for(["blind-img", "body"]))
    variant_names = {t[0] for t in out}
    assert "blind-img" not in variant_names
    assert "body" in variant_names


def test_phase_3_2_blind_variants_do_not_participate_in_waf_mutations(_blind_callback_set):
    """WAF mutations transform '<dXsS>' - the blind payload structure
    would be broken by that. Blind variants explicitly opt out of
    waf_bypass so the URL stays intact."""
    out = list(dxadyn.make_canaries_for(["blind-img"], waf_bypass=True))
    # Only the base variant, no `blind-img/case` etc.
    assert len(out) == 1
    assert "/" not in out[0][0]  # no mutation suffix in the name


def test_phase_3_2_all_five_blind_shapes_substitute_cleanly(_blind_callback_set):
    for name in _BLIND_VARIANT_NAMES:
        out = list(dxadyn.make_canaries_for([name]))
        assert len(out) == 1, f"{name} did not yield"
        vname, cid, canary, marker = out[0]
        assert "{CALLBACK}" not in canary and "{CID}" not in canary
        assert "{CALLBACK}" not in marker and "{CID}" not in marker
        assert cid in canary


def test_phase_3_2_blind_fetch_carries_cookie_exfil_shape(_blind_callback_set):
    """blind-fetch is the cookie exfiltration variant: it must POST
    document.cookie to the callback."""
    _, _, canary, _ = list(dxadyn.make_canaries_for(["blind-fetch"]))[0]
    assert "fetch(" in canary
    assert "method:\"POST\"" in canary
    assert "document.cookie" in canary


def test_phase_3_2_blind_script_uses_js_endpoint(_blind_callback_set):
    """blind-script points at /c/<cid>.js so the callback returns a
    parseable JS response and the payload doesn't throw."""
    _, cid, canary, _ = list(dxadyn.make_canaries_for(["blind-script"]))[0]
    assert f"/c/{cid}.js" in canary


def test_phase_3_2_blind_svg_onload_uses_new_image(_blind_callback_set):
    """blind-svg-onload's payload triggers via SVG onload and beacons
    with `new Image()` - bypasses filters that block <img src=...>
    but not <svg onload>."""
    _, cid, canary, _ = list(dxadyn.make_canaries_for(["blind-svg-onload"]))[0]
    assert "<svg onload=" in canary
    assert "new Image()" in canary
    assert f"/c/{cid}" in canary


def test_phase_3_2_blind_iframe_uses_src_attribute(_blind_callback_set):
    _, cid, canary, _ = list(dxadyn.make_canaries_for(["blind-iframe"]))[0]
    assert "<iframe src=" in canary
    assert f"/c/{cid}" in canary


def test_phase_3_2_each_call_mints_a_fresh_cid(_blind_callback_set):
    """Two back-to-back calls must produce distinct cids so verdicts
    (and callback correlation) stay independent."""
    c1, _ = dxadyn.make_canary("blind-img")
    c2, _ = dxadyn.make_canary("blind-img")
    assert c1 != c2


def test_phase_3_2_variants_all_pulls_blind_only_when_callback_set(_blind_callback_set):
    """--variants all extends the variant list with blind names only
    when a callback is configured. Simulates the resolution logic in
    main() by asserting on the extended set."""
    variants = list(dxadyn.PAYLOAD_VARIANTS.keys())
    if dxadyn.BLIND_CALLBACK:
        variants += list(dxadyn.BLIND_VARIANTS.keys())
    for name in _BLIND_VARIANT_NAMES:
        assert name in variants


def test_phase_3_2_variants_all_omits_blind_when_no_callback():
    dxadyn.BLIND_CALLBACK = ""
    variants = list(dxadyn.PAYLOAD_VARIANTS.keys())
    if dxadyn.BLIND_CALLBACK:
        variants += list(dxadyn.BLIND_VARIANTS.keys())
    for name in _BLIND_VARIANT_NAMES:
        assert name not in variants
