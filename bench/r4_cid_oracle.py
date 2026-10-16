"""Strict correlation of scanner-submitted CIDs with stored reader browser proof."""
from __future__ import annotations

from collections import Counter
import hashlib
import ipaddress
import json
import re
from typing import Any, Iterable, Mapping
import urllib.parse
import urllib.request
from urllib.parse import urlsplit

_CID_IN_QUERY = re.compile(r"[?&]cid=([A-Za-z0-9_-]{12,80})(?:[&#\"'\s]|$)", re.I)
_CID_IN_EXECUTION = re.compile(r"window\.__dxaProof\s*=\s*(['\"])([A-Za-z0-9_-]{12,80})\1", re.I)
_CID_SHAPE = re.compile(r"[A-Za-z0-9_-]{8,80}\Z")
_ALLOWED_RUN_STATES = {"completed", "error", "timeout", "skipped", "incomplete"}
_DXA_STORED_CID = re.compile(r"dxa[0-9a-f]{8}\Z")


def _extract_payload_cid(payload: str) -> str | None:
    """Require the same CID in a resource URL and active JS proof assignment."""
    if not isinstance(payload, str):
        return None
    query_ids = {m.group(1) for m in _CID_IN_QUERY.finditer(payload)}
    execution_ids = {m.group(2) for m in _CID_IN_EXECUTION.finditer(payload)}
    if len(query_ids) != 1 or len(execution_ids) != 1 or query_ids != execution_ids:
        return None
    return next(iter(query_ids))


def _valid_observation(row: Any, case_id: str) -> bool:
    return (
        isinstance(row, Mapping) and row.get("case_id") == case_id
        and row.get("read_path") == "/admin/comments"
        and row.get("role") == "reader-admin" and row.get("role_verified") is True
        and row.get("status") in {"execution-observed", "completed-no-execution"}
        and row.get("window_completed") is True and type(row.get("execution_observed")) is bool
        and ((row.get("status") == "execution-observed") == row.get("execution_observed"))
        and row.get("timed_out") is not True
        and isinstance(row.get("canary_id"), str) and bool(row["canary_id"])
    )


def evaluate_correlation(case_id: str, run_status: str, submitted_payloads: Iterable[str],
                         browser_observations: Iterable[Mapping[str, Any]], *,
                         escaped: bool) -> dict[str, Any]:
    """Correlate exact post-scan stored strings with separate reader-browser proof.

    `submitted_payloads` must come from fixture storage readback, never scanner
    labels/stdout. Browser rows must come from `observe_reader_admin`. Missing
    or malformed scanner CIDs are inconclusive; incomplete runs are not negative.
    """
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("case_id must be a non-empty string")
    if run_status not in _ALLOWED_RUN_STATES:
        raise ValueError("unsupported scanner run status")
    payloads, observations = list(submitted_payloads), list(browser_observations)
    if not all(isinstance(payload, str) for payload in payloads):
        raise TypeError("submitted_payloads must contain strings")
    payload_cids = [_extract_payload_cid(payload) for payload in payloads]
    malformed_count = sum(cid is None for cid in payload_cids)
    counts = Counter(cid for cid in payload_cids if cid is not None)
    candidate_cids = sorted(counts)
    duplicate_candidates = sorted(cid for cid, count in counts.items() if count > 1)
    eligible = [row for row in observations if _valid_observation(row, case_id)]
    executed = [row for row in eligible if row["execution_observed"]]
    observed_cids = sorted({row["canary_id"] for row in executed})
    duplicate_observations = sorted(cid for cid, count in Counter(
        row["canary_id"] for row in executed).items() if count > 1)
    matched = sorted(set(candidate_cids) & set(observed_cids))
    unrelated = sorted(set(observed_cids) - set(candidate_cids))
    completed_windows = {row["canary_id"] for row in eligible
                         if row["status"] == "completed-no-execution"}
    rejected_claim = any(isinstance(row, Mapping) and row.get("execution_observed") is True
                         and not _valid_observation(row, case_id) for row in observations)
    timed_out = run_status == "timeout" or any(
        isinstance(row, Mapping) and row.get("timed_out") is True for row in observations)

    if timed_out:
        outcome = "timeout"
    elif run_status in {"error", "skipped", "incomplete"}:
        outcome = run_status
    elif not candidate_cids or malformed_count:
        outcome = "inconclusive"
    elif rejected_claim:
        outcome = "inconclusive"
    elif escaped:
        if matched:
            outcome = "failed-negative-control"
        elif unrelated:
            outcome = "inconclusive"
        elif not set(candidate_cids).issubset(completed_windows):
            outcome = "inconclusive"
        else:
            outcome = "completed-negative"
    elif matched:
        outcome = "execution-correlated"
    elif unrelated or not set(candidate_cids).issubset(completed_windows):
        outcome = "inconclusive"
    else:
        outcome = "completed-no-matching-execution"

    return {
        "schema": "r4-cid-browser-correlation/1", "case_id": case_id,
        "run_status": run_status, "outcome": outcome, "escaped": bool(escaped),
        "selected": 1, "completed": outcome in {"execution-correlated", "completed-negative",
                                                   "completed-no-matching-execution", "failed-negative-control"},
        "candidate_cids": candidate_cids, "matched_cids": matched,
        "unrelated_execution_cids": unrelated,
        "duplicate_candidate_cids": duplicate_candidates,
        "duplicate_observation_cids": duplicate_observations,
        "malformed_payload_count": malformed_count,
        "observed_execution_count": len(observed_cids),
        "completed_browser_window_cids": sorted(completed_windows),
        "execution_observed": bool(matched), "expected_execution": not escaped,
        "timed_out": timed_out,
    }


