# R7 / A05 Kadrom known-record follow-up — 21 October 2026

## Scope and starting record

Bounded public-record lookup for the selected repository
[`calsgnkadir/hotel-platform`](https://github.com/calsgnkadir/hotel-platform),
anchored to the locally reviewed product commit
[`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`](https://github.com/calsgnkadir/hotel-platform/commit/ae4aebbf8963f550f6bb7c3465fb1270d677af1c).
The previous known-record attempt is recorded in
[`2026-10-21-r7-advisory-lookup`](../2026-10-21-r7-advisory-lookup/README.md)
and the broader A04/A05 assessment in
[`2026-10-21-r7-r6-decision`](../2026-10-21-r7-r6-decision/README.md).

No product endpoint was requested. No code was tested, no exploit or broad
search was performed, and no disclosure, submission, or message was sent.

## Lookup

Checked on **2026-10-21, 18:26–18:28 UTC** using direct URL opens through the
available web source and exact-name indexed queries.

Official GitHub API URLs attempted:

- Repository metadata: <https://api.github.com/repos/calsgnkadir/hotel-platform>
- All repository issues: <https://api.github.com/repos/calsgnkadir/hotel-platform/issues?state=all&per_page=100>
- Repository releases: <https://api.github.com/repos/calsgnkadir/hotel-platform/releases>
- Matching tag refs: <https://api.github.com/repos/calsgnkadir/hotel-platform/git/matching-refs/tags>
- Repository security advisories: <https://api.github.com/repos/calsgnkadir/hotel-platform/security/advisories>

Official NVD API URLs attempted:

- Exact product-name keyword: <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=hotel-platform>
- Exact owner/repository keyword: <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=calsgnkadir%2Fhotel-platform>

The web source returned **“URL … is not accessible via this tool”** for each
direct GitHub/NVD API URL, including the correctly formed all-issues query. It
did not return HTTP status codes or API response bodies. These attempts provide
no evidence about whether an advisory, CVE, issue, release, or tag is present.

Supplementary indexed queries were:

- `site:github.com/advisories "calsgnkadir/hotel-platform"`
- `site:github.com/advisories "hotel-platform"`
- `site:nvd.nist.gov/vuln/detail "calsgnkadir/hotel-platform"`
- `site:nvd.nist.gov/vuln/detail "hotel-platform"`

The combined search response showed generic hotel-platform pages and unrelated
repositories, but no exact matching advisory/CVE result. The search interface
provided no reliable result total; this is not an exhaustive primary-source
lookup.

## Result and limits

**Known-record status: inconclusive.** The official APIs could not be read, and
the supplementary indexed search did not establish a complete result set. Do
not infer that the repository has no issue, advisory, or CVE. This lookup does
not change the prior A05 outcome: `no-candidate-observed` remains limited to
the previously tested local list/role routes. It is not evidence of product
security or absence of known records. No new vulnerability or CVE attribution
is made.

Closure requires a successful public official API/result retrieval, or an
authoritative owner-view result if the advisory is private. No authentication,
owner account, or contact was attempted in this follow-up.
