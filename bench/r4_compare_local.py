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
from r4_scanner_sessions import check_role_boundaries, check_scanner_sessions, provision_scanner_sessions


CASES = (
    {"id": "r4-admin-stored/raw-admin-content", "escaped": False, "expected_execution": True},
    {"id": "r4-admin-stored/escaped-admin-content", "escaped": True, "expected_execution": False},
)
REPETITIONS = 2
REQUEST_LIMIT = 200
RATE_LIMIT = 2
WALL_LIMIT = 120
COMMAND_TIMEOUT = 120
CLIENT_TIMEOUT = 15
DALFOX_VERSION = "3.2.4"
IDENTITY = {"method": "POST", "source_path": "/comments", "parameter": "comment",
            "read_path": "/admin/comments", "role": "writer-to-reader-admin",
            "role_verification": "separate fixture principals checked before and after each scan"}
DXADYN = Path(__file__).resolve().parents[1] / "tools/dom-xss-analyzer/dxadyn.py"
REPO = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _redact_auth_text(value: str, origin: str, sessions) -> str:
    for secret, replacement in (
        (f"writer_session={sessions.writer_token}; admin_session={sessions.admin_token}",
         "<independent-writer-admin-session-pair>"),
        (sessions.writer_token, "<writer-session>"),
        (sessions.admin_token, "<reader-admin-session>"),
        (origin, "http://127.0.0.1:<ephemeral-port>"),
    ):
        value = value.replace(secret, replacement)
    return value


def _command(tool, origin, cookie, report_path, dalfox_path):
    target = origin + "/comments"
    read = origin + "/admin/comments"
    if tool == "dxadyn":
        return [sys.executable, str(DXADYN), "--stored", "--target", target,
                "--target-field", "comment", "--check", read, "--csrf-field", "",
                "--variants", "body", "--parallel", "1", "--rate", str(RATE_LIMIT),
                "--cookie", cookie, "--json-out", str(report_path)]
    return [dalfox_path, "scan", target, "-X", "POST", "-d", "comment=seed",
            "-p", "comment:body", "--sxss", "--sxss-url", read,
            "--sxss-method", "GET", "--sxss-retries", "1",
            "--cookies", cookie, "--max-payloads-per-param", "2",
            "--workers", "1", "--rate-limit", str(RATE_LIMIT),
            "--timeout", str(CLIENT_TIMEOUT), "--scan-timeout", str(WALL_LIMIT), "--skip-mining",
            "--skip-discovery", "--encoders", "none",
            "--skip-ast-analysis", "--skip-waf-probe", "--waf-bypass", "off",
            "--no-color", "--format", "json", "--output", str(report_path)]


def _parse_findings(tool, path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict):
        return None
    rows = value.get("findings")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        return None
    if tool == "dxadyn":
        events = value.get("events", [])
        if not isinstance(events, list) or any(not isinstance(event, dict) for event in events):
            return None
        if value.get("skipped_submits", 0) or any(event.get("kind") in {"error", "skip"} for event in events):
            return None
        return rows
    if tool == "dalfox":
        meta = value.get("meta", {})
        if (isinstance(meta, dict) and meta.get("incomplete") is False
                and type(meta.get("failed_requests")) is int and meta["failed_requests"] == 0
                and type(meta.get("findings_count")) is int and meta["findings_count"] == len(rows)):
            return rows
    return None


def _classify_run(returncode, timed_out, budget_exceeded, findings, wall, *, tool="dxadyn"):
    """Keep scanner errors and timeouts distinct from valid completed runs."""
    if timed_out:
        return "timeout"
    # Both dxadyn and pinned Dalfox 3.2.4 document exit 1 for findings.
    # Incomplete reports are rejected by the parser before this classification.
    finding_exit = tool in {"dxadyn", "dalfox"} and returncode == 1 and isinstance(findings, list) and bool(findings)
    if returncode not in (0, 1):
        return "error"
    if budget_exceeded or findings is None or wall > WALL_LIMIT:
        return "incomplete"
    if returncode != 0 and not finding_exit:
        return "error"
    return "completed"


