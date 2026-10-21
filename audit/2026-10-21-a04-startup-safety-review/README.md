# A04 startup/data-impact review — 21 October 2026

## Scope and conclusion

Read-only source/config review for the selected Kadrom lab, pinned at
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. No Docker daemon query, container
start/stop/create, database connection, build, migration, seed, HTTP request, or
Git operation was performed. Only this audit file was added.

**Do not start the existing stopped containers attached to
`a04-kadrom-20261021_mysql_data`.** Starting that project would run application
startup code against a persistent database and could apply schema changes,
update demo accounts, or alter expired/demo records through schedulers. The
actual Flyway history and current demo sentinel/data state were not queried, so
these effects cannot be excluded. Keep the old volume untouched.

A fresh project/volume configuration can be isolated safely at the Compose
configuration level. I evaluated a proposed override through Compose stdin
(no file written) with project name `a04-kadrom-disposable-20261021`, unique
network `a04-kadrom-disposable-20261021_internal`, and unique volume
`a04-kadrom-disposable-20261021_mysql_data`. Filtered config output confirmed
`internal=true`, all three services with no host-published ports, and only the
new named MySQL volume mounted at `/var/lib/mysql`. No resources were created.
This is a static config result, not proof of runtime state. New seed rows would
have new database IDs, so this path preserves the two demo identities/patterns,
not the exact prior database records or IDs.

## Startup chain and possible data effects

### Entrypoint, profiles, schema ownership

- `hotelapp/Dockerfile:23-25` exposes container port 8080 and starts the jar
  directly with Java. It does not use a separate migration-only entrypoint.
- `docker-compose.yml:31-43` configures the backend for `dev,demo` profiles.
  Lines 61-62 set `JPA_DDL_AUTO=validate` and `FLYWAY_ENABLED=true`.
- `application.yml:35-48` enables Flyway by default, uses the migration
  directory, baseline-on-migrate at version 1, checksum validation, and
  disallows out-of-order migrations. The current source contains migrations
  through V27. The Compose override only changes ports and resource names; it
  does not disable migrations or startup runners.
- `application-dev.yml:14-18` sets Hibernate `ddl-auto: update`. Compose's
  explicit `JPA_DDL_AUTO=validate` is intended to override the base placeholder
  (`application.yml:50-53`) under Spring Boot environment precedence. The
  application was not launched here, and its effective Spring property was
  not observed; if that environment setting were absent or ineffective, the
  dev-profile `update` setting would permit Hibernate schema writes.

Flyway can apply any pending migration when the backend starts. Most later
migrations add tables/columns/indexes, but some also touch rows (for example
`V22__application_optimistic_lock.sql:18-22` sets NULL `applications.version`
values to zero when that column is nullable). `V19__drop_reviews_and_documents.sql:5-7`
unconditionally drops `document_requests`, `documents`, and `reviews` if V19
has not yet been recorded. Therefore an older or untracked schema is not safe
to start on the assumption that migrations are harmless. The prior A04 audit
records that this volume began empty and that the same pinned lab later served
requests and seeded demo data; that is indirect evidence that the initial
startup succeeded, but the Flyway history/version/checksums were not retained
as evidence and are not verified now.

The source also has `SchemaMigration`, a `CommandLineRunner` ordered before the
seeder: `hotelapp/src/main/java/com/hotelapp/config/SchemaMigration.java:23-32`.
Every backend startup issues three `ALTER TABLE ... MODIFY COLUMN` statements
for notifications type/title and application status (`:36-44`). Its comments
call same-type changes no-ops, but these remain schema operations on every
startup and are not guarded by Flyway history.

No `schema.sql`, `data.sql`, or `import.sql` was found in the application main
resources. That does not remove the explicit Flyway migrations or Java runners
above.

### Demo seeder

