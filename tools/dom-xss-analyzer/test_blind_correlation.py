"""Phase 3.3: blind XSS correlation + reporting tests.

Covers:
  - check_blind_callback_hit polling contract (found, timeout, disabled)
  - upgrade_finding_with_blind_hit severity + schema mutation
  - correlate_blind_findings filters blind-only, upgrades on hit
  - render_html includes the blind-hits section with UA / IP / Referer
"""
from __future__ import annotations
import pathlib
import sys
import threading
import time

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import dxadyn      # noqa: E402
import dxa_callback  # noqa: E402


# --- fixture: real callback server + BLIND_CALLBACK wired to it ------------

@pytest.fixture
def callback_server():
    srv = dxa_callback.CallbackServer(port=0, db_path=":memory:")
    srv.start()
    old_cb = dxadyn.BLIND_CALLBACK
    old_wait = dxadyn.BLIND_WAIT_SECONDS
    dxadyn.BLIND_CALLBACK = f"http://127.0.0.1:{srv.port}"
    dxadyn.BLIND_WAIT_SECONDS = 2.0
    try:
        yield srv
    finally:
        srv.stop()
        dxadyn.BLIND_CALLBACK = old_cb
        dxadyn.BLIND_WAIT_SECONDS = old_wait


# --- check_blind_callback_hit ----------------------------------------------

def test_check_returns_none_when_no_callback():
    """Empty BLIND_CALLBACK -> None immediately, no network round-trip."""
    dxadyn.BLIND_CALLBACK = ""
    dxadyn.BLIND_WAIT_SECONDS = 5.0
    assert dxadyn.check_blind_callback_hit("dxaCAFE") is None


def test_check_returns_none_when_timeout_zero(callback_server):
    """timeout=0 short-circuits even when BLIND_CALLBACK is set."""
    result = dxadyn.check_blind_callback_hit("dxaCAFE", timeout=0)
    assert result is None


def test_check_returns_hit_when_present(callback_server):
    """A hit recorded before the poll starts returns immediately."""
    callback_server.db.record(
        "dxaHIT01", "GET", "/c/dxaHIT01",
        user_agent="Mozilla/5.0", remote_ip="10.0.0.1",
        referer="https://target.test/admin", body_preview=None)
    hit = dxadyn.check_blind_callback_hit("dxaHIT01", timeout=1)
    assert hit is not None
    assert hit["cid"] == "dxaHIT01"
    assert hit["user_agent"] == "Mozilla/5.0"


def test_check_polls_until_deadline_then_returns_none(callback_server):
    """No hit + short timeout -> None after roughly timeout seconds."""
    t0 = time.monotonic()
    result = dxadyn.check_blind_callback_hit(
        "dxaMISS", timeout=0.6, poll_interval=0.2)
    elapsed = time.monotonic() - t0
    assert result is None
    # Elapsed must be at least the timeout (with some slack for scheduler).
    assert 0.5 <= elapsed <= 2.5, f"elapsed={elapsed}"


def test_check_returns_hit_arriving_mid_poll(callback_server):
    """A hit that lands DURING the poll window is returned as soon as
    the next poll interval elapses."""
    def _delayed_hit():
        time.sleep(0.3)
        callback_server.db.record(
            "dxaLATE", "GET", "/c/dxaLATE",
            user_agent="LateBrowser", remote_ip="1.1.1.1",
            referer=None, body_preview=None)
    threading.Thread(target=_delayed_hit, daemon=True).start()
    hit = dxadyn.check_blind_callback_hit(
        "dxaLATE", timeout=2.0, poll_interval=0.1)
    assert hit is not None
    assert hit["cid"] == "dxaLATE"


def test_check_unreachable_server_returns_none_no_raise():
    """Server down / bad URL -> None quietly, never raises."""
    dxadyn.BLIND_CALLBACK = "http://127.0.0.1:1"
    dxadyn.BLIND_WAIT_SECONDS = 0.5
    try:
        result = dxadyn.check_blind_callback_hit(
            "dxaX", timeout=0.5, poll_interval=0.1)
        assert result is None
    finally:
        dxadyn.BLIND_CALLBACK = ""


# --- upgrade_finding_with_blind_hit ----------------------------------------

def _mk_finding(cid="dxaCAFE", variant="blind-img", severity="executable"):
    return {
        "url": "http://target/x", "method": "POST", "param": "msg",
        "reflection": "unencoded", "confidence": "high",
        "status": 200, "context": "body", "severity": severity,
        "canary_id": cid, "variant": variant,
        "blind_callback_hit": False, "hit_at": None,
        "hit_from_ua": None, "hit_from_ip": None, "hit_from_referer": None,
    }


def _mk_hit(cid="dxaCAFE"):
    return {
        "id": 1, "cid": cid, "ts": 1234567890.5,
        "method": "GET", "path": f"/c/{cid}",
        "user_agent": "AdminBrowser/1.0",
        "remote_ip": "10.0.0.42",
        "referer": "https://admin.target.test/tickets/42",
        "body_preview": None,
    }


def test_upgrade_promotes_severity_and_fills_schema():
    f = _mk_finding()
    h = _mk_hit()
    ok = dxadyn.upgrade_finding_with_blind_hit(f, h)
    assert ok is True
    assert f["severity"] == dxadyn.PROVEN_BLIND == "proven-blind"
    assert f["blind_callback_hit"] is True
    assert f["hit_at"] == 1234567890.5
    assert f["hit_from_ua"] == "AdminBrowser/1.0"
    assert f["hit_from_ip"] == "10.0.0.42"
    assert f["hit_from_referer"] == "https://admin.target.test/tickets/42"


