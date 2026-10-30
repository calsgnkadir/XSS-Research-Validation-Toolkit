"""Independent R8 helper-flow regressions; HIGH is source evidence, not XSS."""
import pytest

import dxa


def scan(tmp_path, source, sink="fastapi-html"):
    path = tmp_path / "helper_case.py"
    path.write_text(source, encoding="utf-8")
    rows = [row for row in dxa.scan_file(str(path)) if row["sink"] == sink]
    assert len(rows) == 1, rows
    return rows[0]


# Labels describe source evidence at this sink, not vulnerable/safe programs.
CORPUS = [
    ("source-return-assigned", "def get_value():\n    return request.args['q']\nvalue = get_value()\nHTMLResponse(value)\n", True),
    ("source-return-direct", "def get_value():\n    return request.args['q']\nHTMLResponse(get_value())\n", True),
    ("identity", "def wrap(value):\n    return value\nq = request.args['q']\nvalue = wrap(q)\nHTMLResponse(value)\n", True),
    ("encoded-body-assigned", "def wrap(value):\n    return html.escape(value)\nq = request.args['q']\nvalue = wrap(q)\nHTMLResponse(value)\n", False),
    ("encoded-body-direct", "def wrap(value):\n    return html.escape(value)\nq = request.args['q']\nHTMLResponse(wrap(q))\n", False),
    ("constant-return", "def wrap(value):\n    return 'fixed'\nq = request.args['q']\nvalue = wrap(q)\nHTMLResponse(value)\n", False),
    ("unused-argument", "def choose(first, second):\n    return second\nq = request.args['q']\nvalue = choose(q, 'fixed')\nHTMLResponse(value)\n", False),
    ("used-second-argument", "def choose(first, second):\n    return second\nq = request.args['q']\nvalue = choose('fixed', q)\nHTMLResponse(value)\n", True),
    ("mixed-raw-encoded", "def wrap(value):\n    return html.escape(value) + value\nq = request.args['q']\nvalue = wrap(q)\nHTMLResponse(value)\n", True),
    ("source-text-constant", "def wrap():\n    return \"request.args['q']\"\nvalue = wrap()\nHTMLResponse(value)\n", False),
    ("encoded-source-return", "def wrap():\n    return html.escape(request.args['q'])\nvalue = wrap()\nHTMLResponse(value)\n", False),
    ("encoded-source-return-direct", "def wrap():\n    return html.escape(request.args['q'])\nHTMLResponse(wrap())\n", False),
    ("raw-source-concat", "def wrap(value):\n    return 'prefix' + value\nq = request.args['q']\nHTMLResponse(wrap(q))\n", True),
]


@pytest.mark.parametrize("case", CORPUS, ids=lambda case: case[0])
def test_labeled_helper_source_evidence(tmp_path, case):
    _, source, expected_high = case
    row = scan(tmp_path, source)
    assert (row["confidence"] == "high") is expected_high
    if expected_high:
        assert row["sources"] or row["tainted_vars"]
    else:
        assert row["sources"] == []
        assert row["tainted_vars"] == []


@pytest.mark.parametrize("expression", [
    "wrap(q)", "wrap(q) + q", "wrap(q) + html.escape(q)",
])
def test_raw_provenance_reaches_nonhtml_sink_after_html_helper(tmp_path, expression):
    row = scan(tmp_path, "def wrap(value):\n    return html.escape(value)\n"
               "q = request.args['q']\nvalue = " + expression + "\nos.system(value)\n", "os-system")
    assert row["confidence"] == "high"
    assert "value" in row["tainted_vars"]


@pytest.mark.parametrize("argument", ["wrap(q)", "value"])
def test_html_helper_preserves_raw_template_source(tmp_path, argument):
    row = scan(tmp_path, "def wrap(value):\n    return html.escape(value)\n"
               "q = request.args['q']\nvalue = wrap(q)\nrender_template_string(" + argument + ")\n",
               "render-template-str")
    assert row["confidence"] == "high"
    assert row["sources"] or row["tainted_vars"]


