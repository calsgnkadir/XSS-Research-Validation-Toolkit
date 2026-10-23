# A04/A05 Kadrom current-source regressions

**Date:** 2026-10-23  
**Target:** user-owned `calsgnkadir/hotel-platform`, `main`  
**Roadmap:** A04, A05  
**Base:** `b374095344f7b871bbadc4eef571760fd380f9ab`  
**Delivery:** `0ea07ed77c9d2edfc8a3e4394d3ab3700ca69de0`

## Delegated implementation

Three specialists worked in parallel with disjoint ownership:

| Work | Role | Files |
|---|---|---|
| A05 invalid Sort error boundary | XSS security researcher | `GlobalExceptionHandler.java`, `GlobalExceptionHandlerSortTest.java` |
| A04 same-role session ownership regression | QA/security lab specialist | `WorkSessionReadOwnershipHttpTest.java` |
| A05/R7 current advisory disposition | XSS security researcher | This toolkit's `audit/2026-10-23-a05-current-source-disposition/README.md` |

Coordinator reviewed all changes and test boundaries. No specialist performed
independent Git operations.

## Change and observed behavior

`GlobalExceptionHandler` now maps only an
`InvalidDataAccessApiUsageException` that contains Hibernate
`UnknownPathException` and occurs on a request with a `sort` parameter to a
generic HTTP 400 response. Other data-access API misuse remains HTTP 500. Its
standalone MockMvc controls check invalid property → 400 without disclosing the
field, valid property → 200, and unrelated repository misuse → 500.

The A04 integration test creates only synthetic H2 records in a rollback-only
test transaction. It covers the three candidate work-session GET routes using
two same-role candidates: own active/history rows remain visible, while the
other candidate's session rows are absent. It does not exercise a deployed
configuration or other controllers.

The Sort change corrects an input-error response. It is not a fix or
reproduction of CVE-2026-41711; the current Spring Data version is outside the
published affected ranges. The advisory/source version reconciliation is in
the [current A05/R7 disposition](../2026-10-23-a05-current-source-disposition/README.md).

## Validation and delivery

On the exact base plus these three changes, Maven `verify` completed with **739
unit + 45 integration tests, 0 failures, 0 errors, 0 skipped; BUILD SUCCESS**.
The Sort controls passed 3/3 and the A04 ownership regression passed 1/1.
Full command, environment, hashes and log path are in
[VALIDATION.md](../../VALIDATION.md).

Commit `0ea07ed77c9d2edfc8a3e4394d3ab3700ca69de0` was pushed to `main`; a
subsequent fetch confirmed local HEAD equals `origin/main`. GitHub Actions run
[39928860888](https://github.com/calsgnkadir/hotel-platform/actions/runs/39928860888)
completed successfully on that exact SHA.

## Remaining boundary

The user's malformed multipart parser-error cleanup test remains outstanding;
it was not retried. A05 remains partial for this unverified runtime condition.
No external disclosure or CVE claim was made. A04's result is limited to the
three covered work-session GET routes and the test fixture.
