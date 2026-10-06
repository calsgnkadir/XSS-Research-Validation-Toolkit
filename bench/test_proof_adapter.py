"""Independent proof-adapter oracles; no browser required for malformed evidence."""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run as runner


def proof():
    return {"schema": "dxa-browser-proof/1", "status": "execution-observed",
            "execution_observed": True, "http_session_checked": True,
            "browser_session_checked": True, "session_role": "reader",
            "source": {"url": "http://127.0.0.1:1234/comments", "parameter": "comment", "method": "POST"},
            "read_url": "http://127.0.0.1:1234/comments", "canary_id": "attempt-123",
            "read_status": 200, "submit_status": 201, "observe_ms": 400,
            "proofs": [{"canary_id": "attempt-123", "frame_url": "http://127.0.0.1:1234/comments",
                        "event": "matching-browser-canary"}], "events": []}


@pytest.mark.parametrize("mutation", ["cid", "frame", "scope", "role", "source"])
def test_wrong_evidence_cannot_be_credited(mutation):
    p = proof()
    if mutation == "cid":
        p["proofs"][0]["canary_id"] = "wrong"
    elif mutation == "frame":
        p["proofs"][0]["frame_url"] += "/wrong"
    elif mutation == "scope":
        p["proofs"][0]["frame_url"] = "http://127.0.0.1:9999/comments"
    elif mutation == "role":
        p["session_role"] = "admin"
    else:
        p["source"]["parameter"] = "wrong"
    result = runner.adapt_proof(runner.proof_corpus()["targets"][0], p, "http://127.0.0.1:1234")
    assert result["status"] == "invalid"
    assert result["findings"] == []


def test_error_cannot_be_a_completed_negative():
    result = runner.adapt_proof(runner.proof_corpus()["targets"][1], {"status": "error"}, "http://127.0.0.1:1234")
    assert result["status"] == "error"
    assert not runner.score_findings([], result["findings"], status=result["status"])["evaluated"]


def test_real_runner_invokes_identity_scorer(monkeypatch):
    calls = []
    original = runner.score_findings
    def score(*args, **kwargs):
        calls.append(args)
        return original(*args, **kwargs)
    monkeypatch.setattr(runner, "score_findings", score)
    monkeypatch.setattr(runner, "run_dxaprove", lambda target: runner.adapt_proof(target, proof(), "http://127.0.0.1:1234"))
    report = runner.run_all(runner.proof_corpus(), ["dxaprove"], ["proof-raw"])
    assert len(calls) == 1
    assert report["totals"]["dxaprove"]["tp"] == 1
    assert "execution" in report["measurement"]


def test_completed_window_status_does_not_depend_on_expected_label(monkeypatch):
    p = proof()
    p.update(status="inconclusive", execution_observed=False, proofs=[],
             events=[{"stage": "observe", "reason": "no-canary-within-window", "kind": "info"}])
    negative = runner.adapt_proof(runner.proof_corpus()["targets"][1], p, "http://127.0.0.1:1234")
    positive = runner.adapt_proof(runner.proof_corpus()["targets"][0], p, "http://127.0.0.1:1234")
    assert negative["status"] == "completed"
    assert positive["status"] == "completed"
    monkeypatch.setattr(runner, "run_dxaprove", lambda target: runner.adapt_proof(target, p, "http://127.0.0.1:1234"))
    report = runner.run_all(runner.proof_corpus(), ["dxaprove"], None)
    assert report["totals"]["dxaprove"]["fn"] == 1
    assert report["totals"]["dxaprove"]["completed"] == 4
    assert runner.strict_failed(report)


def test_mixed_measurements_are_rejected():
    with pytest.raises(ValueError, match="mix"):
        runner.run_all(runner.proof_corpus(), ["dxaprove", "dxadyn"], None)


@pytest.mark.parametrize("status", ["invalid", "inconclusive", "error"])
def test_incomplete_proof_rows_fail_gate_and_are_not_scored(monkeypatch, status):
    monkeypatch.setattr(runner, "run_dxaprove", lambda target: {
        "status": status, "findings": [], "ok": False})
    report = runner.run_all(runner.proof_corpus(), ["dxaprove"], None)
    assert report["totals"]["dxaprove"][status] == 4
    assert report["totals"]["dxaprove"]["completed"] == 0
    assert all(not row["results"]["dxaprove"]["score"]["evaluated"] for row in report["rows"])
    assert runner.strict_failed(report)


def test_execution_on_negative_fixture_is_false_positive(monkeypatch):
    monkeypatch.setattr(runner, "run_dxaprove", lambda target: runner.adapt_proof(target, proof(), "http://127.0.0.1:1234"))
    report = runner.run_all(runner.proof_corpus(), ["dxaprove"], ["proof-fixed"])
    assert report["totals"]["dxaprove"]["fp"] == 1
    assert runner.strict_failed(report)


def test_missing_observation_window_is_invalid():
    p = proof()
    p.update(status="inconclusive", execution_observed=False, proofs=[])
    result = runner.adapt_proof(runner.proof_corpus()["targets"][1], p, "http://127.0.0.1:1234")
    assert result["status"] == "invalid"
