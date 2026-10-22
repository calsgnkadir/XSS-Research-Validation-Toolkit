# R7 / A05 — Micrometer effective local configuration check

## Scope and identities

Read-only follow-up to [the pinned source/config review](../2026-10-22-a05-micrometer-config-review/README.md). The product checkout is `.dxa/a04-kadrom-source`, pinned at `ae4aebbf8963f550f6bb7c3465fb1270d677af1c` on branch `main`; its `git status --short` returned no changes. Toolkit checkout HEAD at inspection was `e34a4aad1cdd5e2e2054a616b888525bd8d8bb4c`.

The coordinator assigned this read-only task through `collaboration.spawn_agent`
with `agent_type=xss_security_researcher` (`/root/micrometer_effective`). The
coordinator read the corresponding TOML role definition before assignment;
runtime loading of that TOML was not independently verifiable.

SHA-256 of inspected tracked inputs:

| File | SHA-256 |
|---|---|
| `hotelapp/pom.xml` | `AF8E4AED12B15A646460987E2FD94BDA8F31C482537498599A3BB473B5CE8112` |
| `hotelapp/src/main/resources/application.yml` | `2AC8088C1BD346174B851D2EDD046A6303B8BF0A77035EC6A272B247840E1D76` |
| `hotelapp/src/main/resources/application-prod.yml` | `CEAA25212A67FABB4CAEC3EA8D67D73E2B32BC854F43A312E361669DF2A07799` |
| `hotelapp/src/test/resources/application-test.yml` | `E9992524B6E40754D48AC1FCCF043F2558463F97AA847A5A15403939CFEF307E` |

## Checks and evidence

Read-only commands: `docker ps --format "{{.ID}} {{.Image}} {{.Names}} {{.Status}} {{.Ports}}"`; `Get-Process | Where-Object { $_.ProcessName -match 'java|docker|podman' } | Select-Object ProcessName,Id,StartTime`; pinned checkout `git status --short` / `git rev-parse HEAD`; `Get-FileHash -Algorithm SHA256` for the four files above; and line-numbered source searches in the POM and profile YAMLs.

- **Runtime availability — host observation, not product behavior:** The specialist's `docker ps` could not connect to `npipe:////./pipe/docker_engine` (pipe not found); the filtered process query returned no Java, Docker, or Podman processes. The coordinator then retried a read-only `docker ps --all --format "{{.Names}} {{.Status}} {{.Ports}}"` with approved escalation; Docker reported that `npipe:////./pipe/dockerDesktopLinuxEngine` was absent and the daemon could not be reached. No local Java app process was discovered. Because the Docker engine was unavailable, container inventory remains unknown; no app was started, no build/test/request was made, and no container state was changed.
- **Dependency/source config — source evidence:** `hotelapp/pom.xml:131` declares `spring-boot-starter-actuator`; `:134–138` declares the Prometheus registry. The earlier offline resolved tree audit records `micrometer-core:1.12.5` and `micrometer-registry-prometheus:1.12.5` for this same pinned commit ([tree evidence](../2026-10-21-a05-effective-dependency-tree/README.md)). This establishes declared/resolved dependencies, not active beans.
- **Default/local profile — source evidence:** `application.yml:5–6` sets `dev`; `:248–252` exposes the Prometheus endpoint. The earlier source review found no checked-in observation opt-out or custom replacement filter/predicate in the pinned app source. This supports the expectation that Spring Boot's MVC observation auto-configuration can register, but it does not prove a particular runtime context instantiated it or recorded a metric.
- **Production profile — source evidence:** `application-prod.yml:116–120` exposes `metrics` and `prometheus`; no observations opt-out was found in the checked-in profile. Deployment environment overrides, packaged artifact configuration and effective production beans were not inspected.
- **Test profile — source evidence only:** `application-test.yml` exists and its SHA-256 is recorded above. The earlier review found no `management.observations` opt-out there. No test application context was started; no test-profile bean conclusion is claimed.

## Expected vs observed and disposition

Expected from the checked-in config plus the Spring Boot 3.2.5 MVC metrics behavior documented in the prior review: an application context with Actuator, Micrometer registry and MVC enabled, absent external overrides, should normally receive HTTP server observation/metric auto-configuration. Observed here: only the pinned source declarations and profile settings; there is no effective runtime observation. In particular, this review cannot answer whether `ObservationRegistry`, servlet observation instrumentation, or an HTTP server meter is present in a live Kadrom instance, nor whether a custom method produces a metric.

Therefore effective bean/config applicability remains **unverified**. This is not a negative finding, not a reproduced DoS, and not a confirmed vulnerability. No reflection, callback, browser execution, or vulnerability impact test was performed; those evidence classes are not interchangeable with source/config presence.

## Roadmap mapping and limits

Maps to **R7/A05**. It narrows the next step by establishing that no local Java app process was found and the Docker engine was unavailable for the authorized read-only effective inspection. Container inventory therefore remains unknown. A future effective-bean check requires an accessible authorized instance; this assignment did not start one. A05/R7 remains open. No tests were run.
