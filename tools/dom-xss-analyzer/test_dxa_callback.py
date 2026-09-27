"""Phase 3.1: callback server tests. Zero-dep, no browser needed."""
from __future__ import annotations
import http.client
import json
import pathlib
import sqlite3
import sys
import threading
import time

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import dxa_callback  # noqa: E402


# --- CallbackDB unit tests -------------------------------------------------

def test_db_starts_empty():
    db = dxa_callback.CallbackDB(":memory:")
    try:
        assert db.count() == 0
        assert db.list_all() == []
    finally:
        db.close()


def test_db_records_and_retrieves():
    db = dxa_callback.CallbackDB(":memory:")
    try:
        rowid = db.record("dxaCAFE", "GET", "/c/dxaCAFE",
                          user_agent="Mozilla", remote_ip="1.2.3.4",
                          referer=None, body_preview=None)
        assert rowid > 0
        assert db.count() == 1
        rows = db.list_all()
        assert len(rows) == 1
        r = rows[0]
        assert r["cid"] == "dxaCAFE"
        assert r["method"] == "GET"
        assert r["user_agent"] == "Mozilla"
        assert r["remote_ip"] == "1.2.3.4"
        assert isinstance(r["ts"], float) and r["ts"] > 0
    finally:
        db.close()


def test_db_list_for_cid_filters():
    db = dxa_callback.CallbackDB(":memory:")
    try:
        db.record("dxaA", "GET", "/c/dxaA", None, None, None, None)
        db.record("dxaB", "GET", "/c/dxaB", None, None, None, None)
        db.record("dxaA", "GET", "/c/dxaA", None, None, None, None)
        for_a = db.list_for_cid("dxaA")
        assert len(for_a) == 2
        assert all(r["cid"] == "dxaA" for r in for_a)
        for_b = db.list_for_cid("dxaB")
        assert len(for_b) == 1
    finally:
        db.close()


def test_db_list_all_returns_newest_first():
    db = dxa_callback.CallbackDB(":memory:")
    try:
        db.record("dxaA", "GET", "/c/dxaA", None, None, None, None)
        db.record("dxaB", "GET", "/c/dxaB", None, None, None, None)
        rows = db.list_all()
        assert rows[0]["cid"] == "dxaB"
        assert rows[1]["cid"] == "dxaA"
    finally:
        db.close()


def test_db_list_all_respects_limit():
    db = dxa_callback.CallbackDB(":memory:")
    try:
        for i in range(10):
            db.record(f"cid-{i}", "GET", "/c/x", None, None, None, None)
        assert len(db.list_all(limit=3)) == 3
    finally:
        db.close()


def test_db_persists_across_reopen(tmp_path):
    """A closed + reopened DB retrieves prior hits."""
    db_path = str(tmp_path / "cb.db")
    db1 = dxa_callback.CallbackDB(db_path)
    db1.record("dxaP", "GET", "/c/dxaP", None, None, None, None)
    db1.close()

    db2 = dxa_callback.CallbackDB(db_path)
    try:
        assert db2.count() == 1
        assert db2.list_all()[0]["cid"] == "dxaP"
    finally:
        db2.close()


