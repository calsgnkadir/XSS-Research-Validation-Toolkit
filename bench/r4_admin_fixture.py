"""Disposable loopback two-account stored-XSS role-boundary fixture (R4)."""
from __future__ import annotations

from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import html
import secrets
import threading
from urllib.parse import parse_qs


ACCOUNTS = {"writer": ("writer", "writer-pass"), "reader-admin": ("admin", "admin-pass")}


@dataclass
class State:
    sessions: dict[str, str] = field(default_factory=dict)
    comments: list[tuple[str, str]] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)


class FixtureServer:
    """Starts only on 127.0.0.1 and owns its short-lived server thread."""

    def __init__(self):
        self.state = State()
        state = self.state

        class Handler(BaseHTTPRequestHandler):
            server_version = "R4AdminFixture/1"

            def log_message(self, *_args):
                pass

            def _send(self, status, body, content_type="text/html; charset=utf-8", headers=()):
                raw = body.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(raw)))
                for key, value in headers:
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(raw)

            def _role(self):
                cookie = self.headers.get("Cookie", "")
                token = next((part.strip()[8:] for part in cookie.split(";")
                              if part.strip().startswith("session=")), "")
                with state.lock:
                    return state.sessions.get(token)

            def do_POST(self):
                length = min(int(self.headers.get("Content-Length", "0")), 65536)
                form = parse_qs(self.rfile.read(length).decode("utf-8", "replace"),
                                keep_blank_values=True)
                if self.path == "/login":
                    user = form.get("user", [""])[0]
                    password = form.get("password", [""])[0]
                    account = ACCOUNTS.get(user)
                    if not account or account[1] != password:
                        self._send(401, "login failed")
                        return
                    token = secrets.token_urlsafe(24)
                    with state.lock:
                        state.sessions[token] = account[0]
                    self._send(200, "ok", "text/plain; charset=utf-8",
                               (("Set-Cookie", f"session={token}; HttpOnly; SameSite=Strict; Path=/"),))
                    return
                if self.path == "/comments":
                    if self._role() != "writer":
                        self._send(403, "forbidden")
                        return
                    text = form.get("comment", [""])[0]
                    with state.lock:
                        state.comments.append(("writer", text))
                    self._send(200, "accepted", "text/plain; charset=utf-8")
                    return
                self._send(404, "not found")

            def do_GET(self):
                role = self._role()
                if self.path == "/admin/comments":
                    if role != "admin":
                        self._send(403 if role else 401, "forbidden")
                        return
                    with state.lock:
                        entries = list(state.comments)
                    rendered = "".join("<article>" + value + "</article>"
                                       for _author, value in entries)
                    self._send(200, "<!doctype html><meta charset=utf-8>" + rendered)
                    return
                if self.path == "/fixed/admin/comments":
                    if role != "admin":
                        self._send(403 if role else 401, "forbidden")
                        return
                    with state.lock:
                        entries = list(state.comments)
                    self._send(200, "<!doctype html><meta charset=utf-8>" + "".join(
                        "<article>" + html.escape(value) + "</article>" for _author, value in entries))
                    return
                if self.path == "/writer":
                    self._send(200 if role == "writer" else 403 if role else 401, "writer")
                    return
                self._send(404, "not found")

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.httpd.daemon_threads = True
        self.origin = f"http://127.0.0.1:{self.httpd.server_port}"
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_exc):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=3)
        if self.thread.is_alive():
            raise RuntimeError("fixture-server-cleanup-failed")
