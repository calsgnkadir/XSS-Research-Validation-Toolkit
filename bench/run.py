"""Benchmark runner: dxadyn vs (opt-in) DalFox / XSStrike against a corpus.

Zero third-party dependencies. External scanners are auto-detected on PATH
and skipped cleanly if absent — so CI green-path runs on dxadyn alone.

Usage:
    python bench/run.py                       # full corpus, dxadyn only
    python bench/run.py --with dalfox         # add DalFox if on PATH
    python bench/run.py --with dalfox,xsstrike --out bench/results.md
    python bench/run.py --targets mock-reflected-easy,mock-stored-guestbook

Result: one Markdown report (default: bench/results-YYYY-MM-DD.md) plus a
history line appended to bench/history.jsonl (never lost across runs).
"""
from __future__ import annotations
import argparse
import datetime as _dt
import json
import hashlib
import platform
import os
import pathlib
import shutil
import subprocess
import sys
import time
from typing import Any, Callable, Dict, List

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
DXADYN = REPO / "tools" / "dom-xss-analyzer" / "dxadyn.py"

# ---------- corpus loading ----------

def load_corpus(path: pathlib.Path) -> Dict[str, Any]:
    with path.open() as fh:
        return json.load(fh)


# ---------- target lifecycle ----------

def start_mock(handler: str):
    """Bring up the stdlib mock server. Returns a context-manager wrapper."""
    sys.path.insert(0, str(HERE))
    from mock_target import MockServer  # noqa: E402
    return MockServer(port=0)


# ---------- Phase 7.0: docker target adapter --------------------------------
#
# For real OSS targets (Bludit / DVWA / WebGoat / Prestashop / ...) we spin
# up a docker-compose stack, wait for it to become reachable, run the scan,
# then tear it down. The adapter is opt-in - a runner without docker on
# PATH prints one line and skips the docker rows, so CI still passes.
#
# Contract: a docker target in targets.json looks like:
#   {"id": "bludit-3.16", "kind": "docker",
#    "compose_file": "bench/targets/bludit/docker-compose.yml",
#    "url": "http://127.0.0.1:8080/",
#    "ready_path": "/",
#    "expect": {"reflected": 0, "stored": 1, "dom": 0},
#    "budget_seconds": 120}

def _docker_available() -> bool:
    """Docker targets are opt-in: default runs (CI, dev) skip them and
    the report shows a `_note` so the operator knows nothing hung. Set
    `BENCH_ENABLE_DOCKER=1` in the environment to opt in - the sprint
    workflow does this explicitly on the operator's laptop where the
    daemon is up and image pulls are acceptable.

    Even when opted in, `docker` must be on PATH for the adapter to
    actually try; missing binary is a separate condition from opt-in."""
    if os.environ.get("BENCH_ENABLE_DOCKER", "").strip().lower() not in \
            ("1", "true", "yes", "on"):
        return False
    return shutil.which("docker") is not None


