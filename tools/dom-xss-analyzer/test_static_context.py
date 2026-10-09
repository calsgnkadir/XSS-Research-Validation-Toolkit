"""R8 independent counterexamples: confidence is a candidate, never execution."""
import pytest
import dxa


def scan(tmp_path, code, ext="py"):
    path = tmp_path / ("case." + ext)
    path.write_text(code, encoding="utf-8")
    return dxa.scan_file(str(path))


@pytest.mark.parametrize("expr", ["sanitize(q)", "sanitize(q) + q", "html.escape(q) + q", "Markup(q)", "SafeString(q)"])
def test_wrappers_do_not_erase_raw_flow(tmp_path, expr):
    rows = scan(tmp_path, 'q = request.args["q"]\nout = ' + expr + '\nHTMLResponse(out)\n')
    assert next(r for r in rows if r['sink'] == 'fastapi-html')['confidence'] == 'high'


@pytest.mark.parametrize("sink", ["eval", "render_template_string"])
def test_html_escape_does_not_escape_code_or_template(tmp_path, sink):
    ext = "js" if sink == "eval" else "py"
    code = ('const q = location.hash;\neval(DOMPurify.sanitize(q));' if ext == 'js'
            else 'q = request.args["q"]\nrender_template_string(html.escape(q))')
    assert any(r['confidence'] == 'high' for r in scan(tmp_path, code, ext))


def test_unrelated_escaping_cannot_downgrade_sink(tmp_path):
    rows = scan(tmp_path, 'const q = location.hash;\nel.innerHTML = q; DOMPurify.sanitize(q);', 'js')
    assert next(r for r in rows if r['sink'] == 'innerHTML')['confidence'] == 'high'


def test_literal_semicolon_does_not_truncate_sink_expression(tmp_path):
    rows = scan(tmp_path, "const q = location.hash;\nel.innerHTML = '<b>;</b>' + q;", 'js')
    assert next(r for r in rows if r['sink'] == 'innerHTML')['confidence'] == 'high'


def test_html_escape_remains_lower_confidence_in_html_body(tmp_path):
    rows = scan(tmp_path, 'q = request.args["q"]\nHTMLResponse(html.escape(q))')
    assert rows and all(r['confidence'] != 'high' for r in rows)


def test_template_parameter_is_not_template_source(tmp_path):
    rows = scan(tmp_path, 'q = request.args["q"]\nrender_template_string("<p>{{ q }}</p>", q=q)')
    assert rows and all(r['confidence'] != 'high' for r in rows)


@pytest.mark.parametrize('ext,code,sink', [
    ('html', '<p th:utext="${q}"></p>', 'th-utext'),
    ('twig', '{{ q|raw }}', 'twig-raw'),
    ('jinja', '{{ q|safe }}', 'jinja-safe-filter'),
    ('vue', '<div v-html="q"></div>', 'vue-html'),
])
def test_real_template_extensions(tmp_path, ext, code, sink):
    rows = scan(tmp_path, code, ext)
    assert any(r['sink'] == sink for r in rows)
    assert list(dxa.iter_files(str(tmp_path)))


def test_unimported_same_name_does_not_taint_other_file(tmp_path):
    (tmp_path / 'util.py').write_text('def value():\n    return request.args["q"]\n', encoding='utf-8')
    target = tmp_path / 'app.py'
    target.write_text('def value():\n    return "constant"\nHTMLResponse(value())\n', encoding='utf-8')
    mapping = dxa.build_cross_file_taint_map(list(dxa.iter_files(str(tmp_path))))
    assert all(r['confidence'] != 'high' for r in dxa.scan_file(str(target), mapping))


def test_cs_sink_does_not_claim_local_taint(tmp_path):
    rows = scan(tmp_path, 'var q = Request.Query["q"];\nResponse.Write(q);', 'cs')
    assert rows and all(r['confidence'] != 'high' and not r['tainted_vars'] for r in rows)


def test_function_local_name_collision_is_isolated(tmp_path):
    rows = scan(tmp_path, 'def first():\n    q = request.args["q"]\n    return HTMLResponse(q)\n'
                'def second():\n    q = "constant"\n    return HTMLResponse(q)\n')
    assert [r['confidence'] for r in rows] == ['high', 'medium']


def test_later_source_does_not_taint_earlier_sink(tmp_path):
    rows = scan(tmp_path, 'q = "constant"\nHTMLResponse(q)\nq = request.args["q"]\n')
    assert rows[0]['confidence'] == 'medium'


def test_reassignment_is_conservative_without_control_flow(tmp_path):
    rows = scan(tmp_path, 'q = request.args["q"]\nif condition:\n    q = "constant"\nHTMLResponse(q)\n')
    assert rows[0]['confidence'] == 'high'


def test_template_safe_filter_keeps_raw_parameter_candidate(tmp_path):
    rows = scan(tmp_path, 'q = request.args["q"]\nrender_template_string("<p>{{ q|safe }}</p>", q=q)')
    assert any(r['confidence'] == 'high' for r in rows)


def test_encoded_assignment_retains_provenance_for_template(tmp_path):
    rows = scan(tmp_path, 'q = request.args["q"]\nout = html.escape(q)\n'
                'HTMLResponse(out)\nrender_template_string(out)')
    assert [r['confidence'] for r in rows] == ['medium', 'high']


def test_script_string_context_does_not_accept_html_encoding(tmp_path):
    rows = scan(tmp_path, 'q = request.args["q"]\n'
                'HTMLResponse("<script>run(" + html.escape(q) + ")</script>")')
    assert rows[0]['confidence'] == 'high'


def test_import_binding_from_other_module_does_not_collide(tmp_path):
    (tmp_path / 'unsafe.py').write_text('def value():\n    return request.args["q"]\n', encoding='utf-8')
    (tmp_path / 'safe.py').write_text('def value():\n    return "constant"\n', encoding='utf-8')
    target = tmp_path / 'app.py'
    target.write_text('from safe import value\nHTMLResponse(value())\n', encoding='utf-8')
    mapping = dxa.build_cross_file_taint_map(list(dxa.iter_files(str(tmp_path))))
    assert all(r['confidence'] != 'high' for r in dxa.scan_file(str(target), mapping))


@pytest.mark.parametrize('prefix,suffix', [
    ('<script>run(', ')</script>'), ('<style>', '</style>'),
    ('<a href="', '">link</a>'), ('<div data-value="', '">x</div>'),
])
def test_encoded_variable_cannot_sanitize_other_contexts(tmp_path, prefix, suffix):
    code = ('q = request.args["q"]\nencoded = html.escape(q)\n'
            f'out = {prefix!r} + encoded + {suffix!r}\nHTMLResponse(out)\n')
    assert scan(tmp_path, code)[0]['confidence'] == 'high'
