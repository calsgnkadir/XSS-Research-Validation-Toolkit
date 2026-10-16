"""Exercise the installed CLI from outside the source tree using loopback only."""
import argparse
import email.parser
import hashlib
import http.server
import json
import pathlib
import platform
import subprocess
import tempfile
import threading
import urllib.parse
import zipfile


def distribution_identity(wheel_path):
    """Return and validate the wheel's distribution metadata and scripts."""
    with zipfile.ZipFile(wheel_path) as wheel:
        metadata_paths = [name for name in wheel.namelist()
                          if name.endswith(".dist-info/METADATA")]
        assert len(metadata_paths) == 1, "wheel must contain exactly one dist-info METADATA"
        metadata = email.parser.Parser().parsestr(
            wheel.read(metadata_paths[0]).decode("utf-8")
        )
        assert (metadata.get("Name") or "").lower().replace("_", "-") == \
            "dxa-research-toolkit", "unexpected wheel distribution name"
        version = metadata.get("Version")
        assert version, "wheel distribution version is missing"
        entry_paths = [name for name in wheel.namelist()
                       if name.endswith(".dist-info/entry_points.txt")]
        assert len(entry_paths) == 1, "wheel must contain exactly one console-script table"
        entry_points = wheel.read(entry_paths[0]).decode("utf-8")
        expected = "[console_scripts]\ndxa = dxa:main\ndxadyn = dxadyn:main\ndxaprove = dxaprove:main\n"
        normalized = "\n".join(line.strip() for line in entry_points.splitlines() if line.strip()) + "\n"
        assert normalized == expected, "wheel console-script metadata mismatch"
    return {"name": "dxa-research-toolkit", "version": version}


