"""R4 independent labelled fixture oracle and actual browser runner acceptance.

Labels describe execution of the submitted canary within 400 ms, not a finding
of vulnerability or a general declaration that a target is safe.
"""
import html
import http.cookiejar
import json
import os
from pathlib import Path
import sys
import urllib.parse
import urllib.request

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "dom-xss-analyzer"))
import run as runner
from dxa_proof_lab import lab


# Deliberately independent of proof_corpus() and scanner result/status fields.
EXPECTED = {
    "proof-raw": True,
    "proof-fixed": False,
    "proof-json": False,
    "proof-dialog": False,
    "proof-delayed": True,
    "proof-eval": True,
    "proof-title": False,
    "proof-textarea": False,
    "proof-resource-callback": False,
    "proof-sanitized-then-raw": True,
    "proof-identity-sanitizer": True,
    "proof-editor-raw": True,
    "proof-editor-fixed": False,
    "proof-iframe": True,
}
EDITOR_CASES = {"proof-editor-raw", "proof-editor-fixed"}
EXPECTED_FRAME_PATHS = {"proof-iframe": ["/frame"]}
ORACLE_CID = "dxa0123456789abcdef0123456789abcdef"
ORACLE_PAYLOAD = ORACLE_CID + '<img src="/__dxa_missing" onerror="window.__dxaProof=\'' + ORACLE_CID + '\'">'


def test_corpus_has_exact_independent_labels_and_identities():
    corpus = runner.proof_corpus()
    assert corpus["corpus_version"] == "loopback-proof/3"
    targets = {t["id"]: t for t in corpus["targets"]}
    assert len(corpus["targets"]) == 14
    assert targets.keys() == EXPECTED.keys()
    for case, positive in EXPECTED.items():
        mode = case.removeprefix("proof-")
        source_path, parameter, read_path, role = (
            ("/notes", "text", "/review", "editor") if case in EDITOR_CASES
            else ("/comments", "comment", "/comments", "reader"))
        identity = f"proof-v3:{mode}:POST:{source_path}:{parameter}:{read_path}:{role}"
        assert targets[case]["case_id"] == identity
        assert targets[case]["expected_ids"] == ([identity] if positive else [])
        assert targets[case]["expected_identity"] == {
            "method": "POST", "source_path": source_path, "parameter": parameter,
            "read_path": read_path, "role": role}
        assert targets[case]["expected_frame_paths"] == EXPECTED_FRAME_PATHS.get(case, [read_path])
        assert targets[case]["observe_ms"] == 400
        assert targets[case]["oracle_rationale"]


def submit_fixture(spec, value):
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    login = spec["auth_flow"]["steps"][0]
    with opener.open(login["url"], urllib.parse.urlencode(login["body"]).encode()) as response:
        assert response.status == 200
    field = spec["submit"]["field"]
    with opener.open(spec["submit"]["url"], urllib.parse.urlencode({field: value}).encode()) as response:
        assert response.status == 201
    return opener


@pytest.mark.parametrize("case", list(EXPECTED))
def test_fixture_content_and_state_independent_of_scanner(case):
    mode = case.removeprefix("proof-")
    value = ORACLE_PAYLOAD
    with lab(mode) as (spec, state):
        opener = submit_fixture(spec, value)
        with opener.open(spec["read_url"]) as response:
            content_type = response.headers.get_content_type()
            body = response.read().decode()
        assert state["posts"] == 1
        assert state["value"] == value
        if mode in ("fixed", "editor-fixed"):
            assert html.escape(value) in body and value not in body
        elif mode == "sanitized-then-raw":
            assert '<div class="sanitized">' + html.escape(value) + '</div>' in body
            assert '<div class="raw">' + value + '</div>' in body
        elif mode == "identity-sanitizer":
            assert 'function identitySanitize(value){return value;}' in body
            assert 'document.getElementById("sink").innerHTML=identitySanitize(' in body
            assert json.dumps(value) in body
        elif mode == "editor-raw":
            assert spec["submit"]["url"].endswith("/notes")
            assert spec["read_url"].endswith("/review")
            assert value in body
        elif mode == "json":
            assert content_type == "application/json"
            assert json.loads(body) == {"comment": value}
        elif mode == "dialog":
            assert "ordinary application dialog" in body and value not in body
        elif mode in ("title", "textarea"):
            assert f"<{mode}>{value}</{mode}>" in body
        elif mode == "delayed":
            assert "setTimeout" in body and "150" in body and json.dumps(value) in body
        elif mode == "eval":
            assert 'let local=17' in body and 'eval("local")' in body and json.dumps(value) in body
        elif mode == "resource-callback":
            assert html.escape(value) in body and value not in body
            assert '<img src="/resource-callback?cid=' + ORACLE_CID + '">' in body
            assert "<script" not in body
            assert state["resource_callback_hits"] == {}
        elif mode == "iframe":
            assert '<iframe src="/frame"></iframe>' in body
        else:
            assert value in body


