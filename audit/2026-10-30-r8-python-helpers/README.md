# R8 — bounded same-file Python helper returns, 30 October 2026

Base: `ea76fa5` (accepted Leaflet source). The starting main branch was clean
and matched origin/main after fetch. This source change is unreleased;
published PyPI 0.2.2 artifacts are unchanged.

## Root cause and scope

The earlier Python AST pilot inspected argument names but did not resolve
same-file return expressions. A zero-argument helper returning a recognized
request source therefore lost provenance at its caller. Conversely, a helper
returning an HTML encoder expression or a fixed literal inherited irrelevant
argument provenance at an HTML-body sink.

The extension substitutes eligible unique top-level synchronous single-return
helpers into later exact positional calls. It keeps raw and HTML-body views
separate, preserves raw residuals, and declines mitigation with conflicting
bindings or explicit encoder mutations. Helper-generated script/style/attribute
contexts use raw provenance. Starred unpacking and walrus expressions retain
the original AST fallback when a source segment is not standalone eval syntax.
The existing candidate/unreviewed evidence contract is unchanged.

The code remains a bounded source approximation: no general call graph,
runtime typing, branch-return inference, alias resolution, closure/method
resolution or sanitizer validation. Unsupported source-return helper chains
and branch-bearing helpers can still be missed. Full syntax and size limits
are in [STATIC-SCOPE.md](../../tools/dom-xss-analyzer/STATIC-SCOPE.md).

## Validation

- Windows / Python 3.10.11; 68 independent final helper regressions against the
  exact base: **9 failed / 59 passed**, zero errors/skips. The five missed
  HIGH source signals and four excess HIGH signals pass on final source:
  **68 passed**, zero failures/errors/skips.
- Coordinator twelve-file combined acceptance: **498 passed**, zero failures,
  errors or skips. The local CI self-scan exited 0 with static candidates.
- Scanner SHA-256:
  `c526399c1927ae529be35ad4a398b88ba4fbe8637f45952a5ac5ac4863d1c605`.

Acceptance is recorded in [result.json](result.json), binding the selected
test results to scanner/test SHA-256 hashes. The independent exact-base test
run and coordinator integration use the same final test file. Private JUnit
and the exact base module remain under ignored `.dxa/r8-helpers-20261030/`;
public summaries omit local hostnames and temporary paths.

Run the coordinator source acceptance from repository root:

```powershell
py -3.10 audit/2026-10-30-r8-python-helpers/run_validation.py
```

The runner executes twelve selected test files, verifies unchanged hashes
during the test run, runs the labeled measurement, and executes the local CI
self-scan script. Its baseline input is the independent QA historical summary
in [baseline.json](baseline.json); that baseline is not reexecuted by this
runner. The exact-base XML and loader remain private. No full
application/browser suite is claimed. Python initially
failed in the sandbox with WindowsApps access denied; approved escalated
local synthetic/test commands provided the actual runs.

## Labeled source-signal measurement

[measure.py](measure.py) defines twelve synthetic examples with fixed labels
for HIGH source-provenance evidence, not vulnerability labels.
[Baseline](measurement-baseline.json): TP=5, FP=3, FN=4, TN=0.
[Final](measurement-final.json): TP=7, FP=0, FN=2, TN=3.
Both remaining misses are explicitly unsupported helper chains and branched
returns. In the ten supported/control examples the two source-return misses
and three excess HIGH signals are corrected. Medium sink candidates remain;
the FP label means an excess HIGH source signal, not a false vulnerability
report. No general precision/recall percentage is inferred from this corpus.

## Actual ownership and review

Three native specialist invocations used exclusive file ownership:

| Role / task | Owned contribution |
|---|---|
| `scanner_engine_specialist` / `r8_helper_engine` | `dxa.py` implementation |
| `qa_security_lab_specialist` / `r8_helper_qa` | Independent `test_static_python_helpers.py`, exact-base and final QA runs |
| `xss_security_researcher` / `r8_helper_security` | Scope/limits documentation and independent synthetic context/mutation probes |
| Coordinator | Code/oracle review, labeled corpus, combined acceptance, progress records and Git delivery |

The coordinator returned expanded-context, binding/mutation and valid-AST
fallback counterexamples to the relevant owners before final integration.
Native invocation does not independently prove TOML loading or runtime
permission inheritance. No persistent automation was created.
All three specialist tasks are complete; no background work remains active.

Only synthetic local source was analyzed in this delivery. Owner applications,
HTTP targets and browsers were not run; previous owned-project counts and
Leaflet DOM results were not rerun here. No execution, application safety,
confirmed XSS or new CVE is established. Hosted CI is separate from these local
results and is not claimed in this acceptance package.
