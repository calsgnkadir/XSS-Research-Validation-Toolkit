"""dxa-callback: out-of-band callback server for blind XSS.

Callback requests can arrive after an authorized probe was submitted.
An HTTP hit is resource-callback evidence only: an image request or a
direct HTTP client can produce it without JavaScript execution. Correlation
does not establish a vulnerability or a verified browser session.

This module is that server. Deliberately small and stdlib-only so it
can be deployed on any host without a Python venv:

    python -m dxa_callback --port 9999 --db ~/.dxa/callbacks.db

Endpoints:

    GET  /c/<cid>       records the hit; returns a 1x1 GIF so <img
                        src=...> payloads don't render broken.
    GET  /c/<cid>.js    records the hit; returns `void 0` so
                        <script src=...> payloads don't error.
    POST /c/<cid>       records the hit; bounded body discarded; returns
                        `{"ok": true}`.
    GET  /callback      generic entry point without a cid (returns 1x1
                        GIF). For fingerprinting-only payloads.

    GET  /hits          returns every hit as JSON (newest first, up to
                        --list-limit rows).
    GET  /hits/<cid>    returns hits for a specific cid.
    GET  /healthz       readiness probe: returns `{"ok": true, "hits":
                        <count>}` without touching the hits table
                        beyond a COUNT.

CORS is allowed only on collection routes. Reads require an exact local
Host without Origin/cross-site browser headers; an optional bearer token
protects /hits and /healthz. The listener binds only to 127.0.0.1.
HTTP collection omits query strings, user agents, referrers and bodies.
Existing database rows remain unchanged; review legacy data before sharing.
The optional read token is intended for direct HTTP clients. Existing scanner
and journal clients do not supply it; enabling it makes those reads fail with
an explicit authentication/query error until client support is configured.

Storage: SQLite at --db path (default `~/.dxa/callbacks.db`).
`--memory` uses an in-memory DB (test/dev; loses hits on shutdown).
Schema:

    CREATE TABLE hits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cid TEXT NOT NULL,
        ts REAL NOT NULL,
        method TEXT NOT NULL,
        path TEXT NOT NULL,
        user_agent TEXT,
        remote_ip TEXT,
        referer TEXT,
        body_preview TEXT
    );
    CREATE INDEX idx_cid ON hits(cid);
    CREATE INDEX idx_ts ON hits(ts);

Every write is atomic; concurrent hits from many browsers are safe.
"""
from __future__ import annotations
import argparse
import base64
import contextlib
import http.server
import hmac
import math
import json
import os
import pathlib
import sqlite3
import threading
import time
import urllib.parse
from typing import Any, Optional

# 1x1 transparent GIF - what browsers get when they render <img src=/c/...>.
_1PX_GIF = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
)
_LIST_LIMIT_DEFAULT = 200
_BODY_PREVIEW_MAX = 2048  # Maximum accepted body; bodies are never persisted.


