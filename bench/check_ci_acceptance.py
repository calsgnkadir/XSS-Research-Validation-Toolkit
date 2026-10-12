"""Fail closed on the required R3/R4 CI artifacts, without running a scanner.

This checks recorded fixture execution, not vulnerability status or artifact
provenance. Run after pytest, the strict proof corpus and the demo succeed.
"""
import argparse
import json
import math
from pathlib import Path
import sys
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

import run as runner


REQUIRED_MODULES = {
    "test_browser_proof", "test_proof_cleanup", "test_proof_adapter", "test_proof_corpus",
}
POSITIVE = {"proof-raw", "proof-delayed", "proof-eval"}
CASE_IDS = POSITIVE | {
    "proof-fixed", "proof-json", "proof-dialog", "proof-title", "proof-textarea",
    "proof-resource-callback",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_junit(path):
    root = ET.parse(path).getroot()
    require(root.tag in ("testsuites", "testsuite"), "invalid JUnit root")
    cases = list(root.iter("testcase"))
    require(bool(cases), "JUnit contains no test cases")
    require(not any(list(root.iter(tag)) for tag in ("failure", "error", "skipped")),
            "JUnit contains failure, error or skipped cases")
    for suite in root.iter():
        if suite.tag not in ("testsuite", "testsuites"):
            continue
        for key in ("failures", "errors", "skipped"):
            require(int(suite.get(key, "0")) == 0, "JUnit has nonzero outcome counters")
        if "tests" in suite.attrib:
            require(int(suite.attrib["tests"]) == len(list(suite.iter("testcase"))),
                    "JUnit test count disagrees with recorded cases")
    modules = {case.get("classname", "").split(".")[-1] for case in cases}
    require(REQUIRED_MODULES <= modules, "JUnit lacks a required acceptance module")
    identities = [(c.get("classname"), c.get("name")) for c in cases]
    require(all(all(i) for i in identities) and len(set(identities)) == len(identities),
            "JUnit has missing or duplicate test identities")
    return len(cases)


def proof_origin(proof):
    url = proof["read_url"]
    parsed = urlsplit(url)
    require(parsed.scheme == "http" and parsed.hostname in ("127.0.0.1", "localhost", "::1")
            and not parsed.username and not parsed.password and parsed.path == "/comments"
            and not parsed.query and not parsed.fragment, "proof is not a loopback fixture read")
    return f"{parsed.scheme}://{parsed.netloc}"


def check_corpus(report):
    require(report["corpus_version"] == "loopback-proof/2"
            and report["scanners"] == ["dxaprove"], "unexpected corpus or scanner")
    rows = report["rows"]
    require(isinstance(rows, list) and len(rows) == len(CASE_IDS)
            and {row["id"] for row in rows} == CASE_IDS, "missing or duplicate corpus cases")
    targets = {target["id"]: target for target in runner.proof_corpus()["targets"]}
    wall = 0.0
    for row in rows:
        target = targets[row["id"]]
        positive = row["id"] in POSITIVE
        expected_ids = [target["case_id"]] if positive else []
        require(row["expected_ids"] == expected_ids
                and row["expected_identity"] == target["expected_identity"]
                and type(row["observe_ms"]) is int and row["observe_ms"] == 400,
                "corpus expected identity or window changed")
        result = row["results"]["dxaprove"]
        observed = runner.validate_proof_result(result["observed"])
        require(observed["status"] == "completed", "corpus case did not complete")
        adapted = runner.adapt_proof(target, observed["proof"], proof_origin(observed["proof"]),
                                     observed.get("fixture_observation"))
        require(adapted["status"] == "completed" and observed["findings"] == adapted["findings"],
                "corpus nested proof does not support observed findings")
        require(observed["proof"]["execution_observed"] is positive,
                "corpus execution disagrees with independent fixture label")
        require(result["score"] == {"tp": int(positive), "fp": 0, "fn": 0, "evaluated": True}
                and all(type(result["score"][key]) is int for key in ("tp", "fp", "fn"))
                and result["score"]["evaluated"] is True,
                "corpus case score disagrees with label")
        if not positive:
            require(observed.get("negative_window_completed") is True,
                    "negative fixture lacks completed observation window")
        wall += observed.get("wall", 0)
    totals = report["totals"]["dxaprove"]
    for key, expected in dict(tp=3, fp=0, fn=0, selected=9, completed=9,
                              skipped=0, error=0, timeout=0, invalid=0, inconclusive=0).items():
        require(type(totals.get(key)) is int and totals[key] == expected,
                "corpus totals disagree with required case outcomes")
    require(type(totals.get("wall")) in (int, float) and math.isfinite(totals["wall"])
            and math.isclose(totals["wall"], wall, abs_tol=0.01), "corpus wall total disagrees")


def check_demo(proof):
    target = {"case_id": "demo", "observe_ms": proof["observe_ms"], "mode": "raw"}
    adapted = runner.adapt_proof(target, proof, proof_origin(proof))
    require(adapted["status"] == "completed" and proof["execution_observed"] is True
            and bool(adapted["findings"]), "demo lacks matching browser execution")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--junit", required=True, type=Path)
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--demo", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        count = check_junit(args.junit)
        check_corpus(read_json(args.corpus))
        check_demo(read_json(args.demo))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ET.ParseError):
        # Artifact values may contain sensitive content; do not echo them.
        print("R3/R4 acceptance failed: missing, malformed or incomplete artifacts", file=sys.stderr)
        return 1
    print(f"R3/R4 acceptance passed: {count} tests, zero skips/errors; corpus 9/9 TP=3 FP=0 FN=0; demo execution observed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
