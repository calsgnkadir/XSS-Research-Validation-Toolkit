"""Independent real-browser error-path oracles; never XSS negatives."""
import copy
import os
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import auth_failure_corpus as corpus
import run as runner

EXPECTED = {
    "login-rejected": ("http-auth", 0, 0),
    "http-identity-mismatch": ("http-auth", 0, 0),
    "browser-role-mismatch": ("browser-auth", 0, 0),
    "csrf-missing": ("submit", 0, 0),
    "csrf-rejected": ("submit", 1, 0),
    "session-expired-after-submit": ("browser-auth-after-submit", 1, 1),
}

@pytest.mark.parametrize("case", EXPECTED)
def test_real_failure_stops_at_expected_boundary_and_is_unscored(case):
    row = corpus.run_case(case, os.environ.get("DXA_BROWSER"))
    stage, requests, posts = EXPECTED[case]
    assert row["control_passed"], row
    proof = row["proof"]
    assert proof["status"] == "error"
    assert proof["events"][-1]["stage"] == stage
    assert not proof["execution_observed"] and not proof["proofs"]
    assert row["fixture"]["submit_requests"] == requests
    assert row["fixture"]["posts"] == posts
    assert row["fixture"]["reads"] == 0
    target = runner.proof_corpus()["targets"][0]
    adapted = runner.adapt_proof(target, proof, "http://127.0.0.1")
    assert adapted["status"] == "error"
    assert runner.score_findings(target["expected_ids"], adapted["findings"],
                                status=adapted["status"]) == {
        "tp": 0, "fp": 0, "fn": 0, "evaluated": False}
    for field, value in (("status", "inconclusive"), ("execution_observed", True),
                         ("proofs", [{"event": "unrelated"}])):
        changed = copy.deepcopy(proof)
        changed[field] = value
        assert not corpus.accept_failure(case, changed, row["fixture"])
    wrong = dict(row["fixture"], reads=1)
    assert not corpus.accept_failure(case, proof, wrong)
    changed = copy.deepcopy(proof)
    changed["events"][-1]["stage"] = "browser-start"
    assert not corpus.accept_failure(case, changed, row["fixture"])
