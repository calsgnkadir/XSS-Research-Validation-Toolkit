"""Engine design controls for bounded JSX sibling-prop recognition.

These development controls are separate from QA's frozen evaluation corpus.
Fixture code is scanned as text and is never executed as JavaScript.
"""
import pytest

import dxa


def href_rows(tmp_path, source):
    path = tmp_path / "design-control.jsx"
    path.write_text(source, encoding="utf-8")
    return [row for row in dxa.scan_file(str(path)) if row["sink"] == "jsx-href"]


@pytest.mark.parametrize("tail", [
    "broken=", "[broken]", "data-value=42", "data-value={unterminated",
    "data-value={value}}",
])
def test_invalid_later_attribute_invalidates_buffered_href(tmp_path, tail):
    source = "const view = <a href={target} style={{color:'navy'}} " + tail + ">go</a>;"
    assert href_rows(tmp_path, source) == []


@pytest.mark.parametrize("attributes", [
    "{...props} href={target} style={{color:'navy'}}",
    "href={target} style={{color:'navy'}} {...props}",
    "href={target} style={{...theme, color:'navy'}}",
])
def test_spread_remains_outside_supported_subset(tmp_path, attributes):
    assert href_rows(tmp_path, "const view = <a " + attributes + ">go</a>;") == []


@pytest.mark.parametrize("expression", [
    "({url: target}).url", "choose({url: target})", "() => { return target; }",
])
def test_nested_actual_href_remains_unsupported(tmp_path, expression):
    source = "const view = <a style={{color:'navy'}} href={" + expression + "}>go</a>;"
    assert href_rows(tmp_path, source) == []


@pytest.mark.parametrize("objects, expected", [(31, 1), (32, 0)])
def test_sibling_expression_depth_budget(tmp_path, objects, expected):
    nested = "{child:" * objects + "0" + "}" * objects
    source = "const view = <a href={target} data-meta={" + nested + "}>go</a>;"
    rows = href_rows(tmp_path, source)
    assert len(rows) == expected
    if rows:
        assert rows[0]["confidence"] == "medium"


def test_sibling_source_and_href_property_do_not_supply_href_provenance(tmp_path):
    source = ("const target = location.hash;\n"
              "const view = <a style={{href: location.search, label:target}} "
              "href={unknown}>go</a>;")
    rows = href_rows(tmp_path, source)
    assert len(rows) == 1
    assert rows[0]["confidence"] == "medium"
    assert rows[0]["sources"] == []
    assert rows[0]["tainted_vars"] == []


def test_complete_self_closing_tag_with_nested_sibling(tmp_path):
    rows = href_rows(tmp_path, "const view = <a href={target} style={{color:'navy'}} />;")
    assert len(rows) == 1
    assert rows[0]["confidence"] == "medium"


def test_long_sibling_expression_does_not_escape_tag_budget(tmp_path):
    source = "const view = <a href={target} style={{label:'" + "x" * 32768 + "'}} />;"
    assert href_rows(tmp_path, source) == []


@pytest.mark.parametrize("attributes", [
    "href={first} style={{color:'navy'}} href={second}",
    "href={first} style={{color:'navy'}} href='/fixed'",
    "href='/fixed' style={{color:'navy'}} href={second}",
    "href style={{color:'navy'}} href={second}",
    "href={first} style={{color:'navy'}} href",
    "style={{color:'navy'}} href={first} href={second}",
])
def test_duplicate_href_forms_are_ambiguous(tmp_path, attributes):
    assert href_rows(tmp_path, "const view = <a " + attributes + ">go</a>;") == []