def _loopback_origin(origin: str) -> str:
    parsed = urlsplit(origin)
    if parsed.scheme != "http" or parsed.username or parsed.password or not parsed.hostname:
        raise ValueError("oracle requires a plain HTTP loopback origin")
    try:
        is_loopback = parsed.hostname.lower() == "localhost" or ipaddress.ip_address(parsed.hostname).is_loopback
    except ValueError:
        is_loopback = False
    if not is_loopback or parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("oracle requires a plain HTTP loopback origin")
    return f"http://{parsed.netloc}"


def observe_reader_admin(origin: str, case_id: str, reader_token: str,
                         candidate_cids: Iterable[str], *, browser_path: str | None = None,
                         observe_ms: int = 750) -> list[dict[str, Any]]:
    """Use an isolated Playwright context to check role then observe the stored page.

    The raw reader token exists only as an HttpOnly cookie in memory. The helper
    observes `window.__dxaProof`; it never creates, evaluates, or injects a canary.
    Only loopback HTTP fixture origins are accepted.
    """
    safe_origin = _loopback_origin(origin)
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("case_id must be a non-empty string")
    if not isinstance(reader_token, str) or not reader_token:
        raise ValueError("reader token is required")
    if type(observe_ms) is not int or not 100 <= observe_ms <= 10_000:
        raise ValueError("observe_ms must be between 100 and 10000")
    cids = list(dict.fromkeys(candidate_cids))
    if not cids or any(not isinstance(cid, str) or not _CID_SHAPE.fullmatch(cid) for cid in cids):
        raise ValueError("candidate CIDs must be non-empty opaque identifiers")

    from playwright.sync_api import sync_playwright
    rows: list[dict[str, Any]] = []
    with sync_playwright() as playwright:
        options: dict[str, Any] = {"headless": True}
        if browser_path:
            options["executable_path"] = browser_path
        browser = playwright.chromium.launch(**options)
        try:
            context = browser.new_context()
            context.add_cookies([{"name": "admin_session", "value": reader_token,
                                  "url": safe_origin, "httpOnly": True, "sameSite": "Strict"}])
            page = context.new_page()
            check = page.goto(safe_origin + "/session/reader-admin", wait_until="load", timeout=5000)
            try:
                identity = check.json() if check and check.status == 200 else None
            except Exception:
                identity = None
            verified = identity == {"principal": "reader-admin", "role": "reader-admin"}
            if not verified:
                return [{"case_id": case_id, "read_path": "/admin/comments", "principal": None,
                         "role": None, "role_verified": False, "status": "error",
                         "execution_observed": False, "timed_out": False,
                         "window_completed": False, "canary_id": cid} for cid in cids]
            read = page.goto(safe_origin + "/admin/comments", wait_until="load", timeout=5000)
            if read is None or read.status != 200:
                return [{"case_id": case_id, "read_path": "/admin/comments", "principal": "reader-admin",
                         "role": "reader-admin", "role_verified": True, "status": "error",
                         "execution_observed": False, "timed_out": False,
                         "window_completed": False, "canary_id": cid} for cid in cids]
            for cid in cids:
                elapsed, observed = 0, False
                while elapsed < observe_ms:
                    observed = page.evaluate("() => window.__dxaProof || null") == cid
                    if observed:
                        break
                    step = min(25, observe_ms - elapsed)
                    page.wait_for_timeout(step)
                    elapsed += step
                rows.append({"case_id": case_id, "read_path": "/admin/comments",
                             "principal": "reader-admin", "role": "reader-admin",
                             "role_verified": True,
                             "status": "execution-observed" if observed else "completed-no-execution",
                             "execution_observed": observed, "timed_out": False,
                             "window_completed": True, "canary_id": cid})
            context.close()
        finally:
            browser.close()
    return rows


def match_reported_payloads(tool: str, findings: Iterable[Mapping[str, Any]],
                            stored_payloads: Iterable[str]) -> list[str]:
    """Find exact submitted bytes behind a scanner report, without trusting labels.

    Dalfox v3 exposes its submitted payload. dxadyn exposes the stored canary ID;
    its exact string is recovered only when fixture readback has one prefix match.
    Missing or ambiguous matches are left out of the proof experiment.
    """
    stored = list(stored_payloads)
    if not all(isinstance(value, str) for value in stored):
        raise TypeError("stored payloads must be strings")
    matches = []
    for row in findings:
        if not isinstance(row, Mapping):
            continue
        if tool == "dalfox":
            value = row.get("payload")
            if isinstance(value, str) and stored.count(value) == 1 and value not in matches:
                matches.append(value)
        elif tool == "dxadyn":
            cid = row.get("canary_id")
            if isinstance(cid, str) and _DXA_STORED_CID.fullmatch(cid):
                candidates = [value for value in stored if value.startswith(cid)]
                if len(candidates) == 1 and candidates[0] not in matches:
                    matches.append(candidates[0])
    return matches


