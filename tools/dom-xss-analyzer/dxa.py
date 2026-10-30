#!/usr/bin/env python3
"""
dxa - a source-to-sink XSS analyzer for full-stack code.

A heuristic static linter that flags XSS *sources*, *sinks*, and the likely
*source -> sink* flows between them, on both sides of a web app:

  * client side  - JavaScript / TypeScript (DOM XSS)
  * server side  - C# / ASP.NET & Razor (server-rendered XSS)

It is the source->sink methodology documented in this repository, expressed as
code. For JavaScript it also runs a light taint pass so a variable assigned from
a source and later used in a sink is raised to HIGH confidence.

What it is NOT
--------------
A *heuristic* built on regular expressions (plus a small taint pass for JS), not
a sound program analysis. No AST, no precise data-flow graph -> it has false
positives (matches in comments/strings) and false negatives (taint through
calls, aliasing, complex expressions). Use the output to prioritise, then confirm
each finding by hand.

Usage
-----
    python dxa.py <file-or-directory> [--json] [--min-confidence low|medium|high]

Exit code is non-zero when findings are reported, so it can gate a CI pipeline.
"""

import argparse
import ast
import dxa_evidence as evidence
import html
from html.parser import HTMLParser
import json
import os
import re
import sys
REPORT_EVENTS = []

# --- JavaScript / TypeScript sinks ------------------------------------------
JS_SINKS = [
    ("innerHTML",         re.compile(r'\.(?:inner|outer)HTML\s*='),
     "high",   "value assigned to (inner|outer)HTML is parsed as HTML"),
    ("insertAdjacentHTML", re.compile(r'\.insertAdjacentHTML\s*\('),
     "high",   "insertAdjacentHTML() parses its argument as HTML"),
    ("document.write",    re.compile(r'\bdocument\.write(?:ln)?\s*\('),
     "high",   "document.write(ln)() writes raw markup into the page"),
    ("eval",              re.compile(r'\beval\s*\('),
     "high",   "eval() executes its argument as JavaScript"),
    ("Function",          re.compile(r'\b(?:new\s+)?Function\s*\('),
     "high",   "the Function() constructor executes a string as code"),
    ("timer-string",      re.compile(r'\b(?:setTimeout|setInterval)\s*\(\s*[\'"`]'),
     "high",   "setTimeout/setInterval with a string argument runs it as code"),
    ("angular-bypass",    re.compile(r'bypassSecurityTrust\w*\s*\('),
     "high",   "Angular DomSanitizer bypass disables the framework's escaping"),
    ("react-dangerous",   re.compile(r'dangerouslySetInnerHTML'),
     "high",   "React dangerouslySetInnerHTML injects raw HTML"),
    ("jquery-html",       re.compile(r'\.(?:html|append|prepend|after|before|replaceWith|wrapAll|wrapInner|wrap)\s*\('),
     "medium", "jQuery HTML sink - inserts its argument as markup"),
    ("jquery-selector",   re.compile(r'\$\(\s*(?![\'"#.\[\]])[A-Za-z_$]'),
     "medium", "$() on a non-literal value can build and run HTML"),
    ("navigation",        re.compile(r'\blocation(?:\.href)?\s*=|\blocation\.(?:assign|replace)\s*\(|\bwindow\.open\s*\('),
     "medium", "navigation sink - a javascript: URL here executes"),
    ("setAttribute",      re.compile(r'\.setAttribute\s*\(\s*[\'"`](?:href|src|on\w+|formaction|xlink:href|data|style)[\'"`]'),
     "medium", "setAttribute() on a dangerous attribute"),
    ("src-href",          re.compile(r'\.(?:src|href)\s*='),
     "low",    "src/href assignment - javascript:/data: URLs may execute"),
]
JS_SOURCES = [
    ("location.hash",     re.compile(r'\blocation\.hash\b')),
    ("location.search",   re.compile(r'\blocation\.search\b')),
    ("location.href",     re.compile(r'\blocation\.href\b')),
    ("location.pathname", re.compile(r'\blocation\.pathname\b')),
    ("document.URL",      re.compile(r'\bdocument\.(?:URL|documentURI|baseURI)\b')),
    ("document.referrer", re.compile(r'\bdocument\.referrer\b')),
    ("window.name",       re.compile(r'\bwindow\.name\b')),
    ("document.cookie",   re.compile(r'\bdocument\.cookie\b')),
    ("web-storage",       re.compile(r'\b(?:local|session)Storage\b')),
    ("URL-params",        re.compile(r'\bURLSearchParams\b|\.searchParams\b')),
    ("history.state",     re.compile(r'\bhistory\.state\b')),
]
MSG_LISTENER = re.compile(r'addEventListener\s*\(\s*[\'"`]message[\'"`]|\.onmessage\s*=')
MSG_DATA = re.compile(r'\b[A-Za-z_$][\w$]*\.data\b')

# --- C# / ASP.NET & Razor sinks (server-rendered XSS) -----------------------
CS_SINKS = [
    ("Html.Raw",       re.compile(r'@?Html\.Raw\s*\('),
     "high",   "@Html.Raw() emits its argument as unescaped HTML"),
    ("Response.Write", re.compile(r'\bResponse\.Write\s*\('),
     "high",   "Response.Write() writes raw output straight into the response"),
    ("HtmlString",     re.compile(r'\bnew\s+(?:Mvc)?HtmlString\s*\('),
     "high",   "HtmlString/MvcHtmlString marks a string as trusted, un-encoded HTML"),
    ("MarkupString",   re.compile(r'\bnew\s+MarkupString\s*\(|\(\s*MarkupString\s*\)'),
     "high",   "Blazor MarkupString renders a string as raw HTML"),
    ("InnerHtml",      re.compile(r'\.InnerHtml\s*='),
     "high",   "control.InnerHtml assignment renders raw HTML"),
    ("Literal.Text",   re.compile(r'\.Text\s*=\s*(?![\'"])'),
     "low",    "Literal/Label .Text set from a dynamic value (raw when Mode=PassThrough)"),
]
CS_SOURCES = [
    ("Request.Query",   re.compile(r'\bRequest\.(?:Query|QueryString)\b')),
    ("Request.Form",    re.compile(r'\bRequest\.Form\b')),
    ("Request.Params",  re.compile(r'\bRequest\.Params\b|\bRequest\s*\[')),
    ("Request.Cookies", re.compile(r'\bRequest\.Cookies\b')),
    ("Request.Headers", re.compile(r'\bRequest\.Headers\b')),
    ("Request.Route",   re.compile(r'\bRequest\.RouteValues\b|\bRouteData\b')),
    ("Request.Body",    re.compile(r'\bRequest\.Body\b')),
]

# --- PHP sinks (server-side XSS: unescaped output) --------------------------
PHP_SINKS = [
    ("echo",         re.compile(r'\becho\s+[^;]*\$'),
     "high",   "echo of a variable - unescaped output is XSS unless htmlspecialchars() is applied"),
    ("print",        re.compile(r'\bprint\s+[^;]*\$'),
     "high",   "print of a variable - same class as echo"),
    ("short-echo",   re.compile(r'<\?=[^?]*\$'),
     "high",   "<?= $var ?> renders raw HTML; wrap with htmlspecialchars()"),
    ("printf-family", re.compile(r'\b(?:v?printf)\s*\('),
     "medium", "printf/vprintf can render dynamic content unescaped"),
    ("blade-raw",    re.compile(r'\{!!'),
     "high",   "Laravel Blade {!! !!} disables escaping (the safe form is {{ }})"),
    ("twig-raw",     re.compile(r'\|\s*raw\b'),
     "medium", "Twig |raw filter disables escaping"),
    ("file_put_contents", re.compile(r'\bfile_put_contents\s*\('),
     "low",    "file_put_contents may store attacker HTML that is later rendered raw"),
]
PHP_SOURCES = [
    ("$_GET",         re.compile(r'\$_GET\b')),
    ("$_POST",        re.compile(r'\$_POST\b')),
    ("$_REQUEST",     re.compile(r'\$_REQUEST\b')),
    ("$_COOKIE",      re.compile(r'\$_COOKIE\b')),
    ("$_SERVER",      re.compile(r'\$_SERVER\b')),                # incl. HTTP_* headers
    ("$_FILES",       re.compile(r'\$_FILES\b')),
    ("php://input",   re.compile(r'php://input')),
    ("Laravel-Request", re.compile(r'\bRequest::(?:input|all|get|post|query|cookie|header)\b|'
                                    r'\brequest\(\)\s*->\s*(?:input|all|get|post|query|cookie|header)\b')),
    ("Symfony-Request", re.compile(r'\$request\s*->\s*(?:query|request|cookies|headers|files|attributes)\b')),
]

# --- Python sinks (Flask/Jinja + FastAPI + Django) --------------------------
PY_SINKS = [
    ("markupsafe-markup",   re.compile(r'\bMarkup\s*\('),
     "high",   "markupsafe.Markup(x) marks the string as safe HTML - Jinja will render it raw"),
    ("render-template-str", re.compile(r'\brender_template_string\s*\('),
     "high",   "render_template_string(x) treats x itself as a Jinja template - full server-side template injection surface"),
    ("django-mark-safe",    re.compile(r'\bmark_safe\s*\(|SafeString\s*\('),
     "high",   "Django mark_safe / SafeString bypasses auto-escaping"),
    ("django-format-html",  re.compile(r'\bformat_html(?:_join)?\s*\(\s*[\'"][^\'"]*%s'),
     "medium", "format_html with a raw %s in the template placeholder"),
    ("fastapi-html",        re.compile(r'\bHTMLResponse\s*\('),
     "medium", "FastAPI HTMLResponse renders its argument as raw HTML"),
    ("flask-response-html", re.compile(r'\bResponse\s*\([^)]*mimetype\s*=\s*[\'"]text/html[\'"]|make_response\s*\('),
     "medium", "Flask Response/make_response with text/html mimetype and a dynamic body"),
    ("jinja-safe-filter",   re.compile(r'\|\s*safe\b'),
     "high",   "Jinja |safe filter disables auto-escaping (used on a value = raw HTML)"),
    ("html-tostring",       re.compile(r'\blxml\.html\.tostring\s*\(|\bBeautifulSoup\s*\('),
     "low",    "lxml/BeautifulSoup HTML build - source injection depends on where the result flows"),
    ("os-system",           re.compile(r'\b(?:os\.system|os\.popen|subprocess\.(?:call|run|Popen))\s*\(\s*[a-zA-Z_]'),
     "medium", "OS command sink - not XSS but a Python-only injection class worth flagging"),
]
PY_SOURCES = [
    ("flask-request-arg",   re.compile(r'\brequest\s*\.\s*args\s*(?:\.\s*get\s*\(|\[)')),
    ("flask-request-form",  re.compile(r'\brequest\s*\.\s*form\s*(?:\.\s*get\s*\(|\[)')),
    ("flask-request-values",re.compile(r'\brequest\s*\.\s*values\s*(?:\.\s*get\s*\(|\[)')),
    ("flask-request-json",  re.compile(r'\brequest\s*\.\s*get_json\s*\(|\brequest\s*\.\s*json\b')),
    ("flask-request-cookie",re.compile(r'\brequest\s*\.\s*cookies\s*(?:\.\s*get\s*\(|\[)')),
    ("flask-request-header",re.compile(r'\brequest\s*\.\s*headers\s*(?:\.\s*get\s*\(|\[)')),
    ("flask-view-args",     re.compile(r'\brequest\s*\.\s*view_args\b')),
    ("fastapi-param",       re.compile(r'=\s*(?:Query|Body|Header|Cookie|Path|Form|File)\s*\(')),
    ("django-request-get",  re.compile(r'\brequest\s*\.\s*GET\s*(?:\.\s*get\s*\(|\[)')),
    ("django-request-post", re.compile(r'\brequest\s*\.\s*POST\s*(?:\.\s*get\s*\(|\[)')),
    ("django-request-meta", re.compile(r'\brequest\s*\.\s*META\s*(?:\.\s*get\s*\(|\[)')),
    ("environ",             re.compile(r'\bos\.environ(?:\.\s*get\s*\(|\[)')),
    ("input-stdin",         re.compile(r'\bsys\.stdin\.(?:read|readline)\b|\binput\s*\(')),
]