@pytest.mark.parametrize("expression", [
    "'<script>' + wrap(q) + '</script>'",
    "'<style>' + wrap(q) + '</style>'",
    "'<a href=\"' + wrap(q) + '\">link</a>'",
    "'<div title=\"' + wrap(q) + '\">text</div>'",
])
def test_html_helper_does_not_clear_ambiguous_context(tmp_path, expression):
    row = scan(tmp_path, "def wrap(value):\n    return html.escape(value)\n"
               "q = request.args['q']\nHTMLResponse(" + expression + ")\n")
    assert row["confidence"] == "high"
    assert row["sources"] or row["tainted_vars"]


@pytest.mark.parametrize("returned", [
    "'<script>' + value + '</script>'",
    "'<div title=\"' + value + '\">text</div>'",
])
def test_helper_reveals_nonbody_context_for_preencoded_input(tmp_path, returned):
    row = scan(tmp_path, "def wrap(value):\n    return " + returned + "\n"
               "q = request.args['q']\nencoded = html.escape(q)\nHTMLResponse(wrap(encoded))\n")
    assert row["confidence"] == "high"
    assert "encoded" in row["tainted_vars"]


@pytest.mark.parametrize("definition", [
    "@decorate\ndef wrap(value):\n    return html.escape(value)\n",
    "async def wrap(value):\n    return html.escape(value)\n",
    "def wrap(value='fixed'):\n    return html.escape(value)\n",
    "def wrap(*values):\n    return html.escape(values[0])\n",
    "def wrap(value, **options):\n    return html.escape(value)\n",
    "def wrap(value):\n    if value:\n        return html.escape(value)\n    return value\n",
    "def wrap(value):\n    return wrap(value)\n",
    "def inner(value):\n    return html.escape(value)\ndef wrap(value):\n    return inner(value)\n",
    "def wrap(value):\n    other = html.escape(value)\n    return other\n",
    "def wrap(value):\n    return (lambda item: html.escape(item))(value)\n",
    "def wrap(value):\n    return ''.join(html.escape(item) for item in value)\n",
])
def test_unsupported_helper_never_grants_encoding_hint(tmp_path, definition):
    row = scan(tmp_path, definition + "q = request.args['q']\nvalue = wrap(q)\nHTMLResponse(value)\n")
    assert row["confidence"] == "high"
    assert "value" in row["tainted_vars"]


@pytest.mark.parametrize("mutation", [
    "wrap = identity\n",
    "def wrap(value):\n    return value\n",
    "from other import wrap\n",
    "alias = wrap\n",
    "consume(wrap)\n",
])
def test_ambiguous_helper_binding_retains_raw_input(tmp_path, mutation):
    row = scan(tmp_path, "def wrap(value):\n    return html.escape(value)\n" + mutation
               + "q = request.args['q']\nvalue = wrap(q)\nHTMLResponse(value)\n")
    assert row["confidence"] == "high"


@pytest.mark.parametrize("binding", [
    "try:\n    work()\nexcept Exception as wrap:\n    pass\n",
    "match item:\n    case wrap:\n        pass\n",
    "from other import *\n",
    "import other as wrap\n",
    "from other import replace as wrap\n",
])
def test_nonassignment_helper_binders_disable_encoding_hint(tmp_path, binding):
    row = scan(tmp_path, "def wrap(value):\n    return html.escape(value)\n" + binding
               + "q = request.args['q']\nvalue = wrap(q)\nHTMLResponse(value)\n")
    assert row["confidence"] == "high"


@pytest.mark.parametrize("mutation", [
    "html.escape, other = identity, replacement\n",
    "del html.escape\n",
    "html.escape: object = identity\n",
    "import other as html\n",
    "try:\n    work()\nexcept Exception as html:\n    pass\n",
    "match item:\n    case html:\n        pass\n",
    "html.escape.__code__ = identity.__code__\n",
    "html.__dict__['escape'] = identity\n",
    "html.__dict__.update(escape=identity)\n",
])
def test_encoder_receiver_mutations_disable_helper_mitigation(tmp_path, mutation):
    row = scan(tmp_path, "def wrap(value):\n    return html.escape(value)\n" + mutation
               + "q = request.args['q']\nvalue = wrap(q)\nHTMLResponse(value)\n")
    assert row["confidence"] == "high"


