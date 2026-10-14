"""R6 mode selection must fail before any browser or HTTP work."""
import sys

import pytest

import dxadom
import dxadyn


@pytest.mark.parametrize("options", [
    ["--dom", "--stored"],
    ["--dom", "--flow", "unused.json"],
    ["--stored", "--flow", "unused.json"],
    ["http://127.0.0.1/fixture", "--stored"],
    ["http://127.0.0.1/fixture", "--flow", "unused.json"],
    ["--dom", "--auth-flow", "unused.json"],
    ["--dom", "--auth-check", "unused.json"],
    ["--dom", "--login", "http://127.0.0.1/login"],
    ["--dom", "--cookie", "session=LOCAL_SECRET"],
    ["--dom", "--header", "Authorization: LOCAL_SECRET"],
    ["--dom", "--csrf-refresh", "http://127.0.0.1/token"],
    ["--dom", "--csrf-header", "X-CSRF"],
])
def test_invalid_modes_stop_before_io(monkeypatch, tmp_path, capsys, options):
    def forbidden(*args, **kwargs):
        pytest.fail("invalid mode reached browser, session, scan or file loading")

    for name in ("crawl", "login", "apply_cookie", "apply_header", "_load_flow",
                 "run_flow", "probe_stored", "probe_stored_auto"):
        monkeypatch.setattr(dxadyn, name, forbidden)
    monkeypatch.setattr(dxadom, "is_available", forbidden)
    monkeypatch.setattr(dxadom, "summarize_availability", forbidden)
    out = tmp_path / "report.json"
    page = tmp_path / "report.html"
    monkeypatch.setattr(sys, "argv", ["dxadyn", *options, "--json-out", str(out),
                                      "--html", str(page)])
    with pytest.raises(SystemExit) as result:
        dxadyn.main()
    assert result.value.code == 2
    stderr = capsys.readouterr().err
    assert "error:" in stderr
    assert "LOCAL_SECRET" not in stderr
    assert not out.exists() and not page.exists()


def test_dom_availability_only_remains_supported(monkeypatch):
    monkeypatch.setattr(dxadom, "is_available", lambda: (True, "fixture"))
    monkeypatch.setattr(dxadom, "summarize_availability", lambda: "fixture")
    monkeypatch.setattr(sys, "argv", ["dxadyn", "--dom"])
    with pytest.raises(SystemExit) as result:
        dxadyn.main()
    assert result.value.code == 0
