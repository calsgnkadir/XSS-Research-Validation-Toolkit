# R4 / R6 / R8-M1 — pinned local acceptance

Reviewed source commit: `ccdf661abae8a887c30e78e9cbf644133c7f686e`.
Starting fetched source: `3e34515774b16a20c99aa6761f425f2bb36aebdf`, clean,
HEAD/origin difference 0/0. The source commit includes the reviewed HTTP
completion fix, mock fixture repair and JSX presentation tooling. A later
evidence-only commit records final outcomes without changing runtime/tests.

Windows / Python 3.10.11 / Playwright 1.63.0 / local Chrome
156.0.8078.80. Tests use synthetic source and disposable loopback labs only.
No external target, Docker data mutation, PyPI upload or new release tag.

| Acceptance scope | Fresh result |
|---|---|
| Full tools/bench pytest | 2055 passed / 38 skipped / zero failures or errors |
| Complete dxadom repeat with explicit Chrome | 80 passed / zero skips; all original skipped IDs passed |
| Frozen HTTP/runner regressions | 115 passed / zero skips |
| Required R3/R4 browser selection | 224 passed / zero skips |
| JSX selected suite + measurement | 607 passed; 19/19 completed with correct properties; self-scan passed |
| Strict HTTP / proof corpus | completed 3/3 / 17/17; TP/FP/FN 2/0/0 / 8/0/0 |
| Pinned clean package install | 11 equal module hashes, 9 CLI checks + 19 JSX cases passed |
| JSX before/after terminal demo | exit 0; expected minimal/split comparisons reproduced |
| Authenticated loopback browser demo | execution-observed; no events |

These runs overlap; do not add their counts. [Machine-readable acceptance and
source hashes](result.json), [pinned package proof](package-pinned-result.json),
[fresh JSX selected repeat](jsx-result.json). The broad JUnit includes the final
actual-404 regression. Root `cases/` and independent application suites were
not included in the full tools/bench run.

## Reproduction

Use this source commit and new output paths. Commands below are PowerShell,
run from the repository root. The full source/benchmark suite requires pytest,
jsonschema and Playwright; package checking also requires setuptools and wheel.
Set the browser path to an installed compatible Chrome executable.

```powershell
$env:DXA_REQUIRE_BROWSER='1'
$env:DXA_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
py -3.10 -m pytest tools/dom-xss-analyzer bench -q -p no:cacheprovider --tb=short --junitxml=.dxa/repeat-full.xml
py -3.10 -m pytest bench/test_bench.py bench/test_http_completion.py bench/test_runner_isolation.py -q -p no:cacheprovider --tb=short --junitxml=.dxa/repeat-http.xml
py -3.10 audit/2026-11-03-r8-m1/run_validation.py
py -3.10 audit/2026-11-03-release-acceptance/package_check.py --out .dxa/repeat-package.json
py -3.10 audit/2026-11-03-release-acceptance/demo.py --out .dxa/repeat-jsx-demo.json
$env:BENCH_STRICT='1'
py -3.10 bench/run.py --targets mock-reflected-easy,mock-reflected-escaped,mock-stored-guestbook --no-history --out .dxa/repeat-http.md
py -3.10 bench/run.py --proof-suite --browser $env:DXA_BROWSER --no-history --out .dxa/repeat-proof.md
py -3.10 tools/dom-xss-analyzer/dxaprove.py --demo --browser $env:DXA_BROWSER --output .dxa/repeat-browser-demo
```

The actual first broad run set `DXA_REQUIRE_BROWSER=1` but did not set
`DXA_BROWSER`. Some older dxadom tests therefore skipped automatic discovery;
an explicit-path repeat of the complete dxadom module followed. Skips in the
first run are reported as skips; the two runs are not combined into a new
single-run pytest total. The standalone required R3/R4 browser selection also
ran:

```powershell
py -3.10 -m pytest tools/dom-xss-analyzer/test_browser_proof.py tools/dom-xss-analyzer/test_proof_cleanup.py bench/test_proof_adapter.py bench/test_proof_corpus.py bench/test_proof_identity_matrix.py bench/test_auth_failure_corpus.py bench/test_blind_admin_contract.py bench/test_auth_failure_runner.py bench/test_r4_two_account_fixture.py bench/test_r4_comparison_fixture.py bench/test_r4_cid_oracle.py bench/test_e05_context_coverage.py -q -p no:cacheprovider --tb=short --junitxml=.dxa/repeat-required-browser.xml
py -3.10 -m pytest tools/dom-xss-analyzer/test_dxadom.py -q -p no:cacheprovider --tb=short --junitxml=.dxa/repeat-dxadom.xml
```

The optional attempt to run `bench/check_ci_acceptance.py` on these local
artifacts exited 1. Its `check_provenance` explicitly requires Python 3.12/Linux
and CI-specific invocation/output; Windows 3.10 cannot satisfy that gate.
The checker was not weakened or patched. JUnit zero-skip, corpus label/identity/
scores, JSON/Markdown match and demo canary checks were separately verified;
local source and explicit-browser corpus hashes also match. No hosted CI result
or complete Linux acceptance is claimed.

The JSX 607-test repeat and required browser selection started from the initial
source while the HTTP patch was being reviewed. Their runtime/test files did
not change. The final source identity and source/fixture hashes connect the
runs; `result.json` distinguishes the run scopes. Package acceptance is repeated
after the source commit is made. This is local acceptance; hosted CI is separate.
The initial [package result](package-result.json) is preserved separately from
the post-pin package repeat; artifact archive hashes differ between builds.

## HTTP closure

[Root cause and rejected first integration](../2026-11-03-http-bench-completion/README.md).
Changed implementation/fixtures: `bench/run.py`, `bench/mock_target.py`;
regressions: `bench/test_bench.py`, `bench/test_http_completion.py`.
Connection-refused and actual HTTP 404 controls cannot receive completion or
FN credit. Positives and completed encoded-negative observations remain
scoreable. The first 111-pass/2-failure integration is not accepted evidence.
The final frozen HTTP/runner suite passed 115 tests, with no errors or skips.

## Presentation package and limits

- [One-page technical summary and before/after table](../../docs/R8-M1-CASE-STUDY.md).
- [2:40 live demo talk track](../../docs/R8-M1-DEMO.md), with verified runnable
  [terminal comparison](demo.py). This is a live demo script, not a video.
- [Offline package gate](package_check.py) checks a new wheel/sdist, fresh
  isolated install, eleven module identities, nine existing CLI checks and all
  nineteen frozen JSX cases. Local metadata remains 0.2.2; this wheel differs
  from the previously published PyPI artifact and was not published.

JSX results are review-candidate coverage, never missed/found XSS or general
accuracy. The 19-case repeat is not a new unseen evaluation. The 233/47-file
owned-source comparison is historical and was not rerun here; its known vendor
skip remains. Local browser execution is a separate lab observation and does
not validate the JSX candidates as vulnerabilities. No user-time saving was
measured. A05 remains partial/frozen pending a suitable authorized runtime;
K04 historical retest still needs matching artifacts. No new engine scope was
selected under R8: expansion requires a new measured actual-source gap.

Native specialists implemented bounded HTTP, presentation and package work
under exclusive ownership. The coordinator reviewed the changes and oracles,
returned the stored fixture failure, ran integration and owns Git delivery.
Observed native invocation does not independently prove TOML inheritance.
