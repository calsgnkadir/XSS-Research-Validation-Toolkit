"""Require a completed static scan with high-confidence candidates in CI."""

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile


ANALYZER = Path(__file__).resolve().parents[1] / "tools" / "dom-xss-analyzer" / "dxa.py"


def validate_report(report, raw_findings):
    """Check the static report, without promoting candidates to XSS proof."""
    if not isinstance(report, dict) or report.get("schema_version") != 1 or report.get("mode") != "static":
        raise ValueError("expected a static v1 report")
    findings, events = report.get("findings"), report.get("events")
    if not isinstance(findings, list) or not findings or not isinstance(events, list):
        raise ValueError("expected findings and an events list")
    if not isinstance(raw_findings, list) or len(raw_findings) != len(findings):
        raise ValueError("stdout and report findings disagree")
    for finding, raw in zip(findings, raw_findings):
        if not isinstance(finding, dict) or not isinstance(raw, dict):
            raise ValueError("invalid finding")
        if (finding.get("evidence_level") != "candidate"
                or finding.get("confidence") != "high" or raw.get("confidence") != "high"
                or not finding.get("finding_id")):
            raise ValueError("expected identified high-confidence candidates")
        source, sink = finding.get("source"), finding.get("sink")
        if (not isinstance(source, dict) or not isinstance(sink, dict)
                or not raw.get("file") or not raw.get("sink")
                or type(raw.get("line")) is not int or raw["line"] < 1
                or source != {"file": raw["file"], "line": raw["line"]}
                or sink != {"file": raw["file"], "line": raw["line"], "identity": raw["sink"]}):
            raise ValueError("stdout and report source/sink disagree")
    for event in events:
        if not isinstance(event, dict) or event.get("kind") not in ("info", "skip"):
            raise ValueError("invalid or error event in scan report")
        # Confidence filtering is expected; discovery/read skips are incomplete scans.
        if event["kind"] == "skip" and event.get("stage") != "static-filter":
            raise ValueError("scan skipped input")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", type=Path, default=ANALYZER.parent / "examples")
    parser.add_argument("--analyzer", type=Path, default=ANALYZER)
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be finite and positive")
    try:
        # Every invocation gets a fresh path: an old report cannot pass a failed scan.
        with tempfile.TemporaryDirectory(prefix="dxa-self-scan-") as directory:
            output = Path(directory) / "report.json"
            result = subprocess.run(
                [sys.executable, str(args.analyzer), str(args.target),
                 "--min-confidence", "high", "--json", "--json-out", str(output)],
                capture_output=True, text=True, encoding="utf-8", timeout=args.timeout,
            )
            if result.returncode != 1:
                raise ValueError(f"expected finding exit 1, got {result.returncode}")
            # A traceback after writing findings must not be accepted as finding exit 1.
            if result.stderr.strip():
                raise ValueError("analyzer wrote diagnostic output to stderr")
            validate_report(json.loads(output.read_text(encoding="utf-8")),
                            json.loads(result.stdout))
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"Self-scan failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print("Self-scan completed with high-confidence static candidates (not execution proof).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
