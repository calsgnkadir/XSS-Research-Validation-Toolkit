# R7 / A05 — OSV Maven dependency sweep

## Scope and source

Read-only public-record lookup against the official OSV API for directly
declared Maven dependencies with explicit versions in the pinned Kadrom source
POM at `.dxa/a04-kadrom-source/hotelapp/pom.xml` (source commit
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`). No Maven resolution, dependency
tree, product endpoint, product test, disclosure, or contact was performed.

The POM pins these nine direct coordinates:

| POM location | Maven coordinate queried |
|---|---|
| lines 29–32 | `org.apache.poi:poi-ooxml:5.3.0` |
| lines 98–100; property `jjwt.version` at line 23 | `io.jsonwebtoken:jjwt-api:0.12.5` |
| lines 103–105; property `jjwt.version` at line 23 | `io.jsonwebtoken:jjwt-impl:0.12.5` |
| lines 109–111; property `jjwt.version` at line 23 | `io.jsonwebtoken:jjwt-jackson:0.12.5` |
| lines 117–119 | `com.bucket4j:bucket4j-core:8.10.1` |
| lines 125–127 | `io.github.resilience4j:resilience4j-spring-boot3:2.2.0` |
| lines 142–144 | `com.cloudinary:cloudinary-http44:1.36.0` |
| lines 149–151 | `org.springdoc:springdoc-openapi-starter-webmvc-ui:2.5.0` |
| lines 192–194 | `com.iyzipay:iyzipay-java:2.0.129` |

The first column refers to the POM line numbers; the `jjwt.version` property
resolves explicitly to `0.12.5`. Dependencies whose versions are inherited
from the Spring Boot parent/BOM, test-only dependencies without explicit
versions, plugin dependencies, and transitive dependencies were excluded.

## Query method

OSV's official [`POST /v1/querybatch` documentation](https://google.github.io/osv.dev/post-v1-querybatch/)
describes batching multiple package/version lookups, ordered results, and
versioned package URLs. One bounded batch payload contained the nine PURLs
above and this known-positive control:

`pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1`

The request target was `https://api.osv.dev/v1/querybatch`; content type was
`application/json`. The version was included in each PURL, without a second
top-level `version` field, consistent with the official
[`POST /v1/query` version rules](https://google.github.io/osv.dev/post-v1-query/).
The public API request was attempted once in the sandbox and the same bounded
payload was attempted once more after requesting escalated network access.
No retry with the earlier exact product PURL was made.

## Result

- Sandbox attempt: PowerShell `Invoke-WebRequest` reported “Uzak sunucuya
  bağlanılamıyor” (“Unable to connect to the remote server”). No HTTP status or
  response body was obtained.
- Escalated attempt: the command ended in a PowerShell `NullReferenceException`
  while its error/status extraction ran. The HTTP status, response JSON, result
  count, IDs, and pagination state were not captured. This is not a parsed OSV
  response and cannot be counted as an empty result.
- The positive control therefore did not validate successful endpoint access or
  OSV's Maven-coordinate matching on this run.

## Status and limits

This sweep is **inconclusive**. It establishes neither an advisory match nor
the absence of OSV records for these exact versions. Query coverage is limited
to the nine direct dependencies that have explicit versions in this POM; it
does not cover inherited/BOM versions, transitive dependencies, alternate
coordinates, or other vulnerability databases. No vulnerability conclusion
or product finding is made. A05 known-record verification and R7 remain open.

The API method and payload rules were checked against the linked official OSV
documentation on 2026-10-21. No application test was run.
