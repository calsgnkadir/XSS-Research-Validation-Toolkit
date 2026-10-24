## Case 2 — Measuring an HTML `textarea` parser context

**Roadmap:** E05. **Target and scope:** the toolkit's own probe generator and
inert local Chromium parser fixtures. This was not a test of a third-party
application. Page JavaScript was disabled for the independent browser oracle.

**Question:** did the existing generated probe set place a marker element
outside a surrounding `textarea`, and did the selected tool corpus include a
probe for that parser context?

**Method and observed result:** the independent oracle enumerated 50 existing
non-blind families with 18 mutations each (950 generated attempts) in inert
native-browser parsing; none created a marker element outside textarea RCDATA.
The targeted raw closing-textarea marker probe created one such element.
Four controls—the HTML-escaped form, default body probe, mismatched title
terminator, and prior textarea-opening probe—created none. After the narrowly
scoped probe was added, the selected eight-file local suite passed **381 tests,
with zero failures, errors, or skips**. This was a selected suite, not a full
project-suite result.

**What the evidence supports:** a measured parser-context coverage gap existed
in that bounded generated set, and the inert marker probe now reaches the
outside-textarea parse location in the controlled Chromium fixture. The tests
distinguish real parsed elements from string reflection or a matching closing
tag substring.

**What it does not support:** the oracle did not run JavaScript. It does not
prove an `execution-observed` result, a confirmed XSS vulnerability, security
impact, sanitizer bypass, WAF bypass, or general scanner accuracy. HTTP
evidence remains `reflection` / `unreviewed`; the inert marker result is a
separate parser observation, not HTTP reflection upgraded to a finding. No
fix/retest of an affected product is claimed; this is an analyzer context
extension, and the change is unreleased beyond the public `v0.1.0` artifact.

**Evidence:** [E05 acceptance and limits](../2026-10-24-e05-context/README.md),
[independent coverage oracle](../2026-10-24-e05-context/coverage.md),
[implementation and tested hashes](../2026-10-24-e05-context/implementation.md),
and the [evidence contract](../../tools/dom-xss-analyzer/EVIDENCE-CONTRACT.md).

**CV wording:** “Measured a textarea/RCDATA parser-context coverage gap in an
XSS research CLI using a JavaScript-disabled Chromium marker oracle; added an
inert probe and negative controls, while keeping parser placement separate
from JavaScript-execution and vulnerability claims.”
