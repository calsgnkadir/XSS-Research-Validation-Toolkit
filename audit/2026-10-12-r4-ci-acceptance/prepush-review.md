# R4 independent pre-delivery review — 12 October 2026

Reviewer: native QA `/root/r4_acceptance_qa`. This follow-up review owns only
this file. No application changes, Git writes, move or new test run occurred.
The latest user authorization permits the coordinator to commit/push after
review; it does not authorize specialist Git operations.

## Decision

PASS for the narrow local R4/R9 artifact-gate delivery. No reproduced code or
oracle blocker found. This is not general R4 completion or remote Linux
artifact acceptance.

- `bench/check_ci_acceptance.py:32`: JUnit case outcomes and declared counters
  must agree with zero failures/errors/skips; four required modules and unique
  test identities are checked. No fixed historical test total is imposed.
- `bench/check_ci_acceptance.py:64`: exact nine independent fixture labels,
  completed observations, nested proof correlation, row scores and totals are
  checked. Missing, timeout or skipped cases cannot become true negatives.
  Production adapter reuse is explicit; independent synthetic subprocess
  tests supply the adverse oracle rather than importing gate constants.
- `bench/check_ci_acceptance.py:106`: demo execution content is required, so an
  inconclusive demo with CLI exit 0 is insufficient. This proves a correlated
  fixture canary, not vulnerability triage or artifact provenance.
- `bench/test_ci_acceptance.py:142`, `:173`, `:199`, `:205`, `:221`, `:226`:
  correlation, malformed structures, nonfinite time, duplicate cases, cached
  finding disagreement and boolean-count counterexamples remain present.
- `.github/workflows/ci.yml:68`: the gate is required in `r3-proof` after the
  actual producers. The separate optional browser job at `:84` still permits
  failure and does not become accepted browser coverage through this change.

## Evidence checked now

The acceptance manifest's source hashes all match current files; its recorded
integration source-stability flag is true and both command exits are zero.
Saved JUnit content shows browser 94 tests and integration 185 tests, each
with zero failure/error/skip. These are inspected records, not new reruns.
The earlier independent QA run had 72 passing tests and is included in the
185-test integration result; counts must not be added.

`git diff --check` succeeded. All current files in this evidence package were
checked for common token/Bearer/credential patterns, local user-profile paths
and JUnit hostname metadata, with no matches. Files range from approximately
1–27 KB. This scoped check is not a universal secret-detection guarantee.

## Limits and coordinator action

The recorded remote artifact HTTP 401 remains an access blocker. Successful
historical job metadata does not establish artifact content or zero skips.
After an authorized push, inspect the new remote required-gate result and,
when authenticated access is available, its JUnit/corpus/demo artifacts;
record them separately from local Windows evidence. General R4 real-product
bootstrap/login/port-discovery remains open.

Before delivery, update current STATUS/next-step statements to the latest
user Git authorization and actual delivery state. Earlier no-commit/no-push
activity may remain as clearly historical evidence. The coordinator was
notified; no documentation outside this owned review was changed by QA.
