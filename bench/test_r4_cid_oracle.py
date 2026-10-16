"""Regression cases for strict R4 stored-CID to reader-browser correlation."""
from __future__ import annotations

import pathlib
import secrets
import sys
import urllib.parse
import urllib.request

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from r4_cid_oracle import evaluate_correlation, observe_reader_admin
from r4_comparison_fixture import R4ComparisonFixture


CASE = "r4-admin-stored/raw-admin-content"
CID = "dxa0123456789abcdef0123456789abcdef"
OTHER = "dxaabcdef0123456789abcdef0123456789"


def payload(cid= CID):
    return f'<img src="/missing?cid={cid}" onerror="window.__dxaProof=\'{cid}\'">'


def proof(cid=CID, **overrides):
    value = {
        "case_id": CASE,
        "read_path": "/admin/comments",
        "role": "reader-admin",
        "role_verified": True,
        "status": "execution-observed",
        "window_completed": True,
        "execution_observed": True,
        "canary_id": cid,
        "timed_out": False,
    }
    value.update(overrides)
    return value


def test_only_same_submitted_cid_and_reader_admin_execution_correlates():
    result = evaluate_correlation(CASE, "completed", [payload()], [proof()], escaped=False)
    assert result["outcome"] == "execution-correlated"
    assert result["matched_cids"] == [CID]
    assert result["execution_observed"] is True


def test_escaped_case_fails_if_its_submitted_cid_executes():
    result = evaluate_correlation(CASE, "completed", [payload()], [proof()], escaped=True)
    assert result["outcome"] == "failed-negative-control"


def test_escaped_case_is_negative_only_after_its_complete_reader_window():
    no_execution = proof(status="completed-no-execution", execution_observed=False)
    result = evaluate_correlation(CASE, "completed", [payload()], [no_execution], escaped=True)
    assert result["outcome"] == "completed-negative"
    assert result["completed"] is True


def test_escaped_candidate_without_reader_window_is_inconclusive():
    result = evaluate_correlation(CASE, "completed", [payload()], [], escaped=True)
    assert result["outcome"] == "inconclusive"
    assert result["completed"] is False


def test_escaped_multiple_candidates_need_a_window_for_each_identity():
    second = "dxa11111111111111111111111111111111"
    one_window = proof(status="completed-no-execution", execution_observed=False)
    result = evaluate_correlation(CASE, "completed", [payload(), payload(second)],
                                  [one_window], escaped=True)
    assert result["outcome"] == "inconclusive"
    assert result["completed_browser_window_cids"] == [CID]


@pytest.mark.parametrize("candidate", [
    "ordinary reflected text without CID",
    '<img src="/missing?cid=malformed" onerror="window.__dxaProof=\'malformed\'">',
    '<img src="/missing?cid=dxa0123456789abcdef0123456789abcdef" '
    'onerror="window.__dxaProof=\'dxaabcdef0123456789abcdef0123456789\'">',
])
def test_missing_or_malformed_cid_is_inconclusive_not_negative(candidate):
    no_execution = proof(status="completed-no-execution", execution_observed=False)
    result = evaluate_correlation(CASE, "completed", [candidate], [no_execution], escaped=False)
    assert result["outcome"] == "inconclusive"
    assert result["completed"] is False
    assert result["execution_observed"] is False


def test_duplicate_candidate_and_observation_identity_counts_once():
    result = evaluate_correlation(CASE, "completed", [payload(), payload()],
                                  [proof(), proof()], escaped=False)
    assert result["outcome"] == "execution-correlated"
    assert result["candidate_cids"] == [CID]
    assert result["matched_cids"] == [CID]
    assert result["duplicate_candidate_cids"] == [CID]
    assert result["duplicate_observation_cids"] == [CID]


def test_unrelated_execution_does_not_match_scanner_candidate():
    result = evaluate_correlation(CASE, "completed", [payload()], [proof(OTHER)], escaped=False)
    assert result["outcome"] == "inconclusive"
    assert result["matched_cids"] == []
    assert result["unrelated_execution_cids"] == [OTHER]


@pytest.mark.parametrize("changes", [
    {"role": "writer", "role_verified": False},
    {"read_path": "/comments"},
    {"case_id": "another-case"},
    {"window_completed": False},
])
def test_unverified_or_wrong_context_execution_claim_is_inconclusive(changes):
    result = evaluate_correlation(CASE, "completed", [payload()], [proof(**changes)], escaped=False)
    assert result["outcome"] == "inconclusive"
    assert result["matched_cids"] == []


def test_missing_completed_browser_window_is_inconclusive():
    result = evaluate_correlation(CASE, "completed", [payload()], [], escaped=False)
    assert result["outcome"] == "inconclusive"


@pytest.mark.parametrize("run_status", ["error", "skipped", "incomplete"])
def test_noncompleted_scanner_runs_never_become_negative(run_status):
    no_execution = proof(status="completed-no-execution", execution_observed=False)
    result = evaluate_correlation(CASE, run_status, [payload()], [no_execution], escaped=False)
    assert result["outcome"] == run_status
    assert result["completed"] is False


