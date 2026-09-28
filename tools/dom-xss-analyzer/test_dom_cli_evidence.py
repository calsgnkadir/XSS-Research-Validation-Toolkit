"""Bare browser visits must not claim attacker-controlled execution."""
import sys
from unittest.mock import MagicMock

import pytest

import dxadom
import dxadyn


def run_visit(monkeypatch, dialogs):
    browser = MagicMock()
    browser.__enter__.return_value.visit.return_value = {
        "url": "http://127.0.0.1/notice", "status": 200,
        "title": "Notice", "body_len": 80,
        "dialogs": dialogs, "console": [], "errors": [],
    }
    monkeypatch.setattr(dxadom, "BrowserSession", lambda: browser)
    monkeypatch.setattr(dxadom, "is_available", lambda: (True, "test harness"))
    monkeypatch.setattr(dxadom, "summarize_availability", lambda: "test harness")
    monkeypatch.setattr(sys, "argv", ["dxadyn.py", "http://127.0.0.1/notice", "--dom"])
    with pytest.raises(SystemExit) as result:
        dxadyn.main()
    assert result.value.code == 0
    browser.__enter__.return_value.visit.assert_called_once_with("http://127.0.0.1/notice")


@pytest.mark.parametrize("kind,message", [
    ("alert", "Welcome to the demo"),
    ("alert", "dxacafecafe"),  # A marker-looking string is not an owned injection.
    ("confirm", "Leave this page?"),
    ("prompt", "Your name"),
    ("beforeunload", "Unsaved changes"),
])
def test_bare_visit_dialog_is_observation_not_xss(monkeypatch, capsys, kind, message):
    run_visit(monkeypatch, [{"type": kind, "message": message}])
    out = capsys.readouterr().out
    assert "[OBSERVED-DIALOG]" in out
    assert f"{kind}: {message}" in out
    assert "do not establish XSS" in out
    assert "[PROVEN-EXECUTABLE]" not in out


def test_bare_visit_without_dialog_has_no_execution_claim(monkeypatch, capsys):
    run_visit(monkeypatch, [])
    out = capsys.readouterr().out
    assert "[OBSERVED-DIALOG]" not in out
    assert "[PROVEN-EXECUTABLE]" not in out
