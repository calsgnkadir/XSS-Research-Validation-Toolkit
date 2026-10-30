"""Independent R8 bounded JSX URL oracles; fixture code is never executed.

Only lowercase intrinsic anchors are covered. Absence of a jsx-href finding
outside these fixtures is not a safety claim or general JSX parser guarantee.
"""
import pytest

import dxa
import dxa_evidence as evidence


def scan(tmp_path, source, ext):
    path = tmp_path / ("anchor." + ext)
    path.write_text(source, encoding="utf-8")
    return dxa.scan_file(str(path))


def anchor(rows, line=1):
    hits = [r for r in rows if r["sink"] == "jsx-href"]
    assert len(hits) == 1
    assert hits[0]["line"] == line
    return hits[0]


@pytest.mark.parametrize("ext", ["jsx", "tsx"])
@pytest.mark.parametrize("source", ["location.hash", "location.search"])
def test_direct_browser_source(tmp_path, ext, source):
    row = anchor(scan(tmp_path, f"const link = <a href={{{source}}}>Open</a>;", ext))
    assert row["confidence"] == "high"
    assert source in row["sources"]


@pytest.mark.parametrize("ext", ["jsx", "tsx"])
@pytest.mark.parametrize("source", ["location.hash", "location.search"])
def test_tracked_const_target(tmp_path, ext, source):
    rows = scan(tmp_path, f"const next = {source};\nconst link = <a href={{next}}>Open</a>;", ext)
    row = anchor(rows, 2)
    assert row["confidence"] == "high"
    assert "next" in row["tainted_vars"]


@pytest.mark.parametrize("ext", ["jsx", "tsx"])
def test_unknown_identifier_is_generic_medium_candidate(tmp_path, ext):
    row = anchor(scan(tmp_path, "const link = <a href={next}>Open</a>;", ext))
    assert row["confidence"] == "medium"
    assert row["sources"] == []
    assert row["tainted_vars"] == []


@pytest.mark.parametrize("ext", ["jsx", "tsx"])
def test_multiline_href_reports_attribute_physical_line(tmp_path, ext):
    source = ("const next = location.search;\nconst link = (\n  <a\n"
              "    className=\"next\"\n    href={\n      next\n    }\n  >Open</a>\n);\n")
    row = anchor(scan(tmp_path, source, ext), 5)
    assert row["confidence"] == "high"
    assert "next" in row["tainted_vars"]


@pytest.mark.parametrize("ext", ["jsx", "tsx"])
@pytest.mark.parametrize("attribute", [
    'href="/account"', 'href="https://example.invalid/help"',
    "href={'/account'}", 'href={"https://example.invalid/help"}',
])
def test_fixed_url_controls(tmp_path, ext, attribute):
    assert scan(tmp_path, f"const link = <a {attribute}>Open</a>;", ext) == []


@pytest.mark.parametrize("ext", ["jsx", "tsx"])
@pytest.mark.parametrize("source", [
    'const text = <p>{location.hash}</p>;',
    'const text = <a>{location.search}</a>;',
    'const card = <Card href={location.hash}>Open</Card>;',
    'const options = {href: location.hash};',
    '// const link = <a href={location.hash}>Open</a>;',
    '/* const link = <a href={location.hash}>Open</a>; */',
    "const example = '<a href={location.hash}>Open</a>';",
    'const example = "<a href={location.search}>Open</a>";',
    'const example = `<a href={location.hash}>Open</a>`;',
])
def test_non_anchor_or_inert_jsx_controls(tmp_path, ext, source):
    assert scan(tmp_path, source, ext) == []


@pytest.mark.parametrize("ext", ["jsx", "tsx"])
def test_unknown_validation_name_does_not_clear_source(tmp_path, ext):
    source = ("const q = location.search;\n"
              "const link = <a href={validateUrl(q)}>Open</a>;")
    row = anchor(scan(tmp_path, source, ext), 2)
    assert row["confidence"] == "high"
    assert "q" in row["tainted_vars"]


@pytest.mark.parametrize("ext", ["jsx", "tsx"])
@pytest.mark.parametrize("prefix", [
    'const help = "https://example.invalid/help";\n',
    'const label = `Open account`;\n',
    '// Example: <a href={location.hash}>sample</a>\n',
])
def test_same_file_prefix_does_not_hide_real_anchor(tmp_path, ext, prefix):
    source = prefix + "const next = location.hash;\nconst link = <a href={next}>Open</a>;"
    row = anchor(scan(tmp_path, source, ext), 3)
    assert row["confidence"] == "high"
    assert "next" in row["tainted_vars"]


@pytest.mark.parametrize("ext", ["jsx", "tsx"])
def test_local_component_source_origin(tmp_path, ext):
    source = ("function NextLink() {\n  const next = location.search;\n"
              "  return <a href={next}>Open</a>;\n}\n")
    row = anchor(scan(tmp_path, source, ext), 3)
    assert row["confidence"] == "high"
    assert "next" in row["tainted_vars"]


@pytest.mark.parametrize("ext", ["jsx", "tsx"])
def test_unrelated_function_local_does_not_taint_component_parameter(tmp_path, ext):
    # Two flat sibling functions require only a bounded lexical distinction,
    # not interprocedural analysis or a general JSX/JavaScript AST.
    source = ("function readFragment() {\n"
              "  const next = location.hash;\n"
              "  return next;\n"
              "}\n"
              "function NextLink(next) {\n"
              "  return <a href={next}>Open</a>;\n"
              "}\n")
    row = anchor(scan(tmp_path, source, ext), 6)
    assert row["confidence"] == "medium"
    assert row["sources"] == []
    assert row["tainted_vars"] == []


@pytest.mark.parametrize("ext", ["jsx", "tsx"])
def test_existing_property_and_navigation_sinks_survive(tmp_path, ext):
    rows = scan(tmp_path, "link.href = location.hash;\nwindow.location.assign(location.search);", ext)
    assert any(r["sink"] == "src-href" and r["line"] == 1
               and r["confidence"] == "high" for r in rows)
    assert any(r["sink"] == "navigation" and r["line"] == 2
               and r["confidence"] == "high" for r in rows)
    assert not any(r["sink"] == "jsx-href" for r in rows)


@pytest.mark.parametrize("ext", ["jsx", "tsx"])
def test_r1_candidate_contract_does_not_claim_execution(tmp_path, ext):
    rows = scan(tmp_path, "const link = <a href={location.hash}>Open</a>;", ext)
    raw = anchor(rows)
    exported = evidence.static_observations([raw])
    assert len(exported) == 1
    row = exported[0]
    assert row["evidence_level"] == "candidate"
    assert row["triage"] == "unreviewed"
    assert row["context"] == "source-code"
    assert row["source"] == {"file": raw["file"], "line": 1}
    assert row["sink"] == {"file": raw["file"], "line": 1, "identity": "jsx-href"}
    assert row.get("role_verified", False) is False
    assert row.get("attempt_id") is None
    assert row.get("canary_id") is None