# --- Java / JSP / Thymeleaf sinks (server-side XSS: unescaped output) -------
JAVA_SINKS = [
    ("servlet-writer",  re.compile(r'\b(?:getWriter\(\)|PrintWriter\s*\.\s*\w+)\s*\.\s*(?:print(?:ln)?|write|append)\s*\('),
     "high",   "Servlet PrintWriter print/println/write emits raw response body"),
    ("servlet-output",  re.compile(r'\bServletOutputStream\b.*\.(?:print|write)\s*\('),
     "high",   "ServletOutputStream writes raw bytes to the response"),
    ("response-write",  re.compile(r'\bresponse\s*\.\s*getWriter\(\)\s*\.\s*(?:print(?:ln)?|write|append)\s*\('),
     "high",   "response.getWriter() writes raw output"),
    ("jsp-expr",        re.compile(r'<%=[^%]*(?:request|param|session|cookie|\bvar\b|\$)'),
     "high",   "JSP <%= %> scriptlet emits value unescaped (unless htmlEscape wraps it)"),
    ("jsp-el-unescape", re.compile(r'<c:out[^>]+escapeXml\s*=\s*"false"'),
     "high",   "<c:out escapeXml=\"false\"> disables the default JSP escaping"),
    ("th-utext",        re.compile(r'\bth:utext\b'),
     "high",   "Thymeleaf th:utext renders content as raw HTML (th:text is the safe form)"),
    ("th-inline-unesc", re.compile(r'\[\(\$\{[^}]+\}\)\]'),
     "high",   "Thymeleaf [(${...})] inline-unescape; [[${...}]] is the escaped form"),
    ("jsoup-html",      re.compile(r'\.html\s*\(\s*(?![\'"`])'),
     "medium", "jsoup Element.html(x) parses its argument as HTML"),
    ("response-header", re.compile(r'\bresponse\s*\.\s*(?:setHeader|addHeader)\s*\('),
     "low",    "response header write - reflecting user input into a header can enable XSS in old browsers or via error pages"),
]
JAVA_SOURCES = [
    ("request.param",       re.compile(r'\brequest\s*\.\s*getParameter(?:Values|Map)?\s*\(')),
    ("request.header",      re.compile(r'\brequest\s*\.\s*getHeader(?:Names|s)?\s*\(')),
    ("request.cookies",     re.compile(r'\brequest\s*\.\s*getCookies\s*\(|\bCookie\s*\.\s*getValue\s*\(')),
    ("request.body",        re.compile(r'\brequest\s*\.\s*getReader\s*\(|\bgetInputStream\s*\(')),
    ("request.uri",         re.compile(r'\brequest\s*\.\s*(?:getRequestURI|getRequestURL|getQueryString|getPathInfo)\s*\(')),
    ("spring-param",        re.compile(r'@RequestParam\b|@RequestHeader\b|@PathVariable\b|@CookieValue\b|@RequestBody\b|@ModelAttribute\b')),
    ("session-attr",        re.compile(r'\bsession\s*\.\s*getAttribute\s*\(')),
    ("system-in-input",     re.compile(r'\bSystem\s*\.\s*in\b|\bnew\s+Scanner\s*\(\s*System\s*\.\s*in\s*\)')),
]

ASSIGN = re.compile(r'^\s*(?:var|let|const)?\s*([A-Za-z_$][\w$]*)\s*=\s*(.+?)\s*;?\s*$')
PHP_ASSIGN = re.compile(r'^\s*(\$[A-Za-z_]\w*)\s*=\s*(.+?)\s*;?\s*$')
# Java: `Type name = expr;` or `name = expr;` (type is optional, may be generic)
JAVA_ASSIGN = re.compile(
    r'^\s*(?:(?:final|static|public|private|protected|volatile|synchronized)\s+)*'
    r'(?:[\w<>\[\],?.\s]{1,80}?\s+)?'
    r'([A-Za-z_]\w*)\s*=\s*(.+?)\s*;?\s*$'
)
# Python: `name = expr` or `name: type = expr` (no ; terminator, no let/var)
PYTHON_ASSIGN = re.compile(
    r'^\s*([A-Za-z_]\w*)\s*(?::\s*[\w\[\], .]+?\s*)?=\s*(.+?)\s*$'
)
CONF_RANK = {"low": 0, "medium": 1, "high": 2}
JS_EXT = (".js", ".ts", ".jsx", ".tsx", ".mjs")
CS_EXT = (".cs", ".cshtml", ".razor")
PHP_EXT = (".php", ".phtml", ".php3", ".php4", ".php5", ".phps", ".inc")
JAVA_EXT = (".java", ".jsp", ".jspx", ".tag")
PY_EXT   = (".py", ".pyw")
TEMPLATE_EXT = (".html", ".htm", ".twig", ".jinja", ".jinja2", ".vue")
TEMPLATE_SINKS = [s for s in JAVA_SINKS if s[0] in ("th-utext", "th-inline-unesc")]
TEMPLATE_SINKS += [s for s in PHP_SINKS if s[0] == "twig-raw"]
TEMPLATE_SINKS += [s for s in PY_SINKS if s[0] == "jinja-safe-filter"]
TEMPLATE_SINKS += [("vue-html", re.compile(r'\bv-html\s*='), "high",
                    "Vue v-html renders raw HTML; template data flow is not resolved")]


def source_hits(text, sources, msg_active):
    """Names of sources *read* in `text`. A source that is the target of an
    assignment (e.g. `location.href = x`) is a write, not a read, so skip it."""
    hits = []
    for name, rx in sources:
        for m in rx.finditer(text):
            after = text[m.end():].lstrip()
            if after[:1] == "=" and after[1:2] != "=":
                continue  # write target, not a read
            hits.append(name)
            break
    if msg_active:
        # Existing JS callers keep their historical broad heuristic. Inline
        # HTML supplies a callback-specific regex and requires a lexical read.
        message_text = _js_binding_view(text) if isinstance(msg_active, re.Pattern) else text
        message_rx = msg_active if isinstance(msg_active, re.Pattern) else MSG_DATA
        if message_text is not None and message_rx.search(message_text):
            hits.append("postMessage.data")
    return hits


# v3.9 finding dedup. When the same line matches multiple sink patterns that
# overlap semantically (a specific one is a subset of a general one), report
# ONLY the general - the specific was there for extra clarity but a single
# HIGH row per line is what the operator wants.
# Pairs are (specific, general): if `general` also matched on this line,
# drop the specific finding.
SINK_SUPPRESSIONS = [
    ("src-href",       "navigation"),      # location.href/src writes -> navigation covers it
    ("response-write", "servlet-writer"),  # response.getWriter().*() also matches servlet-writer

    # Phase 0.1 widening. Each pair below is (loser, winner): when both regexes
    # match on the same line, drop the LOSER's finding. Verified against the
    # regex sources - each pair has a real-world source shape that trips both.
    ("innerHTML",         "angular-bypass"),      # elem.innerHTML = this.sanitizer.bypassSecurityTrustHtml(x)
                                                  #   -> the bypass call is the actionable signal; the .innerHTML=
                                                  #   assignment is just its target. Report once, as angular-bypass.
    ("jsp-expr",          "jsp-el-unescape"),     # <c:out escapeXml="false"><%=request.getParameter("x")%></c:out>
                                                  #   -> the c:out escapeXml="false" tells the operator WHY the JSP
                                                  #   expression is dangerous. Keep the more informative one.
    ("markupsafe-markup", "django-mark-safe"),    # mark_safe(Markup(user_input))
                                                  #   -> the outer django-mark-safe is idiomatic-Django context;
                                                  #   report as django-mark-safe, drop the inner Markup() noise.
    ("th-utext",          "th-inline-unesc"),     # <span th:utext="${x}">[(${x})]</span> mixes both Thymeleaf
                                                  #   unescape mechanisms on one node; the [( ... )] inline form
                                                  #   is the less-known one worth surfacing.
    ("jinja-safe-filter", "render-template-str"), # render_template_string("...{{ x | safe }}...")
                                                  #   -> render_template_string on user data is the whole-class
                                                  #   attack; the |safe filter inside is a symptom. Report the class.
]


def _joined_for_taint(lines, terminator=";", max_join=8):
    """Return a list the same length as `lines`. Each entry is the original
    line concatenated with continuation lines up to the next `terminator`
    (default `;`). Preserves indexing so tainted-set computation sees complete
    multi-line statements (Java/C# ternaries, long argument lists) without
    breaking scan_file's per-line reporting. v3.8 addition - needed to catch
    the exact hotel-platform shape:
        String cid = (inbound != null && ...)
                ? sanitize(inbound)
                : shortUuid();
    which otherwise splits across 3 lines and hides the sanitize()."""
    joined = list(lines)
    for i, line in enumerate(lines):
        s = line.strip()
        # already terminated on this line, or a block delimiter, or empty
        if terminator in line or not s or s.endswith(("{", "}")) or s.startswith(("//", "#")):
            continue
        buf = line
        for k in range(1, max_join + 1):
            if i + k >= len(lines):
                break
            nxt = lines[i + k]
            buf = buf + " " + nxt.strip()
            if terminator in nxt:
                break
        joined[i] = buf
    return joined


# Phase 0.4 (2026-09-26): cross-file taint pre-pass. When the project
# scan starts, walk every file once and build a `set()` of function
# names whose body includes `return <raw source>` (returning a request /
# location / superglobal directly). During compute_taint, a call to any
# name in that set is treated the same as a direct source access - the
# assignment target becomes tainted. Regex-based, no AST, no import
# resolution: cross-file taint is proven by name-shape only, which is
# imprecise but catches the common util.py -> app.py shape.
# Java / C# skipped here (class + method resolution needs more machinery
# than regex; scheduled for Phase 4 tree-sitter work).
_FUNC_DEF_RE = {
    "py":  re.compile(r'^\s*def\s+(\w+)\s*\('),
    "js":  re.compile(r'^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\('),
    "php": re.compile(r'^\s*(?:public\s+|private\s+|protected\s+|static\s+)*'
                      r'function\s+(\w+)\s*\('),
}
_RETURN_TAINTED_RE = {
    "py":  re.compile(r'\breturn\b[^#]*?('
                      r'request\s*\.\s*(?:args|form|values|json|cookies|'
                      r'headers|view_args|GET|POST|META)|'
                      r'os\.environ|sys\.stdin|input\s*\(|'
                      r'flask\.request|starlette.*request)'),
    "js":  re.compile(r'\breturn\b[^;]*?('
                      r'document\s*\.\s*(?:location|URL|referrer|cookie|'
                      r'documentURI|baseURI)|'
                      r'window\s*\.\s*(?:location|name)|'
                      r'\blocation\s*\.\s*(?:hash|search|href|pathname)|'
                      r'(?:local|session)Storage)'),
    "php": re.compile(r'\breturn\b[^;]*?\$_(?:GET|POST|REQUEST|COOKIE|'
                      r'SERVER|FILES|SESSION|ENV)\b'),
}


def _raw_return_names(paths):
    """Return `set()` of function names whose body includes `return <source>`.
    Function-body tracking is language-shaped:
      - Python: indent-based (body ends when indent <= def's own indent).
      - JS / PHP: brace-depth counter from the opening `{`.
    Both approaches are approximations - nested defs, decorators that eat
    the body, and single-expression arrow functions can be missed. Anything
    the pre-pass misses stays medium/low; nothing here can UPGRADE a wrong
    signal (misclassifying a benign function as tainted-returning would
    just raise a MEDIUM to HIGH for its callers - still triage-worthy)."""
    tainted_funcs = set()
    for path in paths:
        lang = _lang_for(path)[0]
        if lang not in _FUNC_DEF_RE:
            continue
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                lines = fh.read().split("\n")
        except OSError:
            continue
        def_re = _FUNC_DEF_RE[lang]
        ret_re = _RETURN_TAINTED_RE[lang]
        if lang == "py":
            current, base_indent = None, -1
            for line in lines:
                m = def_re.match(line)
                if m:
                    current = m.group(1)
                    base_indent = len(line) - len(line.lstrip())
                    continue
                if current is None:
                    continue
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                line_indent = len(line) - len(line.lstrip())
                if line_indent <= base_indent:
                    current, base_indent = None, -1
                    continue
                if ret_re.search(line):
                    tainted_funcs.add(current)
        else:                                       # js / php - brace depth
            current, depth = None, 0
            for line in lines:
                # Comments strip - shallow but avoids most FP inside a /* */
                stripped_line = re.sub(r'//.*$', '', line)
                if current is None:
                    m = def_re.match(line)
                    if not m:
                        continue
                    current = m.group(1)
                    depth = (stripped_line.count("{") -
                             stripped_line.count("}"))
                    if depth == 0:
                        # single-line function - inspect same line for return
                        if ret_re.search(line):
                            tainted_funcs.add(current)
                        current = None
                    continue
                if ret_re.search(line):
                    tainted_funcs.add(current)
                depth += stripped_line.count("{") - stripped_line.count("}")
                if depth <= 0:
                    current, depth = None, 0
    return tainted_funcs


