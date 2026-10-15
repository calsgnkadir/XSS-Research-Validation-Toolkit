"""Independent source/sink/role/frame identity oracles for R4 proof scoring."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run as runner


BASE = "http://127.0.0.1:1234"
CID = "dxa0123456789abcdef0123456789abcdef"

# These expectations are intentionally authored here rather than copied from
# runner.proof_corpus() or a scanner result.
IDENTITIES = {
    "proof-raw": ("raw", "/comments", "comment", "/comments", "reader", True, ("/comments",)),
    "proof-fixed": ("fixed", "/comments", "comment", "/comments", "reader", False, ("/comments",)),
    "proof-json": ("json", "/comments", "comment", "/comments", "reader", False, ("/comments",)),
    "proof-dialog": ("dialog", "/comments", "comment", "/comments", "reader", False, ("/comments",)),
    "proof-delayed": ("delayed", "/comments", "comment", "/comments", "reader", True, ("/comments",)),
    "proof-eval": ("eval", "/comments", "comment", "/comments", "reader", True, ("/comments",)),
    "proof-title": ("title", "/comments", "comment", "/comments", "reader", False, ("/comments",)),
    "proof-textarea": ("textarea", "/comments", "comment", "/comments", "reader", False, ("/comments",)),
    "proof-resource-callback": ("resource-callback", "/comments", "comment", "/comments", "reader", False, ("/comments",)),
    "proof-sanitized-then-raw": ("sanitized-then-raw", "/comments", "comment", "/comments", "reader", True, ("/comments",)),
    "proof-identity-sanitizer": ("identity-sanitizer", "/comments", "comment", "/comments", "reader", True, ("/comments",)),
    "proof-editor-raw": ("editor-raw", "/notes", "text", "/review", "editor", True, ("/review",)),
    "proof-editor-fixed": ("editor-fixed", "/notes", "text", "/review", "editor", False, ("/review",)),
    "proof-iframe": ("iframe", "/comments", "comment", "/comments", "reader", True, ("/frame",)),
    "proof-comment": ("comment", "/comments", "comment", "/comments", "reader", False, ("/comments",)),
    "proof-template": ("template", "/comments", "comment", "/comments", "reader", False, ("/comments",)),
    "proof-template-activated": ("template-activated", "/comments", "comment", "/comments", "reader", True, ("/comments",)),
}


def corpus_targets():
    corpus = runner.proof_corpus()
    return {target["id"]: target for target in corpus["targets"]}


def make_execution_proof(case_id, *, frame_path=None):
    _, source_path, parameter, read_path, role, _, allowed_frames = IDENTITIES[case_id]
    frame_path = frame_path if frame_path is not None else allowed_frames[0]
    return {
        "schema": "dxa-browser-proof/1",
        "status": "execution-observed",
        "execution_observed": True,
        "http_session_checked": True,
        "browser_session_checked": True,
        "session_role": role,
        "source": {"url": BASE + source_path, "parameter": parameter, "method": "POST"},
        "read_url": BASE + read_path,
        "canary_id": CID,
        "read_status": 200,
        "submit_status": 201,
        "observe_ms": 400,
        "proofs": [{"canary_id": CID, "frame_url": BASE + frame_path,
                    "event": "matching-browser-canary"}],
        "events": [],
    }


def make_no_execution_proof(case_id):
    proof = make_execution_proof(case_id)
    proof.update(status="inconclusive", execution_observed=False, proofs=[],
                 events=[{"stage": "observe", "kind": "info",
                          "reason": "no-canary-within-window"}])
    return proof


def test_v4_identity_matrix_is_bound_to_independent_case_contract():
    targets = corpus_targets()
    assert set(targets) == set(IDENTITIES)
    assert runner.proof_corpus()["corpus_version"] == "loopback-proof/4"

    for case_id, (mode, source_path, parameter, read_path, role, positive, frame_paths) in IDENTITIES.items():
        target = targets[case_id]
        identity = {"method": "POST", "source_path": source_path,
                    "parameter": parameter, "read_path": read_path, "role": role}
        expected_id = f"proof-v4:{mode}:POST:{source_path}:{parameter}:{read_path}:{role}"
        assert target["case_id"] == expected_id
        assert target["expected_ids"] == ([expected_id] if positive else [])
        assert target["expected_identity"] == identity
        assert target["expected_frame_paths"] == list(frame_paths)


@pytest.mark.parametrize("case_id", [case for case, row in IDENTITIES.items() if row[5]])
def test_valid_positive_proof_matches_its_exact_identity(case_id):
    target = corpus_targets()[case_id]
    observed = runner.adapt_proof(target, make_execution_proof(case_id), BASE)
    assert observed["status"] == "completed"
    assert observed["findings"] == [{
        "finding_id": target["case_id"], "evidence": "execution-observed",
        "canary_matched": True, "triage": "unreviewed",
    }]


@pytest.mark.parametrize(("field", "value"), [
    ("session_role", "reader"),
    ("source_url", BASE + "/comments"),
    ("parameter", "comment"),
    ("read_url", BASE + "/comments"),
])
def test_wrong_role_source_parameter_or_read_cannot_be_credited(field, value):
    target = corpus_targets()["proof-editor-raw"]
    proof = make_execution_proof("proof-editor-raw")
    if field in ("session_role", "read_url"):
        proof[field] = value
    elif field == "source_url":
        proof["source"]["url"] = value
    else:
        proof["source"]["parameter"] = value

    observed = runner.adapt_proof(target, proof, BASE)
    score = runner.score_findings(target["expected_ids"], observed["findings"], status=observed["status"])
    assert observed["status"] == "invalid"
    assert observed["findings"] == []
    assert score == {"tp": 0, "fp": 0, "fn": 0, "evaluated": False}


@pytest.mark.parametrize(("case_id", "wrong_frame"), [
    ("proof-raw", "/frame"),
    ("proof-iframe", "/comments"),
    ("proof-editor-raw", "/frame"),
])
def test_frame_execution_is_credited_only_on_the_independently_allowed_path(case_id, wrong_frame):
    target = corpus_targets()[case_id]
    proof = make_execution_proof(case_id, frame_path=wrong_frame)
    observed = runner.adapt_proof(target, proof, BASE)
    assert observed["status"] == "invalid"
    assert observed["findings"] == []


def test_same_canary_from_different_identity_cannot_be_relabelled():
    targets = corpus_targets()
    editor_evidence = make_execution_proof("proof-editor-raw")
    observed = runner.adapt_proof(targets["proof-raw"], editor_evidence, BASE)
    score = runner.score_findings(targets["proof-raw"]["expected_ids"], observed["findings"],
                                  status=observed["status"])
    assert editor_evidence["canary_id"] == CID
    assert observed["status"] == "invalid"
    assert observed["findings"] == []
    assert score["evaluated"] is False


def test_completed_missing_positive_is_label_independent_fn(monkeypatch):
    targets = corpus_targets()
    case_id = "proof-identity-sanitizer"
    target = targets[case_id]
    monkeypatch.setattr(runner, "run_dxaprove",
                        lambda current: runner.adapt_proof(current, make_no_execution_proof(case_id), BASE))

    report = runner.run_all(runner.proof_corpus(), ["dxaprove"], [case_id])
    row = report["rows"][0]
    assert row["results"]["dxaprove"]["observed"]["status"] == "completed"
    assert row["results"]["dxaprove"]["observed"]["findings"] == []
    assert row["results"]["dxaprove"]["score"] == {
        "tp": 0, "fp": 0, "fn": 1, "evaluated": True,
    }
    assert report["totals"]["dxaprove"]["fn"] == 1
    assert target["expected_ids"]


def test_incomplete_positive_is_not_scored_or_counted_as_fn(monkeypatch):
    case_id = "proof-editor-raw"
    monkeypatch.setattr(runner, "run_dxaprove", lambda target: {
        "status": "error", "ok": False, "findings": [], "reason": "test-error"})

    report = runner.run_all(runner.proof_corpus(), ["dxaprove"], [case_id])
    row = report["rows"][0]["results"]["dxaprove"]
    totals = report["totals"]["dxaprove"]
    assert row["observed"]["status"] == "error"
    assert row["score"] == {"tp": 0, "fp": 0, "fn": 0, "evaluated": False}
    assert totals["selected"] == 1 and totals["completed"] == 0 and totals["error"] == 1
    assert (totals["tp"], totals["fp"], totals["fn"]) == (0, 0, 0)
    assert runner.strict_failed(report)


def test_markdown_reports_proof_coverage_incomplete_denominator_and_frame_allowlist(monkeypatch):
    case_id = "proof-iframe"
    monkeypatch.setattr(runner, "run_dxaprove", lambda target: runner.adapt_proof(
        target, make_execution_proof(case_id), BASE))
    report = runner.run_all(runner.proof_corpus(), ["dxaprove"], [case_id])
    markdown = runner.render_md(report)
    assert "dxaprove completed/selected coverage ratio: 1/1" in markdown
    assert "accuracy denominator: completed rows only; incomplete rows are excluded and fail strict acceptance" in markdown
    assert 'expected proof frame paths: ["/frame"]' in markdown


def test_zero_selected_proof_rows_render_coverage_as_not_applicable():
    report = runner.run_all({"corpus_version": "loopback-proof/4", "targets": []}, ["dxaprove"], None)
    markdown = runner.render_md(report)
    assert report["totals"]["dxaprove"]["selected"] == 0
    assert "dxaprove completed/selected coverage ratio: n/a" in markdown
    assert "not a safe or true-negative result" in markdown

@pytest.mark.parametrize("identity", (None, {}, [], "reader"))
def test_explicit_malformed_identity_does_not_use_demo_defaults(identity):
    target = dict(corpus_targets()["proof-raw"], expected_identity=identity)
    observed = runner.adapt_proof(target, make_execution_proof("proof-raw"), BASE)
    assert observed["status"] == "invalid"
    assert observed["findings"] == []
