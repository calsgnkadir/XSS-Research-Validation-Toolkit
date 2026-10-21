# R7 records/version and R6 release decision — 21 October 2026

## Starting point and assignments

Starting toolkit commit: `e7b4b7b7425619535b2e74f066a804167574d57e` on
`main`, equal to `origin/main`; the working tree was clean. Two read-only expert
tasks were assigned and completed:

- XSS Security Researcher: R7 Kadrom public record/version lookup. No product
  endpoint, lab, submission, or repository mutation was used.
- QA + Security Lab specialist: A04/A05 acceptance review against the current
  audit, roadmap criteria, source review, and bounded runtime results. No lab,
  HTTP, tests, or files were touched.

The coordinator separately reviewed the R6 candidate and source hashes. No tag,
release, or package publication was attempted.

## R7 — Kadrom public record and version check

The public GitHub repository API reports `main` at
`ba38bd3a5fde6ea57089ab04eb38f58829110096`, one commit beyond the locally tested
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. The intervening commit changes only
`hotel-web/vite.config.js` (`strictPort`); therefore the earlier backend/list
observations remain tied to the parent commit and were not rerun against the
newer source. Primary source links: [current commit](https://github.com/calsgnkadir/hotel-platform/commit/ba38bd3a5fde6ea57089ab04eb38f58829110096),
[repository API](https://api.github.com/repos/calsgnkadir/hotel-platform),
[branches](https://api.github.com/repos/calsgnkadir/hotel-platform/branches).

The repository issue API returned no issues for `state=all`, and the public
metadata reports zero open issues. Matching tag refs and GitHub releases were
empty in the public API results. The Maven manifest declares
`0.0.1-SNAPSHOT`, Spring Boot `3.2.5`, and Java `17`; this is a development build
identity, not a published application release. Sources: [issues API](https://api.github.com/repos/calsgnkadir/hotel-platform/issues?state=all&per_page=100),
[tags API](https://api.github.com/repos/calsgnkadir/hotel-platform/git/matching-refs/tags),
[releases API](https://api.github.com/repos/calsgnkadir/hotel-platform/releases),
[pom.xml](https://github.com/calsgnkadir/hotel-platform/blob/main/hotelapp/pom.xml).

Exact-repository searches on GitHub Advisory Database and NVD did not surface a
matching advisory. The GitHub repository-advisory API was unavailable through
the connector and the advisory page returned a cache miss. This check is
**inconclusive** and does not establish absence of an advisory or CVE.

Roadmap mapping:

- A01 historical Patchstack duplicate and SQLi/CVE statements remain
  author-reported; this repository lookup does not verify them.
- A02 Bludit CVE/version mapping is separate and unchanged.
- A03 no disclosure program or reporting channel was identified or assumed.
- A04 the runtime result remains a two-role list test on the pinned parent
  source. The single newer frontend-only commit does not change that result or
  broaden it to same-role ownership and other endpoints.
- A05 `no-candidate-observed` remains accurate only for the tested routes.
  Known-advisory lookup is still inconclusive.

## R7 — A04/A05 acceptance review

The QA specialist found A04 partially evidenced: clean local demo provenance,
source role guards, owner-filtered list queries, two-role requests, cross-role
403 controls, and unauthenticated 401 controls are recorded in
[`2026-10-21-a04-kadrom`](../2026-10-21-a04-kadrom/README.md). The source review
and runtime evidence do not establish a source-to-sink vulnerability or
security impact. Same-role object ownership and other routes were not tested.
The pinned product release/support version and known advisory check remain
unconfirmed. No independent PoC was warranted because no candidate was
observed. A05's `no-candidate-observed` status is appropriately limited and is
not conflated with valid, invalid, duplicate, or cannot-reproduce.

Smallest follow-up: verify advisory visibility via an authoritative owner view
or available official result, then decide whether to expand the local test to a
same-role ownership comparison. No expansion or product request was made in
this review.

## R6 — tag/publication decision

The prepared distribution remains `dxa-research-toolkit 0.1.0`. The last
accepted wheel, SHA-256
`d1151704ba4c5e6dbe91696f632040ad528947bf97b04dc765b585ef6c3729ad`, passed the
installed-wheel gate 7/7 with nine source/wheel/install module hashes matched
at the 16 October source snapshot (`f4d8bdf50dcdd8fc93814e9d10adcab650a30d5a`).
The retained acceptance records that this was local Windows evidence and that
no release tag/publication occurred.

The current toolkit `HEAD` is later. Since that accepted snapshot,
`tools/dom-xss-analyzer/dxadyn.py` changed to remove unsupported execution/WAF
claims from historical probe descriptions and the HTML report footer. Its
current SHA-256 is
`6864971fbf0bd152bcbffef2a98c6fb783f8397447fabaa8f36c8876c31e509e`; the accepted
wheel's recorded module hash is
`723d527cde9dcd36c0a892604ae48cae6250d6dbc02900f04cad68511a03ebf2`. The other
eight shipped module hashes match the retained acceptance manifest. This means
the accepted wheel is **not** byte-identical to the current packaged source.

The remote `git ls-remote --tags origin` query returned no tag refs. The GitHub
releases and exact PyPI project pages could not be retrieved by the available
browsing source (cache misses), so those pages were not independently verified.
No statement about a current PyPI listing is made from that failed lookup.

**Decision: hold the R6 tag/publication step.** Before proposing a release tag,
rebuild `0.1.0` from the current committed source and rerun the installed-wheel
gate plus tests covering the changed module, then verify the resulting source,
wheel, and installed hashes and current CI result. This review did not run those
tests. Tag creation and external package publication still require the user's
separate explicit release authorization. No tag or package was published.

## Verification and limits

This was repository/document review, hash comparison, Git ref lookup, and two
read-only expert reviews. No local tests, wheel rebuild, Docker, product request,
release workflow, or publication was run. The local toolkit tree remained clean
at the start of review, before this documentation update.
