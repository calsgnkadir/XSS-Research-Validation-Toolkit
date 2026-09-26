"""Stdlib-only mock HTTP server exposing known-vulnerable and known-safe
endpoints. Lets the benchmark harness run in CI without docker.

Endpoints:
    GET  /echo?q=X           -> raw reflect of X (vulnerable)
    GET  /safe-echo?q=X      -> HTML-escaped reflect of X (safe)
    POST /guestbook (msg=X)  -> store X; then GET /guestbook renders raw
    GET  /guestbook          -> render stored entries (vulnerable)

Start with `python mock_target.py --port 8765`; stop with Ctrl-C or the
context manager in run.py.
"""
from __future__ import annotations
import argparse
import html
import http.server
import threading
import urllib.parse
from typing import List


_GUESTBOOK: List[str] = []


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
        else:
            self._send(404, "not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        form = urllib.parse.parse_qs(body)
        if parsed.path == "/guestbook":
            msg = form.get("msg", [""])[0]
            _GUESTBOOK.append(msg)
            self._send(200, '<html><body>ok. <a href="/guestbook">back</a></body></html>')
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
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
        _GUESTBOOK.clear()


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
