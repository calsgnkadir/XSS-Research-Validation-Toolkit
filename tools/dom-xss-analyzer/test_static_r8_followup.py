"""Independent R8 condition/value provenance tests; HIGH does not mean XSS."""
import importlib.util
import os
from pathlib import Path

import pytest
import dxa


if os.environ.get("DXA_FOLLOWUP_SCANNER"):
    spec = importlib.util.spec_from_file_location("dxa_followup_base", os.environ["DXA_FOLLOWUP_SCANNER"])
    dxa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dxa)


def finding(tmp_path, source, extension=".js"):
    path = tmp_path / ("case" + extension)
    path.write_text(source, encoding="utf-8")
    rows = [row for row in dxa.scan_file(str(path)) if row["sink"] == "innerHTML"]
    assert len(rows) == 1, rows
    assert rows[0]["line"] == next(i for i, line in enumerate(source.splitlines(), 1) if "innerHTML" in line)
    return rows[0]


FIXED = [
    "el.innerHTML = location.hash ? 'one' : 'two';\n",
    "const flag = location.hash;\nel.innerHTML = flag ? 'one' : 'two';\n",
    "const flag = location.hash;\nel.innerHTML = !flag ? 'one' : 'two';\n",
    "const flag = location.hash;\nel.innerHTML = unknown(flag ? 'one' : 'two');\n",
    "const flag = location.hash;\nconst label = flag ? 'one' : 'two';\nel.innerHTML = label;\n",
    "const flag = location.hash;\nconst label = unknown(flag ? 'one' : 'two');\nel.innerHTML = label;\n",
    "const flag = location.hash;\nel.innerHTML = unknown(\n  flag ? 'one' : 'two'\n);\n",
    "const flag = location.hash;\nconst label = unknown(\n  flag\n    ? 'one'\n    : 'two'\n);\nel.innerHTML = label;\n",
    "const flag = location.hash;\nel.innerHTML = unknown('prefix', flag ? 'one' : 'two');\n",
    "const flag = location.hash;\nel.innerHTML = (flag ? 'escaped\\\'one' : 'two');\n",
    "el.innerHTML = mode ? 'location.hash' : 'document.cookie';\n",
]


@pytest.mark.parametrize("source", FIXED)
def test_fixed_arm_condition_does_not_supply_output_provenance(tmp_path, source):
    row = finding(tmp_path, source)
    assert row["confidence"] == "medium"
    assert row["sources"] == []
    assert row["tainted_vars"] == []


RAW = [
    "el.innerHTML = flag ? location.hash : 'two';\n",
    "el.innerHTML = flag ? 'one' : location.hash;\n",
    "const value = location.hash;\nel.innerHTML = flag ? value : 'two';\n",
    "const value = location.hash;\nel.innerHTML = flag ? 'one' : value;\n",
    "const flag = location.hash;\nel.innerHTML = unknown(flag ? 'one' : 'two', flag);\n",
    "const flag = location.hash;\nel.innerHTML = unknown(flag ? 'one' : 'two') + flag;\n",
    "const flag = location.hash;\nel.innerHTML = flag ? 'one' : `two${flag}`;\n",
    "const flag = location.hash;\nel.innerHTML = flag ? `${flag}` : 'two';\n",
    "const flag = location.hash;\nel.innerHTML = flag ? 'one' : 'two' + flag;\n",
    "const flag = location.hash;\nel.innerHTML = (flag ? 'one' : 'two') + flag;\n",
    "const flag = location.hash;\nel.innerHTML = unknown(flag, flag ? 'one' : 'two');\n",
    "const flag = location.hash;\nel.innerHTML = unknown(flag ? 'one' : 'two', location.search);\n",
    "const flag = location.hash;\nel.innerHTML = unknown(flag ? 'one' : 'two') + location.search;\n",
    "const flag = location.hash;\nel.innerHTML = flag ? 'one' : unknown(flag);\n",
    "const flag = location.hash;\nel.innerHTML = unknown(\n flag ? 'one' : 'two',\n flag\n);\n",
    "const flag = location.hash;\nel.innerHTML = unknown(\n flag ? 'one' : 'two'\n) + flag;\n",
]


@pytest.mark.parametrize("source", RAW)
def test_value_arm_extra_argument_or_residual_keeps_source(tmp_path, source):
    row = finding(tmp_path, source)
    assert row["confidence"] == "high"
    assert row["sources"] or row["tainted_vars"]


@pytest.mark.parametrize("condition", ["read(flag)", "flag && other", "flag === 'one'", "flag + other", "flag?.value"])
def test_unsupported_condition_retains_conservative_source(tmp_path, condition):
    row = finding(tmp_path, "const flag = location.hash;\nel.innerHTML = " + condition + " ? 'one' : 'two';\n")
    assert row["confidence"] == "high"


@pytest.mark.parametrize("decoy", [
    "// flag ? 'one' : 'two'\n",
    "/* flag ? 'one' : 'two' */\n",
    "const decoy = \"flag ? 'one' : 'two'\";\n",
    "const decoy = `flag ? 'one' : 'two'`;\n",
    "const decoy = /flag\\?'one':'two'/;\n",
])
def test_lexical_decoys_do_not_clear_later_raw_value(tmp_path, decoy):
    row = finding(tmp_path, "const flag = location.hash;\n" + decoy + "el.innerHTML = flag;\n")
    assert row["confidence"] == "high"
    assert row["tainted_vars"] == ["flag"]


def test_newline_preserves_original_report_code(tmp_path):
    source = "const flag = location.hash;\n\nel.innerHTML = unknown(\n flag ? 'one' : 'two'\n);\n"
    row = finding(tmp_path, source)
    assert row["line"] == 3
    assert row["code"] == "el.innerHTML = unknown("
    assert row["confidence"] == "medium"


