# R7 / A04 Kadrom same-role runtime check — 21 October 2026

## Scope and preservation

The user's selected scope is the user's Kadrom product in a local lab, with a
two-account authorization-boundary comparison. The tested source remains
pinned to `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. Only synthetic seeded
candidate accounts were used. No hosted Kadrom endpoint, third-party service,
disclosure channel, or product outside this local Docker project was contacted.

The previously stopped project `a04-kadrom-20261021` and its
`a04-kadrom-20261021_mysql_data` volume were not started or modified. A new
project, `a04-kadrom-disposable-20261021`, used a new named volume
`a04-kadrom-disposable-20261021_mysql_data` and internal network
`a04-kadrom-disposable-20261021_internal`. Effective configuration and runtime
inspection confirmed `internal=true`, no host-published ports on backend or
MySQL, and the new volume mounted only at MySQL `/var/lib/mysql`. Both services
were healthy before the checks. Afterward, only the new backend and MySQL
containers were stopped. The new synthetic volume remains; no `down -v`, volume
deletion, or cleanup was performed.

The backend image was built from the pinned checkout as
`sha256:ae1792d83385fdda6bf27f122a712d83dcc00926a65be23bb68bd9fecd3bf5e4`;
the Dockerfile's Maven packaging step uses `-DskipTests`. No product test suite
was run. A temporary `curlimages/curl:8.10.1` helper (registry digest
`sha256:d9b4541e214bcd85196d6e92e2753ac6d0ea699f0af5741f8c6cccbfcf00ef4b`)
joined only the internal network and was invoked with `--rm`.

## Synthetic positive control

The fresh DemoSeeder supplied two candidate accounts and application records.
A read-only MySQL query mapped candidate 1 to application ID `23` and candidate
2 to application ID `30`; emails and credentials are omitted. The demo seed
contains no work-session row, so a synthetic session was inserted directly into
the new disposable database for application `23`, with a null shift-slot ID and
synthetic location values. This fixture preparation is a database mutation,
but it affected only the new isolated test volume. It was not created through
the product's clock-in workflow; the work-session GET behavior is tested against
the resulting row, not the validity of the clock-in workflow.

Two login POSTs were made with the synthetic demo accounts. Access tokens and
all response bodies remained in memory and were not recorded. After login,
only the following six GET requests were sent through the temporary helper to
`backend:8080` on the internal Docker network:

| Check | Expected observation | Observed |
|---|---|---|
| Candidate 1 `GET /api/candidate/work-sessions/23` | Own session DTO returned | HTTP 200; one DTO associated with application 23 |
| Candidate 2, same GET for application 23 | No candidate 1 session disclosed | HTTP 200; empty list |
| Candidate 1 `GET /api/candidate/work-sessions/23/active` | Own active session returned | HTTP 200; DTO associated with application 23 |
| Candidate 2, same active GET for application 23 | No candidate 1 session disclosed | HTTP 204; no content |
| Candidate 1 `GET /api/candidate/work-sessions/active-batch?ids=23,30` | Own active session included | HTTP 200; key 23 included |
| Candidate 2, same batch GET | Candidate 1 session omitted | HTTP 200; empty object |

All six bounded response oracles matched. This is runtime evidence that, for
these three GET routes in this synthetic local run, candidate 2 did not receive
candidate 1's work-session data while candidate 1 could retrieve the own
positive-control record. It is not evidence about other records, roles, routes,
mutations, deployment configurations, product versions, or general security.
No vulnerability candidate was observed in these checks.

## Result and limits

A04's same-role GET comparison is now completed for the three listed routes in
the pinned local source. The earlier list/role checks remain separately scoped
to their tested routes. A04 does not establish a supported product release or
test the normal GPS clock-in flow because the demo seed has no work-session
record and no business coordinates. A05's known-record research remains
partial/inconclusive; therefore R7 remains open. No test-suite or browser run
is claimed.
