# R3–R6 acceptance reconciliation

Review completed 23 October 2026 Europe/Istanbul, continuing the 22 October
assignment. Native role: `qa_security_lab_specialist`, task
`/root/r3_r6_acceptance`. Source HEAD:
`132d360cc28c19ed4326a4de821aed93fcd00133`, `main`, toolkit origin verified;
initial worktree clean. Coordinator performed upstream fetch/comparison.
Specialist performed source, recorded evidence and hash review only: no new
test suite, browser run, Docker action, remote CI query, commit or push.

## Finding and correction

The user remembered correctly: **R3, R4, R5 and R6 are complete within the
main roadmap's accepted scope.** `ROADMAP.md:415`–`:418` and the detailed
acceptance sections agree. The current continuation text at the reviewed
`STATUS.md:39`–`:40` incorrectly calls R4 corpus/coverage the next unfinished
technical task. It contradicts both `ROADMAP.md:500` and the same STATUS
file's 16 October closure at `:510`–`:536`. This is a reproduced documentation
contradiction, not a newly reproduced scanner defect. Coordinator owns the
STATUS correction; this specialist did not edit shared planning documents.

| ID | Accepted result | Recorded evidence and remaining boundary |
|---|---|---|
| R3 | Complete, loopback authenticated browser proof pipeline | [7 October revalidation](../2026-10-07-r3-r4-revalidation/README.md): 681 tests passed with zero skips, including lexical eval preservation, cleanup/state restoration and JSON/HTML equivalence. ROADMAP `:480`–`:498` checks all criteria. Header observation and Linux CI moved to R4 and are checked at ROADMAP `:626`–`:627`. This is not product-wide XSS validation. |
| R4 | Complete, 16 October bounded technical measurement scope | [Final replay](../r4-proof-experiment-2026-10-16/README.md): final focused suite 57 passed, no failure/error/skip; 8 historical scanner rows, 6 exact candidate replays, 2 raw Dalfox payloads with raw dialog and clean escaped control; 4 inconclusive. [Recorded remote artifact acceptance](../2026-10-15-resumed-delivery/remote-r4-acceptance.json) binds commit `0261baa`, CI run `38706882024`, 179 tests/zero skips or errors and corpus v4 17/17 with TP=8/FP=0/FN=0 to downloaded artifact provenance. Fixture corpus metrics are separate from scanner comparison. Human triage, general accuracy and superiority were explicitly removed from mandatory closure; no new expansion is required to close R4. |
| R5/K01 | Complete, technical reproducibility | [16 October acceptance](../r5-final-acceptance-2026-10-16/README.md) and its [proof manifest](../r5-final-acceptance-2026-10-16/proof/acceptance.json): new Windows venv 5/5 controls and 5/5 closed ports, plus separately recorded historical Linux artifact acceptance. A second human run remains unfulfilled but optional under the accepted scope. This is a synthetic fixture with fix/retest, not a product CVE. |
| R6 | Complete, v0.1.0 GitHub Release including wheel | [21 October publication](../2026-10-21-r6-release/README.md): tag source `d7d1bd666ae4fe5643bf0574658d8d8a0f4411a0`, uploaded wheel digest matched, installed-wheel gate 7/7. Recorded tagged-source general CI `39650964831` and K01 Linux `39650964757` succeeded. PyPI was excluded by user scope; it is not an outstanding R6 requirement. |

All numbers above are archived observations, **not new runs in this review**.
The replay's rejected manifest/hash attempt and WebSocket timeout remain
unsuccessful attempts in the original audit; neither counts as a passed
control. Inconclusive candidates do not become negatives or vulnerabilities.

## Current source checks

- `bench/run.py:518` validates completion/evidence consistency; `:575`
  only scores matched identities with correlated execution evidence;
  `:590` makes errors, timeouts, skips, invalid and inconclusive outcomes fail
  strict acceptance. `:835`–`:844` retains selected/completed/error/timeout/skip
  coverage separately, and `:874`–`:880` states the denominator in Markdown.
- `bench/r4_comparison_acceptance.py:19` explicitly separates completed,
  error, timeout, incomplete and skipped. Its `validate_comparison` at `:177`
  does not infer TP/TN or rankings from completed candidate rows.
- `.github/workflows/ci.yml:62` defines the required `r3-proof` job, with
  browser-required environment, strict corpus and artifact gate. The separate
  optional DOM harness at `:99` is not the required proof job. Workflow source
  is configuration evidence; historical run results above are distinct.
- `cases/k01-stored-comment/test_repro_gate.py:66`, `:94` and `:181` cover
  incomplete proof, unclosed fixture ports and failed proof without acceptance.
  Tests were inspected, not rerun.
- `git diff d7d1bd666ae4fe5643bf0574658d8d8a0f4411a0 HEAD --stat --
  tools/dom-xss-analyzer bench cases .github/workflows pyproject.toml` produced
  no differences. Thus no post-release source change was found in these areas.
- Fresh SHA-256 comparison of all nine current packaged Python modules with
  `audit/2026-10-21-r6-current-source/release-installed-wheel-gate.json`
  matched **9/9**. This verifies source equality to the recorded package
  acceptance, not a new wheel installation or CI execution.

No unmet current R3–R6 criterion or narrowly necessary implementation change
was identified. No application/test files were changed. Further corpus growth
can be a separately chosen extension with explicit new criteria; it must not
silently reopen the already accepted R4 scope. Continue current A05/R7 work
and choose any later optional expansion from the main ROADMAP.
