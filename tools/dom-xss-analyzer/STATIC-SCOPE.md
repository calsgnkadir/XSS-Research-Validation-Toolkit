# Static source analysis: 0.2.2 scope

Version **0.2.2** includes the three released refinements described before the
separate **UNRELEASED** sections. The Leaflet and same-file Python helper
source extensions are not part of the published 0.2.2 package.
Historical PyPI 0.2.1 artifacts retain
their earlier runtime baseline. Static output is a review candidate, not
JavaScript execution or a confirmed vulnerability. Confidence describes source
evidence, not impact or measured scanner accuracy.

## Receiver false positives

The source analyzer distinguishes bounded native `FormData` append calls from
jQuery HTML insertion, and the declaration `const location = useLocation()`
from browser navigation. Real navigation, real jQuery insertion and unknown
receivers remain candidates. Constructor shadows/mutations, receiver escape,
scope changes and uncertain syntax prevent a local exclusion proof. This is
lexical disambiguation with a 32 KiB local lookup, not general type analysis.

[Acceptance](../../audit/2026-10-30-r8-receiver-fix/README.md) includes independent
regressions and comparison on two unchanged owner-provided source scopes.
Those project tests are static source checks, not live deployment pentests.

## Inline HTML message sources

For `.html` and `.htm`, the analyzer can associate a source read with an actual
executable inline script and a supported direct message callback:

```html
<script>
window.addEventListener('message', event => {
  preview.innerHTML = event.data;
});
</script>
```

Supported callback forms include a single arrow parameter (with optional
parentheses) and `function(event)`, with a flat body of at most 32 KiB. Local
value assignments from `event.data` are tracked within the supported interval.
Physical source lines and the R1 candidate/unreviewed report contract remain
unchanged. An origin comparison is not interpreted as proof of safety.

HTML text/comments, non-executable script types and external-script bodies do
not create inline message provenance. Ordinary `object.data` does not become
message data merely because a listener exists. Nested callbacks/blocks,
templates, destructuring, handler aliases, listener options, `onmessage`, and
propagation after parameter escape/mutation are outside this bounded subset.
Other sink matches remain ordinary candidates; unsupported syntax is not safe.
Malformed HTML rejected by the parser retains generic matches and emits an
analysis error event. It must not be counted as a successful clean scan.

Legacy JavaScript-file message heuristics are unchanged; the new HTML subset
does not claim general JS control-flow precision. The separate Leaflet source
extension is described below; Jinja-in-JavaScript context coverage remains separate.

[Inline acceptance](../../audit/2026-10-30-r8-inline-message/README.md) records
source hashes, baseline failures, independent controls and local results.

## JSX anchor href candidates

In `.jsx` and `.tsx` files, the analyzer recognizes flat lowercase intrinsic
`<a href={...}>` opening tags. Opening-tag scanning and local source-provenance
lookup are each bounded to 32 KiB. Supported direct source expressions and
locally tracked identifiers receive high source-evidence confidence; unknown
nonliteral href expressions remain medium-confidence review candidates.

Fixed URLs and ordinary JSX text are negative controls for this rule.
Spread attributes, nested braces, custom components, namespaced tags and guard
resolution are unsupported. The rule does not provide full AST analysis,
coverage of all JSX props or arbitrary expressions, component rendering,
interprocedural propagation or runtime URL behavior. An unsupported form or
absence of a candidate is not evidence of safety. A candidate remains
`candidate` / `unreviewed`; confidence describes source evidence, not impact.
No browser execution, confirmed vulnerability or general accuracy improvement
is inferred.

## UNRELEASED — Leaflet HTML API candidates (R8)

This accepted narrow source extension is **UNRELEASED**. Leaflet support is
not included in the historical PyPI 0.2.2 features above.

Only ES default/namespace imports from literal `leaflet` establish the intended
library binding: `import L from 'leaflet'` or `import * as ns from 'leaflet'`.
In JavaScript-family source files, the supported subset is
`ns.marker(...).bindPopup(content)`, `ns.popup().setContent(content)`, exact local
`const` marker/popup factory receivers calling those respective methods, and
`ns.divIcon({html: content})`. Namespace escapes, rebinding, property writes and
namespace/receiver shadowing defeat library proof, conservatively even when
elsewhere in the file. Arbitrary methods with the same names do not establish
it. Receiver aliases and intervening chains are unsupported. DivIcon options
must be a direct object with ordinary identifier keys and exactly one `html`
property; spreads, computed/quoted keys and methods are unsupported.

Calls and local binding/provenance lookups are bounded to 32 KiB. Immutable
`const` expansion is limited to depth 16 and 64 provenance reads. Fixed quoted
strings and templates without interpolation, including supported const chains,
are excluded. Simple template identifier/member interpolations can supply source
evidence; complex expressions are not general template evaluation. Adjacent
interpolations are kept separate and literal text cannot invent source tokens.
A separate interpolation walk invalidates binding/DOM proofs on executable
references, bounded to 32 KiB per interpolation and nesting 32. Uncertain or
malformed syntax cannot establish those proofs. This is lexical recognition,
not full AST, type, closure or control-flow analysis. Direct/tracked source
evidence gives high confidence; unknown content remains medium confidence.

