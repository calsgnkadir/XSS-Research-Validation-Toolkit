"""R8 inline-script message provenance: inert source, no execution claims."""
import pytest

import dxa
import dxa_evidence as evidence


def scan(tmp_path, source, ext="html"):
    path = tmp_path / ("message." + ext)
    path.write_text(source, encoding="utf-8")
    return dxa.scan_file(str(path))


def inner_at(rows, line):
    matches = [row for row in rows if row["sink"] == "innerHTML" and row["line"] == line]
    assert len(matches) == 1
    return matches[0]


def assert_message(row):
    assert row["confidence"] == "high"
    assert "postMessage.data" in row["sources"]


def assert_not_message(row):
    # A retained generic sink is not an execution or no-XSS conclusion.
    assert "postMessage.data" not in row["sources"]
    assert row["tainted_vars"] == []
    assert row["confidence"] != "high"


@pytest.mark.parametrize("ext", ["js", "html", "htm"])
@pytest.mark.parametrize("callback", ["e =>", "function(e)"])
def test_direct_message_read_in_executable_script(tmp_path, ext, callback):
    body = "window.addEventListener('message', " + callback + " {\n" \
           "panel.innerHTML = e.data;\n});\n"
    source = body if ext == "js" else "<!doctype html>\n<script>\n" + body + "</script>\n"
    row = inner_at(scan(tmp_path, source, ext), 2 if ext == "js" else 4)
    assert_message(row)


def test_same_line_script_preserves_message_source_and_physical_line(tmp_path):
    rows = scan(tmp_path, "<script>window.addEventListener('message', e => { "
                "panel.innerHTML = e.data; });</script>")
    assert_message(inner_at(rows, 1))


@pytest.mark.parametrize("script_type", ["module", "text/javascript"])
def test_declared_executable_script_type_keeps_message_source(tmp_path, script_type):
    rows = scan(tmp_path, '<script type="' + script_type + '">\n'
                "window.addEventListener('message', e => {\n"
                'panel.innerHTML = e.data;\n});\n</script>')
    assert_message(inner_at(rows, 3))


@pytest.mark.parametrize("ext", ["html", "htm"])
def test_local_message_value_keeps_provenance_and_physical_line(tmp_path, ext):
    rows = scan(tmp_path, "<main>Preview</main>\n<script>\n"
                "window.addEventListener('message', function(evt) {\n"
                "const value = evt.data;\npanel.innerHTML = value;\n});\n</script>\n", ext)
    row = inner_at(rows, 5)
    assert row["confidence"] == "high"
    assert "value" in row["tainted_vars"]


def test_ordinary_object_data_inside_listener_is_generic_candidate(tmp_path):
    rows = scan(tmp_path, "<script>\nwindow.addEventListener('message', e => {\n"
                "panel.innerHTML = object.data;\n});\n</script>")
    assert_not_message(inner_at(rows, 3))


def test_callback_receiver_does_not_escape_callback_or_script(tmp_path):
    rows = scan(tmp_path, "<script>\nwindow.addEventListener('message', e => {\n"
                "panel.innerHTML = e.data;\n});\n"
                "outside.innerHTML = e.data;\n</script>\n<script>\n"
                "sibling.innerHTML = e.data;\n</script>\n"
                "<p>text.innerHTML = e.data;</p>\n")
    assert_message(inner_at(rows, 3))
    for line in (5, 8, 10):
        assert_not_message(inner_at(rows, line))


@pytest.mark.parametrize("decoy", [
    "<!-- window.addEventListener('message', e => {}); -->",
    "<p>window.addEventListener('message', e => {});</p>",
    '<script type="application/ld+json">window.addEventListener("message", e => {});</script>',
    '<script type="text/plain">window.addEventListener("message", e => {});</script>',
    '<script src="ignored.js">window.addEventListener("message", e => {});</script>',
])
def test_non_executable_listener_text_cannot_activate_later_script(tmp_path, decoy):
    rows = scan(tmp_path, decoy + '\n<script>\npanel.innerHTML = e.data;\n</script>')
    assert_not_message(inner_at(rows, 3))


