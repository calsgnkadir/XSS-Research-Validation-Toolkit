"""Private stdin-gated proof worker. Stdout contains one JSON result only."""
import contextlib
import json
import os
import sys


def main():
    # Parent establishes process-tree ownership before sending this request.
    target = json.loads(sys.stdin.read())
    from run import _run_dxaprove_local
    with open(os.devnull, "w") as discard, contextlib.redirect_stdout(discard):
        result = _run_dxaprove_local(target)
    sys.stdout.write(json.dumps(result, allow_nan=False))


if __name__ == "__main__":
    main()
