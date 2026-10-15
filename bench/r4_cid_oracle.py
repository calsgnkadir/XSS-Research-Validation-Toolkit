"""Strict correlation of scanner-submitted CIDs with stored reader browser proof."""
from __future__ import annotations

from collections import Counter
import ipaddress
import json
import re
from typing import Any, Iterable, Mapping
from urllib.parse import urlsplit

_CID_IN_QUERY = re.compile(r"[?&]cid=([A-Za-z0-9_-]{12,80})(?:[&#\"'\s]|$)", re.I)
_CID_IN_EXECUTION = re.compile(r"window\.__dxaProof\s*=\s*(['\"])([A-Za-z0-9_-]{12,80})\1", re.I)
_CID_SHAPE = re.compile(r"[A-Za-z0-9_-]{8,80}\Z")
_ALLOWED_RUN_STATES = {"completed", "error", "timeout", "skipped", "incomplete"}


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
