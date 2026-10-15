"""Request-bounded loopback stored-XSS comparison target for R4."""
from __future__ import annotations

from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import html
import json
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
    login_secrets: dict[str, str] = field(default_factory=lambda: {
        "writer": secrets.token_urlsafe(24), "reader-admin": secrets.token_urlsafe(24)})
    comments: list[str] = field(default_factory=list)
    requests: list[dict] = field(default_factory=list)
    budget_exceeded: bool = False
    max_inflight: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)
    slot: threading.Lock = field(default_factory=threading.Lock)
    started: float = field(default_factory=time.monotonic)
    next_request_at: float = 0.0

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

            def _token(self, cookie_name):
                for item in self.headers.get("Cookie", "").split(";"):
                    key, sep, value = item.strip().partition("=")
                    if sep and key == cookie_name:
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
                    # The pacing sleep is part of the wall budget. A request
                    # admitted before sleeping must not execute after expiry.
                    if time.monotonic() - state.started >= state.wall_limit:
                        with state.lock:
                            state.budget_exceeded = True
                            state.requests.append({"method": self.command, "path": self.path.split("?", 1)[0],
                                                   "status": 429, "budget_rejected": True})
                        self._reply(429, "fixture budget exhausted", "text/plain; charset=utf-8")
                        return
                    status, body, content_type = 404, "not found", "text/plain; charset=utf-8"
                    path = self.path.split("?", 1)[0]
                    if path == "/login" and self.command == "POST":
                        length = min(int(self.headers.get("Content-Length", "0")), 4096)
                        values = parse_qs(self.rfile.read(length).decode("utf-8", "replace"),
                                          keep_blank_values=True)
                        role = values.get("role", [""])[0]
                        principal = values.get("principal", [""])[0]
                        password = values.get("password", [""])[0]
                        if (role not in {"writer", "reader-admin"} or principal != role
                                or not secrets.compare_digest(password, state.login_secrets.get(role, ""))):
                            status, body = 401, "login failed"
                        else:
                            token = secrets.token_urlsafe(24)
                            cookie_name = "writer_session" if role == "writer" else "admin_session"
                            with state.lock:
                                state.sessions[token] = (principal, role)
                            body = "authenticated"
                            self.send_response(200)
                            self.send_header("Content-Type", "text/plain; charset=utf-8")
                            self.send_header("Set-Cookie", f"{cookie_name}={token}; HttpOnly; SameSite=Strict; Path=/")
                            self.send_header("Content-Length", str(len(body)))
                            self.end_headers()
                            self.wfile.write(body.encode("utf-8"))
                            with state.lock:
                                state.requests.append({"method": self.command, "path": path,
                                                       "status": 200, "budget_rejected": False})
                            return
                    elif path in {"/session/writer", "/session/reader-admin"} and self.command == "GET":
                        role = "writer" if path.endswith("/writer") else "reader-admin"
                        cookie_name = "writer_session" if role == "writer" else "admin_session"
                        token = self._token(cookie_name)
                        with state.lock:
                            identities = state.sessions.get(token)
                        status = 200 if identities == (role, role) else 403 if identities else 401
                        body = json.dumps({"principal": role, "role": role}) if status == 200 else "forbidden"
                        content_type = "application/json; charset=utf-8" if status == 200 else content_type
                    elif path == "/comments" and self.command == "GET":
                        token = self._token("writer_session")
                        with state.lock:
                            identities = state.sessions.get(token)
                        status = 200 if identities == ("writer", "writer") else 401
                        body = ('<!doctype html><form method="post"><input name="comment"></form>'
                                if status == 200 else "login required")
                        content_type = "text/html; charset=utf-8"
                    elif path == "/comments" and self.command == "POST":
                        token = self._token("writer_session")
                        with state.lock:
                            identities = state.sessions.get(token)
                        if identities != ("writer", "writer"):
                            status, body = (403, "forbidden") if identities else (401, "login required")
                        else:
                            length = min(int(self.headers.get("Content-Length", "0")), 32768)
                            values = parse_qs(self.rfile.read(length).decode("utf-8", "replace"),
                                              keep_blank_values=True)
                            comment = values.get("comment", [""])[0]
                            with state.lock:
                                state.comments.append(comment)
                            status, body, content_type = 200, "accepted", "text/plain; charset=utf-8"
                    elif path == "/admin/comments" and self.command == "GET":
                        token = self._token("admin_session")
                        with state.lock:
                            identities = state.sessions.get(token)
                        if identities != ("reader-admin", "reader-admin"):
                            status, body = (403, "forbidden") if identities else (401, "login required")
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

    def login(self, role: str) -> tuple[str, str]:
        """Perform one authenticated fixture login and return principal/token."""
        import urllib.error
        import urllib.parse
        import urllib.request

        if role not in {"writer", "reader-admin"}:
            raise ValueError("unknown fixture role")
        body = urllib.parse.urlencode({"role": role, "principal": role,
                                       "password": self.state.login_secrets[role]}).encode("ascii")
        request = urllib.request.Request(self.origin + "/login", data=body, method="POST")
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        cookie_name = "writer_session" if role == "writer" else "admin_session"
        try:
            with opener.open(request, timeout=3) as response:
                cookie = next((item for item in response.headers.get_all("Set-Cookie", [])
                               if item.startswith(cookie_name + "=")), "")
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError("fixture-login-failed") from exc
        token = cookie.partition("=")[2].partition(";")[0]
        if not token:
            raise RuntimeError("fixture-login-cookie-missing")
        return role, token

    def session_cookie(self, writer_token: str, admin_token: str) -> str:
        if not writer_token or not admin_token or writer_token == admin_token:
            raise ValueError("independent writer and reader-admin sessions required")
        return f"writer_session={writer_token}; admin_session={admin_token}"

    def session_check(self, role: str, token: str) -> dict:
        """Verify exact principal and role at the role-specific fixture endpoint."""
        import urllib.error
        import urllib.request

        if role not in {"writer", "reader-admin"} or not token:
            return {"passed": False, "principal": None, "role": role}
        cookie_name = "writer_session" if role == "writer" else "admin_session"
        path = "/session/writer" if role == "writer" else "/session/reader-admin"
        request = urllib.request.Request(self.origin + path,
                                         headers={"Cookie": f"{cookie_name}={token}"})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(request, timeout=3) as response:
                value = json.loads(response.read().decode("utf-8"))
                passed = (response.status == 200 and value.get("principal") == role
                          and value.get("role") == role)
                return {"passed": passed, "principal": role if passed else None, "role": role}
        except (urllib.error.URLError, TimeoutError, UnicodeError, ValueError):
            return {"passed": False, "principal": None, "role": role}

    def stored_comments(self) -> list[str]:
        """Return exact stored submissions to the local harness oracle."""
        with self.state.lock:
            return list(self.state.comments)

    def __exit__(self, *_exc):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=3)
        if self.thread.is_alive():
            raise RuntimeError("fixture-server-cleanup-failed")
