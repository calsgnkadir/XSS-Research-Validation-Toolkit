# R4 local acceptance resume

The current source is the user-selected OneDrive workspace. It has no Git
metadata. Native `scanner_engine_specialist` task `/root/r4_local_acceptance`
owns the two comparison acceptance files and this evidence directory.
The old `C:/xss/xss-github` tree was read only; no commit, push, deletion or
background service was performed. Normal shell startup failed with
`helper_unknown_error: setup refresh had errors`; necessary commands used the
system approval path and then ran successfully. File edits and tests are actual
runtime results, not inferred from agent configuration.

## Preserved import

Before import, both OneDrive acceptance source/test files matched the text of
old Git HEAD `df967d506e8c37033ed6aa2c2e367a7aa0ec20dc`. Consequently no divergent
OneDrive edits were overwritten. `transfer.json` records original and imported
SHA-256 values; the two `*.import.patch` files record the exact incoming diff.
The comparator source already matched between roots and was left unchanged.

`imported-run-02` contains 25 byte-for-byte verified historical files: the
manifest and its 24 bound scanner artifacts. This is a copied prior run, not
a new scanner execution. Its new test path is workspace-relative. The prior
98-test claim is not reused as a new result.

## Reproduced defects and fixes

The incoming v3 implementation inherited timeout equality and per-row timeout
checks only for schema v2. Two mutations (common timeout drift and row timeout
drift) incorrectly passed. Both checks now apply to v2 and v3
(`bench/r4_comparison_acceptance.py:233`, `:269`).

The incoming credential-pattern check covered rows and bound artifacts, but
not top-level manifest metadata. A synthetic cookie in runtime metadata passed;
the v3 whole-document check now rejects it (`:193`). This is a check for known
fixture credential patterns, not a general secret detection guarantee.

A cookie option without a following argument raised IndexError. The new bound
check produces the gate's normal ValueError rejection (`:309`).

`before.xml` records 5 failures / 97 passes: four new counterexamples above,
plus the old run-01 regression failing earlier at an artifact hash mismatch in
this workspace. Historical run-01 bytes were preserved; the missing-trace test
now removes the trace from the hash-verified run-02 manifest and tests that
specific boundary without relying on the damaged historical artifact.

## Validation

Commands were run from the OneDrive project root with Python 3.10 and the
explicit installed Chrome path:

```powershell
$env:DXA_REQUIRE_BROWSER='1'
$env:DXA_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
py -3.10 -m pytest bench/test_r4_comparison_acceptance.py bench/test_bench.py bench/test_proof_adapter.py bench/test_ci_acceptance.py bench/test_r4_compare_local.py bench/test_r4_scanner_sessions.py bench/test_r4_comparison_fixture.py bench/test_r4_cid_oracle.py -q -p no:cacheprovider --tb=short --junitxml=audit/r4-local-acceptance-resume/acceptance.xml
py -3.10 bench/r4_comparison_acceptance.py audit/r4-local-acceptance-resume/imported-run-02/comparison.json --artifacts audit/r4-local-acceptance-resume/imported-run-02
```

The second command exited 0: selected/completed 8/8; error/timeout/incomplete/
skipped 0; artifact/session/trace checks true; equal client timeouts true;
candidate-only true; ranking false. These are present-day validation results
for historical scanner artifacts, not fresh scanner or browser proof results.
`acceptance.json` records the final JUnit totals, runtime and source hashes.
No hosted CI was run or claimed by this task.

## R4 criterion matrix