class _InlineScriptSpans(HTMLParser):
    """Executable inline HTML script offsets only; never execute document code."""

    _INERT = {'template', 'noscript', 'textarea', 'title', 'xmp', 'iframe',
              'noembed', 'noframes', 'style', 'svg', 'math'}
    _TYPES = {'', 'module', 'text/javascript', 'application/javascript',
              'text/ecmascript', 'application/ecmascript'}

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.offsets = [0]
        for match in re.finditer('\n', source):
            self.offsets.append(match.end())
        self.inert, self.script, self.spans = [], None, []
        self.ambiguous = False

    def _offset(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            values = dict(attrs)
            executable = (not self.inert and not self.ambiguous and len(values) == len(attrs)
                          and 'src' not in values
                          and (values.get('type') or '').strip().lower() in self._TYPES
                          and (values.get('language') or 'javascript').lower() in
                          {'javascript', 'ecmascript'})
            self.script = (self._offset() + len(self.get_starttag_text()), executable)
        elif tag in self._INERT:
            self.inert.append(tag)

    def handle_endtag(self, tag):
        if tag == 'script' and self.script is not None:
            start, executable = self.script
            if executable:
                self.spans.append((start, self._offset()))
            self.script = None
        elif tag in self.inert:
            self.inert = self.inert[:self.inert.index(tag)]

    def handle_startendtag(self, tag, attrs):
        # Self-closing scripts are ambiguous in HTML, so supply no proof.
        if tag == 'script' or tag in self._INERT:
            self.ambiguous = True


def _inline_message_regions(source, path):
    """Bounded HTML message provenance, not a JavaScript/HTML execution proof.

    Supported: .html/.htm executable inline scripts, literal direct window
    addEventListener('message', single_parameter => {...}) or function(parameter)
    callbacks, flat bodies up to 32 KiB. Nested blocks/functions, templates,
    slash ambiguity, options, onmessage, destructuring and aliases are outside
    this subset. Parameter mutation/escape ends the supported source interval;
    propagation after that boundary is deliberately not inferred. Other sinks
    remain ordinary existing candidates with their physical source lines.
    """
    parser = _InlineScriptSpans(source)
    try:
        parser.feed(source)
        parser.close()
    except AssertionError:
        # HTMLParser rejects malformed marked declarations with AssertionError.
        # Abandon provenance, preserve generic findings, expose the parse error.
        REPORT_EVENTS.append(evidence.ReportEvent(
            'static-inline-html', 'error', 'HTMLParser rejected malformed markup', str(path)))
        return []
    regions = []
    identifier = r'[A-Za-z_$][\w$]*'
    header_rx = re.compile(
        r'(?<![\w$.])window\s*\.\s*addEventListener\s*\(\s*'
        r'([\'"])message\1\s*,\s*(?:'
        r'(?P<arrow>' + identifier + r')\s*=>|'
        r'\(\s*(?P<paren>' + identifier + r')\s*\)\s*=>|'
        r'function\s*\(\s*(?P<function>' + identifier + r')\s*\))\s*\{')
    for script_start, script_end in parser.spans:
        script = source[script_start:script_end]
        view = _js_binding_view(script)
        if view is None:
            continue
        if '<!--' in view or '-->' in view:
            # Legacy HTML-comment JavaScript syntax is not in this subset.
            continue
        for header in header_rx.finditer(script):
            if _js_binding_view(header.group()) != view[header.start():header.end()]:
                continue
            start = header.end()
            end = view.find('}', start, start + 32769)
            if end < 0:
                continue
            body = view[start:end]
            if (re.search(r'[{}?]|=>|\b(?:function|class|for|while|switch|try|with)\b', body)
                    or not re.match(r'\s*\)', view[end + 1:])):
                continue
            receiver = header.group('arrow') or header.group('paren') or header.group('function')
            name = re.escape(receiver)
            # Unknown receiver escapes and writes cannot remain event reads.
            # Direct .origin reads permit a flat guard, without proving safety.
            stop = len(body)
            for use in re.finditer(r'(?<![\w$.])' + name + r'(?![\w$])', body):
                after = body[use.end():]
                prop = re.match(r'\s*\.\s*(?:data|origin)\b', after)
                if (prop is None
                        or re.search(r'(?:\+\+|--|\bdelete)\s*$', body[:use.start()])
                        or re.match(r'\s*(?:=(?!=)|(?:\*\*|&&|\|\||\?\?|[+*/%&|^-])=|\+\+|--)',
                                    after[prop.end():])):
                    stop = use.start()
                    break
            message_rx = re.compile(r'(?<![\w$.])' + name + r'\s*\.\s*data\b')
            regions.append((script_start + start, script_start + start + stop,
                            message_rx, body[:stop]))
    return regions


def _inline_taint_prefix(source):
    """Split flat callback statements without splitting quoted semicolons."""
    view = _js_binding_view(source)
    if view is None:
        return []
    statements, start = [], 0
    for separator in re.finditer(r'[;\n]', view):
        code = view[start:separator.start()]
        if code.strip():
            first = start + len(code) - len(code.lstrip())
            statements.append(source[first:separator.start()])
        start = separator.end()
    if view[start:].strip():
        first = start + len(view[start:]) - len(view[start:].lstrip())
        statements.append(source[first:])
    return statements


def _js_template_end(text, start, nesting=0):
    """Skip an opaque template, including balanced interpolation/nesting.

    Slash expressions inside interpolation are uncertain; do not infer a
    lexical proof from such a template. This helper never analyzes its values.
    """
    if nesting >= 32:
        return None
    i, depth = start + 1, 0
    while i < len(text):
        char = text[i]
        if char == '\\':
            i += 2
            continue
        if depth == 0:
            if char == '`':
                return i + 1
            if text.startswith('${', i):
                depth = 1
                i += 2
                continue
        elif char == '`':
            i = _js_template_end(text, i, nesting + 1)
            if i is None:
                return None
            continue
        elif char in ('"', "'"):
            quote = char
            i += 1
            while i < len(text) and text[i] != quote:
                i += 2 if text[i] == '\\' else 1
            if i >= len(text):
                return None
        elif char == '/':
            return None
        elif char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
        i += 1
    return None


def _js_binding_view(text):
    """Offset-preserving lexical view for narrow receiver proofs only.

    Comments and quoted literals cannot supply declarations. Opaque templates
    and slash expressions invalidate a proof only in its relevant interval.
    This is not a JavaScript parser or a general receiver type analysis.
    """
    out = list(text)
    i = 0
    while i < len(text):
        if text.startswith('//', i):
            end = text.find('\n', i)
            end = len(text) if end < 0 else end
        elif text.startswith('/*', i):
            end = text.find('*/', i + 2)
            if end < 0:
                return ''.join(out[:i]) + '?' * (len(text) - i)
            end += 2
        elif text[i] in ('"', "'"):
            quote, end = text[i], i + 1
            while end < len(text) and text[end] != quote:
                if text[end] == '\\':
                    end += 1
                elif text[end] == '\n':
                    return ''.join(out[:i]) + '?' * (len(text) - i)
                end += 1
            if end >= len(text):
                return ''.join(out[:i]) + '?' * (len(text) - i)
            end += 1
            # A literal is an opaque value, not whitespace between tokens.
            out[i:end] = '0' + ' ' * (end - i - 1)
            i = end
            continue
        elif text[i] == '`':
            end = _js_template_end(text, i)
            if end is None:
                # Keep earlier proofs available, but nothing after an opaque
                # boundary can establish a declaration/receiver identity.
                out[i:] = '?' * (len(text) - i)
                return ''.join(out)
            # Preserve uncertainty and possible constructor mutation hidden in
            # interpolation; never treat template text as ordinary code.
            marker = '?FormData?' if re.search(r'\bFormData\b', text[i:end]) else '?'
            out[i:end] = marker + ' ' * (end - i - len(marker))
            i = end
            continue
        elif text[i] == '/':
            end = text.find('\n', i)
            end = len(text) if end < 0 else end
            marker = '?FormData?' if re.search(r'\bFormData\b', text[i:end]) else '?'
            out[i:end] = marker + ' ' * (end - i - len(marker))
            i = end
            continue
        else:
            i += 1
            continue
        out[i:end] = ''.join('\n' if c == '\n' else ' ' for c in text[i:end])
        i = end
    return ''.join(out)


def _js_constructor_shadows(view):
    """Index lexical constructor shadows without resolving JavaScript values.

    Only explicit local declarations/recognized function parameters are local.
    Imports, unresolved references and mutations without a local binding stay
    global barriers. Block boundaries are lexical, not a control-flow model.
    """
    if view is None:
        return [(0, 0)]
    scopes = [{'start': 0, 'end': len(view), 'parent': None}]
    stack, references, bodies = [0], [], {}
    for token in re.finditer(r'[{}]|\bFormData\b', view):
        if token.group() == '{':
            index = len(scopes)
            scopes.append({'start': token.start(), 'end': len(view), 'parent': stack[-1]})
            bodies[token.start()] = index
            stack.append(index)
        elif token.group() == '}':
            if len(stack) > 1:
                scopes[stack.pop()]['end'] = token.end()
        elif not re.search(r'\bnew\s+$', view[max(0, token.start() - 32):token.start()]):
            references.append((token.start(), stack[-1]))
    parameters = []
    for header in re.finditer(
            r'\bfunction(?:\s+[\w$]+)?\s*\([^{};]*\)\s*\{'
            r'|(?:\([^{};]*\)|\bFormData)\s*=>\s*\{', view):
        body = bodies.get(header.end() - 1)
        if body is not None:
            header_text = header.group()[:-1]
            # Recognize bare parameter bindings, not FormData reads/mutations
            # in a default expression or a nested parameter expression.
            if header_text.count('(') == header_text.count(')') == 1:
                for parameter in re.finditer(r'(?<=[(,])\s*FormData\b(?=\s*[,)=])', header_text):
                    position = header.start() + header_text.index('FormData', parameter.start())
                    parameters.append((position, position + len('FormData'), body))
            elif re.fullmatch(r'FormData\s*=>\s*', header_text):
                parameters.append((header.start(), header.start() + len('FormData'), body))
    bindings, owners = set(), {}
    for position, scope in references:
        parameter = next((body for start, end, body in parameters
                          if start <= position < end), None)
        if parameter is not None:
            owner = parameter
        elif re.search(r'\b(?:const|let|class)\s+$', view[max(0, position - 32):position]):
            owner = scope
        elif re.search(r'\bvar\s+$', view[max(0, position - 32):position]):
            # Hoisted var in an uncertain block/function stays conservative.
            owner = 0
        else:
            continue
        bindings.add(owner)
        owners[position] = owner
    barriers = set()
    for position, scope in references:
        owner = owners.get(position)
        # A property such as window.FormData can mutate the global constructor
        # even when the surrounding function also has a local FormData name.
        if re.search(r'\.\s*$', view[max(0, position - 32):position]):
            owner = 0
        if owner is None:
            while scope not in bindings and scopes[scope]['parent'] is not None:
                scope = scopes[scope]['parent']
            owner = scope if scope in bindings else 0
        barriers.add(owner)
    return [(scopes[index]['start'], scopes[index]['end']) for index in barriers]


def _js_non_sink_binding(view, offset, line, match, sid, constructor_shadows):
    """Prove only measured FormData append / React declaration false alarms.

    Scope transitions, aliases and uncertain syntax retain the candidate. A
    proof applies to this match, never to every sink on its line or in a file.
    Receiver lookup is bounded to 32 KiB before the match, not the file start.
    Unresolved constructor references remain global barriers; explicit local
    shadows affect their lexical region only. This does not resolve imports,
    computed property mutation, dynamic execution or arbitrary call effects.
    """
    if sid not in ('jquery-html', 'navigation'):
        return False
    if view is None:
        return False
    position = offset + match.start()
    if view[position:offset + match.end()] != match.group():
        return False
    start = max(0, position - 32768)
    before = ('?' if start else '') + view[start:position]
    if sid == 'navigation':
        # Only the declaration itself, never later location writes or hrefs.
        return (bool(re.fullmatch(r'location\s*=', match.group()))
                and bool(re.search(r'(?:^|[;{}\n])[^\S\n]*const\s+$', before))
                and bool(re.match(r'\s*useLocation\s*\(\s*\)\s*(?:;|$)',
                                  line[match.end():])))
    if not re.fullmatch(r'\.append\s*\(', match.group()):
        return False
    if any(start <= position < end for start, end in constructor_shadows):
        return False
    receiver = re.search(r'(?<![\w$.])([A-Za-z_$][\w$]*)\s*$', before)
    if receiver is None:
        return False
    name = re.escape(receiver.group(1))
    declarations = list(re.finditer(
        r'(?:^|[;{}\n])[^\S\n]*(?:const|let|var)\s+' + name
        + r'\s*=\s*new\s+FormData\s*\(\s*'
        + r'(?:[A-Za-z_$][\w$]*(?:\s*\.\s*[A-Za-z_$][\w$]*)*)?'
        + r'[^\S\n]*\)[^\S\n]*(?:;|\n)', before))
    if not declarations:
        return False
    declaration = declarations[-1]
    between = before[declaration.end():receiver.start()]
    # No scope transition/loop, rebinding, escape, or unknown receiver use.
    # A condition-only `if (caption)` is allowed; a receiver reference in that
    # condition (including an assignment) fails the remaining-name check below.
    if re.search(r'[{}?]|\b(?:for|while|switch|try|with|function|class|FormData)\b|=>', between):
        return False
    uses = re.sub(r'(?<![\w$])' + name + r'\s*\.\s*append\s*\(', '(', between)
    if re.search(r'(?<![\w$])' + name + r'(?![\w$])', uses):
        return False
    return True


def _closing_paren(text, opening):
    """Small lexical helper, not a language parser. Fail closed on truncation."""
    depth, quote, escaped = 0, None, False
    for i in range(opening, len(text)):
        char = text[i]
        if quote:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ('"', "'", '`'):
            quote = char
        elif char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0:
                return i
    return None


# HTML-body mitigation hints only. A matching spelling is not a guarantee that
# the library has not been rebound/configured insecurely. Never trust local
# sanitize/clean/validate names, Markup or SafeString as encoders.
_HTML_ENCODER_NAMES = (
    r'html\.escape|markupsafe\.escape|bleach\.clean|nh3\.clean|'
    r'htmlspecialchars|htmlentities|StringEscapeUtils\.escapeHtml[34]?|'
    r'HtmlUtils\.htmlEscape|Encode\.forHtml(?:Content)?|'
    r'ESAPI\.encoder\(\)\.encodeForHTML|HttpUtility\.HtmlEncode|'
    r'WebUtility\.HtmlEncode|HtmlEncoder\.(?:Default\.)?Encode|Html\.Encode|'
    r'DOMPurify\.sanitize|he\.encode|_\.escape'
)
_HTML_ENCODER_CALL = re.compile(r'(?<![\w.])(?:' + _HTML_ENCODER_NAMES + r')\s*\(')
_HTML_ENCODER_REBIND = re.compile(r'^\s*(' + _HTML_ENCODER_NAMES + r')\s*=(?!=)')


def _rebound_html_encoders(lines):
    """Track explicit local rebinding; dynamic imports/aliases remain unsupported."""
    return {match.group(1) for line in lines
            if (match := _HTML_ENCODER_REBIND.match(line))}


def _ambiguous_html_context(text):
    return bool(re.search(r'<\s*(?:script|style)\b|\b[\w:-]+\s*=\s*[\'"]', text, re.I))


def _html_residual(text, rebound=frozenset()):
    """Remove just recognized HTML encoder calls, retaining every other term."""
    # Embedded script/style, URL and attribute contexts require other encoders.
    # This deliberately declines mitigation for ambiguous string constructions.
    if _ambiguous_html_context(text):
        return text
    out, pos = [], 0
    for match in _HTML_ENCODER_CALL.finditer(text):
        if match.start() < pos:
            continue
        if match.group()[:-1].strip() in rebound:
            continue
        end = _closing_paren(text, match.end() - 1)
        if end is None:
            return text
        out.append(text[pos:match.start()])
        out.append('0')
        pos = end + 1
    out.append(text[pos:])
    return ''.join(out)


def _sink_expression(line, match, sid):
    """Isolate common single-line sink arguments; unknown shapes stay broad."""
    if sid in ('innerHTML', 'InnerHtml', 'navigation', 'src-href', 'Literal.Text') and '=' in match.group():
        expr = line[match.end():]
        depth, quote, escaped = 0, None, False
        for i, char in enumerate(expr):
            if quote:
                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == quote:
                    quote = None
            elif char in ('"', "'", '`'):
                quote = char
            elif char in '([{':
                depth += 1
            elif char in ')]}':
                depth -= 1
            elif char == ';' and depth == 0:
                return expr[:i]
        return expr
    if match.group().endswith('('):
        start = match.end()
        end = _closing_paren(line, start - 1)
        if end is not None:
            expr = line[start:end]
            if sid == 'render-template-str' and not re.search(r'\|\s*safe\b', expr):
                # Only the template source (first argument) is an SSTI sink.
                # Keyword values rendered by autoescape are not template source.
                depth, quote, escaped = 0, None, False
                for i, char in enumerate(expr):
                    if quote:
                        if escaped:
                            escaped = False
                        elif char == '\\':
                            escaped = True
                        elif char == quote:
                            quote = None
                    elif char in ('"', "'", '`'):
                        quote = char
                    elif char in '([{':
                        depth += 1
                    elif char in ')]}':
                        depth -= 1
                    elif char == ',' and depth == 0:
                        expr = expr[:i]
                        break
                if re.fullmatch(r'\s*([\'"])(?:\\.|(?!\1).)*\1\s*', expr):
                    return '0'
            return expr
    return line


_HTML_BODY_SINKS = {'innerHTML', 'insertAdjacentHTML', 'document.write',
                    'jquery-html', 'fastapi-html', 'flask-response-html',
                    'markupsafe-markup', 'django-mark-safe', 'echo', 'print',
                    'short-echo', 'servlet-writer', 'response-write', 'Html.Raw',
                    'Response.Write', 'HtmlString', 'MarkupString', 'InnerHtml'}


def _scope_lines(lines, index, lang):
    """Isolate ordinary Python function locals. Complex scopes remain limited.

    Nested closures/classes are deliberately not inferred across boundaries.
    The returned prefix also avoids a later source assignment tainting an
    earlier sink. Brace languages retain file-local conservative scope.
    """
    if lang != 'py':
        return lines[:index + 1]
    scopes = []
    active = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        indent = len(line) - len(line.lstrip())
        while active and indent <= active[-1][1]:
            start, _ = active.pop()
            scopes.append((start, i))
        if re.match(r'\s*(?:async\s+)?def\s+\w+\s*\(', line):
            active.append((i, indent))
    scopes.extend((start, len(lines)) for start, _ in active)
    containing = [(start, end) for start, end in scopes if start <= index < end]
    if containing:
        start, end = max(containing)
        # An explicit module-level encoder override is visible inside a later
        # function. Carry only those bindings, not unrelated module taint or
        # assignments inside a sibling function.
        module_rebindings = [line for i, line in enumerate(lines[:start])
                             if line == line.lstrip()
                             and _HTML_ENCODER_REBIND.match(line)
                             and not any(child <= i < stop for child, stop in scopes)]
        return module_rebindings + [line for i, line in enumerate(lines[start:index + 1], start)
                                    if not any(start < child <= i < stop for child, stop in scopes)]
    return [line for i, line in enumerate(lines[:index + 1])
            if not any(start <= i < end for start, end in scopes)]


class ScopedTaintMap(set):
    """Set-compatible inventory; scan_file uses only explicitly bound file names."""
    def __init__(self, by_file):
        super().__init__(name for names in by_file.values() for name in names)
        self.by_file = by_file

    def for_path(self, path):
        return self.by_file.get(os.path.normcase(os.path.abspath(path)), set())


def build_cross_file_taint_map(paths):
    """Resolve only simple, explicit sibling imports/includes. No global names.

    Unsupported dynamic/module/class resolution stays a candidate. This is not
    an interprocedural proof; see STATIC-LIMITS.md.
    """
    paths = [os.path.normcase(os.path.abspath(p)) for p in paths]
    providers = {p: _raw_return_names([p]) for p in paths}
    result = {}
    for path in paths:
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                code = fh.read()
        except OSError:
            continue
        lang = _lang_for(path)[0]
        bound = set(providers[path])
        directory = os.path.dirname(path)
        imports = []
        if lang == "py":
            for module, names in re.findall(r'^from\s+([\w.]+)\s+import\s+([^\n#]+)', code, re.M):
                # Only a single sibling module is deliberately supported.
                if '.' not in module:
                    imports.append((module + '.py', names))
        elif lang == "js":
            for names, module in re.findall(r'(?:const|let|var)\s*\{([^}]+)\}\s*=\s*require\([\'"](\./[^\'"]+)[\'"]\)', code):
                imports.append((module if os.path.splitext(module)[1] else module + '.js', names))
            for names, module in re.findall(r'import\s*\{([^}]+)\}\s*from\s*[\'"](\./[^\'"]+)[\'"]', code):
                imports.append((module if os.path.splitext(module)[1] else module + '.js', names))
        elif lang == "php":
            for module in re.findall(r'\b(?:require|include)(?:_once)?\s*[\'"]([^\'"]+)[\'"]', code):
                imports.append((module, None))
        for module, names in imports:
            provider = os.path.normcase(os.path.abspath(os.path.join(directory, module)))
            available = providers.get(provider, set())
            if names is None:
                bound.update(available)
            else:
                for name in names.split(','):
                    parts = re.split(r'\s+as\s+|\s*:\s*', name.strip())
                    if parts[0] in available and all(re.fullmatch(r'\w+', p) for p in parts):
                        bound.add(parts[-1])
        # A local declaration can shadow an import. Do not claim that binding.
        def_re = _FUNC_DEF_RE.get(lang)
        if def_re:
            declarations = [m.group(1) for line in code.splitlines() if (m := def_re.match(line))]
            for name in declarations:
                if name not in providers[path] or declarations.count(name) > 1:
                    bound.discard(name)
        result[path] = bound
    return ScopedTaintMap(result)


def compute_taint(lines, sources, msg_active, assign_re=ASSIGN,
                  cross_file_funcs=None, html_context=False):
    """Bounded regex provenance; HTML mitigation is a separate sink-specific view.

    Encoder spelling never erases raw provenance needed for JS/template sinks.
    html_context removes only recognized HTML call spans, never adjacent values.
    """
    tainted = set()
    raw_tainted = (compute_taint(lines, sources, msg_active, assign_re, cross_file_funcs)
                   if html_context else set())
    xfuncs = cross_file_funcs or set()
    # Precompile a single alternation regex for the cross-file call check -
    # much cheaper than N separate re.search() calls per RHS in the fix-point.
    xfunc_call_re = None
    if xfuncs:
        xfunc_call_re = re.compile(
            r'(?<!\w)(?:' + "|".join(re.escape(n) for n in xfuncs) +
            r')\s*\(')
    for _ in range(6):
        changed = False
        rebound = set()
        for line in lines:
            if html_context and (binding := _HTML_ENCODER_REBIND.match(line)):
                rebound.add(binding.group(1))
            m = assign_re.match(line)
            if not m:
                continue
            lhs, rhs = m.group(1), m.group(2)
            # Raw provenance always survives encoders. Only the separate HTML
            # view removes recognized call spans; concatenated raw data remains.
            context_tainted = raw_tainted if html_context and _ambiguous_html_context(rhs) else tainted
            if html_context:
                rhs = _html_residual(rhs, rebound)
            if (source_hits(rhs, sources, msg_active)
                or any(re.search(r'(?<!\w)' + re.escape(v) + r'\b', rhs)
                       for v in context_tainted)
                or (xfunc_call_re is not None and xfunc_call_re.search(rhs))):
                if lhs not in tainted:
                    tainted.add(lhs)
                    changed = True
        if not changed:
            break
    return tainted


def _lang_for(path):
    """Return (lang, sinks, sources, assign_re, wants_taint). lang is one of
    'js', 'cs', 'php', 'java', 'py'; wants_taint tells scan_file whether to run
    compute_taint (JS+PHP+Java+Python yes, C# no - stays sink-only)."""
    ext = os.path.splitext(path)[1].lower()
    if ext in JS_EXT:
        return "js", JS_SINKS, JS_SOURCES, ASSIGN, True
    if ext in PHP_EXT:
        return "php", PHP_SINKS, PHP_SOURCES, PHP_ASSIGN, True
    if ext in JAVA_EXT:
        return "java", JAVA_SINKS, JAVA_SOURCES, JAVA_ASSIGN, True
    if ext in PY_EXT:
        return "py", PY_SINKS, PY_SOURCES, PYTHON_ASSIGN, True
    if ext in TEMPLATE_EXT:
        return "template", TEMPLATE_SINKS + JS_SINKS, JS_SOURCES, ASSIGN, True
    return "cs", CS_SINKS, CS_SOURCES, ASSIGN, False


def _python_helper_expansion(tree, source):
    """One-hop local return summaries; uncertainty keeps the original call.

    This deliberately rejects aliases, conflicting bindings and arbitrary calls.
    It is a bounded expression substitution, not a call graph or safety proof.
    """
    definitions = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            definitions.setdefault(node.name, []).append(node)
    parent = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    summaries = {}
    rebound = _rebound_html_encoders(source.splitlines())
    uncertain_bindings = set()
    wildcard_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.name:
            uncertain_bindings.add(node.name)
        elif isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name:
            uncertain_bindings.add(node.name)
        elif isinstance(node, ast.MatchMapping) and node.rest:
            uncertain_bindings.add(node.rest)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                wildcard_import |= alias.name == '*'
                # The documented encoder spelling is permitted for its own
                # module only; an unrelated import alias is not that module.
                if alias.asname and alias.asname != alias.name:
                    uncertain_bindings.add(alias.asname)
                elif isinstance(node, ast.ImportFrom):
                    uncertain_bindings.add(alias.asname or alias.name)
    # A receiver replacement also invalidates a wrapper's encoder spelling.
    roots_written = {node.id for node in ast.walk(tree)
                     if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del))}
    roots_written.update(node.arg for node in ast.walk(tree) if isinstance(node, ast.arg))
    roots_written.update(uncertain_bindings)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Attribute, ast.Subscript)) and isinstance(node.ctx, (ast.Store, ast.Del)):
            receiver = node
            while isinstance(receiver, (ast.Attribute, ast.Subscript)):
                receiver = receiver.value
            if isinstance(receiver, ast.Name):
                roots_written.add(receiver.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            roots_written.add(node.name)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            # Explicit mutation through a namespace dictionary defeats the
            # same spelling hint as a direct namespace/property assignment.
            if any(isinstance(part, ast.Attribute) and part.attr == '__dict__'
                   for part in ast.walk(node.func)):
                roots_written.update(part.id for part in ast.walk(node.func)
                                     if isinstance(part, ast.Name))
    encoder_names = re.compile(_HTML_ENCODER_NAMES)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = ast.unparse(node.func)
            if encoder_names.fullmatch(name) and name.split('.')[0] in roots_written:
                rebound.add(name)
        elif isinstance(node, ast.Attribute) and isinstance(node.ctx, (ast.Store, ast.Del)):
            rebound.add(ast.unparse(node))
    # Dynamic attribute mutation is not resolved. It disables new wrapper
    # mitigation without changing the legacy direct-encoder contract.
    dynamic_mutation = any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                           and node.func.id in ('setattr', 'delattr', 'exec', 'eval')
                           for node in ast.walk(tree))
    if wildcard_import or dynamic_mutation:
        rebound.update(ast.unparse(node.func) for node in ast.walk(tree)
                       if isinstance(node, ast.Call) and encoder_names.fullmatch(ast.unparse(node.func)))
    for function in tree.body:
        if not isinstance(function, ast.FunctionDef):
            continue
        args = function.args
        parameters = args.posonlyargs + args.args
        if (wildcard_import or dynamic_mutation or function.name in uncertain_bindings
                or len(definitions[function.name]) != 1 or function.decorator_list
                or args.defaults or args.kw_defaults or args.vararg or args.kwarg
                or args.kwonlyargs or len(parameters) > 16
                or len(function.body) != 1 or not isinstance(function.body[0], ast.Return)
                or function.body[0].value is None):
            continue
        conflict = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == function.name:
                owner = parent.get(node)
                if not (isinstance(node.ctx, ast.Load) and isinstance(owner, ast.Call)
                        and owner.func is node):
                    conflict = True
            elif isinstance(node, ast.arg) and node.arg == function.name:
                conflict = True
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if any((alias.asname or alias.name.split('.')[0]) == function.name
                       for alias in node.names):
                    conflict = True
        value = function.body[0].value
        nodes = list(ast.walk(value))
        if conflict or len(nodes) > 64:
            continue
        allowed_names = {arg.arg for arg in parameters}
        valid = True
        for node in nodes:
            text = ast.unparse(node)
            if isinstance(node, ast.Call):
                callee = ast.unparse(node.func)
                if (node.keywords or any(isinstance(arg, ast.Starred) for arg in node.args)
                        or not (encoder_names.fullmatch(callee)
                                or source_hits(callee + '(', PY_SOURCES, False))):
                    valid = False
                    break
                allowed_names.update(item.id for item in ast.walk(node.func)
                                     if isinstance(item, ast.Name))
            elif isinstance(node, (ast.Attribute, ast.Subscript)) and source_hits(text, PY_SOURCES, False):
                allowed_names.update(item.id for item in ast.walk(node)
                                     if isinstance(item, ast.Name))
            elif isinstance(node, (ast.Lambda, ast.NamedExpr, ast.Await, ast.Yield,
                                   ast.YieldFrom, ast.ListComp, ast.SetComp,
                                   ast.DictComp, ast.GeneratorExp)):
                valid = False
                break
        if valid and all(node.id in allowed_names for node in nodes if isinstance(node, ast.Name)):
            summaries[function.name] = (function.end_lineno, [arg.arg for arg in parameters], value)

    class Substitute(ast.NodeTransformer):
        def __init__(self, bindings):
            self.bindings = bindings

        def visit_Name(self, node):
            return self.bindings.get(node.id, node)

    def expand(expression, text=None, line=None):
        # Reparse before substitution so the original source tree is untouched.
        text = text if text is not None else (ast.get_source_segment(source, expression) or ast.unparse(expression))
        if len(text) > 32768:
            return text, set()
        original_line = line if line is not None else getattr(expression, 'lineno', 0)
        try:
            copied = ast.parse(text, mode='eval')
        except (SyntaxError, ValueError, RecursionError):
            return text, set()
        if sum(1 for _ in ast.walk(copied)) > 2048:
            return text, set()

        class Expand(ast.NodeTransformer):
            remaining = 64
            expanded = False
            growth_budget = 2048 - sum(1 for _ in ast.walk(copied))

            def visit_Call(self, node):
                self.generic_visit(node)
                summary = summaries.get(node.func.id) if isinstance(node.func, ast.Name) else None
                if (summary is None or self.remaining <= 0 or original_line <= summary[0]
                        or node.keywords or len(node.args) != len(summary[1])
                        or any(isinstance(arg, ast.Starred) for arg in node.args)):
                    return node
                self.remaining -= 1
                value = ast.parse(ast.unparse(summary[2]), mode='eval').body
                value = Substitute(dict(zip(summary[1], node.args))).visit(value)
                old_size = sum(1 for _ in ast.walk(node))
                new_size = 0
                for _ in ast.walk(value):
                    new_size += 1
                    if new_size > old_size + self.growth_budget:
                        return node
                self.growth_budget -= max(0, new_size - old_size)
                self.expanded = True
                return value

        transformer = Expand()
        try:
            transformed = ast.fix_missing_locations(transformer.visit(copied))
            rendered = ast.unparse(transformed.body)
        except (RecursionError, ValueError):
            return text, set()
        if len(rendered) > 32768:
            return text, set()
        return rendered, (rebound if transformer.expanded else set())

    return expand


