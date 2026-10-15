"""Browser and server-budget oracle for the R4 comparison fixture."""
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
from r4_comparison_fixture import R4ComparisonFixture


def _request(origin, method="GET", path="/", cookie=None, fields=None):
    body = urllib.parse.urlencode(fields).encode() if fields is not None else None
    headers = {"Cookie": "bridge=" + cookie} if cookie else {}
    request = urllib.request.Request(origin + path, data=body, headers=headers, method=method)
    try:
        response = urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=3)
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace")
    with response:
        return response.status, response.read().decode("utf-8", "replace")


@pytest.mark.parametrize("escaped,expected", [(False, True), (True, False)])
def test_brokered_writer_submission_and_reader_admin_browser_oracle(escaped, expected):
    browser_path = os.environ.get("DXA_BROWSER")
    if not browser_path:
        pytest.fail("DXA_BROWSER must identify the installed local browser")
    with R4ComparisonFixture(escaped=escaped) as fixture:
        cookie = fixture.state.broker_cookie()
        assert _request(fixture.origin, path="/comments")[0] == 401
        cid = "cmp-" + secrets.token_hex(12)
        payload = f'<img src="/missing?cid={cid}" onerror="window.__dxaProof=\'{cid}\'">'
        status, ack = _request(fixture.origin, "POST", "/comments", cookie, {"comment": payload})
        assert (status, ack) == (200, "accepted")
        assert cid not in ack
        status, body = _request(fixture.origin, path="/admin/comments", cookie=cookie)
        assert status == 200 and cid in body
        assert fixture.state.sessions[cookie] == ("writer", "reader-admin")

        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, executable_path=browser_path)
            try:
                context = browser.new_context()
                context.add_cookies([{"name": "bridge", "value": cookie, "url": fixture.origin,
                                      "httpOnly": True, "sameSite": "Strict"}])
                page = context.new_page()
                response = page.goto(fixture.origin + "/admin/comments", wait_until="load", timeout=5000)
                assert response and response.status == 200
                page.wait_for_timeout(750)
                observed = page.evaluate("() => window.__dxaProof || null") == cid
                assert observed is expected
            finally:
                browser.close()


def test_server_budget_serializes_and_caps_requests():
    with R4ComparisonFixture(escaped=False, request_limit=1, rate_limit=100,
                             wall_limit=3) as fixture:
        cookie = fixture.state.broker_cookie()
        assert _request(fixture.origin, path="/comments", cookie=cookie)[0] == 200
        assert _request(fixture.origin, path="/admin/comments", cookie=cookie)[0] == 429
        assert fixture.state.budget_exceeded is True
        assert fixture.state.max_inflight == 1
