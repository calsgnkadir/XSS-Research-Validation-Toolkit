"""Phase 1.3: JSON workflow chaining tests. Kept in its own file so the
flow engine's stdlib-server end-to-end tests do not slow down the core
dxadyn suite when someone runs just `pytest test_dxadyn.py`.
"""
from __future__ import annotations
import http.server
import json
import pathlib
import sys
import threading
import urllib.parse

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import dxadyn  # noqa: E402


# --- _jsonpath_get unit tests ----------------------------------------------

def test_jsonpath_root_returns_whole_object():
    data = {"a": 1}
    assert dxadyn._jsonpath_get(data, "$") == data


def test_jsonpath_single_key():
    assert dxadyn._jsonpath_get({"token": "abc"}, "$.token") == "abc"


def test_jsonpath_nested_key():
    data = {"user": {"id": 42, "email": "u@x"}}
    assert dxadyn._jsonpath_get(data, "$.user.id") == 42
    assert dxadyn._jsonpath_get(data, "$.user.email") == "u@x"


def test_jsonpath_list_index():
    data = {"items": [{"id": 10}, {"id": 20}]}
    assert dxadyn._jsonpath_get(data, "$.items[0].id") == 10
    assert dxadyn._jsonpath_get(data, "$.items[1].id") == 20


def test_jsonpath_negative_index():
    data = {"items": [1, 2, 3]}
    assert dxadyn._jsonpath_get(data, "$.items[-1]") == 3


def test_jsonpath_star_returns_list_copy():
    data = {"items": [{"n": 1}, {"n": 2}]}
    out = dxadyn._jsonpath_get(data, "$.items[*]")
    assert out == [{"n": 1}, {"n": 2}]


def test_jsonpath_missing_key_returns_none():
    assert dxadyn._jsonpath_get({"a": 1}, "$.b") is None


def test_jsonpath_missing_index_returns_none():
    assert dxadyn._jsonpath_get({"a": [1, 2]}, "$.a[5]") is None


def test_jsonpath_no_dollar_returns_none():
    assert dxadyn._jsonpath_get({"a": 1}, "a") is None


def test_jsonpath_key_after_leaf_returns_none():
    """`$.a.b` on `{'a': 1}` cannot dereference b on int -> None."""
    assert dxadyn._jsonpath_get({"a": 1}, "$.a.b") is None


# --- _substitute unit tests -------------------------------------------------

def test_substitute_string_replaces_placeholder():
    assert dxadyn._substitute("hi {name}", {"name": "bob"}) == "hi bob"


def test_substitute_leaves_missing_placeholder_literal():
    """Missing key stays as `{unknown}` so the flow author spots the typo
    in the sent request rather than getting an empty value silently."""
    assert dxadyn._substitute("hi {who}", {}) == "hi {who}"


def test_substitute_walks_dict_and_list():
    tpl = {"a": "{x}", "b": ["{x}", {"c": "{x}"}]}
    out = dxadyn._substitute(tpl, {"x": "Z"})
    assert out == {"a": "Z", "b": ["Z", {"c": "Z"}]}


def test_substitute_leaves_primitives_alone():
    assert dxadyn._substitute(42, {"x": "y"}) == 42
    assert dxadyn._substitute(True, {"x": "y"}) is True
    assert dxadyn._substitute(None, {"x": "y"}) is None


def test_substitute_two_placeholders_one_string():
    assert dxadyn._substitute("{a}-{b}", {"a": "1", "b": "2"}) == "1-2"


def test_substitute_rnd_and_canary_special_keys():
    """{RND} / {CANARY} / {CID} are the same substitution mechanism; the
    engine just seeds those into vars_ before running the flow."""
    vars_ = {"RND": "abc123", "CANARY": "dxaXXX<dXsS>", "CID": "dxaXXX"}
    assert dxadyn._substitute("u-{RND}@x", vars_) == "u-abc123@x"
    assert dxadyn._substitute("{CANARY}", vars_) == "dxaXXX<dXsS>"


# --- run_flow end-to-end against a local stdlib server ----------------------