class CallbackDB:
    """Thread-safe SQLite wrapper. Uses check_same_thread=False so the
    stdlib HTTPServer handler threads can share one connection with a
    module-level lock guarding writes."""

    _SCHEMA = """
    CREATE TABLE IF NOT EXISTS hits (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        cid          TEXT NOT NULL,
        ts           REAL NOT NULL,
        method       TEXT NOT NULL,
        path         TEXT NOT NULL,
        user_agent   TEXT,
        remote_ip    TEXT,
        referer      TEXT,
        body_preview TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_cid ON hits(cid);
    CREATE INDEX IF NOT EXISTS idx_ts ON hits(ts);
    """

    def __init__(self, path: str = ":memory:"):
        self.path = path
        if path != ":memory:":
            pathlib.Path(path).expanduser().parent.mkdir(
                parents=True, exist_ok=True)
        # check_same_thread=False lets the handler-thread pool share this
        # connection; we serialise writes via _lock.
        self._conn = sqlite3.connect(
            str(pathlib.Path(path).expanduser()) if path != ":memory:" else ":memory:",
            check_same_thread=False, isolation_level=None,
        )
        self._lock = threading.Lock()
        self._conn.executescript(self._SCHEMA)

    def record(self, cid: str, method: str, path: str,
               user_agent: Optional[str], remote_ip: Optional[str],
               referer: Optional[str], body_preview: Optional[str]) -> int:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO hits (cid, ts, method, path, user_agent, "
                "remote_ip, referer, body_preview) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (cid, time.time(), method, path, user_agent,
                 remote_ip, referer, body_preview),
            )
            return cur.lastrowid

    def list_all(self, limit: int = _LIST_LIMIT_DEFAULT) -> list[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT id, cid, ts, method, path, user_agent, "
                "remote_ip, referer, body_preview "
                "FROM hits ORDER BY id DESC LIMIT ?", (int(limit),),
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def list_for_cid(self, cid: str,
                     limit: int = _LIST_LIMIT_DEFAULT) -> list[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT id, cid, ts, method, path, user_agent, "
                "remote_ip, referer, body_preview "
                "FROM hits WHERE cid = ? ORDER BY id DESC LIMIT ?",
                (cid, int(limit)),
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def count(self) -> int:
        with self._lock:
            row = self._conn.execute(
                "SELECT COUNT(*) FROM hits").fetchone()
        return int(row[0]) if row else 0

    @staticmethod
    def _row_to_dict(row) -> dict:
        return {
            "id": row[0], "cid": row[1], "ts": row[2],
            "method": row[3], "path": row[4],
            "user_agent": row[5], "remote_ip": row[6],
            "referer": row[7], "body_preview": row[8],
        }

    def close(self):
        with self._lock:
            self._conn.close()


def _valid_cid(cid: str) -> bool:
    """A cid must be short + alphanumeric to prevent path abuse. dxadyn
    mints cids as `dxa` + 8 hex chars, but we accept any [A-Za-z0-9_-]
    up to 64 chars to allow operator experiments."""
    if not cid or len(cid) > 64:
        return False
    return cid.isascii() and all(c.isalnum() or c in "_-" for c in cid)


class _Handler(http.server.BaseHTTPRequestHandler):
    """Route table lives here. Endpoints are documented in the module
    docstring. External input from arbitrary clients (path, headers,
    body) is treated as data - never eval'd, never templated back into
    HTML, only stored + returned as JSON with strict content types."""

    # Class attribute so the server instance can hand the DB in.
    db: CallbackDB
    list_limit: int = _LIST_LIMIT_DEFAULT
    read_token: Optional[str] = None
    request_timeout: float = 5.0

    def setup(self):
        super().setup()
        self.connection.settimeout(self.request_timeout)

    def log_message(self, format, *args):
        return

    def _send(self, status: int, body: bytes, ctype: str = "text/plain"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        path = urllib.parse.urlsplit(self.path).path
        if path.startswith("/c/") or path == "/callback":
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, obj: Any):
        self._send(status, json.dumps(obj).encode(),
                   ctype="application/json")

    def _remote_ip(self) -> str:
        # Never trust caller-controlled forwarding headers.
        try:
            return self.client_address[0]
        except Exception:                                # noqa: BLE001
            return ""

    def _record_hit(self, cid: str, body_preview: Optional[str]):
        try:
            self.db.record(
                cid=cid, method=self.command, path=urllib.parse.urlsplit(self.path).path,
                user_agent=None,
                remote_ip=self._remote_ip(),
                referer=None,
                body_preview=None,
            )
        except sqlite3.Error:
            self._send_json(503, {"error": "callback storage unavailable"})
            return False
        return True

    def _authorized(self):
        values = self.headers.get_all("Authorization", [])
        if self.read_token is not None and (len(values) != 1 or not
                hmac.compare_digest(values[0].encode(),
                                    ("Bearer " + self.read_token).encode())):
            self._send_json(401, {"error": "authentication required"})
            return False
        # CORS alone does not stop same-origin/DNS-rebinding requests.
        hosts = self.headers.get_all("Host", [])
        if len(hosts) != 1 or hosts[0] not in {f"127.0.0.1:{self.server.server_port}",
                        f"localhost:{self.server.server_port}"}:
            self._send_json(403, {"error": "local host required"})
            return False
        if self.headers.get_all("Origin", []) or "cross-site" in self.headers.get_all("Sec-Fetch-Site", []):
            self._send_json(403, {"error": "browser read access disabled"})
            return False
        return True

    def do_OPTIONS(self):
        self._send(204, b"", ctype="text/plain")

    def do_GET(self):
        try:
            return self._get()
        except sqlite3.Error:
            return self._send_json(503, {"error": "callback storage unavailable"})

    def _get(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/healthz" or path == "/hits" or path.startswith("/hits/"):
            if not self._authorized():
                return

        if path == "/healthz":
            return self._send_json(200,
                                   {"ok": True, "hits": self.db.count()})

        if path == "/hits":
            qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
            values = qs.get("limit", [str(self.list_limit)])
            if len(values) != 1 or not values[0].isascii() or not values[0].isdigit():
                return self._send_json(400, {"error": "invalid limit"})
            if len(values[0]) > 6 or not 1 <= int(values[0]) <= self.list_limit:
                return self._send_json(400, {"error": "invalid limit"})
            limit = int(values[0])
            return self._send_json(200, {"hits": self.db.list_all(limit)})

        if path.startswith("/hits/"):
            cid = path[len("/hits/"):]
            if not _valid_cid(cid):
                return self._send_json(400, {"error": "invalid cid"})
            return self._send_json(
                200, {"cid": cid, "hits": self.db.list_for_cid(cid, self.list_limit)})

        if path == "/callback":
            if not self._record_hit("callback", None):
                return
            return self._send(200, _1PX_GIF, ctype="image/gif")

        # /c/<cid> or /c/<cid>.js
        if path.startswith("/c/"):
            tail = path[len("/c/"):]
            if tail.endswith(".js"):
                cid = tail[:-3]
                if not _valid_cid(cid):
                    return self._send_json(400, {"error": "invalid cid"})
                if not self._record_hit(cid, None):
                    return
                return self._send(200, b"void 0;\n",
                                  ctype="application/javascript")
            cid = tail
            if not _valid_cid(cid):
                return self._send_json(400, {"error": "invalid cid"})
            if not self._record_hit(cid, None):
                return
            return self._send(200, _1PX_GIF, ctype="image/gif")

        return self._send_json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        self.close_connection = True
        values = self.headers.get_all("Content-Length", [])
        if self.headers.get("Transfer-Encoding") is not None:
            return self._send_json(400, {"error": "transfer encoding unsupported"})
        if len(values) != 1 or not values[0].isascii() or not values[0].isdigit():
            return self._send_json(400, {"error": "invalid content length"})
        if len(values[0]) > 6 or int(values[0]) > _BODY_PREVIEW_MAX:
            return self._send_json(413, {"error": "body too large"})
        length = int(values[0])
        try:
            raw = self.rfile.read(length)
        except TimeoutError:
            return self._send_json(408, {"error": "request body timeout"})
        if len(raw) != length:
            return self._send_json(400, {"error": "incomplete body"})

        if path.startswith("/c/"):
            cid = path[len("/c/"):]
            if not _valid_cid(cid):
                return self._send_json(400, {"error": "invalid cid"})
            if not self._record_hit(cid, None):
                return
            return self._send_json(200, {"ok": True})

        return self._send_json(404, {"error": "not found"})


class CallbackServer:
    """Wrapper around HTTPServer that also owns the DB. Context-manager
    friendly for tests, and exposes .port so a caller with port=0 can
    discover the actual assigned port."""

    def __init__(self, port: int = 0, db_path: str = ":memory:",
                 list_limit: int = _LIST_LIMIT_DEFAULT, *,
                 read_token: Optional[str] = None, request_timeout: float = 5.0):
        if type(list_limit) is not int or not 1 <= list_limit <= 1000:
            raise ValueError("list_limit must be between 1 and 1000")
        if not math.isfinite(request_timeout) or request_timeout <= 0:
            raise ValueError("request_timeout must be finite and positive")
        if read_token is not None and (len(read_token) < 16 or not read_token.isascii()
                                      or any(c.isspace() for c in read_token)):
            raise ValueError("read_token must be at least 16 ASCII characters without whitespace")
        self.db = CallbackDB(db_path)
        # Bind a fresh subclass so the class-level db attribute is
        # scoped to this server instance (multiple servers in one
        # process pick up their own DBs).
        handler_cls = type(
            "_ScopedHandler",
            (_Handler,),
            {"db": self.db, "list_limit": list_limit, "read_token": read_token,
             "request_timeout": request_timeout},
        )
        self._httpd = http.server.ThreadingHTTPServer(
            ("127.0.0.1", port), handler_cls)
        self.port = self._httpd.server_address[1]
        self._thread: Optional[threading.Thread] = None

    def start(self):
        if self._thread is not None:
            return
        self._thread = threading.Thread(
            target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
        self.db.close()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="dxa-callback - out-of-band callback server for "
                    "blind XSS. Authorized targets only.")
    ap.add_argument("--port", type=int, default=9999,
                    help="TCP port to listen on (default 9999).")
    ap.add_argument("--db", default="~/.dxa/callbacks.db",
                    help="SQLite path. --memory for in-memory (test/dev).")
    ap.add_argument("--memory", action="store_true",
                    help="use an in-memory DB. Overrides --db.")
    ap.add_argument("--list-limit", type=int, default=_LIST_LIMIT_DEFAULT,
                    help="max rows returned by /hits and /hits/<cid>.")
    ap.add_argument("--read-token-env", metavar="NAME",
                    help="environment variable containing optional /hits bearer token")
    args = ap.parse_args()

    db_path = ":memory:" if args.memory else args.db
    try:
        token = os.environ[args.read_token_env] if args.read_token_env else None
        srv = CallbackServer(port=args.port, db_path=db_path,
                             list_limit=args.list_limit, read_token=token)
    except (KeyError, ValueError, sqlite3.Error, OSError):
        ap.error("invalid callback configuration or unavailable storage/listener")
    print(f"[dxa-callback] listening on http://127.0.0.1:{srv.port} "
          f"(db={db_path})")
    srv.start()
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("[dxa-callback] bye")
    finally:
        srv.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
