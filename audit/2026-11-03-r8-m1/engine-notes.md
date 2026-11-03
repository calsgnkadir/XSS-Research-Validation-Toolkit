# R8-M1 engine investigation — 3 November 2026

Base: `220bbd2`. This is source analysis, not new acceptance evidence.
The engine owns `dxa.py` only after the coordinator authorizes implementation;
no scanner code was changed during this investigation. Existing working-tree
documentation changes belong to the coordinator and were preserved.

## Candidate behavior and root cause

The previous helper audit already records a missed source signal across a
same-file helper chain. The minimal synthetic candidate is:

```python
def first():
    return request.args['q']

def second():
    return first()

HTMLResponse(second())
```

Expected source-analysis behavior: preserve the existing HTML sink candidate
and expose the recognized request-source signal at that sink. This expectation
does not assert that the program is vulnerable or even runnable as written.

Source evidence in `tools/dom-xss-analyzer/dxa.py` at base `220bbd2`:

- Lines 1275–1279 accept return-expression calls only when the callee matches
  an encoder spelling or recognized Python source. `first()` meets neither
  rule, so no summary is created for `second` at line 1292.
- Lines 1319–1337 substitute an eligible helper once. The replacement return
  expression is not revisited, so merely allowing another helper name would
  not recover nested source provenance.
- Lines 1246–1268 reject unsupported function shapes and ambiguous bindings;
  lines 1301–1348 bound expression size and expansion. These are useful
  constraints to retain, rather than replacing them with general call-graph
  analysis.

## Reproduction status

A local `py -3.10 -c` synthetic scan was attempted on 3 November, but Windows
denied creating the WindowsApps Python process before the scanner executed.
No current observed sink result or test pass is claimed from that attempt.
The coordinator was notified. No application, HTTP, browser or external
target was run. An authorized real-source instance has not been established
by this engine investigation.

## Smallest proposed scope, pending selection and baseline freeze

If the same behavior is measured in authorized real source, prefer composing
eligible summaries of earlier unique top-level synchronous single-return
functions. Start with a small explicit maximum helper depth; retain direct
positional calls, exact arity, definition-before-use and existing size limits.
Reject cycles, forward references, ambiguous/rebound function names, aliases,
decorators, branches, methods, closures and dynamic calls. No implementation
should begin before development/evaluation cases and source identities are
frozen by QA and the coordinator.

Binding and context risks that need controls:

- Substitution must use only function parameter bindings, preserve raw operands
  and avoid introducing a guessed source from function names or string text.
- HTML-body encoder hints must not clear raw source in script, style,
  attribute or template-source contexts, including markup revealed only after
  expanding a helper chain.
- Explicit encoder rebinding, namespace replacement, wildcard imports and
  dynamic mutation must retain current conservative behavior.
- Recursive growth must keep existing node/text/expansion budgets; budget or
  unsupported-shape rejection is a coverage boundary, not evidence of safety.
- A constant-return chain should not acquire an input signal merely because
  an unused argument is tainted. A mixed raw/encoded return must retain raw
  provenance.

R8-M1 remains open. This file records the candidate and investigation status,
not a second roadmap, completed fix, general accuracy result or CV outcome.

## Selection update and separate JS hypotheses

The coordinator reported no actual Python-chain trigger in the currently
available owned sources. Python-chain implementation therefore remains
unselected. The engine was redirected to read-only JS source analysis while
security inspects actual authorized sources. No evaluation cases are owned
or inspected by the engine.

The following narrow shapes were sent to security as hypotheses, not observed
real-source failures:

- `compute_taint` around lines 1136–1146 passes quoted/comment RHS text to
  source and tainted-name matching. A fixed string containing an earlier
  tainted variable spelling could inherit an input signal.
- `_raw_return_names` around lines 399–411 matches raw JS return lines. A
  source spelling inside returned quoted text or a comment could mark a
  provider as source-returning.
- `scan_file` around lines 2280–2287 checks provider calls on the entire
  physical line outside conditional recovery. A sibling statement calling
  a provider could upgrade an unrelated sink on the same line.

These are candidates for a measured trigger search only. This investigation
does not select one for development or assert a vulnerability.

## Measured-candidate handoff: JSX sibling object prop

Security subsequently reported real owned-source anchors with flat
`href={identifier}` omitted when a sibling style attribute contains an object
expression. The engine independently verified the matching source-code
mechanism; security/coordinator own real-source reproduction evidence.

Minimal development seed:

```jsx
const view = <a href={target} style={{color: 'navy'}}>go</a>;
```

At `dxa.py:1678–1690`, `_jsx_href_candidates` marks the entire opening tag
unsupported when *any* expression reaches brace depth two. The nested style
object therefore defeats recognition of the separate flat href expression.
At line 1707, attribute consumption also uses the first closing brace rather
than its matching brace. Both decisions must be addressed together.

Proposed narrow change, awaiting coordinator baseline-freeze approval:

- Keep the opening-tag 32 KiB bound and a small bounded balanced brace stack;
  reject unclosed/underflowed braces and excessive nesting.
- Skip each non-href expression attribute using its matching closing brace.
  No source or URL-safety inference comes from that sibling expression.
- Retain nested-brace rejection for the actual href expression, and retain
  current spread, custom-component and namespaced-tag exclusions.
- Preserve flat href provenance and quoted/fixed href exclusions, offset and
  physical line mapping.

This addresses candidate coverage. Guarded real href values do not establish
a missed XSS. No implementation has begun at this handoff point, and engine
has not viewed QA's separate evaluation cases.

## Implementation after baseline freeze

The coordinator authorized implementation only after freezing the original
scanner and the 19-case QA split manifest. Engine has not read or run the
separate evaluation cases.

Only `_jsx_href_candidates` changed. It now indexes matching braces within
the existing 32 KiB opening-tag interval, caps nesting at 32, consumes complete
non-href expression props without analyzing their values, and still rejects
nested actual href expressions and all previously excluded spread forms.
Candidates are buffered until parsing all opening-tag attributes succeeds,
so a malformed later attribute cannot leave a partial href observation.

Initial implementation freeze SHA-256:
`7b999618f85fa56c24c054ae357b1df14041025c31c30f2d6ffabe6118988af1`.

The engine added `tools/dom-xss-analyzer/test_m1_parser_boundaries.py` with 16
development controls covering malformed later attributes, spread forms,
nested href exclusions, depth/tag budgets, sibling-name/source leakage and
self-closing tags. These are distinct from QA's evaluation corpus.

`git diff --check` passed with only the existing LF/CRLF conversion warning.
Python execution remains unavailable in the engine sandbox; the coordinator
was asked to run development checks and then the first separate evaluation.
No test pass is claimed here until the actual run result is received.

Before the first separate evaluation, coordinator and security source review
identified ambiguous duplicate href attributes. With the coordinator's edit
approval, the parser was amended to reject any second href attribute,
including literal or bare forms. Six design controls were added (22 total).
This was source-review feedback, not evaluation-case feedback.

Second implementation freeze SHA-256, established before first evaluation:
`1d3baa91fcf85e60d1be0e8bc4da06c99442e34b89ffe8b868190b3d985a70b4`.
The coordinator reported that development checks and 70 existing/design
checks passed on the earlier `7b9996` source; those are intermediate results,
not acceptance of this second source version. Coordinator owns final run
results and source binding. Engine still has not inspected evaluation cases.
