# R8 bounded Leaflet source acceptance — 30 October 2026

Source-only, unreleased change after base commit
`1b1c1027af6b0d5cf43f14b8dbcc4b91d529a71a`. Published PyPI 0.2.2 is unchanged.

The analyzer recognizes proven default/namespace ES imports from `leaflet`,
marker `bindPopup`, popup `setContent`, and direct `divIcon({html: ...})`.
It separates fixed developer strings and locally proven literal div/span nodes
from dynamic HTML-content review candidates. Prior native HTML assignments
remain candidates. See [supported syntax and limits](../../tools/dom-xss-analyzer/STATIC-SCOPE.md).

## Acceptance

- Windows / Python 3.10.11: 67 independently authored Leaflet cases against the
  baseline produced 39 failures and 28 passes; against the final source they
  pass within a ten-file combined suite: **417 passed**, zero failures/errors/skips.
- Existing CI self-scan completed with high-confidence static candidates; this
  is a local run of the CI script, not a hosted CI result.
- Two unchanged owned source scopes retained all 20 and 129 previous candidates;
  zero new Leaflet candidates. All 233/47 inventoried source hashes remained
  unchanged. Scope B retains one known vendor-directory skip, so this is not a
  complete scan or an application safety result. No application was started.
- Separately, local Leaflet 1.9.4 in headless Chrome passed seven inert DOM
  assertions for string parsing versus node append and preservation of earlier
  markup. No external request occurred. Library/harness JavaScript ran, but no
  event payload or execution canary was used. This proves library branch
  semantics only, not an exploitable application vulnerability.

[Machine-readable acceptance](result.json) binds results to source/test hashes.
[Library oracle result](inert-library-result.json) records the library digest,
browser and seven checks. Raw XML, owned source reports, inventories, baseline
loader and local oracle harness remain private in ignored `.dxa/leaflet-20261030/`.
Public evidence contains no private source paths or code.

## Commands and review

Final selected regression command (from repository root):

```powershell
py -3.10 -m pytest tools/dom-xss-analyzer/test_static_leaflet.py tools/dom-xss-analyzer/test_static_jsx_href.py tools/dom-xss-analyzer/test_static_inline_messages.py tools/dom-xss-analyzer/test_static_receiver_bindings.py tools/dom-xss-analyzer/test_dxa.py tools/dom-xss-analyzer/test_static_context.py tools/dom-xss-analyzer/test_dxa_config.py tools/dom-xss-analyzer/test_r8_sanitizer.py tools/dom-xss-analyzer/test_r8_ast_pilot.py tools/dom-xss-analyzer/test_sarif.py -q -p no:cacheprovider --tb=short
py -3.10 bench/ci_self_scan.py
```

Actual suite invocation used `py -3.10 .dxa/run_leaflet_acceptance.py`, adding
private JUnit output. Its `--baseline` mode loaded exactly the base commit's
`dxa.py` into the test process before running the same 67 Leaflet cases.
Project comparison used the existing private source inventories and previous
0.2.2 raw candidate keys; no target code or data was changed.

Three native specialists worked concurrently with exclusive ownership:
`scanner_engine_specialist` (dxa.py), `qa_security_lab_specialist`
(test_static_leaflet.py), and `xss_security_researcher` (scope/API semantics).
The coordinator reviewed code and independent test oracles and ran integration.
All three specialist tasks are closed; no background work remains active.
An initial receiver/factory-name collision produced 1 failure/411 passes;
the next iteration passed 414. Coordinator probes then exposed mutations
inside executable template placeholders that invalidated factory/node proofs.
Two regressions and a literal-template negative control were added; final
417-pass acceptance supersedes those intermediate counts.

This lexical subset does not implement general JS typing, all Leaflet APIs,
callback-return flow, CommonJS/global bindings, arbitrary chains or option
spreads. Confidence describes source evidence. Findings stay
`candidate` / `unreviewed`, not browser execution or confirmed XSS. Broader
encoding/helper analysis and labeled precision/recall measurement remain open.
