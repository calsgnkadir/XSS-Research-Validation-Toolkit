# R7 / A05 — Micrometer HTTP instrumentation applicability review

## Scope and source identity

Source/configuration-only review of the user-selected Kadrom checkout at
`.dxa/a04-kadrom-source`, pinned commit
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. The toolkit workspace was at
`a20a281c898b430861b9f0539fee444efe0c5965` when assigned. I read the project
instructions, roadmap/status, workflow and XSS specialist TOML, along with the
prior A05 effective dependency tree, advisory range review, Spring/Tomcat source
review, and remaining-path audit. The TOML contents were inspected; this record
does not treat that as proof of native role configuration being loaded.

No application runtime, build, test, endpoint, Docker service, callback, or
browser was used. No product/toolkit application code was changed. Only this
audit file was created.

## Dependency and advisory match

The pinned POM declares `spring-boot-starter-actuator` at
`hotelapp/pom.xml:131` and `micrometer-registry-prometheus` at
`hotelapp/pom.xml:134–138`. The successful offline Maven runtime tree resolves
the registry to 1.12.5; its transitive `io.micrometer:micrometer-core` is also
1.12.5. The exact coordinates and tree method are recorded in the
[effective dependency-tree audit](../2026-10-21-a05-effective-dependency-tree/README.md).
This establishes presence in the pinned compile/runtime graph; it does not by
itself establish active instrumentation.

The official [GitHub advisory](https://github.com/advisories/GHSA-g3pr-3p32-fp23)
lists `micrometer-core` 1.12.5 within its affected range. The [Spring vendor
advisory](https://spring.io/security/cve-2026-40984/) states the additional
condition: one or more HTTP server instrumentations must be configured and
metrics must be recorded through the instrumentation. GitHub's range summary
and vendor's prose differ for some later 1.13.x versions; that discrepancy does
not affect pinned 1.12.5, which is in both published affected ranges.

The upstream [Micrometer fix commit](https://github.com/micrometer-metrics/micrometer/commit/36da131525228188a36779a28471a76c79213dd4)
shows a change to bound the HTTP `method` tag to standard methods, mapping other
methods to `UNKNOWN`. This supports the relevant crafted input class as an
unrecognized/nonstandard HTTP method. It does not prove that every arbitrary
method reaches Kadrom's servlet stack or causes resource exhaustion there.

## Configuration and source-path assessment

### Local/default profile

- Base configuration selects `dev` by default (`hotelapp/src/main/resources/application.yml:5–6`). The local Compose declaration selects `dev,demo` (`docker-compose.yml:43`).
- The base configuration exposes Prometheus along with other actuator endpoints (`application.yml:248–252`), and the POM supplies its registry. No `management.observations` disablement or custom `ServerHttpObservationFilter`, `ObservationPredicate`, or replacement observation configuration was found in the pinned application source/configuration search.
- Spring Boot 3.2.5's [official MVC metrics documentation](https://docs.spring.io/spring-boot/docs/3.2.5/reference/html/actuator.html#actuator.metrics.tagged-metrics) says auto-configuration instruments all Spring MVC controller and functional-handler requests; the default filter handles all requests unless replaced. Therefore the checked-in local/default source config supports the instrumentation and metric-recording prerequisites. This is framework-plus-source inference, not runtime bean evidence.

### Test profile

- The checked-in test resource is `hotelapp/src/test/resources/application-test.yml`; integration tests use `@ActiveProfiles("test")` (for example, `hotelapp/src/test/java/com/hotelapp/integration/SecurityHardeningIT.java:50`).
- That test resource does not define a `management.observations` opt-out. The test profile is not configured as a substitute for Micrometer or the servlet instrumentation; test dependencies supplement rather than remove application runtime dependencies.
- Thus the source indicates instrumentation may also be active in Spring Boot integration-test contexts. No test application context was started here, so effective test-profile bean registration and metric recording remain unverified.

### Production profile/deployment declarations

- `application-prod.yml:116–120` exposes `metrics` and `prometheus`, and does not declare observations disabled.
- Checked-in production launch declarations select `prod` in `deploy/prod/docker-compose.prod.yml:52`, `deploy/fly/backend.fly.toml:22`, and `compose.production-check.yml:27`. The local profile declarations are present in `docker-compose.yml:43`; Render's profile key is at `render.yaml:32`.
- The official [Spring Boot 3.2.5 MVC metrics documentation](https://docs.spring.io/spring-boot/docs/3.2.5/reference/html/actuator.html#actuator.metrics.tagged-metrics) supports default request instrumentation. Given the dependency graph and checked-in profile configuration, production configuration is source-supported as enabling the relevant Micrometer metric path. Actual deployed environment overrides, packaged artifact contents, and effective runtime beans were not inspected, so deployment-effective state is not proven.

### Request and access preconditions

The relevant signal is a nonstandard/custom HTTP method reaching the HTTP server instrumentation and its metric being recorded, rather than a special business-controller payload. The instrumentation is for Spring MVC requests generally, so Actuator endpoint exposure is not itself the prerequisite. Kadrom's `SecurityConfig.java:163–175` makes health routes public and places other actuator paths behind ADMIN authorization; this controls Actuator response access, but source alone cannot establish at which exact filter stage a rejected custom-method request is recorded. The method token may also be constrained by the deployed HTTP connector or upstream proxy; neither effective connector limits nor proxy behavior were reviewed.

## Disposition and evidence class

- **Dependency present:** confirmed by pinned POM plus successful offline resolved runtime tree: `micrometer-core:1.12.5`.
- **Auto-configuration possibility:** confirmed by Spring Boot 3.2.5's documented Spring MVC metrics auto-configuration and the app's Actuator/MVC/Micrometer dependencies.
- **Checked-in profile configuration:** source indicates no opt-out and exposes Prometheus in default/local and production configuration. Test profile likewise has no observations opt-out.
- **Effective configuration:** not established for a running test/local instance or production deployment; no runtime inspection occurred.
- **Advisory applicability:** source-backed candidate with all documented prerequisites supported by dependencies and checked-in configuration. No request behavior, DoS, impact, or Kadrom vulnerability is reproduced or confirmed. Treat as a plausible R7/A05 dependency triage candidate, not a confirmed product vulnerability.
- **Reflection/callback/execution:** not evaluated; no callback or browser/JavaScript execution occurred.
- **Test result:** none run in this source-only review.

## Smallest safe next step

If the coordinator wants to resolve effective local applicability, inspect the
already-authorized disposable local app's effective Spring configuration/bean
presence without sending unusual methods. If active instrumentation is present,
decide separately whether one harmless, bounded request using a valid but
nonstandard method is justified in that disposable lab; capture only status,
health-after, and whether a method metric was recorded. Do not repeat requests
or infer a production result from the local profile. A dependency update and
regression test would be a separate remediation decision.

This review maps to **R7/A05**. It adds source/configuration triage to the
existing dependency/advisory evidence but does not complete A05 or R7.