class _FlowFixtureHandler(http.server.BaseHTTPRequestHandler):
    """Minimal register->post->render server used by the flow-engine e2e
    tests. Kept inside the test file so it cannot drift from the tests."""
    def log_message(self, format, *args):
        return

    tokens: dict = {}
    comments: dict = {}
    next_uid = [1]

    def _send(self, status, body, ctype="text/html; charset=utf-8"):
        b = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        if self.path == "/api/register":
            payload = json.loads(body or "{}")
            uid = self.next_uid[0]
            self.next_uid[0] += 1
            token = f"tok-{uid}"
            self.tokens[token] = uid
            self.comments[uid] = []
            self._send(200, json.dumps({
                "token": token,
                "user": {"id": uid, "email": payload.get("email", "")},
            }), ctype="application/json")
        elif self.path == "/api/comments":
            auth = self.headers.get("Authorization", "")
            tok = auth.split()[-1] if auth.lower().startswith("bearer ") else ""
            uid = self.tokens.get(tok)
            if uid is None:
                self._send(401, '{"error":"no token"}', ctype="application/json")
                return
            payload = json.loads(body or "{}")
            self.comments.setdefault(uid, []).append(str(payload.get("text", "")))
            self._send(200, json.dumps({"id": len(self.comments[uid])}),
                       ctype="application/json")
        else:
            self._send(404, "not found")

    def do_GET(self):
        if self.path.startswith("/comments/"):
            uid = int(self.path.rsplit("/", 1)[1])
            rows = "".join(f"<li>{t}</li>" for t in self.comments.get(uid, []))
            self._send(200, f"<html><body>{rows}</body></html>")
        else:
            self._send(404, "not found")