@pytest.fixture(scope="module")
def browser_path():
    required = os.environ.get("DXA_REQUIRE_BROWSER") == "1"
    if required:
        __import__("playwright.sync_api")
    else:
        pytest.importorskip("playwright.sync_api")
    path = os.environ.get("DXA_BROWSER")
    chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if not path and chrome.exists():
        path = str(chrome)
    if not path:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            if not Path(pw.chromium.executable_path).exists():
                if required:
                    pytest.fail("required browser is missing")
                pytest.skip("install Playwright Chromium or set DXA_BROWSER")
    return path


@pytest.fixture(scope="module")
def browser_report(browser_path):
    return runner.run_all(runner.proof_corpus(browser_path), ["dxaprove"], None)


@pytest.mark.parametrize("case,positive", list(EXPECTED.items()))
def test_real_runner_matches_independent_case_oracle(browser_report, case, positive):
    row = next(row for row in browser_report["rows"] if row["id"] == case)
    result = row["results"]["dxaprove"]
    observed = result["observed"]
    assert observed["status"] == "completed", observed
    assert result["score"] == {"tp": int(positive), "fp": 0, "fn": 0, "evaluated": True}
    proof = observed["proof"]
    assert proof["execution_observed"] is positive
    assert proof["status"] == ("execution-observed" if positive else "inconclusive")
    assert proof["http_session_checked"] and proof["browser_session_checked"]
    target = next(target for target in runner.proof_corpus()["targets"] if target["id"] == case)
    assert proof["session_role"] == target["expected_identity"]["role"]
    assert proof["submit_status"] == 201 and proof["read_status"] == 200
    if positive:
        assert proof["proofs"] and all(p["canary_id"] == proof["canary_id"] for p in proof["proofs"])
        assert all(urllib.parse.urlsplit(p["frame_url"]).path in target["expected_frame_paths"]
                   for p in proof["proofs"])
    else:
        assert proof["proofs"] == [] and observed["negative_window_completed"]
    if case == "proof-resource-callback":
        assert observed["callback_observed"] is True
        assert observed["callback_count"] >= 1
        assert observed["fixture_observation"]["resource_callback_hits"][proof["canary_id"]] >= 1


def test_real_runner_strict_totals(browser_report):
    totals = browser_report["totals"]["dxaprove"]
    assert totals["selected"] == totals["completed"] == 14
    assert (totals["tp"], totals["fp"], totals["fn"]) == (7, 0, 0)
    assert all(totals[status] == 0 for status in ("error", "timeout", "skipped", "invalid", "inconclusive"))
    assert not runner.strict_failed(browser_report)


def test_resource_callback_occurs_with_javascript_disabled(browser_path):
    from playwright.sync_api import sync_playwright
    value = ORACLE_PAYLOAD
    with lab("resource-callback") as (spec, state):
        submit_fixture(spec, value)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, executable_path=browser_path)
            try:
                context = browser.new_context(java_script_enabled=False)
                page = context.new_page()
                login = spec["auth_flow"]["steps"][0]
                response = context.request.post(login["url"], form=login["body"])
                assert response.status == 200
                page.goto(spec["read_url"], wait_until="networkidle")
                assert state["resource_callback_hits"].get(ORACLE_CID, 0) >= 1
                assert page.locator("img[onerror], script").count() == 0
            finally:
                browser.close()
