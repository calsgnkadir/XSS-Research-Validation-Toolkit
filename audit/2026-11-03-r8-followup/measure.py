"""Fixed synthetic source-evidence labels; no fixture code is executed."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile


PREFIX = "const flag = location.hash;\n"
PROVIDER = "export function currentUser() { return localStorage.getItem('user'); }\n"
IMPORTED = ("import {currentUser} from './session.js';\n"
            "const role = (currentUser() || {}).role;\n"
            "const flag = role === 'staff';\n")
# The boolean labels HIGH source provenance at the sink, never vulnerability.
CASES = [
    ("fixed-direct", False, False, "el.innerHTML = location.hash ? 'one' : 'two';\n"),
    ("fixed-helper", False, False, PREFIX + "el.innerHTML = unknown(flag ? 'one' : 'two');\n"),
    ("fixed-assignment", False, False, PREFIX + "const label = flag ? 'one' : 'two';\nel.innerHTML = label;\n"),
    ("fixed-provider-multiline", False, True, IMPORTED + "el.innerHTML = unknown(flag\n ? 'one'\n : 'two');\n"),
    ("raw-true-arm", True, False, PREFIX + "el.innerHTML = flag ? flag : 'two';\n"),
    ("raw-false-arm", True, False, PREFIX + "el.innerHTML = flag ? 'one' : flag;\n"),
    ("raw-extra-argument", True, False, PREFIX + "el.innerHTML = unknown(flag ? 'one' : 'two', flag);\n"),
    ("raw-multiline-extra-argument", True, False, PREFIX + "el.innerHTML = unknown(flag\n ? 'one'\n : 'two',\n flag);\n"),
    ("raw-multiline-residual", True, False, PREFIX + "el.innerHTML = unknown(flag\n ? 'one'\n : 'two')\n + flag;\n"),
    ("raw-provider-arm", True, True, IMPORTED + "el.innerHTML = unknown(flag ? 'one' : role);\n"),
    ("dynamic-template-arm", True, False, PREFIX + "el.innerHTML = flag ? 'one' : `two${flag}`;\n"),
    ("unsupported-call-condition", True, False, PREFIX + "el.innerHTML = read(flag) ? 'one' : 'two';\n"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scanner", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "tools/dom-xss-analyzer"))
    spec = importlib.util.spec_from_file_location("measured_followup", args.scanner)
    scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scanner)
    cases = []
    with tempfile.TemporaryDirectory(prefix="dxa-condition-labels-") as temporary:
        directory = Path(temporary)
        provider = directory / "session.js"
        provider.write_text(PROVIDER, encoding="utf-8")
        for case_id, expected, mapped, source in CASES:
            consumer = directory / "view.js"
            consumer.write_text(source, encoding="utf-8")
            scanner.REPORT_EVENTS.clear()
            mapping = scanner.build_cross_file_taint_map([str(provider), str(consumer)]) if mapped else None
            rows = [row for row in scanner.scan_file(str(consumer), cross_file_funcs=mapping)
                    if row["sink"] == "innerHTML"]
            if len(rows) != 1 or scanner.REPORT_EVENTS:
                raise RuntimeError(f"{case_id}: incomplete measurement")
            row = rows[0]
            observed = row["confidence"] == "high"
            outcome = ("TP" if observed else "FN") if expected else ("FP" if observed else "TN")
            cases.append(dict(id=case_id, expected_high=expected, observed_high=observed,
                              outcome=outcome, confidence=row["confidence"],
                              provider_map=mapped, source_sha256=hashlib.sha256(source.encode()).hexdigest()))
    result = dict(meaning="HIGH source-evidence labels; not vulnerability accuracy",
                  scanner_sha256=hashlib.sha256(args.scanner.read_bytes()).hexdigest(),
                  measurement_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  counts={key: sum(case["outcome"] == key for case in cases) for key in ("TP", "FP", "FN", "TN")},
                  cases=cases)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"]))


if __name__ == "__main__":
    main()
