"""Offline command for exporting a saved common R1 report to SARIF."""

import argparse
import json
from pathlib import Path
import sys

import dxa_sarif


def _reject_constant(value):
    raise ValueError("non-finite JSON number")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert a saved common R1 evidence report to SARIF 2.1.0 offline."
    )
    parser.add_argument("input", help="common --json-out R1 evidence JSON")
    parser.add_argument("--output", required=True, help="destination SARIF file")
    args = parser.parse_args(argv)
    source, destination = Path(args.input), Path(args.output)
    try:
        if source.resolve() == destination.resolve() or (
                destination.exists() and source.samefile(destination)):
            parser.error("input and output must have distinct paths")
        with source.open(encoding="utf-8-sig") as stream:
            document = json.load(stream, parse_constant=_reject_constant)
        # Validate and serialize before opening output so invalid input cannot
        # truncate an existing report. Do not echo arbitrary input or paths.
        rendered = json.dumps(dxa_sarif.to_sarif(document),
                              ensure_ascii=False, indent=2, allow_nan=False)
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError):
        print("dxa-sarif: cannot read or convert the R1 report", file=sys.stderr)
        return 2
    try:
        destination.write_text(rendered + "\n", encoding="utf-8")
    except (OSError, UnicodeError):
        print("dxa-sarif: cannot write the SARIF report", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
