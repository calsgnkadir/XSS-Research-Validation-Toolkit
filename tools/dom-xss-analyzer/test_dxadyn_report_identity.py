"""R6 JSON and HTML must describe one normalized sharing document."""
import html
import json
import sys
from unittest.mock import MagicMock

import pytest

import dxadyn
import dxadom


def test_reflected_cli_reuses_one_redacted_document_for_json_and_html(monkeypatch, tmp_path):
    target = "http://127.0.0.1/fixture?token=LOCAL_ONLY_SECRET"
    injected_name = '<svg onload="alert(1)">'
    row = dxadyn._finding("http://127.0.0.1/fixture", "GET", injected_name,
                          "unencoded", 200, "html-body", "cid-local", "text/html")
    row["headers"] = {"Authorization": "LOCAL_HEADER_SECRET"}
    monkeypatch.setattr(dxadyn, "crawl", lambda *args, **kwargs: [row])
    original_report = dxadyn.evidence.report
    calls = []

    def track_report(*args, **kwargs):
        calls.append(1)
        return original_report(*args, **kwargs)

    monkeypatch.setattr(dxadyn.evidence, "report", track_report)
    out, page = tmp_path / "findings.json", tmp_path / "findings.html"
    monkeypatch.setattr(sys, "argv", ["dxadyn.py", target, "--depth", "0",
                                      "--json-out", str(out), "--html", str(page)])
    with pytest.raises(SystemExit) as result:
        dxadyn.main()
    assert result.value.code == 1
    assert len(calls) == 1

    document = json.loads(out.read_text(encoding="utf-8"))
    markup = page.read_text(encoding="utf-8")
    finding = document["findings"][0]
    assert document["schema_version"] == finding["schema_version"] == 1
    assert document["mode"] == "reflected"
    assert document["meta"]["depth"] == "0"
    assert "<b>depth:</b>" in markup
    assert finding["finding_id"] == row["finding_id"]
    assert finding["finding_id"] in markup
    assert finding["evidence_level"] == "reflection"
    assert finding["param"] == injected_name
    assert html.escape(json.dumps(document["findings"], ensure_ascii=False, indent=2)) in markup
    assert html.escape(injected_name) in markup
    assert injected_name not in markup
    for secret in ("LOCAL_ONLY_SECRET", "LOCAL_HEADER_SECRET"):
        assert secret not in json.dumps(document) + markup
    assert row["headers"]["Authorization"] == "LOCAL_HEADER_SECRET"


@pytest.mark.parametrize("html_only", [False, True])
def test_reflected_cli_normalizes_only_when_output_requested(monkeypatch, tmp_path, html_only):
    row = dxadyn._finding("http://127.0.0.1/fixture", "GET", "fixture-field",
                          "unencoded", 200, "html-body", "cid-local", "text/html")
    monkeypatch.setattr(dxadyn, "crawl", lambda *args, **kwargs: [row])
    original_report = dxadyn.evidence.report
    calls = []

    def track_report(*args, **kwargs):
        calls.append(1)
        return original_report(*args, **kwargs)

    monkeypatch.setattr(dxadyn.evidence, "report", track_report)
    page = tmp_path / "html-only.html"
    argv = ["dxadyn.py", "http://127.0.0.1/fixture", "--depth", "0"]
    if html_only:
        argv.extend(["--html", str(page)])
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as result:
        dxadyn.main()
    assert result.value.code == 1
    assert len(calls) == int(html_only)
    if html_only:
        assert row["finding_id"] in page.read_text(encoding="utf-8")
    else:
        assert not page.exists()
    assert not (tmp_path / "findings.json").exists()


def test_dom_cli_observed_header_names_have_no_values_or_replay_claim(monkeypatch, capsys):
    summary = {"url": "http://127.0.0.1/fixture", "status": 200, "title": "fixture",
               "body_len": 0, "console": [], "errors": [],
               "auth_headers": {"Authorization": "LOCAL_HEADER_SECRET"}}
    browser = MagicMock()
    browser.__enter__.return_value.visit.return_value = summary
    monkeypatch.setattr(dxadom, "BrowserSession", lambda: browser)
    monkeypatch.setattr(dxadom, "is_available", lambda: (True, "fixture"))
    monkeypatch.setattr(dxadom, "summarize_availability", lambda: "fixture")
    monkeypatch.setattr(sys, "argv", ["dxadyn.py", summary["url"], "--dom"])
    with pytest.raises(SystemExit) as result:
        dxadyn.main()
    assert result.value.code == 0
    output = capsys.readouterr().out
    assert "observed auth header names (1); values unavailable, no replay" in output
    assert "Authorization" in output
    assert "LOCAL_HEADER_SECRET" not in output