`DemoSeeder` is active under the Compose `demo` profile (`DemoSeeder.java:35-42`)
and is ordered after `SchemaMigration` (`:41`). It is guarded by the sentinel
`demo-aday1@test.com` (`:54,77-85`). If the sentinel exists, it skips the bulk
seed, but calls `markExistingDemoAccountsVerified()` first (`:80-83`); that
method writes `emailVerifiedAt` for any of the 10 demo candidate or 6 demo
business-owner rows still missing it (`:61-74`). If the sentinel is absent,
the runner attempts to seed users, businesses, listings, applications,
conversations, and messages (`:87-90` and subsequent save loops through `:345`).
This is a sentinel-based skip, not a per-record reconciliation guarantee for an
arbitrary pre-existing partial dataset. The current database sentinel and row
state were not inspected, so the branch that would run on the old volume is
unknown.

The prior A04 record says the volume was initially empty and the seeder
reported 10 candidates, 6 businesses, 15 listings, and 65 applications. This
supports that the first seed completed in that run; it does not prove what data
is currently present after the application was stopped.

### Schedulers after startup

Compose does not provide scheduler-delay overrides. Several active schedulers
can write soon after application startup:

- `ExpiredApplicationScheduler.java:39-52` expires overdue held applications;
  its initial delay defaults to 0 (`:40-41`).
- The standby expiry job has initial delay 0 by default and may advance/close
  overdue offers (`ExpiredApplicationScheduler.java:55-65`).
- `OutboxRelay.java:53-74` starts with default initial delay 0; pending events
  may be marked processed/deferred/failed, and email events are handed to its
  email handler. The internal Docker network limits container egress in the
  proposed setup, but no service was started to observe actual handling.
- `ListingAutoCloseScheduler.java:38-45` begins after a default 60 seconds and
  can close listings whose shifts have ended.
- Scheduled expiry, GDPR anonymization, SGK reminders, and old outbox cleanup
  also have cron schedules (`ExpiredApplicationScheduler.java:25-36,76-78`,
  `GdprService.java:192-218`, `OutboxRelay.java:120-133`). Their database
  effects depend on current rows and when the app runs; that state is unknown.

Thus even if Flyway reports no pending migration, starting the old backend can
still mutate existing demo data through the runner and schedulers.

## Disposable Compose isolation check

The checked-in A04 override hardcodes the original volume and network names at
`.dxa/a04-kadrom-compose.override.yml:13-20`. Changing only the Compose
project-name while reusing that override would **not** isolate the persistent
resources: explicit Compose `name:` values bypass project-name prefixing.
Therefore do not run a fresh project with the old override unchanged.

An in-memory override was evaluated using Compose config with a different
project name and new explicit volume/network names. Its filtered result was:

| Service/resource | Configured result |
|---|---|
| backend | No host ports; default network |
| mysql | No host ports; new `mysql_data` volume mounted at `/var/lib/mysql` |
| frontend | No host ports; default network |
| default network | `a04-kadrom-disposable-20261021_internal`, internal `true` |
| `mysql_data` volume | `a04-kadrom-disposable-20261021_mysql_data` |

This proves Compose resolves distinct names and no published ports for that
proposed config. It does not prove the names are unused in the Docker daemon or
that the created runtime will match; both must be rechecked read-only before
any future startup. The project/volume have not been created. Before test
requests, also confirm the backend is healthy and the internal network and
mounts match this config. The direct API check can use a request from inside the
backend container to its own loopback, avoiding host port publication.

## Preservation and next step

1. Leave the existing stopped project and
   `a04-kadrom-20261021_mysql_data` untouched; do not start or recreate those
   containers and do not run `down -v`.
2. If the coordinator authorizes a disposable runtime, use only a new project,
   volume, and internal network matching the filtered config above, with no
   published service ports. Verify those names are unused and inspect the
   resulting state before sending requests.
3. The fresh demo seed supplies synthetic accounts with new database IDs. If
   exact existing records/IDs are required instead, keep A04 blocked until a
   separately verified, restorable copy/export plan exists; do not point the
   existing stopped MySQL container at its current volume.
4. Preserve the old volume as the rollback/reference copy. Any future cleanup
   or deletion requires separate authorization; none is proposed here.

No runtime startup, migration, seed, scheduler, database query, test, or same-
role HTTP request was performed. No vulnerability conclusion is made. A04 and
R7 remain open.
