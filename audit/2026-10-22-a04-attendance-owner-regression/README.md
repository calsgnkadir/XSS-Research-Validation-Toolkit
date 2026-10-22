# A04 attendance ownership regression — 22 October 2026

## Scope and ownership

This adds one persistent service-level negative oracle for the bounded A04
Kadrom authorization work. The user authorized changes to their Kadrom code;
the task was performed against the local checkout pinned at
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. Only
`.dxa/a04-kadrom-source/hotelapp/src/test/java/com/hotelapp/service/CheckInServiceTest.java`
was changed by this task. The concurrent BCrypt work modified separate auth
files in the same checkout; those files are outside this task's ownership.

The added test, `attendance_denies_another_business_owner_before_reading_roster_rows`
at `CheckInServiceTest.java:187-197`, sets up a listing owned by ID 7 and calls
the attendance service with owner ID 999. Expected behavior is a deliberate
`UnauthorizedException`; Mockito verifies that `RosterService.collectRows`
is never called. The test exercises the owner-ID boundary before attendance
data is collected. It is a service unit test: it does not create authenticated
HTTP principals or prove role assignment, controller wiring, or database
behavior.

At the pinned source, `CheckInController.java:47-55` exposes the
`BUSINESS_OWNER` attendance GET and passes the authenticated principal ID to
the service. `CheckInService.java:215-218,287-294` checks listing ownership
before calling `collectRows`. These source facts explain the test's oracle;
source inspection alone is not runtime evidence.

## Verification

Command, run from `hotelapp/`:

```powershell
& 'C:\Users\user\.m2\wrapper\dists\apache-maven-3.9.16\56ba1f9f\bin\mvn.cmd' '-Dmaven.repo.local=C:/Users/user/.m2/repository' -o -Dtest=CheckInServiceTest test
```

Environment: Windows, Java 17 compiler target, Maven 3.9.16, offline local
dependency cache. Exit code **0**. `CheckInServiceTest`: **15 run, 0 failures,
0 errors, 0 skipped**. Main and test sources compiled; this was one selected
test class, not the whole Kadrom suite. Maven's wrapper script reports Maven
is not installed, and the first direct invocation selected inaccessible
`C:\.m2`; the escalated invocation with the existing user cache completed.

This test made no HTTP request and started no service or Docker resource.
It is persistent source regression coverage, not a new endpoint retest.

After the BCrypt dependency upgrade to Boot 4.1.1 / Security 7.1.1, the same
`CheckInServiceTest` was included in the final combined auth/A04 selector. That
run passed **51 tests total, including all 15 `CheckInServiceTest` tests**;
all 91 target test sources compiled. Exact command and result are in
[the final remediation validation](../2026-10-22-a05-bcrypt-remediation/README.md).

## Existing runtime evidence and disposition

The separate [owner-read runtime record](../2026-10-22-a04-owner-read-runtime/README.md)
contains the real local HTTP comparison for two synthetic `BUSINESS_OWNER`
accounts on `GET /api/business/listings/19/attendance` and
`GET /api/business/listings/19/roster`: the owner received 200 on both routes,
and the other owner received 403 on both. Attendance was empty; roster response
was not opened. This task did not repeat those requests or start Docker.

Together with the earlier bounded list and work-session records, A04 remains
accepted only for the selected routes and fixtures already named in those
records. The new unit test strengthens the attendance denial regression but
does not expand the tested product surface, establish product-wide safety, or
close R7/A05. No multipart test was run.

## Acceptance cross-check and remaining boundary

The current A04 row in `ROADMAP.md` defines bounded acceptance as the selected
local demo list/role checks, three candidate work-session GETs, and two
business-owner ID GETs (`attendance` and `roster`) using two accounts. The
linked runtime records contain those route/account comparisons and positive
controls; the attendance positive fixture was empty, as documented in the
owner-read audit. Therefore no additional A04 authorization oracle required by
that bounded roadmap criterion was missing at this follow-up. The persistent
unit test is complementary: it verifies that the service rejects a foreign
owner before collecting roster rows, but it is not a substitute for the
two-account HTTP observation.

The remaining boundary is explicit: this evidence does not cover normal
clock-in, mutation routes, every ID-addressed resource, every role, deployed
configuration, supported product releases, or product-wide authorization
safety. Those are outside the selected A04 acceptance recorded in the roadmap;
source/test inventory leads in the separate scope-completeness audit are not
runtime findings. The test class was not rerun for this documentation-only
follow-up, and no new pass/failure/timeout/skip is claimed. The previously
recorded focused results remain 15/15 for `CheckInServiceTest` and 51/51 for
the combined auth/A04 selector.

## Coordinator full-suite update — 22 October 2026

The coordinator later ran the final Kadrom full Maven suite after the Boot 4
dependency updates: **665 tests, 0 failures, 0 errors, 0 skipped**. All 15
`CheckInServiceTest` tests passed, including this owner-denial/no-roster-read
regression. The suite uses the in-memory H2 test profile; the full command,
H2 test-version workaround and limits are recorded in
[VALIDATION](../../VALIDATION.md). This does not repeat or widen the selected
two-owner HTTP route checks described above.
