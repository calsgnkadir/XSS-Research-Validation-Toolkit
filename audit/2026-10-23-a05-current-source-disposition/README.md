# A05 / R7 — current dependency and source disposition

**Review date:** 2026-10-23  
**Review type:** read-only, selected advisory reconciliation against current source  
**Roadmap:** A05, R7  
**Target:** user-owned `calsgnkadir/hotel-platform`, branch `main`, commit
`b374095344f7b871bbadc4eef571760fd380f9ab`  
**Current source identity:** `b374095344f7b871bbadc4eef571760fd380f9ab`  
**Source used when the 248-coordinate OSV query was made:**
`1276892bd62eab8838ce5a03b877c545cf67da3f`

## Scope and method

This note rechecks the specific A05 candidates recorded in the
[22 October source review](../2026-10-22-a05-remaining-paths/README.md) and
[advisory disposition](../2026-10-22-a05-advisory-disposition/README.md)
against current resolved dependencies and source. It is a bounded reconciliation,
not a complete dependency audit or proof that the application has no
vulnerabilities.

The current checkout and reviewed source identity is `b374095...`.
`hotelapp/pom.xml` is byte-for-byte unchanged from `1276892...`; its SHA-256 is
`f757453d4066791a0b58409133dd9a3d22a6c932b4ad3a7caa3a51b8aa1678b2`. The
saved dependency tree and normalized coordinate-set hashes in the R7 snapshot
also identify the same resolved graph at both source identities. The 248-row
OSV query itself was made against the `1276892...` identity, not rerun at
`b374095...`; unchanged POM and matching saved dependency-tree and coordinate
set hashes establish that its queried dependency graph is the same. The snapshot
queried 248 Maven coordinates (including test scope) against OSV between
`2026-10-23T06:56:43.1698927Z` and `2026-10-23T06:56:44.1002895Z`; it recorded
248 response rows and zero matched rows. Coordinate-set SHA-256:
`e7482dc3fbca7cf7de3c48c2264c4edd388844c36d91c15ff2438ec6d9b61759`;
dependency-tree SHA-256:
`d8ebcd896e982834d66d9d42ea7b1d22b687931da1194b9a47dd751147e7bca5`.
See the [source identity and query record](../2026-10-23-r7-source-identity/README.md)
and its `osv-query.json`. This bounded OSV result is not a full advisory
inventory and says nothing about unpublished, unindexed, product-code, or
deployment-specific issues.

Current relevant Maven coordinates from that graph are:

| Component | Resolved coordinate |
|---|---|
| Spring Boot parent / Actuator | `org.springframework.boot:spring-boot-starter-parent:4.1.1`; `spring-boot-starter-actuator:4.1.1` |
| Spring Security | `spring-security-web`, `spring-security-config`, `spring-security-core`: `7.1.1` |
| Micrometer | `micrometer-core`, `micrometer-observation`, `micrometer-registry-prometheus`: `1.17.1` |
| Spring Data | `org.springframework.data:spring-data-commons:4.1.1` |
| Spring MVC | `org.springframework:spring-webmvc:7.0.9` |
| Tomcat embedded | `tomcat-embed-core`, `tomcat-embed-el`, `tomcat-embed-websocket`: `11.0.27` |

The values are resolved coordinates, not an independent rerun of Maven at
`b374095`. No build, test, Docker, application, malformed-request, or runtime
operation was performed for this review. Current source line references below
are relative to the target checkout.

## Candidate-by-candidate disposition

