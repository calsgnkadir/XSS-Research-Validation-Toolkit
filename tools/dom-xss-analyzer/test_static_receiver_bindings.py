"""R8 receiver counterexamples, using inert source and the public scan API.

These assertions concern static candidates, never JavaScript execution or XSS.
Unknown or ambiguous receivers must retain candidates; only a known native
FormData append and a router location declaration justify exclusion.
"""
import pytest

import dxa


def scan(tmp_path, source, ext="js"):
    path = tmp_path / ("receiver." + ext)
    path.write_text(source, encoding="utf-8")
    return dxa.scan_file(str(path))


def sink_lines(rows, sink):
    return {row["line"] for row in rows if row["sink"] == sink}


@pytest.mark.parametrize("ext", ["js", "jsx"])
def test_native_formdata_append_is_not_html_but_jquery_is(tmp_path, ext):
    rows = scan(tmp_path, 'const upload = new FormData();\n'
                'upload.append("label", location.hash);\n'
                '$("#preview").append(location.hash);\n', ext)
    assert sink_lines(rows, "jquery-html") == {3}
    assert any(row["sink"] == "jquery-html" and row["confidence"] == "high"
               for row in rows)


@pytest.mark.parametrize("source,expected", [
    ('data.append(location.hash);', {1}),
    ('const data = makeUpload();\ndata.append(location.hash);', {2}),
    ('let data = new FormData();\ndata = $("#out");\ndata.append(location.hash);', {3}),
    ('let data = new FormData();\nif (flag) data = unknown;\ndata.append(location.hash);', {3}),
    ('let data;\nif (flag) data = new FormData();\ndata.append(location.hash);', {3}),
    ('const data = new FormData();\nfunction render(data) {\ndata.append(location.hash);\n}', {3}),
    ('function upload() {\nconst data = new FormData();\n}\nfunction render(data) {\ndata.append(location.hash);\n}', {5}),
    ('const data = new FormData();\n{\nconst data = unknown;\ndata.append(location.hash);\n}', {4}),
])
def test_ambiguous_or_changed_append_receiver_is_retained(tmp_path, source, expected):
    assert sink_lines(scan(tmp_path, source), "jquery-html") == expected


@pytest.mark.parametrize("binding", [
    'import FormData from "./custom-form.js";',
    'class FormData { append(value) { render(value); } }',
    'const FormData = CustomHtmlBuilder;',
])
def test_custom_formdata_constructor_is_not_native_proof(tmp_path, binding):
    rows = scan(tmp_path, binding + '\nconst data = new FormData();\ndata.append(location.hash);')
    assert sink_lines(rows, "jquery-html") == {3}


def test_formdata_constructor_parameter_is_not_native_proof(tmp_path):
    rows = scan(tmp_path, 'function render(FormData) {\nconst data = new FormData();\n'
                'data.append(location.hash);\n}')
    assert sink_lines(rows, "jquery-html") == {3}


@pytest.mark.parametrize("ext", ["js", "jsx"])
def test_router_declaration_excluded_navigation_writes_retained(tmp_path, ext):
    rows = scan(tmp_path, 'import { useLocation } from "react-router-dom";\n'
                'const location = useLocation();\n'
                'location.href = next;\nwindow.location = next;\n'
                'window.location.href = next;\nlocation.assign(next);\n'
                'location.replace(next);\nwindow.open(next);\n', ext)
    assert sink_lines(rows, "navigation") == {3, 4, 5, 6, 7, 8}


def test_router_binding_does_not_hide_other_function_navigation(tmp_path):
    rows = scan(tmp_path, 'function view() {\nconst location = useLocation();\n}\n'
                'function navigate(next) {\nlocation = next;\n}\n')
    assert sink_lines(rows, "navigation") == {5}


@pytest.mark.parametrize("write", [
    'location = next;',
    'if (flag) location = next;',
    '{ let location; location = next; }',
])
def test_router_declaration_does_not_clear_later_assignment(tmp_path, write):
    rows = scan(tmp_path, 'const location = useLocation();\n' + write)
    assert sink_lines(rows, "navigation") == {2}


@pytest.mark.parametrize("source,sink", [
    ('const data = new FormData(); data.append("x", value); $("#out").append(location.hash);', "jquery-html"),
    ('$("#out").append(location.hash); const data = new FormData(); data.append("x", value);', "jquery-html"),
    ('const location = useLocation(); window.location.href = next;', "navigation"),
    ('window.location.href = next; const location = useLocation();', "navigation"),
])
def test_excluded_match_cannot_erase_real_sink_on_same_line(tmp_path, source, sink):
    assert sink_lines(scan(tmp_path, source), sink) == {1}


@pytest.mark.parametrize("ext", ["js", "jsx"])
def test_source_controls_keep_dom_and_global_navigation_candidates(tmp_path, ext):
    rows = scan(tmp_path, 'const input = location.hash;\n'
                'panel.innerHTML = input;\nlocation = input;\n', ext)
    assert sink_lines(rows, "innerHTML") == {2}
    assert sink_lines(rows, "navigation") == {3}
    assert any(row["sink"] == "innerHTML" and row["confidence"] == "high"
               for row in rows)


