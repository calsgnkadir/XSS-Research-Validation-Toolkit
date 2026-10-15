"""Run the R6 installed-wheel readiness matrix using local tools only."""
import argparse
from email.parser import Parser
import hashlib
import json
import pathlib
import platform
import subprocess
import sys
import tempfile
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, cwd, timeout=60):
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin-dir", type=pathlib.Path, required=True)
    parser.add_argument("--demo-bin-dir", type=pathlib.Path, required=True)
    parser.add_argument("--wheel", type=pathlib.Path, required=True)
    parser.add_argument("--browser", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must not exist")

    bindir = args.bin_dir.resolve()
    demobindir = args.demo_bin_dir.resolve()
    suffix = ".exe" if platform.system() == "Windows" else ""
    cli = {name: bindir / (name + suffix) for name in ("dxa", "dxadyn", "dxaprove")}
    demo_cli = demobindir / ("dxaprove" + suffix)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    expected_docs = [
        "python -m pip install .", 'python -m pip install ".[browser]"',
        "dxa --help", "dxadyn --help", "dxaprove --help", "0.0.0.dev0",
        '"schema_version": 1, "min_confidence": "medium"',
        '"schema_version": 1, "depth": 1, "parallel": 1, "rate": 0',
        "Git release etiketi", "PyPI yayını",
        "dxaprove --demo --browser", "dxaprove --spec",
    ]
    missing_docs = [text for text in expected_docs if text not in readme]
    assert not missing_docs, f"README missing documented package/config contract: {missing_docs}"
    assert "Unreleased — 2026-10-15" in changelog

    module_hashes = {}
    help_results = {}
    with tempfile.TemporaryDirectory(prefix="dxa-r6-release-matrix-") as temp:
        cwd = pathlib.Path(temp)
        for name, executable in cli.items():
            result = run([str(executable), "--help"], cwd)
            assert result.returncode == 0, f"{name} help failed"
            help_results[name] = {"exit_code": 0, "has_usage": "usage:" in result.stdout.lower()}
        assert "--config" in run([str(cli["dxa"]), "--help"], cwd).stdout
        assert "--config" in run([str(cli["dxadyn"]), "--help"], cwd).stdout
        proof_help = run([str(cli["dxaprove"]), "--help"], cwd).stdout
        assert "--spec" in proof_help and "--demo" in proof_help
        proof_docs = (ROOT / "tools/dom-xss-analyzer/BROWSER-PROOF.md").read_text(encoding="utf-8")
        assert "--spec config.json" in proof_docs and "dxaprove.py --demo" in proof_docs

        for module in ("dxa", "dxadyn", "dxaprove"):
            source = ROOT / "tools/dom-xss-analyzer" / (module + ".py")
            identity = run([str(bindir / ("python" + suffix)), "-I", "-c",
                            "import hashlib," + module + "; from pathlib import Path; "
                            "print(hashlib.sha256(Path(" + module + ".__file__).read_bytes()).hexdigest())"], cwd)
            assert identity.returncode == 0 and identity.stdout.strip() == digest(source), f"{module} installed source mismatch"
            module_hashes[module] = digest(source)

        source = cwd / "case.py"
        source.write_text('HTMLResponse("constant")\nq = request.args["q"]\nHTMLResponse(q)\n', encoding="utf-8")
        config = cwd / "scan.json"
        config.write_text('{"schema_version":1,"min_confidence":"high"}', encoding="utf-8")
        configured = run([str(cli["dxa"]), str(source), "--config", str(config), "--json"], cwd)
        assert configured.returncode == 1
        rows = json.loads(configured.stdout)
        assert rows and all(row["confidence"] == "high" for row in rows)
        overridden = run([str(cli["dxa"]), str(source), "--config", str(config),
                          "--min-confidence", "low", "--json"], cwd)
        assert overridden.returncode == 1
        override_rows = json.loads(overridden.stdout)
        assert len(override_rows) > len(rows)

        dynamic_output = cwd / "dynamic-installed.json"
        dynamic = run([sys.executable, str(ROOT / "audit/2026-10-15-r6-config-release/smoke_installed.py"),
                       "--bin-dir", str(bindir), "--output", str(dynamic_output)], cwd, timeout=90)
        assert dynamic.returncode == 0, f"dynamic installed smoke failed: {dynamic.stderr}"
        dynamic_result = json.loads(dynamic_output.read_text(encoding="utf-8"))

        demo_output = cwd / "proof-demo"
        demo = run([str(demo_cli), "--demo", "--browser", str(args.browser.resolve()),
                    "--output", str(demo_output)], cwd, timeout=90)
        assert demo.returncode == 0, f"installed dxaprove demo failed: {demo.stderr}"
        proof = json.loads((demo_output / "result.json").read_text(encoding="utf-8"))
        assert proof.get("schema") == "dxa-browser-proof/1"
        assert proof.get("execution_observed") is True and len(proof.get("proofs", [])) == 1
        assert proof.get("triage") == "unreviewed"

    with zipfile.ZipFile(args.wheel.resolve()) as package:
        modules = sorted(name for name in package.namelist()
                         if name.endswith(".py") and ".dist-info/" not in name)
        metadata_file = next(name for name in package.namelist()
                             if name.endswith(".dist-info/METADATA"))
        package_metadata = Parser().parsestr(package.read(metadata_file).decode("utf-8"))
    requires_python = package_metadata.get("Requires-Python")
    extras = package_metadata.get_all("Provides-Extra", [])
    requires = package_metadata.get_all("Requires-Dist", [])
    assert requires_python == ">=3.10"
    assert "browser" in extras and any("playwright==1.63.0" in req for req in requires)
    assert all("extra ==" in req for req in requires), "unexpected mandatory runtime dependency"
    metadata_probe = run([str(bindir / ("python" + suffix)), "-I", "-c",
                          "import importlib.metadata as m; print(m.version('dxa-research-toolkit'))"],
                        pathlib.Path(tempfile.gettempdir()))
    assert metadata_probe.returncode == 0, "installed package metadata unavailable"
    metadata_version = metadata_probe.stdout.strip()
    assert metadata_version == "0.0.0.dev0"
    demo_identity = run([str(demobindir / ("python" + suffix)), "-c",
                         "import importlib.metadata as m; import playwright,dxaprove,sys; "
                         "from pathlib import Path; "
                         "assert Path(dxaprove.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()); "
                         "print(m.version('dxa-research-toolkit') + '|' + m.version('playwright') + '|' + "
                         "str(Path(playwright.__file__).resolve()))"],
                        pathlib.Path(tempfile.gettempdir()))
    assert demo_identity.returncode == 0
    demo_package_version, demo_playwright_version, playwright_path = demo_identity.stdout.strip().split("|", 2)
    assert demo_package_version == "0.0.0.dev0" and demo_playwright_version == "1.63.0"
    assert len(modules) == 9
    result = {
        "schema_version": 1,
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(), "platform": platform.system(),
        "package_version": metadata_version, "wheel_sha256": digest(args.wheel.resolve()),
        "wheel_metadata": {"requires_python": requires_python, "optional_extras": extras,
                           "requires_dist": requires, "mandatory_dependencies": 0},
        "wheel_modules": modules, "source_sha256": module_hashes,
        "cli_help": help_results,
        "docs": {"install_and_config_examples_match": True,
                 "proof_spec_and_demo_docs_match_help": True,
                 "changelog_has_unreleased_entry": True},
        "static_config": {"config_exit": configured.returncode,
                           "config_findings": len(rows), "config_confidence": "high",
                           "cli_override_findings": len(override_rows), "precedence": "CLI > config > default"},
        "dynamic_config": dynamic_result,
        "proof_demo": {"exit_code": demo.returncode, "status": proof["status"],
                       "execution_observed": proof["execution_observed"],
                       "proof_count": len(proof["proofs"]), "triage": proof["triage"],
                       "scope": "built-in disposable single-origin loopback fixture",
                       "environment": "fresh venv contains installed toolkit; Playwright 1.63.0 reused from preinstalled user site, no download",
                       "playwright_import_path": "user-site package path recorded privately at runtime; not copied to shared acceptance"},
        "limits": ["0.0.0.dev0 is a developer version; no release tag/publication",
                   "dxaprove --spec has a separate proof contract, not a general configuration schema",
                   "R4 broad admin/comparison and R5 independent-human prerequisites remain open",
                   "demo execution is not vulnerability confirmation"],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "wheel_sha256": result["wheel_sha256"],
                      "package_version": metadata_version, "proof_demo": result["proof_demo"]["status"]}))


if __name__ == "__main__":
    main()