def observe_exact_payload_replay(payload: str, *, browser_path: str | None = None,
                                 observe_ms: int = 500) -> dict[str, Any]:
    """Replay exact fixture-readback bytes in isolated raw and escaped loopback labs.

    This is evidence about the scanner's submitted payload shape, not an
    observation of its original request. Each replay has one stored string,
    a verified reader-admin identity, and a completed browser window. Dialogs
    are observed and dismissed; the observer adds no script to the page.
    """
    if not isinstance(payload, str) or not payload or len(payload.encode("utf-8")) > 16_384:
        raise ValueError("payload must be a bounded non-empty string")
    if type(observe_ms) is not int or not 100 <= observe_ms <= 10_000:
        raise ValueError("observe_ms must be between 100 and 10000")
    from playwright.sync_api import sync_playwright
    from r4_comparison_fixture import R4ComparisonFixture

    rows: dict[str, dict[str, Any]] = {}
    with sync_playwright() as playwright:
        options: dict[str, Any] = {"headless": True}
        if browser_path:
            options["executable_path"] = browser_path
        browser = playwright.chromium.launch(**options)
        try:
            for escaped in (False, True):
                label = "escaped" if escaped else "raw"
                with R4ComparisonFixture(escaped=escaped, request_limit=20,
                                         rate_limit=50, wall_limit=30) as fixture:
                    _, writer = fixture.login("writer")
                    _, reader = fixture.login("reader-admin")
                    body = urllib.parse.urlencode({"comment": payload}).encode("utf-8")
                    request = urllib.request.Request(
                        fixture.origin + "/comments", data=body, method="POST",
                        headers={"Cookie": f"writer_session={writer}"})
                    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                    with opener.open(request, timeout=5) as response:
                        submitted = response.status == 200
                    if not submitted or fixture.stored_comments() != [payload]:
                        rows[label] = {"status": "error", "reason": "storage-mismatch"}
                        continue
                    context = browser.new_context(service_workers="block")
                    try:
                        blocked_external: list[str] = []

                        def route_loopback_only(route):
                            target = urlsplit(route.request.url)
                            if f"{target.scheme}://{target.netloc}" == fixture.origin:
                                route.continue_()
                            else:
                                blocked_external.append(target.scheme)
                                route.abort()

                        context.route("**/*", route_loopback_only)
                        context.add_cookies([{"name": "admin_session", "value": reader,
                                              "url": fixture.origin, "httpOnly": True,
                                              "sameSite": "Strict"}])
                        page = context.new_page()
                        check = page.goto(fixture.origin + "/session/reader-admin",
                                          wait_until="load", timeout=5000)
                        try:
                            verified = check is not None and check.status == 200 and check.json() == {
                                "principal": "reader-admin", "role": "reader-admin"}
                        except Exception:
                            verified = False
                        if not verified:
                            rows[label] = {"status": "error", "reason": "reader-role-check"}
                            continue
                        dialogs = []
                        def on_dialog(dialog):
                            dialogs.append(dialog.type)
                            dialog.dismiss()
                        page.on("dialog", on_dialog)
                        read = page.goto(fixture.origin + "/admin/comments",
                                         wait_until="load", timeout=5000)
                        if read is None or read.status != 200:
                            rows[label] = {"status": "error", "reason": "reader-http"}
                            continue
                        page.wait_for_timeout(observe_ms)
                        rows[label] = {"status": "completed", "role_verified": True,
                                       "dialog_observed": "alert" in dialogs,
                                       "dialog_count": len(dialogs),
                                       "external_http_blocked": len(blocked_external),
                                       "request_attempts": len(fixture.state.requests),
                                       "budget_exceeded": fixture.state.budget_exceeded}
                    finally:
                        context.close()
        finally:
            browser.close()
    raw, escaped = rows.get("raw", {}), rows.get("escaped", {})
    completed = all(row.get("status") == "completed" and row.get("role_verified") is True
                    and row.get("budget_exceeded") is False for row in (raw, escaped))
    raw_dialog = raw.get("dialog_observed") is True
    escaped_dialog = escaped.get("dialog_observed") is True
    outcome = ("inconclusive" if not completed else
               "failed-negative-control" if escaped_dialog else
               "exact-payload-replay-execution" if raw_dialog else "inconclusive")
    return {"schema": "r4-exact-payload-replay/1", "payload_sha256": hashlib.sha256(
                payload.encode("utf-8")).hexdigest(), "outcome": outcome,
            "raw_dialog_observed": raw_dialog, "escaped_dialog_observed": escaped_dialog,
            "raw": raw, "escaped": escaped,
            "original_scanner_request_observed_in_browser": False}
