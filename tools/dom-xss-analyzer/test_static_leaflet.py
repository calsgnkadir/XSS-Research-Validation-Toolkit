"""Independent R8 Leaflet source oracles; JavaScript fixtures never execute.

Only exact ES default/namespace imports and bounded local receivers are covered.
Missing candidates outside this subset do not establish safety or execution.
"""
import pytest

import dxa
import dxa_evidence as evidence


POPUP = "leaflet-popup-html"
ICON = "leaflet-divicon-html"


def scan(tmp_path, source, ext="js"):
    path = tmp_path / ("leaflet." + ext)
    path.write_text(source, encoding="utf-8")
    return dxa.scan_file(str(path))


def leaflet(rows):
    return [row for row in rows if row["sink"] in {POPUP, ICON}]


def one(rows, sink, line):
    hits = leaflet(rows)
    assert [(row["sink"], row["line"]) for row in hits] == [(sink, line)]
    return hits[0]


@pytest.mark.parametrize("binding", ['import Maps from "leaflet";',
                                      'import * as Maps from "leaflet";'])
@pytest.mark.parametrize("setup,call,sink", [
    ("", "Maps.marker([0, 0]).bindPopup(VALUE);", POPUP),
    ("const pin = Maps.marker([0, 0]);\n", "pin.bindPopup(VALUE);", POPUP),
    ("", "Maps.popup().setContent(VALUE);", POPUP),
    ("const panel = Maps.popup();\n", "panel.setContent(VALUE);", POPUP),
    ("", "Maps.divIcon({html: VALUE});", ICON),
])
@pytest.mark.parametrize("value,confidence", [("location.hash", "high"),
                                             ("unknownContent", "medium")])
def test_import_alias_and_receiver_candidates(tmp_path, binding, setup, call, sink,
                                             value, confidence):
    row = one(scan(tmp_path, binding + "\n" + setup + call.replace("VALUE", value)),
              sink, 2 + setup.count("\n"))
    assert row["confidence"] == confidence
    if confidence == "high":
        assert "location.hash" in row["sources"]
    else:
        assert row["sources"] == []
        assert row["tainted_vars"] == []


@pytest.mark.parametrize("call,sink,line", [
    ("Maps.marker([0, 0])\n  .bindPopup(\n    content\n  );", POPUP, 4),
    ("Maps.popup()\n  .setContent(\n    content\n  );", POPUP, 4),
    ("Maps.divIcon({\n  className: 'pin',\n  html:\n    content\n});", ICON, 5),
])
def test_tracked_content_and_physical_sink_line(tmp_path, call, sink, line):
    row = one(scan(tmp_path, 'import Maps from "leaflet";\n'
                   'const content = location.search;\n' + call), sink, line)
    assert row["confidence"] == "high"
    assert "content" in row["tainted_vars"]


@pytest.mark.parametrize("value", ['`<b>${location.hash}</b>`',
                                   '`<b>${content}</b>`'])
def test_simple_template_interpolation_remains_source_candidate(tmp_path, value):
    row = one(scan(tmp_path, 'import Maps from "leaflet";\n'
                   'const content = location.search;\n'
                   f'Maps.popup().setContent({value});'), POPUP, 3)
    assert row["confidence"] == "high"


def test_adjacent_template_placeholders_keep_separate_source_tokens(tmp_path):
    row = one(scan(tmp_path, 'import Maps from "leaflet";\n'
                   'Maps.popup().setContent(`${location.hash}${location.search}`);'),
              POPUP, 2)
    assert row["confidence"] == "high"
    assert {"location.hash", "location.search"} <= set(row["sources"])


@pytest.mark.parametrize("declaration,call", [
    ('const marker = Maps.marker([0, 0]);', 'marker.bindPopup(location.hash);'),
    ('const popup = Maps.popup();', 'popup.setContent(location.hash);'),
])
def test_local_receiver_name_matching_factory_property_keeps_provenance(tmp_path, declaration, call):
    # Bare local identifiers do not mutate same-named qualified factory members.
    row = one(scan(tmp_path, 'import Maps from "leaflet";\n' +
                   declaration + '\n' + call), POPUP, 3)
    assert row["confidence"] == "high"
    assert "location.hash" in row["sources"]


def test_local_template_assignment_preserves_content_provenance(tmp_path):
    row = one(scan(tmp_path, 'import Maps from "leaflet";\n'
                   'const popup = Maps.popup();\n'
                   'const content = location.search;\n'
                   'const html = `<b>${content}</b>`;\n'
                   'popup.setContent(html);'), POPUP, 5)
    assert row["confidence"] == "high"
    assert "html" in row["tainted_vars"]


