"""Independent counterexamples for the K01 Linux artifact gate."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.parse import urlsplit

import pytest

from check_repro import validate
import check_repro

HISTORICAL = Path(__file__).resolve().parents[2] / "audit" / "2026-10-14-r5-k01-clean-repeat" / "proof"


@pytest.fixture
def proof(tmp_path):
    target = tmp_path / "proof"
    shutil.copytree(HISTORICAL, target)
    report = json.loads((target / "result.json").read_text(encoding="utf-8"))
    ports = [urlsplit(row["bot_finding"]["url"]).port for row in report["cases"]]
    return target, ports, report


def check(proof):
    target, ports, _ = proof
    return validate(target, ports, expected_platform="Windows", expected_python="3.10.")


def write_report(proof):
    target, _, report = proof
    (target / "result.json").write_text(json.dumps(report), encoding="utf-8")


def test_historical_proof_passes_with_explicit_historical_environment(proof):
    assert check(proof)["result"] == {
        "passed": 5, "total": 5, "fixture_ports_closed": 5, "distinct_fixture_ports": 5
    }


@pytest.mark.parametrize("field,value", [("platform", "Linux"), ("python", "3.11.9"),
                                          ("playwright", "1.62.0")])
def test_wrong_environment_rejected(proof, field, value):
    proof[2][field] = value
    write_report(proof)
    with pytest.raises(ValueError, match="wrong .* version|wrong platform"):
        check(proof)


def test_forged_negative_execution_rejected(proof):
    proof[2]["cases"][2]["observed_canary"] = proof[2]["cid"]
    write_report(proof)
    with pytest.raises(ValueError, match="browser control"):
        check(proof)


def test_http_candidate_promoted_to_execution_rejected(proof):
    proof[2]["cases"][2]["bot_finding"]["evidence_level"] = "execution-confirmed"
    write_report(proof)
    with pytest.raises(ValueError, match="HTTP candidate classification"):
        check(proof)


def test_incomplete_control_rejected(proof):
    proof[2]["cases"].pop()
    write_report(proof)
    with pytest.raises(ValueError, match="controls"):
        check(proof)


def test_modified_fixed_response_rejected(proof):
    target, _, _ = proof
    (target / "fixed-response.txt").write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="HTML response"):
        check(proof)


def test_missing_source_hash_rejected(proof):
    proof[2]["source_sha256"].pop("prove.py")
    write_report(proof)
    with pytest.raises(ValueError, match="source hashes"):
        check(proof)


def test_wrong_source_digest_rejected(proof):
    proof[2]["source_sha256"]["render_fixed.py"] = "0" * 64
    write_report(proof)
    with pytest.raises(ValueError, match="source hashes"):
        check(proof)


def test_open_fixture_port_rejected(proof):
    import socket
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        proof[1][0] = server.getsockname()[1]
        proof[2]["cases"][0]["bot_finding"]["url"] = (
            "http://127.0.0.1:" + str(proof[1][0]) + "/comments"
        )
        write_report(proof)
        with pytest.raises(ValueError, match="remained open"):
            check(proof)


@pytest.mark.parametrize("field,value", [("platform", "Linux"), ("python", "3.10.12")])
def test_exact_runtime_binding_rejects_plausible_wrong_values(proof, field, value):
    runtime = {key: proof[2][key] for key in ("platform", "python")}
    proof[2][field] = value
    write_report(proof)
    with pytest.raises(ValueError, match="executing runtime"):
        validate(proof[0], proof[1], "Windows", "3.10.", runtime=runtime)


def test_local_cli_forwards_browser_and_binds_runtime(tmp_path, monkeypatch, capsys):
    output = tmp_path / "new-proof"
    original = check_repro.prove.fixture
    calls = []
    monkeypatch.setattr(check_repro.platform, "system", lambda: "Windows")
    monkeypatch.setattr(check_repro.platform, "python_version", lambda: "3.10.11")

    def run(path, browser):
        calls.append((path, browser))
        path.mkdir()

    def gate(path, ports, expected_platform, expected_python, *, runtime):
        assert (path, ports, expected_platform, expected_python) == (output, [], "Windows", "3.10.11")
        assert runtime == {"platform": "Windows", "python": "3.10.11"}
        return {"result": {"passed": 5}}

    monkeypatch.setattr(check_repro.prove, "run", run)
    monkeypatch.setattr(check_repro, "validate", gate)
    check_repro.main(["--output", str(output), "--profile", "local", "--browser", "private-browser-path"])
    assert calls == [(output, "private-browser-path")]
    assert check_repro.prove.fixture is original
    record = (output / "acceptance.json").read_text()
    assert json.loads(record)["profile"] == "local"
    assert json.loads(record)["gate_sha256"] == check_repro.sha256(Path(check_repro.__file__))
    assert "private-browser-path" not in record + capsys.readouterr().out


@pytest.mark.parametrize("os_name,version", [("Windows", (3, 12)), ("Linux", (3, 10))])
def test_default_ci_profile_rejects_other_runtime_before_proof(tmp_path, monkeypatch, os_name, version):
    monkeypatch.setattr(check_repro.platform, "system", lambda: os_name)
    monkeypatch.setattr(check_repro.sys, "version_info", version)
    monkeypatch.setattr(check_repro.prove, "run", lambda *a: pytest.fail("proof must not start"))
    with pytest.raises(SystemExit) as exc:
        check_repro.main(["--output", str(tmp_path / "proof")])
    assert exc.value.code == 2
    assert not (tmp_path / "proof").exists()


def test_default_ci_profile_keeps_strict_environment(tmp_path, monkeypatch):
    output = tmp_path / "proof"
    monkeypatch.setattr(check_repro.platform, "system", lambda: "Linux")
    monkeypatch.setattr(check_repro.platform, "python_version", lambda: "3.12.15")
    monkeypatch.setattr(check_repro.sys, "version_info", (3, 12))
    monkeypatch.setattr(check_repro.prove, "run", lambda path, browser: path.mkdir())

    def gate(path, ports, expected_platform, expected_python, *, runtime):
        assert (expected_platform, expected_python) == ("Linux", "3.12.")
        assert runtime == {"platform": "Linux", "python": "3.12.15"}
        return {}

    monkeypatch.setattr(check_repro, "validate", gate)
    check_repro.main(["--output", str(output)])
    assert json.loads((output / "acceptance.json").read_text())["profile"] == "ci"


def test_optimized_interpreter_refused_before_creating_proof(tmp_path):
    output = tmp_path / "proof"
    result = subprocess.run([sys.executable, "-O", check_repro.__file__, "--profile", "local",
                             "--output", str(output)], capture_output=True, text=True)
    assert result.returncode == 2
    assert "optimized Python disables fixture assertions" in result.stderr
    assert not output.exists()


def test_failed_proof_restores_fixture_and_never_writes_acceptance(tmp_path, monkeypatch):
    output = tmp_path / "proof"
    original = check_repro.prove.fixture

    def fail(path, browser):
        path.mkdir()
        raise TimeoutError("incomplete proof")

    monkeypatch.setattr(check_repro.prove, "run", fail)
    with pytest.raises(TimeoutError):
        check_repro.main(["--profile", "local", "--output", str(output)])
    assert check_repro.prove.fixture is original
    assert not (output / "acceptance.json").exists()


def test_local_cli_preserves_existing_output(tmp_path):
    output = tmp_path / "proof"
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_text("existing evidence")
    with pytest.raises(FileExistsError):
        check_repro.main(["--profile", "local", "--output", str(output)])
    assert sentinel.read_text() == "existing evidence"
    assert set(output.iterdir()) == {sentinel}
