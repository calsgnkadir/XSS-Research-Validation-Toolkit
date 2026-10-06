import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import dxaprove
from dxa_proof_lab import lab


@pytest.fixture
def browser_path():
    if os.environ.get("DXA_REQUIRE_BROWSER") == "1":
        __import__("playwright.sync_api")
    else:
        pytest.importorskip("playwright.sync_api")
    path = os.environ.get("DXA_BROWSER")
    if not path and Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe").exists():
        path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not path:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            if not Path(pw.chromium.executable_path).exists():
                if os.environ.get("DXA_REQUIRE_BROWSER") == "1":
                    pytest.fail("required browser is missing")
                pytest.skip("install Playwright Chromium or set DXA_BROWSER")
    return path


@pytest.mark.parametrize("mode,expected", [("raw", True), ("fixed", False), ("json", False),
                                          ("dialog", False), ("iframe", True), ("delayed", True),
                                          ("too-late", False), ("eval", True), ("bearer", True), ("csrf", True)])
def test_authenticated_submit_read_canary(browser_path, mode, expected):
    with lab(mode) as (spec, state):
        result = dxaprove.run(spec, browser_path)
        assert result["status"] == ("execution-observed" if expected else "inconclusive"), result
        assert result["http_session_checked"] and result["browser_session_checked"]
        assert result["execution_observed"] is expected
        assert state["posts"] == 1 and state["checks"] == 3
        assert "lab-only-secret" not in json.dumps(result)
        assert "lab-password" not in json.dumps(result)
        if mode == "iframe":
            assert any(p["frame_url"].endswith("/frame") for p in result["proofs"])


def test_wrong_browser_role_stops_before_submit(browser_path):
    with lab("wrong-browser-role") as (spec, state):
        result = dxaprove.run(spec, browser_path)
        assert result["status"] == "error" and state["posts"] == 0
        assert result["events"][-1]["stage"] == "browser-auth"


@pytest.mark.parametrize("mode,variant,javascript,expected", [
    ("raw", "image", False, False), ("raw", "href", True, True), ("fixed", "href", True, False),
])
def test_js_disabled_and_real_href_controls(browser_path, mode, variant, javascript, expected):
    with lab(mode) as (spec, state):
        spec.update(variant=variant, javascript=javascript)
        result = dxaprove.run(spec, browser_path)
        assert result["status"] == ("execution-observed" if expected else "inconclusive"), result
        assert state["posts"] == 1


def test_scope_filter_blocks_other_origin(browser_path):
    with lab() as (spec, state):
        state["outside"] = "http://127.0.0.1:1/private"
        result = dxaprove.run(spec, browser_path)
        assert result["execution_observed"]
        assert any(e["reason"] == "request-blocked" for e in result["events"])


def test_bad_browser_is_error_before_submit():
    with lab() as (spec, state):
        result = dxaprove.run(spec, "missing-browser-executable")
        assert result["status"] == "error" and state["posts"] == 0
        assert result["events"][-1]["stage"] == "browser-start"


def test_cross_origin_config_is_rejected_without_requests():
    with lab() as (spec, state):
        spec["read_url"] = "http://127.0.0.1:1/"
        result = dxaprove.run(spec)
        assert result["status"] == "error" and state["checks"] == 0


def test_one_command_demo_outputs_same_json_html(browser_path, tmp_path):
    out = tmp_path / "proof"
    cmd = [sys.executable, str(Path(dxaprove.__file__)), "--demo", "--output", str(out)]
    if browser_path:
        cmd += ["--browser", browser_path]
    completed = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    assert completed.returncode == 0, completed.stderr
    result = json.loads((out / "result.json").read_text())
    assert result["execution_observed"] and result["triage"] == "unreviewed"
    assert result["canary_id"] in (out / "result.html").read_text()
