"""Request-bounded loopback stored-XSS comparison target for R4."""
from __future__ import annotations

from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import html
import secrets
import threading
import time
from urllib.parse import parse_qs


@dataclass
class ComparisonState:
    escaped: bool
    request_limit: int
    rate_limit: float
    wall_limit: float
    sessions: dict[str, tuple[str, str]] = field(default_factory=dict)
    comments: list[str] = field(default_factory=list)
    requests: list[dict] = field(default_factory=list)
    budget_exceeded: bool = False
    max_inflight: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)
    slot: threading.Lock = field(default_factory=threading.Lock)
    started: float = field(default_factory=time.monotonic)
    next_request_at: float = 0.0

    def broker_cookie(self) -> str:
        """Create two underlying role sessions behind one test-harness cookie."""
        token = secrets.token_urlsafe(24)
        with self.lock:
            self.sessions[token] = ("writer", "reader-admin")
        return token


class R4ComparisonFixture:
    def __init__(self, *, escaped: bool, request_limit: int = 20,
                 rate_limit: float = 2.0, wall_limit: float = 20.0):
        self.state = ComparisonState(escaped, request_limit, rate_limit, wall_limit)
        state = self.state

        class Handler(BaseHTTPRequestHandler):
            server_version = "R4ComparatorFixture/1"

            def log_message(self, *_args):
                pass

            def _reply(self, status, body, content_type="text/html; charset=utf-8"):
                raw = body.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def _token(self):
                for item in self.headers.get("Cookie", "").split(";"):
                    key, sep, value = item.strip().partition("=")
                    if sep and key == "bridge":
                        return value
                return ""

            def _dispatch(self):
                with state.slot:
                    with state.lock:
                        state.max_inflight = max(state.max_inflight, 1)
                        elapsed = time.monotonic() - state.started
                        if len(state.requests) >= state.request_limit or elapsed >= state.wall_limit:
                            state.budget_exceeded = True
                            state.requests.append({"method": self.command, "path": self.path.split("?", 1)[0],
                                                   "status": 429, "budget_rejected": True})
                            self._reply(429, "fixture budget exhausted", "text/plain; charset=utf-8")
                            return
                        wait_for = max(0.0, state.next_request_at - time.monotonic())
                        state.next_request_at = max(time.monotonic(), state.next_request_at) + 1.0 / state.rate_limit
                    if wait_for:
                        time.sleep(wait_for)
                    token = self._token()
                    with state.lock:
                        identities = state.sessions.get(token)
                    status, body, content_type = 404, "not found", "text/plain; charset=utf-8"
                    path = self.path.split("?", 1)[0]
                    if path == "/comments" and self.command == "GET":
                        status = 200 if identities else 401
                        body = ('<!doctype html><form method="post"><input name="comment"></form>'
                                if identities else "login required")
                        content_type = "text/html; charset=utf-8"
                    elif path == "/comments" and self.command == "POST":
                        if not identities:
                            status, body = 401, "login required"
                        elif identities[0] != "writer":
                            status, body = 403, "forbidden"
                        else:
                            length = min(int(self.headers.get("Content-Length", "0")), 32768)
                            values = parse_qs(self.rfile.read(length).decode("utf-8", "replace"),
                                              keep_blank_values=True)
                            comment = values.get("comment", [""])[0]
                            with state.lock:
                                state.comments.append(comment)
                            status, body, content_type = 200, "accepted", "text/plain; charset=utf-8"
                    elif path == "/admin/comments" and self.command == "GET":
                        if not identities:
                            status, body = 401, "login required"
                        elif identities[1] != "reader-admin":
                            status, body = 403, "forbidden"
                        else:
                            with state.lock:
                                values = list(state.comments)
                            render = html.escape if state.escaped else (lambda value: value)
                            status, body = 200, "<!doctype html><meta charset=utf-8>" + "".join(
                                "<article>" + render(value) + "</article>" for value in values)
                            content_type = "text/html; charset=utf-8"
                    with state.lock:
                        state.requests.append({"method": self.command, "path": path, "status": status,
                                               "budget_rejected": False})
                    self._reply(status, body, content_type)

            do_GET = _dispatch
            do_POST = _dispatch
            do_HEAD = _dispatch

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
