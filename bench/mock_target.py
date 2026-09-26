"""Stdlib-only mock HTTP server exposing known-vulnerable and known-safe
endpoints. Lets the benchmark harness run in CI without docker.

Endpoints:
    GET  /echo?q=X                     raw reflect of X (vulnerable)
    GET  /safe-echo?q=X                HTML-escaped reflect of X (safe)
    POST /guestbook (msg=X)            store X; then GET /guestbook renders raw
    GET  /guestbook                    render stored entries (vulnerable)

Flow-engine fixture endpoints (Phase 1.3):
    POST /api/register {email,password}          -> {token, user: {id}}
    POST /api/comments {text,author_id}
         (Authorization: Bearer <token>)          -> {id, text}
    GET  /comments/<uid>                          renders comment text raw

Start with `python mock_target.py --port 8765`; stop with Ctrl-C or the
context manager in run.py.
"""
from __future__ import annotations
import argparse
import html
import http.server
import json
import secrets
import threading
import urllib.parse
from typing import Dict, List


_GUESTBOOK: List[str] = []
_TOKENS: Dict[str, int] = {}          # token -> user id
_COMMENTS: Dict[int, List[str]] = {}  # uid -> [raw text, ...]
_NEXT_UID = 1


class _Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _send(self, status: int, body: str, ctype: str = "text/html; charset=utf-8"):
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        if parsed.path == "/echo-land":
            self._send(200, '<html><body><a href="/echo?q=seed">echo</a></body></html>')
        elif parsed.path == "/safe-echo-land":
            self._send(200, '<html><body><a href="/safe-echo?q=seed">safe</a></body></html>')
        elif parsed.path == "/echo":
            q = qs.get("q", [""])[0]
            self._send(200, f"<html><body><h1>echo</h1><div>{q}</div></body></html>")
        elif parsed.path == "/safe-echo":
            q = qs.get("q", [""])[0]
            self._send(200, f"<html><body><h1>safe</h1><div>{html.escape(q)}</div></body></html>")
        elif parsed.path == "/guestbook":
            rows = "".join(f"<li>{m}</li>" for m in _GUESTBOOK)
            self._send(
                200,
                f"<html><body><h1>guestbook</h1>"
                f'<form method="POST"><input name="msg"><button>go</button></form>'
                f"<ul>{rows}</ul></body></html>",
            )
        elif parsed.path.startswith("/comments/"):
            # Flow-fixture: render one user's comments raw (vulnerable).
            try:
                uid = int(parsed.path.rsplit("/", 1)[1])
            except ValueError:
                self._send(400, "bad uid")
                return
            rows = "".join(f"<li>{t}</li>" for t in _COMMENTS.get(uid, []))
            self._send(
                200,
                f"<html><body><h1>comments {uid}</h1><ul>{rows}</ul></body></html>",
            )
        else:
            self._send(404, "not found")

    def do_POST(self):
        global _NEXT_UID
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length)
        body = raw.decode("utf-8", errors="replace")
        if parsed.path == "/guestbook":
            form = urllib.parse.parse_qs(body)
            msg = form.get("msg", [""])[0]
            _GUESTBOOK.append(msg)
            self._send(200, '<html><body>ok. <a href="/guestbook">back</a></body></html>')
        elif parsed.path == "/api/register":
            # Flow-fixture: accept a JSON registration, return a token + uid.
            try:
                payload = json.loads(body or "{}")
            except (ValueError, json.JSONDecodeError):
                self._send(400, '{"error":"bad json"}',
                           ctype="application/json")
                return
            uid = _NEXT_UID
            _NEXT_UID += 1
            token = secrets.token_hex(8)
            _TOKENS[token] = uid
            _COMMENTS[uid] = []
            self._send(200,
                       json.dumps({"token": token, "user": {"id": uid,
                                   "email": payload.get("email", "")}}),
                       ctype="application/json")
        elif parsed.path == "/api/comments":
            # Flow-fixture: authenticated POST, stores raw text under uid.
            auth = self.headers.get("Authorization", "")
            token = auth.split()[-1] if auth.lower().startswith("bearer ") else ""
            uid = _TOKENS.get(token)
            if uid is None:
                self._send(401, '{"error":"no token"}',
                           ctype="application/json")
                return
            try:
                payload = json.loads(body or "{}")
            except (ValueError, json.JSONDecodeError):
                self._send(400, '{"error":"bad json"}',
                           ctype="application/json")
                return
            text = str(payload.get("text", ""))
            _COMMENTS.setdefault(uid, []).append(text)
            self._send(200,
                       json.dumps({"id": len(_COMMENTS[uid]), "text": text}),
                       ctype="application/json")
        else:
            self._send(404, "not found")


class MockServer:
    def __init__(self, port: int = 0):
        self.port = port
        self._httpd: http.server.HTTPServer | None = None
        self._thread: threading.Thread | None = None

    def __enter__(self):
        self._httpd = http.server.HTTPServer(("127.0.0.1", self.port), _Handler)
        self.port = self._httpd.server_address[1]
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        global _NEXT_UID
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
        _GUESTBOOK.clear()
        _TOKENS.clear()
        _COMMENTS.clear()
        _NEXT_UID = 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    with MockServer(port=args.port) as srv:
        print(f"mock target listening on http://127.0.0.1:{srv.port}")
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            print("bye")


if __name__ == "__main__":
    main()
