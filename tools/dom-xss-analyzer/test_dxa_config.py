"""R6 static CLI configuration precedence and fail-closed input checks."""

import json
import sys

import pytest

import dxa


def run_cli(monkeypatch, capsys, *args):
    monkeypatch.setattr(sys, "argv", ["dxa", *map(str, args)])
    with pytest.raises(SystemExit) as stopped:
        dxa.main()
    captured = capsys.readouterr()
    return stopped.value.code, captured.out, captured.err


def test_min_confidence_cli_overrides_config_and_default(tmp_path, monkeypatch, capsys):
    source = tmp_path / "case.py"
    source.write_text('HTMLResponse("constant")\nq = request.args["q"]\nHTMLResponse(q)\n',
                      encoding="utf-8")
    config = tmp_path / "scan.json"
    config.write_text(json.dumps({"schema_version": 1, "min_confidence": "high"}),
                      encoding="utf-8")

    code, output, _ = run_cli(monkeypatch, capsys, source, "--json")
    assert code == 1
    assert len(json.loads(output)) == 2  # built-in low default

    code, output, _ = run_cli(monkeypatch, capsys, source, "--config", config, "--json")
    assert code == 1
    assert [row["confidence"] for row in json.loads(output)] == ["high"]

    code, output, _ = run_cli(monkeypatch, capsys, source, "--config", config,
                              "--min-confidence", "low", "--json")
    assert code == 1
    assert len(json.loads(output)) == 2


@pytest.mark.parametrize("document", [
    {"schema_version": 2, "min_confidence": "high"},
    {"schema_version": 1, "min_confidence": "unknown"},
    {"schema_version": 1, "min_confidence": ["high"]},
    {"schema_version": 1, "min_confidence": "high", "cookie": "secret"},
    ["high"],
])
def test_invalid_config_rejected_without_echoing_values(tmp_path, monkeypatch, capsys, document):
    source = tmp_path / "case.py"
    source.write_text('HTMLResponse("constant")\n', encoding="utf-8")
    config = tmp_path / "scan.json"
    config.write_text(json.dumps(document), encoding="utf-8")
    code, output, error = run_cli(monkeypatch, capsys, source, "--config", config, "--json")
    assert code == 2
    assert output == ""
    assert "secret" not in error


def test_json_and_html_share_the_same_static_evidence(tmp_path, monkeypatch, capsys):
    source = tmp_path / "evil&name.py"
    source.write_text('HTMLResponse(request.args["<script>alert(1)</script>"])\n',
                      encoding="utf-8")
    json_out = tmp_path / "report.json"
    html_out = tmp_path / "report.html"
    original_report = dxa.evidence.report
    calls = []

    def recorded_report(*args, **kwargs):
        calls.append(1)
        return original_report(*args, **kwargs)

    monkeypatch.setattr(dxa.evidence, "report", recorded_report)
    code, _, _ = run_cli(monkeypatch, capsys, source, "--json-out", json_out,
                         "--html", html_out)
    assert code == 1
    assert len(calls) == 1
    document = json.loads(json_out.read_text(encoding="utf-8"))
    rendered = html_out.read_text(encoding="utf-8")
    assert document["schema_version"] == 1
    assert len(document["findings"]) == 1
    assert document["findings"][0]["finding_id"] in rendered
    assert "evil&amp;name.py" in rendered
    assert "evil&name.py" not in rendered
    assert "<script>alert(1)</script>" not in rendered


def test_powershell_utf8_bom_config_is_accepted(tmp_path, monkeypatch, capsys):
    source = tmp_path / "case.py"
    source.write_text('HTMLResponse("constant")\n', encoding="utf-8")
    config = tmp_path / "scan.json"
    config.write_bytes(b'\xef\xbb\xbf{"schema_version":1,"min_confidence":"high"}')
    code, output, error = run_cli(monkeypatch, capsys, source, "--config", config, "--json")
    assert (code, json.loads(output), error) == (0, [], "")


def test_duplicate_config_keys_are_rejected_before_scanning(tmp_path, monkeypatch, capsys):
    source = tmp_path / "case.py"
    source.write_text('HTMLResponse("constant")\n', encoding="utf-8")
    config = tmp_path / "scan.json"
    config.write_text(
        '{"schema_version":1,"min_confidence":"low",'
        '"min_confidence":"high"}',
        encoding="utf-8",
    )

    def unexpected_scan(*args, **kwargs):
        pytest.fail("ambiguous config reached source discovery")

    monkeypatch.setattr(dxa, "iter_files", unexpected_scan)
    code, output, error = run_cli(monkeypatch, capsys, source, "--config", config, "--json")
    assert code == 2
    assert output == ""
    assert "min_confidence" not in error