def test_db_concurrent_writes_safe():
    """Many threads writing at once must all land - the lock guarantees
    no lost writes under stdlib HTTPServer's threaded handler pool."""
    db = dxa_callback.CallbackDB(":memory:")
    try:
        N = 200
        errors = []
        def _writer(i):
            try:
                db.record(f"cid-{i}", "GET", "/c/x",
                          None, None, None, None)
            except Exception as e:
                errors.append(e)
        threads = [threading.Thread(target=_writer, args=(i,))
                   for i in range(N)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert errors == []
        assert db.count() == N
    finally:
        db.close()


# --- _valid_cid --------------------------------------------------------------

def test_valid_cid_accepts_dxadyn_format():
    """dxadyn mints cids as `dxa` + 8 hex chars."""
    assert dxa_callback._valid_cid("dxaCAFEBABE")
    assert dxa_callback._valid_cid("dxa12345678")


def test_valid_cid_accepts_underscore_and_dash():
    assert dxa_callback._valid_cid("op_test-01")


def test_valid_cid_rejects_path_abuse():
    """No `/`, no `..`, no `?`, no URL characters that would let an
    attacker steer records into a different table row via SQL literal
    escape (defensive; we use bound params, but the input filter is
    an early boundary)."""
    for bad in ("../../etc/passwd", "foo/bar", "foo?a=1",
                "'; DROP TABLE hits;--", "with space", ""):
        assert not dxa_callback._valid_cid(bad)


def test_valid_cid_rejects_too_long():
    assert not dxa_callback._valid_cid("a" * 65)


# --- HTTP endpoint tests (real server on ephemeral port) --------------------

@pytest.fixture
def server():
    srv = dxa_callback.CallbackServer(port=0, db_path=":memory:")
    srv.start()
    try:
        yield srv
    finally:
        srv.stop()


def _get(port, path, headers=None):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    conn.request("GET", path, headers=headers or {})
    resp = conn.getresponse()
    body = resp.read()
    hdrs = dict(resp.getheaders())
    conn.close()
    return resp.status, hdrs, body


def _post(port, path, body=b"", headers=None):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    hdrs = dict(headers or {})
    hdrs.setdefault("Content-Length", str(len(body)))
    conn.request("POST", path, body=body, headers=hdrs)
    resp = conn.getresponse()
    rbody = resp.read()
    rhdrs = dict(resp.getheaders())
    conn.close()
    return resp.status, rhdrs, rbody


def test_get_c_cid_returns_1x1_gif_and_records(server):
    status, hdrs, body = _get(
        server.port, "/c/dxaHIT01",
        headers={"User-Agent": "TestUA", "Referer": "https://victim.test/"})
    assert status == 200
    assert hdrs.get("Content-Type") == "image/gif"
    assert body[:6] in (b"GIF89a", b"GIF87a")
    assert hdrs.get("Access-Control-Allow-Origin") == "*"
    # And the hit landed in the DB.
    assert server.db.count() == 1
    row = server.db.list_all()[0]
    assert row["cid"] == "dxaHIT01"
    assert row["user_agent"] == "TestUA"
    assert row["referer"] == "https://victim.test/"
    assert row["method"] == "GET"


def test_get_c_cid_js_returns_javascript(server):
    """<script src=/c/<cid>.js> payloads need a valid JS content type."""
    status, hdrs, body = _get(server.port, "/c/dxaJS01.js")
    assert status == 200
    assert hdrs.get("Content-Type") == "application/javascript"
    assert b"void" in body
    assert server.db.list_for_cid("dxaJS01")[0]["cid"] == "dxaJS01"


def test_post_c_cid_stores_body_preview(server):
    payload = b'{"stolen": "cookie=abc; token=xyz"}'
    status, hdrs, body = _post(
        server.port, "/c/dxaPOST", body=payload,
        headers={"Content-Type": "application/json"})
    assert status == 200
    parsed = json.loads(body)
    assert parsed == {"ok": True}
    row = server.db.list_for_cid("dxaPOST")[0]
    assert row["body_preview"] == payload.decode()


def test_post_body_truncated_at_preview_limit(server):
    """Large POSTs are truncated to 2 KiB; the tail must be dropped so
    the DB doesn't grow unbounded per hit."""
    payload = b"A" * 8000
    status, _, _ = _post(server.port, "/c/dxaBIG", body=payload)
    assert status == 200
    row = server.db.list_for_cid("dxaBIG")[0]
    assert len(row["body_preview"]) <= dxa_callback._BODY_PREVIEW_MAX


def test_get_callback_generic_no_cid(server):
    """The `/callback` endpoint accepts fingerprinting payloads that
    don't carry a cid; hits are recorded under the literal cid
    'callback'."""
    status, hdrs, _ = _get(server.port, "/callback")
    assert status == 200
    assert hdrs.get("Content-Type") == "image/gif"
    assert server.db.list_for_cid("callback")[0]["cid"] == "callback"


def test_get_hits_returns_all(server):
    _get(server.port, "/c/dxaA")
    _get(server.port, "/c/dxaB")
    status, hdrs, body = _get(server.port, "/hits")
    assert status == 200
    assert hdrs.get("Content-Type") == "application/json"
    obj = json.loads(body)
    assert len(obj["hits"]) == 2
    # Newest first
    assert obj["hits"][0]["cid"] == "dxaB"


def test_get_hits_per_cid(server):
    _get(server.port, "/c/dxaA")
    _get(server.port, "/c/dxaB")
    _get(server.port, "/c/dxaA")
    status, _, body = _get(server.port, "/hits/dxaA")
    assert status == 200
    obj = json.loads(body)
    assert obj["cid"] == "dxaA"
    assert len(obj["hits"]) == 2


def test_get_hits_invalid_cid_returns_400(server):
    status, _, body = _get(server.port, "/hits/..%2Fetc%2Fpasswd")
    assert status == 400
    assert b"invalid" in body.lower()


def test_healthz_reports_ok_and_count(server):
    _get(server.port, "/c/dxaHZ")
    status, _, body = _get(server.port, "/healthz")
    assert status == 200
    obj = json.loads(body)
    assert obj == {"ok": True, "hits": 1}


def test_options_returns_204_with_cors(server):
    """CORS preflight returns 204 + Access-Control-* headers."""
    conn = http.client.HTTPConnection("127.0.0.1", server.port, timeout=5)
    conn.request("OPTIONS", "/c/dxaCORS")
    resp = conn.getresponse()
    conn.close()
    assert resp.status == 204
    assert resp.getheader("Access-Control-Allow-Origin") == "*"


def test_unknown_path_returns_404(server):
    status, _, body = _get(server.port, "/nope")
    assert status == 404
    assert b"not found" in body


def test_x_forwarded_for_respected(server):
    """When behind a reverse proxy, XFF header is the real client IP."""
    _get(server.port, "/c/dxaXFF",
         headers={"X-Forwarded-For": "203.0.113.5, 10.0.0.1"})
    row = server.db.list_for_cid("dxaXFF")[0]
    assert row["remote_ip"] == "203.0.113.5"


def test_concurrent_hits_all_recorded(server):
    """Many parallel GETs must all land - proves the DB lock survives
    stdlib HTTPServer's threaded handler pool."""
    N = 50
    threads = []
    for i in range(N):
        t = threading.Thread(
            target=lambda i=i: _get(server.port, f"/c/dxaCONC{i:03d}"))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    # Give the server a beat to flush any pending inserts.
    time.sleep(0.05)
    assert server.db.count() == N


def test_context_manager_starts_and_stops():
    """CallbackServer must work as a `with` block for clean test setup."""
    with dxa_callback.CallbackServer(port=0, db_path=":memory:") as srv:
        status, _, _ = _get(srv.port, "/healthz")
        assert status == 200
    # After exit, server is stopped - connecting should now fail.
    import socket
    with pytest.raises((ConnectionRefusedError, socket.error, OSError)):
        _get(srv.port, "/healthz")
