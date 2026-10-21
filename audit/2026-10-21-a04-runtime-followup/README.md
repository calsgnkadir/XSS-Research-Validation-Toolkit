# A04 runtime follow-up — 21 October 2026

## Scope

Continuation of the bounded same-role ownership check for the user's Kadrom
repository, pinned in the prior audit to
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. The intended check is limited to
the two existing synthetic candidate accounts, existing application IDs, and
read-only work-session GET routes. No application data, source, or container
was changed. No Git operation was performed.

## Read-only safety inspection

The retained toolkit override `.dxa/a04-kadrom-compose.override.yml` declares
an internal Compose network, disables MySQL and frontend published ports, binds
the backend to `127.0.0.1:18081`, and retains the named volume
`a04-kadrom-20261021_mysql_data`. These are configuration declarations only;
they do not prove that the override is active or describe the current engine
state. The base Kadrom `docker-compose.yml` publishes MySQL, backend, and
frontend ports (`.dxa/a04-kadrom-source/docker-compose.yml:14-18,74-76,93-97`),
so a runtime check requires verifying the effective Compose project first.

Read-only Docker queries were attempted for the project containers, the named
network `a04-kadrom-20261021_internal`, and the named volume
`a04-kadrom-20261021_mysql_data`. Each returned an access error before Docker
could return state:

- `docker ps --filter label=com.docker.compose.project=a04-kadrom-20261021`
- `docker network inspect a04-kadrom-20261021_internal`
- `docker volume inspect a04-kadrom-20261021_mysql_data`

The Docker client reported permission denied for
`npipe:////./pipe/docker_engine`; it also could not read the user's Docker
configuration. Consequently, the active containers, effective port bindings,
network internal flag, and existing volume attachment/preservation could not
be independently verified. The safety gate was not met. No container was
started or stopped, no volume was changed, and no HTTP request was sent.

## Source evidence and runtime result

Source inspection remains consistent with the earlier source-only audit:

- `WorkSessionController.java:25-30` restricts the controller to the candidate
  role; `:55-62`, `:69-82`, and `:85-91` expose ID-based GET routes for an
  active session, batch active sessions, and an application's session history.
- `WorkSessionService.java:133-149` filters returned session records by the
  application's candidate ID for the authenticated principal.
- The service's ownership validation at `WorkSessionService.java:154-164`
  checks that the application belongs to the candidate for the relevant
  mutating/check-in path; this source observation does not establish runtime
  behavior for the list GET route.

**Runtime outcome: not run.** There are no HTTP status codes or observed
cross-account response contents to report. This is an environment permission
failure, not a product response, test failure, timeout, or safe-result
observation. No vulnerability candidate was observed in this follow-up, and no
security conclusion can be drawn from the unrun check. The earlier
`no-candidate-observed` result still applies only to its previously tested
list/role routes.

## Roadmap status and next step

This follow-up adds no runtime evidence and does not close A04 or R7. Repeat
the same read-only Docker state inspection only from an environment that can
read the existing Docker engine. If and only if the active project is verified
to use the internal network, keep the backend loopback-only with no exposed
MySQL/frontend ports, and retain its existing named volume, perform bounded
GET-only same-role comparisons using the two existing synthetic accounts and
existing application IDs. Otherwise stop without requests. Do not use
`down -v`, mutate data, rebuild/migrate the database, or contact an external
service.

No tests, build, browser, analyzer, product endpoint, or external endpoint was
run in this follow-up.