def _python_ast_analysis(source):
    """Return bounded Python taint snapshots and syntax-level sources.

    This is a single-language pilot, not a sound data-flow analysis. It handles
    ordinary assignments (including matching tuple/list unpacking) in lexical
    statement order. A separate bounded substitution handles one-hop local
    single-return helpers. Conditional bodies are merged monotonically; aliases,
    general interprocedural graphs, class/closure scopes and dynamic imports are
    not resolved. Invalid Python returns None so the legacy heuristic remains
    the fallback.
    """
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, TypeError):
        return None

    expand_helpers = _python_helper_expansion(tree, source)

    source_lines = {}

    def source_names_in(node, text):
        found = set()
        for child in ast.walk(node):
            # Inspect the syntactic receiver/callee only. Looking at an outer
            # call's full source text would mistake a quoted example for input.
            if isinstance(child, ast.Call):
                segment = ast.get_source_segment(text, child.func)
                if segment:
                    found.update(source_hits(segment + "(", PY_SOURCES, False))
            elif isinstance(child, (ast.Subscript, ast.Attribute)):
                segment = ast.get_source_segment(text, child)
                if segment:
                    found.update(source_hits(segment, PY_SOURCES, False))
        return found

    def source_names(node):
        return source_names_in(node, source)

    for node in ast.walk(tree):
        found = set()
        if isinstance(node, ast.Call):
            segment = ast.get_source_segment(source, node.func)
            if segment:
                found.update(source_hits(segment + "(", PY_SOURCES, False))
        elif isinstance(node, (ast.Subscript, ast.Attribute)):
            segment = ast.get_source_segment(source, node)
            if segment:
                found.update(source_hits(segment, PY_SOURCES, False))
        if found:
            source_lines.setdefault(node.lineno, set()).update(found)

    raw_at_line = {}
    html_at_line = {}
    rebound_at_line = {}
    tainted = set()
    html_tainted = set()
    source_lines_text = source.splitlines()

    def expr_tainted(node, names):
        text, _ = expand_helpers(node)
        try:
            normalized = ast.parse(text, mode='eval')
        except (SyntaxError, ValueError, RecursionError):
            # Starred unpack members and unparenthesized walrus segments are
            # valid within their original tree but not standalone eval input.
            return bool(source_names(node)) or any(
                isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)
                and item.id in names for item in ast.walk(node))
        if source_names_in(normalized, text):
            return True
        return any(isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)
                   and item.id in names for item in ast.walk(normalized))

    def bind(target, value, raw_value, html_value, rebound_names):
        if isinstance(target, (ast.Tuple, ast.List)):
            if isinstance(value, (ast.Tuple, ast.List)) and len(target.elts) == len(value.elts):
                for lhs, rhs in zip(target.elts, value.elts):
                    bind(lhs, rhs, expr_tainted(rhs, tainted),
                         expr_tainted_text(rhs, html_tainted, tainted, rebound_names), rebound_names)
                return
            for lhs in target.elts:
                bind(lhs, value, raw_value, html_value, rebound_names)
            return
        if isinstance(target, ast.Name):
            # Taint is monotonic, matching the existing conservative behavior.
            if raw_value:
                tainted.add(target.id)
            if html_value:
                html_tainted.add(target.id)

    def expr_tainted_text(node, names, raw_names, rebound_names):
        segment, helper_rebound = expand_helpers(node)
        if _ambiguous_html_context(segment):
            return expr_tainted(node, raw_names)
        residual = _html_residual(segment, rebound_names | helper_rebound)
        try:
            residual_ast = ast.parse(residual, mode="eval")
        except (SyntaxError, ValueError, RecursionError):
            return expr_tainted(node, names)
        if source_names_in(residual_ast, residual):
            return True
        return any(isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)
                   and item.id in names for item in ast.walk(residual_ast))

    def visit_statements(statements, inherited_rebound=None):
        local_rebound = set(inherited_rebound or ())
        for statement in statements:
            start = getattr(statement, "lineno", 1)
            end = getattr(statement, "end_lineno", start)
            for line in range(start, end + 1):
                if 1 <= line <= len(source_lines_text):
                    binding = _HTML_ENCODER_REBIND.match(source_lines_text[line - 1])
                    if binding:
                        local_rebound.add(binding.group(1))
            for line in range(start, end + 1):
                raw_at_line[line] = set(tainted)
                html_at_line[line] = set(html_tainted)
                rebound_at_line[line] = set(local_rebound)

            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Function bodies are independent scopes. Nested definitions
                # are intentionally not traversed by this pilot.
                saved_raw, saved_html = tainted.copy(), html_tainted.copy()
                tainted.clear()
                html_tainted.clear()
                visit_statements(statement.body, local_rebound)
                tainted.clear(); tainted.update(saved_raw)
                html_tainted.clear(); html_tainted.update(saved_html)
                continue
            if isinstance(statement, (ast.ClassDef,)):
                continue

            value = None
            targets = []
            if isinstance(statement, ast.Assign):
                value, targets = statement.value, statement.targets
            elif isinstance(statement, ast.AnnAssign) and statement.value is not None:
                value, targets = statement.value, [statement.target]
            elif isinstance(statement, ast.NamedExpr):
                value, targets = statement.value, [statement.target]
            elif isinstance(statement, ast.AugAssign):
                value, targets = statement.value, [statement.target]
                if isinstance(statement.target, ast.Name) and statement.target.id in tainted:
                    tainted.add(statement.target.id)
                    html_tainted.add(statement.target.id)

            if value is not None:
                raw_value = expr_tainted(value, tainted)
                html_value = expr_tainted_text(value, html_tainted, tainted, local_rebound)
                for target in targets:
                    bind(target, value, raw_value, html_value, local_rebound)

            # Merge control-flow blocks into a conservative monotonic view.
            # This deliberately makes no claim about branch feasibility.
            child_blocks = []
            if isinstance(statement, (ast.If, ast.For, ast.AsyncFor, ast.While)):
                child_blocks.extend((statement.body, statement.orelse))
            elif isinstance(statement, (ast.With, ast.AsyncWith)):
                child_blocks.append(statement.body)
            elif isinstance(statement, (ast.Try,)):
                child_blocks.extend([statement.body, statement.orelse, statement.finalbody])
                child_blocks.extend(handler.body for handler in statement.handlers)
            for block in child_blocks:
                visit_statements(block, local_rebound)

    visit_statements(tree.body)

    def evaluate_sink(text, line, html_body, scoped_rebound):
        try:
            node = ast.parse(text.strip(), mode='eval').body
            expanded, helper_rebound = expand_helpers(node, text.strip(), line)
            if html_body and _ambiguous_html_context(expanded):
                html_body = False
            if html_body:
                expanded = _html_residual(expanded, scoped_rebound | helper_rebound)
            normalized = ast.parse(expanded, mode='eval')
        except (SyntaxError, ValueError, RecursionError):
            return None
        names = (html_at_line if html_body else raw_at_line).get(line, set())
        return (sorted(source_names_in(normalized, expanded)),
                sorted({item.id for item in ast.walk(normalized)
                        if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)
                        and item.id in names}))

    return {"raw": raw_at_line, "html": html_at_line,
            "sources": source_lines, "rebound": rebound_at_line,
            "evaluate_sink": evaluate_sink}