@pytest.mark.parametrize("outputs", ["json", "html", "both"])
@pytest.mark.parametrize("mode", ["stored", "stored-auto", "flow", "dom", "auth-check", "login", "auth-flow"])
def test_cli_report_mode_matrix(monkeypatch, tmp_path, mode, outputs):
    """Every output branch shares one document, including operational failures."""
    url = "http://127.0.0.1/fixture"
    argv = ["dxadyn"]
    expected_exit = 0
    if mode in ("stored", "stored-auto"):
        argv += ["--stored", "--target", url, "--target-field", "comment"]
        if mode == "stored":
            argv += ["--check", url]
            monkeypatch.setattr(dxadyn, "probe_stored", lambda *a, **k: ([], "cid-fixture"))
        else:
            argv += ["--auto-check"]
            monkeypatch.setattr(dxadyn, "probe_stored_auto", lambda *a, **k: (
                [], "cid-fixture", {"submit_landing": url, "checked_pages": 1, "candidates": 1}))
    elif mode == "flow":
        argv += ["--flow", "fixture.json"]
        monkeypatch.setattr(dxadyn, "_load_flow", lambda *a: {})
        monkeypatch.setattr(dxadyn, "run_flow", lambda *a: {
            "verdicts": [], "name": "fixture", "steps_run": 1, "error": None})
    elif mode == "dom":
        argv += [url, "--dom"]
        browser = MagicMock()
        browser.__enter__.return_value.visit.return_value = {
            "url": url, "status": 200, "title": "fixture", "body_len": 0,
            "console": [], "errors": []}
        monkeypatch.setattr(dxadom, "BrowserSession", lambda: browser)
        monkeypatch.setattr(dxadom, "is_available", lambda: (True, "fixture"))
        monkeypatch.setattr(dxadom, "summarize_availability", lambda: "fixture")
    elif mode == "auth-check":
        argv += ["--auth-check", "fixture.json"]
        monkeypatch.setattr(dxadyn, "_load_flow", lambda *a: {})
        monkeypatch.setattr(dxadyn, "verify_session", lambda *a: True)
    elif mode == "login":
        argv += [url, "--login", url, "--user", "fixture", "--pass", "LOCAL_SECRET"]
        monkeypatch.setattr(dxadyn, "login", lambda *a, **k: False)
        expected_exit = 2
    else:
        argv += [url, "--auth-flow", "fixture.json"]
        monkeypatch.setattr(dxadyn, "_load_flow", lambda *a: {"__error__": "fixture failure"})
        expected_exit = 2

    documents, rendered = [], []
    original_report, original_render = dxadyn.evidence.report, dxadyn.render_html

    def track_report(*args, **kwargs):
        document = original_report(*args, **kwargs)
        documents.append(document)
        return document

    def track_render(*args, **kwargs):
        rendered.append(kwargs.get("document"))
        return original_render(*args, **kwargs)

    monkeypatch.setattr(dxadyn.evidence, "report", track_report)
    monkeypatch.setattr(dxadyn, "render_html", track_render)
    out, page = tmp_path / "report.json", tmp_path / "report.html"
    if outputs in ("json", "both"):
        argv += ["--json-out", str(out)]
    if outputs in ("html", "both"):
        argv += ["--html", str(page)]
    monkeypatch.setattr(sys, "argv", argv)
    try:
        dxadyn.main()
    except SystemExit as result:
        assert result.code == expected_exit
    else:
        assert expected_exit == 0
    assert len(documents) == 1
    document = documents[0]
    assert document["schema_version"] == 1
    assert document["mode"] == mode
    assert "LOCAL_SECRET" not in json.dumps(document)
    if expected_exit == 2:
        assert any(event["kind"] == "error" for event in document["events"])
    assert out.exists() == (outputs in ("json", "both"))
    assert page.exists() == (outputs in ("html", "both"))
    if out.exists():
        assert json.loads(out.read_text(encoding="utf-8")) == document
    if page.exists():
        assert len(rendered) == 1 and rendered[0] is document
        assert "LOCAL_SECRET" not in page.read_text(encoding="utf-8")