| Lead | Old candidate and current version comparison | Published affected range / needed conditions | Current disposition |
|---|---|---|---|
| Actuator authentication bypass, CVE-2026-22733 | Old Boot `3.2.5`; now Boot/Actuator `4.1.1` | Spring lists Boot `4.0.0–4.0.3`, `3.5.x`, `3.4.x`, `3.3.x`, and `2.7.31 and earlier`. Exploitation also requires a web app with Actuator and Spring Security plus an authenticated application endpoint beneath the Cloud Foundry Actuator path. | The old version-match concern is superseded: `4.1.1` is outside the published affected ranges. Current source still has Actuator and Spring Security (`hotelapp/pom.xml:11,149`; `SecurityConfig.java:104`), but a source search found no `cloudfoundryapplication` mapping. This source condition was not runtime-verified. No current CVE-2026-22733 finding is supported by the version or searched route evidence. |
| X.509 principal extraction, CVE-2026-47838 | Old Security `6.2.4`; now Security `7.1.1` | Spring's affected list is `6.5.0–6.5.10`, `6.4.0–6.4.17`, `6.3.0–6.3.17`, `5.8.0–5.8.26`, and `5.7.24 and earlier`. The bug concerns malformed certificate CN handling in `SubjectDnX509PrincipalExtractor`; the pre-authentication flow assumes a trusted upstream already validated the certificate. | The old `6.2.4` discrepancy between a structured range and Spring's prose list is moot for this current graph: `7.1.1` is outside the vendor's listed ranges. Current source search found no `x509`/`SubjectDnX509PrincipalExtractor` use under `hotelapp/src/main` and no client-certificate flow in the checked app source. Deployment-side trust configuration was not reviewed. No certificate was constructed or tested. |
| Micrometer HTTP instrumentation DoS, CVE-2026-40984 | Old Micrometer `1.12.5`; now core/observation/Prometheus registry `1.17.1` | Spring lists affected Micrometer `1.16.0–1.16.5`, `1.15.0–1.15.11`, `1.14.0–1.14.15`, `1.10.0–1.13.18`, and `1.9.17 and earlier`. In addition to a vulnerable artifact, a listed HTTP server instrumentation must be configured and recording metrics. | The old version match is superseded: `1.17.1` is outside the vendor-published affected ranges. Earlier local diagnostics found HTTP instrumentation/metric recording, which is relevant only when the dependency version also falls in range; it does not restore applicability at `1.17.1`. No current DoS behavior was tested. |
| Crafted Sort DoS, CVE-2026-41711 | Old Spring Data Commons `3.2.5`; now `4.1.1` | Spring lists `4.0.0–4.0.5`, `3.5.0–3.5.11`, `3.4.0–3.4.14`, `3.0.0–3.3.16`, and `2.7.19 and earlier`. DoS requires an exposed endpoint that passes untrusted `Sort` without sanitization, or applicable `@ProjectedPayload`/`@QuerydslPredicate` use. | The old version lead is superseded: `4.1.1` is beyond the listed affected branches. Current source does expose `Pageable` parameters in application/message controllers (`ApplicationController.java:51,99`; `MessageController.java:59–60,86–87`), so input handling remains worth checking independently. Historical observation on `3.2.5` was one malformed property returning HTTP 500, without a `StackOverflowError`; it did not reproduce the advisory DoS. A separate current-source 500-to-400 regression change is in progress; it is not evidence of CVE-2026-41711 applicability. |
| Multipart size-limit DoS, CVE-2025-48988 | Old Tomcat `10.1.20`; now embedded Tomcat `11.0.27` | GitHub Advisory Database lists Tomcat 11.0.0-M1 through 11.0.7 (fixed in 11.0.8). | Current `11.0.27` is beyond the published affected range. The source sets 20 MB file and 25 MB request limits (`application.yml:82–85`; `application-prod.yml:82–85`), but config values are not a parser-specific runtime test. |
| Multipart size-limit bypass, CVE-2025-52520 | Old Tomcat `10.1.20`; now `11.0.27` | Affected Tomcat 11.0.0-M1 through 11.0.8 (fixed in 11.0.9); the advisory describes DoS under some unlikely multipart configurations. | Current `11.0.27` is beyond the published affected range. No malformed upload was sent and no effective connector or proxy behavior was tested in this review. |
| Multipart temporary-copy cleanup, CVE-2025-61795 | Old Tomcat `10.1.20`; now `11.0.27` | Affected Tomcat 11 versions before 11.0.12; advisory concerns temporary multipart copies not being promptly removed after upload-processing errors. | Current `11.0.27` is beyond the published affected range. Whether the deployment's parser/temp-file behavior is correct under failure remains outside this version reconciliation and was not tested. |
| WebSocket redirect authentication-header exposure, CVE-2026-42498 | Old Tomcat `10.1.20`; now Tomcat `11.0.27` | Affected Tomcat 11 versions below 11.0.22; issue requires an authenticated WebSocket-client request redirected to another host. | Current `11.0.27` is beyond the published affected range. This does not establish whether application or deployment code uses the vulnerable client behavior; no redirect test was performed. |

