# R7 public advisory lookup — 21 October 2026

## Scope and method

Read-only public-record lookup for the selected repository/product
`calsgnkadir/hotel-platform`. No owner account, maintainer contact, product
endpoint, lab, submission, or repository change was used. The lookup was
performed by the XSS Security Researcher specialist, with the coordinator
recording its result.

At 2026-10-21 14:28 UTC, exact-name search terms were:

- `site:github.com/advisories "calsgnkadir/hotel-platform"`
- `site:github.com/advisories "calsgnkadir"`
- `site:nvd.nist.gov/vuln/detail "calsgnkadir/hotel-platform"`
- `site:nvd.nist.gov/vuln/detail "calsgnkadir"`

No exact matching advisory/CVE result surfaced in those indexed searches. The
search results exposed no reliable total, so an empty result is not proof that
the databases contain no record.

Direct attempts to open the GitHub Advisory Database query
`https://github.com/advisories?query=calsgnkadir%2Fhotel-platform`, the
repository security advisory page, NVD API keyword queries for
`calsgnkadir/hotel-platform` and `hotel-platform`, and GitHub's global
advisories API were inaccessible through the available browser connector
(cache miss / inaccessible response). No authoritative exhaustive result was
retrieved.

## Result and roadmap mapping

**Known-record result: inconclusive.** Do not state that Kadrom has no advisory
or CVE. The bounded public search attempt is recorded; A04/A05 runtime evidence
and the `no-candidate-observed` result remain limited to the already tested
list/role routes. R7 remains open for authoritative known-record verification.

The earlier public repository issue/tag/version review and limits are in the
[R7/R6 decision audit](../2026-10-21-r7-r6-decision/README.md). No local test
or product request was made for this lookup.
