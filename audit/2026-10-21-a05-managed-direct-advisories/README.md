# R7 / A05 — deps.dev direct runtime advisory lookup

## Scope and source identity

Read-only known-record lookup for the selected, user-owned Kadrom source. The
dependency set is the 21 effective direct compile/runtime roots in the
[resolved dependency-tree audit](../2026-10-21-a05-effective-dependency-tree/README.md),
including versions inherited from the Spring Boot 3.2.5 parent/BOM. The source
checkout is pinned there at `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`; its
resolved Maven graph was produced offline from the existing cache. This lookup
did not contact Kadrom endpoints, run the application, or submit a disclosure.

The official stable deps.dev v3 `GetVersion` route is documented as returning
version metadata and advisory keys:
[API v3 GetVersion](https://docs.deps.dev/api/v3/#getversion) and
[official API protocol](https://github.com/google/deps.dev/blob/main/api/v3/api.proto).
The requested route shape was
`GET https://api.deps.dev/v3/systems/MAVEN/packages/{URL-encoded-group:artifact}/versions/{version}`.
Each successful response's `versionKey` exactly matched the requested Maven
coordinate and version. `advisoryKeys` is reported as returned by deps.dev; it
is an index result, not an independent affected-range or product-impact review.

## Positive control

Before querying the Kadrom coordinates, a fresh request through the same
`GetVersion` route was made for the known-positive Maven control
`org.apache.logging.log4j:log4j-core@2.14.1`.

| UTC start | UTC end | HTTP client result | Returned version key | Advisory count / IDs |
|---|---|---|---|---|
| 2026-10-21T20:18:11.1136967Z | 2026-10-21T20:18:11.4749689Z | OK | `org.apache.logging.log4j:log4j-core@2.14.1` | 7: `GHSA-3pxv-7cmr-fjr4`, `GHSA-6hg6-v5c8-fphq`, `GHSA-7rjr-3q55-vv33`, `GHSA-8489-44mv-ggj8`, `GHSA-jfh8-c2jp-5v3q`, `GHSA-p6xc-xr62-6r2g`, `GHSA-vc5p-v9hr-52mj` |

The control demonstrates that this API path returned known advisory keys during
the run. It does not establish the completeness of deps.dev's data for other
coordinates.

## Direct runtime-root responses

Times below are the UTC request-start timestamps emitted by the client. All 21
requests returned successfully; all returned version keys exactly matched the
requested coordinates. A zero count means this response contained no
`advisoryKeys`; it is not proof that the version is safe or that no record
exists in another source.

| UTC start | Requested and returned exact version key | Advisory count / IDs |
|---|---|---|
| 2026-10-21T20:17:42.4281436Z | `org.apache.poi:poi-ooxml@5.3.0` | 1: [`GHSA-gmg8-593g-7mv3`](https://github.com/advisories/GHSA-gmg8-593g-7mv3) |
| 2026-10-21T20:17:43.0943383Z | `org.springframework.boot:spring-boot-starter-web@3.2.5` | 0 |
| 2026-10-21T20:17:43.4563184Z | `org.springframework.boot:spring-boot-starter-websocket@3.2.5` | 0 |
| 2026-10-21T20:17:43.7977342Z | `org.springframework.boot:spring-boot-starter-security@3.2.5` | 0 |
| 2026-10-21T20:17:44.1603970Z | `org.springframework.boot:spring-boot-starter-oauth2-client@3.2.5` | 0 |
| 2026-10-21T20:17:44.5014761Z | `org.springframework.boot:spring-boot-starter-data-jpa@3.2.5` | 0 |
| 2026-10-21T20:17:44.8459628Z | `org.springframework.boot:spring-boot-starter-validation@3.2.5` | 0 |
| 2026-10-21T20:17:45.2010610Z | `com.mysql:mysql-connector-j@8.3.0` | 0 |
| 2026-10-21T20:17:45.5635554Z | `org.flywaydb:flyway-core@9.22.3` | 0 |
| 2026-10-21T20:17:45.9052836Z | `org.flywaydb:flyway-mysql@9.22.3` | 0 |
| 2026-10-21T20:17:46.2486339Z | `io.jsonwebtoken:jjwt-api@0.12.5` | 0 |
| 2026-10-21T20:17:46.6054017Z | `io.jsonwebtoken:jjwt-impl@0.12.5` | 0 |
| 2026-10-21T20:17:46.9514450Z | `io.jsonwebtoken:jjwt-jackson@0.12.5` | 0 |
| 2026-10-21T20:17:47.2996712Z | `com.bucket4j:bucket4j-core@8.10.1` | 0 |
| 2026-10-21T20:17:47.6612788Z | `io.github.resilience4j:resilience4j-spring-boot3@2.2.0` | 0 |
| 2026-10-21T20:17:47.9931327Z | `org.springframework.boot:spring-boot-starter-actuator@3.2.5` | 1: [`GHSA-mgvc-8q2h-5pgc`](https://github.com/advisories/GHSA-mgvc-8q2h-5pgc) |
| 2026-10-21T20:17:48.3380290Z | `io.micrometer:micrometer-registry-prometheus@1.12.5` | 0 |
| 2026-10-21T20:17:48.6984264Z | `com.cloudinary:cloudinary-http44@1.36.0` | 0 |
| 2026-10-21T20:17:49.0412344Z | `org.springdoc:springdoc-openapi-starter-webmvc-ui@2.5.0` | 0 |
| 2026-10-21T20:17:49.3791760Z | `org.projectlombok:lombok@1.18.32` | 0 |
| 2026-10-21T20:17:49.7207407Z | `com.iyzipay:iyzipay-java@2.0.129` | 0 |

For the two returned records, the advisory identifiers link to the official
GitHub Advisory Database entries. This task records index matches only; it does
not determine whether the resolved package version falls inside each
advisory's affected range or whether the application is exploitable. The
Spring Boot Actuator match in particular requires source-advisory range and
dependency-path review before any applicability statement.

## Execution, errors, and limits

- The default sandboxed PowerShell request to the control could not connect to
  the remote host. After network escalation was approved, the control and all
  21 bounded direct-root requests succeeded. The escalated client returned no
  HTTP error for these requests; no retry or batch API was used.
- There were 21 direct-root queries, sent serially with a 250 ms pause between
  requests. No transitive coordinate, test-scope dependency, plugin dependency,
  or packaged-artifact inventory was queried. The source is the Maven-resolved
  compile/runtime graph documented in the linked dependency-tree audit.
- deps.dev data is an index of known advisories, not a complete guarantee of
  database coverage or current vendor policy. Exact keys and nonzero counts are
  lookup evidence, not vulnerability confirmation. Zero counts do not imply
  safety.
- No code, POM, local application, container, test, or product endpoint was
  changed or run. No disclosure was prepared or sent. No CVE or application
  vulnerability is confirmed by this audit.

**Bounded result:** 21/21 direct runtime roots resolved to their exact requested
keys; 2 roots returned one advisory key each and 19 returned zero keys. The
Log4j positive control returned 7 keys. Follow-up should review the two linked
advisory ranges and their resolved dependency paths; the broader R7/A05 status
must not be marked as “no advisories” based on this lookup alone.
