# R7 / A04 Kadrom attendance and roster owner-boundary check — 22 October 2026

## Assignment and scope

Bounded local runtime comparison for R7/A04 on the user-selected Kadrom product
checkout, pinned to `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. The toolkit
checkout baseline was `a20a281c898b430861b9f0539fee444efe0c5965`; unrelated
pre-existing toolkit edits were preserved. This task was performed by temporary
collaboration worker `/root/a04_owner_read_runtime`; a native TOML custom-agent
invocation was not selected or verified.

The two routes tested were:

- `GET /api/business/listings/{listingId}/attendance`
- `GET /api/business/listings/{listingId}/roster`

Only a fresh, local disposable Kadrom database, two synthetic
`BUSINESS_OWNER` demo accounts, and a listing seeded for owner 1 were used. No
existing account or database row was reused. Two login POSTs were used only to
establish the test sessions. Exactly four target GETs were then sent: owner 1
positive control and owner 2 same-role cross-owner control on each route. No
browser, exploit payload, mutation endpoint, public/third-party product, or
external Kadrom URL was contacted.

## Source and lab isolation

The source checkout was clean at the pinned commit. The checked-in
`.dxa/a04-kadrom-source/docker-compose.yml` ordinarily publishes ports and has
explicit named resources, so the lab used an in-memory Compose override; no
source/config file was edited. A pre-create filtered Docker query found no
container with the new Compose project label, volume, or network names.

New resources:

| Resource | Name / observed value |
|---|---|
| Compose project | `a04-kadrom-owner-read-20261022` |
| MySQL volume | `a04-kadrom-owner-read-20261022_mysql_data` |
| Internal network | `a04-kadrom-owner-read-20261022_internal`, `internal=true` |
| Backend image | `sha256:773ffd3a73373b974b80fab06897640a4c65bde044f9a246e22834853d2065a5` |

The effective Compose JSON had no published ports for MySQL, backend, or
frontend. Only MySQL and backend were created; frontend was not started. Before
requests, filtered runtime inspection showed both containers healthy and
running, backend/MySQL published-port mappings null, backend with no mounts,
and MySQL mounting only the new volume at `/var/lib/mysql`. Both were attached
to the new internal network. The backend was healthy before requests. The helper
image `curlimages/curl:8.10.1` was already present locally; each one-shot helper
used only the new internal network and `--rm`.

The database volume was absent before this run and was created empty. The
application started with the Compose `dev,demo` profiles, Flyway enabled, and
the configured Hibernate validate mode. Startup therefore ran the app's
migration/seed startup path against the new disposable volume; the database
query below confirmed the demo seed accounts/listings existed. Startup also
enables scheduled jobs from this pinned product configuration; no specific
scheduler job execution is claimed. The previous project
`a04-kadrom-20261021` and its `a04-kadrom-20261021_mysql_data` volume were never
started or mounted; no old-volume database contents were queried. Only Docker
resource-presence/status metadata was checked. At the final read-only check,
both previous containers remained exited and the old volume still existed.

## Synthetic fixture and bounded requests

A read-only query inside the new MySQL container identified these synthetic
records (no emails, credentials, tokens, or response bodies are retained):

| Fixture | Database ID |
|---|---:|
| Owner 1 user | 45 |
| Owner 1 business | 8 |
| Owner 1 seeded listing | 19 |
| Owner 2 user | 46 |
| Owner 2 business | 9 |

Both login responses were HTTP 200 and identified their principals as
`BUSINESS_OWNER`. Login tokens remained in process memory and were not printed
or written. The only target GET observations were:

| Request | Expected control | Observed |
|---|---|---|
| Owner 1 `GET .../19/attendance` | Own-listing positive control | HTTP 200; response `listingId=19`; `expected=0`, `arrived=0`, zero rows |
| Owner 2 `GET .../19/attendance` | Same-role cross-owner denial | HTTP 403 |
| Owner 1 `GET .../19/roster` | Own-listing positive control | HTTP 200; XLSX media type; 3,948 bytes |
| Owner 2 `GET .../19/roster` | Same-role cross-owner denial | HTTP 403; JSON media type; 124 bytes |

The attendance positive response is an empty attendance fixture, not evidence
that candidate or shift records were isolated. The roster response was not
opened or inspected; only its status, media type, and byte count were recorded.
Owner 2 received no successful response from either endpoint in this run.

## Source correspondence and result

At the pinned source, `CheckInController.java:47-56` declares the attendance
route for `BUSINESS_OWNER`; `CheckInService.java:215-218` delegates to the
owner-scoped lookup, and `:287-293` compares the listing business owner ID with
the authenticated owner ID. `RosterController.java:33-43` declares the roster
route for `BUSINESS_OWNER`; `RosterService.java:69-75` loads the listing and
checks the same owner relationship before building the workbook. The two-owner
runtime results match those source-level checks for listing 19 in this fresh
synthetic run.

This is evidence for these two GET routes, one seeded listing, two synthetic
business-owner accounts, and this pinned local configuration only. It is not a
product-wide authorization result, a supported-release assessment, or a
vulnerability finding. A04 and R7 remain open for the broader roadmap scope.

## Setup failures, stop, and test limits

There were non-application command setup errors before the successful
comparison:

- An initial read-only SQL invocation passed its arguments incorrectly and
  returned MySQL error 1045. A second quoting attempt returned SQL syntax error
  1064. Neither query changed data. The corrected SQL was sent on stdin and
  returned only the synthetic IDs above.
- Two initial curl-helper command forms failed locally before reaching the
  application: one shell parse error (`EOF in backquote substitution`) and one
  `curl: (2) no URL specified`. No login or target GET was issued by either
  failed invocation. The final direct-entrypoint helper method completed the
  two logins and four target GETs reported above.

No Kadrom product test suite or toolkit test suite was run. The Dockerfile
packages the backend with `-DskipTests`; that build is not a test pass. The
observed endpoint responses are the only runtime test evidence in this record.

After the GETs, `docker compose stop backend mysql` completed successfully.
Both new containers are now exited; their filtered inspect records show no
published ports. The new MySQL volume still exists and is retained. Observed
container exit codes were backend 143 and MySQL 137 (the MySQL process appears
to have reached Docker's stop timeout and received SIGKILL); this is recorded as
a stop outcome, not as an endpoint or product test failure. No `down -v`,
volume deletion, or cleanup was run. The old project and volume remain intact.

## Coordinator disposition

The Roadmap's bounded A04 acceptance for the selected two-account list and
same-role GET checks is accepted for the exact routes recorded in the linked
A04 runtime audits. This closes that bounded A04 item; it does not close R7,
claim all Kadrom routes are covered, or establish product-wide authorization
safety. The broader limits above remain.
