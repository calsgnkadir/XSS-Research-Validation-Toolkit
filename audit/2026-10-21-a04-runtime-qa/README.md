# A04 same-role runtime evidence QA — 21 October 2026

## Scope and method

Read-only comparison of the recorded six GET observations in
`../2026-10-21-a04-same-role-runtime/README.md` against the pinned Kadrom
checkout `.dxa/a04-kadrom-source`, identified there as commit
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. I did not query Docker, send HTTP,
run tests, contact external services, or change the product source. The source
and runtime outcomes below are different evidence types: this review can check
that the recorded outcomes are consistent with source, but it cannot reproduce
or independently authenticate the runtime requests.

## Route and ownership mapping

The controller is class-protected by `@PreAuthorize("hasRole('CANDIDATE')")`
(`hotelapp/src/main/java/com/hotelapp/controller/WorkSessionController.java:30`).
Each of the three GETs passes the authenticated principal's user ID to
`WorkSessionService`:

| Recorded request pair | Source behavior | Relation to recorded observations |
|---|---|---|
| `GET /api/candidate/work-sessions/23` (`WorkSessionController.java:86-90`) | `listForApplication` fetches rows by application ID, then keeps only rows whose application's candidate ID equals the principal ID (`WorkSessionService.java:144-150`). | For the one recorded row on application 23, candidate 1's 200 with one DTO and candidate 2's 200 with an empty list are consistent with the filter. The query can still return an empty list for an application with no rows; the foreign-row case is the meaningful negative control here. |
| `GET /api/candidate/work-sessions/23/active` (`WorkSessionController.java:56-63`) | `getActiveSession` fetches an open row by application ID and filters it by candidate ID (`WorkSessionService.java:135-142`). The controller maps a DTO to 200 and null to 204. | Candidate 1's 200 and candidate 2's 204 are consistent with one open row belonging to candidate 1 and the service ownership filter. |
| `GET /api/candidate/work-sessions/active-batch?ids=23,30` (`WorkSessionController.java:70-84`) | The handler loops over submitted IDs, calls the same `getActiveSession` filter, and adds only non-null DTOs to its map. | Candidate 1's response containing key 23 is consistent with the fixture. Candidate 2's empty object is consistent with the foreign row at 23 being filtered and there being no active row at 30. It does not demonstrate denial on a second foreign-owned active row. |

The repository methods are application-ID based (`hotelapp/src/main/java/com/hotelapp/repository/WorkSessionRepository.java:11-19`);
the application-to-candidate ownership check occurs in the service stream
filters, rather than in those repository method names. The positive session
was inserted directly into the fresh disposable database for application 23,
according to the runtime audit (`../2026-10-21-a04-same-role-runtime/README.md:34-38`).
The demo seeder creates applications, not work-session rows
(`hotelapp/src/main/java/com/hotelapp/config/DemoSeeder.java:250-304`), so this
direct fixture is consistent with the recorded setup.

## Acceptance and caveats

**Source-to-observation consistency: supported.** The implementation has an
explicit same-role owner filter on both the list and active-session service
paths, and the batch endpoint delegates to the latter. The six reported status
and body summaries are consistent with that source and the stated single-row
fixture. The bounded claim that these three GET routes returned candidate 1's
synthetic session to candidate 1 and did not return that row to candidate 2 is
reasonable if the runtime audit's observations are accepted as the operator's
run record.

**Independent runtime verification: unavailable from retained artifacts.** The
runtime audit says access tokens and all response bodies remained in memory and
were not recorded (`../2026-10-21-a04-same-role-runtime/README.md:39-45`). It
contains a six-row result summary, but no sanitized per-request assertion
transcript, response hashes, or tool output. This QA therefore did not verify
that the six requests were actually sent or that their reported statuses/bodies
were observed. Retaining a sanitized assertion record (route, account alias,
status, DTO count/application ID or map keys, and pass/fail; no token, email, or
raw body) would make the runtime claim independently auditable without retaining
secrets.

The work-session row was created directly in MySQL, not through the application's
clock-in flow. The normal flow performs application ownership/status checks,
business-coordinate and GPS-fence checks, open-session checks, and persistence
(`hotelapp/src/main/java/com/hotelapp/service/WorkSessionService.java:49-101`).
Those creation controls, clock-out, other roles, other records, and other routes
are outside this GET read-boundary check. The batch negative for candidate 2 is
also bounded by the fact that only application 23 had the described synthetic
session; application 30 had no active positive-control row.

### R7 / A04 disposition

This QA supports the three-route **bounded same-role GET comparison as a
coordinator-recorded runtime result corroborated by source**, with the audit
retention caveat above. It does not independently reproduce runtime behavior or
justify a general security conclusion. No vulnerability candidate was
confirmed by this review. No product suite, browser test, or CI result was
checked or run here. A04/R7 status remains subject to the coordinator's
acceptance criteria and the separate open A05 known-record research.