@pytest.mark.parametrize("call", ["wrap(value=q)", "wrap(*[q])", "wrap(q, 'extra')"])
def test_unsupported_call_shape_retains_raw_input(tmp_path, call):
    row = scan(tmp_path, "def wrap(value):\n    return html.escape(value)\n"
               "q = request.args['q']\nvalue = " + call + "\nHTMLResponse(value)\n")
    assert row["confidence"] == "high"


@pytest.mark.parametrize("mutation", [
    "html.escape = identity\n", "html = fake_html\n",
])
def test_rebound_encoder_does_not_clear_helper_input(tmp_path, mutation):
    row = scan(tmp_path, "def wrap(value):\n    return html.escape(value)\n" + mutation
               + "q = request.args['q']\nvalue = wrap(q)\nHTMLResponse(value)\n")
    assert row["confidence"] == "high"


def test_caller_parameter_shadows_helper_binding(tmp_path):
    row = scan(tmp_path, "def wrap(value):\n    return html.escape(value)\n"
               "def render(wrap):\n    q = request.args['q']\n    value = wrap(q)\n    return HTMLResponse(value)\n")
    assert row["confidence"] == "high"


def test_encoder_parameter_shadow_in_helper(tmp_path):
    row = scan(tmp_path, "def wrap(html, value):\n    return html.escape(value)\n"
               "q = request.args['q']\nvalue = wrap(fake_html, q)\nHTMLResponse(value)\n")
    assert row["confidence"] == "high"


def test_helper_definition_after_call_does_not_grant_mitigation(tmp_path):
    row = scan(tmp_path, "q = request.args['q']\nvalue = wrap(q)\nHTMLResponse(value)\n"
               "def wrap(value):\n    return html.escape(value)\n")
    assert row["confidence"] == "high"


def test_physical_sink_line_and_separate_scope_provenance(tmp_path):
    source = ("def get_value():\n    return request.args['q']\n\n"
              "def render():\n    value = get_value()\n    return HTMLResponse(value)\n")
    row = scan(tmp_path, source)
    assert row["line"] == 6
    assert row["confidence"] == "high"
    assert row["tainted_vars"] == ["value"]


def test_free_helper_name_does_not_capture_caller_local(tmp_path):
    row = scan(tmp_path, "def helper():\n    return q\n"
               "def render():\n    q = request.args['q']\n    value = helper()\n    return HTMLResponse(value)\n")
    assert row["confidence"] != "high"
    assert row["sources"] == []
    assert row["tainted_vars"] == []


@pytest.mark.parametrize("source, variable", [
    ("a, b = [*request.args['q']]\nHTMLResponse(a)\n", "a"),
    ("value = (q := request.args['q'])\nHTMLResponse(value)\n", "value"),
])
def test_ast_expression_shapes_preserve_source_without_crash(tmp_path, source, variable):
    row = scan(tmp_path, source)
    assert row["confidence"] == "high"
    assert variable in row["tainted_vars"]


def test_large_helper_parameter_list_retains_conservative_input(tmp_path):
    parameters = ["arg" + str(index) for index in range(17)]
    arguments = ["q"] + ["'fixed'"] * 16
    source = ("def wrap(" + ", ".join(parameters) + "):\n    return html.escape(arg0)\n"
              "q = request.args['q']\nvalue = wrap(" + ", ".join(arguments) + ")\nHTMLResponse(value)\n")
    row = scan(tmp_path, source)
    assert row["confidence"] == "high"
    assert row["tainted_vars"] == ["value"]


def test_large_return_expression_does_not_grant_encoding_hint(tmp_path):
    source = ("def wrap(value):\n    return " + " + ".join(["html.escape(value)"] * 40)
              + "\nq = request.args['q']\nvalue = wrap(q)\nHTMLResponse(value)\n")
    row = scan(tmp_path, source)
    assert row["confidence"] == "high"
    assert row["tainted_vars"] == ["value"]
