"""Reproduce E02 local tests and isolated installed-wheel acceptance."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import venv
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TESTS = [
    "tools/dom-xss-analyzer/test_sarif.py",
    "tools/dom-xss-analyzer/test_dxa.py",
    "tools/dom-xss-analyzer/test_static_context.py",
    "tools/dom-xss-analyzer/test_r1_contract.py",
    "tools/dom-xss-analyzer/test_http_evidence.py",
    "tools/dom-xss-analyzer/test_dxadyn.py",
    "tools/dom-xss-analyzer/test_r2_contract.py",
    "tools/dom-xss-analyzer/test_dxa_config.py",
    "bench/test_check_installed_cli.py",
]


def run(arguments):
    subprocess.run([str(value) for value in arguments], cwd=ROOT, check=True)


def main():
    with tempfile.TemporaryDirectory(prefix="dxa-e02-") as temporary:
        work = Path(temporary)
        junit = work / "tests.xml"
        run([sys.executable, "-m", "pytest", *TESTS, "-q", "-p", "no:cacheprovider",
             "--tb=short", "--junitxml", junit])
        suites = ET.parse(junit).getroot().iter("testsuite")
        totals = {key: 0 for key in ("tests", "failures", "errors", "skipped")}
        for suite in suites:
            for key in totals:
                totals[key] += int(suite.get(key, 0))
        wheel_directory = work / "wheels"
        run([sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation",
             ".", "--wheel-dir", wheel_directory])
        wheels = list(wheel_directory.glob("*.whl"))
        assert len(wheels) == 1
        environment = work / "installed"
        venv.EnvBuilder(with_pip=True).create(environment)
        bin_directory = environment / ("Scripts" if sys.platform == "win32" else "bin")
        python = bin_directory / ("python.exe" if sys.platform == "win32" else "python")
        run([python, "-m", "pip", "install", "--no-index", "--no-deps", wheels[0]])
        installed_result = work / "installed.json"
        run([sys.executable, "bench/check_installed_cli.py", "--bin-dir", bin_directory,
             "--wheel", wheels[0], "--output", installed_result])
        installed = json.loads(installed_result.read_text(encoding="utf-8"))
        # Exclude temporary installation paths from shareable evidence.
        installed.pop("installed_module", None)
        sources = ["pyproject.toml", ".github/workflows/ci.yml",
                   "bench/check_installed_cli.py", "bench/test_check_installed_cli.py"]
        sources += [str(path.relative_to(ROOT)).replace("\\", "/")
                    for path in sorted((ROOT / "tools/dom-xss-analyzer").glob("*sarif*.py"))]
        sources += ["tools/dom-xss-analyzer/" + name for name in
                    ("dxa.py", "dxa2dyn.py", "dxadyn.py", "dxa_evidence.py",
                     "schemas/sarif-schema-2.1.0.json")]
        result = {"python": sys.version.split()[0], "tests": totals,
                  "test_selection": TESTS, "installed": installed,
                  "source_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                                    for name in sources}}
        (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "passed", **totals, "installed_cases": len(installed["results"])}))


if __name__ == "__main__":
    main()
