"""Run local R8 source regressions and synthetic source-signal measurement."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PRIVATE = ROOT / ".dxa/r8-helpers-20261030"
FILES = [
    "test_static_python_helpers.py", "test_static_leaflet.py",
    "test_static_jsx_href.py", "test_static_inline_messages.py",
    "test_static_receiver_bindings.py", "test_dxa.py",
    "test_static_context.py", "test_dxa_config.py", "test_r8_sanitizer.py",
    "test_r8_ast_pilot.py", "test_sarif.py", "test_r6_cli_modes.py",
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def counts(path):
    suites = ET.parse(path).getroot().iter("testsuite")
    result = {key: 0 for key in ("tests", "failures", "errors", "skipped")}
    for suite in suites:
        for key in result:
            result[key] += int(suite.get(key, 0))
    result["passed"] = result["tests"] - sum(result[key] for key in ("failures", "errors", "skipped"))
    return result


def run(command):
    print(" ".join(map(str, command)), flush=True)
    return subprocess.run(list(map(str, command)), cwd=ROOT).returncode


def main():
    PRIVATE.mkdir(parents=True, exist_ok=True)
    baseline = json.loads((HERE / "baseline.json").read_text(encoding="utf-8"))
    paths = ["tools/dom-xss-analyzer/" + name for name in FILES]
    hashes = {name: digest(ROOT / name) for name in ["tools/dom-xss-analyzer/dxa.py"] + paths}
    command = [sys.executable, "-m", "pytest", *paths, "-q", "-p", "no:cacheprovider",
               "--tb=short", "--junitxml=" + str(PRIVATE / "combined.xml")]
    code = run(command)
    fixed = counts(PRIVATE / "combined.xml")
    fixed["exit_code"] = code
    if any(digest(ROOT / name) != value for name, value in hashes.items()):
        raise RuntimeError("source/test files changed during acceptance")
    measurement_code = run([sys.executable, HERE / "measure.py", "--scanner",
                            "tools/dom-xss-analyzer/dxa.py", "--out", HERE / "measurement-final.json"])
    self_scan_code = run([sys.executable, "bench/ci_self_scan.py"])
    result = {
        "roadmap": "R8", "base_commit": "ea76fa5",
        "environment": {"os": platform.system(), "python": platform.python_version()},
        "release_status": "unreleased; PyPI 0.2.2 unchanged",
        "source_sha256": hashes,
        "baseline": {key: baseline[key] for key in ("tests", "failures", "errors", "skipped", "passed")},
        "baseline_scanner_sha256": baseline["scanner_sha256"],
        "baseline_origin": "Independent QA recorded baseline.json; not reexecuted by this runner",
        "fixed": fixed, "test_files": paths,
        "local_ci_self_scan_exit": self_scan_code,
        "measurement_exit": measurement_code,
        "measurement": "measurement-final.json",
        "hosted_ci": "not checked", "evidence_level": "candidate", "triage": "unreviewed",
        "limits": "Synthetic source only; no target application/HTTP/browser or general accuracy claim",
    }
    (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return int(code != 0 or fixed["failures"] != 0 or fixed["errors"] != 0
               or fixed["skipped"] != 0 or measurement_code != 0 or self_scan_code != 0)


if __name__ == "__main__":
    raise SystemExit(main())
