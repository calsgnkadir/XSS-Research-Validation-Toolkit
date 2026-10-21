# A04 same-role ownership follow-up — 21 October 2026

## Scope and source pin

This is a source-only follow-up to the bounded A04 local Kadrom check. The
authorized product scope is the user's Kadrom repository and two synthetic
accounts for a read-only same-role ownership comparison. Product source was
confirmed at `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`; the source checkout was
clean. No source, account data, or application state was changed.

The question was whether the pinned source exposes an ID-based candidate GET
route that could compare access to one candidate's record when authenticated
as another candidate. Source review found relevant work-session routes:

- `GET /api/candidate/work-sessions/{applicationId}/active` —
  `WorkSessionController.java:55-62`.
- `GET /api/candidate/work-sessions/{applicationId}` —
  `WorkSessionController.java:85-91`.
- `GET /api/candidate/work-sessions/active-batch?ids=...` —
  `WorkSessionController.java:69-82`.

The controller applies `hasRole('CANDIDATE')` at class level
(`WorkSessionController.java:25-31`). The first two routes pass the
authenticated user ID and requested application ID to the service. The service
filters work sessions by the application's candidate ID before producing a
DTO (`WorkSessionService.java:133-149`). Source therefore identifies a
read-only route suitable for a bounded same-role comparison; this is not
runtime verification or proof of vulnerability/safety.

The already tested application-list routes remain role-scoped lists rather
than ID-addressed record reads: `ApplicationController.java:45-54,91-102`,
with repository predicates binding results to the authenticated candidate or
business owner (`ApplicationRepository.java:192-224`). The candidate
withdrawal route is ID-addressed but mutating (`ApplicationController.java:71-80`)
and was excluded from this read-only follow-up.

## Lab safety check and runtime status

The retained override file `.dxa/a04-kadrom-compose.override.yml` declares
`internal: true`, disables MySQL/frontend published ports, and binds the
backend only to `127.0.0.1:18081`. Its SHA-256 is
`b017b679caeb1a44139ab65e1a4386512d0fd27c6b60d060bf314f98f03d062`.
The source repository's base `docker-compose.yml` publishes MySQL, backend,
and frontend ports without loopback-only bindings (`docker-compose.yml:14-16,
74-76,93-94`), so the override must be active for a safe run.

The Docker engine could not be queried in this environment. Read-only
`docker ps`, `docker network inspect`, and `docker volume inspect` commands
returned `permission denied while trying to connect to the Docker API at
npipe:////./pipe/docker_engine`; Docker also reported access denied for its
user config. As a result, the effective Compose configuration, actual
published bindings, internal network state, existing container state, and
persisted volume could not be independently confirmed. No container was
started, stopped, or changed, and no HTTP request was made. This was an
environment permission failure, not an application response or test result.

## Outcome and narrow next step

Source review found a suitable same-role read-only ownership comparison, but
the runtime comparison is **not run**. No request status exists to report.
There is no new runtime finding. The prior `no-candidate-observed` outcome
continues to apply only to the previously tested candidate/business list
routes; it does not cover these work-session routes or establish security.

The smallest next step is to repeat the Docker safety inspection from an
environment that can read the Docker engine, verify the effective project
configuration uses only the `internal: true` network and loopback-only backend
binding with MySQL/frontend ports disabled, and confirm the existing named
volume remains attached. Only then, if safe, use existing synthetic candidate
accounts and existing application IDs for GET-only calls to the three routes
above. Keep credentials/tokens and response bodies in memory; record only
masked status and whether data belonging to the second account was returned.
Do not create, mutate, migrate, or delete records or volumes.

## Evidence integrity and limits

Source file SHA-256 values at the pinned commit:

| File | SHA-256 |
|---|---|
| `hotelapp/src/main/java/com/hotelapp/controller/WorkSessionController.java` | `71d5dcbfe17eff0457e780b0a67ad023b656682da731c0e59d4f66f6392301c5` |
| `hotelapp/src/main/java/com/hotelapp/service/WorkSessionService.java` | `503f5cfb820b2125f4b93851d0c622c3f99f87c036fb0b82635c17185e68ccbb` |
| `hotelapp/src/main/java/com/hotelapp/controller/CandidateController.java` | `7d1c87377018e0dc16e6a670dfffd94ed722d5f82e9c8d8469ab32dffec07112` |
| `hotelapp/src/main/java/com/hotelapp/controller/ApplicationController.java` | `76cb83ac478a95dac0bc84a8b9a2d1d035d4b17db4a4d259e173881c5738eec7` |
| `hotelapp/src/main/java/com/hotelapp/repository/ApplicationRepository.java` | `b8f6a6fab12927e87a3354714cb5a6c5bfd25329845e055c9976b61abfb34a01` |
| `docker-compose.yml` | `56894fa2e28f88d1e9097eee2f225ea47880c82417c7210814772ca72a5eb45a` |

No tests, build, analyzer, browser, external endpoint, or product HTTP request
was run. This record is a source-level A04 follow-up only; it does not close
A04/A05 or the broader R7 work.
