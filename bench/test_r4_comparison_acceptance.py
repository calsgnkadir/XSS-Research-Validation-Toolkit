"""Counterexamples to candidate accounting and artifact/proof promotion."""
import copy
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r4_comparison_acceptance import validate_comparison

HISTORICAL = Path(__file__).resolve().parents[1] / "audit/2026-10-15-r4-admin-comparison/candidate-comparison/comparison.json"
AUTH_RUN = Path(__file__).resolve().parents[1] / "audit/r4-local-acceptance-resume/imported-run-02"


@pytest.fixture
def manifest():
    return json.loads(HISTORICAL.read_text(encoding="utf-8"))


@pytest.fixture
def authenticated_run():
    return json.loads((AUTH_RUN / "comparison.json").read_text(encoding="utf-8"))


def test_authenticated_v3_run_passes_independent_artifact_gate(authenticated_run):
    result = validate_comparison(authenticated_run, AUTH_RUN)
    assert result == {"selected": 8, "completed": 8, "error": 0, "timeout": 0,
                      "incomplete": 0, "skipped": 0, "candidate_only": True,
                      "ranking": False, "artifacts_verified": True,
                      "equal_client_timeouts": True,
                      "authenticated_sessions_verified": True,
                      "request_traces_verified": True}


def test_authenticated_run_without_request_trace_is_rejected(authenticated_run):
    authenticated_run["results"][0].pop("request_trace")
    with pytest.raises(ValueError, match="request trace missing"):
        validate_comparison(authenticated_run, AUTH_RUN)


@pytest.mark.parametrize("mutation", [
    lambda row: row["session_checks"]["writer"].update(pre=False),
    lambda row: row["session_checks"]["reader_admin"].update(post=False),
    lambda row: row["session_checks"].update(independent_tokens=False),
    lambda row: row["session_checks"].update(cookie_values_recorded=True),
    lambda row: row["role_boundary_checks"]["writer_cannot_read_admin"].update(passed=False),
    lambda row: row["role_boundary_checks"]["reader_admin_cannot_submit"].update(status=200),
    lambda row: row["role_boundary_checks"]["admin_token_rejected_as_writer"].update(expected_status=401),
    lambda row: row["role_boundary_checks"]["writer_token_rejected_as_admin"].update(passed=False),
])
def test_authenticated_role_evidence_mutations_are_rejected(authenticated_run, mutation):
    mutation(authenticated_run["results"][0])
    with pytest.raises(ValueError):
        validate_comparison(authenticated_run, AUTH_RUN)


@pytest.mark.parametrize("mutation", [
    lambda row: row.pop("request_trace"),
    lambda row: row["request_trace"][0].update(path="/outside"),
    lambda row: row["request_trace"][0].update(status=403),
    lambda row: row["request_trace"][0].update(cookie="secret"),
    lambda row: row["request_trace"].pop(),
    lambda row: row["fixture_request_counts"].update(scanner_requests=999),
    lambda row: row["scanner_requests_by_path"].update({"/comments": 999}),
])
def test_authenticated_request_trace_and_budget_mutations_are_rejected(authenticated_run, mutation):
    mutation(authenticated_run["results"][0])
    with pytest.raises(ValueError):
        validate_comparison(authenticated_run, AUTH_RUN)


@pytest.mark.parametrize("mutation", [
    lambda d: d["results"].pop(),
    lambda d: d["summary"].update(selected=7),
    lambda d: d["summary"].update(completed=7),
    lambda d: d["results"][0].update(status="timeout", timeout=True, completed=False),
    lambda d: d["results"][0].update(status="skipped", timeout=False, completed=False,
                                     candidate_count=None, candidate_observed=None),
    lambda d: d["results"][0].update(tp=1),
])
def test_authenticated_coverage_or_candidate_score_mutations_are_rejected(authenticated_run, mutation):
    mutation(authenticated_run)
    with pytest.raises(ValueError):
        validate_comparison(authenticated_run, AUTH_RUN)


def test_authenticated_manifest_rejects_raw_cookie_pattern(authenticated_run):
    authenticated_run["results"][0]["stored_payloads"].append("admin_session=not-a-real-secret")
    with pytest.raises(ValueError, match="unredacted credential"):
        validate_comparison(authenticated_run, AUTH_RUN)