def test_timeout_precedes_absence_of_matching_execution():
    result = evaluate_correlation(CASE, "timeout", [payload()], [], escaped=False)
    assert result["outcome"] == "timeout"
    assert result["timed_out"] is True


def test_untrusted_execution_claim_cannot_be_used_as_a_negative_control_failure():
    result = evaluate_correlation(CASE, "completed", [payload()],
                                  [proof(role="writer", role_verified=False)], escaped=True)
    assert result["outcome"] == "inconclusive"


@pytest.mark.parametrize("escaped,expected", [(False, "execution-correlated"),
                                               (True, "completed-negative")])
def test_local_reader_browser_oracle_observes_only_the_submitted_fixture_cid(escaped, expected):
    browser_path = __import__("os").environ.get("DXA_BROWSER")
    case_id = "r4-admin-stored/escaped-admin-content" if escaped else CASE
    cid = "dxa" + secrets.token_hex(16)
    candidate = payload(cid)
    with R4ComparisonFixture(escaped=escaped, request_limit=60, rate_limit=50,
                             wall_limit=30) as fixture:
        _, writer = fixture.login("writer")
        _, reader = fixture.login("reader-admin")
        form = urllib.parse.urlencode({"comment": candidate}).encode()
        request = urllib.request.Request(
            fixture.origin + "/comments", data=form,
            headers={"Cookie": f"writer_session={writer}"}, method="POST")
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=3) as response:
            assert response.status == 200
        stored = fixture.stored_comments()
        assert stored == [candidate]
        observations = observe_reader_admin(fixture.origin, case_id, reader, [cid],
                                            browser_path=browser_path, observe_ms=250)
        result = evaluate_correlation(case_id, "completed", stored, observations,
                                      escaped=escaped)
        assert result["outcome"] == expected
        assert result["matched_cids"] == ([] if escaped else [cid])


def test_standard_dxadyn_reflection_canary_cannot_be_upgraded_to_execution():
    # dxadyn's ordinary canary carries an opaque CID plus probe text; it does not
    # bind that CID to a browser-readable JS proof assignment.
    cid = "dxa" + "01234567"
    scanner_payload = cid + '"<dXsS>'
    no_proof = proof(status="completed-no-execution", execution_observed=False)
    result = evaluate_correlation(CASE, "completed", [scanner_payload], [no_proof], escaped=False)
    assert result["outcome"] == "inconclusive"


@pytest.mark.parametrize("origin", [
    "https://127.0.0.1:8080", "http://example.test", "http://127.0.0.1:8080/path",
    "http://user:pass@127.0.0.1:8080",
])
def test_browser_observer_rejects_non_loopback_or_non_origin_urls(origin):
    from r4_cid_oracle import _loopback_origin
    with pytest.raises(ValueError, match="loopback"):
        _loopback_origin(origin)


def test_exact_candidate_matching_rejects_unsubmitted_report_payload():
    from r4_cid_oracle import match_reported_payloads
    assert match_reported_payloads("dalfox", [{"payload": "<img onerror=alert(1)>"}],
                                   ["different stored text"]) == []


def test_exact_candidate_matching_keeps_only_unique_submitted_bytes():
    from r4_cid_oracle import match_reported_payloads
    stored = ["dxa12345678\"<dXsS>", "'><IMG src=x onerror=alert(1) ClAss=dlx1234>"]
    assert match_reported_payloads("dxadyn", [{"canary_id": "dxa12345678"}], stored) == stored[:1]
    assert match_reported_payloads("dalfox", [{"payload": stored[1]}], stored) == stored[1:]
    assert match_reported_payloads("dxadyn", [{"canary_id": "dxa"}], stored) == []


def test_exact_replay_observes_scanner_shape_with_escaped_negative_control():
    from r4_cid_oracle import observe_exact_payload_replay
    scanner_shape = "'><IMG src=x onerror=alert(1) ClAss=dlx1234>"
    result = observe_exact_payload_replay(scanner_shape, browser_path=__import__("os").environ.get("DXA_BROWSER"))
    assert result["raw_dialog_observed"] is True
    assert result["escaped_dialog_observed"] is False
    assert result["outcome"] == "exact-payload-replay-execution"
    assert scanner_shape not in str(result)


def test_exact_replay_benign_marker_stays_inconclusive():
    from r4_cid_oracle import observe_exact_payload_replay
    result = observe_exact_payload_replay('dxa12345678"<dXsS>',
                                          browser_path=__import__("os").environ.get("DXA_BROWSER"))
    assert result["outcome"] == "inconclusive"
    assert result["raw_dialog_observed"] is False


def test_exact_replay_blocks_external_http_and_websocket(monkeypatch):
    from r4_cid_oracle import observe_exact_payload_replay
    payload = '<img src="http://203.0.113.1/pixel" onerror=alert(1)>'
    result = observe_exact_payload_replay(payload,
                                          browser_path=__import__("os").environ.get("DXA_BROWSER"))
    assert result["raw"]["external_http_blocked"] >= 1
    assert result["raw_dialog_observed"] is True
    assert result["escaped_dialog_observed"] is False
