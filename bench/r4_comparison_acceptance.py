"""Independent accounting gate for bounded candidate comparisons, never accuracy."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

TOOLS = ("dxadyn", "dalfox")
CASES = {"r4-admin-stored/raw-admin-content": (False, True),
         "r4-admin-stored/escaped-admin-content": (True, False)}
IDENTITY = {"method": "POST", "source_path": "/comments", "parameter": "comment",
            "read_path": "/admin/comments", "role": "writer-to-reader-admin fixture broker"}
IDENTITY_V3 = {"method": "POST", "source_path": "/comments", "parameter": "comment",
               "read_path": "/admin/comments", "role": "writer-to-reader-admin",
               "role_verification": "separate fixture principals checked before and after each scan"}
STATES = ("completed", "error", "timeout", "incomplete", "skipped")
REDACTED_AUTH_MARKERS = {"<independent-writer-admin-session-pair>", "<writer-session>",
                         "<reader-admin-session>"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, name, *, integer=False, positive=False):
    require(type(value) in ((int,) if integer else (int, float)) and
            math.isfinite(value) and value >= (1 if positive else 0),
            f"invalid {name}")
    return value


def no_scores(value):
    if isinstance(value, dict):
        require(not ({"tp", "fp", "fn", "tn", "accuracy", "execution_observed",
                      "confirmed_vulnerability"} & value.keys()),
                "candidate manifest cannot contain execution or accuracy scores")
        for item in value.values():
            no_scores(item)
    elif isinstance(value, list):
        for item in value:
            no_scores(item)


def _artifact(entry, root):
    require(isinstance(entry, dict), "missing artifact binding")
    name = entry.get("path")
    require(isinstance(name, str) and name and "\\" not in name,
            "artifact path must be relative POSIX path")
    path = Path(name)
    require(not name.startswith("/") and not path.is_absolute() and ".." not in path.parts and ":" not in name,
            "unsafe artifact path")
    target = (root / path).resolve()
    require(target.is_relative_to(root.resolve()), "artifact escapes root")
    require(target.is_file(), "artifact missing")
    content = target.read_bytes()
    require(hashlib.sha256(content).hexdigest() == entry.get("sha256"),
            "artifact hash mismatch")
    return content


def _command_identity(command, tool):
    def option(name):
        require(command.count(name) == 1 and command.index(name) + 1 < len(command),
                "missing or duplicate command option: " + name)
        return command[command.index(name) + 1]
    origin = "http://127.0.0.1:<ephemeral-port>"
    if tool == "dxadyn":
        require("--stored" in command and option("--target") == origin + "/comments" and
                option("--target-field") == "comment" and option("--check") == origin + "/admin/comments",
                "command identity mismatch")
    else:
        require(len(command) > 2 and command[1:3] == ["scan", origin + "/comments"] and
                option("-X") == "POST" and option("-p") == "comment:body" and
                option("--sxss-url") == origin + "/admin/comments" and
                option("--sxss-method") == "GET", "command identity mismatch")


def _validate_v3_session_evidence(row):
    checks = row.get("session_checks")
    require(isinstance(checks, dict) and set(checks) == {"writer", "reader_admin",
                                                        "independent_tokens", "cookie_values_recorded"},
            "session evidence missing or malformed")
    require(checks.get("independent_tokens") is True and checks.get("cookie_values_recorded") is False,
            "independent credential evidence or redaction failed")
    for key, role in (("writer", "writer"), ("reader_admin", "reader-admin")):
        principal = checks[key]
        require(isinstance(principal, dict) and principal.get("role") == role
                and principal.get("pre") is True and principal.get("post") is True
                and isinstance(principal.get("principal_sha256"), str)
                and re.fullmatch(r"[0-9a-f]{64}", principal["principal_sha256"]),
                "pre/post role identity check failed")
    require(checks["writer"]["principal_sha256"] != checks["reader_admin"]["principal_sha256"],
            "writer and admin principal identities must be distinct")
    require(row.get("session_verified") is True, "scanner session was not verified")

    boundaries = row.get("role_boundary_checks")
    expected = {"writer_cannot_read_admin": (401, "GET", "/admin/comments"),
                "reader_admin_cannot_submit": (401, "POST", "/comments"),
                "admin_token_rejected_as_writer": (403, "GET", "/session/writer"),
                "writer_token_rejected_as_admin": (403, "GET", "/session/reader-admin")}
    require(isinstance(boundaries, dict) and set(boundaries) == set(expected),
            "four cross-role controls required")
    for name, (status, _method, _path) in expected.items():
        item = boundaries[name]
        require(isinstance(item, dict) and item.get("status") == status
                and item.get("expected_status") == status and item.get("passed") is True,
                "cross-role control did not pass: " + name)


def _validate_v3_request_trace(row, budgets):
    trace = row.get("request_trace")
    require(isinstance(trace, list), "schema v3 request trace missing")
    for item in trace:
        require(isinstance(item, dict)
                and set(item) == {"method", "path", "status", "budget_rejected"}
                and item.get("method") in {"GET", "POST", "HEAD"}
                and item.get("path") in {"/login", "/session/writer", "/session/reader-admin",
                                         "/comments", "/admin/comments"}
                and type(item.get("status")) is int and 100 <= item["status"] <= 599
                and type(item.get("budget_rejected")) is bool,
                "request trace contains invalid or sensitive fields")
    require(len(trace) == row.get("request_attempts"), "request trace length mismatch")
    statuses = [item["status"] for item in trace]
    require(statuses == row.get("http_statuses"), "request trace status mismatch")
    rejected = sum(item["budget_rejected"] for item in trace)
    require(rejected == row.get("budget_rejected_requests")
            and len(trace) - rejected == row.get("forwarded_requests"),
            "request trace budget accounting mismatch")
    require(len(trace) <= budgets["requests_per_run"]
            and row.get("request_attempts") == row.get("forwarded_requests") + rejected,
            "auth setup and scanner requests exceed common budget")
    require(not any(item["budget_rejected"] for item in trace)
            or row.get("budget_exceeded") is True, "budget rejection is not reflected in outcome")

    counts = row.get("fixture_request_counts")
    require(isinstance(counts, dict) and counts == {
        "login": 2,
        "role_checks": sum(item["path"].startswith("/session/") for item in trace),
        "cross_role_controls": 4,
        "preflight_total": 8,
        "scanner_requests": len(trace) - 10,
        "postflight_role_checks": 2,
    }, "fixture request category totals disagree with trace")
    require(len(trace) >= 10 and counts["scanner_requests"] >= 0,
            "request trace omits setup or postflight requests")
    preflight = trace[:8]
    expected_prefix = [("POST", "/login", 200), ("POST", "/login", 200),
                       ("GET", "/session/writer", 200), ("GET", "/session/reader-admin", 200),
                       ("GET", "/admin/comments", 401), ("POST", "/comments", 401),
                       ("GET", "/session/writer", 403), ("GET", "/session/reader-admin", 403)]
    require([(x["method"], x["path"], x["status"]) for x in preflight] == expected_prefix,
            "preflight role-control request trace mismatch")
    postflight = trace[-2:]
    require([(x["method"], x["path"], x["status"]) for x in postflight] == [
        ("GET", "/session/writer", 200), ("GET", "/session/reader-admin", 200)],
        "postflight identity request trace mismatch")
    scanner_trace = trace[8:-2]
    require(all(item["path"] in {"/comments", "/admin/comments"} for item in scanner_trace),
            "scanner request escaped the fixture endpoints")
    by_path = {path: sum(item["path"] == path for item in scanner_trace)
               for path in ("/comments", "/admin/comments")}
    require(row.get("scanner_requests_by_path") == by_path,
            "scanner endpoint counts disagree with request trace")


def _require_redacted_auth(text):
    for name in ("writer_session", "admin_session", "bridge"):
        for match in re.finditer(re.escape(name) + r"=([^\s;,'\"]+)", text, re.I):
            require(match.group(1) in REDACTED_AUTH_MARKERS,
                    "unredacted credential found in command, manifest or artifact")


def validate_comparison(document, artifact_root=None):
    """Return coverage, rejecting inconsistent claims. Files required only in artifact mode.

    A structurally valid incomplete run is accepted as incomplete evidence. This
    function deliberately has no ranking/TP/TN output, even for completed runs.
    Hashes bind supplied bytes, not independent authorship or authentic execution.
    """
    require(isinstance(document, dict), "manifest must be an object")
    no_scores(document)
    schema = document.get("schema")
    require(schema in ("r4-local-comparison/1", "r4-local-comparison/2", "r4-local-comparison/3"),
            "unsupported schema")
    if schema == "r4-local-comparison/2":
        require(artifact_root is not None, "v2 requires artifact verification")
    if schema == "r4-local-comparison/3":
        require(artifact_root is not None, "v3 requires artifact verification")
        _require_redacted_auth(json.dumps(document, sort_keys=True))
    require(document.get("corpus_version") == "r4-admin-stored-candidate/1", "wrong corpus")
    expected_identity = IDENTITY_V3 if schema.endswith("/3") else IDENTITY
    require(document.get("identity") == expected_identity, "identity mismatch")
    cases = document.get("cases")
    require(isinstance(cases, list) and len(cases) == len(CASES), "case coverage mismatch")
    require(all(isinstance(c, dict) for c in cases), "invalid case object")
    require({c.get("id") for c in cases} == set(CASES), "case identity mismatch")
    for case in cases:
        escaped, expected = CASES[case["id"]]
        require(case.get("escaped") is escaped and case.get("expected_execution") is expected,
                "case oracle mismatch")
    require(document.get("repetitions") == 2 and type(document["repetitions"]) is int,
            "two repetitions required")
    order = {"rep-1": ["dxadyn", "dalfox"], "rep-2": ["dalfox", "dxadyn"]}
    require(document.get("order") == order, "run order mismatch")
    interpretation = document.get("interpretation", {})
    require(isinstance(interpretation, dict), "invalid interpretation")
    require(interpretation.get("candidate_only") is True and interpretation.get("ranking") is False,
            "candidate-only interpretation required")
    auth = document.get("auth", {})
    require(isinstance(auth, dict), "invalid auth")
    if schema.endswith("/3"):
        require(auth.get("scanner_input") == "separate per-run writer and reader-admin login sessions"
                and auth.get("endpoint_role_binding") == {"POST /comments": "writer_session",
                                                            "GET /admin/comments": "admin_session"}
                and auth.get("pre_and_post_identity_checks") is True
                and auth.get("cookie_values_recorded") is False
                and auth.get("preflight_requests_counted_in_same_fixture_budget") is True,
                "authenticated scanner session contract overstated")
    else:
        require(auth.get("real_login_coverage") is False and
                auth.get("brokered_roles") == ["writer", "reader-admin"], "broker auth overstated")
    budgets = document.get("budgets", {})
    require(isinstance(budgets, dict), "invalid budgets")
    mapping = {"request_limit": "requests_per_run", "rate_limit_rps": "rate_rps",
               "wall_limit_seconds": "wall_seconds", "command_timeout_seconds": "outer_process_seconds"}
    for key in (*mapping.values(), "concurrency", "dalfox_per_request_seconds", "dxadyn_per_request_seconds"):
        number(budgets.get(key), key, positive=True)
    require(budgets["concurrency"] == 1, "serial comparison required")
    if schema.endswith(("/2", "/3")):
        require(budgets["dalfox_per_request_seconds"] == budgets["dxadyn_per_request_seconds"],
                "client timeout mismatch")
    runtime = document.get("runtime", {})
    require(isinstance(runtime, dict), "invalid runtime")
    for key in ("dalfox_sha256", "dxadyn_sha256", "adapter_sha256", "test_sha256", "fixture_sha256"):
        require(isinstance(runtime.get(key), str) and re.fullmatch(r"[0-9a-f]{64}", runtime[key]),
                "missing runtime hash: " + key)
    for key in ("python", "platform", "dalfox_version"):
        require(isinstance(runtime.get(key), str) and runtime[key].strip(), "missing runtime: " + key)
    require(runtime["dalfox_version"] == "3.2.4", "unsupported Dalfox exit contract")
    rows = document.get("results")
    require(isinstance(rows, list), "results missing")
    seen = set()
    counts = dict.fromkeys(STATES, 0)
    for row in rows:
        require(isinstance(row, dict), "invalid result row")
        identity = (row.get("case_id"), row.get("repetition"), row.get("tool"))
        require(identity[0] in CASES and type(identity[1]) is int and identity[1] in (1, 2)
                and identity[2] in TOOLS and identity not in seen, "duplicate or unknown run identity")
        seen.add(identity)
        require(row.get("identity", expected_identity if schema.endswith("/1") else None) == expected_identity,
                "row identity mismatch")
        require(row.get("expected_execution") is CASES[identity[0]][1], "row oracle mismatch")
        require(type(row.get("order_index")) is int and
                row["order_index"] == order[f"rep-{identity[1]}"].index(identity[2]), "row order mismatch")
        require(type(row.get("selected")) is int and row["selected"] == 1, "selected must equal one")
        state = row.get("status")
        require(state in STATES, "unknown status")
        for flag in ("completed", "error", "timeout"):
            require(row.get(flag) is (state == flag), "status flag mismatch")
        for flag in ("timed_out", "budget_exceeded"):
            require(type(row.get(flag)) is bool, "invalid boolean: " + flag)
        for key, budget in mapping.items():
            number(row.get(key), key, positive=True)
            require(row[key] == budgets[budget], "row budget mismatch")
        if schema.endswith(("/2", "/3")):
            number(row.get("per_request_timeout_seconds"), "per_request_timeout_seconds", positive=True)
            require(row["per_request_timeout_seconds"] == budgets[identity[2] + "_per_request_seconds"],
                    "row client timeout mismatch")
        for key in ("request_attempts", "forwarded_requests", "budget_rejected_requests", "max_inflight"):
            number(row.get(key), key, integer=True)
        require(row["request_attempts"] == row["forwarded_requests"] + row["budget_rejected_requests"],
                "request accounting mismatch")
        require(row["forwarded_requests"] <= budgets["requests_per_run"] and
                row["max_inflight"] <= budgets["concurrency"], "hard budget violated")
        require(not row["budget_rejected_requests"] or row["budget_exceeded"], "rejections require exceeded flag")
        statuses = row.get("http_statuses")
        require(isinstance(statuses, list) and len(statuses) == row["request_attempts"] and
                all(type(s) is int and 100 <= s <= 599 for s in statuses), "HTTP accounting mismatch")
        wall = number(row.get("wall_seconds"), "wall_seconds")
        count = row.get("candidate_count")
        if count is not None:
            number(count, "candidate_count", integer=True)
        require(row.get("candidate_observed") is (None if count is None else count > 0),
                "candidate count mismatch")
        code = row.get("return_code")
        require(code is None or type(code) is int, "invalid return code")
        if state == "skipped" and schema.endswith("/3"):
            require(code is None and not row["timed_out"] and count is None
                    and row.get("skip_reason"), "invalid skipped run")
        elif state == "skipped":
            require(code is None and not row["timed_out"] and count is None and
                    row["request_attempts"] == 0 and row.get("skip_reason"), "invalid skipped run")
        else:
            # Both dxadyn and pinned Dalfox 3.2.4 document exit 1 for findings.
            expected_state = ("timeout" if row["timed_out"] else "error" if code not in (0, 1) else
                              "incomplete" if row["budget_exceeded"] or count is None or
                              wall > budgets["wall_seconds"] else "error" if code == 1 and count == 0
                              else "completed")
            require(state == expected_state, "run classification mismatch")
        require(isinstance(row.get("safe_command"), list) and row["safe_command"] and
                all(isinstance(x, str) for x in row["safe_command"]), "command provenance missing")
        _command_identity(row["safe_command"], identity[2])
        if schema.endswith("/3"):
            cookie_option = "--cookie" if identity[2] == "dxadyn" else "--cookies"
            require(row["safe_command"].count(cookie_option) == 1
                    and row["safe_command"].index(cookie_option) + 1 < len(row["safe_command"])
                    and row["safe_command"][row["safe_command"].index(cookie_option) + 1]
                    == "<independent-writer-admin-session-pair>",
                    "scanner command does not contain only the redacted independent session pair")
        if artifact_root is not None:
            evidence = row.get("artifacts", {})
            require(isinstance(evidence, dict), "invalid artifact bindings")
            _artifact(evidence.get("stdout"), Path(artifact_root))
            _artifact(evidence.get("stderr"), Path(artifact_root))
            report = evidence.get("report")
            require(report is not None or count is None, "candidate report missing")
            if report is not None:
                raw = _artifact(report, Path(artifact_root))
                try:
                    parsed = json.loads(raw)
                except (ValueError, UnicodeError):
                    parsed = None
                findings = (parsed if schema.endswith("/1") and identity[2] == "dalfox"
                            and isinstance(parsed, list) else None)
                if isinstance(parsed, dict):
                    keys = (("findings",) if schema.endswith(("/2", "/3")) or identity[2] == "dxadyn"
                            else ("data", "findings", "issues", "results"))
                    findings = next((parsed[k] for k in keys if isinstance(parsed.get(k), list)), None)
                    if identity[2] == "dalfox":
                        meta = parsed.get("meta", {})
                        require(isinstance(meta, dict), "invalid Dalfox metadata")
                        failed = meta.get("failed_requests", 0)
                        number(failed, "Dalfox failed_requests", integer=True)
                        require(type(meta.get("incomplete", False)) is bool, "invalid Dalfox incomplete flag")
                        if meta.get("incomplete") is not False or "failed_requests" not in meta or failed or \
                                type(meta.get("findings_count")) is not int or findings is None or \
                                meta["findings_count"] != len(findings):
                            findings = None
                    else:
                        events = parsed.get("events", [])
                        require(isinstance(events, list) and all(isinstance(e, dict) for e in events),
                                "invalid scanner events")
                        skipped = parsed.get("skipped_submits", 0)
                        number(skipped, "skipped_submits", integer=True)
                        if skipped or any(e.get("kind") in ("error", "skip") for e in events):
                            findings = None
                if findings is not None and not all(isinstance(finding, dict) for finding in findings):
                    findings = None
                require(count == (len(findings) if findings is not None else None), "artifact candidate count mismatch")
            if schema.endswith("/3"):
                for label, entry in evidence.items():
                    if entry is not None:
                        raw = _artifact(entry, Path(artifact_root))
                        _require_redacted_auth(raw.decode("utf-8", "replace"))
                _validate_v3_session_evidence(row)
                _validate_v3_request_trace(row, budgets)
        elif schema.endswith("/3"):
            _validate_v3_session_evidence(row)
            _validate_v3_request_trace(row, budgets)
        if schema.endswith("/3"):
            _require_redacted_auth(json.dumps(row, sort_keys=True))
        counts[state] += 1
    require(len(seen) == 8, "selected coverage incomplete")
    summary = document.get("summary", {})
    require(isinstance(summary, dict), "invalid summary")
    require(type(summary.get("selected")) is int and summary["selected"] == len(seen), "selected total mismatch")
    for state, value in counts.items():
        observed = summary.get(state, 0 if state == "skipped" else None)
        require(type(observed) is int and observed == value, "summary total mismatch: " + state)
    return {"selected": len(seen), **counts, "candidate_only": True, "ranking": False,
            "artifacts_verified": artifact_root is not None,
            "equal_client_timeouts": budgets["dalfox_per_request_seconds"] == budgets["dxadyn_per_request_seconds"],
            "authenticated_sessions_verified": schema.endswith("/3"),
            "request_traces_verified": schema.endswith("/3")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--artifacts", type=Path, help="verify bound files under this directory")
    args = parser.parse_args()
    try:
        result = validate_comparison(json.loads(args.manifest.read_text(encoding="utf-8")), args.artifacts)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        parser.exit(2, f"comparison rejected: {exc}\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