def _jsx_lexical_view(text):
    """Mask opaque JS tokens without changing offsets or physical lines.

    Unlike the receiver-proof view, closing JSX tags are not slash expressions.
    This is a bounded lexical convenience, not a JSX/TypeScript parser.
    """
    out = list(text)
    i = 0
    jsx_depth, in_tag, closing_tag, tag_braces = 0, False, False, 0
    text_expression = 0
    while i < len(text):
        # JSX child text is not JavaScript: apostrophes and URL slashes there
        # cannot start quoted literals/comments and hide subsequent anchors.
        if jsx_depth and not in_tag and not text_expression:
            if text[i] == '{':
                text_expression = 1
                i += 1
                continue
            if text[i] != '<':
                if text[i] != '\n':
                    out[i] = ' '
                i += 1
                continue
        tag = re.match(r'<(/?)(?:[A-Za-z][\w:.-]*(?=\s|/?>)|(?=>))', text[i:]) if text[i] == '<' else None
        if tag and not in_tag:
            in_tag, closing_tag, tag_braces = True, bool(tag.group(1)), 0
            i += len(tag.group())
            continue
        if in_tag:
            if text[i] == '{':
                tag_braces += 1
            elif text[i] == '}':
                tag_braces -= 1
            elif text[i] == '>' and not tag_braces:
                if closing_tag:
                    jsx_depth = max(0, jsx_depth - 1)
                elif text[i - 1:i] != '/':
                    jsx_depth += 1
                in_tag = False
        elif text_expression:
            if text[i] == '{':
                text_expression += 1
            elif text[i] == '}':
                text_expression -= 1
        end = None
        if text.startswith('//', i):
            end = text.find('\n', i)
            end = len(text) if end < 0 else end
        elif text.startswith('/*', i):
            stop = text.find('*/', i + 2)
            end = len(text) if stop < 0 else stop + 2
        elif text[i] in ('"', "'", '`'):
            quote, end = text[i], i + 1
            if quote == '`':
                end = _js_template_end(text, i) or len(text)
            else:
                while end < len(text) and text[end] != quote:
                    end += 2 if text[end] == '\\' else 1
                end = min(end + 1, len(text))
        elif text[i] == '/' and re.search(r'(?:[=(:,!\[;]|\breturn)\s*$', text[max(0, i - 128):i]):
            # Opaque regex literal, including escaped slashes and character sets.
            end, bracket = i + 1, False
            while end < len(text) and text[end] != '\n':
                if text[end] == '\\':
                    end += 2
                    continue
                if text[end] == '[':
                    bracket = True
                elif text[end] == ']':
                    bracket = False
                elif text[end] == '/' and not bracket:
                    end += 1
                    break
                end += 1
        if end is None:
            i += 1
            continue
        out[i:end] = ''.join('\n' if c == '\n' else ' ' for c in text[i:end])
        i = end
    return ''.join(out)


