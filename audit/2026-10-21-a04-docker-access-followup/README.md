# A04 Docker-state follow-up — 21 October 2026

## Scope and source identity

This is a bounded, read-only continuation of R7/A04 for the user's Kadrom
local-lab scope and its two existing synthetic candidate accounts. The product
source checkout remains pinned to
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c` and was clean when checked. Only the
three requested Docker state queries were issued. No container was started or
stopped; no volume, source, account, or application data was changed. No HTTP
request, build, migration, seed, or test was run. No Git operation was
performed.

## Docker read-only queries and result

The sandbox attempt could not connect to the current Docker daemon at
`npipe:////./pipe/docker_engine`; it returned `permission denied`. Following
the task boundary, the same read-only queries were retried with elevated
execution approval limited to reading this existing daemon's state:

1. `docker ps --filter label=com.docker.compose.project=a04-kadrom-20261021 --format '{{.ID}} {{.Names}} {{.Status}} {{.Ports}}'`
   — completed with exit code 0 and empty output: no running containers for the
   Compose project were returned.
2. `docker network inspect a04-kadrom-20261021_internal`
   — completed with exit code 0. Docker returned the named network with
   `Internal: true`, project label `a04-kadrom-20261021`, and `Containers: {}`.
3. `docker volume inspect a04-kadrom-20261021_mysql_data`
   — completed with exit code 0. Docker returned the named volume with project
   label `a04-kadrom-20261021` and the expected `mysql_data` volume label.

The volume object exists, but the three permitted queries do not establish
whether a stopped container retains a mount to it. Likewise, with no running
container and an empty network container map, no backend binding or MySQL /
frontend host-port state could be verified. The stored Compose override is a
configuration declaration, not proof of the effective runtime configuration.

## Gate and outcome

**Runtime HTTP check: not run.** The required preconditions were not all
verified: `docker ps` found no running lab containers, the network had no
attached containers, and the existing volume's attachment could not be
confirmed from the allowed queries. Therefore loopback-only backend binding,
absence of MySQL/frontend published ports, and preservation of the active
volume attachment could not be established. No credentials or application IDs
were used and no route was contacted.

This is a successful read-only state query with an unmet runtime precondition;
it is not a product test failure, timeout, or security result. No vulnerability
candidate was observed because no endpoint was tested. The earlier
`no-candidate-observed` outcome remains limited to the list/role routes covered
by the prior A04 runtime record. It does not establish the behavior or safety
of the same-role work-session GET routes.

A04 and R7 remain open. A future same-role check needs a running lab instance
whose effective network, host bindings, and volume attachment are verified
before requests; this follow-up did not start services or alter Docker state.
The candidate routes and limits are recorded in the prior
[same-role source review](../2026-10-21-a04-same-role-followup/README.md) and
[runtime follow-up](../2026-10-21-a04-runtime-followup/README.md).