@pytest.mark.parametrize("attributes", [
    'type="application/ld+json"', 'type="text/plain"', 'src="ignored.js"',
])
def test_non_executable_script_callback_has_no_message_provenance(tmp_path, attributes):
    rows = scan(tmp_path, '<script ' + attributes + '>\n'
                "window.addEventListener('message', e => {\n"
                "panel.innerHTML = e.data;\n});\n</script>")
    assert_not_message(inner_at(rows, 3))


@pytest.mark.parametrize("body,sink_line", [
    ('e = object;\npanel.innerHTML = e.data;', 4),
    ('function render(e) {\npanel.innerHTML = e.data;\n}', 4),
])
def test_rebound_or_nested_receiver_is_not_attributed_to_message(tmp_path, body, sink_line):
    rows = scan(tmp_path, "<script>\nwindow.addEventListener('message', e => {\n"
                + body + '\n});\n</script>')
    assert_not_message(inner_at(rows, sink_line))


@pytest.mark.parametrize("comparison", ["!==", "===", "=="])
def test_origin_guard_does_not_clear_message_candidate(tmp_path, comparison):
    rows = scan(tmp_path, "<script>\nwindow.addEventListener('message', e => {\n"
                "if (e.origin " + comparison + " 'https://example.invalid') return;\n"
                "panel.innerHTML = e.data;\n});\n</script>")
    assert_message(inner_at(rows, 4))


def test_inline_location_source_and_textcontent_controls(tmp_path):
    rows = scan(tmp_path, "<script>\nwindow.addEventListener('message', e => {\n"
                "panel.textContent = e.data;\n});\n"
                "panel.innerHTML = location.hash;\n</script>")
    assert {row["line"] for row in rows if row["sink"] == "innerHTML"} == {5}
    row = inner_at(rows, 5)
    assert row["confidence"] == "high"
    assert "location.hash" in row["sources"]
    assert "postMessage.data" not in row["sources"]


def test_inline_message_report_remains_r1_static_candidate(tmp_path):
    rows = scan(tmp_path, "<script>\nwindow.addEventListener('message', e => {\n"
                "panel.innerHTML = e.data;\n});\n</script>")
    row = inner_at(rows, 3)
    assert_message(row)
    report = evidence.report(evidence.static_observations([row]), "static")
    assert report["schema_version"] == 1
    finding, = report["findings"]
    assert finding["evidence_level"] == "candidate"
    assert finding["triage"] == "unreviewed"
    assert finding["context"] == "source-code"
    assert finding["source"] == {"file": row["file"], "line": 3}
    assert finding["sink"] == {"file": row["file"], "line": 3, "identity": "innerHTML"}
    assert finding["attempt_id"] is None
    assert finding["canary_id"] is None
    assert finding["role_verified"] is False


def test_malformed_marked_section_retains_candidate_and_reports_analysis_error(tmp_path, monkeypatch):
    # Isolate the public event collector without discarding another test's
    # events. HTMLParser may reject this marked section with AssertionError.
    monkeypatch.setattr(dxa, "REPORT_EVENTS", [])
    rows = scan(tmp_path, '<![bogus]>\n<script>\n'
                'panel.innerHTML = e.data;\n</script>')
    assert_not_message(inner_at(rows, 3))
    errors = [event for event in dxa.REPORT_EVENTS if event.kind == "error"]
    assert errors, "malformed HTML analysis must emit an explicit error event"
    assert all(event.stage and event.reason for event in errors)


def test_same_line_callback_cannot_replace_earlier_genuine_location_source(tmp_path):
    rows = scan(tmp_path, '<script>first.innerHTML = location.hash; '
                "window.addEventListener('message', e => { "
                'second.innerHTML = object.data; });</script>')
    sinks = [row for row in rows if row["sink"] == "innerHTML" and row["line"] == 1]
    assert any(row["confidence"] == "high" and "location.hash" in row["sources"]
               for row in sinks)
    assert all("postMessage.data" not in row["sources"] for row in sinks)


def test_same_line_constant_sink_cannot_hide_later_genuine_message_source(tmp_path):
    rows = scan(tmp_path, '<script>first.innerHTML = "constant"; '
                "window.addEventListener('message', e => { "
                'second.innerHTML = e.data; });</script>')
    sinks = [row for row in rows if row["sink"] == "innerHTML" and row["line"] == 1]
    assert any(row["confidence"] == "high" and "postMessage.data" in row["sources"]
               for row in sinks)
