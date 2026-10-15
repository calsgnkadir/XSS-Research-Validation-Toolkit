"""R4 independent HTTP-role and browser oracle for a blind stored submission."""
from __future__ import annotations

import os
import pathlib
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from r4_admin_fixture import FixtureServer


def _client(origin, user=None):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}),
                                         urllib.request.HTTPCookieProcessor())
    if user:
        password = "admin-pass" if user == "reader-admin" else "writer-pass"
        body = urllib.parse.urlencode({"user": user, "password": password}).encode()
        response = opener.open(urllib.request.Request(origin + "/login", data=body), timeout=3)
        assert response.status == 200
        response.close()
    return opener


def _get(opener, url):
    try:
        response = opener.open(url, timeout=3)
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()
    with response:
        return response.status, response.read().decode()


def _post(opener, url, fields):
    body = urllib.parse.urlencode(fields).encode()
    try:
        response = opener.open(urllib.request.Request(url, data=body), timeout=3)
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()
    with response:
        return response.status, response.read().decode()


def test_writer_and_reader_admin_are_distinct_and_submission_is_blind():
    with FixtureServer() as app:
        anonymous = _client(app.origin)
        writer = _client(app.origin, "writer")
        admin = _client(app.origin, "reader-admin")
        assert _get(anonymous, app.origin + "/admin/comments")[0] == 401
        assert _get(writer, app.origin + "/admin/comments")[0] == 403
        assert _get(admin, app.origin + "/writer")[0] == 403
        assert _post(admin, app.origin + "/comments", {"comment": "admin cannot write"})[0] == 403

        cid = "r4-" + secrets.token_hex(12)
        payload = f'<img src="/missing?cid={cid}" onerror="window.__dxaProof=\'{cid}\'">'
        status, ack = _post(writer, app.origin + "/comments", {"comment": payload})
        assert (status, ack) == (200, "accepted")
        # The submit response does not echo the stored body; only the distinct
        # reader-admin session can read it after submission.
        assert cid not in ack
        assert _get(writer, app.origin + "/admin/comments")[0] == 403
        status, page = _get(admin, app.origin + "/admin/comments")
        assert status == 200 and payload in page
        assert app.state.comments == [("writer", payload)]


@pytest.mark.parametrize("route,expected", [("/admin/comments", True), ("/fixed/admin/comments", False)])
def test_admin_browser_oracle_matches_cid_and_escaped_control(route, expected):
    browser_path = os.environ.get("DXA_BROWSER")
    with FixtureServer() as app:
        writer, admin = _client(app.origin, "writer"), _client(app.origin, "reader-admin")
        cid = "r4-" + secrets.token_hex(12)
        payload = f'<img src="/missing?cid={cid}" onerror="window.__dxaProof=\'{cid}\'">'
        assert _post(writer, app.origin + "/comments", {"comment": payload})[0] == 200
        assert _get(writer, app.origin + route)[0] == 403
        assert _get(admin, app.origin + route)[0] == 200

        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            launch = {"headless": True}
            if browser_path:
                launch["executable_path"] = browser_path
            browser = pw.chromium.launch(**launch)
            try:
                context = browser.new_context()
                response = context.request.post(app.origin + "/login", form={"user": "reader-admin", "password": "admin-pass"})
                assert response.status == 200
                context.add_cookies([{"name": "session", "value": response.headers["set-cookie"].split(";", 1)[0].split("=", 1)[1],
                                      "url": app.origin, "httpOnly": True, "sameSite": "Strict"}])
                page = context.new_page()
                result = page.goto(app.origin + route, wait_until="load", timeout=5000)
                assert result and result.status == 200
                page.wait_for_timeout(250)
                observed = page.evaluate("() => window.__dxaProof || null") == cid
                assert observed is expected
            finally:
                browser.close()
