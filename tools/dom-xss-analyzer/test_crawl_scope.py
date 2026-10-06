"""Reflected crawler boundary regressions against two loopback origins."""
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

import dxadyn


@pytest.fixture
def lab(monkeypatch):
    requests = []
    servers = []
    threads = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            self.respond()

        def do_POST(self):
            self.respond()

        def respond(self):
            data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            requests.append((self.server.server_port, self.command, self.path,
                             dict(self.headers), data.decode()))
            status, headers, body = self.server.route(self.path, data.decode())
            encoded = body.encode()
            self.send_response(status)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(encoded)))
            for name, value in headers.items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(encoded)

    def start(route):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        server.route = route
        servers.append(server)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        threads.append(thread)
        return f"http://127.0.0.1:{server.server_port}"

    monkeypatch.setattr(dxadyn, "OPENER", dxadyn._opener())
    monkeypatch.setattr(dxadyn, "EXTRA_HEADERS", {})
    monkeypatch.setattr(dxadyn, "REPORT_EVENTS", [])
    monkeypatch.setattr(dxadyn, "SKIPPED_SUBMITS", [])
    monkeypatch.setattr(dxadyn, "CSRF_REFRESH_URL", "")
    monkeypatch.setattr(dxadyn, "CSRF_HEADER_NAME", "")
    monkeypatch.setattr(dxadyn, "_RATE_LIMITER", None)
    monkeypatch.setattr(dxadyn, "JITTER_MS_MIN", 0)
    monkeypatch.setattr(dxadyn, "JITTER_MS_MAX", 0)
    monkeypatch.setattr(dxadyn, "PARALLEL_WORKERS", 1)
    yield start, requests
    for server in servers:
        server.shutdown()
        server.server_close()
    for thread in threads:
        thread.join(timeout=2)


def reflect(path, data):
    return 200, {}, urllib.parse.unquote_plus(data or path)


def test_crawl_never_probes_external_forms_or_query_links(lab):
    start, requests = lab
    outside = start(reflect)

    def route(path, data):
        if path == "/":
            return 200, {}, (
                f'<form action="{outside}/post" method="post"><input name="q"></form>'
                f'<form action="{outside}/get"><input name="q"></form>'
                f'<a href="{outside}/search?q=one">external</a>'
                '<a href="/local?q=one">local</a>')
        return reflect(path, data)

    inside = start(route)
    findings = dxadyn.crawl(inside + "/", 1)
    assert all(port != int(outside.rsplit(":", 1)[1]) for port, *_ in requests)
    assert any(row["param"] == "q" for row in findings)


@pytest.mark.parametrize("entry", ["/redirect", "/"])
def test_crawl_blocks_external_redirect_before_request(lab, entry):
    start, requests = lab
    outside = start(reflect)

    def route(path, data):
        if path == "/":
            return 200, {}, '<a href="/redirect?q=one">redirect</a>'
        return 302, {"Location": outside + "/capture"}, ""

    inside = start(route)
    assert dxadyn.crawl(inside + entry, 1) == []
    assert all(port != int(outside.rsplit(":", 1)[1]) for port, *_ in requests)
    assert any(event.reason == "out-of-scope-redirect" for event in dxadyn.REPORT_EVENTS)


def test_same_origin_redirect_and_empty_cookie_jar_preserve_session(lab):
    start, requests = lab

    def route(path, data):
        if path == "/":
            return 302, {"Location": "/landing", "Set-Cookie": "sid=local; Path=/"}, ""
        if path == "/landing":
            return 200, {}, '<form action="/submit" method="post"><input name="q"></form>'
        return reflect(path, data)

    inside = start(route)
    findings = dxadyn.crawl(inside + "/", 0)
    submissions = [r for r in requests if r[1] == "POST"]
    assert len(findings) == 1
    assert len(submissions) == 1
    assert submissions[0][3].get("Cookie") == "sid=local"


@pytest.mark.parametrize("redirect_refresh", [False, True])
def test_csrf_refresh_cannot_leave_crawl_origin(lab, monkeypatch, redirect_refresh):
    start, requests = lab
    outside = start(lambda path, data: (200, {}, '<input name="csrf_token" value="local-token">'))

    def route(path, data):
        if path == "/token":
            return 302, {"Location": outside + "/token"}, ""
        return 200, {}, '<form action="/submit" method="post"><input name="q"></form>'

    inside = start(route)
    monkeypatch.setattr(dxadyn, "CSRF_REFRESH_URL", (inside if redirect_refresh else outside) + "/token")
    monkeypatch.setattr(dxadyn, "CSRF_HEADER_NAME", "X-CSRF-Token")
    assert dxadyn.crawl(inside + "/", 0) == []
    assert all(port != int(outside.rsplit(":", 1)[1]) for port, *_ in requests)
    assert not any(r[1] == "POST" for r in requests)


def test_same_origin_csrf_refresh_and_submit_work(lab, monkeypatch):
    start, requests = lab

    def route(path, data):
        if path == "/":
            return 200, {}, '<form action="/submit" method="post"><input name="q"></form>'
        if path == "/token":
            return 200, {"Set-Cookie": "sid=local; Path=/"}, '<input name="csrf_token" value="local-token">'
        return reflect(path, data)

    inside = start(route)
    monkeypatch.setattr(dxadyn, "CSRF_REFRESH_URL", inside + "/token")
    monkeypatch.setattr(dxadyn, "CSRF_HEADER_NAME", "X-CSRF-Token")
    assert len(dxadyn.crawl(inside + "/", 0)) == 1
    submitted = next(r for r in requests if r[1] == "POST")
    assert submitted[3].get("X-Csrf-Token") == "local-token"
    assert submitted[3].get("Cookie") == "sid=local"


@pytest.mark.parametrize("url", ["https://example.test/", "http://example.test:81/", "http://other.test/", "file:///tmp/test"])
def test_origin_boundary_includes_scheme_host_and_port(url):
    assert not dxadyn._in_origin(url, dxadyn._origin("http://example.test/"))
