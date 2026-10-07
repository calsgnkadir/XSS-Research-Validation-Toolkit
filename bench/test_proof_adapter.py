"""Independent proof-adapter oracles; no browser required for malformed evidence."""
import json
import pathlib
import subprocess
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
    monkeypatch.setattr(runner, "run_dxaprove", lambda target: runner.adapt_proof(
        target, p, "http://127.0.0.1:1234", {"resource_callback_hits": {"attempt-123": 1}}))
    report = runner.run_all(runner.proof_corpus(), ["dxaprove"], None)
    assert report["totals"]["dxaprove"]["fn"] == 3
    assert report["totals"]["dxaprove"]["completed"] == 9
    assert runner.strict_failed(report)


def test_mixed_measurements_are_rejected():
    with pytest.raises(ValueError, match="mix"):
        runner.run_all(runner.proof_corpus(), ["dxaprove", "dxadyn"], None)


@pytest.mark.parametrize("status", ["invalid", "inconclusive", "error", "timeout", "skipped"])
def test_incomplete_proof_rows_fail_gate_and_are_not_scored(monkeypatch, status):
    monkeypatch.setattr(runner, "run_dxaprove", lambda target: {
        "status": status, "findings": [], "ok": False})
    report = runner.run_all(runner.proof_corpus(), ["dxaprove"], None)
    assert report["totals"]["dxaprove"][status] == 9
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


@pytest.mark.parametrize("field,value", [
    ("events", None), ("events", [None]), ("events", "not-events"),
    ("proofs", None), ("proofs", [None]), ("proofs", {}),
    ("source", None), ("canary_id", ""), ("http_session_checked", False),
    ("browser_session_checked", False), ("read_status", 500),
    ("submit_status", 403), ("observe_ms", 0),
    ("events", [{"kind": "skip"}]), ("events", [{"kind": "error"}]),
    ("events", [{"stage": "observe", "kind": "info", "reason": "no-canary-within-window"}]),
])
def test_malformed_or_contradictory_proof_is_invalid(field, value):
    p = proof()
    p[field] = value
    result = runner.adapt_proof(runner.proof_corpus()["targets"][0], p, "http://127.0.0.1:1234")
    assert result["status"] == "invalid"
    assert result["findings"] == []


@pytest.mark.parametrize("malformed", [None, [], "proof", 1])
def test_non_object_proof_is_invalid(malformed):
    result = runner.adapt_proof(runner.proof_corpus()["targets"][0], malformed, "http://127.0.0.1:1234")
    assert result["status"] == "invalid"


@pytest.mark.parametrize("hits", [{}, {"wrong-cid": 1}, {"attempt-123": 0}])
def test_callback_negative_requires_actual_matching_request(hits):
    target = next(t for t in runner.proof_corpus()["targets"] if t["id"] == "proof-resource-callback")
    p = proof()
    p.update(status="inconclusive", execution_observed=False, proofs=[],
             events=[{"stage": "observe", "reason": "no-canary-within-window", "kind": "info"}])
    result = runner.adapt_proof(target, p, "http://127.0.0.1:1234", {"resource_callback_hits": hits})
    assert result["status"] != "completed"
    assert not runner.score_findings([], result["findings"], status=result["status"])["evaluated"]


FAILURE_SECRET = "SENTINEL_PRIVATE_EXCEPTION_BODY_9274"
FAILURE_CASES = [
    pytest.param(RuntimeError(FAILURE_SECRET), "error", id="runtime-error"),
    pytest.param(OSError(FAILURE_SECRET), "error", id="os-error"),
    pytest.param(TimeoutError(FAILURE_SECRET), "timeout", id="timeout-error"),
    pytest.param(subprocess.TimeoutExpired([FAILURE_SECRET], 1,
                 output=FAILURE_SECRET, stderr=FAILURE_SECRET), "timeout", id="subprocess-timeout"),
]


def install_case_failure(monkeypatch, failure):
    """Inject a boundary failure, preserving the real adapter and scoring path."""
    visited = []

    def observe(target):
        visited.append(target["id"])
        if target["id"] == "proof-raw":
            raise failure
        p = proof()
        p.update(status="inconclusive", execution_observed=False, proofs=[],
                 events=[{"stage": "observe", "reason": "no-canary-within-window", "kind": "info"}])
        return runner.adapt_proof(target, p, "http://127.0.0.1:1234")

    monkeypatch.setattr(runner, "run_dxaprove", observe)
    return visited


def assert_failed_case_report(report, status):
    totals = report["totals"]["dxaprove"]
    assert totals["selected"] == 2
    assert totals["completed"] == 1
    assert totals[status] == 1
    assert totals["error" if status == "timeout" else "timeout"] == 0
    assert all(totals[key] == 0 for key in ("tp", "fp", "fn", "skipped", "invalid", "inconclusive"))
    failed, completed = [row["results"]["dxaprove"] for row in report["rows"]]
    assert failed["observed"]["status"] == status
    assert failed["observed"]["ok"] is False
    assert failed["observed"]["findings"] == []
    assert failed["score"] == {"tp": 0, "fp": 0, "fn": 0, "evaluated": False}
    assert completed["observed"]["status"] == "completed"
    assert completed["score"]["evaluated"] is True
    assert runner.strict_failed(report)
    assert FAILURE_SECRET not in json.dumps(report)


@pytest.mark.parametrize("failure,status", FAILURE_CASES)
def test_proof_case_exception_preserves_remaining_cases(monkeypatch, failure, status):
    visited = install_case_failure(monkeypatch, failure)
    report = runner.run_all(runner.proof_corpus(), ["dxaprove"], ["proof-raw", "proof-fixed"])
    assert visited == ["proof-raw", "proof-fixed"]
    assert_failed_case_report(report, status)


@pytest.mark.parametrize("failure,status", FAILURE_CASES)
def test_proof_case_exception_cli_writes_artifacts_and_fails_strict(
        monkeypatch, tmp_path, capsys, failure, status):
    visited = install_case_failure(monkeypatch, failure)
    output = tmp_path / "proof-failure.md"
    monkeypatch.setenv("BENCH_STRICT", "1")
    monkeypatch.setattr(sys, "argv", ["bench/run.py", "--proof-suite", "--targets",
                        "proof-raw,proof-fixed", "--no-history", "--out", str(output)])
    assert runner.main() == 1
    assert visited == ["proof-raw", "proof-fixed"]
    json_text = output.with_suffix(".json").read_text(encoding="utf-8")
    markdown = output.read_text(encoding="utf-8")
    assert_failed_case_report(json.loads(json_text), status)
    assert f"{status} (not evaluated)" in markdown
    captured = capsys.readouterr()
    assert FAILURE_SECRET not in json_text + markdown + captured.out + captured.err


@pytest.mark.parametrize("failure", [KeyboardInterrupt(), SystemExit(2)],
                         ids=["keyboard-interrupt", "system-exit"])
def test_proof_case_process_control_exception_propagates(monkeypatch, failure):
    visited = install_case_failure(monkeypatch, failure)
    with pytest.raises(type(failure)):
        runner.run_all(runner.proof_corpus(), ["dxaprove"], ["proof-raw", "proof-fixed"])
    assert visited == ["proof-raw"]
