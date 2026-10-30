# R8 — measured receiver false positives fixed

Base `1bd74b0126ed1568bd53ae54c72f430cf70649dd`, Windows / Python 3.10.11.
The user authorized finishing the measured false-positive delivery before
strengthening XSS coverage. No target application code/data was changed.

## Root cause and behavior

The generic `.append()` rule confused native FormData uploads with jQuery HTML
insertion. The navigation regex confused `const location = useLocation()` with
browser navigation. Narrow per-match lexical checks now recognize the measured
non-sink shapes. Unknown receivers, constructor shadowing/mutation, aliases,
scope changes and unresolved syntax retain candidates. Real jQuery insertion
and real location writes/calls remain reported, including same-line controls.

The bounded helper is not a JS parser, general type resolution or security
proof. Receiver lookup is limited to 32 KiB before the match. Constructor
imports/dynamic effects and computed mutations remain analysis limitations.
An uncertain lexical suffix cannot supply new exclusion evidence.

## Independent evidence

- QA-owned black-box regressions: final baseline **23 failed / 20 passed**;
  failures expose the old behavior, not a successful scan.
- Final selected five-file suite: **146 passed, zero failure/error/skip**.
  Files: test_static_receiver_bindings.py, test_dxa.py, test_static_context.py,
  test_dxa_config.py and test_r8_sanitizer.py.
- Same-source static comparison: owned scope A **22 -> 12** candidates, exactly
  five FormData and five router declaration records removed, no new candidate.
  Scope B **129 -> 129**, unchanged. 233 and 47 source hashes respectively
  match the earlier inputs. Scope B retains one vendor-directory skip.
- These are static candidates, not vulnerability counts. No app/HTTP/browser
  execution, deployment security or CVE outcome is claimed. App-specific paths,
  raw results, source hashes and reports remain ignored/private.

[Machine acceptance and source hashes](result.json). Commands:

```text
py -3.10 .dxa/run_fp_regression.py --baseline
py -3.10 .dxa/run_fp_regression.py
.dxa/pypi-refresh-021/Scripts/python.exe -B .dxa/run_fp_project_comparison.py --accept-phase1
```

The first implementation passed 129 selected tests but removed no actual
project false positives; coordinator rejected it. Realistic QA cases exposed
module-prefix/ASI problems. A second iteration removed nine records but failed
two scope negatives. Final acceptance preserves those negatives and removes
all ten reviewed false alarms. Private iteration records are retained; old
test counts are not presented as the final run.

Engine specialist owned dxa.py; QA specialist owned the regression file;
research specialist scoped the following coverage work without runtime edits.
Coordinator reviewed changes, returned defects, verified source comparisons
and accepted this milestone. No PyPI release is made: installed 0.2.1 remains
the published baseline. Hosted CI is separate from these local checks.

Next accepted work direction: bounded inline HTML message-source provenance,
using actual script elements and receiver/context negative controls. JSX URL,
Leaflet and Jinja context additions remain separate work.
