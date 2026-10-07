"""A teardown failure must not leak proof-runner session state to the next case."""
import json

import pytest

import dxadyn
import dxaprove
from dxa_proof_lab import lab
from test_browser_proof import browser_path


@pytest.mark.parametrize("failed_close", ["context", "browser"])
def test_cleanup_error_restores_session_and_allows_next_case(browser_path, monkeypatch, failed_close):
    from playwright.sync_api import Browser, BrowserContext

    names = ("OPENER", "EXTRA_HEADERS", "REPORT_EVENTS", "SESSION_ROLE", "SESSION_CHECK",
             "CSRF_REFRESH_URL", "CSRF_HEADER_NAME", "_RATE_LIMITER")
    previous = {name: getattr(dxadyn, name) for name in names}
    original_context_close = BrowserContext.close
    original_browser_close = Browser.close
    closed = []

    def close_context(context, *args, **kwargs):
        original_context_close(context, *args, **kwargs)
        closed.append("context")
        if failed_close == "context":
            raise RuntimeError("SYNTHETIC_PRIVATE_CLEANUP_MESSAGE")

    def close_browser(browser, *args, **kwargs):
        original_browser_close(browser, *args, **kwargs)
        closed.append("browser")
        if failed_close == "browser":
            raise RuntimeError("SYNTHETIC_PRIVATE_CLEANUP_MESSAGE")

    with monkeypatch.context() as patch:
        patch.setattr(BrowserContext, "close", close_context)
        patch.setattr(Browser, "close", close_browser)
        with lab("fixed") as (spec, _):
            result = dxaprove.run(spec, browser_path)
        # Restore the test process even when the pre-fix assertion fails.
        try:
            assert result["status"] == "error"
            assert result["events"][-1]["stage"] == "cleanup"
            assert "SYNTHETIC_PRIVATE_CLEANUP_MESSAGE" not in json.dumps(result)
            assert closed == ["context", "browser"]
            assert all(getattr(dxadyn, name) is value for name, value in previous.items())
        finally:
            for name, value in previous.items():
                setattr(dxadyn, name, value)
    with lab("raw") as (spec, _):
        following = dxaprove.run(spec, browser_path)
    assert following["status"] == "execution-observed"
