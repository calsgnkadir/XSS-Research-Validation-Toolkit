"""Synthetic source-signal labels; not vulnerability precision/recall.

Run from the repository root with --scanner and --out. No target requests.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile


SOURCE = 'q = request.args["q"]\n'
ENCODER = 'def encode(value):\n    return html.escape(value)\n'
CASES = [
    ("source-return-direct", True, "supported",
     'def read():\n    return request.args["q"]\nHTMLResponse(read())\n'),
    ("source-return-assignment", True, "supported",
     'def read():\n    return request.args["q"]\nvalue = read()\nHTMLResponse(value)\n'),
    ("identity-argument", True, "supported",
     'def identity(value):\n    return value\n' + SOURCE + 'HTMLResponse(identity(q))\n'),
    ("encoder-body-direct", False, "supported",
     ENCODER + SOURCE + 'HTMLResponse(encode(q))\n'),
    ("encoder-body-assignment", False, "supported",
     ENCODER + SOURCE + 'value = encode(q)\nHTMLResponse(value)\n'),
    ("encoder-template-source", True, "supported",
     ENCODER + SOURCE + 'render_template_string(encode(q))\n'),
    ("encoder-attribute-context", True, "supported",
     ENCODER + SOURCE + 'HTMLResponse(\'<a href="\' + encode(q) + \'">link</a>\')\n'),
    ("mixed-encoded-raw", True, "supported",
     ENCODER + SOURCE + 'HTMLResponse(encode(q) + q)\n'),
    ("literal-return", False, "supported",
     'def fixed(value):\n    return "fixed"\n' + SOURCE + 'HTMLResponse(fixed(q))\n'),
    ("rebound-encoder", True, "conservative-control",
     ENCODER + 'html.escape = lambda value: value\n' + SOURCE + 'HTMLResponse(encode(q))\n'),
    ("unsupported-helper-chain", True, "unsupported-boundary",
     'def first():\n    return request.args["q"]\n'
     'def second():\n    return first()\nHTMLResponse(second())\n'),
    ("unsupported-branch-return", True, "unsupported-boundary",
     'def read(flag):\n    if flag:\n        return request.args["q"]\n'
     '    return "fixed"\nHTMLResponse(read(True))\n'),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scanner", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "tools/dom-xss-analyzer"))
    spec = importlib.util.spec_from_file_location("measured_dxa", args.scanner)
    scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scanner)
    rows = []
    with tempfile.TemporaryDirectory(prefix="dxa-helper-labels-") as directory:
        for case_id, expected_high, scope, source in CASES:
            path = Path(directory) / (case_id + ".py")
            path.write_text(source, encoding="utf-8")
            findings = [row for row in scanner.scan_file(str(path))
                        if row["sink"] in {"fastapi-html", "render-template-str"}]
            if len(findings) != 1:
                raise RuntimeError(f"{case_id}: expected exactly one sink, got {len(findings)}")
            observed_high = findings[0]["confidence"] == "high"
            outcome = ("TP" if observed_high else "FN") if expected_high else (
                "FP" if observed_high else "TN")
            rows.append(dict(id=case_id, scope=scope, expected_high=expected_high,
                             observed_high=observed_high, outcome=outcome,
                             confidence=findings[0]["confidence"],
                             source_sha256=hashlib.sha256(source.encode()).hexdigest()))
    result = {
        "meaning": "HIGH source-provenance signal labels, not vulnerability accuracy",
        "scanner_sha256": hashlib.sha256(args.scanner.read_bytes()).hexdigest(),
        "measurement_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "counts": {key: sum(row["outcome"] == key for row in rows)
                   for key in ("TP", "FP", "FN", "TN")},
        "cases": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"]))


if __name__ == "__main__":
    main()
