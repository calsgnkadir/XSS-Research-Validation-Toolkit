"""R9 self-scan acceptance through real local CLI subprocesses.

The bundled examples are intentionally vulnerable *static candidates*, not
browser execution evidence. No network or browser is used by these tests.
"""
import json
import pathlib
import re
import shlex
import subprocess
import sys

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "dom-xss-analyzer" / "dxa.py"
EXAMPLES = ANALYZER.parent / "examples"
GATE = ROOT / "bench" / "ci_self_scan.py"


def gate(*arguments):
    # A timeout in this outer harness is a test error, never a passing gate.
    return subprocess.run(
        [sys.executable, str(GATE), *map(str, arguments)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=20,
    )


def write_analyzer(tmp_path, body):
    script = tmp_path / "analyzer.py"
    script.write_text(body, encoding="utf-8")
    return script


def test_real_example_corpus_passes():
    result = gate(EXAMPLES)
    assert result.returncode == 0, result.stdout + result.stderr


def test_required_ci_job_runs_gate_and_regressions():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    # Inspect actual run commands in the required job, not a comment mentioning
    # the helper. This deliberately avoids depending on human-readable step names.
    job = re.search(r"(?ms)^  test:\n(.*?)(?=^  [\w-]+:|\Z)", workflow).group(1)
    assert "continue-on-error: true" not in job
    commands = [shlex.split(line.strip()) for line in re.findall(r"(?m)^\s+run: (.+)$", job)]
    assert ["python", "bench/ci_self_scan.py"] in commands
    assert any(command[0] == "pytest" and "bench/test_ci_self_scan.py" in command
               for command in commands)


@pytest.mark.parametrize("corpus", ["clean", "empty", "missing"])
def test_no_findings_or_incomplete_discovery_fails(tmp_path, corpus):
    target = tmp_path / corpus
    if corpus != "missing":
        target.mkdir()
    if corpus == "clean":
        (target / "safe.js").write_text(
            'document.body.textContent = "constant";\n', encoding="utf-8"
        )
    result = gate(target)
    assert result.returncode != 0, result.stdout + result.stderr


@pytest.mark.parametrize("body", [
    'raise RuntimeError("injected scanner crash")\n',
    'import dxa_missing_dependency_for_ci_regression\n',
    'import argparse\nargparse.ArgumentParser().parse_args()\n',
    'print("1 finding(s) - 1 at HIGH confidence")\n'
    'raise RuntimeError("crash after finding-like output")\n',
])
def test_scanner_failure_is_not_an_expected_finding(tmp_path, body):
    analyzer = write_analyzer(tmp_path, body)
    result = gate(EXAMPLES, "--analyzer", analyzer)
    assert result.returncode != 0, result.stdout + result.stderr


def test_timed_out_scanner_fails(tmp_path):
    analyzer = write_analyzer(tmp_path, 'import time\ntime.sleep(10)\n')
    result = gate(EXAMPLES, "--analyzer", analyzer, "--timeout", "0.2")
    assert result.returncode != 0, result.stdout + result.stderr
    assert "timeout" in (result.stdout + result.stderr).lower()


@pytest.fixture(scope="module")
def real_report(tmp_path_factory):
    """Produce evidence with the actual scanner, independent of gate internals."""
    report_path = tmp_path_factory.mktemp("self-scan-evidence") / "report.json"
    result = subprocess.run(
        [sys.executable, str(ANALYZER), str(EXAMPLES), "--min-confidence",
         "high", "--json", "--json-out", str(report_path)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=20,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["findings"]
    return report, result.stdout


@pytest.mark.parametrize("fault", [
    "missing-report", "malformed-report", "empty-findings",
    "error-event", "traceback-after-report", "unexpected-exit",
    "read-skip", "medium-confidence", "invalid-mode", "source-mismatch",
])
def test_findings_cannot_hide_failed_or_invalid_run(tmp_path, real_report, fault):
    # Start with actual scanner evidence, then inject a single independent
    # failure. A plausible finding count or stdout is insufficient for success.
    report, stdout = real_report
    report = json.loads(json.dumps(report))
    if fault == "empty-findings":
        report["findings"] = []
    if fault in ("error-event", "read-skip"):
        report["events"].append({
            "event_id": "ci-read-error", "observed_at": "2026-10-11T00:00:00Z",
            "stage": "static-read", "kind": "error" if fault == "error-event" else "skip",
            "reason": "unreadable file",
            "url": None, "status": None, "canary_id": None,
        })
    if fault == "medium-confidence":
        report["findings"][0]["confidence"] = "medium"
    if fault == "invalid-mode":
        report["mode"] = "http"
    if fault == "source-mismatch":
        report["findings"][0]["source"]["line"] += 1
    serialized = "{" if fault == "malformed-report" else json.dumps(report)
    body = "import pathlib, sys\n"
    if fault != "missing-report":
        body += (
            'output = pathlib.Path(sys.argv[sys.argv.index("--json-out") + 1])\n'
            f'output.write_text({serialized!r}, encoding="utf-8")\n'
        )
    body += f"print({stdout!r})\n"
    if fault == "traceback-after-report":
        body += 'raise RuntimeError("crash after report write")\n'
    else:
        body += f"sys.exit({2 if fault == 'unexpected-exit' else 1})\n"
    analyzer = write_analyzer(tmp_path, body)
    result = gate(EXAMPLES, "--analyzer", analyzer)
    assert result.returncode != 0, result.stdout + result.stderr
