# R7 / A05 advisory-source follow-up — 21 October 2026

## Scope and source identity

Read-only public advisory research for the selected Kadrom source pinned at
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. The package list below is the nine
direct Maven coordinates with explicit versions already recorded from the
pinned `hotelapp/pom.xml` in the
[prior GHSA sweep](../2026-10-21-a05-ghsa-dependency-sweep/README.md). No
Kadrom endpoint or application was contacted, no dependency was installed or
resolved, and no disclosure, submission, or message was sent.

## Official source and supported search path

GitHub documents its [global security advisory REST API](https://docs.github.com/en/rest/security-advisories/global-advisories?apiVersion=2022-11-28)
as a public, unauthenticated source for global advisories. The endpoint's
documented filters include Maven ecosystem and affected package/version. The
REST endpoint itself was not retried here: direct GitHub API and OSV API calls
in the preceding audits did not produce a trustworthy response in this
environment.

As a materially different transport, I used the available web search tool to
query the official GitHub Advisory Database's indexed HTML records. The same
tool could open an individual official advisory page. This provides an
independent indexed search path and source-page inspection, but it is not a
direct API response and does not expose a complete result count or pagination
state.

## Positive control

At **2026-10-21 20:06–20:08 UTC**, the query
`site:github.com/advisories "org.apache.logging.log4j:log4j-core" "2.14.1"`
returned the official
[GHSA-jfh8-c2jp-5v3q / CVE-2021-44228 advisory](https://github.com/advisories/GHSA-jfh8-c2jp-5v3q).
Its package section names Maven coordinate
`org.apache.logging.log4j:log4j-core` and lists affected versions
`>= 2.13.0, < 2.15.0`; therefore `2.14.1` is covered. The opened page showed
those package/version fields directly. This validates the search route against
the known-positive control, not the completeness of its index.

## Kadrom explicit-version coordinates queried

Each query used the exact coordinate and version in a phrase search scoped to
`github.com/advisories`:

| Pinned POM coordinate | Indexed official-advisory result |
|---|---|
| `org.apache.poi:poi-ooxml:5.3.0` | No exact matching advisory page surfaced in the returned results. |
| `io.jsonwebtoken:jjwt-api:0.12.5` | No exact matching advisory page surfaced in the returned results. |
| `io.jsonwebtoken:jjwt-impl:0.12.5` | No exact matching advisory page surfaced in the returned results. |
| `io.jsonwebtoken:jjwt-jackson:0.12.5` | No exact matching advisory page surfaced in the returned results. |
| `com.bucket4j:bucket4j-core:8.10.1` | No exact matching advisory page surfaced in the returned results. |
| `io.github.resilience4j:resilience4j-spring-boot3:2.2.0` | No exact matching advisory page surfaced in the returned results. |
| `com.cloudinary:cloudinary-http44:1.36.0` | No exact matching advisory page surfaced in the returned results. |
| `org.springdoc:springdoc-openapi-starter-webmvc-ui:2.5.0` | No exact matching advisory page surfaced in the returned results. |
| `com.iyzipay:iyzipay-java:2.0.129` | No exact matching advisory page surfaced in the returned results. |

The tool returned some non-advisory GitHub pages for several searches (for
example, discussions and issues mentioning a dependency); those were not
treated as security advisories. Each executed search used the pattern
`site:github.com/advisories "<group>:<artifact>" "<version>"` for the exact
coordinate in the table. The available web search tool does not expose a
replayable request URL or raw HTTP response for those searches.

## Result and limits

The supported web-search transport successfully surfaced the known-positive
Log4j advisory and its affected Maven version range. It did not surface an
exact matching advisory page for the nine listed Kadrom direct dependencies.
This is an indexed-search observation only. The web tool supplied neither an
authoritative zero-result API response nor a complete total/pagination
boundary; GitHub's index may omit records or use alternate package aliases.
The nine lookups therefore do **not** establish absence of advisories. No
package was matched to an advisory in this pass, and no vulnerability or CVE
claim is made for Kadrom.

At the end of this web-search-only pass, A05 remained inconclusive. The
subsequent deps.dev package-version API results recorded below supersede that
interim known-record status. This web-search pass did not resolve
parent-managed or transitive versions and does not replace an effective
dependency tree.

## References checked

- [GitHub global security advisory REST API documentation](https://docs.github.com/en/rest/security-advisories/global-advisories?apiVersion=2022-11-28): endpoint and supported parameters.
- [GHSA-jfh8-c2jp-5v3q](https://github.com/advisories/GHSA-jfh8-c2jp-5v3q): official positive-control record and Maven affected range.
- [Prior pinned-POM dependency inventory](../2026-10-21-a05-ghsa-dependency-sweep/README.md): source/version basis for nine queried coordinates.

## deps.dev package-version API follow-up

### Documented route and positive control

At **2026-10-21 20:09–20:15 UTC** I checked the official [deps.dev v3 API
documentation](https://docs.deps.dev/api/v3/index.html). It documents
`GET /v3/systems/{system}/packages/{group:artifact}/versions/{version}` as
`GetVersion`, explicitly says it includes known security advisories, supports
Maven, and returns `advisoryKeys[]`. The docs also define Maven names as
`<group ID>:<artifact ID>`. This is a public, package-version lookup.

I also reviewed the official [v3alpha API documentation](https://docs.deps.dev/api/v3alpha/),
which documents `GetFindings` for Maven package versions. It is explicitly an
alpha API. The first request was the documented Maven positive control:

```text
GET https://api.deps.dev/v3alpha/systems/MAVEN/packages/org.apache.logging.log4j%3Alog4j-core/versions/2.14.1:findings
```

The browser web tool's clicked official API example returned JSON at
**2026-10-21 20:10 UTC**. Its parsed `requestedVersion.versionKey` matched
`org.apache.logging.log4j:log4j-core@2.14.1`, with one finding:
`VULNERABLE / RISK_CRITICAL`. `packageFindings` was empty. A direct PowerShell
GET of the same endpoint was separately run after network escalation and
returned the same parsed fields. This positive control allowed proceeding to
the nine coordinates on the same alpha endpoint.

To obtain advisory IDs on the stable route, I then made the stable v3 positive
control request first:

```text
GET https://api.deps.dev/v3/systems/MAVEN/packages/org.apache.logging.log4j%3Alog4j-core/versions/2.14.1
```

The direct PowerShell response parsed as the requested Maven version and
returned seven `advisoryKeys`, including `GHSA-jfh8-c2jp-5v3q`:
`GHSA-3pxv-7cmr-fjr4`, `GHSA-6hg6-v5c8-fphq`, `GHSA-7rjr-3q55-vv33`,
`GHSA-8489-44mv-ggj8`, `GHSA-jfh8-c2jp-5v3q`, `GHSA-p6xc-xr62-6r2g`,
`GHSA-vc5p-v9hr-52mj`. The official GitHub record for the last-mentioned
positive control GHSA is linked above. It confirms the source route returns
parsed advisory identifiers for the known-vulnerable version.

### Stable v3 results for pinned coordinates

After the positive control succeeded, nine public `GetVersion` GET requests
were made with `system=MAVEN`, exact group/artifact name, and the version from
the pinned POM. Each response returned the exact requested `versionKey` and
parsed `advisoryKeys` as follows:

| Coordinate | Returned version | Advisory count | Returned IDs |
|---|---:|---:|---|
| `org.apache.poi:poi-ooxml:5.3.0` | `5.3.0` | 1 | `GHSA-gmg8-593g-7mv3` |
| `io.jsonwebtoken:jjwt-api:0.12.5` | `0.12.5` | 0 | — |
| `io.jsonwebtoken:jjwt-impl:0.12.5` | `0.12.5` | 0 | — |
| `io.jsonwebtoken:jjwt-jackson:0.12.5` | `0.12.5` | 0 | — |
| `com.bucket4j:bucket4j-core:8.10.1` | `8.10.1` | 0 | — |
| `io.github.resilience4j:resilience4j-spring-boot3:2.2.0` | `2.2.0` | 0 | — |
| `com.cloudinary:cloudinary-http44:1.36.0` | `1.36.0` | 0 | — |
| `org.springdoc:springdoc-openapi-starter-webmvc-ui:2.5.0` | `2.5.0` | 0 | — |
| `com.iyzipay:iyzipay-java:2.0.129` | `2.0.129` | 0 | — |

The GETs were made through public PowerShell `Invoke-RestMethod` calls after
the sandboxed request failed with “Unable to connect to the remote server”;
the approved calls returned parseable JSON without caught errors. The script
did not retain per-request HTTP status headers. The individual requests ran
between the **20:09:36 UTC** pre-run clock observation and the **20:15:49 UTC**
post-run clock observation on 21 October 2026; per-request wall-clock
timestamps were not captured, so a more precise request timestamp cannot be
substantiated from this record.

For completeness, the nine earlier alpha `GetFindings` requests also returned
the exact requested package/version keys, with zero `requestedVersion.findings`
and zero `packageFindings` for every coordinate. Those alpha findings were
not used to derive advisory IDs; the stable v3 results above are the source
for the ID counts.

### POI advisory and interpretation

The matching official [GHSA-gmg8-593g-7mv3 record](https://github.com/advisories/GHSA-gmg8-593g-7mv3)
identifies Maven package `org.apache.poi:poi-ooxml`, affected versions `<5.4.0`,
and patched version `5.4.0`. It aliases `CVE-2025-31672`. The pinned direct
POM version `5.3.0` falls within that published affected range. The advisory
describes improper input validation when parsing OOXML files with duplicate
ZIP entry names.

This establishes a **known dependency advisory match** for the pinned direct
POI version. It does not establish that Kadrom reaches the affected parser,
accepts attacker-controlled OOXML, or is exploitable in its deployed
configuration. No application endpoint or input path was tested; do not
promote this package-version match directly to a product vulnerability. It
does give R7 a concrete dependency-triage candidate for source-path and
effective dependency review.

### Source and completeness limits

The stable deps.dev v3 API is documented and returned the package keys and
advisory IDs for both the positive control and nine pinned direct versions.
The alpha `GetFindings` call independently returned a critical vulnerability
classification for the control, but no advisory IDs; the alpha endpoint is
experimental. The stable v3 `GetVersion` result is preferable for this record.
deps.dev describes its data as collected from upstream services such as OSV,
GitHub, and package registries; thus this is a reachable package-version index,
but it is not independent corroboration from each underlying advisory source.
An empty `advisoryKeys` array means deps.dev reported no known direct advisory
for that exact package version at query time; it does not prove universal
absence or cover dependencies of that package version. This lookup initially
covered only the nine explicitly versioned direct POM coordinates. A separate
offline [effective dependency-tree audit](../2026-10-21-a05-effective-dependency-tree/README.md)
later resolved 21 effective direct runtime roots and their transitive graph; a
subsequent [direct-root lookup](../2026-10-21-a05-managed-direct-advisories/README.md)
queried all 21 direct roots. Transitive advisories were not covered by either
lookup at the time this note was written.

**A05 is positive for a known dependency advisory match and remains incomplete
for transitive dependency coverage and product impact triage. R7 remains open.**
No new vulnerability, product exploit, or CVE attribution for Kadrom is claimed.
