"""Separate-process CLI acceptance, including an injected real-lab failure."""
import argparse
import html
import json
import os
from pathlib import Path
import subprocess
import sys


FAULT_DRIVER = r'''
import sys
from pathlib import Path
root = Path.cwd()
sys.path.insert(0, str(root / "bench"))
sys.path.insert(0, str(root / "tools/dom-xss-analyzer"))
import run as runner
import dxaprove
original = dxaprove.run
calls = []
def fail_once(spec, browser_path=None):
    calls.append(spec["origin"])
    if len(calls) == 1:
        raise RuntimeError("SYNTHETIC_PRIVATE_FAILURE")
    return original(spec, browser_path)
dxaprove.run = fail_once
sys.argv = ["bench/run.py", "--proof-suite", "--targets", "proof-raw,proof-fixed",
            "--browser", sys.argv[1], "--no-history", "--out", sys.argv[2]]
code = runner.main()
assert len(calls) == 2
# run_dxaprove's real lab context must release both listeners, including the
# one whose producer raised before browser launch.
import socket
from urllib.parse import urlsplit
for origin in calls:
    with socket.socket() as probe:
        probe.settimeout(1)
        assert probe.connect_ex(("127.0.0.1", urlsplit(origin).port)) != 0
raise SystemExit(code)
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    repo = here.parents[1]
    relative = here.relative_to(repo)
    records = []
    env = dict(os.environ, BENCH_STRICT="1")
    env.pop("BENCH_ENABLE_DOCKER", None)

    def run(command, expected, name):
        completed = subprocess.run(command, cwd=repo, env=env, capture_output=True,
                                   text=True, timeout=90)
        assert completed.returncode == expected, (name, completed.returncode, completed.stderr)
        assert "SYNTHETIC_PRIVATE_FAILURE" not in completed.stdout + completed.stderr
        records.append({"name": name, "command": command[1:], "exit_code": completed.returncode,
                        "expected_exit_code": expected, "stdout": completed.stdout,
                        "stderr": completed.stderr})

    normal = str(relative / "corpus-results.md")
    run([sys.executable, "bench/run.py", "--proof-suite", "--browser", args.browser,
         "--no-history", "--out", normal], 0, "strict-corpus")
    report = json.loads((here / "corpus-results.json").read_text(encoding="utf-8"))
    total = report["totals"]["dxaprove"]
    assert total["selected"] == total["completed"] == 9
    assert (total["tp"], total["fp"], total["fn"]) == (3, 0, 0)
    assert all(total[k] == 0 for k in ("error", "timeout", "skipped", "invalid", "inconclusive"))

    missing = str(relative / "missing-browser.md")
    run([sys.executable, "bench/run.py", "--proof-suite", "--browser", "missing-browser-executable",
         "--no-history", "--out", missing], 1, "missing-browser")
    report = json.loads((here / "missing-browser.json").read_text(encoding="utf-8"))
    assert report["totals"]["dxaprove"]["error"] == 9
    assert report["totals"]["dxaprove"]["completed"] == 0
    assert all(not row["results"]["dxaprove"]["score"]["evaluated"] for row in report["rows"])

    failure = str(relative / "injected-failure.md")
    run([sys.executable, "-c", FAULT_DRIVER, args.browser, failure], 1, "real-lab-exception")
    raw = (here / "injected-failure.json").read_text(encoding="utf-8")
    report = json.loads(raw)
    total = report["totals"]["dxaprove"]
    assert (total["selected"], total["completed"], total["error"]) == (2, 1, 1)
    assert (total["tp"], total["fp"], total["fn"]) == (0, 0, 0)
    assert not report["rows"][0]["results"]["dxaprove"]["score"]["evaluated"]
    assert "SYNTHETIC_PRIVATE_FAILURE" not in raw + (here / "injected-failure.md").read_text(encoding="utf-8")

    run([sys.executable, "tools/dom-xss-analyzer/dxaprove.py", "--demo", "--browser", args.browser,
         "--output", str(relative / "demo")], 0, "r3-demo")
    result = json.loads((here / "demo/result.json").read_text(encoding="utf-8"))
    rendered = (here / "demo/result.html").read_text(encoding="utf-8")
    assert json.loads(html.unescape(rendered.split("<pre>", 1)[1].split("</pre>", 1)[0])) == result
    assert result["status"] == "execution-observed" and result["triage"] == "unreviewed"
    (here / "cli-checks.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print("4 CLI checks passed; expected exits: 0, 1, 1, 0")


if __name__ == "__main__":
    main()