| Existing ROADMAP criterion | Evidence in the refreshed test command | Disposition |
|---|---|---|
| Identity matching, expected 3 / correct 1 gives TP1 FN2 | `bench/test_bench.py:61` checks three identities, duplicate correct observation and wrong sink: TP1 FP1 FN2. `bench/test_proof_adapter.py:48` checks runner invokes identity scorer. | Local acceptance supported; candidate comparator remains separate. |
| Crash/timeout/skip not success or TN; denominator explicit | `bench/test_bench.py:56`, `:80`, `:101`; `bench/test_proof_adapter.py:92` checks all 17 rows unscored and strict failure for incomplete states. | Local acceptance supported. |
| JSON-only / resource callback not execution TP | `bench/test_bench.py:69` excludes reflection and callback; proof adapter and CI callback negatives check completed observation and actual callback evidence. Existing corpus contains JSON and callback negatives. | Local acceptance supported; no raw reflection promoted to execution. |
| Negative FP / required positive FN fail CI gate | `bench/test_ci_acceptance.py:173` empty-proof positive and other correlation mutations return 1; `:190` negative execution fails despite zero claimed total. `bench/test_proof_adapter.py:62` checks completed positive misses yield FN8 and strict failure. | Local gate implementation acceptance supported; historical remote evidence remains separately recorded in VALIDATION. |
| Required browser CI, application lifecycle, CI artifacts | Prior accepted records remain in ROADMAP/VALIDATION; this task changes none of those components. | Historical acceptance preserved, not rerun as remote/Docker evidence. |
| Comparable scanner scope/auth/budget plus human triage | Imported run-02 passes candidate artifact/session/request accounting gate; scanner payload CID/browser execution correlation remains inconclusive. | Human triage and broader comparison deferred by current user direction; no ranking or overall comparison acceptance. |

No external target was contacted. Browser tests use disposable loopback fixtures.
The deliverable supports closure of the four local measurement criteria after
coordinator review. It does not support a winner, scanner accuracy, confirmed
vulnerability, or overall completion of the deferred comparison criterion.

## Final review after Git metadata restoration

Coordinator integration on the final R4 source used the eight-module required
Chrome command shown above. First run ended with **371 passed, 1 failed**:
the loopback fixture request in `test_rate_wait_cannot_forward_after_wall_deadline`
raised Windows `ConnectionAbortedError [WinError 10053]`. The same test passed
alone (1/1). The repeated full command then passed **372/372** in 51.68
seconds, with zero failure/error/skip. Both runs are recorded; the first is
not treated as a successful gate. This is a local fixture request result,
not scanner execution or a hosted CI result.

The coordinator restored Git metadata in this same workspace. The review base
is now locally verifiable HEAD `df967d506e8c37033ed6aa2c2e367a7aa0ec20dc`;
the earlier no-Git statement above describes the initial import stage only.

Three new counterexamples reproduced two additional v3 defects:

- The credential regex skipped values starting with `<`, accepting unknown
  angle-wrapped values and an allowed marker followed by a suffix. It now reads
  the entire value and permits only an exact known marker. The positive marker
  control still passes. This remains a fixture-pattern check, not universal
  credential detection.
- Canonical Dalfox `findings` was enforced for v2 but not v3, permitting the
  legacy `data` alias to replace it after rehashing the artifact. Both modern
  schemas now require the canonical field, matching the current producer.

`review-before.xml`: 3 failed, 1 passed (102 deselected), before the fixes.
`review-acceptance.xml`: **132 passed, 0 failure/error/skip**, after the fixes:

```powershell
py -3.10 -m pytest bench/test_r4_comparison_acceptance.py bench/test_r4_compare_local.py bench/test_r4_scanner_sessions.py -q -p no:cacheprovider --tb=short --junitxml=audit/r4-local-acceptance-resume/review-acceptance.xml
```

These are focused offline/loopback tests; no new browser/scanner comparison or
hosted CI run. The previous 368-test integration refers to the preceding source
revision. `review-acceptance.json` binds this focused result to final source
hashes and base commit; counts must not be added together.

CI review: `.github/workflows/ci.yml:47` already runs the comparison acceptance
module in the required main test job. The separate required browser job at
`:75` runs browser fixture/CID tests, not this browser-independent gate module.
No workflow edit is needed to execute the new gate regressions on the next CI.

Delivery recommendation: include both changed bench files and this audit
directory, including the 25 imported test-fixture files (79,527 bytes). Tests
depend on those files; omitting them would break fresh-checkout CI. They contain
historical sanitized fixture results, not credentials or fresh execution claims.
Seventeen imported files have CRLF bytes bound by SHA-256; `core.autocrlf=true`
would otherwise corrupt those bindings on Linux checkout. Coordinator staged
byte checks also found conversion in five other local evidence files. The
audit-local `.gitattributes` rule therefore disables text conversion for this
evidence package only; product source files are unaffected.
The coordinator should verify staged/exported blobs against `transfer.json`.
No Git staging, commit or push was performed by this specialist.