def _jsx_taint_prefix(text):
    """Keep statements only from module/current open lexical blocks.

    Closed sibling bodies never contribute local provenance. Function/arrow
    parameter identifiers conservatively shadow outer bindings. This bounded
    lexical subset does not resolve closures, destructuring or control flow.
    Beyond 32 KiB, retain the candidate without asserting identifier provenance;
    cutting into an unknown enclosing body could invent a module binding.
    """
    if len(text) > 32768:
        return []
    view = _jsx_lexical_view(text)
    stack, statements, shadows = [], [], {}
    first = 0
    for match in re.finditer(r'[{};\n]', view):
        token, pos = match.group(), match.start()
        statement = view[first:pos].strip()
        if token == '{':
            header = view[max(0, first):pos]
            params = re.search(r'(?:\bfunction\s*\w*\s*\(([^()]*)\)|\(([^()]*)\)\s*=>|\b([A-Za-z_$][\w$]*)\s*=>)\s*$', header)
            stack.append(pos)
            if params:
                shadows[pos] = set(re.findall(r'[A-Za-z_$][\w$]*', next(g for g in params.groups() if g is not None)))
        elif token == '}':
            if stack:
                closed = stack.pop()
                statements = [(owners, value) for owners, value in statements if closed not in owners]
        elif statement:
            statements.append((tuple(stack), statement))
        first = match.end()
    active = set(stack)
    result = []
    for owners, statement in statements:
        binding = ASSIGN.match(statement)
        if binding and any(binding.group(1) in names and frame in active and frame not in owners
                           for frame, names in shadows.items()):
            continue
        if set(owners) <= active:
            result.append(statement)
    return result


def _jsx_href_candidates(text):
    """Yield (href offset, expression) for flat intrinsic anchor attributes.

    Opening tags are capped at 32 KiB. Spreads, nested braces, namespaced and
    custom components are outside this subset. Unknown calls remain candidates;
    neither a validator name nor HTML escaping establishes URL safety.
    """
    view = _jsx_lexical_view(text)
    for anchor in re.finditer(r'<a(?=\s|/?>)', view):
        start = anchor.end()
        depth, stop, unsupported = 0, None, False
        for pos in range(start, min(len(view), start + 32768)):
            char = view[pos]
            if char == '{':
                depth += 1
                unsupported |= depth > 1
            elif char == '}':
                depth -= 1
                unsupported |= depth < 0
            elif char == '>' and depth == 0:
                stop = pos
                break
            elif char == '<' and depth == 0:
                break
        if stop is None or unsupported or re.search(r'\{\s*\.\.\.', view[start:stop]):
            continue
        # Consume attributes in order: href-like text inside another attribute's
        # expression must not be reinterpreted as an anchor attribute.
        pos = start
        while pos < stop:
            attr = re.match(r'\s*([A-Za-z_$][\w$:.-]*)\s*(=)?', view[pos:stop])
            if attr is None:
                break
            name, assigned = attr.group(1), attr.group(2)
            offset = pos + attr.start(1)
            pos += attr.end()
            if not assigned:
                continue
            while pos < stop and text[pos].isspace():
                pos += 1
            if pos < stop and view[pos] == '{':
                end = view.find('}', pos + 1, stop)
                if end < 0:
                    break
                expr = text[pos + 1:end].strip()
                expression_view = _jsx_lexical_view(expr).strip()
                fixed_scalar = re.fullmatch(r'(?:null|undefined|true|false|\d+(?:\.\d+)?)', expression_view)
                if name == 'href' and expression_view and not fixed_scalar:
                    yield offset, expr
                pos = end + 1
            else:
                # Quoted JSX attribute values are opaque in the lexical view.
                # Advance over their original extent rather than swallowing the
                # next attribute after the masked whitespace.
                original = text[pos:stop]
                literal = re.match(r'''(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')''', original)
                if literal is None:
                    break
                pos += literal.end()


def _leaflet_proof_view(text, view):
    """Expose executable template references only to invalidate type proofs.

    Literal template text, quotes and comments stay masked. Interpolations are
    capped at 32 KiB and nesting at 32; uncertainty prevents type proof. This
    lexical walk neither evaluates expressions nor establishes new bindings.
    """
    proof = list(view)

    def code(pos, interpolation=False, nesting=0):
        if nesting >= 32:
            return None
        first, braces = pos, 1
        while pos < len(text):
            if interpolation and pos - first > 32768:
                return None
            if text.startswith('//', pos):
                end = text.find('\n', pos)
                pos = len(text) if end < 0 else end
                continue
            if text.startswith('/*', pos):
                end = text.find('*/', pos + 2)
                if end < 0:
                    return None
                pos = end + 2
                continue
            char = text[pos]
            if char in "\"'":
                quote, end = char, pos + 1
                while end < len(text) and text[end] != quote:
                    end += 2 if text[end] == '\\' else 1
                if end >= len(text):
                    return None
                if interpolation:
                    proof[pos] = '0'
                pos = end + 1
                continue
            if char == '`':
                pos = template(pos + 1, nesting + 1)
                if pos is None:
                    return None
                continue
            if char == '/' and re.search(r'(?:[=(:,!\[;]|\breturn)\s*$', text[max(0, pos - 128):pos]):
                # Match the existing lexical view's opaque regex boundary.
                end, bracket = pos + 1, False
                while end < len(text) and text[end] != '\n':
                    if text[end] == '\\':
                        end += 2
                        continue
                    if text[end] == '[':
                        bracket = True
                    elif text[end] == ']':
                        bracket = False
                    elif text[end] == '/' and not bracket:
                        end += 1
                        break
                    end += 1
                pos = end
                continue
            if interpolation:
                if char == '{':
                    braces += 1
                elif char == '}':
                    braces -= 1
                    if braces == 0:
                        return pos + 1
                proof[pos] = char
            pos += 1
        return None if interpolation else pos

    def template(pos, nesting):
        if nesting >= 32:
            return None
        while pos < len(text):
            if text[pos] == '\\':
                pos += 2
            elif text[pos] == '`':
                return pos + 1
            elif text.startswith('${', pos):
                pos = code(pos + 2, True, nesting + 1)
                if pos is None:
                    return None
            else:
                pos += 1
        return None

    return ''.join(proof) if code(0) is not None else None


