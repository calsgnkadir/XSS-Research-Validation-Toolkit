# Static analysis limits (R8)

`dxa.py` is a regex source/sink linter, not an AST analyzer or an execution
validator. HIGH is a candidate with a recognized source/provenance signal.
MEDIUM, LOW or no findings do not prove safety. Static output does not establish
HTTP reflection, a resource callback, browser execution or vulnerability impact.
Those observations and the separate role/by-design/self-XSS triage require their
own evidence; see EVIDENCE-CONTRACT.md and BROWSER-PROOF.md.

## Supported approximations

- JavaScript/TypeScript, PHP, Java and Python have bounded assignment taint.
  Raw provenance survives encoder calls, unknown `sanitize`/`clean` helpers,
  and trust markers such as `Markup`, `mark_safe` and `SafeString`.
- Recognized HTML encoder call spans provide only an HTML-body mitigation
  hint. Adjacent raw expressions still flow. Encoding is not assumed to protect
  eval, template source, script/style, URL or attribute contexts. Library names
  can be rebound and sanitizer configuration is not validated; a lowered
  confidence is never sanitizer verification.
- C#/Razor have source and sink pattern detection, including same-line sources,
  but no assignment taint propagation. Language support is not equivalent.
- `.html`, `.htm`, `.twig`, `.jinja`, `.jinja2` and `.vue` are discovered.
  Thymeleaf raw output, Twig `raw`, Jinja `safe`, Vue `v-html` and embedded JS
  patterns are candidates. Template binding, framework compilation and
  autoescape configuration are not resolved.
- Ordinary Python function-local names and earlier sink prefixes are isolated.
  Other languages retain conservative file-local scope. Assignment taint is
  monotonic, including after reassignment, because control-flow analysis is
  absent. Complex expressions, multiline sinks, classes, closures, aliases,
  comments/strings and nested scopes can yield false positives or negatives.
- The directory prepass binds only simple explicit sibling Python imports,
  JS named imports/destructured requires and PHP literal includes. It inspects
  recognized direct source returns. It does not resolve packages, dynamic
  imports, transitive call graphs or runtime rebinding. Unrelated files with
  identical function names are not shared taint providers. Explicit legacy
  caller-supplied sets remain a trusted API input, not resolved bindings.

`render_template_string` treats its first argument as template source. A
constant template with ordinary keyword parameters is distinct from concatenated
source (SSTI); explicit `|safe` keeps the raw-output candidate. The safe Python
fixture uses template parameters. This heuristic does not prove any runtime
template or sanitizer is safe.

Tests: `test_static_context.py` exercises identity/mixed encoders, trust markers,
context changes, source versus template parameters, file/name collisions,
template extensions and the C# boundary. `test_dxa.py` retains provenance and
existing language/fixture coverage. Future AST work remains a separate,
single-language pilot measured on labeled positive and negative examples;
there is no vulnerability-count quota for clean projects.
