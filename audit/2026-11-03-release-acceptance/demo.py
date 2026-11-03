"""Repeat frozen JSX candidate-presence cases on pinned scanner revisions.

No checkout, application, browser or JSX execution; local Git history required.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "audit/2026-11-03-r8-m1"
SCANNER = "tools/dom-xss-analyzer/dxa.py"
REVISIONS = {
    "before": ("220bbd2ead87f555fc09a45366558549dc2c536f",
               "5401e79a676bb4b7deed4b9ca0233c93591718c498e6a37573160519672c5a4c"),
    "after": ("3e34515774b16a20c99aa6761f425f2bb36aebdf",
              "1d3baa91fcf85e60d1be0e8bc4da06c99442e34b89ffe8b868190b3d985a70b4"),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Optional new JSON file; refuses overwrite")
    args = parser.parse_args()
    if args.out and args.out.exists():
        parser.error("Output exists; choose a new file")
    results = {}
    with tempfile.TemporaryDirectory(prefix="dxa-jsx-demo-") as directory:
        directory = Path(directory)
        for label, (revision, expected_hash) in REVISIONS.items():
            source = subprocess.run(["git", "show", revision + ":" + SCANNER],
                                    cwd=ROOT, capture_output=True, check=True).stdout
            if hashlib.sha256(source).hexdigest() != expected_hash:
                raise RuntimeError(label + " scanner hash differs from accepted source")
            scanner = directory / (label + "-dxa.py")
            scanner.write_bytes(source)
            output = directory / (label + ".json")
            subprocess.run([sys.executable, str(STUDY / "measure.py"),
                            "--scanner", str(scanner), "--out", str(output)],
                           cwd=ROOT, check=True, capture_output=True, text=True)
            results[label] = json.loads(output.read_text(encoding="utf-8"))
    print("R8-M1: static review-candidate presence (not XSS)")
    for label, (revision, _) in REVISIONS.items():
        print(label + " commit: " + revision)
    print("\nMinimal contrast                         before  after")
    before = {row["id"]: row for row in results["before"]["cases"]}
    after = {row["id"]: row for row in results["after"]["cases"]}
    for case_id in ("dev-flat", "dev-style-after", "dev-fixed-url", "dev-custom-component"):
        print(f"{case_id:40} {before[case_id]['observed_candidates']:>3} {after[case_id]['observed_candidates']:>6}")
    print("\nFrozen corpus: TP/FP/FN/TN mean candidate-presence labels")
    expected_before = {"development": [1, 0, 2, 3], "evaluation": [0, 0, 6, 4],
                       "boundary": [0, 0, 0, 3]}
    expected_after = {"development": [3, 0, 0, 3], "evaluation": [6, 0, 0, 4],
                      "boundary": [0, 0, 0, 3]}
    for split in expected_before:
        counts = [[results[label]["counts"][split][key] for key in ("TP", "FP", "FN", "TN")]
                  for label in ("before", "after")]
        print(f"{split:12} {counts[0]} -> {counts[1]}")
        if counts != [expected_before[split], expected_after[split]]:
            raise RuntimeError("Pinned comparison differs from historical evidence")
    for label in results:
        if any(row["status"] != "completed" for row in results[label]["cases"]):
            raise RuntimeError("Incomplete cases cannot receive demo success")
    if any(not row["properties_ok"] for row in results["after"]["cases"]):
        raise RuntimeError("Final candidate properties differ from frozen oracle")
    print("\n19 cases per revision; no errors/skips. Three unsupported href controls stay excluded.")
    print("Repeated frozen evaluation; no new unseen cases, general accuracy or execution claim.")
    if args.out:
        with args.out.open("x", encoding="utf-8") as stream:
            json.dump({"schema": "dxa-r8-m1-demo/1", "revisions": REVISIONS,
                       "meaning": "Repeat of frozen static candidate-presence cases",
                       "results": results}, stream, indent=2)
            stream.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
