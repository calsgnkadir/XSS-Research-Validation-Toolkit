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

The tool returned a cache-miss/inaccessible result for all six. It did not provide origin HTTP status, response headers, JSON, result counts or CVE records. The lookup was not retried. Therefore it adds no public-record evidence and does not change the existing partial/inconclusive disposition in [the identity lookup audit](../2026-10-21-a05-public-records-followup/README.md). No “no record” conclusion is supported.

## Result and remaining R7 disposition

The report now records the new local-remediation authorization while preserving the external-disclosure boundary. The identity question could not be advanced because the official endpoints were not evaluable in this tool session. Existing primary Spring advisory/fix sources and the already recorded product evidence are linked in the report; no new technical source fact was asserted.

The BCrypt application-path defect and Unicode packaged-library behavior remain as previously recorded evidence. This task did not rerun them. The proposed bounded advisory-range/source questions for Actuator and X.509, partial product-identity lookup, and A05 remediation/effective-runtime obligations remain open. R7 is not closed by this documentation/lookup attempt. No tests or CI were run.
