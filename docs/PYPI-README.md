# DXA Research Toolkit

An evidence-oriented Python CLI toolkit for XSS research in controlled labs.
Version **0.2.2** includes the bounded static-source improvements described
below. Version **0.2.1** remains the
historical documentation-only refresh with runtime behavior unchanged from 0.2.0;
its published artifacts are not replaced.

[Project README](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/blob/main/README.md) ·
[Local demo guide](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/blob/main/docs/PORTFOLIO-DEMO.md) ·
[K01 case study](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/blob/main/docs/K01-CASE-STUDY.md)

## Capabilities and limits

- `dxa`: heuristic source/sink candidate analysis for JavaScript/TypeScript,
  Java, C#, PHP and Python, with HTML, JSON and SARIF output. Analysis depth
  varies by language; it is not sound, interprocedural data-flow analysis.
- `dxadyn`: bounded HTTP reflection and stored-input checks, same-origin
  discovery, and optional browser/DOM observations.
- `dxaprove`: bounded browser proof workflows with a disposable loopback demo.
- `dxa-sarif`: offline SARIF 2.1.0 export from supported evidence JSON.

## Static-source changes in 0.2.2

- Receiver false-positive fix: bounded lexical checks distinguish native
  `FormData.append()` and `const location = useLocation()` declarations from
  jQuery HTML insertion and browser navigation. Real sinks and unresolved
  receivers remain candidates; this is not general type resolution.
- Inline HTML message-source tracking: executable inline scripts in `.html`
  and `.htm` support direct window message callbacks, their `event.data` reads
  and local value assignments within a bounded flat body of at most 32 KiB.
  HTML text/comments, non-executable or external scripts and unrelated
  `object.data` do not establish this provenance. Nested callbacks/blocks,
  handler aliases and arbitrary control flow are outside this subset.
- JSX anchor href candidates: `.jsx`/`.tsx` support flat lowercase intrinsic
  `<a href={...}>` opening tags, with 32 KiB opening-tag and local provenance
  bounds. Supported direct sources and locally tracked identifiers receive
  high source-evidence confidence; unknown nonliteral href expressions receive
  medium confidence. Fixed URLs and ordinary JSX text are negative controls.
  Spread attributes, nested braces, custom components, namespaced tags and
  guard resolution are unsupported. This is not a full AST analysis and does
  not cover all props, component rendering or interprocedural data flow.

See the [static scope and exclusions](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/blob/main/tools/dom-xss-analyzer/STATIC-SCOPE.md),
[receiver acceptance](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/blob/main/audit/2026-10-30-r8-receiver-fix/README.md)
and [inline-message acceptance](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/blob/main/audit/2026-10-30-r8-inline-message/README.md).
These are bounded source-analysis changes, not browser execution results or
measurements of general scanner accuracy.

Static candidates, HTTP reflections, sink observations, resource callbacks,
browser execution and vulnerability triage remain separate evidence states.
A reflection or callback alone does not prove JavaScript execution. Even a
matched browser canary does not establish a confirmed vulnerability or CVE.
Errors, timeouts and missing browsers are not evidence of safety.

This is a research-support prototype with bounded coverage, not a
general-purpose autonomous scanner or general network sandbox. Use it only
on systems you own or are explicitly authorized to test. See the current
[status and limitations](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/blob/main/STATUS.md).

## Install

Python 3.10 or later is required. The core CLI uses the Python standard library.

```console
python -m pip install dxa-research-toolkit==0.2.2
dxa --help
dxadyn --help
dxaprove --help
dxa-sarif --help
```

## Optional browser demo

Install the browser extra and Chromium, then choose a new output directory
for each run:

```console
python -m pip install "dxa-research-toolkit[browser]==0.2.2"
python -m playwright install chromium
dxaprove --demo --output dxa-proof-demo-001
```

The demo starts its own disposable loopback fixture and writes JSON/HTML
evidence. An `execution-observed` result applies only to that fixture;
triage remains `unreviewed`. It does not scan another application.

The [K01 case study](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/blob/main/docs/K01-CASE-STUDY.md)
describes a local stored-comment fixture, negative controls, output encoding
and retesting. K01 runs from a repository checkout, separately from the
installed-package demo; it is a training case, not a third-party product finding.
Follow the [demo guide](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/blob/main/docs/PORTFOLIO-DEMO.md)
for the checkout-based K01 commands and evidence boundaries.