def test_unknown_validation_helper_does_not_clear_content_provenance(tmp_path):
    row = one(scan(tmp_path, 'import Maps from "leaflet";\n'
                   'const content = location.search;\n'
                   'Maps.popup().setContent(validateHtml(content));'), POPUP, 3)
    assert row["confidence"] == "high"
    assert "content" in row["tainted_vars"]


def test_divicon_other_property_source_does_not_taint_fixed_html(tmp_path):
    rows = scan(tmp_path, 'import Maps from "leaflet";\n'
                "Maps.divIcon({html: 'fixed', title: location.hash});")
    assert leaflet(rows) == []


def test_mutated_marker_factory_loses_local_receiver_provenance(tmp_path):
    rows = scan(tmp_path, 'import Maps from "leaflet";\n'
                'Maps.marker = foreign;\n'
                'const pin = Maps.marker([0, 0]);\n'
                'pin.bindPopup(location.hash);')
    # A replaced factory cannot establish Leaflet identity for its return value.
    assert leaflet(rows) == []


def test_template_expression_mutation_invalidates_native_dom_creator_proof(tmp_path):
    # The assignment is inside an evaluated placeholder, not literal template
    # text. Unknown creator return types cannot justify the HTMLElement exclusion.
    rows = scan(tmp_path, 'import Maps from "leaflet";\n'
                'const changed = `${document.createElement = foreignFactory}`;\n'
                "Maps.popup().setContent(document.createElement('div'));")
    row = one(rows, POPUP, 3)
    assert row["confidence"] == "medium"
    assert row["sources"] == []
    assert row["tainted_vars"] == []


def test_template_expression_mutation_invalidates_marker_factory_proof(tmp_path):
    rows = scan(tmp_path, 'import Maps from "leaflet";\n'
                'const changed = `${Maps.marker = foreignFactory}`;\n'
                'const pin = Maps.marker([0, 0]);\n'
                'pin.bindPopup(location.hash);')
    # Unknown factory identity is neither proven Leaflet nor proof of safety.
    assert leaflet(rows) == []


def test_literal_template_mutation_text_does_not_hide_genuine_popup_call(tmp_path):
    row = one(scan(tmp_path, 'import Maps from "leaflet";\n'
                   'const hint = `Maps.marker = foreignFactory`; '
                   'Maps.popup().setContent(location.hash);'), POPUP, 2)
    assert row["confidence"] == "high"
    assert "location.hash" in row["sources"]


@pytest.mark.parametrize("value", ['"Developer label"', '`<b>Fixed label</b>`'])
def test_fixed_strings_are_not_leaflet_raw_candidates(tmp_path, value):
    rows = scan(tmp_path, 'import Maps from "leaflet";\n'
                f'Maps.marker([0, 0]).bindPopup({value});\n'
                f'Maps.popup().setContent({value});\n'
                f'Maps.divIcon({{html: {value}}});')
    assert leaflet(rows) == []


def test_semicolonless_import_local_factory_and_popup_call(tmp_path):
    source = ('import MapLibrary from "leaflet"\n'
              'const content = location.hash\n'
              'const pin = MapLibrary.marker([41.01, 28.97])\n'
              'pin.bindPopup(content)\n')
    row = one(scan(tmp_path, source), POPUP, 4)
    assert row["confidence"] == "high"
    assert "content" in row["tainted_vars"]


def test_static_multiline_backtick_divicon_html_is_not_candidate(tmp_path):
    source = ('import MapLibrary from "leaflet"\n'
              'const icon = MapLibrary.divIcon({\n'
              '  html: `\n'
              '    <div class="map-pin">\n'
              '      <span>Selected place</span>\n'
              '    </div>\n'
              '  `\n'
              '})\n')
    assert leaflet(scan(tmp_path, source)) == []


@pytest.mark.parametrize("source", [
    'const other = {}; other.bindPopup(location.hash); other.setContent(location.hash);',
    'const options = {html: location.hash};',
    'import Maps from "fake-leaflet"; Maps.popup().setContent(location.hash);',
    'import Maps from "./leaflet"; Maps.marker([0, 0]).bindPopup(location.hash);',
    'import Maps from "leaflet-extra"; Maps.divIcon({html: location.hash});',
    '// import Maps from "leaflet";\nMaps.popup().setContent(location.hash);',
    'const sample = \'import Maps from "leaflet"; Maps.popup().setContent(location.hash);\';',
    'import Maps from "leaflet";\n// Maps.popup().setContent(location.hash);',
    'import Maps from "leaflet";\n/* Maps.divIcon({html: location.hash}); */',
    'import Maps from "leaflet";\nconst sample = "Maps.popup().setContent(location.hash)";',
    'import Maps from "leaflet";\nconst sample = `Maps.divIcon({html: location.hash})`;',
])
def test_unrelated_libraries_objects_and_inert_calls(tmp_path, source):
    assert leaflet(scan(tmp_path, source)) == []


