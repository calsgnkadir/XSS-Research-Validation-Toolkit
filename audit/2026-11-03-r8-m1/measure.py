"""Frozen intrinsic JSX candidate-presence study. No fixture code is executed.

Freeze before scanner edits; withhold evaluation details from the engine until
implementation freeze. These purposive cases are not a general accuracy test.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CASES_PATH = HERE / "cases.json"
MANIFEST_PATH = HERE / "split-manifest.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_cases(split="all"):
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]
    return [case for case in cases if split == "all" or case["split"] == split]


def identity(case):
    return {key: value for key, value in case.items() if key != "source"} | {
        "source_sha256": digest(case["source"].encode("utf-8"))}


def verify_manifest():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest["cases_sha256"] != digest(CASES_PATH.read_bytes()):
        raise RuntimeError("Frozen corpus bytes changed")
    if manifest["cases"] != [identity(case) for case in load_cases()]:
        raise RuntimeError("Frozen case identities changed")
    return manifest


def load_scanner(path):
    sys.path.insert(0, str(ROOT / "tools/dom-xss-analyzer"))
    spec = importlib.util.spec_from_file_location("m1_measured_scanner", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def observe(scanner, case, directory):
    path = directory / (case["id"] + "." + case["extension"])
    path.write_text(case["source"], encoding="utf-8")
    hits = [row for row in scanner.scan_file(str(path)) if row["sink"] == "jsx-href"]
    expected = case["expected_candidates"]
    actual = len(hits)
    outcome = ("TP" if actual else "FN") if expected else ("FP" if actual else "TN")
    properties_ok = actual == expected
    if expected and actual == 1:
        properties_ok = (hits[0]["line"] == case["expected_line"]
                         and hits[0]["confidence"] == case["expected_confidence"])
        if case["expected_confidence"] == "medium":
            properties_ok &= not hits[0]["sources"] and not hits[0]["tainted_vars"]
        else:
            properties_ok &= bool(hits[0]["sources"] or hits[0]["tainted_vars"])
    return identity(case) | {"status": "completed", "observed_candidates": actual,
             "outcome": outcome, "properties_ok": bool(properties_ok),
             "observations": [{"line": row["line"], "sink": row["sink"],
                               "confidence": row["confidence"]} for row in hits]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--split", choices=("all", "development", "evaluation", "boundary"), default="all")
    parser.add_argument("--scanner", type=Path, default=ROOT / "tools/dom-xss-analyzer/dxa.py")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.freeze:
        manifest = {"schema": "dxa-r8-m1-split/1", "base_commit": "220bbd2",
                    "meaning": "Intrinsic jsx-href review-candidate presence, not XSS labels",
                    "selection": json.loads(CASES_PATH.read_text(encoding="utf-8"))["selection"],
                    "evaluation_policy": "Withheld from engine until implementation freeze. Shared filesystem is not technical secrecy. Any evaluation-driven edits invalidate unseen-case status.",
                    "scanner_sha256_at_freeze": digest(args.scanner.read_bytes()),
                    "cases_sha256": digest(CASES_PATH.read_bytes()),
                    "cases": [identity(case) for case in load_cases()]}
        with MANIFEST_PATH.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(manifest, indent=2) + "\n")
        print(json.dumps({"frozen_cases": len(manifest["cases"]),
                          "manifest_sha256": digest(MANIFEST_PATH.read_bytes())}))
        return
    if args.out is None:
        parser.error("--out is required for measurement")
    verify_manifest()
    before = digest(args.scanner.read_bytes())
    scanner = load_scanner(args.scanner)
    rows = []
    with tempfile.TemporaryDirectory(prefix="dxa-m1-jsx-") as temp:
        for case in load_cases(args.split):
            try:
                rows.append(observe(scanner, case, Path(temp)))
            except Exception as exc:
                rows.append(identity(case) | {"status": "error", "reason": type(exc).__name__,
                            "observed_candidates": None, "outcome": None,
                            "properties_ok": False, "observations": []})
    if before != digest(args.scanner.read_bytes()):
        raise RuntimeError("Scanner changed during measurement")
    verify_manifest()
    counts = {}
    for split in ("development", "evaluation", "boundary"):
        selected = [row for row in rows if row["split"] == split]
        if not selected:
            continue
        counts[split] = {key: sum(row["outcome"] == key for row in selected)
                         for key in ("TP", "FP", "FN", "TN")}
        counts[split] |= {"completed": sum(row["status"] == "completed" for row in selected),
                          "errors": sum(row["status"] == "error" for row in selected),
                          "skips": 0, "timeouts": 0,
                          "candidates": sum(row["observed_candidates"] or 0 for row in selected),
                          "property_mismatches": sum(not row["properties_ok"] for row in selected)}
    result = {"meaning": "Intrinsic jsx-href review-candidate labels, not XSS/general accuracy",
              "split": args.split, "python": platform.python_version(),
              "scanner_sha256": before, "measure_sha256": digest(Path(__file__).read_bytes()),
              "manifest_sha256": digest(MANIFEST_PATH.read_bytes()),
              "counts": counts, "cases": rows}
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(counts))
    if any(value["errors"] for value in counts.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