def _leaflet_candidates(text):
    """Bounded Leaflet 1.9.4 ES-import/factory proof, not general JS typing.

    Only default/namespace literal imports, marker.bindPopup, popup.setContent
    and direct divIcon object literals participate. No CommonJS/global/named
    imports, constructors, receiver aliases, arbitrary chains or computed keys.
    Calls and provenance prefixes are bounded to 32 KiB. Ambiguous bindings
    cannot prove library identity or an HTMLElement exclusion. Such exclusions
    describe this API's node append only, never preceding DOM operations.
    """
    view = _jsx_lexical_view(text)
    proof_view = _leaflet_proof_view(text, view)
    if proof_view is None:
        return
    ident = r'[A-Za-z_$][\w$]*'
    # Pair delimiters in the masked view; strings/comments/templates are opaque.
    pairs, stack, scopes = {}, [], []
    for token in re.finditer(r'[(){}\[\]]', view):
        pos, char = token.start(), token.group()
        if char in '({[':
            stack.append((char, pos))
            if char == '{':
                scopes.append(pos)
        elif stack and stack[-1][0] == {')': '(', '}': '{', ']': '['}[char]:
            opening, start = stack.pop()
            pairs[start] = pos
            if opening == '{':
                scopes.pop()
        else:
            # Malformed delimiter structure cannot support a receiver proof.
            return

    def scope_at(pos):
        return tuple(sorted(start for start, end in pairs.items()
                            if view[start] == '{' and start < pos < end))

    def parts(start, stop):
        """Top-level comma spans, preserving original literal content."""
        result, first, pos = [], start, start
        while pos < stop:
            if pos in pairs:
                pos = pairs[pos] + 1
                continue
            if view[pos] == ',':
                result.append((first, pos))
                first = pos + 1
            pos += 1
        result.append((first, stop))
        return result

    def call_end(opening):
        end = pairs.get(opening)
        return end if end is not None and end - opening <= 32768 else None

    def bare_refs(name, code=proof_view):
        # A factory property Maps.popup is not a read of a local named popup.
        # Check the preceding token as well as adjacent characters so spaced
        # members (Maps . popup) and masked comments obey the same rule. Bare
        # reassignments, declarations, parameters and receiver writes remain.
        for ref in re.finditer(r'(?<![\w$])' + re.escape(name) + r'(?![\w$])', code):
            if not re.search(r'\.\s*$', code[:ref.start()]):
                yield ref

    imports = {}
    for match in re.finditer(
            r'\bimport\s+(?:\*\s+as\s+)?(' + ident + r')\s+from\s*'
            r'''(['"])leaflet\2\s*;?''', text):
        name = match.group(1)
        if (view[match.start():match.start() + 6] != 'import'
                or scope_at(match.start())):
            continue
        valid = True
        for ref in re.finditer(r'(?<![\w$])' + re.escape(name) + r'(?![\w$])', proof_view):
            if ref.start() == match.start(1):
                continue
            # Every other namespace use must be an ordinary member call.
            # Bare escapes, parameters, redefinitions and property writes lose
            # proof for the alias throughout the file, deliberately conservative.
            tail = proof_view[ref.end():]
            if (not re.match(r'\s*\.\s*' + ident + r'(?:\s*\.\s*' + ident + r')?\s*\(', tail)
                    or re.search(r'(?:\.|\bnew)\s*$', proof_view[max(0, ref.start() - 32):ref.start()])):
                valid = False
                break
        if valid and name not in imports:
            imports[name] = match.end()

    def const_value(name, before):
        """Unique immutable lexical binding; uncertain shadows defeat proof."""
        escaped = re.escape(name)
        refs = list(bare_refs(name))
        declarations = list(re.finditer(r'\bconst\s+(' + escaped + r')\s*=(?!=)', view))
        if len(declarations) != 1:
            return None
        decl = declarations[0]
        if not decl.end() < before or before - decl.start() > 32768:
            return None
        own = scope_at(decl.start())
        if scope_at(before)[:len(own)] != own:
            return None
        for ref in refs:
            if ref.start() == decl.start(1):
                continue
            if (ref.start() < decl.end()
                    or re.match(r'\s*(?:=(?!=|>)|\+\+|--|[+*/%&|^?-]=)', proof_view[ref.end():])
                    or re.search(r'\b(?:const|let|var|class|function|import)\s*$', proof_view[max(0, ref.start()-32):ref.start()])):
                return None
        # Includes function, arrow, catch and simple method parameter lists.
        for header in re.finditer(r'\(([^()]*)\)\s*(?:=>\s*)?\{|\b(' + ident + r')\s*=>', view):
            if any(bare_refs(name, header.group(1) or header.group(2) or '')):
                return None
        # Reject destructuring/redeclaration and unmodelled bare binding syntax.
        for binding in re.finditer(r'\b(?:const|let|var)\s+[^;\n=]+', view):
            if binding.start() != decl.start() and re.search(r'\b' + escaped + r'\b', binding.group()):
                return None
        end = decl.end()
        pos = end
        while pos < len(view):
            # Preserve a complete multiline literal initializer rather than
            # treating its masked physical newline as an ASI boundary.
            if text[pos] == '`':
                literal_end = _js_template_end(text, pos)
                if literal_end is None:
                    return None
                pos = literal_end
                continue
            if text[pos] in "\"'":
                quote, literal_end = text[pos], pos + 1
                while literal_end < len(text) and text[literal_end] != quote:
                    literal_end += 2 if text[literal_end] == '\\' else 1
                if literal_end >= len(text):
                    return None
                pos = literal_end + 1
                continue
            if pos in pairs:
                pos = pairs[pos] + 1
                continue
            if view[pos] in ';\n':
                break
            pos += 1
        return text[end:pos].strip(), decl.start()

    def node_content(expr, before, depth=0):
        # Only benign literal element factories are recognized. No claim about
        # script/unknown tags, shadowed document, or mutation of its factory.
        expr = expr.strip()
        if depth >= 16:
            return False
        if re.fullmatch(ident, expr):
            binding = const_value(expr, before)
            return bool(binding and node_content(binding[0], binding[1], depth + 1))
        if re.fullmatch(r'''document\s*\.\s*createElement\s*\(\s*(['"])(?:div|span)\1\s*\)''', expr):
            docrefs = list(re.finditer(r'\bdocument\b', proof_view))
            return all(re.match(r'\s*\.\s*(?:createElement\s*\(|(?:URL|referrer|cookie|baseURI)\b)', proof_view[r.end():])
                       and not re.search(r'(?:\.|\bnew)\s*$', proof_view[max(0, r.start()-20):r.start()])
                       for r in docrefs)
        return False

    def evaluated(expr):
        # Reveal only simple template interpolation; text between interpolations
        # cannot invent a source. Complex interpolation remains unknown.
        result, pos = [], 0
        while pos < len(expr):
            if expr.startswith('//', pos):
                end = expr.find('\n', pos)
                pos = len(expr) if end < 0 else end
                result.append(' ')
            elif expr.startswith('/*', pos):
                end = expr.find('*/', pos + 2)
                pos = len(expr) if end < 0 else end + 2
                result.append(' ')
            elif expr[pos] == '`':
                end = _js_template_end(expr, pos)
                if end is None:
                    break
                template = expr[pos:end]
                result.extend(' ' + m.group(1) + ' ' for m in re.finditer(
                    r'(?<!\\)\$\{\s*(' + ident + r'(?:\.' + ident + r')*)\s*\}', template))
                pos = end
            elif expr[pos] in "\"'":
                quote, end = expr[pos], pos + 1
                while end < len(expr) and expr[end] != quote:
                    end += 2 if expr[end] == '\\' else 1
                pos = end + 1
                result.append(' ')
            else:
                result.append(expr[pos])
                pos += 1
        return ''.join(result)

    def fixed_content(expr, before, depth=0):
        if depth >= 16:
            return False
        if re.fullmatch(ident, expr):
            binding = const_value(expr, before)
            return bool(binding and fixed_content(binding[0], binding[1], depth + 1))
        fixed = re.fullmatch(r'''(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`)''', expr, re.S)
        if not fixed:
            return False
        if not expr.startswith('`'):
            return True
        # An escaped dollar is text, not interpolation (including even/odd
        # backslash parity). No template value evaluation is performed here.
        pos = 1
        while pos < len(expr) - 1:
            if expr[pos] == '\\':
                pos += 2
            elif expr.startswith('${', pos):
                return False
            else:
                pos += 1
        return True

    def const_provenance(expr, before):
        """Keep raw source evidence through at most 64 immutable const reads.

        Initializers use the same literal/template masking as direct content.
        Scope, uniqueness, mutation and parameter checks remain in const_value;
        calls never establish safety merely from an encoder/validator name.
        Only referenced content bindings participate, never sibling options.
        """
        remaining = [64]

        def expand(value, position, depth):
            if depth >= 16 or remaining[0] <= 0:
                return ''
            pieces = [value]
            for name in dict.fromkeys(re.findall(r'(?<![\w$.])(' + ident + r')(?![\w$])', value)):
                if remaining[0] <= 0:
                    break
                remaining[0] -= 1
                binding = const_value(name, position)
                if binding:
                    pieces.append(expand(evaluated(binding[0]), binding[1], depth + 1))
            return ' '.join(pieces)

        result = {}
        for name in dict.fromkeys(re.findall(r'(?<![\w$.])(' + ident + r')(?![\w$])', expr)):
            if remaining[0] <= 0:
                break
            remaining[0] -= 1
            binding = const_value(name, before)
            if binding:
                result[name] = expand(evaluated(binding[0]), binding[1], 0)
        return result

    def content(offset, start, end, sink):
        expr = text[start:end].strip()
        if not expr:
            return None
        if fixed_content(expr, offset):
            return None
        if node_content(expr, offset):
            return None
        value = evaluated(expr)
        return offset, sink, value, const_provenance(value, offset)

    def method(opening, factory):
        end = call_end(opening)
        if end is None:
            return None
        method_name = 'bindPopup' if factory == 'marker' else 'setContent'
        match = re.match(r'\s*\.\s*' + method_name + r'\s*\(', view[end + 1:])
        if not match:
            return None
        method_start = end + 1 + match.start() + match.group().index('.') + 1
        while view[method_start].isspace():
            method_start += 1
        arg = end + 1 + match.end() - 1
        stop = call_end(arg)
        if stop is not None:
            first, last = parts(arg + 1, stop)[0]
            return content(method_start, first, last, 'leaflet-popup-html')
        return None

    yielded = set()
    for name, imported_at in imports.items():
        factory_rx = re.compile(r'(?<![\w$.])' + re.escape(name) + r'\s*\.\s*(marker|popup|divIcon)\s*\(')
        for match in factory_rx.finditer(view):
            if (match.start() < imported_at or re.search(r'\bnew\s*$', view[max(0, match.start()-16):match.start()])):
                continue
            opening = match.end() - 1
            end = call_end(opening)
            if end is None:
                continue
            factory = match.group(1)
            if factory == 'divIcon':
                args = parts(opening + 1, end)
                start, stop = args[0]
                while start < stop and view[start].isspace():
                    start += 1
                if (start >= stop or view[start] != '{'
                        or pairs.get(start) != start + len(view[start:stop].rstrip()) - 1):
                    continue
                properties = parts(start + 1, pairs[start])
                # Spreads, duplicate/computed keys and methods are unsupported.
                parsed = []
                for first, last in properties:
                    key = re.match(r'\s*(' + ident + r')\s*:', view[first:last])
                    if not key:
                        if view[first:last].strip():
                            parsed = []
                            break
                        continue
                    parsed.append((key.group(1), first + key.start(1), first + key.end(), last))
                if len([p for p in parsed if p[0] == 'html']) != 1:
                    continue
                _, offset, first, last = next(p for p in parsed if p[0] == 'html')
                row = content(offset, first, last, 'leaflet-divicon-html')
                if row:
                    yield row
                continue
            row = method(opening, factory)
            if row:
                yielded.add(row[0])
                yield row
            # Local receiver: exact const initializer only; no arbitrary chains.
            declaration = re.search(r'\bconst\s+(' + ident + r')\s*=\s*$', view[:match.start()])
            after = view[end + 1:]
            if (not declaration or (after.lstrip()[:1] not in (';', '')
                                    and not re.match(r'[^\S\n]*\n', after))):
                continue
            receiver = declaration.group(1)
            method_name = 'bindPopup' if factory == 'marker' else 'setContent'
            receiver_refs = list(bare_refs(receiver))
            if any(ref.start() != declaration.start(1) and not re.match(
                    r'\s*\.\s*' + method_name + r'\s*\(', proof_view[ref.end():])
                   for ref in receiver_refs):
                continue
            for use in re.finditer(r'(?<![\w$.])' + re.escape(receiver) + r'\s*\.\s*(' + method_name + r')\s*\(', view):
                binding = const_value(receiver, use.start())
                if not binding or binding[1] != declaration.start():
                    continue
                stop = call_end(use.end() - 1)
                if stop is None or use.start(1) in yielded:
                    continue
                first, last = parts(use.end(), stop)[0]
                row = content(use.start(1), first, last, 'leaflet-popup-html')
                if row:
                    yielded.add(row[0])
                    yield row


