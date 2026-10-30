# Static source analysis: current source-checkout refinements

These refinements are **unreleased**. Published PyPI 0.2.1 remains the earlier
runtime baseline. Static output is a review candidate, not JavaScript execution
or a confirmed vulnerability. Confidence describes source evidence, not impact.

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
does not claim general JS control-flow precision. JSX URL, Leaflet HTML and
Jinja-in-JavaScript context coverage are separate follow-up work.

[Inline acceptance](../../audit/2026-10-30-r8-inline-message/README.md) records
source hashes, baseline failures, independent controls and local results.