def run_comparison(dalfox_path: Path, output: Path):
    dalfox_path = dalfox_path.resolve()
    if output.exists():
        raise ValueError("comparison output must be a new directory")
    version = subprocess.run([str(dalfox_path), "--version"], capture_output=True,
                             text=True, timeout=10, check=True).stdout.strip()
    if version != "dalfox " + DALFOX_VERSION:
        raise ValueError("unexpected Dalfox version")
    output.mkdir(parents=True, exist_ok=False)
    records = []
    order = ("dxadyn", "dalfox")
    for repetition in range(1, REPETITIONS + 1):
        tool_order = order if repetition == 1 else tuple(reversed(order))
        for case in CASES:
            for tool in tool_order:
                with R4ComparisonFixture(escaped=case["escaped"], request_limit=REQUEST_LIMIT,
                                         rate_limit=RATE_LIMIT, wall_limit=WALL_LIMIT) as fixture:
                    sessions = provision_scanner_sessions(fixture)
                    session_checks = check_scanner_sessions(fixture, sessions, "pre")
                    boundary_checks = check_role_boundaries(fixture, sessions)
                    if (not all(row["passed"] for row in session_checks.values())
                            or not all(row["passed"] for row in boundary_checks.values())):
                        raise RuntimeError("fixture session preflight failed")
                    preflight_request_count = len(fixture.state.requests)
                    cookie = sessions.cookie_header
                    run_dir = output / "runs" / f"rep-{repetition}" / case["id"].rsplit("/", 1)[-1] / tool
                    run_dir.mkdir(parents=True, exist_ok=True)
                    report_path = run_dir / ("scanner.json" if tool == "dalfox" else "scanner-report.json")
                    argv = _command(tool, fixture.origin, cookie, report_path, str(dalfox_path))
                    safe_argv = ["<output>/" + report_path.relative_to(output).as_posix() if x == str(report_path) else
                                 "<dalfox-v3.2.4>" if x == str(dalfox_path) else
                                 "<python-3.10>" if x == sys.executable else
                                 "<repo>/tools/dom-xss-analyzer/dxadyn.py" if x == str(DXADYN) else
                                 x.replace(cookie, "<independent-writer-admin-session-pair>")
                                 .replace(sessions.writer_token, "<writer-session>")
                                 .replace(sessions.admin_token, "<reader-admin-session>")
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
                    scanner_request_rows = list(fixture.state.requests[preflight_request_count:])
                    session_checks.update(check_scanner_sessions(fixture, sessions, "post"))
                    session_ok = all(row.get("passed") for row in session_checks.values())
                    for name, contents in (("stdout.txt", stdout), ("stderr.txt", stderr)):
                        contents = _redact_auth_text(contents, fixture.origin, sessions)
                        (run_dir / name).write_text(contents, encoding="utf-8")
                    if report_path.is_file():
                        report_text = report_path.read_text(encoding="utf-8", errors="replace")
                        report_text = _redact_auth_text(report_text, fixture.origin, sessions)
                        report_path.write_text(report_text, encoding="utf-8")
                    exhausted = fixture.state.budget_exceeded
                    outcome = _classify_run(returncode, timed_out, exhausted, findings, wall, tool=tool)
                    if not session_ok and outcome == "completed":
                        outcome = "incomplete"
                    statuses = [row["status"] for row in fixture.state.requests]
                    rejected = sum(1 for row in fixture.state.requests if row.get("budget_rejected"))
                    artifacts = {}
                    for label, path in (("stdout", run_dir / "stdout.txt"),
                                        ("stderr", run_dir / "stderr.txt"), ("report", report_path)):
                        artifacts[label] = ({"path": path.relative_to(output).as_posix(),
                                             "sha256": sha256(path)} if path.is_file() else None)
                    records.append({
                        "identity": dict(IDENTITY), "artifacts": artifacts,
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
                        "rate_limit_rps": RATE_LIMIT, "per_request_timeout_seconds": CLIENT_TIMEOUT,
                        "wall_seconds": wall, "wall_limit_seconds": WALL_LIMIT,
                        "command_timeout_seconds": COMMAND_TIMEOUT,
                        "safe_command": safe_argv, "http_statuses": statuses,
                        "request_trace": [
                            {"method": row["method"], "path": row["path"], "status": row["status"],
                             "budget_rejected": row.get("budget_rejected", False)}
                            for row in fixture.state.requests],
                        "scanner_requests_by_path": {
                            path: sum(row["path"] == path for row in scanner_request_rows)
                            for path in ("/comments", "/admin/comments")},
                        "session_checks": sessions.public_record(session_checks),
                        "session_verified": session_ok,
                        "role_boundary_checks": boundary_checks,
                        "stored_payloads": fixture.stored_comments(),
                        "fixture_request_counts": {
                            "login": sum(row["path"] == "/login" for row in fixture.state.requests),
                            "role_checks": sum(row["path"].startswith("/session/") for row in fixture.state.requests),
                            "cross_role_controls": len(boundary_checks),
                            "preflight_total": preflight_request_count,
                            "scanner_requests": len(scanner_request_rows),
                            "postflight_role_checks": 2},
                    })
    counts = {name: sum(1 for row in records if row["status"] == name)
              for name in ("completed", "error", "timeout", "incomplete")}
    return {
        "schema": "r4-local-comparison/3", "status": "partial-candidate-comparison",
        "summary": {"selected": len(records), **counts},
        "corpus_version": "r4-admin-stored-candidate/1",
        "cases": list(CASES), "repetitions": REPETITIONS,
        "order": {"rep-1": ["dxadyn", "dalfox"], "rep-2": ["dalfox", "dxadyn"]},
        "identity": dict(IDENTITY),
        "auth": {"scanner_input": "separate per-run writer and reader-admin login sessions",
                 "endpoint_role_binding": {"POST /comments": "writer_session",
                                           "GET /admin/comments": "admin_session"},
                 "pre_and_post_identity_checks": True, "cookie_values_recorded": False,
                 "preflight_requests_counted_in_same_fixture_budget": True},
        "budgets": {"requests_per_run": REQUEST_LIMIT, "rate_rps": RATE_LIMIT,
                    "concurrency": 1, "wall_seconds": WALL_LIMIT,
                    "outer_process_seconds": COMMAND_TIMEOUT, "dalfox_per_request_seconds": CLIENT_TIMEOUT,
                    "dxadyn_per_request_seconds": CLIENT_TIMEOUT},
        "runtime": {"python": platform.python_version(), "platform": platform.platform(),
                    "dalfox_version": DALFOX_VERSION, "dalfox_version_output": version, "dalfox_sha256": sha256(dalfox_path),
                    "dxadyn_sha256": sha256(DXADYN), "adapter_sha256": sha256(Path(__file__)),
                    "test_sha256": sha256(Path(__file__).with_name("test_r4_compare_local.py")),
                    "fixture_sha256": sha256(Path(__file__).with_name("r4_comparison_fixture.py"))},
        "results": records,
        "interpretation": {
            "candidate_only": True,
            "browser_execution_oracle": "reported separately by test_r4_comparison_fixture.py",
            "ranking": False,
            "coverage_gaps": [
                "candidate rows are not correlated to scanner-generated CIDs and must not be scored as execution TP/FP/FN",
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
