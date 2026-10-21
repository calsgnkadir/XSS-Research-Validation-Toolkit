# R7 / A05 CVEProject alternate-source review — 21 October 2026

## Scope and local product metadata

Read-only assessment of whether an official CVEProject source provides an
accessible, documented package-level lookup for the selected Kadrom Maven
dependencies. No Kadrom endpoint was requested; no disclosure, contact, scan,
or product test occurred. No CVE query was submitted because an official,
documented Maven package-query route could not be established.

The local cached Kadrom source is pinned at
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. Its
[pinned hotelapp/pom.xml](https://raw.githubusercontent.com/calsgnkadir/hotel-platform/ae4aebbf8963f550f6bb7c3465fb1270d677af1c/hotelapp/pom.xml) declares
Spring Boot parent `3.2.5`, Java `17`, and explicit dependency versions
including `org.apache.poi:poi-ooxml:5.3.0`, `io.jsonwebtoken:jjwt-*` via
`0.12.5`, `com.bucket4j:bucket4j-core:8.10.1`,
`io.github.resilience4j:resilience4j-spring-boot3:2.2.0`,
`com.cloudinary:cloudinary-http44:1.36.0`,
`org.springdoc:springdoc-openapi-starter-webmvc-ui:2.5.0`, and
`com.iyzipay:iyzipay-java:2.0.129`. Several Spring Boot, MySQL, Flyway, and
test dependencies omit direct versions and inherit dependency management;
this review did not resolve an effective dependency tree or inspect
transitive versions.

## Official source and documented schema

The CVE Program's [13 October CVE Search API announcement](https://www.cve.org/Media/News/item/blog/2026/10/13/CVE-Search-API)
describes a beta public search service without authentication and links to
Swagger documentation. The available page view returned only the JavaScript
application shell, so the linked Swagger document and its deployed base URL
could not be retrieved or verified in this session.

The official [CVEProject/CVE-Search-API source documentation](https://github.com/CVEProject/CVE-Search-API)
describes an API that searches CVE records in an existing OpenSearch index.
Its documented `/search` schema supports CVE metadata filters, free-text
`keywordSearch`, and CPE applicability filters such as `cpeName` and
`virtualMatchString`. It explains that `keywordSearch` searches the selected
CNA/ADP **description text**, while CPE matching operates on CVE CNA CPE
applicability data. It does not document a Maven ecosystem, PURL, or Maven
group/artifact/version query field. The repository's run instructions require
an existing OpenSearch deployment supplied by the operator; they do not
identify the beta service's public hostname. Thus this source-level schema
does not establish a supported package-level query for Kadrom's Maven
coordinates.

The CVEProject [cvelistV5 repository](https://github.com/CVEProject/cvelistV5)
is identified by CVEProject as a cache/bulk distribution of official CVE JSON
records. Its bulk-download role is not a package-level query API. No bulk
download or broad local corpus scan was performed.

## Access check and outcome

At **2026-10-21 19:26 UTC**, the official announcement and CVEProject API
source documentation were inspected through the available web reader. The
announcement's Swagger destination was not exposed by the JavaScript-only
page; no documented public base URL or package-query schema could therefore
be confirmed. No endpoint request or positive-control request was made, and
there is no HTTP status, result count, or CVE ID to report. This is a
documentation/access limitation, not an empty search result.

This review neither confirms nor excludes CVE records for Kadrom or its
dependencies. Earlier GitHub, NVD, OSV, and UI lookup results retain only their
previously documented narrow meanings. **A05 remains partial/inconclusive and
R7 remains open.**
