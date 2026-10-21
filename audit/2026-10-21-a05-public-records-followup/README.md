# R7 / A05 Kadrom public-record follow-up — 21 October 2026

## Scope

Read-only check of public records for the selected Kadrom repository,
[`calsgnkadir/hotel-platform`](https://github.com/calsgnkadir/hotel-platform),
anchored to the reviewed product source commit
[`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`](https://github.com/calsgnkadir/hotel-platform/commit/ae4aebbf8963f550f6bb7c3465fb1270d677af1c).
No product endpoint, login, exploit, scan, owner-only/private access, contact,
disclosure, or message was used. No product or toolkit code was changed.

The prior lookup is in
[`2026-10-21-a05-known-records-followup`](../2026-10-21-a05-known-records-followup/README.md).
This follow-up added direct public GETs to official GitHub endpoints. All times
below are UTC; checks ran **2026-10-21 18:48–18:51 UTC**.

## Product identity used for matching

The pinned source's official raw Maven manifest at
[`hotelapp/pom.xml`](https://raw.githubusercontent.com/calsgnkadir/hotel-platform/ae4aebbf8963f550f6bb7c3465fb1270d677af1c/hotelapp/pom.xml)
returned HTTP 200. It identifies:

- Maven group: `com.hotelapp`
- Artifact/name: `hotel-student-platform`
- Version: `0.0.1-SNAPSHOT`
- Parent Spring Boot: `3.2.5`; Java: `17`
- Maven package coordinate: `com.hotelapp:hotel-student-platform:0.0.1-SNAPSHOT`
- Matching PURL form: `pkg:maven/com.hotelapp/hotel-student-platform@0.0.1-SNAPSHOT`

`0.0.1-SNAPSHOT` is the source manifest's development version, not evidence of
a published product release. Matching was therefore tried with the repository
name and with the Maven artifact/package identity; this does not claim that a
public registry contains the artifact.

## Direct official GitHub results

Requests used the public GitHub REST API, `Accept: application/vnd.github+json`,
and a non-authenticated GET client. The returned status and result were:

| Exact URL | HTTP | Observable result |
|---|---:|---|
| [`GET /repos/calsgnkadir/hotel-platform`](https://api.github.com/repos/calsgnkadir/hotel-platform) | 200 | Public repository; default branch `main`; API `open_issues_count=0`. |
| [`GET /issues?state=all&per_page=100`](https://api.github.com/repos/calsgnkadir/hotel-platform/issues?state=all&amp;per_page=100) | 200 | Empty JSON array (`[]`); zero returned issue/PR records for this all-state request. |
| [`GET /releases`](https://api.github.com/repos/calsgnkadir/hotel-platform/releases) | 200 | Empty JSON array (`[]`). |
| [`GET /git/matching-refs/tags`](https://api.github.com/repos/calsgnkadir/hotel-platform/git/matching-refs/tags) | 200 | Empty JSON array (`[]`). |
| [`GET /security/advisories`](https://api.github.com/repos/calsgnkadir/hotel-platform/security/advisories) | 404 | `Not Found`; this endpoint did not expose repository advisory records. It does not prove that no private or otherwise inaccessible advisory exists. |

The public global GitHub Advisory Database API returned HTTP 200 and zero
results for each of these exact filters:

- [`ecosystem=maven&affects=hotel-student-platform`](https://api.github.com/advisories?ecosystem=maven&amp;affects=hotel-student-platform)
- [`ecosystem=maven&affects=hotel-student-platform@0.0.1-SNAPSHOT`](https://api.github.com/advisories?ecosystem=maven&amp;affects=hotel-student-platform%400.0.1-SNAPSHOT)
- [`ecosystem=maven&affects=com.hotelapp:hotel-student-platform`](https://api.github.com/advisories?ecosystem=maven&amp;affects=com.hotelapp%3Ahotel-student-platform)
- [`ecosystem=maven&affects=com.hotelapp:hotel-student-platform@0.0.1-SNAPSHOT`](https://api.github.com/advisories?ecosystem=maven&amp;affects=com.hotelapp%3Ahotel-student-platform%400.0.1-SNAPSHOT)

These are actual successful public API responses, unlike the earlier indexed
searches. They support the narrow statement that those GitHub API filters
returned no matching public GHSA record at the check time. They do not cover
private advisories, unindexed records, other package identities, or all
possible CVE naming/alias forms.

## CVE/NVD routes that remained unavailable

Official NVD API queries were attempted for
[`keywordSearch=hotel-platform`](https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=hotel-platform)
and
[`keywordSearch=calsgnkadir%2Fhotel-platform`](https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=calsgnkadir%2Fhotel-platform).
Both returned HTTP **406** with an NVD web-services/Cloudflare challenge page,
not CVE JSON; the query was therefore not evaluated. The NVD HTML search for
`hotel-student-platform` also returned HTTP 406. A successful NVD result count
was not obtained.

The official [CVE.org search page](https://www.cve.org/CVERecord/SearchResults?query=hotel-student-platform)
returned HTTP 200 with the JavaScript application shell only. No rendered query
results were present in the response body, so this is not a completed CVE.org
search.

## A05 result and closure path

**Known-record status remains partial / inconclusive.** Direct public GitHub
issue, release, tag, and exact Maven-coordinate GHSA endpoints were reachable;
their returned collections were empty. The repository-scoped advisory endpoint
returned 404, and NVD/CVE.org did not return evaluable search results. Do not
convert these limits into “no known record.” The A04 `no-candidate-observed`
result remains restricted to its tested local routes and roles; this lookup
does not change it. No vulnerability or CVE attribution is asserted, and R7
remains open.

The narrow remaining check is to retrieve an official NVD CVE API response in a
client/network that is not blocked by the 406 challenge, querying both
`hotel-student-platform` and `com.hotelapp:hotel-student-platform` and recording
the JSON `totalResults` and returned CVE IDs. If the repository-scoped GitHub
advisory 404 needs clarification, only the repository owner can confirm whether
private advisory records are visible; this audit did not access an owner view.
