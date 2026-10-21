# R7 / A05 NVD UI follow-up — 21 October 2026

## Scope

One alternate official route was attempted: the NVD vulnerability search UI,
queried for the exact Maven artifact name `hotel-student-platform`, matching
the pinned Kadrom source `ae4aebbf8963f550f6bb7c3465fb1270d677af1c` and POM
coordinate `com.hotelapp:hotel-student-platform:0.0.1-SNAPSHOT`.

At **2026-10-21 19:15 UTC**, the web retrieval tool was given this URL:

`https://nvd.nist.gov/vuln/search/results?form_type=Basic&results_type=overview&query=hotel-student-platform&search_type=all&isCpeNameSearch=false`

The tool did not return a rendered result page, HTTP status, or result count.
Its subsequent diagnostic for the same NVD UI route said the URL was not
accessible via the tool. No query result was evaluated and no CVE IDs were
retrieved. The retrieval interface exposes no HTTP status for this attempt.

## Result and limits

This is an access limitation, not an empty NVD search result. It does not
repeat the earlier NVD API request or OSV request; no further route or retry
was attempted. No attribution, CVE match, or absence of known records is
asserted. A05 remains partial/inconclusive and **R7 remains open** pending a
retrievable authoritative result. No product endpoint, login, test, scan,
message, or submission was used.
