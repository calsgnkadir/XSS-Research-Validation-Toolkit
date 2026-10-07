"""Disposable authenticated loopback fixture for the R3 proof command."""
from contextlib import contextmanager
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
import threading
import urllib.parse


@contextmanager
def lab(mode="raw"):
    state = {"value": "", "posts": 0, "checks": 0, "outside": "",
             "resource_callback_hits": {}}
    callback_lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, status, body, content_type="text/html", cookie=False):
            raw = body.encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw)))
            if cookie:
                self.send_header("Set-Cookie", "session=lab-only-secret; Path=/; HttpOnly")
            self.end_headers()
            self.wfile.write(raw)

        def authed(self):
            if mode == "bearer":
                return self.headers.get("Authorization") == "Bearer lab-only-secret"
            return "session=lab-only-secret" in self.headers.get("Cookie", "")

        def do_POST(self):
            size = int(self.headers.get("Content-Length", 0))
            fields = urllib.parse.parse_qs(self.rfile.read(size).decode())
            if self.path == "/login":
                if fields.get("user") == ["alice"] and fields.get("password") == ["lab-password"]:
                    if mode == "bearer":
                        return self.send(200, '{"token":"lab-only-secret"}', "application/json")
                    return self.send(200, "ok", cookie=True)
                return self.send(401, "denied")
            if self.path == "/comments" and self.authed():
                if mode == "csrf" and fields.get("csrf") != ["single-use"]:
                    return self.send(403, "missing csrf")
                state["value"] = fields.get("comment", [""])[0]
                state["posts"] += 1
                return self.send(201, "stored")
            self.send(403, "denied")

        def do_GET(self):
            if not self.authed():
                return self.send(401, "denied")
            if mode == "resource-callback" and self.path.startswith("/resource-callback?"):
                cid = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query).get("cid", [""])[0]
                submitted_cid = state["value"].split("<", 1)[0]
                if cid != submitted_cid or not re.fullmatch(r"dxa[0-9a-f]{32}", cid):
                    return self.send(400, "invalid callback identity")
                with callback_lock:
                    hits = state["resource_callback_hits"]
                    hits[cid] = hits.get(cid, 0) + 1
                return self.send(200, "resource observed", "text/plain")
            if self.path == "/me":
                state["checks"] += 1
                role = "wrong" if mode == "wrong-browser-role" and state["checks"] >= 2 else "reader"
                return self.send(200, json.dumps({"user": "alice", "role": role}), "application/json")
            if self.path == "/__dxa_missing":
                return self.send(404, "missing")
            if mode == "csrf" and self.path == "/comments":
                return self.send(200, '<input name="csrf" value="single-use">')
            value = state["value"]
            if mode == "fixed":
                body = html.escape(value)
            elif mode in ("title", "textarea"):
                # The image payload has no closing title/textarea tag: it is inert RCDATA.
                body = '<' + mode + '>' + value + '</' + mode + '>'
            elif mode == "resource-callback":
                # Preserve submitted text inertly; a separate handler-free image makes
                # a CID-correlated HTTP request, never a JavaScript canary assignment.
                cid = value.split("<", 1)[0]
                body = html.escape(value) + '<img src="/resource-callback?cid=' + urllib.parse.quote(cid, safe="") + '">'
            elif mode == "json":
                return self.send(200, json.dumps({"comment": value}), "application/json")
            elif mode == "dialog":
                body = '<script>alert("ordinary application dialog")</script>'
            elif mode == "iframe" and self.path != "/frame":
                body = '<iframe src="/frame"></iframe>'
            elif mode in ("delayed", "too-late"):
                delay = 150 if mode == "delayed" else 2000
                body = '<script>setTimeout(()=>{document.body.innerHTML=' + json.dumps(value) + '},' + str(delay) + ')</script>'
            elif mode == "eval":
                # A wrapper converting direct eval to indirect eval breaks this fixture.
                body = '<script>function render(){let local=17;if(eval("local")===17)document.body.innerHTML=' + json.dumps(value) + ';}setTimeout(render,0)</script>'
            elif mode == "spa":
                body = '<script>history.pushState({},"","/spa/one");history.pushState({},"","/spa/two");</script>' + value
            else:
                body = value
            if state["outside"]:
                body += '<img src="' + html.escape(state["outside"], quote=True) + '">'
            self.send(200, '<!doctype html><body>' + body + '</body>')

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    spec = {"origin": base, "role_path": "$.role", "observe_ms": 400,
            "auth_flow": {"steps": [{"url": base + "/login", "method": "POST",
                                      "body": {"user": "alice", "password": "lab-password"}}]},
            "session_check": {"url": base + "/me", "expect": {"$.user": "alice", "$.role": "reader"}},
            "submit": {"url": base + "/comments", "field": "comment", "csrf_field": ""},
            "read_url": base + "/comments"}
    if mode == "bearer":
        spec["auth_flow"]["steps"][0]["save"] = {"token": "$.token"}
        spec["auth_flow"]["auth"] = {"header": "Authorization", "value": "Bearer {token}"}
    if mode == "csrf":
        spec["submit"]["csrf_field"] = "csrf"
        spec["read_url"] = base + "/view"
    try:
        yield spec, state
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