def _docker_compose_up(compose_file: str, timeout: int = 120) -> tuple[bool, str]:
    """Bring the stack up in detached mode. Returns (ok, msg)."""
    if not pathlib.Path(compose_file).is_file():
        return False, f"compose file not found: {compose_file}"
    try:
        proc = subprocess.run(
            ["docker", "compose", "-f", compose_file, "up", "-d"],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        if proc.returncode != 0:
            return False, (proc.stderr or proc.stdout or "unknown error")[-400:]
    except subprocess.TimeoutExpired:
        return False, f"docker compose up timed out after {timeout}s"
    except Exception as e:                                # noqa: BLE001
        return False, str(e)
    return True, "up"


def _docker_compose_down(compose_file: str, timeout: int = 60) -> None:
    """Best-effort teardown. A stuck container is the operator's problem;
    the runner never blocks longer than `timeout` on cleanup."""
    try:
        subprocess.run(
            ["docker", "compose", "-f", compose_file, "down", "-v"],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
    except Exception:                                    # noqa: BLE001
        pass


def _wait_for_http(url: str, deadline_s: float = 60) -> bool:
    """Poll the target URL until 2xx/3xx or the deadline expires."""
    import urllib.request
    end = time.time() + deadline_s
    while time.time() < end:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if 200 <= resp.status < 400:
                    return True
        except Exception:                                # noqa: BLE001
            pass
        time.sleep(2)
    return False


class DockerTarget:
    """Context manager wrapping docker-compose up/down around a scan."""

    def __init__(self, compose_file: str, ready_url: str, ready_timeout: int = 90):
        self.compose_file = compose_file
        self.ready_url = ready_url
        self.ready_timeout = ready_timeout
        self.up_ok = False

    def __enter__(self):
        ok, msg = _docker_compose_up(self.compose_file)
        self.up_ok = ok
        if not ok:
            self._up_msg = msg
            return self
        # Wait for HTTP readiness before handing control to the runner.
        if not _wait_for_http(self.ready_url, deadline_s=self.ready_timeout):
            self._up_msg = "container up but URL never became reachable"
            self.up_ok = False
        else:
            self._up_msg = "ready"
        return self

    def __exit__(self, *exc):
        _docker_compose_down(self.compose_file)


# ---------- scanner adapters ----------
# Each adapter returns a dict:
#   {"reflected": int, "stored": int, "dom": int, "wall": float, "ok": bool,
#    "raw_tail": str}

def run_dxadyn(target: Dict[str, Any], base_url: str, budget: int) -> Dict[str, Any]:
    url = target["url"].format(port=int(base_url.rsplit(":", 1)[1].split("/", 1)[0]))
    started = time.time()
    if target["expect"]["stored"] > 0:
        cmd = [
            sys.executable, str(DXADYN),
            "--stored", "--target", url,
            "--target-field", (target.get("params") or ["msg"])[0],
            "--auto-check",
            "--auto-check-from", url,
            "--auto-check-max", "5",
            "--csrf-field", target.get("csrf_field", "tokenCSRF"),
        ]
    else:
        # reflected mode: url as positional
        cmd = [sys.executable, str(DXADYN), url]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=budget, check=False,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "ok": False, "wall": time.time() - started}
    except OSError as exc:
        return {"status": "error", "ok": False, "reason": str(exc)}
    if proc.returncode not in (0, 1) or "Traceback (most recent call last)" in out:
        return {"status": "error", "ok": False, "returncode": proc.returncode,
                "wall": time.time() - started, "raw_tail": out[-400:]}
    return _parse_dxadyn(out, time.time() - started)


def _parse_dxadyn(out: str, wall: float) -> Dict[str, Any]:
    """Extract verdict counts from dxadyn stdout.

    dxadyn prints a summary line like:
      '1 reflected candidate(s) - 1 EXECUTABLE ...'
      '1 unique stored candidate(s) - 1 EXECUTABLE ...'
    and per-finding lines with '[EXECUTABLE]' or '[breakout-req]'.
    """
    import re
    reflected = 0
    stored = 0
    m = re.search(r"(\d+)\s+reflected candidate", out)
    if m:
        reflected = int(m.group(1))
    m = re.search(r"(\d+)\s+(?:unique\s+)?stored candidate", out)
    if m:
        stored = int(m.group(1))
    return {
        "reflected": reflected,
        "stored": stored,
        "dom": 0,  # Phase 2
        "wall": round(wall, 2),
        "ok": bool(re.search(r"candidate|No unencoded reflections|No stored", out)),
        "status": "completed" if re.search(r"candidate|No unencoded reflections|No stored", out) else "error",
        "measurement": "candidate-counts-not-confirmed-xss",
        "raw_tail": out[-400:],
    }


def run_dalfox(target: Dict[str, Any], base_url: str, budget: int) -> Dict[str, Any]:
    if not shutil.which("dalfox"):
        return {"skipped": "dalfox not on PATH"}
    url = target["url"].format(port=int(base_url.rsplit(":", 1)[1].split("/", 1)[0]))
    started = time.time()
    try:
        proc = subprocess.run(
            ["dalfox", "url", url, "--no-color", "--silence"],
            capture_output=True, text=True, timeout=budget, check=False,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "ok": False, "wall": time.time() - started}
    except OSError as exc:
        return {"status": "error", "ok": False, "reason": str(exc)}
    if proc.returncode != 0:
        return {"status": "error", "ok": False, "returncode": proc.returncode}
    lo = out.lower()
    return {
        "reflected": lo.count("[poc]") + lo.count("vuln"),
        "stored": 0,
        "dom": lo.count("dom"),
        "wall": round(time.time() - started, 2),
        "ok": True,
        "raw_tail": out[-400:],
    }


def run_xsstrike(target: Dict[str, Any], base_url: str, budget: int) -> Dict[str, Any]:
    if not shutil.which("xsstrike"):
        return {"skipped": "xsstrike not on PATH"}
    url = target["url"].format(port=int(base_url.rsplit(":", 1)[1].split("/", 1)[0]))
    started = time.time()
    try:
        proc = subprocess.run(
            ["xsstrike", "-u", url, "--skip"],
            capture_output=True, text=True, timeout=budget, check=False,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "ok": False, "wall": time.time() - started}
    except OSError as exc:
        return {"status": "error", "ok": False, "reason": str(exc)}
    if proc.returncode != 0:
        return {"status": "error", "ok": False, "returncode": proc.returncode}
    lo = out.lower()
    return {
        "reflected": lo.count("payload:") + lo.count("vulnerable"),
        "stored": 0,
        "dom": 0,
        "wall": round(time.time() - started, 2),
        "ok": True,
        "raw_tail": out[-400:],
    }


SCANNERS: Dict[str, Callable] = {
    "dxadyn": run_dxadyn,
    "dalfox": run_dalfox,
    "xsstrike": run_xsstrike,
}


def proof_corpus(browser_path=None):
    """Small versioned execution corpus, entirely in disposable loopback labs."""
    targets = []
    cases = (
        ("raw", True, "Raw HTML image onerror assigns the submitted canary."),
        ("fixed", False, "HTML encoding leaves the submitted image payload as text."),
        ("json", False, "An application/json response does not execute the submitted image markup."),
        ("dialog", False, "An ordinary application dialog never assigns the submitted canary."),
        ("delayed", True, "After 150 ms the submitted image enters innerHTML within the 400 ms window."),
        ("eval", True, "Native direct eval reads a function-local binding before inserting the submitted image."),
        ("title", False, "The image payload remains inert title RCDATA without a closing title tag."),
        ("textarea", False, "The image payload remains inert textarea RCDATA without a closing textarea tag."),
        ("resource-callback", False, "Escaped payload plus a handler-free image requests its CID URL; HTTP callback is not execution."),
    )
    for mode, executes, rationale in cases:
        identity = f"proof-v2:{mode}:POST:/comments:comment:/comments:reader"
        targets.append({"id": "proof-" + mode, "kind": "proof-lab", "mode": mode,
                        "case_id": identity, "expected_ids": [identity] if executes else [],
                        "expected_identity": {"method": "POST", "source_path": "/comments",
                                              "parameter": "comment", "read_path": "/comments", "role": "reader"},
                        "oracle_rationale": rationale, "observe_ms": 400,
                        "expect": {}, "browser_path": browser_path, "budget_seconds": 30})
    return {"corpus_version": "loopback-proof/2", "targets": targets}


def adapt_proof(target, proof, base_url, fixture_observation=None):
    """Validate producer evidence before assigning the stable fixture identity.

    Negative completion means only no matching canary in this labelled fixture's
    observation window. It is never a safe-target or vulnerability verdict.
    A completed window is scored independently of the expected label; a missed
    positive is FN. Producer inconclusive is retained in the nested proof.
    """
    observed = {"status": "invalid", "ok": False, "findings": [], "proof": proof,
                "measurement": "correlated-browser-execution-not-vulnerability"}
    if not isinstance(proof, dict):
        return observed
    if proof.get("status") == "error":
        observed["status"] = "error"
        return observed
    events, proofs = proof.get("events"), proof.get("proofs")
    if (not isinstance(events, list) or not all(isinstance(e, dict) for e in events)
            or not isinstance(proofs, list) or not all(isinstance(p, dict) for p in proofs)):
        return observed
    no_canary = any(e.get("stage") == "observe" and e.get("reason") == "no-canary-within-window"
                    and e.get("kind") == "info" for e in events)
    expected_url = base_url + "/comments"
    common = (proof.get("schema") == "dxa-browser-proof/1"
              and proof.get("http_session_checked") is True
              and proof.get("browser_session_checked") is True
              and proof.get("session_role") == "reader"
              and proof.get("source") == {"url": expected_url, "parameter": "comment", "method": "POST"}
              and proof.get("read_url") == expected_url
              and proof.get("read_status") == 200 and proof.get("submit_status") == 201
              and type(proof.get("observe_ms")) is int
              and proof["observe_ms"] == target.get("observe_ms", 400)
              and isinstance(proof.get("canary_id"), str) and bool(proof["canary_id"])
              and all(e.get("kind") == "info" for e in events))
    if not common:
        return observed
    if target.get("mode") == "resource-callback":
        hits = fixture_observation.get("resource_callback_hits", {}) if isinstance(fixture_observation, dict) else {}
        count = hits.get(proof["canary_id"], 0) if isinstance(hits, dict) else 0
        observed["callback_count"] = count if type(count) is int and count >= 0 else 0
        observed["callback_observed"] = observed["callback_count"] > 0
    if proof.get("status") == "execution-observed" and proof.get("execution_observed") is True:
        if no_canary or not proofs or any(p.get("canary_id") != proof["canary_id"]
                             or p.get("frame_url") != expected_url
                             or p.get("event") != "matching-browser-canary" for p in proofs):
            return observed
        observed.update(status="completed", ok=True, findings=[{
            "finding_id": target["case_id"], "evidence": "execution-observed",
            "canary_matched": True, "triage": "unreviewed"}])
    elif (proof.get("status") == "inconclusive" and proof.get("execution_observed") is False
          and not proofs and no_canary):
        if target.get("mode") == "resource-callback" and not observed["callback_observed"]:
            observed["reason"] = "resource-callback-not-observed"
            return observed
        observed["status"] = "completed"
        observed["ok"] = True
        observed["negative_window_completed"] = True
    return observed


def run_dxaprove(target):
    sys.path.insert(0, str(DXADYN.parent))
    import dxaprove
    from dxa_proof_lab import lab
    started = time.monotonic()
    with lab(target["mode"]) as (spec, state):
        spec["observe_ms"] = target["observe_ms"]
        proof = dxaprove.run(spec, target.get("browser_path"))
        fixture_observation = {"resource_callback_hits": dict(state["resource_callback_hits"])}
        result = adapt_proof(target, proof, spec["origin"], fixture_observation)
        result["fixture_observation"] = fixture_observation
    result["wall"] = round(time.monotonic() - started, 2)
    return result


# ---------- scoring ----------

def score(expected: Dict[str, int], observed: Dict[str, Any]) -> Dict[str, int]:
    if observation_status(observed) != "completed":
        return {"tp": 0, "fp": 0, "fn": 0}
    tp = fp = fn = 0
    for cls in ("reflected", "stored", "dom"):
        want = int(expected.get(cls, 0))
        got = int(observed.get(cls, 0))
        if want > 0 and got > 0:
            tp += min(want, got)
            fn += max(want - got, 0)
            if got > want:
                fp += got - want
        elif want == 0 and got > 0:
            fp += got
        elif want > 0 and got == 0:
            fn += want
    return {"tp": tp, "fp": fp, "fn": fn}


def observation_status(observed: Dict[str, Any]) -> str:
    if "skipped" in observed:
        return "skipped"
    return observed.get("status", "error" if observed.get("ok") is False else "completed")


def score_findings(expected_ids, findings, *, status="completed"):
    """Match stable corpus IDs, only for correlated browser execution evidence.

    IDs identify labelled source/sink/role cases, never random attempt canaries.
    Candidate/reflection/callback observations cannot count as execution TP.
    """
    if status != "completed":
        return {"tp": 0, "fp": 0, "fn": 0, "evaluated": False}
    expected = set(expected_ids)
    observed = {f["finding_id"] for f in findings
                if f.get("evidence") == "execution-observed" and f.get("canary_matched") is True}
    return {"tp": len(expected & observed), "fp": len(observed - expected),
            "fn": len(expected - observed), "evaluated": True}


def strict_failed(report):
    totals = report["totals"].get("dxaprove", report["totals"].get("dxadyn", {}))
    return not totals.get("completed") or any(totals.get(k, 0) for k in
        ("fp", "fn", "error", "timeout", "skipped", "invalid", "inconclusive"))


# ---------- runner ----------

def run_one(target: Dict[str, Any], scanners: List[str]) -> Dict[str, Any]:
    row: Dict[str, Any] = {"id": target["id"], "expect": target["expect"], "results": {}}
    budget = int(target.get("budget_seconds", 60))

    if target["kind"] == "proof-lab":
        if scanners != ["dxaprove"]:
            raise ValueError("cannot mix execution and candidate measurements")
        row["expected_ids"] = target["expected_ids"]
        row["expected_identity"] = target["expected_identity"]
        row["oracle_rationale"] = target["oracle_rationale"]
        row["observe_ms"] = target["observe_ms"]
        if "mode" not in target:
            raise KeyError("mode")
        started = time.monotonic()
        try:
            observed = run_dxaprove(target)
        except Exception as exc:
            # Preserve case coverage without exporting exception contents.
            status = "timeout" if isinstance(exc, (TimeoutError, subprocess.TimeoutExpired)) else "error"
            observed = {"status": status, "ok": False, "findings": [],
                        "reason": "proof-runner-" + status,
                        "wall": round(time.monotonic() - started, 2)}
        row["results"]["dxaprove"] = {"observed": observed, "score": score_findings(
            target["expected_ids"], observed["findings"], status=observed["status"])}
        return row

    if target["kind"] == "mock":
        with start_mock(target["handler"]) as srv:
            base_url = f"http://127.0.0.1:{srv.port}"
            for name in scanners:
                fn = SCANNERS[name]
                observed = fn(target, base_url, budget)
                row["results"][name] = {
                    "observed": observed,
                    "score": score(target["expect"], observed),
                }
        return row

    if target["kind"] == "docker":
        # Phase 7.0: real docker-composed target.
        if not _docker_available():
            row["results"]["_note"] = (
                "docker target skipped - set BENCH_ENABLE_DOCKER=1 and "
                "ensure docker is on PATH to opt in on your operator "
                "laptop; CI leaves these off by design")
            return row
        compose_file = target.get("compose_file")
        ready_url = target.get("url") or ""
        with DockerTarget(compose_file, ready_url,
                          ready_timeout=target.get("ready_timeout", 90)) as dt:
            if not dt.up_ok:
                row["results"]["_note"] = f"docker setup: {dt._up_msg}"
                for name in scanners:
                    row["results"][name] = {"observed": {"status": "error", "ok": False},
                                            "score": {"tp": 0, "fp": 0, "fn": 0}}
                return row
            # base_url is the target URL directly; the scanner adapters
            # split off the port from it just as they do for mock targets.
            base_url = ready_url.rstrip("/")
            for name in scanners:
                fn = SCANNERS[name]
                observed = fn(target, base_url, budget)
                row["results"][name] = {
                    "observed": observed,
                    "score": score(target["expect"], observed),
                }
        return row

    row["results"]["_note"] = f"kind={target['kind']} not runnable in this session"
    return row


def run_all(corpus: Dict[str, Any], scanners: List[str], only: List[str] | None) -> Dict[str, Any]:
    proof_mode = "dxaprove" in scanners
    if proof_mode and (scanners != ["dxaprove"] or any(t.get("kind") != "proof-lab" for t in corpus["targets"])):
        raise ValueError("cannot mix execution and candidate measurements")
    unknown = set(only or []) - {t['id'] for t in corpus['targets']}
    if unknown:
        raise ValueError(f"Unknown target IDs: {sorted(unknown)}")
    rows = []
    for tgt in corpus["targets"]:
        if only and tgt["id"] not in only:
            continue
        rows.append(run_one(tgt, scanners))
    totals = {s: dict(tp=0, fp=0, fn=0, wall=0.0, selected=len(rows),
                      completed=0, skipped=0, error=0, timeout=0, invalid=0, inconclusive=0) for s in scanners}
    for row in rows:
        for s in scanners:
            r = row["results"].get(s)
            if not r:
                totals[s]["skipped"] += 1
                continue
            status = observation_status(r["observed"])
            totals[s][status if status in ("completed", "skipped", "timeout", "invalid", "inconclusive") else "error"] += 1
            for k in ("tp", "fp", "fn"):
                totals[s][k] += r["score"][k]
            totals[s]["wall"] += float(r["observed"].get("wall", 0))
    return {
        "run_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "measurement": ("correlated-browser-execution; not confirmed vulnerability accuracy" if proof_mode
                        else "legacy-candidate-counts; not confirmed XSS accuracy"),
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        "runner_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
                        "scanner_sha256": hashlib.sha256((DXADYN.with_name("dxaprove.py") if proof_mode else DXADYN).read_bytes()).hexdigest(),
                        "fixture_sha256": hashlib.sha256((DXADYN.with_name("dxa_proof_lab.py") if proof_mode else HERE / "mock_target.py").read_bytes()).hexdigest(),
                        "corpus_sha256": hashlib.sha256(json.dumps(corpus, sort_keys=True).encode()).hexdigest()},
        "corpus_version": corpus.get("corpus_version", "?"),
        "scanners": scanners,
        "rows": rows,
        "totals": totals,
    }


