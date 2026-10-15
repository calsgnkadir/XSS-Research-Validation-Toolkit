"""Budget and result-accounting regressions for the R4 comparator."""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from r4_compare_local import _classify_run


@pytest.mark.parametrize("args,expected", [
    ((0, False, False, [], 1), "completed"),
    ((0, True, True, [], 20), "timeout"),
    ((1, False, False, [], 1), "error"),
    ((1, False, False, [{"reflection": "unencoded"}], 1), "completed"),
    ((0, False, True, [], 2), "incomplete"),
    ((0, False, False, None, 1), "incomplete"),
])
def test_run_accounting_never_promotes_errors_or_budget_violations(args, expected):
    assert _classify_run(*args) == expected


def test_unknown_tool_exit_one_with_rows_remains_error():
    assert _classify_run(1, False, False, [{"type": "R"}], 1, tool="unknown") == "error"

def test_existing_output_rejected_before_binary_or_fixture(tmp_path):
    from r4_compare_local import run_comparison
    previous = tmp_path / "previous"
    previous.mkdir()
    marker = previous / "scanner.json"
    marker.write_text("[]")
    with pytest.raises(ValueError, match="new directory"):
        run_comparison(tmp_path / "missing-binary", previous)
    assert marker.read_text() == "[]"

def test_unexpected_version_rejected_before_creating_output(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import r4_compare_local as adapter
    monkeypatch.setattr(adapter.subprocess, "run", lambda *a, **k: SimpleNamespace(stdout="dalfox 9.0"))
    output = tmp_path / "new"
    with pytest.raises(ValueError, match="version"):
        adapter.run_comparison(tmp_path / "binary", output)
    assert not output.exists()


def test_pinned_dalfox_findings_exit_is_completed():
    assert _classify_run(1, False, False, [{"type": "R"}], 1, tool="dalfox") == "completed"

@pytest.mark.parametrize("tool,document", [
    ("dalfox", {"findings": [{}], "meta": {"incomplete": True, "failed_requests": 0, "findings_count": 1}}),
    ("dalfox", {"findings": [], "meta": {"incomplete": False, "failed_requests": 1, "findings_count": 0}}),
    ("dalfox", {"findings": []}),
    ("dxadyn", {"findings": [], "events": [{"kind": "error"}]}),
    ("dxadyn", {"findings": [], "events": [{"kind": "skip"}]}),
    ("dxadyn", {"findings": [], "skipped_submits": 1}),
])
def test_partial_reports_cannot_be_completed(tmp_path, tool, document):
    import json
    from r4_compare_local import _parse_findings
    report = tmp_path / "report.json"
    report.write_text(json.dumps(document))
    findings = _parse_findings(tool, report)
    assert findings is None
    assert _classify_run(1, False, False, findings, 1, tool=tool) == "incomplete"


@pytest.mark.parametrize("events", [None, 42, "error", [None]])
def test_malformed_events_are_incomplete(tmp_path, events):
    import json
    from r4_compare_local import _parse_findings
    report = tmp_path / "report.json"
    report.write_text(json.dumps({"findings": [], "events": events}))
    assert _parse_findings("dxadyn", report) is None

def test_invalid_utf8_report_is_incomplete(tmp_path):
    from r4_compare_local import _parse_findings
    report = tmp_path / "report.json"
    report.write_bytes(b"\xff")
    assert _parse_findings("dalfox", report) is None
