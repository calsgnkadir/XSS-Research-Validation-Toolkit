"""Independent adverse artifacts for the R4/R9 CI gate; no browser required."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest
import run as runner


GATE = Path(__file__).with_name("check_ci_acceptance.py")
LABELS = {
    "raw": True, "fixed": False, "json": False, "dialog": False,
    "delayed": True, "eval": True, "title": False, "textarea": False,
    "resource-callback": False,
}
MODULES = ("test_browser_proof", "test_proof_cleanup", "test_proof_adapter", "test_proof_corpus")
CID = "dxa0123456789abcdef0123456789abcdef"
URL = "http://127.0.0.1:49152/comments"


def proof(positive):
    return {
        "schema": "dxa-browser-proof/1", "status": "execution-observed" if positive else "inconclusive",
        "execution_observed": positive, "http_session_checked": True,
        "browser_session_checked": True, "session_role": "reader", "triage": "unreviewed",
        "source": {"url": URL, "parameter": "comment", "method": "POST"},
        "read_url": URL, "read_status": 200, "submit_status": 201, "observe_ms": 400,
        "canary_id": CID,
        "proofs": [{"canary_id": CID, "frame_url": URL, "event": "matching-browser-canary"}] if positive else [],
        "events": [] if positive else [{"stage": "observe", "kind": "info", "reason": "no-canary-within-window"}],
    }


def source_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def corpus():
    rows = []
    for mode, positive in LABELS.items():
        identity = f"proof-v2:{mode}:POST:/comments:comment:/comments:reader"
        observation = {
            "status": "completed", "ok": True, "proof": proof(positive), "wall": 0.1,
            "findings": [{"finding_id": identity, "evidence": "execution-observed", "canary_matched": True, "triage": "unreviewed"}] if positive else [],
            "fixture_observation": {"resource_callback_hits": {CID: 1} if mode == "resource-callback" else {}},
        }
        if not positive:
            observation["negative_window_completed"] = True
        if mode == "resource-callback":
            observation.update(callback_observed=True, callback_count=1)
        rows.append({"id": "proof-" + mode, "expect": {}, "expected_ids": [identity] if positive else [],
                     "observe_ms": 400, "expected_identity": {"method": "POST", "source_path": "/comments", "parameter": "comment", "read_path": "/comments", "role": "reader"},
                     "oracle_rationale": "independent fixture label",
                     "results": {"dxaprove": {"observed": observation, "score": {"tp": int(positive), "fp": 0, "fn": 0, "evaluated": True}}}})
    return {"run_at": "2026-10-13T00:00:00+00:00",
            "environment": {"python": "3.12.0", "platform": "Linux-test",
                            "runner_sha256": source_hash(runner.__file__),
                            "scanner_sha256": source_hash(runner.DXADYN.with_name("dxaprove.py")),
                            "fixture_sha256": source_hash(runner.DXADYN.with_name("dxa_proof_lab.py")),
                            "corpus_sha256": hashlib.sha256(json.dumps(runner.proof_corpus(), sort_keys=True).encode()).hexdigest()},
            "command": ["bench/run.py", "--proof-suite", "--no-history", "--out", "r4-proof.md"],
            "measurement": "correlated-browser-execution; not confirmed vulnerability accuracy",
            "corpus_version": "loopback-proof/2", "scanners": ["dxaprove"], "rows": rows,
            "totals": {"dxaprove": {"selected": 9, "completed": 9, "tp": 3, "fp": 0, "fn": 0,
                                     "error": 0, "timeout": 0, "skipped": 0, "invalid": 0, "inconclusive": 0, "wall": 0.9}}}


@pytest.fixture
def artifacts(tmp_path):
    suite = ET.Element("testsuite", tests="4", failures="0", errors="0", skipped="0")
    for module in MODULES:
        ET.SubElement(suite, "testcase", classname="tests." + module, name="test_acceptance")
    report = corpus()
    return {"path": tmp_path, "junit": suite, "corpus": report, "markdown": runner.render_md(report), "demo": proof(True)}


def invoke(artifacts, missing=None, malformed=None):
    paths = {key: artifacts["path"] / (key + (".xml" if key == "junit" else ".md" if key == "corpus-markdown" else ".json"))
             for key in ("junit", "corpus", "corpus-markdown", "demo")}
    for key, path in paths.items():
        if key == missing:
            continue
        if key == malformed:
            path.write_text("broken artifact", encoding="utf-8")
        elif key == "junit":
            ET.ElementTree(artifacts[key]).write(path, encoding="utf-8")
        elif key == "corpus-markdown":
            path.write_text(artifacts["markdown"], encoding="utf-8")
        else:
            path.write_text(json.dumps(artifacts[key]), encoding="utf-8")
    result = subprocess.run([sys.executable, str(GATE), *[part for key, path in paths.items() for part in ("--" + key, str(path))]], capture_output=True, text=True, timeout=20)
    assert "Traceback" not in result.stderr, result.stderr
    return result


def test_complete_independent_artifacts_pass(artifacts):
    result = invoke(artifacts)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("key", ("junit", "corpus", "corpus-markdown", "demo"))
@pytest.mark.parametrize("failure", ("missing", "malformed"))
def test_unreadable_artifact_fails(artifacts, key, failure):
    assert invoke(artifacts, **{failure: key}).returncode == 1


@pytest.mark.parametrize("tag", ("skipped", "error", "failure"))
def test_junit_bad_case_fails_even_with_zero_summary(artifacts, tag):
    ET.SubElement(artifacts["junit"][0], tag)
    assert invoke(artifacts).returncode == 1


@pytest.mark.parametrize("attribute,value", (("skipped", "1"), ("errors", "1"), ("failures", "1"), ("tests", "999"), ("tests", "bad")))
def test_junit_summary_inconsistency_fails(artifacts, attribute, value):
    artifacts["junit"].set(attribute, value)
    assert invoke(artifacts).returncode == 1


def test_missing_required_module_fails(artifacts):
    artifacts["junit"][0].set("classname", "tests.unrelated")
    assert invoke(artifacts).returncode == 1


def test_empty_suite_is_not_acceptance(artifacts):
    artifacts["junit"] = ET.Element("testsuite", tests="0", errors="0", failures="0", skipped="0")
    assert invoke(artifacts).returncode == 1


@pytest.mark.parametrize("mutation", ("missing", "duplicate", "unknown", "empty"))
def test_corpus_case_set_must_be_complete(artifacts, mutation):
    rows = artifacts["corpus"]["rows"]
    if mutation == "missing":
        rows.pop()
    elif mutation == "duplicate":
        rows[-1] = copy.deepcopy(rows[0])
    elif mutation == "unknown":
        rows[-1]["id"] = "proof-unreviewed"
    else:
        rows.clear()
    assert invoke(artifacts).returncode == 1


@pytest.mark.parametrize("status", ("error", "timeout", "skipped", "invalid", "inconclusive"))
def test_noncompleted_row_cannot_hide_behind_success_totals(artifacts, status):
    artifacts["corpus"]["rows"][0]["results"]["dxaprove"]["observed"]["status"] = status
    assert invoke(artifacts).returncode == 1


@pytest.mark.parametrize("field,value", (("tp", 2), ("fp", 1), ("fn", 1), ("completed", 8), ("selected", 8), ("skipped", 1)))
def test_false_totals_fail(artifacts, field, value):
    artifacts["corpus"]["totals"]["dxaprove"][field] = value
    assert invoke(artifacts).returncode == 1


@pytest.mark.parametrize("target", ("demo", "corpus"))
@pytest.mark.parametrize("mutation", ("inconclusive", "wrong_cid", "error_event", "session_unchecked", "wrong_frame", "empty_proofs"))
def test_execution_evidence_must_correlate(artifacts, target, mutation):
    item = artifacts["demo"] if target == "demo" else artifacts["corpus"]["rows"][0]["results"]["dxaprove"]["observed"]["proof"]
    if mutation == "inconclusive":
        item.update(proof(False))
    elif mutation == "wrong_cid":
        item["proofs"][0]["canary_id"] = "unrelated"
    elif mutation == "error_event":
        item["events"].append({"kind": "error", "reason": "read failed"})
    elif mutation == "session_unchecked":
        item["browser_session_checked"] = False
    elif mutation == "wrong_frame":
        item["proofs"][0]["frame_url"] = "http://127.0.0.1:49152/unrelated"
    else:
        item["proofs"] = []
    assert invoke(artifacts).returncode == 1


def test_negative_fixture_false_positive_fails_even_with_zero_fp_total(artifacts):
    row = artifacts["corpus"]["rows"][1]
    row["results"]["dxaprove"]["observed"]["proof"] = proof(True)
    assert invoke(artifacts).returncode == 1


def test_missing_callback_is_not_a_completed_callback_negative(artifacts):
    observed = artifacts["corpus"]["rows"][-1]["results"]["dxaprove"]["observed"]
    observed["fixture_observation"]["resource_callback_hits"] = {}
    assert invoke(artifacts).returncode == 1


@pytest.mark.parametrize("target", ("demo", "corpus"))
@pytest.mark.parametrize("value", (None, [], "unexpected"))
def test_json_document_wrong_type_fails_cleanly(artifacts, target, value):
    artifacts[target] = value
    assert invoke(artifacts).returncode == 1


@pytest.mark.parametrize("field,value", (("rows", None), ("rows", {}), ("totals", []), ("scanners", None)))
def test_corpus_wrong_container_types_fail_cleanly(artifacts, field, value):
    artifacts["corpus"][field] = value
    assert invoke(artifacts).returncode == 1


@pytest.mark.parametrize("field,value", (("proof", None), ("proof", []), ("findings", {}), ("fixture_observation", None)))
def test_wrong_nested_observation_types_fail_cleanly(artifacts, field, value):
    observed = artifacts["corpus"]["rows"][-1]["results"]["dxaprove"]["observed"]
    observed[field] = value
    assert invoke(artifacts).returncode == 1


def test_negative_window_with_skip_is_not_complete(artifacts):
    observed = artifacts["corpus"]["rows"][1]["results"]["dxaprove"]["observed"]
    observed["proof"]["events"].append({"kind": "skip", "stage": "observe", "reason": "frame unavailable"})
    assert invoke(artifacts).returncode == 1


@pytest.mark.parametrize("value", (float("nan"), float("inf"), -1))
@pytest.mark.parametrize("location", ("row", "totals"))
def test_invalid_elapsed_time_fails(artifacts, value, location):
    item = artifacts["corpus"]["totals"]["dxaprove"] if location == "totals" else artifacts["corpus"]["rows"][0]["results"]["dxaprove"]["observed"]
    item["wall"] = value
    assert invoke(artifacts).returncode == 1


def test_duplicate_testcase_does_not_supply_independent_coverage(artifacts):
    suite = artifacts["junit"]
    suite.append(copy.deepcopy(suite[0]))
    suite.set("tests", "5")
    assert invoke(artifacts).returncode == 1


def test_nested_junit_skip_cannot_hide_behind_clean_parent(artifacts):
    suite = artifacts["junit"]
    ET.SubElement(suite[0], "skipped")
    root = ET.Element("testsuites", tests="4", failures="0", errors="0", skipped="0")
    root.append(suite)
    artifacts["junit"] = root
    assert invoke(artifacts).returncode == 1


def test_cached_findings_must_match_nested_evidence(artifacts):
    artifacts["corpus"]["rows"][0]["results"]["dxaprove"]["observed"]["findings"] = []
    assert invoke(artifacts).returncode == 1


def test_boolean_score_is_not_an_integer_count(artifacts):
    artifacts["corpus"]["rows"][0]["results"]["dxaprove"]["score"]["tp"] = True
    assert invoke(artifacts).returncode == 1


def test_demo_external_read_origin_fails_without_network(artifacts):
    artifacts["demo"]["read_url"] = "https://example.invalid/comments"
    assert invoke(artifacts).returncode == 1


@pytest.mark.parametrize("field", ("python", "platform", "runner_sha256", "scanner_sha256", "fixture_sha256", "corpus_sha256"))
def test_missing_or_malformed_provenance_fails(artifacts, field):
    artifacts["corpus"]["environment"][field] = "unknown" if field.endswith("sha256") else ""
    assert invoke(artifacts).returncode == 1


@pytest.mark.parametrize(("field", "value"), (
    ("python", "3.11.9"), ("python", "3.13.0"),
    ("platform", "Windows-10-10.0.26200-SP0"), ("platform", "Darwin-24.0.0"),
))
def test_well_formed_but_non_ci_runtime_fails(artifacts, field, value):
    artifacts["corpus"]["environment"][field] = value
    # Keep the two artifacts internally consistent so this exercises runtime
    # provenance, not the earlier Markdown/JSON consistency guard.
    artifacts["markdown"] = runner.render_md(artifacts["corpus"])
    assert invoke(artifacts).returncode == 1


@pytest.mark.parametrize("field", ("runner_sha256", "scanner_sha256", "fixture_sha256", "corpus_sha256"))
def test_well_formed_but_stale_source_hash_fails(artifacts, field):
    artifacts["corpus"]["environment"][field] = "0" * 64
    assert invoke(artifacts).returncode == 1


@pytest.mark.parametrize("command", ([], ["bench/run.py", "--out", "r4-proof.md"],
                                      ["bench/run.py", "--proof-suite", "--no-history", "--out", "other.md"]))
def test_wrong_corpus_command_provenance_fails(artifacts, command):
    artifacts["corpus"]["command"] = command
    assert invoke(artifacts).returncode == 1


def test_markdown_score_mismatch_fails(artifacts):
    assert invoke(artifacts).returncode == 0
    path = artifacts["path"] / "corpus-markdown.md"
    content = path.read_text(encoding="utf-8").replace("| dxaprove | 3 | 0 | 0 |", "| dxaprove | 2 | 1 | 0 |")
    path.write_text(content, encoding="utf-8")
    result = subprocess.run([sys.executable, str(GATE), "--junit", str(artifacts["path"] / "junit.xml"),
                             "--corpus", str(artifacts["path"] / "corpus.json"),
                             "--corpus-markdown", str(path), "--demo", str(artifacts["path"] / "demo.json")],
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 1


def test_markdown_missing_case_fails(artifacts):
    result = invoke(artifacts)
    assert result.returncode == 0
    path = artifacts["path"] / "corpus-markdown.md"
    path.write_text(path.read_text(encoding="utf-8").replace("### proof-json\n", ""), encoding="utf-8")
    # Re-run the gate against the modified Markdown while retaining the same JSON artifact.
    result = subprocess.run([sys.executable, str(GATE), "--junit", str(artifacts["path"] / "junit.xml"),
                             "--corpus", str(artifacts["path"] / "corpus.json"),
                             "--corpus-markdown", str(path), "--demo", str(artifacts["path"] / "demo.json")],
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 1


def test_markdown_identity_mismatch_fails(artifacts):
    assert invoke(artifacts).returncode == 0
    path = artifacts["path"] / "corpus-markdown.md"
    content = path.read_text(encoding="utf-8").replace("proof-v2:raw:POST:/comments:comment:/comments:reader", "proof-v2:other:POST:/comments:comment:/comments:reader", 1)
    path.write_text(content, encoding="utf-8")
    result = subprocess.run([sys.executable, str(GATE), "--junit", str(artifacts["path"] / "junit.xml"),
                             "--corpus", str(artifacts["path"] / "corpus.json"),
                             "--corpus-markdown", str(path), "--demo", str(artifacts["path"] / "demo.json")],
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 1
