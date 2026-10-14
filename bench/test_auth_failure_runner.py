"""Independent runner and failure lifecycle oracles; no XSS accuracy credit."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auth_failure_corpus as controls
import process_control
import run as runner

EXPECTED = {
    "login-rejected": ("http-auth", 0, 0, 0),
    "http-identity-mismatch": ("http-auth", 0, 0, 0),
    "browser-role-mismatch": ("browser-auth", 0, 0, 0),
    "csrf-missing": ("submit", 0, 0, 1),
    "csrf-rejected": ("submit", 1, 0, 1),
    "session-expired-after-submit": ("browser-auth-after-submit", 1, 1, 0),
}


def row_for(case):
    stage, requests, posts, csrf = EXPECTED[case]
    return {
        "case_id": "auth-failure-v1:" + case,
        "control_passed": False,  # parent must recompute, never trust worker boolean
        "scanner_status": "error", "accuracy_evaluated": False,
        "expected_stage": stage,
        "proof": {"schema": "dxa-browser-proof/1", "status": "error",
                  "execution_observed": False, "proofs": [],
                  "events": [{"kind": "error", "stage": stage, "reason": "ValueError"}],
                  "submit_status": 403 if case == "csrf-rejected" else 201 if posts else None},
        "fixture": {"login_requests": 1, "submit_requests": requests,
                    "posts": posts, "reads": 0, "csrf_fetches": csrf},
    }


def install_worker(monkeypatch, fault=None):
    calls = []

    class Worker:
        def __init__(self, command):
            self.proc = type("Process", (), {"returncode": 0})()
            calls.append(self)
            self.closed = False

        def communicate(self, config, timeout):
            self.config = json.loads(config)
            self.timeout = timeout
            if fault == "timeout":
                raise subprocess.TimeoutExpired("owned worker", timeout)
            if fault == "nonzero":
                self.proc.returncode = 2
            row = row_for(self.config["case"])
            if fault == "identity":
                row["case_id"] = "other"
            if fault == "stage":
                row["proof"]["events"][0]["stage"] = "browser-start"
                row["control_passed"] = True
            if fault == "malformed":
                row["proof"] = None
            return json.dumps(row)

        def close(self):
            self.closed = True
            if fault == "cleanup":
                raise OSError("private cleanup details")

    monkeypatch.setattr(process_control, "OwnedProcess", Worker)
    return calls


@pytest.mark.parametrize("fault", [None, "timeout", "nonzero", "identity", "stage", "malformed", "cleanup"])
def test_owned_workers_have_deadline_cleanup_and_independent_acceptance(monkeypatch, fault):
    calls = install_worker(monkeypatch, fault)
    report = controls.run_suite("local-browser")
    assert len(calls) == report["selected"] == 6
    assert report["passed"] == (6 if fault is None else 0)
    assert all(call.closed and call.timeout == 30 for call in calls)
    assert all(call.config["browser"] == "local-browser" for call in calls)
    assert all(row["accuracy_evaluated"] is False for row in report["rows"])
    assert "private cleanup details" not in json.dumps(report)
    if fault == "timeout":
        assert all(row["scanner_status"] == "timeout" for row in report["rows"])
    if fault == "cleanup":
        assert all(row["cleanup_status"] == "error" for row in report["rows"])


def base_report():
    return {"run_at": "test", "corpus_version": "test/1", "measurement": "test",
            "scanners": ["dxadyn"], "rows": [],
            "totals": {"dxadyn": {"tp": 2, "fp": 0, "fn": 0, "wall": 0,
                                   "completed": 2, "selected": 2}}}


@pytest.mark.parametrize("proof_mode", [False, True])
@pytest.mark.parametrize("fault", [None, "stage", "timeout", "cleanup"])
def test_runner_cli_reports_controls_separately_and_returns_nonzero(tmp_path, monkeypatch, proof_mode, fault):
    install_worker(monkeypatch, fault)
    monkeypatch.setattr(runner, "run_all", lambda *_: base_report())
    monkeypatch.setattr(runner, "load_corpus", lambda *_: {"targets": []})
    monkeypatch.setattr(runner, "proof_corpus", lambda *_: {"targets": []})
    output = tmp_path / "result.md"
    args = ["bench/run.py", "--auth-failure-controls", "--browser", "local-browser",
            "--out", str(output), "--no-history"]
    if proof_mode:
        args.append("--proof-suite")
    monkeypatch.setattr(sys, "argv", args)
    monkeypatch.setenv("BENCH_STRICT", "1")
    assert runner.main() == (0 if fault is None else 2)
    report = json.loads(output.with_suffix(".json").read_text(encoding="utf-8"))
    assert report["totals"] == base_report()["totals"]
    assert report["rows"] == []
    assert report["operational_controls"][0]["passed"] == (6 if fault is None else 0)
    assert output.read_text(encoding="utf-8") == runner.render_md(report)
    assert "no TP/FP/FN or completed-negative credit" in output.read_text(encoding="utf-8")


def test_controls_are_opt_in(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "run_all", lambda *_: base_report())
    monkeypatch.setattr(runner, "load_corpus", lambda *_: {"targets": []})
    monkeypatch.setattr(controls, "run_suite", lambda *_: pytest.fail("unexpected controls"))
    output = tmp_path / "plain.md"
    monkeypatch.setattr(sys, "argv", ["bench/run.py", "--out", str(output), "--no-history"])
    assert runner.main() == 0
    assert "operational_controls" not in json.loads(output.with_suffix(".json").read_text())


@pytest.mark.parametrize("args", [
    ["--browser", "unselected"],
    ["--proof-suite", "--auth-failure-controls", "--with", "dalfox"],
    ["--auth-failure-controls", "--bludit-browser", "unselected"],
    ["--auth-failure-controls", "--proof-suite", "--bludit-control"],
])
def test_incompatible_options_rejected_before_work(monkeypatch, args):
    monkeypatch.setattr(runner, "run_all", lambda *_: pytest.fail("unexpected scan"))
    monkeypatch.setattr(sys, "argv", ["bench/run.py"] + args)
    with pytest.raises(SystemExit) as result:
        runner.main()
    assert result.value.code == 2


@pytest.mark.parametrize("field,value", [("proof", None), ("fixture", None)])
def test_malformed_worker_evidence_is_not_accepted(field, value):
    row = row_for("csrf-missing")
    row[field] = value
    assert controls.accept_failure("csrf-missing", row["proof"], row["fixture"]) is False