def test_authenticated_artifact_rejects_raw_cookie_pattern_after_rehash(authenticated_run, tmp_path):
    import shutil
    import hashlib

    copied = tmp_path / "run"
    shutil.copytree(AUTH_RUN, copied)
    row = authenticated_run["results"][0]
    entry = row["artifacts"]["stdout"]
    target = copied / entry["path"]
    target.write_text("admin_session=synthetic-secret", encoding="utf-8")
    entry["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="unredacted credential"):
        validate_comparison(authenticated_run, copied)


def test_authenticated_report_hash_is_verified(authenticated_run):
    authenticated_run["results"][0]["artifacts"]["stdout"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="artifact hash mismatch"):
        validate_comparison(authenticated_run, AUTH_RUN)


def test_authenticated_document_metadata_rejects_raw_cookie(authenticated_run):
    authenticated_run["runtime"]["note"] = "admin_session=synthetic-secret"
    with pytest.raises(ValueError, match="unredacted credential"):
        validate_comparison(authenticated_run, AUTH_RUN)


def test_authenticated_missing_cookie_argument_fails_cleanly(authenticated_run):
    command = authenticated_run["results"][0]["safe_command"]
    option = "--cookie" if authenticated_run["results"][0]["tool"] == "dxadyn" else "--cookies"
    index = command.index(option)
    del command[index:index + 2]
    command.append(option)
    with pytest.raises(ValueError, match="redacted independent session pair"):
        validate_comparison(authenticated_run, AUTH_RUN)


@pytest.mark.parametrize("level", ["common", "row"])
def test_authenticated_client_timeout_drift_is_rejected(authenticated_run, level):
    if level == "common":
        authenticated_run["budgets"]["dalfox_per_request_seconds"] = 16
    else:
        authenticated_run["results"][0]["per_request_timeout_seconds"] = 16
    with pytest.raises(ValueError, match="client timeout mismatch"):
        validate_comparison(authenticated_run, AUTH_RUN)


@pytest.mark.parametrize("value", ["<synthetic-secret>", "<writer-session>suffix"])
def test_authenticated_unknown_angle_cookie_is_rejected(authenticated_run, value):
    authenticated_run["runtime"]["note"] = "admin_session=" + value
    with pytest.raises(ValueError, match="unredacted credential"):
        validate_comparison(authenticated_run, AUTH_RUN)


def test_authenticated_known_redacted_cookie_marker_is_allowed(authenticated_run):
    authenticated_run["runtime"]["note"] = "admin_session=<reader-admin-session>"
    assert validate_comparison(authenticated_run, AUTH_RUN)["candidate_only"]


def test_authenticated_dalfox_canonical_findings_cannot_be_replaced(authenticated_run, tmp_path):
    import shutil

    copied = tmp_path / "run"
    shutil.copytree(AUTH_RUN, copied)
    row = next(row for row in authenticated_run["results"] if row["tool"] == "dalfox")
    entry = row["artifacts"]["report"]
    target = copied / entry["path"]
    report = json.loads(target.read_text(encoding="utf-8"))
    report["data"] = report.pop("findings")
    target.write_text(json.dumps(report), encoding="utf-8")
    entry["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="artifact candidate count mismatch"):
        validate_comparison(authenticated_run, copied)


def test_historical_incomplete_run_is_not_accuracy(manifest):
    result = validate_comparison(manifest)
    assert result == {"selected": 8, "completed": 4, "error": 0, "timeout": 4,
                      "incomplete": 0, "skipped": 0, "candidate_only": True,
                      "ranking": False, "artifacts_verified": False,
                      "equal_client_timeouts": False,
                      "authenticated_sessions_verified": False,
                      "request_traces_verified": False}


@pytest.mark.parametrize("key,value", [
    ("status", "completed"), ("completed", True), ("timeout", False),
    ("timed_out", False), ("candidate_observed", False),
    ("request_limit", 21), ("rate_limit_rps", 3), ("wall_limit_seconds", 21),
    ("command_timeout_seconds", 21), ("forwarded_requests", 21),
    ("request_attempts", 0), ("budget_rejected_requests", 0),
    ("budget_exceeded", False), ("max_inflight", 2),
    ("http_statuses", []), ("wall_seconds", float("nan")),
    ("expected_execution", False), ("order_index", 0), ("selected", True),
    ("tool", "other"), ("repetition", True), ("return_code", True),
    ("candidate_count", -1), ("safe_command", []),
    ("identity", {"role": "reader"}),
])
def test_timeout_row_cannot_be_relabelled_or_change_scope(manifest, key, value):
    manifest["results"][1][key] = value
    with pytest.raises(ValueError):
        validate_comparison(manifest)


@pytest.mark.parametrize("change", [
    lambda d: d["results"].pop(),
    lambda d: d["results"].append(copy.deepcopy(d["results"][0])),
    lambda d: d["summary"].update(completed=8, timeout=0),
    lambda d: d["summary"].update(selected=7),
    lambda d: d["summary"].update(tp=4, tn=4),
    lambda d: d["identity"].update(parameter="other"),
    lambda d: d["cases"][0].update(expected_execution=False),
    lambda d: d["cases"].append(copy.deepcopy(d["cases"][0])),
    lambda d: d["auth"].update(real_login_coverage=True),
    lambda d: d["interpretation"].update(ranking=True),
    lambda d: d["interpretation"].update(candidate_only=False),
    lambda d: d["runtime"].update(adapter_sha256="bad"),
    lambda d: d["runtime"].pop("python"),
    lambda d: d["order"].update({"rep-2": ["dxadyn", "dalfox"]}),
    lambda d: d["results"][0].update(execution_observed=True),
])
def test_manifest_counterexamples(manifest, change):
    change(manifest)
    with pytest.raises(ValueError):
        validate_comparison(manifest)


def test_dalfox_error_exit_with_candidates_is_error_not_completed(manifest):
    row = manifest["results"][1]
    row.update(timed_out=False, return_code=2, status="error", timeout=False, error=True,
               candidate_count=1, candidate_observed=True)
    manifest["summary"].update(error=1, timeout=3)
    assert validate_comparison(manifest)["error"] == 1
    row.update(status="completed", error=False, completed=True)
    manifest["summary"].update(error=0, completed=5)
    with pytest.raises(ValueError, match="classification"):
        validate_comparison(manifest)


def test_dalfox_pinned_finding_exit_is_completed(manifest):
    row = manifest["results"][1]
    row.update(timed_out=False, return_code=1, status="completed", completed=True,
               timeout=False, budget_exceeded=False, wall_seconds=1,
               budget_rejected_requests=0, forwarded_requests=0, request_attempts=0,
               http_statuses=[], candidate_count=1, candidate_observed=True)
    manifest["summary"].update(completed=5, timeout=3)
    assert validate_comparison(manifest)["completed"] == 5


@pytest.mark.parametrize("index,flag,replacement", [
    (0, "--target", "http://127.0.0.1:<ephemeral-port>/other"),
    (0, "--target-field", "other"),
    (0, "--check", "http://127.0.0.1:<ephemeral-port>/public"),
    (1, "-X", "GET"), (1, "-p", "other:body"),
    (1, "--sxss-method", "POST"),
])
def test_command_scope_cannot_disagree_with_manifest(manifest, index, flag, replacement):
    command = manifest["results"][index]["safe_command"]
    command[command.index(flag) + 1] = replacement
    with pytest.raises(ValueError, match="command identity"):
        validate_comparison(manifest)


def test_skipped_remains_in_selected_denominator(manifest):
    row = manifest["results"][1]
    row.update(status="skipped", timeout=False, timed_out=False, budget_exceeded=False,
               request_attempts=0, forwarded_requests=0, budget_rejected_requests=0,
               http_statuses=[], max_inflight=0, wall_seconds=0, skip_reason="tool unavailable")
    manifest["summary"].update(skipped=1, timeout=3)
    result = validate_comparison(manifest)
    assert result["selected"] == 8 and result["completed"] == 4 and result["skipped"] == 1


def bind_artifacts(manifest, tmp_path):
    manifest["schema"] = "r4-local-comparison/2"
    manifest["budgets"]["dalfox_per_request_seconds"] = 15
    for index, row in enumerate(manifest["results"]):
        row["identity"] = copy.deepcopy(manifest["identity"])
        row["per_request_timeout_seconds"] = 15
        row["artifacts"] = {}
        for name in ("stdout", "stderr", "report"):
            if name == "report" and row["candidate_count"] is None:
                row["artifacts"][name] = None
                continue
            content = b"" if name != "report" else json.dumps(
                {"findings": [{"evidence_level": "reflection"}] * row["candidate_count"]}).encode()
            path = tmp_path / f"{index}-{name}.json"
            path.write_bytes(content)
            row["artifacts"][name] = {"path": path.name, "sha256": hashlib.sha256(content).hexdigest()}


def test_v2_binds_report_bytes_and_count(manifest, tmp_path):
    bind_artifacts(manifest, tmp_path)
    assert validate_comparison(manifest, tmp_path)["artifacts_verified"]
    report = manifest["results"][0]["artifacts"]["report"]
    (tmp_path / report["path"]).write_text('{"findings":[]}', encoding="utf-8")
    with pytest.raises(ValueError, match="hash mismatch"):
        validate_comparison(manifest, tmp_path)
    report["sha256"] = hashlib.sha256((tmp_path / report["path"]).read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="candidate count mismatch"):
        validate_comparison(manifest, tmp_path)


@pytest.mark.parametrize("path", ["../outside", "C:/secret", "/absolute", "..\\outside"])
def test_artifact_path_cannot_escape(manifest, tmp_path, path):
    bind_artifacts(manifest, tmp_path)
    manifest["results"][0]["artifacts"]["stdout"]["path"] = path
    with pytest.raises(ValueError, match="path"):
        validate_comparison(manifest, tmp_path)


def test_v2_requires_artifacts_and_per_row_identity(manifest, tmp_path):
    bind_artifacts(manifest, tmp_path)
    with pytest.raises(ValueError, match="requires artifact"):
        validate_comparison(manifest)
    manifest["results"][0].pop("identity")
    with pytest.raises(ValueError, match="identity"):
        validate_comparison(manifest, tmp_path)


def test_v2_rejects_different_client_timeouts(manifest, tmp_path):
    bind_artifacts(manifest, tmp_path)
    manifest["budgets"]["dalfox_per_request_seconds"] = 2
    with pytest.raises(ValueError, match="client timeout"):
        validate_comparison(manifest, tmp_path)


def test_v2_rejects_row_timeout_drift(manifest, tmp_path):
    bind_artifacts(manifest, tmp_path)
    manifest["results"][0]["per_request_timeout_seconds"] = 2
    with pytest.raises(ValueError, match="client timeout"):
        validate_comparison(manifest, tmp_path)


@pytest.mark.parametrize("field", ["cases", "interpretation", "auth", "budgets", "runtime", "results", "summary"])
def test_malformed_nested_objects_fail_closed(manifest, field):
    manifest[field] = None
    with pytest.raises(ValueError):
        validate_comparison(manifest)


@pytest.mark.parametrize("tool,extra", [
    ("dalfox", {"meta": {"incomplete": True, "failed_requests": 0}}),
    ("dalfox", {"meta": {"incomplete": False, "failed_requests": 1}}),
    ("dxadyn", {"events": [{"kind": "error"}]}),
    ("dxadyn", {"events": [{"kind": "skip"}]}),
    ("dxadyn", {"skipped_submits": 1}),
])
def test_report_failures_cannot_be_completed_negatives(manifest, tmp_path, tool, extra):
    # Replace a genuine timeout by an apparently clean exit/empty report.
    row = manifest["results"][1 if tool == "dalfox" else 0]
    previous = row["status"]
    row.update(status="completed", completed=True, error=False, timeout=False,
               timed_out=False, budget_exceeded=False, request_attempts=0,
               forwarded_requests=0, budget_rejected_requests=0, http_statuses=[],
               wall_seconds=1, return_code=0, candidate_count=0, candidate_observed=False)
    manifest["summary"][previous] -= 1
    manifest["summary"]["completed"] += 1
    bind_artifacts(manifest, tmp_path)
    binding = row["artifacts"]["report"]
    content = json.dumps({"findings": [], **extra}).encode()
    (tmp_path / binding["path"]).write_bytes(content)
    binding["sha256"] = hashlib.sha256(content).hexdigest()
    with pytest.raises(ValueError, match="candidate count mismatch"):
        validate_comparison(manifest, tmp_path)
    row.update(status="incomplete", completed=False, candidate_count=None, candidate_observed=None)
    manifest["summary"]["completed"] -= 1
    manifest["summary"]["incomplete"] += 1
    assert validate_comparison(manifest, tmp_path)["incomplete"] == 1


@pytest.mark.parametrize("report", [[], {"data": [], "meta": {
    "incomplete": False, "failed_requests": 0, "findings_count": 0}}])
def test_v2_dalfox_requires_pinned_structured_report(manifest, tmp_path, report):
    row = manifest["results"][1]
    row.update(status="completed", completed=True, timeout=False, timed_out=False,
               budget_exceeded=False, request_attempts=0, forwarded_requests=0,
               budget_rejected_requests=0, http_statuses=[], wall_seconds=1,
               return_code=0, candidate_count=0, candidate_observed=False)
    manifest["summary"].update(completed=5, timeout=3)
    bind_artifacts(manifest, tmp_path)
    binding = row["artifacts"]["report"]
    content = json.dumps(report).encode()
    (tmp_path / binding["path"]).write_bytes(content)
    binding["sha256"] = hashlib.sha256(content).hexdigest()
    with pytest.raises(ValueError, match="candidate count mismatch"):
        validate_comparison(manifest, tmp_path)
