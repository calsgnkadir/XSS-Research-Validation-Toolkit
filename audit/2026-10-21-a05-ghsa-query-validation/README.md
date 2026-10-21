# R7 / A05 GitHub Advisory query-method validation — 21 October 2026

## Scope

Read-only method validation of the global GitHub Advisory Database endpoint
queries recorded in the
[Kadrom public-record audit](../2026-10-21-a05-public-records-followup/README.md).
No product endpoint was accessed and no disclosure or contact was made.

## Official API documentation

GitHub's [REST documentation for global security advisories](https://docs.github.com/en/rest/security-advisories/global-advisories?apiVersion=2022-11-28)
documents `GET /advisories` as public-resource accessible without
authentication (API-versioned doc, lines 17–34). It lists `ecosystem` as a
supported query parameter with `maven` as an allowed value (line 42), and
`affects` as a supported filter for `package` or `package@version` (line 46).
Thus the **parameter names and general filter form** used in the previous
Kadrom queries are supported by the documented endpoint.

The docs describe generic package strings; they do not establish how every
Maven group/artifact spelling or a PURL is normalized for matching. The prior
queries tested bare artifact names and `group:artifact` spellings, with and
without the development version. A PURL was not sent as an `affects` value.
Do not treat those spellings as a canonicalization guarantee.

The same documentation says the endpoint defaults to GitHub-reviewed
advisories and excludes malware (lines 22 and 40). Since the prior requests
did not specify `type=unreviewed` or `type=malware`, their empty responses
cover only the endpoint's default reviewed, non-malware result set.

## Optional positive-control request

One public GET positive-control query for a known Maven advisory package was
attempted at **2026-10-21 19:16:59 UTC**:

`https://api.github.com/advisories?ecosystem=maven&affects=log4j-core`

The client could not connect to the remote server before receiving an HTTP
response. HTTP status, response body, count, and GHSA IDs are unavailable.
The control therefore **did not validate live endpoint behavior** in this
session. No retry or alternate control query was made.

## Interpretation

The official docs confirm that `ecosystem=maven` and `affects=package` or
`package@version` are supported filters. The positive control could not be
evaluated. The prior Kadrom queries were recorded as HTTP 200 with zero results
for their specified values; this method check does not expand those results to
other package spellings, unreviewed advisories, malware advisories, private
records, or CVE records outside GitHub's database. It does not establish that
Kadrom has no GHSA, CVE, or known vulnerability. **A05 remains
partial/inconclusive and R7 remains open.**