@pytest.mark.parametrize("branch,expected_high", [
    ("flag\n ? 'one'\n : 'two'", False),
    ("flag ? role : 'two'", True),
    ("flag ? 'one' : role", True),
])
def test_directory_provider_map_distinguishes_control_from_value(tmp_path, branch, expected_high):
    provider = tmp_path / "session.js"
    provider.write_text("export function getCurrentUser() { return localStorage.getItem('user'); }\n", encoding="utf-8")
    consumer = tmp_path / "view.js"
    source = ("import {getCurrentUser} from './session.js';\n"
              "const role = (getCurrentUser() || {}).role;\n"
              "const flag = role === 'staff';\n"
              "el.innerHTML = unknown(\n" + branch + "\n);\n")
    consumer.write_text(source, encoding="utf-8")
    mapping = dxa.build_cross_file_taint_map([str(provider), str(consumer)])
    assert mapping.for_path(str(consumer)) == {"getCurrentUser"}
    rows = [row for row in dxa.scan_file(str(consumer), cross_file_funcs=mapping)
            if row["sink"] == "innerHTML"]
    assert len(rows) == 1
    row = rows[0]
    assert row["line"] == 4
    assert (row["confidence"] == "high") is expected_high
    if expected_high:
        assert row["tainted_vars"]
    else:
        assert row["sources"] == row["tainted_vars"] == row["xfunc_calls"] == []


def test_oversized_conditional_keeps_source(tmp_path):
    source = "const flag = location.hash;\nel.innerHTML = flag ? '" + "x" * 32769 + "' : 'two';\n"
    assert finding(tmp_path, source)["confidence"] == "high"


@pytest.mark.parametrize("expression", [
    "flag ? 'one' : other ? 'two' : flag",
    "flag /* uncertain */ ? 'one' : 'two'",
    "flag ? 'one' : 'unterminated",
    "flag ? 'one' : 'two' + unknown(flag)",
])
def test_nested_or_uncertain_syntax_never_clears_raw_source(tmp_path, expression):
    row = finding(tmp_path, "const flag = location.hash;\nel.innerHTML = " + expression + ";\n")
    assert row["confidence"] == "high"


@pytest.mark.parametrize("condition", ["mode === flag", "mode != flag", "mode += flag", "mode <= flag"])
def test_operator_before_condition_is_not_plain_assignment_boundary(tmp_path, condition):
    row = finding(tmp_path, "const flag = location.hash;\nel.innerHTML = " + condition + " ? 'one' : 'two';\n")
    assert row["confidence"] == "high"
    assert row["tainted_vars"] == ["flag"]


@pytest.mark.parametrize("assignment", [
    "el.innerHTML = fixed",
    "el.innerHTML = unknown(flag ? 'one' : 'two')",
])
@pytest.mark.parametrize("later", ["const raw = location.hash;", "raw = location.hash;", "consume(location.hash);"])
def test_asi_next_statement_is_not_part_of_sink_value(tmp_path, assignment, later):
    source = "const flag = location.hash;\n" + assignment + "\n" + later + "\n"
    row = finding(tmp_path, source)
    assert row["confidence"] == "medium"
    assert row["sources"] == row["tainted_vars"] == []


def test_newline_plus_is_real_value_continuation(tmp_path):
    source = "const flag = location.hash;\nel.innerHTML = unknown(flag ? 'one' : 'two')\n + flag;\n"
    row = finding(tmp_path, source)
    assert row["confidence"] == "high"
    assert row["tainted_vars"] == ["flag"]


def test_parenthesized_multiline_raw_residual_is_not_asi(tmp_path):
    source = "const flag = location.hash;\nel.innerHTML = (unknown(flag ? 'one' : 'two')\n + flag);\n"
    assert finding(tmp_path, source)["confidence"] == "high"


@pytest.mark.parametrize("source", [
    "el.innerHTML = fixed\n++location.hash;\n",
    "el.innerHTML = fixed / 2\nconst raw = location.hash;\n",
])
def test_asi_increment_and_opaque_slash_do_not_merge_next_statement(tmp_path, source):
    row = finding(tmp_path, source)
    assert row["confidence"] == "medium"
    assert row["sources"] == row["tainted_vars"] == []


@pytest.mark.parametrize("variable,markup", [
    ("info", '<div class="alert-info">fixed</div>'),
    ("input", '<input value="fixed">'),
])
def test_multiline_template_literal_text_does_not_invent_variable_flow(tmp_path, variable, markup):
    source = ("const " + variable + " = location.hash;\n"
              "view.innerHTML = `\n" + markup + "\n`;\n")
    row = finding(tmp_path, source)
    assert row["confidence"] == "medium"
    assert row["sources"] == row["tainted_vars"] == []


def test_same_line_template_raw_interpolation_retains_original_source_signal(tmp_path):
    source = "const info = location.hash;\nview.innerHTML = `<div>${info}</div>`;\n"
    row = finding(tmp_path, source)
    assert row["confidence"] == "high"
    assert row["tainted_vars"] == ["info"]


def test_unrelated_multiline_quoted_literal_does_not_invent_variable_flow(tmp_path):
    source = "const info = location.hash;\nview.innerHTML = unknown(\n 'alert-info'\n);\n"
    row = finding(tmp_path, source)
    assert row["confidence"] == "medium"
    assert row["sources"] == row["tainted_vars"] == []


def test_recovered_conditional_quoted_sibling_does_not_invent_variable_flow(tmp_path):
    source = ("const info = location.hash;\nview.innerHTML = unknown(\n"
              " flag ? 'one' : 'two',\n 'alert-info'\n);\n")
    row = finding(tmp_path, source)
    assert row["confidence"] == "medium"
    assert row["sources"] == row["tainted_vars"] == []
