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
import dxa_evidence as evidence
import html
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
    if msg_active and MSG_DATA.search(text):
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
_HTML_ENCODER_CALL = re.compile(
    r'(?<![\w.])(?:html\.escape|markupsafe\.escape|bleach\.clean|nh3\.clean|'
    r'htmlspecialchars|htmlentities|StringEscapeUtils\.escapeHtml[34]?|'
    r'HtmlUtils\.htmlEscape|Encode\.forHtml(?:Content)?|'
    r'ESAPI\.encoder\(\)\.encodeForHTML|HttpUtility\.HtmlEncode|'
    r'WebUtility\.HtmlEncode|HtmlEncoder\.(?:Default\.)?Encode|Html\.Encode|'
    r'DOMPurify\.sanitize|he\.encode|_\.escape)\s*\(')


def _ambiguous_html_context(text):
    return bool(re.search(r'<\s*(?:script|style)\b|\b[\w:-]+\s*=\s*[\'"]', text, re.I))


def _html_residual(text):
    """Remove just recognized HTML encoder calls, retaining every other term."""
    # Embedded script/style, URL and attribute contexts require other encoders.
    # This deliberately declines mitigation for ambiguous string constructions.
    if _ambiguous_html_context(text):
        return text
    out, pos = [], 0
    for match in _HTML_ENCODER_CALL.finditer(text):
        if match.start() < pos:
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
        return [line for i, line in enumerate(lines[start:index + 1], start)
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
        for line in lines:
            m = assign_re.match(line)
            if not m:
                continue
            lhs, rhs = m.group(1), m.group(2)
            # Raw provenance always survives encoders. Only the separate HTML
            # view removes recognized call spans; concatenated raw data remains.
            context_tainted = raw_tainted if html_context and _ambiguous_html_context(rhs) else tainted
            if html_context:
                rhs = _html_residual(rhs)
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
            lines = fh.read().split("\n")
    except OSError as exc:
        REPORT_EVENTS.append(evidence.ReportEvent("static-read", "error", type(exc).__name__, str(path)))
        return []

    msg_active = lang == "js" and bool(MSG_LISTENER.search("\n".join(lines)))
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
    for lineno, line in enumerate(lines, 1):
        matched_here = {sid for sid, rx, *_ in sinks if rx.search(line)}
        if not matched_here:
            continue
        scope = _scope_lines(taint_view, lineno - 1, lang)
        tainted = (compute_taint(scope, sources, msg_active, assign_re,
                                 cross_file_funcs=cross_file_funcs) if wants_taint else set())
        html_tainted = (compute_taint(scope, sources, msg_active, assign_re,
                                      cross_file_funcs=cross_file_funcs, html_context=True)
                        if wants_taint else set())
        # v3.9 dedup: drop specific sinks when the general one already matched
        suppressed = {specific for specific, general in SINK_SUPPRESSIONS
                      if specific in matched_here and general in matched_here}
        for sid, rx, severity, desc in sinks:
            if sid not in matched_here or sid in suppressed:
                continue
            expr = _sink_expression(line, rx.search(line), sid)
            html_body = sid in _HTML_BODY_SINKS and not _ambiguous_html_context(expr)
            evaluated = _html_residual(expr) if html_body else expr
            srcs = source_hits(evaluated, sources, msg_active)
            tvars = sorted(v for v in (html_tainted if html_body else tainted)
                           if re.search(r'(?<!\w)' + re.escape(v) + r'\b', evaluated))
            # Phase 0.4: cross-file call directly on the sink line - upgrade
            # confidence too. E.g. `res.send(getUserInput())` where
            # getUserInput lives in util.js and returns req.query raw.
            xfunc_hits = ([fname for fname in xfuncs
                          if re.search(r'(?<!\w)' + re.escape(fname) + r'\s*\(', evaluated)]
                          if xfunc_call_re and xfunc_call_re.search(line) else [])
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


def main():
    ap = argparse.ArgumentParser(description="source-to-sink XSS analyzer (JS + C#/.NET)")
    ap.add_argument("target", help="file or directory to scan")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    ap.add_argument("--json-out", metavar="FILE", help="write common R1 evidence report")
    ap.add_argument("--html", metavar="FILE", help="write a self-contained HTML report to FILE")
    ap.add_argument("--min-confidence", choices=["low", "medium", "high"],
                    default="low", help="hide findings below this confidence")
    args = ap.parse_args()
    REPORT_EVENTS.clear()
    if args.json_out and args.html and os.path.abspath(args.json_out) == os.path.abspath(args.html):
        ap.error("--json-out and --html must have distinct paths")
    if not os.path.exists(args.target):
        REPORT_EVENTS.append(evidence.ReportEvent("static-discovery", "error", "target does not exist", args.target))

    floor = CONF_RANK[args.min_confidence]
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
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(evidence.report(evidence.static_observations(findings), "static", REPORT_EVENTS), fh, indent=2)
    result_code = 2 if any(event.kind == "error" for event in REPORT_EVENTS) else (1 if findings else 0)

    if args.html:
        with open(args.html, "w", encoding="utf-8") as fh:
            fh.write(render_html(findings, args.target))
        print(f"HTML report written to {args.html}  ({len(findings)} finding(s))")
        sys.exit(result_code)

    if args.json:
        print(json.dumps(findings, indent=2))
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
        print(f"    | {f['code']}")
        print()

    highs = sum(1 for f in findings if f["confidence"] == "high")
    print(f"{len(findings)} finding(s) - {highs} at HIGH confidence "
          f"(a source or tainted value reaches the sink).")
    sys.exit(1)


if __name__ == "__main__":
    main()