def test_upgrade_none_hit_is_noop():
    f = _mk_finding()
    assert dxadyn.upgrade_finding_with_blind_hit(f, None) is False
    assert f["severity"] == "executable"
    assert f["blind_callback_hit"] is False


def test_upgrade_rejects_cid_mismatch():
    """Defensive: a hit whose cid doesn't match the finding must NOT
    upgrade the finding. Guards against caller misuse."""
    f = _mk_finding(cid="dxaAAA")
    h = _mk_hit(cid="dxaBBB")
    assert dxadyn.upgrade_finding_with_blind_hit(f, h) is False
    assert f["severity"] == "executable"


# --- correlate_blind_findings ----------------------------------------------

def test_correlate_returns_zero_when_no_callback():
    dxadyn.BLIND_CALLBACK = ""
    dxadyn.BLIND_WAIT_SECONDS = 5
    n, out = dxadyn.correlate_blind_findings([_mk_finding()])
    assert n == 0


def test_correlate_returns_zero_when_wait_zero(callback_server):
    dxadyn.BLIND_WAIT_SECONDS = 0
    n, _ = dxadyn.correlate_blind_findings([_mk_finding()])
    assert n == 0


def test_correlate_upgrades_matching_blind_finding(callback_server):
    callback_server.db.record(
        "dxaCAFE", "GET", "/c/dxaCAFE",
        user_agent="Victim/2.0", remote_ip="203.0.113.9",
        referer="https://admin/tickets", body_preview=None)
    finding = _mk_finding(cid="dxaCAFE")
    n, out = dxadyn.correlate_blind_findings([finding], timeout=1.0)
    assert n == 1
    assert out[0]["severity"] == "proven-blind"
    assert out[0]["hit_from_ip"] == "203.0.113.9"


def test_correlate_skips_non_blind_findings(callback_server):
    """A `body` or `title-breakout` finding is not blind - no polling
    should happen for it."""
    reflected = _mk_finding(cid="dxaREF", variant="body")
    n, out = dxadyn.correlate_blind_findings([reflected], timeout=0.5)
    assert n == 0
    assert out[0]["severity"] == "executable"  # unchanged
    assert out[0]["blind_callback_hit"] is False


def test_correlate_multiple_findings_only_matched_upgraded(callback_server):
    """Only findings whose cid appears in the callback are upgraded;
    the others stay at their pre-correlation severity."""
    callback_server.db.record(
        "dxaONE", "GET", "/c/dxaONE", "UA", "1.1.1.1", None, None)
    a = _mk_finding(cid="dxaONE", variant="blind-img")
    b = _mk_finding(cid="dxaTWO", variant="blind-img")
    n, out = dxadyn.correlate_blind_findings([a, b], timeout=0.5)
    assert n == 1
    upgraded = [f for f in out if f["severity"] == "proven-blind"]
    assert len(upgraded) == 1
    assert upgraded[0]["canary_id"] == "dxaONE"


def test_correlate_handles_subvariant_names(callback_server):
    """A variant name like `blind-img/case` (waf-mutation subvariant,
    hypothetical) still counts as blind for correlation - the family
    prefix is what matters."""
    callback_server.db.record(
        "dxaSUB", "GET", "/c/dxaSUB", "UA", "1.1.1.1", None, None)
    f = _mk_finding(cid="dxaSUB", variant="blind-img/case")
    n, _ = dxadyn.correlate_blind_findings([f], timeout=0.5)
    assert n == 1


# --- render_html blind section ---------------------------------------------

def test_render_html_shows_blind_section_when_hit_present():
    """A finding with blind_callback_hit=True must produce a dedicated
    'blind XSS - callback confirmed' section carrying UA / IP / Referer."""
    f = _mk_finding(cid="dxaHTML")
    f["blind_callback_hit"] = True
    f["hit_at"] = 1234567890.5
    f["hit_from_ua"] = "Mozilla/5.0 (Windows NT 10.0) AdminBrowser/2"
    f["hit_from_ip"] = "203.0.113.5"
    f["hit_from_referer"] = "https://admin.target.test/panel"
    f["severity"] = "proven-blind"

    html = dxadyn.render_html([f], target="target.test", mode="stored-auto")
    assert "blind XSS" in html
    assert "callback confirmed" in html
    assert "dxaHTML" in html
    assert "203.0.113.5" in html
    assert "admin.target.test" in html
    # AdminBrowser is captured (may be truncated by the report's 60-char cap)
    assert "AdminBrowser" in html


def test_render_html_omits_blind_section_when_no_hits():
    """Reflected-only report should not carry the blind section shell."""
    f = _mk_finding(variant="body")
    html = dxadyn.render_html([f], target="target.test", mode="reflected")
    assert "blind XSS" not in html
    assert "callback confirmed" not in html


def test_render_html_blind_stat_tile_present():
    """The stat tiles row should include a `blind (proven)` tile when
    any finding carries a blind hit."""
    f = _mk_finding()
    f["blind_callback_hit"] = True
    f["severity"] = "proven-blind"
    html = dxadyn.render_html([f], target="t", mode="stored")
    assert "blind (proven)" in html
