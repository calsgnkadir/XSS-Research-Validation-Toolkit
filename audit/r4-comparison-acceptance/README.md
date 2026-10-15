# R4 independent candidate comparison acceptance — 15 October 2026

Native QA specialist implementation, based on `521efae`; ownership is limited
to `bench/r4_comparison_acceptance.py`, its test module, and this audit directory.
The engine specialist separately owns the live scanner harness and fixtures.

The gate independently checks declared corpus identities, reversed execution
order, all eight selected runs, outcome flags, exit/report consistency, budget
and HTTP request accounting, totals, command scope and candidate-only claims.
Errors, timeout, incomplete and skipped runs retain their selected denominator;
none becomes a true negative. This gate does not produce TP/FP/FN/TN or ranking.

Version 1 accepts historical structural evidence while reporting that artifacts
were not checked. Version 2 requires per-row identities, equal client timeouts
and hashes of stdout/stderr/report files under the supplied artifact root.
Report candidate counts are independently parsed from those bytes. Dalfox
incomplete/failed-request metadata and dxadyn error/skip events or skipped
submissions prevent complete candidate results. Both dxadyn and pinned Dalfox
3.2.4 use exit 1 for findings; an early assumption that Dalfox exit 1 meant an
error was corrected after the engine inspected its version-pinned source and
live output. The earlier engine run remains preserved as historical evidence.

## Local validation

Windows / Python 3.10, commands run from repository root:

```console
py -3.10 -m pytest bench/test_r4_comparison_acceptance.py -q -p no:cacheprovider --tb=short
```

**72 passed**, zero failures/errors/skips. Corruption regressions include
timeout promotion, omitted/duplicated rows, wrong totals, drifted identities
and CLI scope, mismatched budgets, candidate-to-execution promotion, malformed
nested objects, report byte/hash and candidate-count mismatch, traversal, and
incomplete scanner metadata and nonconforming Dalfox list/alias reports.
An initial test expected a different traversal
error wording; the unsafe path was rejected before and after its adjustment.

```console
py -3.10 bench/r4_comparison_acceptance.py audit/2026-10-15-r4-comparator-execution/run-02/comparison.json --artifacts audit/2026-10-15-r4-comparator-execution/run-02
```

Exit **0**: selected **8**, completed **8**, error **0**, timeout **0**,
incomplete **0**, skipped **0**, equal client timeouts true, artifacts verified
true, candidate-only true, ranking false. This is an independent check of the
engine's recorded local run, not another scanner run or remote CI acceptance.
Validated manifest SHA-256:
`ea01e804852ba80c67c15f4639c96a4486c3f11bd2f87b6fcc0b672302d7b693`.

## Limits and roadmap mapping

R4 accounting/provenance is strengthened. The broker cookie still does not
represent independently authenticated scanner accounts. Candidate reports are
not correlated scanner-generated CID execution proof; escaped reflection
candidates are not automatically XSS false positives. Human triage and overall
competitor-comparison acceptance remain open. Hashes bind supplied bytes, not
the authenticity or independent authorship of a run. Runtime source hashes are
format-checked, not compared against an arbitrary current checkout. No external
target was scanned; R5 independent human repetition remains deferred. No CI
result, commit or push was performed by this specialist.
