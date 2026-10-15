"""Bounded, local-only Dalfox vs dxadyn stored-XSS candidate adapter."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import secrets
import subprocess
import sys
import time

from r4_comparison_fixture import R4ComparisonFixture


CASES = (
    {"id": "r4-admin-stored/raw-admin-content", "escaped": False, "expected_execution": True},
    {"id": "r4-admin-stored/escaped-admin-content", "escaped": True, "expected_execution": False},
)
REPETITIONS = 2
REQUEST_LIMIT = 20
RATE_LIMIT = 2
WALL_LIMIT = 20
COMMAND_TIMEOUT = 20
DXADYN = Path(__file__).resolve().parents[1] / "tools/dom-xss-analyzer/dxadyn.py"
REPO = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _command(tool, origin, cookie, report_path, dalfox_path):
    target = origin + "/comments"
    read = origin + "/admin/comments"
    if tool == "dxadyn":
        return [sys.executable, str(DXADYN), "--stored", "--target", target,
                "--target-field", "comment", "--check", read, "--csrf-field", "",
                "--variants", "body", "--parallel", "1", "--rate", str(RATE_LIMIT),
                "--cookie", "bridge=" + cookie, "--json-out", str(report_path)]
    return [dalfox_path, "scan", target, "-X", "POST", "-d", "comment=seed",
            "-p", "comment:body", "--sxss", "--sxss-url", read,
            "--sxss-method", "GET", "--sxss-retries", "1",
            "--cookies", "bridge=" + cookie, "--max-payloads-per-param", "2",
            "--workers", "1", "--rate-limit", str(RATE_LIMIT),
            "--timeout", "2", "--scan-timeout", "12", "--skip-mining",
            "--skip-ast-analysis", "--skip-waf-probe", "--waf-bypass", "off",
            "--no-color", "--format", "json", "--output", str(report_path)]


def _parse_findings(tool, path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if tool == "dxadyn":
        rows = value.get("findings") if isinstance(value, dict) else None
        return rows if isinstance(rows, list) else None
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("data", "findings", "issues", "results"):
            rows = value.get(key)
            if isinstance(rows, list):
                return rows
    return None


def _classify_run(returncode, timed_out, budget_exceeded, findings, wall):
    """Keep scanner errors and timeouts distinct from valid completed runs."""
    if timed_out:
        return "timeout"
    # dxadyn documents exit 1 when it has candidate findings. Treat that as a
    # completed scan only when its structured output also contains candidates.
    finding_exit = returncode == 1 and isinstance(findings, list) and bool(findings)
    if returncode != 0 and not finding_exit:
        return "error"
    if budget_exceeded or findings is None or wall > WALL_LIMIT:
        return "incomplete"
    return "completed"


def run_comparison(dalfox_path: Path, output: Path):
    dalfox_path = dalfox_path.resolve()
    output.mkdir(parents=True, exist_ok=True)
    records = []
    order = ("dxadyn", "dalfox")
    for repetition in range(1, REPETITIONS + 1):
        tool_order = order if repetition == 1 else tuple(reversed(order))
        for case in CASES:
            for tool in tool_order:
                # A new identical fixture per tool/case/repetition keeps the
                # scanner's writes and budgets isolated and repeatable.
                with R4ComparisonFixture(escaped=case["escaped"], request_limit=REQUEST_LIMIT,
                                         rate_limit=RATE_LIMIT, wall_limit=WALL_LIMIT) as fixture:
                    cookie = fixture.state.broker_cookie()
                    run_dir = output / "runs" / f"rep-{repetition}" / case["id"].rsplit("/", 1)[-1] / tool
                    run_dir.mkdir(parents=True, exist_ok=True)
                    report_path = run_dir / ("scanner.json" if tool == "dalfox" else "scanner-report.json")
                    argv = _command(tool, fixture.origin, cookie, report_path,
                                    str(dalfox_path))
                    # Credentials and ephemeral ports are deliberately omitted
                    # from the shareable command manifest.
                    safe_argv = ["<dalfox-v3.2.4>" if x == str(dalfox_path) else
                                 "<python-3.10>" if x == sys.executable else
                                 "<repo>/tools/dom-xss-analyzer/dxadyn.py" if x == str(DXADYN) else
                                 x.replace("bridge=" + cookie, "bridge=<fixture-token>")
                                 .replace(fixture.origin, "http://127.0.0.1:<ephemeral-port>")
                                 for x in argv]
                    env = os.environ.copy()
                    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy",
                                 "https_proxy", "all_proxy"):
                        env.pop(name, None)
                    env["NO_PROXY"] = "127.0.0.1,localhost"
                    started = time.monotonic()
                    timed_out = False
                    try:
                        completed = subprocess.run(argv, cwd=str(REPO), env=env,
                                                   capture_output=True, text=True,
                                                   timeout=COMMAND_TIMEOUT, check=False)
                        returncode, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
                    except subprocess.TimeoutExpired as exc:
                        timed_out = True
                        returncode = None
                        stdout = (exc.stdout or b"").decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                        stderr = (exc.stderr or b"").decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
                    wall = round(time.monotonic() - started, 3)
                    findings = _parse_findings(tool, report_path)
                    redactions = ((fixture.origin, "http://127.0.0.1:<ephemeral-port>"),
                                  (cookie, "<fixture-token>"))
                    for name, contents in (("stdout.txt", stdout), ("stderr.txt", stderr)):
                        for secret, replacement in redactions:
                            contents = contents.replace(secret, replacement)
                        (run_dir / name).write_text(contents, encoding="utf-8")
                    if report_path.is_file():
                        report_text = report_path.read_text(encoding="utf-8")
                        for secret, replacement in redactions:
                            report_text = report_text.replace(secret, replacement)
                        report_path.write_text(report_text, encoding="utf-8")
                    exhausted = fixture.state.budget_exceeded
                    outcome = _classify_run(returncode, timed_out, exhausted, findings, wall)
                    statuses = [row["status"] for row in fixture.state.requests]
                    rejected = sum(1 for row in fixture.state.requests if row.get("budget_rejected"))
                    records.append({
                        "case_id": case["id"], "expected_execution": case["expected_execution"],
                        "repetition": repetition, "order_index": tool_order.index(tool),
                        "tool": tool, "status": outcome,
                        "selected": 1, "completed": outcome == "completed",
                        "error": outcome == "error", "timeout": outcome == "timeout",
                        "candidate_count": len(findings) if findings is not None else None,
                        "candidate_observed": bool(findings) if findings is not None else None,
                        "return_code": returncode, "timed_out": timed_out,
                        "budget_exceeded": exhausted,
                        "request_attempts": len(fixture.state.requests),
                        "forwarded_requests": len(fixture.state.requests) - rejected,
                        "budget_rejected_requests": rejected,
                        "request_limit": REQUEST_LIMIT, "max_inflight": fixture.state.max_inflight,
                        "rate_limit_rps": RATE_LIMIT, "wall_seconds": wall,
                        "wall_limit_seconds": WALL_LIMIT, "command_timeout_seconds": COMMAND_TIMEOUT,
                        "safe_command": safe_argv,
                        "http_statuses": statuses,
                    })
    counts = {name: sum(1 for row in records if row["status"] == name)
              for name in ("completed", "error", "timeout", "incomplete")}
    return {
        "schema": "r4-local-comparison/1", "status": "partial-candidate-comparison",
        "summary": {"selected": len(records), **counts},
        "corpus_version": "r4-admin-stored-candidate/1",
        "cases": list(CASES), "repetitions": REPETITIONS,
        "order": {"rep-1": ["dxadyn", "dalfox"], "rep-2": ["dalfox", "dxadyn"]},
        "identity": {"method": "POST", "source_path": "/comments", "parameter": "comment",
                     "read_path": "/admin/comments", "role": "writer-to-reader-admin fixture broker"},
        "auth": {"scanner_input": "same ephemeral bridge cookie", "brokered_roles": ["writer", "reader-admin"],
                 "real_login_coverage": False},
        "budgets": {"requests_per_run": REQUEST_LIMIT, "rate_rps": RATE_LIMIT,
                    "concurrency": 1, "wall_seconds": WALL_LIMIT,
                    "outer_process_seconds": COMMAND_TIMEOUT, "dalfox_per_request_seconds": 2,
                    "dxadyn_per_request_seconds": 15},
        "runtime": {"python": platform.python_version(), "platform": platform.platform(),
                    "dalfox_version": "3.2.4", "dalfox_sha256": sha256(dalfox_path),
                    "dxadyn_sha256": sha256(DXADYN), "adapter_sha256": sha256(Path(__file__)),
                    "test_sha256": sha256(Path(__file__).with_name("test_r4_compare_local.py")),
                    "fixture_sha256": sha256(Path(__file__).with_name("r4_comparison_fixture.py"))},
        "results": records,
        "interpretation": {
            "candidate_only": True,
            "browser_execution_oracle": "reported separately by test_r4_compare_local.py",
            "ranking": False,
            "coverage_gaps": [
                "scanner accounts are not independently authenticated; local broker maps one test cookie to distinct writer and reader-admin fixture roles",
                "candidate rows are not correlated to scanner-generated CIDs and must not be scored as execution TP/FP/FN",
                "per-request client timeouts differ; hard request, rate, concurrency, and outer wall budgets are shared",
                "dxaprove execution proof is not a scanner candidate parser and is not ranked against either candidate scanner"
            ]
        }
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dalfox", required=True, help="path to checksum-verified Dalfox 3.2.4 binary")
    parser.add_argument("--output", required=True, type=Path, help="new R4 audit output directory")
    args = parser.parse_args()
    result = run_comparison(Path(args.dalfox), args.output)
    (args.output / "comparison.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"selected={result['summary']['selected']} completed={result['summary']['completed']} "
          f"error={result['summary']['error']} timeout={result['summary']['timeout']} "
          f"incomplete={result['summary']['incomplete']}")
    return 0 if result["summary"]["selected"] == result["summary"]["completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