def scan_file(path, cross_file_funcs=None):
    """Scan a single file for XSS-family sinks. Phase 0.4: optional
    `cross_file_funcs` set is passed through to compute_taint AND used to
    upgrade sink-line confidence when the sink argument is a call to a
    known tainted-returning function from another file in the project."""
    lang, sinks, sources, assign_re, wants_taint = _lang_for(path)
    if isinstance(cross_file_funcs, ScopedTaintMap):
        cross_file_funcs = cross_file_funcs.for_path(path)

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            source_text = fh.read()
            lines = source_text.split("\n")
    except OSError as exc:
        REPORT_EVENTS.append(evidence.ReportEvent("static-read", "error", type(exc).__name__, str(path)))
        return []

    msg_active = lang == "js" and bool(MSG_LISTENER.search("\n".join(lines)))
    python_ast = _python_ast_analysis(source_text) if lang == "py" else None
    # Java/C# statements often span lines (ternaries, long argument lists,
    # generic types); join by `;` before taint so multi-line sanitize()
    # wraps are visible. JS/PHP/Python usually single-line - default OK.
    taint_view = _joined_for_taint(lines) if lang in ("java", "cs") else lines
    dynamic = re.compile(r'[A-Za-z_$@][\w$]*')

    # Phase 0.4: precompiled sink-line xfunc detector (empty regex if map empty).
    xfuncs = cross_file_funcs or set()
    xfunc_call_re = (re.compile(
        r'(?<!\w)(?:' + "|".join(re.escape(n) for n in xfuncs) + r')\s*\(')
        if xfuncs else None)

    findings = []
    inline_messages = (_inline_message_regions(source_text, path)
                       if os.path.splitext(path)[1].lower() in ('.html', '.htm') else [])
    js_view = _js_binding_view(source_text) if lang == 'js' else None
    constructor_shadows = _js_constructor_shadows(js_view) if lang == 'js' else []
    source_offset = 0
    for lineno, line in enumerate(lines, 1):
        line_offset = source_offset
        matches = {sid: [m for m in rx.finditer(line)
                         if not (lang == 'js' and _js_non_sink_binding(
                             js_view, source_offset, line, m, sid,
                             constructor_shadows))]
                   for sid, rx, *_ in sinks}
        source_offset += len(line) + 1
        matched_here = {sid for sid, found in matches.items() if found}
        if not matched_here:
            continue
        scope = _scope_lines(taint_view, lineno - 1, lang)
        tainted = (compute_taint(scope, sources, msg_active, assign_re,
                                 cross_file_funcs=cross_file_funcs) if wants_taint else set())
        html_tainted = (compute_taint(scope, sources, msg_active, assign_re,
                                      cross_file_funcs=cross_file_funcs, html_context=True)
                        if wants_taint else set())
        rebound = _rebound_html_encoders(scope)
        # v3.9 dedup: drop specific sinks when the general one already matched
        suppressed = {specific for specific, general in SINK_SUPPRESSIONS
                      if specific in matched_here and general in matched_here}
        for sid, rx, severity, desc in sinks:
            if sid not in matched_here or sid in suppressed:
                continue
            sink_match = matches[sid][0]
            expr = _sink_expression(line, sink_match, sid)
            html_body = sid in _HTML_BODY_SINKS and not _ambiguous_html_context(expr)
            evaluated = _html_residual(expr, rebound) if html_body else expr
            srcs = source_hits(evaluated, sources, msg_active)
            tvars = sorted(v for v in (html_tainted if html_body else tainted)
                           if re.search(r'(?<!\w)' + re.escape(v) + r'\b', evaluated))
            # Keep the original first-match evidence; add only actual message
            # evidence from supported matches on this same physical line.
            for candidate in matches[sid] if inline_messages else ():
                candidate_expr = _sink_expression(line, candidate, sid)
                position = line_offset + candidate.start()
                expression_end = line_offset + candidate.end() + len(candidate_expr)
                message_context = next((region for region in inline_messages
                                        if region[0] <= position < region[1]
                                        and expression_end <= region[1]
                                        and region[3][position - region[0]:
                                                      position - region[0] + len(candidate.group())]
                                        == candidate.group()), None)
                if message_context is None:
                    continue
                callback_start, _, message_rx, _ = message_context
                candidate_html = sid in _HTML_BODY_SINKS and not _ambiguous_html_context(candidate_expr)
                candidate_evaluated = (_html_residual(candidate_expr, rebound)
                                       if candidate_html else candidate_expr)
                callback_scope = _inline_taint_prefix(
                    source_text[callback_start:position])
                message_tainted = compute_taint(callback_scope, [], message_rx,
                                                 html_context=candidate_html)
                srcs = sorted(set(srcs) | set(source_hits(candidate_evaluated, [], message_rx)))
                message_evaluated = _js_binding_view(candidate_evaluated) or ''
                tvars = sorted(set(tvars) | {name for name in message_tainted
                                           if re.search(r'(?<!\w)' + re.escape(name) + r'\b', message_evaluated)})
            legacy_tvars = tvars
            # Python AST does not resolve the separate sibling-import provider map.
            xfunc_hits = ([fname for fname in xfuncs
                          if re.search(r'(?<!\w)' + re.escape(fname) + r'\s*\(', evaluated)]
                          if xfunc_call_re and xfunc_call_re.search(line) else [])
            if python_ast is not None:
                srcs = sorted(python_ast["sources"].get(lineno, set()))
                ast_names = (python_ast["html"] if html_body else python_ast["raw"]).get(lineno, set())
                tvars = sorted({
                    name for name in ast_names
                    if re.search(r'(?<!\w)' + re.escape(name) + r'\b', evaluated)
                })
                helper_result = python_ast["evaluate_sink"](expr, lineno, html_body, rebound)
                if helper_result is not None:
                    srcs, tvars = helper_result
                if xfuncs:
                    tvars = sorted(set(tvars) | set(legacy_tvars))
            # Phase 0.4: cross-file call directly on the sink line - upgrade
            # confidence too. E.g. `res.send(getUserInput())` where
            # getUserInput lives in util.js and returns req.query raw.
            if srcs or tvars or xfunc_hits:
                confidence = "high"
            elif dynamic.search(line.split("//", 1)[0]):
                confidence = "medium"
            else:
                confidence = "low"
            findings.append({
                "file": path, "line": lineno, "sink": sid, "lang": lang,
                "severity": severity, "confidence": confidence, "description": desc,
                "code": line.strip()[:200], "sources": srcs, "tainted_vars": tvars,
                "xfunc_calls": xfunc_hits,           # Phase 0.4: which cross-file
                                                     # tainted funcs this sink calls
            })
    if os.path.splitext(path)[1].lower() in ('.jsx', '.tsx'):
        for offset, expr in _jsx_href_candidates(source_text):
            lineno = source_text.count('\n', 0, offset) + 1
            evaluated = _jsx_lexical_view(expr)
            srcs = source_hits(evaluated, sources, msg_active)
            prefix = _jsx_taint_prefix(source_text[:offset])
            tainted = compute_taint(prefix, sources, msg_active, assign_re)
            tvars = sorted(v for v in tainted
                           if re.search(r'(?<![\w$])' + re.escape(v) + r'(?![\w$])', evaluated))
            findings.append({
                'file': path, 'line': lineno, 'sink': 'jsx-href', 'lang': lang,
                'severity': 'medium', 'confidence': 'high' if srcs or tvars else 'medium',
                'description': 'JSX anchor href URL-control candidate; review URL validation and allowed schemes. '
                               'Static evidence does not establish an unsafe scheme or execution.',
                'code': lines[lineno - 1].strip()[:200], 'sources': srcs,
                'tainted_vars': tvars, 'xfunc_calls': [],
            })
    if lang == 'js':
        for offset, sink, evaluated, const_sources in _leaflet_candidates(source_text):
            lineno = source_text.count('\n', 0, offset) + 1
            srcs = source_hits(evaluated, sources, msg_active)
            prefix = _jsx_taint_prefix(source_text[:offset])
            tainted = compute_taint(prefix, sources, msg_active, assign_re)
            tvars = sorted({v for v in tainted if re.search(
                r'(?<![\w$])' + re.escape(v) + r'(?![\w$])', evaluated)}
                | {name for name, value in const_sources.items()
                   if source_hits(value, sources, msg_active)})
            findings.append({
                'file': path, 'line': lineno, 'sink': sink, 'lang': lang,
                'severity': 'high', 'confidence': 'high' if srcs or tvars else 'medium',
                'description': 'Leaflet HTML-content review candidate: string content may be parsed as HTML when rendered. '
                               'Unknown content may be an HTMLElement; static evidence does not establish execution.',
                'code': lines[lineno - 1].strip()[:200], 'sources': srcs,
                'tainted_vars': tvars, 'xfunc_calls': [],
            })
    return findings


def iter_files(target):
    if os.path.isfile(target):
        yield target
        return
    for root, _, files in os.walk(target, onerror=lambda exc: REPORT_EVENTS.append(
            evidence.ReportEvent("static-discovery", "error", type(exc).__name__, str(exc.filename or target)))):
        if "node_modules" in root or "vendor" in root or os.sep + ".git" in root:
            REPORT_EVENTS.append(evidence.ReportEvent("static-discovery", "skip", "excluded directory", root))
            continue
        for name in files:
            if name.lower().endswith(JS_EXT + CS_EXT + PHP_EXT + JAVA_EXT + PY_EXT + TEMPLATE_EXT):
                yield os.path.join(root, name)


def render_html(findings, target):
    return evidence.render_report(evidence.report(evidence.static_observations(findings), "static", REPORT_EVENTS))


def _load_cli_config(path, parser):
    """Load the small, versioned static CLI config without echoing its contents."""
    if path is None:
        return {}

    def unique_object(pairs):
        config = {}
        for key, value in pairs:
            if key in config:
                raise ValueError("duplicate config key")
            config[key] = value
        return config

    try:
        with open(path, encoding="utf-8-sig") as stream:
            config = json.load(stream, object_pairs_hook=unique_object)
    except (OSError, UnicodeError, ValueError):
        parser.error("--config must name a readable UTF-8 JSON file")
    if (not isinstance(config, dict)
            or type(config.get("schema_version")) is not int
            or config["schema_version"] != 1
            or not set(config) <= {"schema_version", "min_confidence"}
            or not isinstance(config.get("min_confidence", "low"), str)
            or config.get("min_confidence", "low") not in CONF_RANK):
        parser.error("--config requires schema_version 1 and min_confidence low|medium|high")
    return config


_CREDENTIAL_SOURCE_KEY = (
    r"(?:x[-_]?api[-_]?key|api[-_]?key|authorization|proxy[-_]authorization|"
    r"access[-_]token|refresh[-_]token|id[-_]token|client[-_]secret|"
    r"auth[-_]token|csrf[-_]token|x[-_]csrf[-_]token|x[-_]xsrf[-_]token|"
    r"set[-_]cookie|(?:document\.)?cookie)"
)
_QUOTED_CREDENTIAL_ASSIGNMENT = re.compile(
    rf'''(?ix)(?P<prefix>(?:["'`]?{_CREDENTIAL_SOURCE_KEY}["'`]?)\s*[:=]\s*)'''
    rf'''(?P<quote>["'`])(?:\\.|(?! (?P=quote) ).)*(?P=quote)'''
)
_UNQUOTED_BEARER_ASSIGNMENT = re.compile(
    rf'''(?ix)(?P<prefix>(?:["'`]?{_CREDENTIAL_SOURCE_KEY}["'`]?)\s*[:=]\s*)'''
    r'''Bearer\s+[^\s,;}]+'''
)


def _redact_raw_json_source(findings):
    """Mask obvious credential literals in legacy JSON without mutating scans.

    Only literal assignments with credential-specific field names are changed.
    Arbitrary source snippets remain intact; common sharing reports use the
    separate fingerprint-only adapter.
    """
    exported = []
    for finding in findings:
        row = dict(finding)
        code = row.get("code")
        if isinstance(code, str):
            row["code"] = _redact_source_code(code)
        exported.append(row)
    return exported


def _redact_source_code(code):
    """Redact only credential-labeled source literals in a displayed snippet."""
    code = _QUOTED_CREDENTIAL_ASSIGNMENT.sub(
        lambda match: (match.group("prefix") + match.group("quote")
                       + "[redacted]" + match.group("quote")), code)
    return _UNQUOTED_BEARER_ASSIGNMENT.sub(
        lambda match: match.group("prefix") + "[redacted]", code)


def main():
    ap = argparse.ArgumentParser(description="source-to-sink XSS analyzer (JS + C#/.NET)")
    ap.add_argument("target", help="file or directory to scan")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    ap.add_argument("--json-out", metavar="FILE", help="write common R1 evidence report")
    ap.add_argument("--html", metavar="FILE", help="write a self-contained HTML report to FILE")
    ap.add_argument("--sarif-out", metavar="FILE", help="write a SARIF 2.1.0 report")
    ap.add_argument("--config", metavar="FILE", help="versioned JSON static scan settings")
    ap.add_argument("--min-confidence", choices=["low", "medium", "high"],
                    help="hide findings below this confidence (overrides config; default low)")
    args = ap.parse_args()
    config = _load_cli_config(args.config, ap)
    REPORT_EVENTS.clear()
    output_paths = [path for path in (args.json_out, args.html, args.sarif_out) if path]
    if len({os.path.abspath(path) for path in output_paths}) != len(output_paths):
        ap.error("--json-out, --html, and --sarif-out must have distinct paths")
    if not os.path.exists(args.target):
        REPORT_EVENTS.append(evidence.ReportEvent("static-discovery", "error", "target does not exist", args.target))

    floor = CONF_RANK[args.min_confidence or config.get("min_confidence", "low")]
    # Phase 0.4: two-pass scan. First collect the full file list (one os.walk
    # traversal), then pre-build the cross-file tainted-return function map
    # over Python + JS + PHP files. Java / C# skipped in Phase 0.4. The map is
    # then handed to every per-file scan so `foo(request.args['q'])`-shaped
    # helpers in util.py taint their callers' locals in app.py.
    all_files = list(iter_files(args.target))
    if not all_files and not REPORT_EVENTS:
        REPORT_EVENTS.append(evidence.ReportEvent("static-discovery", "skip", "no supported source files", args.target))
    xfunc_map = build_cross_file_taint_map(all_files) if len(all_files) > 1 else set()
    findings = []
    for f in all_files:
        findings.extend(scan_file(f, cross_file_funcs=xfunc_map))
    filtered = [f for f in findings if CONF_RANK[f["confidence"]] >= floor]
    if len(filtered) != len(findings):
        REPORT_EVENTS.append(evidence.ReportEvent("static-filter", "skip", f"{len(findings)-len(filtered)} candidates below confidence threshold"))
    findings = filtered
    findings.sort(key=lambda f: (-CONF_RANK[f["confidence"]], f["file"], f["line"]))
    document = (evidence.report(evidence.static_observations(findings), "static", REPORT_EVENTS)
                if args.json_out or args.html or args.sarif_out else None)
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(document, fh, indent=2)
    if args.sarif_out:
        import dxa_sarif
        sarif_document = dxa_sarif.to_sarif(document)
        with open(args.sarif_out, "w", encoding="utf-8") as fh:
            json.dump(sarif_document, fh, ensure_ascii=False, indent=2)
    result_code = 2 if any(event.kind == "error" for event in REPORT_EVENTS) else (1 if findings else 0)

    if args.html:
        with open(args.html, "w", encoding="utf-8") as fh:
            fh.write(evidence.render_report(document))
        print(f"HTML report written to {args.html}  ({len(findings)} finding(s))")
        sys.exit(result_code)

    if args.json:
        print(json.dumps(_redact_raw_json_source(findings), indent=2))
        sys.exit(result_code)

    if not findings:
        print("No XSS source/sink patterns found (at the chosen confidence).")
        sys.exit(result_code)

    for f in findings:
        flow = ""
        if f["sources"]:
            flow = "  <- source: " + ", ".join(f["sources"])
        elif f["tainted_vars"]:
            flow = "  <- tainted var: " + ", ".join(f["tainted_vars"])
        print(f"{f['file']}:{f['line']}  [{f['severity'].upper()}/{f['confidence']} "
              f"confidence, {f['lang']}]  sink: {f['sink']}{flow}")
        print(f"    {f['description']}")
        print(f"    | {_redact_source_code(f['code'])}")
        print()

    highs = sum(1 for f in findings if f["confidence"] == "high")
    print(f"{len(findings)} finding(s) - {highs} at HIGH confidence "
          f"(a source or tainted value reaches the sink).")
    sys.exit(1)


if __name__ == "__main__":
    main()
