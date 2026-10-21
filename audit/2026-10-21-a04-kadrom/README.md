# R7 / A04 bounded local role-boundary review — 21 October 2026

## Scope and authorization

Following the user's scope selection, the coordinator chose the user's Kadrom
repository, `calsgnkadir/hotel-platform`, for a local-only check. It was the best
fit among the visible repositories because its README describes a local
Spring Boot stack, its demo seeder provides synthetic candidate and business
accounts, and the selected endpoints directly exercise the requested role
boundary. No live or hosted Kadrom service was contacted. No external report or
message was sent.

The reviewed source was pinned to `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`
(`main` at clone time). No release tag or supported-version claim was
established. This was a bounded check of application-list read endpoints for
one seeded `CANDIDATE` and one seeded `BUSINESS_OWNER` account.

## Source review

`ApplicationController.java` requires `CANDIDATE` for
`GET /api/candidate/applications` (line 45) and `BUSINESS_OWNER` for
`GET /api/business/applications` (line 91). The repository queries constrain
candidate rows by the authenticated candidate ID (line 192) and business rows
by the authenticated owner's ID (line 207) in
`ApplicationRepository.java`. These source paths guided the read-only runtime
checks. Source review alone was not treated as runtime proof.

## Local setup

- Compose project: `a04-kadrom-20261021`.
- Database volume: `a04-kadrom-20261021_mysql_data`, created empty and unique to
  this run; Docker Compose `down -v` was not used.
- Network: `a04-kadrom-20261021_internal` with `internal: true`.
- The backend image built locally as
  `sha256:375accc0ee4c63ee350deb4f8c285a8883d17152783022861cd862a9a6a5fb92`.
  Maven packaged the application with `-DskipTests`; tests were not run.
- The compose config specified a loopback-only host port, but the created
  container had no host port binding (`NetworkSettings.Ports` was empty). To
  keep the internal network isolated, the API checks ran with `curl` from inside
  the backend container against `127.0.0.1:8080`; there was no host-published
  port. The initial host-side connection attempt did not reach the API.
- The demo seeder reported 10 candidates, 6 businesses, 15 listings, and 65
  applications in this clean volume. Seeded accounts and records were synthetic.
- After the checks, only this Compose project's backend and MySQL containers
  were stopped. Docker reported exit code 137 for both containers; the unique
  demo volume still exists and was not deleted. No other container or volume
  was touched.

Docker image and Maven dependency downloads were setup traffic to their
registries. No product endpoint outside this local container was contacted.

## Runtime observations

Login responses were used only in memory. The saved summary excludes tokens,
cookies, passwords, emails, names, and response bodies. Requests after login
were GET-only and made no state changes.

| Check | Result |
|---|---|
| Candidate's own application list | HTTP 200; 7 rows; every returned candidate ID matched the authenticated account |
| Business owner's incoming application list | HTTP 200; 9 rows; every returned business-owner ID matched the authenticated account |
| Candidate token on business list | HTTP 403 |
| Business-owner token on candidate list | HTTP 403 |
| No token on candidate list | HTTP 401 |
| No token on business list | HTTP 401 |

These observations support the expected role gates and account-scoped list
filters for these endpoints in this seeded local run. They do not test whether
one candidate can access another candidate's object by ID, whether one business
owner can access another owner's individual object, mutation endpoints,
messages, profiles, or any other route. The two chosen accounts have different
roles; this is not a same-role IDOR test.

## Known-record check and outcome

The public GitHub issue/security-advisory page lookup was attempted, but the
browsing source returned cache misses for those pages; search results did not
identify an exact-repository advisory. This is inconclusive and is not evidence
that the project has no known issue or advisory. No CVE or vulnerability
attribution is made.

No candidate vulnerability was observed in the bounded role/list checks, so no
independent PoC was warranted. The outcome is `no-candidate-observed` for these
routes, not `valid`, `invalid`, `duplicate`, or `cannot-reproduce`. A04 has
bounded runtime evidence; R7/A04–A05 remain open for a completed known-record
check and any separately scoped follow-up. This result does not establish that
the product is secure or that untested routes are safe.

## Validation and limits

This was source review plus six local GET checks and two local login requests;
no project unit/integration suite, browser, analyzer, product mutation, or
external target test was run. The Maven build skipped tests. The local runtime
result is tied to the source commit above and the clean demo volume for this
run. The repository itself was not modified by this research; this audit is the
toolkit's record of the bounded result.
