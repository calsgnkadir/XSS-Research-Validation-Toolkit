"""Run the local R9 self-scan acceptance and record portable provenance."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TESTS = [
    "bench/test_ci_self_scan.py", "bench/test_bench.py",
    "tools/dom-xss-analyzer/test_dxa.py",
    "tools/dom-xss-analyzer/test_static_context.py",
]
SOURCES = TESTS + [
    ".github/workflows/ci.yml", "bench/ci_self_scan.py", "bench/run.py",
    "tools/dom-xss-analyzer/dxa.py", "tools/dom-xss-analyzer/dxa_evidence.py",
    "audit/2026-10-11-continuity/run_validation.py",
] + [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / ".codex/agents").glob("*.toml"))] + [p.relative_to(ROOT).as_posix() for p in sorted(
    (ROOT / "tools/dom-xss-analyzer/examples").rglob("*")
) if p.is_file() and "__pycache__" not in p.parts]


def hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}


def main():
    if any((OUT / p).exists() for p in ("acceptance.xml", "acceptance.json")):
        raise SystemExit("Refusing to replace existing acceptance evidence")
    before = hashes()
    commands = [
        ["-m", "pytest", *TESTS, "-q", "-p", "no:cacheprovider", "--tb=short",
         "--junitxml=audit/2026-10-11-continuity/acceptance.xml"],
        ["bench/ci_self_scan.py"],
    ]
    results = []
    for args in commands:
        run = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True,
                             text=True, encoding="utf-8", errors="replace", timeout=180)
        output = (run.stdout + run.stderr).replace(str(ROOT), "<repo>")
        results.append({"command": "python " + " ".join(args),
                        "exit_code": run.returncode, "output": output})
        print(output)
    tree = ET.parse(OUT / "acceptance.xml")
    counts = {key: sum(int(s.get(key, "0")) for s in tree.iter("testsuite"))
              for key in ("tests", "failures", "errors", "skipped")}
    for suite in tree.iter("testsuite"):
        suite.attrib.pop("hostname", None)
    tree.write(OUT / "acceptance.xml", encoding="utf-8", xml_declaration=True)
    previous = json.loads((ROOT / "audit/2026-10-09-resume/environment.json").read_text("utf-8"))
    mismatch = [p for p, h in previous["source_sha256"].items()
                if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h]
    data = {
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(), "platform": platform.system(),
        "pytest": __import__("pytest").__version__, "browser_used": False, "docker_used": False,
        "commands": results, "junit": counts, "source_sha256": before,
        "source_unchanged_during_run": before == hashes(),
        "previous_acceptance_hash_check": {"checked": len(previous["source_sha256"]), "mismatches": mismatch},
    }
    (OUT / "acceptance.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf-8")
    return int(any(r["exit_code"] for r in results) or not data["source_unchanged_during_run"]
               or any(counts[k] for k in ("failures", "errors", "skipped")))


if __name__ == "__main__":
    sys.exit(main())
