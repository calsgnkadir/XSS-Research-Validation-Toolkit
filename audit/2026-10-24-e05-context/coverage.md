# E05 — independent context coverage review

Date: 24 October 2026. Baseline source: toolkit `532be7ac01e82fbe0612749ead6d3cb39f0be7e9`.
Native role: `qa_security_lab_specialist`; exclusive ownership of this record
and `bench/test_e05_context_coverage.py`. The coordinator owns integration and
acceptance; the security specialist owns the new production variant and its
unit/transport regressions. No existing corpus totals are reclassified.

## Source review and selected gap

The existing registry consists of historical marker shapes. A returned marker
is reflection evidence; its variant name does not establish parser placement,
execution, sanitizer bypass, or a vulnerability. Registry/mutation shape counts
are not the coverage metric used here.

| Context | Existing source/test coverage at baseline | Gap / disposition |
|---|---|---|
| Body HTML and escaped body | `bench/run.py:369–370`; `bench/test_proof_corpus.py:25–26` label image-canary raw/escaped controls | Existing bounded execution controls; no reopening of R4 |
| Title RCDATA | `dxadyn.py:86` provides `title-breakout`; `bench/run.py:375` labels the default image inert in title | Targeted marker exists; no broad title completeness claim |
| Textarea RCDATA | `dxadyn.py:153–155` provides `textarea-onfocus-breakout`, whose marker precedes its closing textarea tag; `bench/run.py:376` and `bench/test_proof_corpus.py:32` cover default-image inertness | **Selected E05 gap:** no family places the marker after an end tag that closes the surrounding textarea |
| HTML comment | `dxadyn.py:117` provides a comment terminator; `bench/run.py:383` labels the default image inert in comments | Existing terminator shape and negative execution control; not selected |
| Template inert / activated | `bench/run.py:384–385`; independent native-browser oracle `bench/test_proof_corpus.py:217` | Existing context-specific negative/positive execution pair; not selected |
| XMP raw text | `dxadyn.py:259–262` provides `xmp-breakout` | Existing terminator shape only; broader parser coverage not inferred |
| Quoted attributes, script strings, style/CSS | `dxadyn.py:88,112,189–208`; wrong-context controls `test_http_evidence.py:51–67` | Source shapes and conservative reflection labels exist; complete parser/execution coverage was not measured by this task |

Paths abbreviated above are under `tools/dom-xss-analyzer/` except `bench/`.
Line references identify the baseline source; adding the variant moves later
production lines. The matrix distinguishes existing source/test cases from
newly reproduced runtime behavior; it is not a new execution accuracy score.

## Independent oracle

`bench/test_e05_context_coverage.py:85` enumerates all 50 baseline non-blind
families with their base plus 18 mutations (950 generated attempts) through the real generator, then passes those
strings to Chromium's native `DOMParser` inside a textarea document. The oracle
counts actual `dxss` elements rather than matching a closing-tag substring or
trusting scanner labels. The parsed documents are inert: handlers and resources
from historical probe strings are not activated.

`bench/test_e05_context_coverage.py:109` navigates a disposable loopback server
with the real generated probe. It checks DOM placement for a targeted raw
textarea positive and four controls: HTML-escaped targeted probe, default body
probe, mismatched title terminator, and the old textarea-onfocus family. Page
JavaScript is disabled; the assertion concerns native marker-element placement,
never execution. The server/thread are closed and joined after each case.

Acceptance command (coordinator-run because the specialist sandbox cannot start
the WindowsApps Python runtime):

```powershell
$env:DXA_REQUIRE_BROWSER='1'
py -3.10 -m pytest bench/test_e05_context_coverage.py -q -p no:cacheprovider --tb=short
```

`DXA_REQUIRE_BROWSER=1` makes missing Playwright/Chromium a failure, not a passing
skip. On Windows the test discovers the existing Chrome executable or accepts
`DXA_BROWSER`; on Linux it accepts installed Playwright Chromium.

The coordinator ran this command before the production edit on Windows / Python
3.10.11 with the existing Chrome executable: **1 failed, 5 passed** in 9.16s.
The targeted raw textarea case failed at the native DOM assertion: expected one
marker element, observed zero. The exhaustive legacy-family/mutation test and
all four escaped/inert controls passed. This is a reproduced missing-context
case, not merely a source hypothesis. No browser test was skipped.

After the production edit, the coordinator ran this combined selection:

```powershell
$env:DXA_REQUIRE_BROWSER='1'
py -3.10 -m pytest tools/dom-xss-analyzer/test_e05_context.py bench/test_e05_context_coverage.py tools/dom-xss-analyzer/test_dxadyn.py tools/dom-xss-analyzer/test_http_evidence.py tools/dom-xss-analyzer/test_json_transport.py tools/dom-xss-analyzer/test_blind_journal.py tools/dom-xss-analyzer/test_r1_contract.py tools/dom-xss-analyzer/test_sarif.py -q -p no:cacheprovider --tb=short --junitxml=.dxa/e05-acceptance.xml
```

Result: **381 passed, zero failures/errors/skips**, 43.01s for the entire
combined selection. All six independent browser cases are included; no separate
after-change browser duration or full-suite run is claimed. The targeted raw
response now produces one parsed marker element outside textarea, while the
950 legacy attempts and all four navigation controls still produce none.

The measured change is **zero prior generated shapes producing a parsed marker
outside textarea → one targeted base shape producing that marker**, with the
escaped/inert controls remaining zero. This is a bounded parser-context
reach measurement, not an execution score. Browser execution, deployment behavior,
WAF bypass, vulnerability confirmation, external scans and the reserved A05
malformed multipart test are outside this task.

Ownership is released to the coordinator for final review and integration.
The specialist did not commit, push, replace a release or inspect hosted
artifacts; hosted CI is separate from this local coordinator-run acceptance.
