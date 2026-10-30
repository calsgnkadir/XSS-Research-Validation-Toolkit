# DXA Research Toolkit

An evidence-oriented Python CLI toolkit for XSS research in controlled labs.
Version **0.2.1** is a documentation-only maintenance refresh of the PyPI
description and package metadata; runtime behavior is unchanged from 0.2.0.

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
python -m pip install dxa-research-toolkit==0.2.1
dxa --help
dxadyn --help
dxaprove --help
dxa-sarif --help
```

## Optional browser demo

Install the browser extra and Chromium, then choose a new output directory
for each run:

```console
python -m pip install "dxa-research-toolkit[browser]==0.2.1"
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
