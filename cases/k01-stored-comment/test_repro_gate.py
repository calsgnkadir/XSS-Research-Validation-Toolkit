"""Independent counterexamples for the K01 Linux artifact gate."""

import json
from pathlib import Path
import shutil
from urllib.parse import urlsplit

import pytest

from check_repro import validate

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