The old A05 records sometimes mention `10.1.20` because that was the then-pinned
Tomcat line. Those old coordinates must not be carried forward as current
dependency findings: the current resolved embedded Tomcat is 11.0.27.

## Summary and remaining boundary

For these selected advisory leads, the prior Boot 3.2.5, Security 6.2.4,
Micrometer 1.12.5, Spring Data 3.2.5, and Tomcat 10.1.20 version matches do not
describe the current resolved graph. Current versions fall outside the cited
vendor/advisory ranges. This is a scoped version disposition; it is not a
blanket security conclusion. Source preconditions and runtime behavior remain
separate evidence: Sort-accepting endpoints exist; multipart limits are
configured but parser cleanup and proxy behavior are unverified; Actuator and
Security are present but no Cloud Foundry path was found; and no X.509 flow was
found in checked app source. The earlier `HTTP 500` Sort observation is a
separate error-handling regression lead.

The narrow next step for A05 is to record the separate Sort input-boundary
regression result against the current source, and let the user perform the
planned malformed multipart test. Neither result should be upgraded to a CVE
finding unless its advisory's version and behavioral preconditions match.
Roadmap disposition: **A05 remains partial** because malformed-parser cleanup
and other runtime/source preconditions remain unverified. **Bounded local R7
research is complete**: the exact current source identity is recorded, the
248-coordinate advisory query is bound to a matching saved dependency graph,
and no public release/tag or formal support policy was found, so the target is
recorded as a source snapshot rather than a supported release. That identity
result is not evidence that advisories are absent, that the code is safe, or
that a production graph was inspected. External contact or disclosure is not
part of this local disposition.

## Authoritative advisory references

Public pages were retrieved on 2026-10-23; retrieval time for this review was
08:46 UTC. These links support the stated version ranges and conditions:

- [Spring CVE-2026-22733: Actuator Cloud Foundry authentication bypass](https://spring.io/security/cve-2026-22733/)
- [Spring CVE-2026-47838: X.509 principal extraction](https://spring.io/security/cve-2026-47838/)
- [Spring CVE-2026-40984: Micrometer HTTP server instrumentation DoS](https://spring.io/security/cve-2026-40984/)
- [Spring CVE-2026-41711: crafted Sort parameters](https://spring.io/security/cve-2026-41711/)
- [GitHub Advisory GHSA-h3gc-qfqq-6h8f / CVE-2025-48988](https://github.com/advisories/GHSA-h3gc-qfqq-6h8f)
- [GitHub Advisory GHSA-wr62-c79q-cv37 / CVE-2025-52520](https://github.com/advisories/GHSA-wr62-c79q-cv37)
- [GitHub Advisory GHSA-hgrr-935x-pq79 / CVE-2025-61795](https://github.com/advisories/GHSA-hgrr-935x-pq79)
- [GitHub Advisory GHSA-fv25-8xcx-gqjc / CVE-2026-42498](https://github.com/advisories/GHSA-fv25-8xcx-gqjc)
- [GitHub Advisory GHSA-5vpf-xvv7-c8vh / CVE-2026-41711](https://github.com/advisories/GHSA-5vpf-xvv7-c8vh)