Leaflet's [1.9.4 API](https://leafletjs.com/reference.html#layer-bindpopup)
permits string, element, function and Popup content for `bindPopup`.
Binding sets up an overlay; it does not itself prove rendering.
[Popup binding source](https://github.com/Leaflet/Leaflet/blob/v1.9.4/src/layer/Popup.js#L375-L394).
[`setContent`](https://leafletjs.com/reference.html#popup-setcontent) stores
content; when updated on a map, resolved strings reach `innerHTML`, while
nonstring node content is appended. Function results follow the same split.
[Overlay source](https://github.com/Leaflet/Leaflet/blob/v1.9.4/src/layer/DivOverlay.js#L162-L189),
[content update](https://github.com/Leaflet/Leaflet/blob/v1.9.4/src/layer/DivOverlay.js#L269-L282).
[`divIcon` HTML](https://leafletjs.com/reference.html#divicon-html) appends an
`Element`; other values take its `innerHTML` branch when the icon is created.
[Icon source](https://github.com/Leaflet/Leaflet/blob/v1.9.4/src/layer/marker/DivIcon.js#L41-L50).

Fixed strings and templates without interpolation are negative controls for
this dynamic-content rule. The DOM exclusion recognizes unshadowed, unmodified
`document.createElement('div')` / `document.createElement('span')`, directly or
through supported unique immutable const bindings, including empty elements and those
populated through `textContent`: passing such an element is not a new string
parse. A `textContent` assignment is not required for that branch distinction.
This does not clear prior
`innerHTML` or unsafe `setAttribute` operations. Arbitrary DOM tags, including
created script elements, do not inherit that exclusion or a safety verdict.
Unknown string/DOM types remain conservative review candidates. DomUtil.create
is not part of the DOM proof. Absence of a Leaflet candidate does not establish safety.
Function-return analysis, Popup-instance overload tracking, named/CommonJS
imports, global `L`, arbitrary aliases, option spreads and general control-flow
analysis are outside this subset. Inline HTML scripts do not gain this Leaflet rule.

Coordinator acceptance for `dxa.py` SHA-256
`1b9aa186f58794affe0597f105c60845d0e3d9a586f08ec435e9577b8e8049fa`:
combined local suite **417 passed**, zero failures/errors/skips. Separately,
seven inert Leaflet 1.9.4 browser DOM checks passed, confirming string parsing,
node non-reparsing and retention of prior markup, with zero external requests.
They used no application visit, event payload, callback or execution canary.
The two unchanged owned source scopes retained 20/129 candidates and produced
zero new Leaflet candidates. These are coordinator-run results, not tests rerun
for this documentation edit or a general accuracy/safety measurement.

Static results remain `candidate` / `unreviewed`. Neither reflection,
sink observation nor resource callback is browser execution; execution itself
still requires separate vulnerability triage. See the
[evidence contract](EVIDENCE-CONTRACT.md) and [browser proof](BROWSER-PROOF.md).

## UNRELEASED — same-file Python return helpers (R8)

The Python AST pilot can substitute a narrow same-file helper's return
expression into a later call, both in assignments and directly at supported
sinks. This adds local return summaries, not a general interprocedural graph.
Only a unique top-level, synchronous, undecorated function with one `return`
statement and ordinary positional parameters is eligible. Calls must follow
the definition in source order and supply exactly those positional arguments.
Defaults, keyword arguments, starred arguments, methods, closures, async
functions, helper-to-helper calls and recursive returns are outside this subset.

Return expressions may use their parameters, constants, recognized source
reads and recognized encoder calls. Unknown free names or arbitrary function
calls prevent a summary. Conflicting helper definitions, imports, assignments,
parameter shadows, exception/pattern bindings and use of the helper as a value
prevent substitution. A wildcard import disables these local summaries.
Unsupported helpers retain the ordinary conservative argument provenance;
source reads hidden inside an unsupported helper may still be missed.

Raw provenance and the HTML-body mitigation view remain separate. For example,
`def encode(value): return html.escape(value)` can provide the same limited
HTML-body hint as the recognized direct encoder spelling. It does not erase
raw provenance used for template-source or embedded script/style/attribute
contexts. Mixed encoded and raw terms retain the raw term. Encoder rebinding
defeats the wrapper's mitigation hint conservatively. Recognized spellings do
not validate library origin, configuration, runtime behavior or output safety.
An encoded HTML-body sink remains a review candidate at lowered confidence.
The new wrapper check treats detected receiver/property writes and explicit
dynamic mutation constructs conservatively, even when they occur in unrelated
code. It does not resolve arbitrary runtime mutation, alias-based changes or
the effects of unknown calls.

The return expression is limited to 64 AST nodes and 16 parameters. Input
expressions are limited to 32 KiB and 2,048 AST nodes; expansion allows at most
64 substitutions, a 2,048-node total budget and a 32 KiB output limit.
Exceeding a bound retains the affected call or unexpanded expression. Branch
feasibility,
side effects, arbitrary call effects, aliases, packages and transitive flow
are not resolved. Other language rules and the separate sibling-import
prepass do not gain these summaries. Python `eval` is not a supported sink;
the generic encoder warning about eval is not a Python sink-coverage claim.

These labeled examples define source-evidence expectations for local checks,
not an estimate of scanner accuracy or application vulnerability:

| Example at a supported sink | Expected source-evidence result |
|---|---|
| `read(): return request.args["q"]`; `HTMLResponse(read())` | High candidate: source returned by a supported helper |
| `identity(value): return value`; source argument passed through it | High candidate: raw argument survives |
| `encode(value): return html.escape(value)` into an ordinary HTML body | Medium candidate: limited mitigation hint; no safety verdict |
| The same encoded result as `render_template_string` template source | High candidate: HTML encoding does not remove raw template-source provenance |
| Encoded helper result concatenated with a raw source | High candidate: raw residual survives |
| Fixed literal source text or a constant-return helper | No invented high source signal; an ordinary sink candidate can remain |
| A source read hidden in a branch-bearing or chained helper | Outside the subset; absence of high confidence can be a miss |

New test results, source hashes and any measured confusion counts belong to
the dated acceptance record. They must identify the exact labeled examples;
they do not establish general precision, recall, browser execution or XSS.
