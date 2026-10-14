"""R8 source-to-sink counterexamples; HIGH is a static candidate only."""
import pytest

import dxa


def html_finding(tmp_path, source):
    path = tmp_path / "case.py"
    path.write_text(source, encoding="utf-8")
    return next(row for row in dxa.scan_file(str(path))
                if row["sink"] == "fastapi-html")


@pytest.mark.parametrize("expression", [
    "identity_sanitize(q)",
    "identity_sanitize(q) + q",
    "html.escape(q) + q",
    "Markup(q)",
    "SafeString(q)",
])
def test_raw_flow_survives_wrappers_and_mixed_expression(tmp_path, expression):
    row = html_finding(
        tmp_path,
        'q = request.args["q"]\n'
        'value = ' + expression + '\nHTMLResponse(value)\n',
    )
    assert row["confidence"] == "high"
    assert row["tainted_vars"] == ["value"]


@pytest.mark.parametrize("expression", [
    "html.escape(q)",
    "bleach.clean(q)",
])
def test_explicit_identity_rebinding_is_not_encoder(tmp_path, expression):
    name = expression.split("(", 1)[0]
    row = html_finding(
        tmp_path,
        'def identity(value):\n    return value\n'
        + name + ' = identity\n'
        + 'q = request.args["q"]\n'
        + 'value = ' + expression + '\nHTMLResponse(value)\n',
    )
    assert row["confidence"] == "high"
    assert row["tainted_vars"] == ["value"]


def test_rebound_encoder_directly_at_sink_retains_raw_source(tmp_path):
    row = html_finding(
        tmp_path,
        'html.escape = lambda value: value\n'
        'HTMLResponse(html.escape(request.args["q"]))\n',
    )
    assert row["confidence"] == "high"
    assert row["sources"] == ["flask-request-arg"]


def test_unrebound_html_encoder_still_lowers_body_candidate(tmp_path):
    row = html_finding(
        tmp_path,
        'q = request.args["q"]\n'
        'value = html.escape(q)\nHTMLResponse(value)\n',
    )
    assert row["confidence"] != "high"
    assert row["sources"] == []
    assert row["tainted_vars"] == []




def test_rebinding_does_not_retroactively_taint_encoded_value(tmp_path):
    path = tmp_path / "case.py"
    path.write_text(
        'q = request.args["q"]\n'
        'early = html.escape(q)\n'
        'html.escape = lambda value: value\n'
        'late = html.escape(q)\n'
        'HTMLResponse(early)\n'
        'HTMLResponse(late)\n',
        encoding="utf-8",
    )
    rows = [row for row in dxa.scan_file(str(path))
            if row["sink"] == "fastapi-html"]
    assert [row["confidence"] for row in rows] == ["medium", "high"]
    assert rows[0]["tainted_vars"] == []
    assert rows[1]["tainted_vars"] == ["late"]


def test_rebinding_after_direct_sink_does_not_change_earlier_result(tmp_path):
    path = tmp_path / "case.py"
    path.write_text(
        'q = request.args["q"]\n'
        'HTMLResponse(html.escape(q))\n'
        'html.escape = lambda value: value\n'
        'HTMLResponse(html.escape(q))\n',
        encoding="utf-8",
    )
    rows = [row for row in dxa.scan_file(str(path))
            if row["sink"] == "fastapi-html"]
    assert [row["confidence"] for row in rows] == ["medium", "high"]


def test_unrelated_function_local_rebinding_does_not_affect_other_function(tmp_path):
    path = tmp_path / "case.py"
    path.write_text(
        'def override():\n'
        '    html.escape = lambda value: value\n'
        'def render():\n'
        '    q = request.args["q"]\n'
        '    return HTMLResponse(html.escape(q))\n',
        encoding="utf-8",
    )
    rows = [row for row in dxa.scan_file(str(path))
            if row["sink"] == "fastapi-html"]
    assert len(rows) == 1
    assert rows[0]["confidence"] == "medium"


def test_module_rebinding_before_function_is_visible_at_html_sink(tmp_path):
    row = html_finding(
        tmp_path,
        'html.escape = lambda value: value\n'
        'def render():\n'
        '    q = request.args["q"]\n'
        '    return HTMLResponse(html.escape(q))\n',
    )
    assert row["confidence"] == "high"
    assert row["tainted_vars"] == ["q"]
