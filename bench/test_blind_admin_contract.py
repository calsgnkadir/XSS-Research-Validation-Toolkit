"""Adapter boundary regressions, not cross-account/admin execution acceptance."""
import copy
import pytest
from test_proof_identity_matrix import BASE, CID, corpus_targets, make_execution_proof, make_no_execution_proof
import run as runner

@pytest.mark.parametrize("case", ["proof-raw", "proof-editor-raw"])
def test_admin_role_label_cannot_relabel_reader_or_editor_evidence(case):
    proof = make_execution_proof(case)
    proof["session_role"] = "admin"
    observed = runner.adapt_proof(corpus_targets()[case], proof, BASE)
    assert observed["status"] == "invalid"
    assert observed["findings"] == []

@pytest.mark.parametrize("event", ["resource-callback", "admin-visit", "callback"])
def test_callback_or_admin_visit_event_is_not_matching_browser_canary(event):
    proof = make_execution_proof("proof-raw")
    proof["proofs"][0]["event"] = event
    observed = runner.adapt_proof(corpus_targets()["proof-raw"], proof, BASE)
    assert observed["status"] == "invalid" and observed["findings"] == []

def test_matching_callback_completes_only_labelled_negative_window():
    target = corpus_targets()["proof-resource-callback"]
    proof = make_no_execution_proof("proof-resource-callback")
    observed = runner.adapt_proof(target, proof, BASE, {"resource_callback_hits": {CID: 1}})
    assert observed["callback_observed"]
    assert observed["status"] == "completed" and observed["findings"] == []
    assert observed["proof"]["execution_observed"] is False
    assert observed["proof"]["status"] == "inconclusive"

def test_foreign_callback_cannot_complete_negative_window():
    target = corpus_targets()["proof-resource-callback"]
    observed = runner.adapt_proof(target, make_no_execution_proof(target["id"]), BASE,
                                  {"resource_callback_hits": {"foreign-cid": 1}})
    assert observed["status"] == "invalid" and observed["findings"] == []
