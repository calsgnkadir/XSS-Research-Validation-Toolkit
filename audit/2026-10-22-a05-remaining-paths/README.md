# R7 / A05 — remaining advisory source-path review

**Date:** 2026-10-22
**Review type:** bounded read-only source/configuration triage
**Roadmap:** R7, A05
**Source under review:** user-owned Kadrom repository, pinned commit
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`
**Toolkit checkout:** `a20a281c898b430861b9f0539fee444efe0c5965` on `main`; the
local `origin/main` ref matched. Existing toolkit worktree changes were present
and were preserved.

## Scope and method

This follow-up examines selected source conditions previously left open in the
A05 direct/transitive advisory and source reviews: Micrometer HTTP server
instrumentation, Spring Security X.509 extraction, BCrypt password length,
Spring Data `Sort` parsing, multipart parsing/temp files, and Tomcat WebSocket
client redirects. It also rechecks how these findings relate to the already
recorded Spring RFD lead. The pinned Kadrom checkout was clean at the reviewed
commit.

Official GitHub Advisory Database and Spring security pages were reachable and
read for the relevant descriptions, prose version lists, and machine-readable
package ranges. The exact resolved coordinates remain documented in the
[effective Maven tree](../2026-10-21-a05-effective-dependency-tree/README.md)
and [range review](../2026-10-21-a05-transitive-range-review/README.md).
Searches and reads were limited to the pinned Kadrom source/configuration and
already cached local metadata. Spring Boot, Spring Security, Micrometer, and
Tomcat source JARs were not present in the checked Maven cache. No Maven,
application, container, endpoint, provider, or test was run; no Kadrom source or
dependency was changed.

## Source identity

The following SHA-256 values identify files used for the conclusions below.
All paths are relative to the toolkit repository root and point into the
read-only pinned Kadrom checkout.

| File | SHA-256 |
|---|---|
| `hotelapp/pom.xml` | `AF8E4AED12B15A646460987E2FD94BDA8F31C482537498599A3BB473B5CE8112` |
| `hotelapp/src/main/java/com/hotelapp/config/AppConfig.java` | `2586662E7345B1FCE2D68811ADE48DB3185E6E401C76EE1061F20A2B5175D207` |
| `hotelapp/src/main/java/com/hotelapp/config/SecurityConfig.java` | `DC2E1C21A333D6223F4EE4280E3E140450270A8FD5DD66CDE26CB23763598D18` |
| `hotelapp/src/main/java/com/hotelapp/metrics/AppMetrics.java` | `2B109A0294740C222F26C47CB82FAE712ACBF1F46C44A286C0FBA18CAAA17AE7` |
| `hotelapp/src/main/resources/application-prod.yml` | `CEAA25212A67FABB4CAEC3EA8D67D73E2B32BC854F43A312E361669DF2A07799` |
| `hotelapp/src/main/resources/application.yml` | `2AC8088C1BD346174B851D2EDD046A6303B8BF0A77035EC6A272B247840E1D76` |
| `hotelapp/src/main/java/com/hotelapp/dto/LoginRequest.java` | `EFDA86370176914859F102CAF81BBEC736DDC8EB465C7023544829A497244D30` |
| `hotelapp/src/main/java/com/hotelapp/service/AuthService.java` | `068333799B9FBDEC4F02E2FEABF9E5C64BB0D1935ED1D9B6C9A707170C71B695` |
| `hotelapp/src/main/java/com/hotelapp/validation/PasswordPolicy.java` | `CCB6C866D3DA5A22938E6951B33EDE9D7F3667A1DC2A6974AD4FE1952458394E` |
| `hotelapp/src/main/java/com/hotelapp/controller/ApplicationController.java` | `76CB83AC478A95DAC0BC84A8B9A2D1D035D4B17DB4A4D259E173881C5738EEC7` |
| `hotelapp/src/main/java/com/hotelapp/controller/MessageController.java` | `EA77EFD19302CDB2E1BB3EDBD3CCC85A2DE609763512E48F2B3F5C05A56D8D0B` |
| `hotelapp/src/main/java/com/hotelapp/config/WebSocketConfig.java` | `7DCF41BEA9C98E0B5D712B651122A08F88F71378A288B76B4C77BD8FB7C3627A` |
| `hotelapp/src/main/java/com/hotelapp/security/StompAuthorizationInterceptor.java` | `C59AD11A2961344877E9F0D7027C851F607586E10290DE6E648C88AEF80B7FE1` |
| `hotelapp/src/main/java/com/hotelapp/service/MessageService.java` | `CD34B413E8923412094B58F1852842EFD5FB231DB87BE2182CA0448AAD04D50D` |
| `hotelapp/src/main/java/com/hotelapp/controller/AuthController.java` | `106E4CA7FCE40926DAE5CFCEBE49F92F74275C1FA71AD328F9F453537FF72E6F` |
| `hotelapp/src/main/java/com/hotelapp/controller/PasswordResetController.java` | `D5CD45B1CE0DF2B858740CEBA22A0DE0332CCF4C6F5365C810FC316299349CE1` |

## Findings by advisory path

### Micrometer HTTP server instrumentation — `GHSA-g3pr-3p32-fp23` / CVE-2026-40984

The official Spring advisory states two application preconditions: a vulnerable
Micrometer artifact version, and one or more HTTP server instrumentations from
those artifacts configured with metrics recorded through that instrumentation.
The pinned `micrometer-core:1.12.5` is within the advisory's published affected
range. Spring's page specifically lists Micrometer 1.10.0–1.13.18 among affected
versions, so 1.12.5 is included.

Source evidence shows an active Spring MVC web starter and the Prometheus
registry (`hotelapp/pom.xml:36-40,134-138`), Actuator metrics/prometheus
exposure in the production profile (`application-prod.yml:111-120`), and custom
domain counters registered through `MeterRegistry` (`metrics/AppMetrics.java:15-43`).
The application also protects `/actuator/**` to ADMIN while allowing health
and info (`config/SecurityConfig.java:156-175`). These facts establish metrics
and HTTP server features in the application, but they do **not** prove that the
specific vulnerable Micrometer HTTP server observation is effectively
configured and recording metrics. Custom domain counters and exposure of the
metrics endpoint alone do not establish that condition. No relevant source JAR
was available, and no application context was run.

**Disposition:** version match; application instrumentation applicability
remains unresolved. This is not a confirmed DoS or product vulnerability.
**Smallest next step:** inspect the effective local Boot auto-configuration and
observation registry in the disposable pinned lab; only if the relevant handler
is active should a narrowly bounded request/control check be considered.

### Spring Security X.509 principal extraction — `GHSA-293q-567p-wmwq` / CVE-2026-47838

The GitHub advisory's structured Maven range says
`spring-security-web >=6.0.0, <=6.3.10`, which contains the resolved 6.2.4.
However, its prose affected-version list starts at 6.3.0 and does not include
6.2.x; the official Spring vendor page likewise starts at 6.3.0. The advisory
describes malformed X.509 certificate CN handling in
`SubjectDnX509PrincipalExtractor`, in a pre-authentication flow that assumes
credentials were validated by a trusted upstream.

In the pinned app's `SecurityConfig.java:104-117,141-179,194-207`, authentication
uses its JWT filter/provider and OAuth2 login; no `x509()` security DSL or
X.509 client-certificate flow was found. Source-wide searches of the pinned
`hotelapp/src` and checked deployment/configuration files found no
`SubjectDnX509PrincipalExtractor`, X.509 authentication filter, or client-auth
configuration. The repo's deployment sources were searched, but the actual
deployed proxy/trust configuration is not part of this review.

**Disposition:** the advisory-specific application flow is absent from the
reviewed source/configuration; the exact applicability of 6.2.4 remains
unresolved because the structured range conflicts with both narrative/vendor
version lists. Do not label the dependency record inapplicable or vulnerable
based on this pass. No malformed certificate was created or tested.
**Smallest next step:** resolve the upstream advisory's 6.2.x version discrepancy
from an authoritative clarification; no local product test is indicated unless
the app introduces X.509 pre-authentication.

### BCrypt password length — `GHSA-mg83-c7gq-rv5c` / CVE-2025-22228

The official advisory says `BCryptPasswordEncoder.matches` can return true for
an input longer than 72 characters when the first 72 match, and includes
Spring Security Crypto 6.2.4 in its affected range. The application configures
`BCryptPasswordEncoder` as the `PasswordEncoder` at `config/AppConfig.java:74-75`
and installs it on its DAO authentication provider at lines 53-58.

`dto/LoginRequest.java:8-16` only requires a nonblank password; there is no
maximum length. `controller/AuthController.java:76-83` validates that DTO and
calls `AuthService.login`; `service/AuthService.java:141-157` sends the supplied
password to `AuthenticationManager.authenticate`, whose configured provider
uses BCrypt. `PasswordPolicy.java:22-27` checks only the minimum length and
composition for registration; `AuthService.java:62-82` applies it before
encoding new registration passwords. The same policy has no maximum. The
change-password current-password field is nonblank only and reaches
`passwordEncoder.matches` (`AuthService.java:288-302,313-322`), while reset
confirmation applies a maximum of 128 (`PasswordResetController.java:68-78`).

**Disposition:** source-supported authentication input path with no 72-character
guard in the login/current-password request schemas. This is a plausible lead,
not a reproduced authentication bypass; account state, stored hash, actual
library behavior, and practical conditions were not tested.
**Smallest next step:** in a disposable local database with a synthetic account,
test one known password and one longer input sharing its first 72 characters;
verify the login result without repeated attempts, then evaluate a source fix
and regression test if the behavior is reproduced.

### Spring Data `Sort` parsing — `GHSA-5vpf-xvv7-c8vh` / CVE-2026-41711

The official advisory names a `StackOverflowException`/DoS when parsing Sort
parameters; its prose includes Spring Data Commons 3.2.0–3.2.15, and the pinned
3.2.5 is in range. The application exposes `Pageable` arguments on
`ApplicationController.java:46-51,91-100` and `MessageController.java:54-61,80-88`.
The Spring MVC argument resolver therefore receives request `page`, `size`,
and `sort` values on these endpoints. The application-facing endpoints are
authenticated by `SecurityConfig.java:178-183`, but that does not remove the
request parsing path for an authenticated caller.

**Disposition:** source-supported route to the advisory's parser input; the
exception and availability effect are not reproduced. Source inspection does
not establish effective limits on sort parameter depth/size or resulting
processing cost.
**Smallest next step:** one bounded malformed/deep Sort value to an isolated
local own-app endpoint, with a fixed request timeout and a simple post-request
health check. Do not send repeated or volume traffic.

### Multipart request parsing and Tomcat temporary parts —
`GHSA-cjpg-rgq5-fr37`, `GHSA-h3gc-qfqq-6h8f`,
`GHSA-wr62-c79q-cv37`, `GHSA-hgrr-935x-pq79`

The official Spring Framework advisory covers multipart request smuggling in
Spring MVC, with `spring-webmvc` affected through 6.2.18; pinned Spring MVC
6.1.6 falls within its listed affected line (through 6.1.27). The Tomcat
advisories cover resource allocation/size-limit cases for multipart, an
integer-overflow bypass in some unlikely multipart configurations, and
disk-backed temporary parts left for garbage collection when multipart
processing errors occur. Pinned Tomcat 10.1.20 is in each listed range.

The app enables servlet multipart and configures 20 MB per file / 25 MB per
request in both `application.yml:81-85` and `application-prod.yml:81-85`.
Authenticated upload routes accept `MultipartFile`, including
`MessageController.java:103-115`; `MessageService.java:294-324` passes the
file into storage and retains its metadata. The source also applies a 15 MB
storage limit in the service layer, but that takes effect after servlet
multipart parsing and does not itself prove parser or temporary-file bounds.
The source does not establish effective Tomcat part-count/header limits,
disk-backed temp behavior under parse errors, or the deployment's exact
multipart configuration.

**Disposition:** multipart parsing is a source-confirmed feature path and the
versions match; exact affected parser conditions and availability impact are
unresolved. No malformed multipart body, size-limit bypass, or resource
exhaustion was attempted.
**Smallest next step:** first inspect the effective local multipart/Tomcat
configuration. Any later runtime validation should use a single harmless
boundary request in the disposable local lab; do not probe exhaustion, bypass
limits, or repeat requests.

### Tomcat WebSocket authentication-header redirect — `GHSA-fv25-8xcx-gqjc` / CVE-2026-42498

The official advisory says Tomcat's WebSocket **client** can forward its most
recent authentication header to a redirect target host after an authenticated
WebSocket request is redirected. The application configures a server endpoint
and simple broker (`config/WebSocketConfig.java:31-77`); the STOMP CONNECT
interceptor reads the `Authorization` native header and authenticates it
(`security/StompAuthorizationInterceptor.java:50-95`). A source search found
no outbound Tomcat/Spring WebSocket client setup (`WebSocketClient`,
`StandardWebSocketClient`, or connection manager) in the application.

**Disposition:** the presence of an inbound STOMP Authorization header is not
the advisory's affected client flow. No source-supported path was found from
the app's server-side STOMP configuration to an authenticated outbound Tomcat
WebSocket client redirect. This narrows the app-local applicability question;
it does not cover external components or deployment extensions. No redirect or
credential disclosure was tested.

### Spring RFD follow-up context — `GHSA-6r3c-xf4w-jxjm` / CVE-2025-41234

The prior source review found the conversation attachment filename and bytes
flow into an authenticated download response. The coordinator's separately
recorded local check used an inert body and a non-ASCII marker filename and
observed Spring's encoded `Content-Disposition`; that check did not use active
content or prove browser execution/RFD. This source-path review makes no new
RFD conclusion. The lead remains unconfirmed as recorded in the
[RFD local-check audit](../2026-10-21-a05-rfd-local-check/README.md).

## Evidence classification and roadmap disposition

- **R7/A05:** source/configuration review of selected dependency leads in the
  user's authorized local Kadrom scope. The exact dependency graph and range
  checks are in the linked prior audits; this review adds no dependency scan.
- **Reflection:** not evaluated.
- **Callbacks:** none used or observed.
- **Browser or JavaScript execution:** none performed.
- **Vulnerability triage:** source-backed plausible paths exist for BCrypt,
  Sort, and multipart; Micrometer remains conditional/unresolved; the X.509
  advisory has an explicit version-data conflict and no app X.509 path; the
  Tomcat WebSocket client path was not found. No runtime failure or application
  vulnerability is confirmed, and no general safety claim follows.
- **Agent runtime:** this audit was produced by a delegated generic subagent
  invocation. A native/custom specialist role invocation was not independently
  verified.
- **Tests:** none run in this review. The earlier bounded RFD local check is
  not a test of these other paths.
- **Next work:** prioritize the bounded BCrypt login behavior check, then Sort
  parsing. For multipart and Micrometer, establish effective local
  configuration before considering any behavior check. Resolve the Spring
  Security 6.2.x X.509 advisory discrepancy through authoritative record
  clarification. These are recommendations, not additional testing performed
  or authorization for an external target.

R7/A05 remains open: dependency-advisory matching and source triage do not by
themselves complete product vulnerability triage.

## Official advisory sources

- [Micrometer CVE-2026-40984 — GitHub Advisory](https://github.com/advisories/GHSA-g3pr-3p32-fp23) · [Spring vendor advisory](https://spring.io/security/cve-2026-40984/)
- [Spring Security CVE-2026-47838 — GitHub Advisory](https://github.com/advisories/GHSA-293q-567p-wmwq) · [Spring vendor advisory](https://spring.io/security/cve-2026-47838/)
- [Spring Security CVE-2025-22228 — GitHub Advisory](https://github.com/advisories/GHSA-mg83-c7gq-rv5c)
- [Spring Data CVE-2026-41711 — GitHub Advisory](https://github.com/advisories/GHSA-5vpf-xvv7-c8vh)
- [Spring Framework CVE-2026-41853 — GitHub Advisory](https://github.com/advisories/GHSA-cjpg-rgq5-fr37)
- [Tomcat CVE-2025-48988 — GitHub Advisory](https://github.com/advisories/GHSA-h3gc-qfqq-6h8f) · [CVE-2025-52520](https://github.com/advisories/GHSA-wr62-c79q-cv37) · [CVE-2025-61795](https://github.com/advisories/GHSA-hgrr-935x-pq79)
- [Tomcat CVE-2026-42498 — GitHub Advisory](https://github.com/advisories/GHSA-fv25-8xcx-gqjc)