@pytest.mark.parametrize("argument,setup", [
    ('document.createElement("div")', ""),
    ('document.createElement("span")', ""),
    ("node", 'const node = document.createElement("div");\n'
              'node.textContent = location.hash;\n'),
    ("node", 'const node = document.createElement("span");\n'
              'node.textContent = location.hash;\n'),
])
def test_known_dom_content_is_not_leaflet_html(tmp_path, argument, setup):
    # Benign literal div/span controls establish no new Leaflet string parse;
    # they do not assert that arbitrary nodes (e.g. script) are universally safe.
    rows = scan(tmp_path, 'import Maps from "leaflet";\n' + setup +
                f'Maps.marker([0, 0]).bindPopup({argument});\n'
                f'Maps.popup().setContent({argument});')
    assert leaflet(rows) == []


def test_dom_exclusion_preserves_unsafe_native_html_candidate(tmp_path):
    # Passing an HTMLElement adds no string parse, but its earlier unsafe HTML
    # assignment must still be reported independently of the Leaflet call.
    rows = scan(tmp_path, 'import Maps from "leaflet";\n'
                'const node = document.createElement("div");\n'
                'node.innerHTML = location.hash;\n'
                'Maps.popup().setContent(node);')
    assert leaflet(rows) == []
    native = [row for row in rows if row["sink"] == "innerHTML"]
    assert len(native) == 1
    assert native[0]["line"] == 3
    assert native[0]["confidence"] == "high"


@pytest.mark.parametrize("setup,confidence", [
    ('let node = document.createElement("div");\nnode = location.hash;\n', "high"),
    ('let node = document.createElement("div");\nif (flag) node = unknownContent;\n', "medium"),
    ('function build() { const node = document.createElement("div"); }\n', "medium"),
])
def test_reassigned_or_sibling_dom_binding_cannot_exclude_html(tmp_path, setup, confidence):
    rows = scan(tmp_path, 'import Maps from "leaflet";\n' + setup +
                'Maps.popup().setContent(node);')
    row = one(rows, POPUP, 2 + setup.count("\n"))
    assert row["confidence"] == confidence


@pytest.mark.parametrize("setup,call", [
    ('Maps = other;\n', 'Maps.popup().setContent(location.hash);'),
    ('let pin = Maps.marker([0, 0]);\npin = other;\n', 'pin.bindPopup(location.hash);'),
    ('function build() { const pin = Maps.marker([0, 0]); }\n', 'pin.bindPopup(location.hash);'),
    ('function render(Maps) {\n', 'Maps.popup().setContent(location.hash);\n}'),
])
def test_changed_or_out_of_scope_library_receiver_is_not_known_leaflet(tmp_path, setup, call):
    # Losing library identity is not proof that the unknown receiver is safe.
    assert leaflet(scan(tmp_path, 'import Maps from "leaflet";\n' + setup + call)) == []


def test_sibling_source_local_does_not_upgrade_unknown_content(tmp_path):
    rows = scan(tmp_path, 'import Maps from "leaflet";\n'
                'function read() { const content = location.hash; }\n'
                'function render(content) {\nMaps.popup().setContent(content);\n}')
    row = one(rows, POPUP, 4)
    assert row["confidence"] == "medium"
    assert row["sources"] == []
    assert row["tainted_vars"] == []


@pytest.mark.parametrize("ext", ["jsx", "tsx"])
def test_react_leaflet_plain_children_are_not_raw_html(tmp_path, ext):
    assert leaflet(scan(tmp_path, 'import { Popup } from "react-leaflet";\n'
                        'const view = <Popup>{location.hash}</Popup>;', ext)) == []


def test_inert_prefix_does_not_hide_real_leaflet_call(tmp_path):
    row = one(scan(tmp_path, 'import Maps from "leaflet";\n'
                   'const example = "Maps.popup().setContent(location.hash)";\n'
                   'Maps.popup().setContent(location.search);'), POPUP, 3)
    assert row["confidence"] == "high"
    assert "location.search" in row["sources"]


def test_r1_contract_remains_candidate_unreviewed(tmp_path):
    raw = one(scan(tmp_path, 'import Maps from "leaflet";\n'
                   'Maps.divIcon({html: location.hash});'), ICON, 2)
    row, = evidence.static_observations([raw])
    assert row["evidence_level"] == "candidate"
    assert row["triage"] == "unreviewed"
    assert row["context"] == "source-code"
    assert row["source"] == {"file": raw["file"], "line": 2}
    assert row["sink"] == {"file": raw["file"], "line": 2, "identity": ICON}
    assert row.get("role_verified", False) is False
    assert row.get("attempt_id") is None
    assert row.get("canary_id") is None
