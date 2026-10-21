# R7 / A05 Maven dependency GHSA sweep — 21 October 2026

## Scope and source identity

This was a bounded, read-only attempt to check the **direct dependencies whose
versions are explicitly declared in the pinned Kadrom POM**. It did not contact
Kadrom or any product endpoint, and did not submit a report or message anyone.
The pinned source is
[`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`](https://github.com/calsgnkadir/hotel-platform/commit/ae4aebbf8963f550f6bb7c3465fb1270d677af1c);
the reviewed manifest is [`hotelapp/pom.xml`](https://raw.githubusercontent.com/calsgnkadir/hotel-platform/ae4aebbf8963f550f6bb7c3465fb1270d677af1c/hotelapp/pom.xml).

The POM declares these direct Maven dependencies with an explicit version
(including versions supplied through an explicit POM property):

| Maven coordinate | Declared version |
|---|---:|
| `org.apache.poi:poi-ooxml` | `5.3.0` |
| `io.jsonwebtoken:jjwt-api` | `0.12.5` (`jjwt.version` property) |
| `io.jsonwebtoken:jjwt-impl` | `0.12.5` (`jjwt.version` property) |
| `io.jsonwebtoken:jjwt-jackson` | `0.12.5` (`jjwt.version` property) |
| `com.bucket4j:bucket4j-core` | `8.10.1` |
| `io.github.resilience4j:resilience4j-spring-boot3` | `2.2.0` |
| `com.cloudinary:cloudinary-http44` | `1.36.0` |
| `org.springdoc:springdoc-openapi-starter-webmvc-ui` | `2.5.0` |
| `com.iyzipay:iyzipay-java` | `2.0.129` |

Direct dependencies without a version in this POM were omitted, including
Spring Boot starters, MySQL Connector/J, Flyway, Micrometer, Lombok, and test
dependencies. Their effective versions may be inherited from the Spring Boot
parent/BOM or another build mechanism; no effective dependency tree was
resolved here. Transitive dependencies and the product's own SNAPSHOT coordinate
are outside this sweep.

## Method and result

The official [GitHub REST documentation for global security advisories](https://docs.github.com/en/rest/security-advisories/global-advisories?apiVersion=2022-11-28)
documents public unauthenticated access, `ecosystem=maven`, and `affects` values
in the form `package` or `package@version` (documentation lines 17–46). It also
states that the default result set is GitHub-reviewed advisories excluding
malware (lines 22–23, 40). This establishes the general parameter form, not
Maven group/artifact canonicalization behavior.

At **2026-10-21 19:46 UTC**, one combined public API lookup was prepared for the
nine coordinates above, plus the known-positive control
`org.apache.logging.log4j:log4j-core@2.14.1`:

[`GET https://api.github.com/advisories?ecosystem=maven&affects=<10 package@version values>`](https://api.github.com/advisories?ecosystem=maven&affects=org.apache.poi%3Apoi-ooxml%405.3.0%2Cio.jsonwebtoken%3Ajjwt-api%400.12.5%2Cio.jsonwebtoken%3Ajjwt-impl%400.12.5%2Cio.jsonwebtoken%3Ajjwt-jackson%400.12.5%2Ccom.bucket4j%3Abucket4j-core%408.10.1%2Cio.github.resilience4j%3Aresilience4j-spring-boot3%402.2.0%2Ccom.cloudinary%3Acloudinary-http44%401.36.0%2Corg.springdoc%3Aspringdoc-openapi-starter-webmvc-ui%402.5.0%2Ccom.iyzipay%3Aiyzipay-java%402.0.129%2Corg.apache.logging.log4j%3Alog4j-core%402.14.1)

The research tool reported that the `api.github.com` URL was not accessible
through that tool. No HTTP status, body, result count, GHSA ID, or positive
control result was obtained. The query was not retried through another route.
Consequently this run produced **no evaluated GHSA result** for either Kadrom's
dependencies or the positive control.

## Interpretation and status

This is a source-scope inventory plus an **unavailable lookup attempt**, not a
zero-result search. It establishes neither the presence nor absence of a GHSA
for these package versions. The API documentation does not guarantee the exact
normalization of Maven coordinates used in the attempted filter, and the
positive control did not validate live behavior. Unversioned inherited/direct
dependencies, transitive dependencies, unreviewed advisories, malware advisories,
private records, and other databases remain outside this attempt.

**A05 remains partial / inconclusive; R7 remains open.** No vulnerability,
known-record absence, CVE attribution, or product safety conclusion is asserted.
No tests or product requests were run.
