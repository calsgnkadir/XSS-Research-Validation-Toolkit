"""Role/session isolation and evidence privacy regressions for R4 scanner runs."""
from __future__ import annotations

import pathlib
import sys
import urllib.error
import urllib.request

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from r4_comparison_fixture import R4ComparisonFixture
from r4_scanner_sessions import check_scanner_sessions, provision_scanner_sessions
from r4_compare_local import _redact_auth_text


def request(origin, path, cookie=None, method="GET", body=None):
    headers = {"Cookie": cookie} if cookie else {}
    req = urllib.request.Request(origin + path, headers=headers, method=method, data=body)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=2) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code


def test_two_scanner_principals_are_independently_authenticated_and_path_limited():
    with R4ComparisonFixture(escaped=False, request_limit=30, rate_limit=100, wall_limit=5) as fixture:
        sessions = provision_scanner_sessions(fixture)
        assert sessions.writer_token != sessions.admin_token
        assert sessions.writer_token != fixture.state.login_secrets["writer"]
        assert sessions.admin_token != fixture.state.login_secrets["reader-admin"]
        pair = sessions.cookie_header
        assert request(fixture.origin, "/session/writer", pair) == 200
        assert request(fixture.origin, "/session/reader-admin", pair) == 200

        # Each protected endpoint consults only its designated session identity.
        assert request(fixture.origin, "/admin/comments",
                       f"writer_session={sessions.writer_token}") == 401
        assert request(fixture.origin, "/comments", method="POST",
                       cookie=f"admin_session={sessions.admin_token}",
                       body=b"comment=blocked") == 401
        assert request(fixture.origin, "/session/writer",
                       f"writer_session={sessions.admin_token}") == 403
        assert request(fixture.origin, "/session/reader-admin",
                       f"admin_session={sessions.writer_token}") == 403


def test_pre_and_post_checks_record_exact_role_without_credential_values():
    with R4ComparisonFixture(escaped=False, request_limit=30, rate_limit=100, wall_limit=5) as fixture:
        sessions = provision_scanner_sessions(fixture)
        checks = check_scanner_sessions(fixture, sessions, "pre")
        assert all(row["passed"] for row in checks.values())
        checks.update(check_scanner_sessions(fixture, sessions, "post"))
        record = sessions.public_record(checks)
        text = repr(record)
        assert sessions.writer_token not in text
        assert sessions.admin_token not in text
        assert record["writer"]["role"] == "writer"
        assert record["reader_admin"]["role"] == "reader-admin"
        assert record["writer"]["pre"] and record["writer"]["post"]
        assert record["reader_admin"]["pre"] and record["reader_admin"]["post"]
        assert record["cookie_values_recorded"] is False


def test_invalid_role_login_and_collapsed_cookie_pair_are_rejected():
    with R4ComparisonFixture(escaped=False, request_limit=20, rate_limit=100, wall_limit=5) as fixture:
        with pytest.raises(ValueError, match="unknown fixture role"):
            fixture.login("admin")
        with pytest.raises(ValueError, match="independent"):
            fixture.session_cookie("same", "same")


def test_failed_role_check_makes_session_pair_unfit_for_scanning(monkeypatch):
    with R4ComparisonFixture(escaped=False, request_limit=20, rate_limit=100, wall_limit=5) as fixture:
        sessions = provision_scanner_sessions(fixture)
        monkeypatch.setattr(fixture, "session_check",
                            lambda role, _token: {"passed": role == "writer", "principal": role,
                                                  "role": role})
        checks = check_scanner_sessions(fixture, sessions, "pre")
        assert checks["writer_pre"]["passed"]
        assert not checks["reader-admin_pre"]["passed"]
        assert not all(row["passed"] for row in checks.values())


def test_redactor_removes_both_tokens_pair_and_origin():
    with R4ComparisonFixture(escaped=False, request_limit=20, rate_limit=100, wall_limit=5) as fixture:
        sessions = provision_scanner_sessions(fixture)
        pair = sessions.cookie_header
        source = f"origin={fixture.origin} Cookie: {pair} writer={sessions.writer_token} admin={sessions.admin_token}"
        cleaned = _redact_auth_text(source, fixture.origin, sessions)
        for secret in (fixture.origin, pair, sessions.writer_token, sessions.admin_token):
            assert secret not in cleaned
        assert "<independent-writer-admin-session-pair>" in cleaned