@pytest.mark.parametrize("ext,prefix", [
    ("js", 'import { send } from "./api/client.js";'),
    ("js", 'const endpoint = "/api/upload";'),
    ("js", 'const caption = `Upload ${count} files`;'),
    ("js", 'const ratio = total / count;'),
    ("jsx", 'const banner = <section><span>Upload</span></section>;'),
])
def test_unrelated_source_prefix_does_not_prevent_local_exclusions(tmp_path, ext, prefix):
    # A realistic module prefix must not turn known local receivers back into
    # HTML/navigation candidates. Real sinks in the same function still count.
    rows = scan(tmp_path, prefix + '\nfunction submit() {\n'
                'const location = useLocation();\n'
                'const data = new FormData();\n'
                'data.append("label", location.hash);\n'
                '$("#preview").append(location.hash);\n'
                'window.location.href = next;\n}\n', ext)
    assert sink_lines(rows, "jquery-html") == {6}
    assert sink_lines(rows, "navigation") == {7}


def test_separate_functions_can_each_construct_native_formdata(tmp_path):
    rows = scan(tmp_path, 'function saveDraft() {\n'
                'const data = new FormData();\n'
                'data.append("draft", draft);\n}\n'
                'function submit() {\nconst data = new FormData();\n'
                'data.append("label", location.hash);\n'
                '$("#preview").append(location.hash);\n}\n')
    assert sink_lines(rows, "jquery-html") == {8}


@pytest.mark.parametrize("local_binding", [
    'const FormData = CustomHtmlBuilder;',
    'class FormData { append(value) { render(value); } }',
])
def test_prior_native_usage_does_not_clear_current_local_constructor_shadow(tmp_path, local_binding):
    rows = scan(tmp_path, 'function saveDraft() {\n'
                'const data = new FormData();\n'
                'data.append("draft", draft);\n}\n'
                'function renderPreview() {\n' + local_binding + '\n'
                'const data = new FormData();\n'
                'data.append(location.hash);\n}\n')
    assert sink_lines(rows, "jquery-html") == {8}


def test_semicolonless_native_formdata_declaration_and_append(tmp_path):
    rows = scan(tmp_path, 'function submit() {\n'
                'const data = new FormData()\n'
                'data.append("label", location.hash)\n'
                '$("#preview").append(location.hash)\n}\n')
    assert sink_lines(rows, "jquery-html") == {4}


def test_large_unrelated_prefix_does_not_disable_local_receiver_evidence(tmp_path):
    # A modest generated module, not a stress test: local proof should survive
    # being beyond 32 KiB without requiring whole-file lexical acceptance.
    prefix = ''.join('const label%d = "ordinary upload label";\n' % index
                     for index in range(900))
    assert len(prefix.encode("utf-8")) > 32 * 1024
    first_local_line = prefix.count('\n') + 1
    rows = scan(tmp_path, prefix + 'function submit() {\n'
                'const data = new FormData();\n'
                'data.append("label", location.hash);\n'
                '$("#preview").append(location.hash);\n}\n')
    assert sink_lines(rows, "jquery-html") == {first_local_line + 3}


def test_native_upload_receiver_survives_append_and_caption_condition(tmp_path):
    rows = scan(tmp_path, 'function upload(file, caption) {\n'
                'const form = new FormData()\n'
                "form.append('file', file)\n"
                "if (caption) form.append('caption', caption)\n"
                '$("#preview").append(location.hash)\n}\n')
    assert sink_lines(rows, "jquery-html") == {5}


@pytest.mark.parametrize("conditional,expected", [
    ('if ((data = other)) data.append(location.hash);', {4}),
    ('if (caption) { data = other; data.append(location.hash); }', {4}),
    ('if (caption) data = other;\ndata.append(location.hash);', {5}),
])
def test_condition_or_branch_receiver_reassignment_keeps_candidate(tmp_path, conditional, expected):
    rows = scan(tmp_path, 'let data = new FormData()\n'
                'data.append("file", file)\n'
                '// The earlier append does not prove a later receiver is native.\n'
                + conditional)
    assert sink_lines(rows, "jquery-html") == expected


@pytest.mark.parametrize("source", [
    'const note = `${FormData = CustomHtmlBuilder}`;\n'
    'const data = new FormData();\n'
    'data.append(location.hash);',
    'const data = new FormData();\n'
    'const note = `${data = other}`;\n'
    'data.append(location.hash);',
])
def test_evaluated_template_interpolation_mutations_keep_append_candidate(tmp_path, source):
    # Interpolations execute expressions: treating the whole template as inert
    # text must not hide constructor or receiver reassignment.
    assert sink_lines(scan(tmp_path, source), "jquery-html") == {3}


def test_later_jsx_text_apostrophe_does_not_invalidate_earlier_local_evidence(tmp_path):
    # The apostrophe is JSX text, not the start of a JavaScript string. Later
    # source must neither erase earlier local proof nor clear unknown sinks.
    rows = scan(tmp_path, 'function RegisterPage() {\n'
                'const location = useLocation();\n'
                'const form = new FormData();\n'
                'form.append("file", file);\n'
                "return <p>Google'la kayıt</p>;\n"
                '}\nfunction later(unknown, next) {\n'
                'unknown.append(location.hash);\n'
                'window.location.href = next;\n}\n', "jsx")
    assert sink_lines(rows, "jquery-html") == {8}
    assert sink_lines(rows, "navigation") == {9}