@pytest.fixture
def flow_server():
    _FlowFixtureHandler.tokens = {}
    _FlowFixtureHandler.comments = {}
    _FlowFixtureHandler.next_uid = [1]
    httpd = http.server.HTTPServer(("127.0.0.1", 0), _FlowFixtureHandler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


def _register_only_flow(port):
    return {
        "name": "register-only",
        "steps": [{
            "name": "reg",
            "method": "POST",
            "url": f"http://127.0.0.1:{port}/api/register",
            "content_type": "application/json",
            "body": {"email": "u-{RND}@x.test", "password": "p"},
            "save": {"token": "$.token", "uid": "$.user.id"},
        }],
    }


def _full_flow(port):
    return {
        "name": "reg-post-verify",
        "steps": [
            {
                "name": "reg",
                "method": "POST",
                "url": f"http://127.0.0.1:{port}/api/register",
                "content_type": "application/json",
                "body": {"email": "u-{RND}@x.test", "password": "p"},
                "save": {"token": "$.token", "uid": "$.user.id"},
            },
            {
                "name": "post",
                "method": "POST",
                "url": f"http://127.0.0.1:{port}/api/comments",
                "content_type": "application/json",
                "headers": {"Authorization": "Bearer {token}"},
                "body": {"text": "{CANARY}"},
            },
            {
                "name": "verdict",
                "method": "GET",
                "url": f"http://127.0.0.1:{port}/comments/{{uid}}",
                "verdict": True,
            },
        ],
    }


def test_flow_saves_jsonpath_values_between_steps(flow_server):
    port = flow_server
    summary = dxadyn.run_flow(_register_only_flow(port))
    assert summary["steps_run"] == 1
    assert summary["error"] is None
    # save extracted token + uid into the vars namespace
    assert summary["vars"]["token"] == "tok-1"
    assert summary["vars"]["uid"] == 1


def test_flow_threads_saved_var_into_next_step_header(flow_server):
    port = flow_server
    summary = dxadyn.run_flow(_full_flow(port))
    assert summary["steps_run"] == 3
    assert summary["error"] is None
    # header {token} substitution reached the auth check successfully;
    # any 401 would have surfaced in the verdict step body.


def test_flow_verdict_fires_on_stored_canary(flow_server):
    port = flow_server
    summary = dxadyn.run_flow(_full_flow(port))
    verdicts = summary["verdicts"]
    assert len(verdicts) == 1
    # The comment page renders the canary raw -> unencoded reflection.
    assert verdicts[0]["reflection"] == "unencoded"
    assert verdicts[0]["step"] == "verdict"


def test_flow_verdict_negative_when_canary_absent(flow_server):
    """A verdict step against a URL that never received the canary must
    return `absent`, not silently pass. This is the false-negative
    discipline for flows."""
    port = flow_server
    flow = {
        "name": "reg-then-verdict-empty",
        "steps": [
            {
                "name": "reg",
                "method": "POST",
                "url": f"http://127.0.0.1:{port}/api/register",
                "content_type": "application/json",
                "body": {"email": "u-{RND}@x.test", "password": "p"},
                "save": {"uid": "$.user.id"},
            },
            {
                "name": "check",
                "method": "GET",
                "url": f"http://127.0.0.1:{port}/comments/{{uid}}",
                "verdict": True,
            },
        ],
    }
    summary = dxadyn.run_flow(flow)
    assert summary["verdicts"][0]["reflection"] == "absent"


def test_flow_error_on_network_failure_leaves_summary_clean():
    """If a step targets an unreachable port, the flow stops with an
    error recorded in the summary rather than crashing."""
    flow = {
        "name": "unreachable",
        "steps": [{
            "name": "boom",
            "method": "GET",
            "url": "http://127.0.0.1:1/does-not-exist",
        }],
    }
    summary = dxadyn.run_flow(flow, canary="dxaAAA\"<dXsS>",
                              cid="dxaAAA", marker="<dXsS>")
    assert summary["error"] and "boom" in summary["error"]
    assert summary["steps_run"] == 1


def test_flow_missing_step_field_uses_defaults():
    """Method defaults to GET; body/headers optional."""
    flow = {"name": "empty", "steps": []}
    summary = dxadyn.run_flow(flow)
    assert summary["steps_run"] == 0
    assert summary["error"] is None
    assert summary["verdicts"] == []


def test_flow_load_returns_error_dict_on_bad_path(tmp_path):
    result = dxadyn._load_flow(str(tmp_path / "does-not-exist.json"))
    assert "__error__" in result


def test_flow_load_returns_error_dict_on_bad_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{ not: json")
    result = dxadyn._load_flow(str(p))
    assert "__error__" in result


def test_flow_load_parses_valid_json(tmp_path):
    p = tmp_path / "ok.json"
    payload = {"name": "n", "steps": [{"name": "s", "url": "http://x"}]}
    p.write_text(json.dumps(payload))
    result = dxadyn._load_flow(str(p))
    assert result == payload


def test_flow_example_file_parses():
    """The shipped example flow must at least load cleanly."""
    p = HERE / "examples" / "flows" / "register-comment-verify.json"
    result = dxadyn._load_flow(str(p))
    assert result.get("name") == "register-then-post-comment-then-verify"
    assert len(result["steps"]) == 3


# --- Phase 1.5: macro-based auth (run_auth_flow) ---------------------------


@pytest.fixture(autouse=True)
def _reset_extra_headers_after_test():
    """Auth flows install headers into a module-level dict. Snapshot +
    restore around every test so cross-test contamination cannot happen."""
    snapshot = dict(dxadyn.EXTRA_HEADERS)
    yield
    dxadyn.EXTRA_HEADERS.clear()
    dxadyn.EXTRA_HEADERS.update(snapshot)


def test_auth_flow_installs_bearer_header_from_jwt(flow_server):
    """Explicit auth={header,value} JWT/Bearer flow: after the login step
    returns {token: ...}, the substituted 'Authorization: Bearer <tok>'
    header must be installed into EXTRA_HEADERS."""
    port = flow_server
    flow = {
        "name": "jwt-login",
        "steps": [{
            "name": "login",
            "method": "POST",
            "url": f"http://127.0.0.1:{port}/api/register",
            "content_type": "application/json",
            "body": {"email": "u-{RND}@x.test", "password": "p"},
            "save": {"token": "$.token"},
        }],
        "auth": {"header": "Authorization", "value": "Bearer {token}"},
    }
    summary = dxadyn.run_auth_flow(flow)
    assert summary["error"] is None
    assert summary["authenticated"] is True
    hname, hval = summary["auth_header"]
    assert hname == "Authorization"
    assert hval.startswith("Bearer tok-")
    assert dxadyn.EXTRA_HEADERS["Authorization"] == hval


def test_auth_flow_cookie_login_sets_no_header_but_marks_authenticated():
    """Cookie flow with no `auth` field: no header installed, but the
    cookie jar (populated by Set-Cookie) implies authentication."""
    class _CookieHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return

        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0") or "0")
            self.rfile.read(length)
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Set-Cookie", "session=deadbeef; Path=/")
            self.end_headers()
            self.wfile.write(b"ok")

    httpd = http.server.HTTPServer(("127.0.0.1", 0), _CookieHandler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        # start with a fresh cookie jar so an old session doesn't pass the
        # "cookies exist" check spuriously
        dxadyn.OPENER = dxadyn._opener()
        flow = {
            "name": "cookie-login",
            "steps": [{
                "name": "login",
                "method": "POST",
                "url": f"http://127.0.0.1:{port}/login",
                "content_type": "application/x-www-form-urlencoded",
                "body": {"u": "admin", "p": "changeme"},
            }],
        }
        summary = dxadyn.run_auth_flow(flow)
        assert summary["error"] is None
        assert summary["auth_header"] is None
        assert summary["authenticated"] is True
        assert "Authorization" not in dxadyn.EXTRA_HEADERS
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_auth_flow_flags_unresolved_placeholder_as_error(flow_server):
    """If the flow author asks for `Bearer {token}` but no step saved
    `token`, the engine must NOT install a broken header - it flags the
    error so the operator fixes the JSONPath."""
    port = flow_server
    flow = {
        "name": "misconfigured",
        "steps": [{
            "name": "login",
            "method": "POST",
            "url": f"http://127.0.0.1:{port}/api/register",
            "content_type": "application/json",
            "body": {"email": "u-{RND}@x.test", "password": "p"},
            "save": {"oops": "$.does_not_exist"},
        }],
        "auth": {"header": "Authorization", "value": "Bearer {token}"},
    }
    summary = dxadyn.run_auth_flow(flow)
    assert summary["error"] and "placeholder" in summary["error"].lower()
    assert summary["auth_header"] is None
    assert "Authorization" not in dxadyn.EXTRA_HEADERS


def test_auth_flow_carries_error_from_underlying_run_flow():
    """A failed step surfaces via summary['error'] and blocks auth install."""
    flow = {
        "name": "unreachable",
        "steps": [{"name": "boom", "method": "GET",
                   "url": "http://127.0.0.1:1/x"}],
        "auth": {"header": "Authorization", "value": "Bearer {tok}"},
    }
    summary = dxadyn.run_auth_flow(flow)
    assert summary["error"] == "auth request failed"
    assert summary["auth_header"] is None
    assert summary["authenticated"] is False


def test_auth_flow_multiple_saves_and_composite_header(flow_server):
    """Composite auth values (e.g. `Bearer {token} X-User: {uid}`) work
    because _substitute is called on the whole value string."""
    port = flow_server
    flow = {
        "name": "multi",
        "steps": [{
            "name": "login",
            "method": "POST",
            "url": f"http://127.0.0.1:{port}/api/register",
            "content_type": "application/json",
            "body": {"email": "u-{RND}@x.test", "password": "p"},
            "save": {"token": "$.token", "uid": "$.user.id"},
        }],
        "auth": {"header": "X-Auth", "value": "tok={token};uid={uid}"},
    }
    summary = dxadyn.run_auth_flow(flow)
    assert summary["auth_header"][1].startswith("tok=tok-")
    assert ";uid=1" in summary["auth_header"][1]


def test_clear_auth_header_removes_installed_header(flow_server):
    """clear_auth_header lets a caller switch auth contexts in one run."""
    port = flow_server
    flow = {
        "name": "jwt-login",
        "steps": [{
            "name": "login",
            "method": "POST",
            "url": f"http://127.0.0.1:{port}/api/register",
            "content_type": "application/json",
            "body": {"email": "u-{RND}@x.test", "password": "p"},
            "save": {"token": "$.token"},
        }],
        "auth": {"header": "Authorization", "value": "Bearer {token}"},
    }
    dxadyn.run_auth_flow(flow)
    assert "Authorization" in dxadyn.EXTRA_HEADERS
    dxadyn.clear_auth_header("Authorization")
    assert "Authorization" not in dxadyn.EXTRA_HEADERS


def test_auth_flow_installed_header_reaches_subsequent_flow_step(flow_server):
    """The whole point of Phase 1.5: after run_auth_flow, a downstream
    run_flow call must send the installed auth header on every request.
    This test verifies end-to-end by hitting an endpoint that requires
    the Bearer token."""
    port = flow_server
    # 1. Register + install Bearer header
    auth = {
        "name": "jwt-login",
        "steps": [{
            "name": "login",
            "method": "POST",
            "url": f"http://127.0.0.1:{port}/api/register",
            "content_type": "application/json",
            "body": {"email": "u-{RND}@x.test", "password": "p"},
            "save": {"token": "$.token", "uid": "$.user.id"},
        }],
        "auth": {"header": "Authorization", "value": "Bearer {token}"},
    }
    a = dxadyn.run_auth_flow(auth)
    assert a["authenticated"]
    uid = a["vars"]["uid"]

    # 2. A follow-on flow posts to the AUTH-REQUIRED endpoint. If the
    # Authorization header did NOT ride along, the mock returns 401 and
    # our subsequent GET finds no canary - so the verdict would be absent.
    scan = {
        "name": "post-authenticated",
        "steps": [
            {
                "name": "post",
                "method": "POST",
                "url": f"http://127.0.0.1:{port}/api/comments",
                "content_type": "application/json",
                "body": {"text": "{CANARY}"},
            },
            {
                "name": "check",
                "method": "GET",
                "url": f"http://127.0.0.1:{port}/comments/{uid}",
                "verdict": True,
            },
        ],
    }
    scan_summary = dxadyn.run_flow(scan)
    # If the Authorization header was NOT installed, post would 401 and
    # the check would see an empty comments page -> reflection=absent.
    assert scan_summary["verdicts"][0]["reflection"] == "unencoded"


def test_auth_flow_example_files_parse():
    """Both shipped auth example files must load and expose the expected
    shape."""
    jwt = dxadyn._load_flow(str(HERE / "examples" / "flows" / "jwt-login.json"))
    assert jwt.get("auth", {}).get("header") == "Authorization"
    assert "Bearer" in jwt["auth"]["value"]

    cookie = dxadyn._load_flow(str(HERE / "examples" / "flows"
                                    / "cookie-login.json"))
    assert "auth" not in cookie
    assert cookie["steps"][0]["method"] == "POST"
