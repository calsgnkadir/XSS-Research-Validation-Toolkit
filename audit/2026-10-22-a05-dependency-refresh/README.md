# Kadrom bounded A05 dependency refresh — 22 October 2026

## Scope and source state

This follow-up records the coordinated review of the user-authorized local
Kadrom remediation at `.dxa/a04-kadrom-source`. The target checkout is pinned
at `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`, branch `main`. The cached
`origin/main` is `ba38bd3a5fde6ea57089ab04eb38f58829110096`; it is one commit
ahead, with the previously observed frontend-only change in
`hotel-web/vite.config.js`. The target worktree has 38 tracked modifications
and three new files (41 source files total). No target fetch, merge, commit or
push was performed. No deployment, production account, Docker service or
multipart request was tested. The user reserved multipart testing for a later
session.

The final Maven run used Windows, Java 17, Maven 3.9.16 and the in-memory H2
test profile. It compiled 247 main source files and all 91 test source files.
The final full suite passed 665/665; the exact command and an earlier
Boot-managed H2 failure/resolution are in [VALIDATION](../../VALIDATION.md).
Docker integration, CI and deployment checks were not run.

## Dependency review and bounded scan

The final resolved Maven tree contained 246 distinct JAR coordinates across
the compile/runtime/test dependency graph, including Resilience4j 2.4.0 and
test-only H2 2.3.232. An OSV `v1/querybatch` snapshot queried all 246
coordinates and returned 246 response rows with zero matched coordinates at
`2026-10-22T13:26:35Z`. This is a known-record snapshot
for the captured graph and source; it is not proof that no vulnerability
exists, does not identify the currently supported Kadrom release, and does not
replace vendor advisories or a later scan. The dependency tree was generated
under `hotelapp/target` and is not a source deliverable.

The POM changes map to these upstream component issues and source paths:

| Component / change | Reason and bounded applicability | Primary record |
|---|---|---|
| Jackson 2 `2.21.8`, Jackson 3 `3.1.8` | Boot 4.1.1 managed `2.21.5` / `3.1.5`; latest reviewed Jackson advisory CVE-2026-110879 is fixed in the selected versions. Existing source uses Jackson 2 `ObjectMapper`; no app default-typing activation was found in the reviewed path. | [GHSA-m8xf-2cr7-77ph](https://github.com/advisories/GHSA-m8xf-2cr7-77ph), [Jackson 2.21.8 release](https://github.com/FasterXML/jackson/wiki/Jackson-Release-2.21.8) |
| Tomcat `11.0.27` | Boot 4.1.1 managed `11.0.24`; update to a reviewed security release on the 11.0 line. This is a dependency-level precaution, not a reproduced Kadrom exploit. | [Apache Tomcat 11 security](https://tomcat.apache.org/security-11) |
| Apache POI `5.4.0` | Replaces `5.3.0`, below the advisory's fixed release. Inspected Kadrom source generates XLSX with POI; no user-supplied OOXML parsing path was identified. | [GHSA-gmg8-593g-7mv3](https://github.com/advisories/GHSA-gmg8-593g-7mv3) |
| Apache HttpClient `4.5.14` | Pins a fixed 4.x version because `cloudinary-http44` otherwise resolves `4.4`, below the advisory fix. No standalone request-path exploit was reproduced. | [GHSA-7r82-7xv7-xcpj](https://github.com/advisories/GHSA-7r82-7xv7-xcpj) |
| Resilience4j `2.4.0` Boot 4 module + Spring Boot AspectJ starter | Boot 4.1.1 had retained `resilience4j-spring-boot3:2.2.0`; upstream introduced a separate Boot 4 module in 2.4.0. The application uses `@CircuitBreaker` and circuit-breaker YAML, so this fixes framework integration alignment. AOP effectiveness in production is not inferred from compilation. | [Resilience4j 2.4.0 release notes](https://github.com/resilience4j/resilience4j/releases), [module build](https://github.com/resilience4j/resilience4j/blob/v2.4.0/resilience4j-spring-boot4/build.gradle), [Spring Boot 4 migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide) |
| H2 `2.3.232` test scope only | Boot 4.1.1 manages H2 2.4.240, which caused six full-suite errors in generated CHECK/enum constraints. Upstream reports the cross-connection bug for 2.4.240 and states the same workflow works in 2.3.232. The override is test-only and is not in the production dependency graph. | [H2 issue #4320](https://github.com/h2database/h2database/issues/4320), [H2 issue #4302](https://github.com/h2database/h2database/issues/4302) |

The graph also resolves Spring Security `7.1.1`, Spring Framework `7.0.9`,
Spring Data `4.1.1`, Micrometer `1.17.1` and springdoc `3.1.1`. The previously
reviewed Spring advisory ranges relevant to BCrypt, Sort, Micrometer, Spring
Data, RFD and the Boot 3 Actuator/X.509 leads were compared against this tree;
the current tree no longer contains the old vulnerable versions for those
leads. This version comparison does not close any product-specific source,
configuration, runtime or record-identity question. Vendor range conflicts
and product identity lookup remain documented in the earlier A05/R7 records.

## Remediation and acceptance boundary

The BCrypt application fix and regression coverage remain as described in the
[remediation audit](../2026-10-22-a05-bcrypt-remediation/README.md), including
the UTF-8 72-byte policy before encode/match paths and the exact-72-byte
multibyte password-change test. A selected integration/auth/A04/POI/email run
passed **63/63**, then the final full suite passed **665/665**, including
`CheckInServiceTest` (A04) and `RosterServiceTest` (POI-backed XLSX generation).
`git diff --check` passed in the target checkout.

Disposition:

- **A04 bounded acceptance:** complete for the specific selected routes,
  synthetic accounts and positive controls listed in the A04 runtime records.
  It is not product-wide authorization assurance.
- **BCrypt remediation lead:** local source fix and focused auth regression
  accepted for this pinned source state. The existing-account recovery plan,
  source merge onto the current target upstream, deployment and production
  behavior are not verified.
- **A05 umbrella:** bounded dependency snapshot and selected local candidate
  work are complete for this source state. The user-owned multipart test is
  still pending; prior Micrometer/Sort and advisory applicability limits,
  effective deployed dependencies, and supported-release identity remain
  outside what this snapshot closes.
- **R7:** the owner-review report is prepared locally. Later exact-coordinate
  GitHub global advisory and OSV queries were evaluable and returned zero rows
  for the local Maven coordinate; public repository issues/releases/tags were
  empty, and the repo security-advisories endpoint returned 404. These results
  do not identify a supported product release or rule out private advisories.
  No absence-of-record conclusion, external disclosure, or maintainer contact
  is claimed. R7 remains open for supported-release identity and owner
  disposition. See the [R7 follow-up](../2026-10-22-r7-authorization-followup/README.md).

No application data was migrated or deleted. Target commit `6be6a07` was merged
with upstream Vite commit `ba38bd3` and pushed as `c3ce102`; fetched
`origin/main` matched. The tested 41-file target source remains undeployed. No
CI, production runtime or multipart test is claimed.
