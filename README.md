# XSS Research Toolkit

An evidence-oriented Python CLI toolkit for researching and validating XSS
behavior in controlled labs. It combines heuristic source/sink candidate
analysis, bounded HTTP checks, and browser-based observations. Reports keep
reflection, parser placement, callback receipt, JavaScript execution, and
vulnerability triage as distinct evidence states.

**Current release:** [`dxa-research-toolkit 0.2.1` on PyPI](https://pypi.org/project/dxa-research-toolkit/0.2.1/) ·
[GitHub release](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/releases/tag/v0.2.0) ·
[Run the local demos](docs/PORTFOLIO-DEMO.md)

Version 0.2.1 refreshes the PyPI description and package metadata; runtime
behavior is unchanged from 0.2.0. See [publication evidence](audit/2026-10-30-pypi-portfolio/README.md).

The toolkit provides heuristic source/sink candidate rules for JavaScript and
TypeScript, Java, C#, PHP, and Python; bounded HTTP reflection and stored-input
checks; browser proof workflows for local fixtures; and HTML, JSON, and SARIF
reports. Analysis depth varies by language, and the static analyzer is not a
sound, interprocedural data-flow engine. This is a research-support prototype,
not a general-purpose autonomous scanner.

```console
python -m pip install dxa-research-toolkit
dxa --help
dxadyn --help
dxaprove --help
dxa-sarif --help
```

## How to use the toolkit

Create an ignored `.dxa/` output directory, then run the modes you need against
your own code and explicitly authorized local lab. These commands are separate
checks; the toolkit does not automatically turn one mode's result into proof
from another.

```text
# 1. Find heuristic source/sink candidates in a source tree.
dxa ./path/to/source --json-out .dxa/static.json --html .dxa/static.html --sarif-out .dxa/static.sarif

# 2. Check a reflected input on an authorized local HTTP target.
dxadyn "http://127.0.0.1:8000/search?q=demo" --json-out .dxa/http.json --html .dxa/http.html

# 3. Optionally collect bounded browser/DOM observations for a local page.
dxadyn "http://127.0.0.1:8000/" --dom --json-out .dxa/dom.json

# 4. Run the isolated canary demo; this starts its own loopback fixture.
dxaprove --demo --output .dxa/proof-demo
```

Static matches are candidates; an HTTP reflection is not proof of execution.
DOM observations are a separate browser result. The `dxaprove` demo proves a
canary only inside its own disposable fixture; it does not scan the HTTP target
above. Review the JSON/HTML/SARIF records and preserve these evidence boundaries
when triaging a result. The `--dom` and `dxaprove` commands require the optional
browser extra and Chromium described below; use a fresh proof output directory
for each run.

## Selected evidence-backed work

- **Read the case study:** [K01: stored XSS, output encoding, and retest](docs/K01-CASE-STUDY.md)
  explains the root cause, browser proof, negative controls, and reproducible lab.
- **Stored XSS proof → fix → retest:** [K01 local fixture](cases/k01-stored-comment/README.md)
  records a CID-matched browser execution, negative controls, output encoding,
  and a successful retest. This is a training fixture, not a third-party
  product finding.
- **Parser-context coverage test:** [E05 case](audit/2026-10-24-portfolio-cases/e05-case.md)
  measures inert marker placement in a `textarea` context with JavaScript
  disabled. It does not claim JavaScript execution or a confirmed vulnerability.
- **Installable release:** version 0.2.0 is published on PyPI; package and CLI
  installation checks are recorded in [the release audit](audit/2026-10-24-pypi-0.2.0/README.md).

## Project status and scope

The 0.2.0 release includes the offline SARIF CLI and E05 parser-context
extension. A04 is complete only for its selected local routes. A05 is frozen as
partial after one bounded multipart cleanup fixture; broader runtime and
deployment checks were not completed. K04's historical bypass has not been
faithfully retested: the matching artifact was not found in the searched local
paths, and the Docker image inventory could not be checked.
These limits, current handoff, and validation records are documented in
[STATUS](STATUS.md), the [roadmap](ROADMAP.md), and [VALIDATION](VALIDATION.md).
Use the tools only on systems you own or are explicitly authorized to test.

## Additional engineering evidence

- **Owned-source static evaluation (unreleased refinements):** measured and
  fixed FormData/router false positives on two owned source scopes, then added
  bounded inline HTML message-source tracking. See the [static scope](tools/dom-xss-analyzer/STATIC-SCOPE.md)
  and [acceptance](audit/2026-10-30-r8-inline-message/README.md). This is source
  analysis, not live deployment penetration testing or XSS discovery; published
  PyPI 0.2.1 remains unchanged.
- **Tooling failure → regression:** [R9 browser-fixture follow-up](audit/2026-10-16-r6-r9-final-source/README.md)
  records serial fixture failures, the threaded-server correction, and the
  full local Chrome DOM suite. This measures fixture reliability, not scanner
  accuracy.
- **Controlled research replay:** [R4 exact-payload replay](audit/r4-proof-experiment-2026-10-16/README.md)
  checks stored scanner candidates in separate writer/reader-admin loopback
  fixtures with escaped controls. Some outcomes remain inconclusive; it is not
  a fresh scanner comparison or a vulnerability ranking.

### Evidence handling

Stored blind attempts are retained even when no reflection appears, then checked
against the callback collector and reported in JSON/HTML journals. A callback
is resource evidence, not JavaScript execution. See the [blind journal contract](tools/dom-xss-analyzer/BLIND-JOURNAL.md).

HTTP modes share a finding producer, and `--json-out` and `--html` report the
same findings. A raw marker or JSON response is not execution evidence. See the
[HTTP evidence contract](tools/dom-xss-analyzer/HTTP-EVIDENCE.md).

The 0.2.0 package includes offline [SARIF 2.1.0 export](tools/dom-xss-analyzer/SARIF.md):
`dxa-sarif evidence.json --output evidence.sarif`. Results preserve observation
and triage categories as review records, without vulnerability severity or
execution claims.

The accepted R1–R3 work covers shared evidence reporting, HTTP session/rate/CSRF
controls, and a bounded loopback browser-proof workflow. It does not provide a
general network sandbox. See the [R1 closure](audit/2026-10-05-r1/R1-KAPANIS.md),
[HTTP session contract](tools/dom-xss-analyzer/SESSION-CONTRACT.md), and
[browser-proof scope](tools/dom-xss-analyzer/BROWSER-PROOF.md).

Historical reviews are available in the [2026-09-28 audit report](audit/2026-09-28/DENETIM-RAPORU-TR.md)
and [file-by-file review](audit/2026-09-28/DOSYA-INCELEMESI-TR.md).

- [Current status and limitations](STATUS.md)
- [Project roadmap](ROADMAP.md)
- [Historical original-ZIP file-to-task mapping](DOSYA-KAPSAM.md)
- [Validation record](VALIDATION.md)
- [Changelog](CHANGELOG.md)
- [Historical message review](HISTORY-NOTES.md)

## Tools and boundaries

| Component | Function | Boundary |
|---|---|---|
| `dxa.py` | Static source/sink candidates, with a bounded Python AST pilot | Language coverage differs; this is not general sound data-flow analysis |
| `dxadyn.py` | HTTP reflection, stored checks, and bounded same-origin discovery | Findings are candidates/reflections; they do not alone establish XSS |
| `dxadom.py` | Playwright page, sink, dialog, route, and header observations | Bounded loopback adapter; observation is distinct from CID-matched execution |
| `dxa_callback.py` | Local callback collection and lookup | A matched callback is `resource-callback`, not JavaScript execution |
| `dxa2dyn.py` | Parameter hints from static candidates | A hint is not a complete source-to-sink proof |

Payload-corpus metadata lists 50 base variants and 18 mutation definitions.
The historical generator count of 950 strings (895 after removing CID-specific
uniqueness) describes generated inputs only; it is not a count of working
exploits, successful executions, WAF bypasses, or findings. The HTTP and static
core use the Python standard library; tests use pytest, and browser observation
uses Playwright with a supported browser.

## Install from this checkout

Python 3.10 or later is required. From the repository root, create an environment
and install the checkout:

```console
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install .
dxa --help
dxadyn --help
dxaprove --help
dxa-sarif --help
```

macOS/Linux:

```console
source .venv/bin/activate
python -m pip install .
dxa --help
dxadyn --help
dxaprove --help
dxa-sarif --help
```

The base install has no required runtime dependencies. To run the browser-proof
demo, install the optional browser extra, pinned to `playwright==1.63.0`, and
install the Chromium browser:

```console
python -m pip install ".[browser]"
python -m playwright install chromium
dxaprove --demo --output demo-evidence
```

The demo starts and stops its own temporary loopback fixture. Choose a fresh
output directory for each run. `execution-observed` records a canary observed
in this fixture; it is not vulnerability triage or a claim about general browser
accuracy. For another authorized loopback lab, use `dxaprove --spec <local.json>`;
this proof contract is separate from `dxa` and `dxadyn` scan configuration. Run
scans only against your own fixtures or explicitly authorized targets.

The current published package is `dxa-research-toolkit 0.2.1`; `0.1.0` remains
the historical GitHub release. The tool is an experimental research assistant;
see [STATUS](STATUS.md) and the linked audits for scope and evidence limits.

For `dxadyn`, the `--dom`, `--stored`, and `--flow` modes are mutually
exclusive. Stored/flow targets are supplied through their mode options rather
than a positional URL. `--dom` does not accept HTTP session options such as
`--login`, `--auth-flow`, `--auth-check`, `--cookie`, `--header`,
`--csrf-refresh`, or `--csrf-header`. Unsupported combinations exit with code 2
before network/browser activity or report writes. Use `dxaprove` for a
session-aware browser proof.

### Static `dxa` configuration

```json
{"schema_version": 1, "min_confidence": "medium"}
```

For `dxa <local-source> --config scan.json`, precedence is
`--min-confidence` > config > the default `low`. This limited config contract
applies only to the static CLI; do not put session data in the file.

The dynamic `dxadyn` CLI has a separate, limited HTTP tuning config:

```json
{"schema_version": 1, "depth": 1, "parallel": 1, "rate": 0}
```

For an authorized local target, `dxadyn <local-url> --config http.json --depth 0`
uses explicit CLI values before config, then defaults (`depth=0`, `parallel=1`,
`rate=0`, unlimited). Depth applies to reflected mode, parallel to reflected/stored,
and rate to HTTP modes. DOM rejects HTTP tuning. Worker count does not promise
parallel HTTP throughput; shared-session HTTP transactions remain serialized.

UTF-8 BOM is supported. Unknown/duplicate fields, invalid types/version, negative
depth/rate, parallel below one, nonfinite rate and irrelevant mode settings return
exit 2 before target/session/browser I/O. CLI overrides cannot hide invalid config.
Targets, credentials and output paths are not config fields. `dxaprove --spec`
retains its separate proof contract.
[Config scope and validation](audit/2026-10-15-r6-config-release/README.md).

## Historical research records

- [Historical technical writeups](writeups/README.md): XSS, SQL injection, JWT,
  BOLA, and tool development.
- [Raw v3.10 reports](reports/2026-09-26-v310-live/README.md): 50 JSON-only
  rows, two Bludit HTTP records, and 78 static MEDIUM candidates; these are not
  an independently verified vulnerability total.
- [Screenshots](screenshots/README.md): evidence of workflow and selected
  challenge/source/filter steps, not independent proof of every claimed
  execution.
- [Research records](research/README.md): historical reproduction/duplicate
  claims; acceptance evidence and any new-CVE credit are not independently
  established by these archives.

For a current case, publish the version and command with masked request/response,
canary proof, negative controls, and a post-fix retest. Historical claims remain
bounded by the evidence recorded in STATUS and the roadmap.

## Research principle

Treat candidate detection, reflection, browser execution, and vulnerability
triage as separate claims. The [roadmap](ROADMAP.md) records current priorities;
historical plans are not current acceptance evidence.

[MIT License](LICENSE). [Legacy README](README-LEGACY.md) is historical only.
