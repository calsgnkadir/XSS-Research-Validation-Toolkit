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
    """Cheap check: is `docker` binary on PATH? We deliberately do NOT
    connect to the daemon here (that would slow every bench run); the
    subsequent `docker compose up` will surface a daemon-down error."""
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
        out = "<timeout>"
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
        "ok": True,
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
        out = "<timeout>"
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
        out = "<timeout>"
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


# ---------- scoring ----------

def score(expected: Dict[str, int], observed: Dict[str, Any]) -> Dict[str, int]:
    if "skipped" in observed:
        return {"tp": 0, "fp": 0, "fn": 0}
    tp = fp = fn = 0
    for cls in ("reflected", "stored", "dom"):
        want = int(expected.get(cls, 0))
        got = int(observed.get(cls, 0))
        if want > 0 and got > 0:
            tp += min(want, got)
            if got > want:
                fp += got - want
        elif want == 0 and got > 0:
            fp += got
        elif want > 0 and got == 0:
            fn += want
    return {"tp": tp, "fp": fp, "fn": fn}


# ---------- runner ----------

def run_one(target: Dict[str, Any], scanners: List[str]) -> Dict[str, Any]:
    row: Dict[str, Any] = {"id": target["id"], "expect": target["expect"], "results": {}}
    budget = int(target.get("budget_seconds", 60))

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
                "docker not on PATH - install docker or run this bench "
                "target outside CI")
            return row
        compose_file = target.get("compose_file")
        ready_url = target.get("url") or ""
        with DockerTarget(compose_file, ready_url,
                          ready_timeout=target.get("ready_timeout", 90)) as dt:
            if not dt.up_ok:
                row["results"]["_note"] = f"docker setup: {dt._up_msg}"
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
    rows = []
    for tgt in corpus["targets"]:
        if only and tgt["id"] not in only:
            continue
        rows.append(run_one(tgt, scanners))
    totals: Dict[str, Dict[str, int]] = {s: {"tp": 0, "fp": 0, "fn": 0, "wall": 0.0} for s in scanners}
    for row in rows:
        for s in scanners:
            r = row["results"].get(s)
            if not r or "_note" in row["results"]:
                continue
            for k in ("tp", "fp", "fn"):
                totals[s][k] += r["score"][k]
            totals[s]["wall"] += float(r["observed"].get("wall", 0))
    return {
        "run_at": _dt.datetime.utcnow().isoformat() + "Z",
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
        lines.append(f"- expected: reflected={exp.get('reflected', 0)} stored={exp.get('stored', 0)} dom={exp.get('dom', 0)}")
        for s, r in row["results"].items():
            if s.startswith("_"):
                lines.append(f"- {s}: {r}")
                continue
            obs = r.get("observed", {})
            sc = r.get("score", {})
            if "skipped" in obs:
                lines.append(f"- **{s}**: skipped ({obs['skipped']})")
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
    args = ap.parse_args()

    scanners = ["dxadyn"] + [s.strip() for s in args.with_.split(",") if s.strip()]
    only = [t.strip() for t in args.targets.split(",") if t.strip()] or None

    corpus = load_corpus(pathlib.Path(args.corpus))
    report = run_all(corpus, scanners, only)

    out_path = pathlib.Path(args.out) if args.out else (HERE / f"results-{_dt.date.today().isoformat()}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_md(report))
    append_history(report, HERE / "history.jsonl")

    totals = report["totals"]
    print(f"[bench] wrote {out_path}")
    for s, t in totals.items():
        print(f"  {s}: TP={t['tp']} FP={t['fp']} FN={t['fn']} wall={round(t['wall'], 2)}s")

    # regression gate: fail if dxadyn has any FN on the mock corpus
    dxadyn_fn = totals.get("dxadyn", {}).get("fn", 0)
    return 1 if dxadyn_fn > 0 and os.environ.get("BENCH_STRICT") == "1" else 0


if __name__ == "__main__":
    raise SystemExit(main())
