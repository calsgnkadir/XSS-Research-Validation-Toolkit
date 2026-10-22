# R7 report and authorization follow-up — 22 October 2026

## Scope

Follow-up to the owner-review draft at [research/kadrom-local-triage.md](../../research/kadrom-local-triage.md), within R7/A05. This task owned only that report and this audit. It performed no application request, build, test, Docker action, Git operation or external contact. No multipart work was performed; the user reserved multipart testing for a later follow-up.

## Authorization update

In the current conversation on 22 October 2026, the product owner explicitly authorized the coordinator to remediate identified issues in their Kadrom product, including the BCrypt finding. This supersedes the draft's former statement that separate target-code authorization was still required. The authorization is not evidence of implementation, regression coverage, deployment or acceptance; those remain pending coordinator work. The user separately stated they will handle the multipart test after this conversation.

The authorization does not include external disclosure or messaging. The report continues to state that no maintainer, database or disclosure service was contacted and no channel was selected.

## Bounded identity lookup attempt

To see whether the earlier product-identity gap could be closed without contacting anyone, a single official-source web-tool attempt opened these public URLs:

- `https://github.com/calsgnkadir/hotel-platform`
- `https://api.github.com/repos/calsgnkadir/hotel-platform`
- `https://api.github.com/repos/calsgnkadir/hotel-platform/issues?state=all`
- `https://api.github.com/repos/calsgnkadir/hotel-platform/releases`
- `https://api.github.com/advisories?ecosystem=MAVEN&affects=com.hotelapp%3Ahotel-student-platform%400.0.1-SNAPSHOT`
- `https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=hotel-student-platform`

The tool returned a cache-miss/inaccessible result for all six. It did not provide origin HTTP status, response headers, JSON, result counts or CVE records. A later coordinator follow-up used read-only GitHub REST and OSV API calls with valid query parameters. GitHub returned HTTP 200 for public repository metadata: `calsgnkadir/hotel-platform`, default branch `main`, not archived, pushed on 21 October 2026. Its public issues, releases and tags endpoints returned empty arrays. GitHub's exact Maven package and package-version advisory queries both returned HTTP 200 and zero rows:

- `GET https://api.github.com/advisories?ecosystem=maven&affects=com.hotelapp%3Ahotel-student-platform&per_page=100`
- `GET https://api.github.com/advisories?ecosystem=maven&affects=com.hotelapp%3Ahotel-student-platform%400.0.1-SNAPSHOT&per_page=100`
- `POST https://api.osv.dev/v1/query` with ecosystem `Maven`, package `com.hotelapp:hotel-student-platform`, version `0.0.1-SNAPSHOT`: HTTP 200, `vulns=[]`, query time `2026-10-22T13:33:04Z`.

GitHub's repository security-advisories endpoint returned 404; this is inconclusive and does not establish that private advisories do not exist. No public release or tag identifies the latest supported product version. The exact coordinate is a local Maven artifact identity, and no evidence ties it to a published supported product build. GitHub documents the unauthenticated global advisory endpoint and its `affects` package/package-version filter [here](https://docs.github.com/en/rest/security-advisories/global-advisories).

These results advance the lookup from inaccessible to partially evaluable. They do not establish that the product has no advisories, determine the supported release, or resolve deployed dependency identity. The partial/inconclusive disposition in [the identity lookup audit](../2026-10-21-a05-public-records-followup/README.md) remains appropriate. No “no advisory” conclusion is supported.

## Result and remaining R7 disposition

The report records the local-remediation authorization and preserves the external-disclosure boundary. Exact-coordinate public advisory lookups returned zero rows, but product release identity and private advisory status remain unresolved. Existing primary Spring advisory/fix sources and the already recorded product evidence are linked in the report.

The BCrypt application-path defect and Unicode packaged-library behavior remain as previously recorded evidence. This task did not rerun them. The proposed bounded advisory-range/source questions for Actuator and X.509, identification of a supported product release/effective dependency tree, and A05 runtime obligations remain open. R7 is not closed by this documentation/lookup attempt. No tests or CI were run.
