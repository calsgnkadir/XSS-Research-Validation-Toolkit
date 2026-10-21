# R7 / A05 — Spring Boot Actuator source impact triage

## Scope and source identity

Read-only review of the user-selected Kadrom source checkout at
`.dxa/a04-kadrom-source`, commit
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. The deps.dev result recorded in
the [managed direct advisory lookup](../2026-10-21-a05-managed-direct-advisories/README.md)
associates the direct root
`org.springframework.boot:spring-boot-starter-actuator:3.2.5` with
`GHSA-mgvc-8q2h-5pgc`. This audit inspects only source, Maven metadata already
recorded in the [effective dependency tree](../2026-10-21-a05-effective-dependency-tree/README.md),
and configuration. No app, test, container, endpoint, or external service was
run or contacted for this audit.

## Dependency mapping

- The POM inherits Spring Boot `3.2.5` from `spring-boot-starter-parent`
  (`.dxa/a04-kadrom-source/hotelapp/pom.xml:10-12`) and declares
  `spring-boot-starter-actuator` without an explicit version
  (`pom.xml:129-132`).
- The previously resolved effective tree confirms that direct starter at
  `3.2.5`, and its resolved compile/runtime path is
  `spring-boot-starter-actuator:3.2.5` →
  `spring-boot-actuator-autoconfigure:3.2.5` →
  `spring-boot-actuator:3.2.5`
  (`audit/2026-10-21-a05-effective-dependency-tree/README.md`, “Filtered
  Actuator subtree follow-up”).
- GHSA `GHSA-mgvc-8q2h-5pgc` keys the record to the direct
  `spring-boot-starter-actuator` package. The advisory-range review records its
  GitHub ecosystem range as including 3.2.5 (3.0.0 through 3.3.13), while the
  Spring vendor advisory's enumerated affected/fixed lines omit 3.2.x. Keep this
  vendor-versus-GHSA discrepancy unresolved; the source dependency path does not
  decide which version statement governs this branch. See the
  [advisory range review](../2026-10-21-a05-advisory-range-review/README.md).
- The effective subtree establishes that all three artifacts are present at
  3.2.5. It does not by itself establish that each is independently affected;
  the advisory's package key is the starter and its vulnerable behavior is
  conditional on the application route precondition below.

## Endpoint exposure and authorization in source

- The application uses `SERVER_PORT` with default `8080`
  (`hotelapp/src/main/resources/application.yml:1-2`). No
  `management.server.port` or management address override occurs in the three
  application YAML files. The source therefore configures Actuator on the
  application's ordinary server path/port; this does not establish whether a
  deployed network makes that port reachable.
- Base configuration exposes `health`, `info`, `circuitbreakers`, `flyway`,
  and `prometheus` over HTTP (`application.yml:248-256`). The `prod` profile
  overrides the exposed set to `health`, `info`, `metrics`, `prometheus`, and
  `circuitbreakers` (`application-prod.yml:113-126`), so `flyway` is not in that
  profile's configured include list. `application-dev.yml` contains no
  management override; the base include list applies there unless an external
  property overrides it.
- In the sole `SecurityFilterChain` reviewed, exact `/actuator/health`, its
  descendants, and `/actuator/info` are in the `permitAll` matcher list
  (`SecurityConfig.java:154-171`). The subsequent `/actuator/**` rule requires
  `ADMIN` (`SecurityConfig.java:174-179`). Thus the source intends the health
  summary/probes and info endpoint to be public, while other exposed Actuator
  endpoints (including metrics, Prometheus and circuit-breaker data) require an
  authenticated ADMIN role. This is a source-level matcher reading, not an
  observed HTTP result.
- Spring's vendor advisory precondition, as summarized in the
  [advisory-range review](../2026-10-21-a05-advisory-range-review/README.md),
  is a protected application endpoint declared under the Cloud Foundry Actuator
  endpoint path (for example `/cloudfoundryapplication/admin`). A source search
  across the pinned `hotelapp/src/main` and `hotelapp/src/test` trees found no
  `cloudfoundryapplication`/Cloud Foundry mapping, controller mapping under
  that path, Actuator base-path override, or application mapping under an
  Actuator path. The reviewed application controller routes are namespaced
  under `/api` (for example `AdminController.java:37,39`), while the explicit
  Actuator rules are under `/actuator` (`SecurityConfig.java:163-175`). The
  generic `.anyRequest().authenticated()` rule at `SecurityConfig.java:179`
  does not itself declare a handler at the required Cloud Foundry path.
  **Therefore the specific Spring vendor route precondition was not found in
  this pinned source.** This is a bounded source-search result, not a runtime
  route inventory.
- Base configuration sets health details to `when-authorized` and health role
  to `ADMIN` (`application.yml:253-256`). Production repeats that policy,
  additionally sets components to `when-authorized`, and enables liveness and
  readiness probes (`application-prod.yml:121-138`). The source comments and
  test name describe health summary as public and details/metrics as admin-only;
  the test is `SecurityHardeningIT.java:82-107`, under `@ActiveProfiles("test")`
  at line 50. This audit did not run or independently validate that test.
- Production enables the `env` info contributor and disables Java and OS info
  (`application-prod.yml:139-148`); the configured app name/version are at
  `application-prod.yml:151-154`. Although `/actuator/info` is public in the
  security matcher, the source reviewed here does not establish which runtime
  environment values, if any, are emitted. No inference of secret disclosure is
  made.

## Assessment and limits

The source shows the three-artifact Actuator path at 3.2.5, multiple Actuator
endpoints configured for web exposure, a public health/info exception, and an
ADMIN gate for the remaining `/actuator/**` paths. The protected application
route beneath `/cloudfoundryapplication` that Spring's vendor description
requires was not found in the pinned source. Combined with the unresolved
vendor-versus-GHSA 3.2.x range discrepancy, this source review does not
establish applicability or exploitability and is not a vulnerability finding.
Deployment reachability, active runtime profiles/property overrides, and the
actual runtime route table remain unverified here.

**R7/A05 disposition:** source impact review completed. The exact resolved
Actuator subtree and absent vendor route precondition are recorded, but the
vendor-versus-GHSA version discrepancy remains unresolved. No runtime
validation or exploitability conclusion is implied.
