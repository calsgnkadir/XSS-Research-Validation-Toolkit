# R7 preparation and K03/K04 follow-up — 20 October 2026

## Scope and starting point

Starting source: `acf7dd2fa74a2fdd1436fd41ddc92a4f3b3e0a9a` (`main`). The working
tree was clean before this follow-up. This delivery is a document/evidence review;
no analyzer, browser, Docker, or product test was run. No external product or
program scope was selected, and no external target was contacted.

## R7 / A01–A03 preparation

- `research/README.md` now labels historical Patchstack duplicate and SQLi/CVE
  stories as author-reported because the matching product/version, PoC, source
  diff, receipt, triage, and CVE attribution are not retained here.
- `research/2026-09-27-cve-hunt-sprint/README.md` is identified as a historical
  plan. Its prior general Patchstack/MITRE route and 90-day language no longer
  imply current program eligibility or a universal disclosure timeline.
- The CERT Polska advisory for [CVE-2026-4420](https://cert.pl/en/posts/2026/04/CVE-2026-4420/)
  names Yassin Abdelrazek and confirms Bludit 3.17.2 and 3.18.0 as tested and
  vulnerable; it says other versions were not tested. Therefore this repository's
  local Bludit 3.16.2 observation does not establish that it matches that CVE and
  does not establish that 3.16.2 is safe. The [NVD entry](https://nvd.nist.gov/vuln/detail/CVE-2026-4420)
  reflects the same tested versions and source attribution. Sources checked
  2026-10-20; they do not authorize testing any product.
- R7 product research remains at preparation pending a selected, authorized
  product/program scope. No CVE or disclosure outcome was added.

## 21 October A03 evidence-label correction

The A04 readiness review found that the historical sprint procedure still
mapped an alert or callback hit directly to `proven-executable` /
`proven-blind`, which conflicts with the current evidence contract. The
procedure now labels CID-matched browser canary evidence as
`execution-observed` and callback-only evidence as `resource-callback`; neither
alone confirms a vulnerability. Role, impact, by-design behavior, and
authorization remain separate triage questions. This was a documentation-only
correction: no target, browser, lab, or product test was run, and no product
scope was selected.

## K03 evidence audit

QA + Security Lab specialist `/root/k03_evidence_check` reviewed the masked
claims against `.dxa/k03_private_capture_20261019.json` without exposing any
secret values, re-running Docker, or changing files. The capture has 17
request/response records; its SHA-256 and `capture_local.js` SHA-256 match the
19 October audit. The SQLi, unsigned JWT, and two-account BOLA summaries match
the local capture and negative controls. For the modified-RS256 control, the
response is HTTP 200 but has no `user.email`; that supports “no identity
returned,” not a claim that the token was rejected with 401. The existing audit
already uses the narrower “identity empty” formulation. Historical sessions,
CVE attribution, and remediation retest remain outside this proof.

Evidence type: local raw-capture review and hash verification, not an independent
lab rerun or Docker-network revalidation. K03 acceptance remains inventory plus
bounded local reproduction.

### 21 October independent QA follow-up

QA + Security Lab specialist `/root/k03_followup_qa` performed a separate,
read-only review. The private capture was present; its SHA-256 matched the
19 October audit and `VALIDATION.md`, and the `capture_local.js` hash matched
as well. Metadata inspection confirmed 17 unique request/response records and
the masked SQLi, unsigned-JWT, BOLA, and negative-control summaries. The
modified-signature control returned HTTP 200 with no `user.email`, supporting
“no identity returned,” not “401/rejected.”

Evidence type: private capture/hash inspection, not a Docker or product rerun.
Historical sessions, CVE attribution, remediation retest, general Juice Shop
behavior, and independent Docker-network provenance remain unverified. No raw
credentials, tokens, or bodies were copied into this audit.

## K04 documentation audit and correction

XSS Security Researcher specialist `/root/k04_defense_review` performed a
read-only review. The documentation-scope acceptance is otherwise supported,
and it correctly states that historical Juice Shop remediations were not
retested. The specialist found two stale claims in
`writeups/01-filtering-is-not-protection.md`: recursive/idempotent sanitizer
application was still recommended at the same time that later sections rejected
it as a general fix; and `textContent` was described as performing HTML escaping.
The coordinator corrected these statements to describe text-node insertion and
to recommend a maintained parser-based allowlist with context-appropriate output
and regression tests. No historical target fix was applied or retested.

## Validation and limits

Documentation review only. `git diff --check` passed; no separate local runtime
or security test suite was run. After delivery, hosted CI for commit `366b01c`
passed its three jobs ([general CI run 39332180912](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/39332180912));
the separate K01 Linux run also passed ([39332180858](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/39332180858)).
K03 capture hashes were checked by the QA specialist. These results do not
establish general Juice Shop behavior, CVE attribution, external program
eligibility, or a new vulnerability.
