"""R9 real loopback HTTP boundary regressions; no existing databases touched."""
import http.client
import json
import socket
import sqlite3

import pytest

from dxa_callback import CallbackServer
from dxa_callback import CallbackDB
from dxa_callback import _valid_cid


@pytest.mark.parametrize("cid", ["caf\u00e9", "\uff11", "\u03b1"])
def test_cid_rejects_non_ascii_identifiers(cid):
    assert not _valid_cid(cid)


def exchange(srv, path, headers=(), method="GET", body=b"", finish=True):
    with socket.create_connection(("127.0.0.1", srv.port), timeout=2) as conn:
        request = f"{method} {path} HTTP/1.1\r\nHost: 127.0.0.1:{srv.port}\r\n"
        request += "".join(f"{key}: {value}\r\n" for key, value in headers)
        conn.sendall(request.encode() + b"\r\n" + body)
        if finish:
            conn.shutdown(socket.SHUT_WR)
        response = http.client.HTTPResponse(conn)
        response.begin()
        return response.status, dict(response.getheaders()), response.read()


@pytest.fixture
def srv():
    with CallbackServer(request_timeout=0.15, list_limit=3) as server:
        yield server


@pytest.mark.parametrize("limit", ["", "-1", "0", "4", "1&limit=", "1&limit=2", "nan", "9" * 100])
def test_invalid_limits_fail_closed(srv, limit):
    assert exchange(srv, "/hits?limit=" + limit)[0] == 400


@pytest.mark.parametrize("path", ["/hits", "/hits/cid", "/healthz"])
@pytest.mark.parametrize("headers", [[("Host", "attacker.invalid")], [("Origin", "")], [("Origin", "null")], [("Sec-Fetch-Site", "cross-site")]])
def test_browser_and_ambiguous_host_reads_denied(srv, path, headers):
    status, hdrs, _ = exchange(srv, path, headers)
    assert status == 403
    assert "Access-Control-Allow-Origin" not in hdrs


def test_bearer_and_duplicates():
    token = "test-only-token-123456"
    with CallbackServer(read_token=token) as server:
        assert exchange(server, "/hits")[0] == 401
        auth = [("Authorization", "Bearer " + token)]
        assert exchange(server, "/hits", auth)[0] == 200
        assert exchange(server, "/hits", auth * 2)[0] == 401
        assert exchange(server, "/c/cid")[0] == 200


@pytest.mark.parametrize("headers,body,finish,status", [
    ([], b"", True, 400),
    ([("Content-Length", "-1")], b"", True, 400),
    ([("Content-Length", "0"), ("Content-Length", "0")], b"", True, 400),
    ([("Content-Length", "0"), ("Transfer-Encoding", "chunked")], b"", True, 400),
    ([("Content-Length", "2049")], b"", True, 413),
    ([("Content-Length", "2")], b"a", True, 400),
    ([("Content-Length", "2")], b"a", False, 408),
])
def test_bad_post_never_records(srv, headers, body, finish, status):
    assert exchange(srv, "/c/cid", headers, "POST", body, finish)[0] == status
    assert srv.db.count() == 0


def test_collection_privacy_and_boundary(srv):
    headers = [("Content-Length", "2048"), ("User-Agent", "private"), ("Referer", "http://private/")]
    assert exchange(srv, "/c/cid?secret=private", headers, "POST", b"x" * 2048)[0] == 200
    row = srv.db.list_all()[0]
    assert row["path"] == "/c/cid"
    assert all(row[key] is None for key in ("user_agent", "referer", "body_preview"))


@pytest.mark.parametrize("path,operation", [("/hits", "list_all"), ("/hits/cid", "list_for_cid"), ("/healthz", "count"), ("/c/cid", "record")])
def test_sqlite_failure_is_unavailable_not_empty(srv, monkeypatch, path, operation):
    def fail(*args, **kwargs):
        raise sqlite3.OperationalError("private database path")
    monkeypatch.setattr(srv.db, operation, fail)
    status, _, body = exchange(srv, path)
    assert status == 503
    assert json.loads(body) == {"error": "callback storage unavailable"}


@pytest.mark.parametrize("path,allowed", [("/c/cid", True), ("/c/cid.js", True),
                                        ("/callback", True), ("/hits", False),
                                        ("/hits/cid", False), ("/healthz", False),
                                        ("/missing", False)])
@pytest.mark.parametrize("method", ["GET", "OPTIONS"])
def test_cors_only_allows_collection(srv, path, allowed, method):
    _, headers, _ = exchange(srv, path, method=method)
    assert headers.get("Access-Control-Allow-Origin") == ("*" if allowed else None)


@pytest.mark.parametrize("method", ["GET", "POST"])
def test_readonly_sqlite_write_failure_preserves_prior_hit(srv, method):
    assert exchange(srv, "/c/prior")[0] == 200
    prior = srv.db.list_all()
    srv.db._conn.execute("PRAGMA query_only=ON")
    status, _, body = exchange(srv, "/c/new", [("Content-Length", "0")], method=method)
    assert status == 503
    assert json.loads(body) == {"error": "callback storage unavailable"}
    assert srv.db.list_all() == prior


def test_legacy_database_rows_preserved(tmp_path):
    path = str(tmp_path / "legacy.db")
    old = CallbackDB(path)
    old.record("old", "POST", "/c/old", "legacy-UA", "127.0.0.1", "legacy-referrer", "legacy-body")
    expected = old.list_all()
    schema = old._conn.execute("SELECT sql FROM sqlite_master ORDER BY name").fetchall()
    old.close()
    with CallbackServer(db_path=path) as server:
        assert server.db.list_all() == expected
        assert server.db._conn.execute("SELECT sql FROM sqlite_master ORDER BY name").fetchall() == schema
        assert exchange(server, "/c/new")[0] == 200
    reopened = CallbackDB(path)
    try:
        assert reopened.list_for_cid("old") == expected
        assert reopened.count() == 2
    finally:
        reopened.close()