def main():
    if not __debug__:
        raise SystemExit("installed CLI gate requires assertions; do not use optimized Python")
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin-dir", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--wheel", type=pathlib.Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must not exist")
    wheel_identity = distribution_identity(args.wheel)
    suffix = ".exe" if platform.system() == "Windows" else ""
    executables = {name: args.bin_dir.resolve() / (name + suffix)
                   for name in ("dxa", "dxadyn", "dxaprove")}
    root = pathlib.Path(__file__).resolve().parents[1]
    source = root / "tools/dom-xss-analyzer/dxadyn.py"
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    results = {}
    with tempfile.TemporaryDirectory(prefix="dxa-installed-config-") as temp:
        directory = pathlib.Path(temp)
        # Isolated interpreter mode excludes PYTHONPATH/current-directory
        # imports. Bind acceptance to the installed module actually imported.
        installed_python = args.bin_dir.resolve() / ("python" + suffix)
        identity = subprocess.run([
            str(installed_python), "-I", "-c",
            "import dxadyn,hashlib,json,pathlib,platform,sys; "
            "p=pathlib.Path(dxadyn.__file__).resolve(); "
            "print(json.dumps({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),"
            "'under_venv':p.is_relative_to(pathlib.Path(sys.prefix).resolve()),"
            "'python':platform.python_version(),'platform':platform.system()}))"
        ], cwd=directory, capture_output=True, text=True, timeout=30)
        assert identity.returncode == 0, "installed module identity failed"
        installed = json.loads(identity.stdout)
        assert installed["under_venv"] is True, "module was not imported from the venv"
        assert installed["sha256"] == source_hash, "installed module differs from tested source"
        metadata_probe = subprocess.run([
            str(installed_python), "-I", "-c",
            "import importlib.metadata,json; d=importlib.metadata.distribution('dxa-research-toolkit'); "
            "print(json.dumps({'name':d.metadata['Name'],'version':d.version}))"
        ], cwd=directory, capture_output=True, text=True, timeout=30)
        assert metadata_probe.returncode == 0, "installed distribution metadata unavailable"
        installed_identity = json.loads(metadata_probe.stdout)
        assert installed_identity["name"].lower().replace("_", "-") == wheel_identity["name"]
        assert installed_identity["version"] == wheel_identity["version"], \
            "installed distribution version differs from supplied wheel"
        # Check every shipped module, not just the HTTP entry point. Isolated
        # imports must resolve inside the supplied environment.
        modules = ("dxa", "dxadyn", "dxaprove", "dxadom", "dxa_evidence",
                   "dxa_callback", "dxa_attempts", "dxa_proof_lab", "dxa2dyn")
        probe = subprocess.run([str(installed_python), "-I", "-c",
            "import hashlib,importlib,json,pathlib,sys; "
            "names=" + repr(modules) + "; "
            "paths={n:pathlib.Path(importlib.import_module(n).__file__).resolve() for n in names}; "
            "assert all(p.is_relative_to(pathlib.Path(sys.prefix).resolve()) for p in paths.values()); "
            "print(json.dumps({n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in paths.items()}))"
        ], cwd=directory, capture_output=True, text=True, timeout=30)
        assert probe.returncode == 0, "packaged module import failed"
        module_hashes = json.loads(probe.stdout)
        for name in modules:
            assert module_hashes[name] == hashlib.sha256(
                (root / "tools/dom-xss-analyzer" / (name + ".py")).read_bytes()
            ).hexdigest(), name + " packaged source mismatch"
        with zipfile.ZipFile(args.wheel) as wheel:
            for name in modules:
                assert hashlib.sha256(wheel.read(name + ".py")).hexdigest() == module_hashes[name], name + " wheel mismatch"
        for name, executable in executables.items():
            result = subprocess.run([str(executable), "--help"], cwd=directory,
                                    capture_output=True, text=True, timeout=30)
            assert result.returncode == 0, f"{name} help failed"
            results[name + "_help"] = {"exit_code": result.returncode}
            if name == "dxadyn":
                assert "--config" in result.stdout
        static_source = directory / "static.py"
        static_source.write_text('HTMLResponse("constant")\nq = request.args["q"]\nHTMLResponse(q)\n', encoding="utf-8")
        static_config = directory / "static.json"
        static_config.write_text('{"schema_version":1,"min_confidence":"high"}', encoding="utf-8")
        counts = []
        for options in ([], ["--min-confidence", "low"]):
            scan = subprocess.run([str(executables["dxa"]), str(static_source),
                                   "--config", str(static_config), "--json", *options],
                                  cwd=directory, capture_output=True, text=True, timeout=30)
            assert scan.returncode == 1, "static candidate scan did not complete"
            findings = json.loads(scan.stdout)
            if not options:
                assert findings and all(row["confidence"] == "high" for row in findings)
            counts.append(len(findings))
        assert counts[1] > counts[0], "CLI did not override static config"
        results["static_config"] = {"configured_findings": counts[0], "override_findings": counts[1]}
        config = directory / "tuning.json"
        config.write_text(json.dumps({"schema_version": 1, "depth": 1,
                                      "parallel": 1, "rate": 0}), encoding="utf-8-sig")
        for case, override, expected_depth in (("config", [], 1),
                                               ("cli_override", ["--depth", "0"], 0)):
            requests = []

            class Handler(http.server.BaseHTTPRequestHandler):
                def do_GET(self):
                    requests.append(self.path)
                    # Discovery collects query-bearing links. Both depths
                    # probe the query, but only depth 1 crawls bare /child.
                    body = (b'<html><a href="/child?q=1">child</a></html>'
                            if self.path == "/" else b'<html>local child</html>')
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)

                def log_message(self, *unused):
                    pass

            server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            report, page = directory / (case + ".json"), directory / (case + ".html")
            try:
                command = [str(executables["dxadyn"]),
                           f"http://127.0.0.1:{server.server_port}/", "--config", str(config),
                           *override, "--json-out", str(report), "--html", str(page)]
                result = subprocess.run(command, cwd=directory, capture_output=True,
                                        text=True, timeout=30)
                assert result.returncode == 0, f"{case} failed"
            finally:
                server.shutdown()
                server.server_close()
                worker.join(timeout=5)
            assert not worker.is_alive()
            document = json.loads(report.read_text(encoding="utf-8"))
            markup = page.read_text(encoding="utf-8")
            assert document["meta"]["depth"] == str(expected_depth)
            assert document["findings"] == [] and document["mode"] == "reflected"
            assert "<b>depth:</b> <span class='mono'>" + str(expected_depth) + "</span>" in markup
            assert ("/child" in requests) == bool(expected_depth), requests
            results[case] = {"exit_code": result.returncode, "depth": expected_depth,
                             "observed_routes": sorted({urllib.parse.urlsplit(route).path +
                                 ("?<query>" if urllib.parse.urlsplit(route).query else "")
                                 for route in requests}),
                             "html_json_depth_match": True, "fixture_thread_closed": True}
        invalid = directory / "invalid.json"
        invalid.write_text('{"schema_version":1,"cookie":"LOCAL_TEST_SECRET"}', encoding="utf-8")
        result = subprocess.run([str(executables["dxadyn"]), "http://127.0.0.1:1/",
                                 "--config", str(invalid)], cwd=directory,
                                capture_output=True, text=True, timeout=30)
        assert result.returncode == 2 and "LOCAL_TEST_SECRET" not in result.stderr
        results["invalid_config"] = {"exit_code": result.returncode, "secret_not_echoed": True}
    output = {"schema_version": 1, "python": platform.python_version(),
              "platform": platform.system(), "results": results,
              "installed_module": installed,
              "distribution": {**wheel_identity, "installed_version": installed_identity["version"]},
              "packaged_module_sha256": module_hashes,
              "wheel_sha256": hashlib.sha256(args.wheel.read_bytes()).hexdigest(),
              "source_sha256": {"tools/dom-xss-analyzer/dxadyn.py":
                                source_hash},
              "limits": ["No browser execution claimed", "No release tag created",
                         "Loopback fixture only; not a vulnerability result"]}
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "cases": len(results)}))


if __name__ == "__main__":
    main()
