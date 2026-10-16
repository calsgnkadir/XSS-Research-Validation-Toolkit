# Final commit retest and P02/P03 review — 2026-10-17

Base/source commit: `3ef8499bc56827614602540d962eb4ab0ea9bdca`, which matched
`origin/main` before this documentation-only follow-up. Local tests ran on
Windows with Python 3.10.11 unless a browser is named below. This record
distinguishes local runs from hosted workflow outcomes; test counts are not
scanner accuracy measurements.

## P02/P03 outcome

The root README now describes the project as an experimental Python CLI and
states its bounded evidence model and limits. Historical payload corpus counts
are identified as generated input counts, not exploit or execution counts.
`writeups/README.md` groups entries 06–10 as a single tool-development series
and explains that repeated historical outcome claims are not independent
measurements. The history files remain intact. Relative-link review and
`git diff --check` passed. These are editorial changes; no runtime behavior
changed.

## Local final-source test matrix

| Check | Result | Scope |
|---|---:|---|
| `py -3.10 -m pytest tools/dom-xss-analyzer -q -p no:cacheprovider --tb=short` | 789 passed, 38 skipped, 0 failed | Full analyzer package |
| Selected benchmark/CI acceptance tests (10 files) | 520 passed, 0 failed | Runner, proof adapter, CI self-scan/acceptance, Bludit, R4 compare/session and installed CLI gates |
| `py -3.10 bench/ci_self_scan.py` | Passed | Static self-scan candidate workflow; not execution proof |
| Strict three-target mock smoke | TP=2, FP=0, FN=0 | Controlled mock targets |
| Required R3/R4 Chrome acceptance selection (11 files) | 218 passed, 0 failed | Windows, Python 3.10.11, Chrome 155.0.8059.82, Playwright 1.63.0 |
| Strict proof suite | TP=8, FP=0, FN=0 | Controlled proof fixtures |
| Auth failure controls | TP=1, FP=0, FN=0 | Mock reflected target |
| `dxaprove --demo` | `execution-observed` | Local loopback demo only |
| K01 fixture/gate tests | 22 passed, 0 failed | Local K01 fixture |
| K01 fresh local profile | 5/5 controls; 5/5 fixture ports closed; artifact gate passed | Local profile, Python 3.10.11 |
| `test_dxadom.py` with required Chrome | 80 passed, 0 skipped, 0 failed | Full DOM browser test package |

The strict proof run was repeated with the required `.dxa/r4-proof.md` basename;
the run itself passed with TP=8, FP=0, FN=0. The local
`bench/check_ci_acceptance.py` checker did not accept the Windows/Python 3.10
artifacts because its provenance contract requires Linux/Python 3.12. This is
an environment-provenance limitation, not a test failure or passing artifact
gate. No local artifact acceptance is claimed from that checker.

## Hosted workflows

For `3ef8499bc56827614602540d962eb4ab0ea9bdca`, general CI run
[38982247229](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38982247229)
passed all three jobs; K01 Linux run
[38982247201](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38982247201)
passed. These are hosted workflow/job results. Their artifacts were not
downloaded and independently inspected in this retest.

## Limits

The local Windows matrix tests the final source commit, not the later
documentation-only P02/P03 changes. No external target was tested. Controlled
mock, fixture, browser, or corpus results do not establish broad detection
accuracy, a vulnerability finding, a new CVE, or superiority over other tools.