# ---------- reporting ----------

def render_md(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# Benchmark run — {report['run_at']}")
    lines.append("")
    lines.append(f"- corpus: `{report['corpus_version']}`")
    lines.append(f"- scanners: {', '.join(report['scanners'])}")
    lines.append(f"- measurement: {report.get('measurement', 'unspecified')}")
    for name, total in report['totals'].items():
        lines.append(f"- {name} coverage: " + ', '.join(f"{key}={total.get(key, 0)}" for key in
                     ('selected', 'completed', 'skipped', 'error', 'timeout', 'invalid', 'inconclusive')))
    lines.append("")
    lines.append("## Totals")
    lines.append("")
    lines.append("| scanner | TP | FP | FN | wall (s) |")
    lines.append("|---|---:|---:|---:|---:|")
    for s, t in report["totals"].items():
        lines.append(f"| {s} | {t['tp']} | {t['fp']} | {t['fn']} | {round(t['wall'], 2)} |")
    lines.append("")
    lines.append("## Per-target")
    lines.append("")
    for row in report["rows"]:
        lines.append(f"### {row['id']}")
        exp = row["expect"]
        if "expected_ids" in row:
            lines.append(f"- expected execution case IDs: {row['expected_ids']}")
            lines.append(f"- expected identity: {json.dumps(row['expected_identity'], sort_keys=True)}")
            lines.append(f"- oracle: {row['oracle_rationale']}")
            lines.append(f"- observation window: {row['observe_ms']} ms")
        else:
            lines.append(f"- expected: reflected={exp.get('reflected', 0)} stored={exp.get('stored', 0)} dom={exp.get('dom', 0)}")
        for s, r in row["results"].items():
            if s.startswith("_"):
                lines.append(f"- {s}: {r}")
                continue
            obs = r.get("observed", {})
            sc = r.get("score", {})
            if "callback_count" in obs:
                lines.append(f"- matching resource callback count: {obs['callback_count']} (not JavaScript proof)")
            if observation_status(obs) != "completed":
                lines.append(f"- **{s}**: {observation_status(obs)} (not evaluated)")
            elif "findings" in obs:
                lines.append(f"- **{s}**: execution TP={sc['tp']} FP={sc['fp']} FN={sc['fn']}; "
                             f"negative window completed={obs.get('negative_window_completed', False)} ({obs.get('wall', 0)}s)")
            else:
                lines.append(
                    f"- **{s}**: reflected={obs.get('reflected', 0)} "
                    f"stored={obs.get('stored', 0)} dom={obs.get('dom', 0)} "
                    f"— TP={sc.get('tp', 0)} FP={sc.get('fp', 0)} FN={sc.get('fn', 0)} "
                    f"({obs.get('wall', 0)}s)"
                )
        lines.append("")
    return "\n".join(lines) + "\n"


def append_history(report: Dict[str, Any], history_path: pathlib.Path) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a") as fh:
        fh.write(json.dumps({
            "run_at": report["run_at"],
            "corpus_version": report["corpus_version"],
            "totals": report["totals"],
        }) + "\n")


# ---------- cli ----------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(HERE / "targets.json"))
    ap.add_argument("--with", dest="with_", default="", help="extra scanners, comma-separated: dalfox,xsstrike")
    ap.add_argument("--targets", default="", help="comma-separated target ids; empty = all")
    ap.add_argument("--out", default="")
    ap.add_argument("--proof-suite", action="store_true", help="isolated loopback execution corpus; no legacy candidate totals")
    ap.add_argument("--browser", help="Chrome/Chromium executable for --proof-suite")
    ap.add_argument("--no-history", action="store_true", help="do not append shared benchmark history")
    args = ap.parse_args()

    scanners = ["dxadyn"] + [s.strip() for s in args.with_.split(",") if s.strip()]
    only = [t.strip() for t in args.targets.split(",") if t.strip()] or None

    if args.proof_suite and args.with_:
        ap.error("--proof-suite cannot mix extra candidate scanners")
    if args.proof_suite:
        scanners = ["dxaprove"]
    corpus = proof_corpus(args.browser) if args.proof_suite else load_corpus(pathlib.Path(args.corpus))
    report = run_all(corpus, scanners, only)
    report["command"] = sys.argv

    out_path = pathlib.Path(args.out) if args.out else (HERE / f"results-{_dt.date.today().isoformat()}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_md(report), encoding="utf-8")
    out_path.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not args.no_history:
        append_history(report, HERE / "history.jsonl")

    totals = report["totals"]
    print(f"[bench] wrote {out_path}")
    for s, t in totals.items():
        print(f"  {s}: TP={t['tp']} FP={t['fp']} FN={t['fn']} wall={round(t['wall'], 2)}s")

    # regression gate: fail if dxadyn has any FN on the mock corpus
    return 1 if strict_failed(report) and os.environ.get("BENCH_STRICT") == "1" else 0


if __name__ == "__main__":
    raise SystemExit(main())
