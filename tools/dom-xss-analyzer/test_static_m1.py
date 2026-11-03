"""Independent frozen JSX review-candidate regressions, no fixture execution."""
import importlib.util
from pathlib import Path

import pytest
import dxa
import dxa_evidence as evidence

_PATH = Path(__file__).resolve().parents[2] / "audit/2026-11-03-r8-m1/measure.py"
_SPEC = importlib.util.spec_from_file_location("m1_measure_for_tests", _PATH)
study = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(study)


@pytest.mark.parametrize("case", study.load_cases(), ids=lambda case: case["id"])
def test_frozen_jsx_candidate(case, tmp_path):
    study.verify_manifest()
    observed = study.observe(dxa, case, tmp_path)
    assert observed["status"] == "completed", observed
    assert observed["observed_candidates"] == case["expected_candidates"], observed
    assert observed["properties_ok"], observed


@pytest.mark.parametrize("case", [case for case in study.load_cases("development")
                                 if case["expected_candidates"]], ids=lambda case: case["id"])
def test_style_anchor_remains_unreviewed_candidate(case, tmp_path):
    path = tmp_path / (case["id"] + ".jsx")
    path.write_text(case["source"], encoding="utf-8")
    rows = [row for row in dxa.scan_file(str(path)) if row["sink"] == "jsx-href"]
    assert len(rows) == 1
    exported = evidence.static_observations(rows)
    assert len(exported) == 1
    assert exported[0]["evidence_level"] == "candidate"
    assert exported[0]["triage"] == "unreviewed"
