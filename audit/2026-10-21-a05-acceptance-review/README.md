# R7 / A05 independent acceptance review — 21 October 2026

## Scope

Independent, read-only acceptance review of the A05 evidence recorded on
2026-10-21. Scope is the pinned, user-owned Kadrom source at
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`, its resolved Maven compile/runtime
graph, public advisory metadata, and source triage. No source, product endpoint,
application runtime, test suite, Docker service, or disclosure was exercised in
this review. No test or build result is claimed here.

## Acceptance assessment

**A05 is materially advanced but remains open.** The effective graph and
positive-controlled deps.dev lookups support a complete bounded lookup of the
resolved compile/runtime Maven coordinates available from the local Maven
cache: 21 direct roots and 127 unique transitive coordinates returned exact
version keys. The transitive pass found advisory keys on 18 coordinate/version
rows (93 package-to-key associations, 92 distinct IDs). This is meaningful
known-record index evidence; it is not a product vulnerability finding, a
complete advisory-database guarantee, or a safety result for rows with zero
keys.

The direct-key follow-up establishes one clear package/version range match for
`poi-ooxml:5.3.0` against GHSA-gmg8-593g-7mv3 / CVE-2025-31672. The source
review found only generated-workbook creation and no path from user-provided
OOXML into a POI parser in the pinned snapshot. The Actuator starter key is a
GitHub range match at 3.2.5, but Spring's vendor release list omits 3.2.x and
the required protected `/cloudfoundryapplication/...` route was not found in
source. Neither is a confirmed Kadrom vulnerability; Actuator applicability
remains unresolved.

No equivalent affected-range review or product-source triage is recorded for
the 92 distinct transitive advisory IDs. The public product-identity searches
also remain partial: GitHub's four exact Maven filters returned empty
collections, but NVD returned a 406 challenge, CVE.org returned only an
unrendered app shell, and the OSV request failed before an HTTP response. These
are bounded outcomes, not evidence that Kadrom has no product-level record.

## Evidence reviewed

- `ROADMAP.md`, R7/A05 current snapshot and acceptance rows (lines 87–98,
  232–235, 265, 309, 835–845). The A05 row at line 843 defines the relevant
acceptance evidence; R7 remains open pending a bounded product/role result and
honest triage.
- `STATUS.md`, current top block (lines 35–54), and dated A05 follow-ups.
- `audit/2026-10-21-a05-effective-dependency-tree/README.md`, “Effective
  direct runtime roots”, “Filtered Actuator subtree follow-up”, and
  “Exclusions and status”: pinned POM hash, offline BUILD SUCCESS, 21 roots,
  and the 3-artifact Actuator path. No application build/test is claimed.
- `audit/2026-10-21-a05-managed-direct-advisories/README.md`, “Positive
  control” and “Direct runtime-root responses”: 21/21 exact keys, two nonzero
  roots, and explicit limits on zero keys.
- `audit/2026-10-21-a05-transitive-advisories/README.md`, “Positive control”
  and “Runtime tree extraction and lookup result”: successful control,
  127/127 exact returned keys, zero API errors/mismatches, 18 rows with keys,
  93 associations and 92 distinct IDs. The complete table records the
  package/version rows and returned key lists. This is a completed metadata
  lookup, not a completed range or product-impact triage.
- `audit/2026-10-21-a05-advisory-range-review/README.md`, “Results” and
  “Source comparison and limits”: POI range match and unresolved Spring
  vendor/GHSA disagreement.
- `audit/2026-10-21-r7-poi-source-triage/README.md`, “Source flow” and
  “Assessment”: generated XLSX flow; no parser of attacker-provided OOXML
  found in reviewed source; source review only.
- `audit/2026-10-21-r7-actuator-source-triage/README.md`, “Endpoint exposure
  and authorization in source” and “Assessment and limits”: route precondition
  not found in pinned source; runtime route table/profile/reachability not
  validated.
- `audit/2026-10-21-a05-public-records-followup/README.md`, “Direct official
  GitHub results” and “CVE/NVD routes that remained unavailable”; and
  `audit/2026-10-21-a05-osv-followup/README.md`, “Result”: exact public GHSA
  filter results were empty, while NVD/CVE.org/OSV did not produce evaluable
  search results.
- `audit/2026-10-21-a05-cveproject-alternate-followup/README.md`, “Official
  source and documented schema” and “Access check and outcome”: no documented
  public Maven/PURL query route was established; no query was submitted.

## Stale progress statements to reconcile

The newest A05 snapshot at `ROADMAP.md:87–98` still says the 127 transitive
queries “are running”. It should say the lookup completed and summarize its
counts, while retaining the open range/source triage status. The status table
at `ROADMAP.md:232`, current-evidence row at `:265`, R7 row at `:309`, and A05
acceptance row at `:843` also say the transitive lookup is ongoing. Those are
the active summaries that need reconciliation with the completed audit.

`STATUS.md:35–54` is the current top block but still states that the transitive
scan is open as the next step. It should record 127/127 exact index responses,
18 nonzero rows, 93 associations/92 IDs, then name affected-range and source
triage as the next gate. Earlier dated paragraphs in ROADMAP/STATUS that report
an earlier lookup attempt as inconclusive are historical snapshots; retain
their dates and do not rewrite them as if the earlier attempts succeeded.

## Remaining A05 acceptance criteria

1. Review advisory metadata for the 18 nonzero transitive package/version rows
   (93 returned associations; deduplicate the 92 IDs), capture the advisory's
   package identity and affected/fixed ranges from a primary record, and
   compare each range with the exact resolved version. Separate aliases and
   duplicate IDs from distinct package records. Do not call an index key an
   affected-version match until the range is checked.
2. For transitive coordinates with confirmed range matches, inspect only the
   relevant application source paths/configuration and record any documented
   preconditions. If no plausible input or reachable feature path exists in
   the pinned source, record that bounded absence; do not run a product test
   solely because an advisory key exists.
3. Resolve or preserve as explicitly unresolved the direct Actuator GHSA vs
   Spring-vendor 3.2.x discrepancy. Product applicability cannot be declared
   without authoritative version clarification; source absence of the route
   condition is not runtime proof.
4. Keep public product-identity lookup status partial/inconclusive until an
   authoritative, evaluable result is available for the product identity.
   Empty exact GitHub GHSA filters and failed/challenged sources do not support
   “no known record”. No owner-only access, contact, or disclosure is implied.
5. Update ROADMAP/STATUS current snapshots, then state the bounded outcome
   against A05's Roadmap acceptance row. A05 is not accepted merely because
   the dependency graph and index lookups completed.

## Smallest next step

Create a compact range-triage matrix from the 18 nonzero transitive rows in the
existing transitive audit: for each distinct GHSA ID, record the affected Maven
package, authoritative range/fix, exact resolved version(s), range-match
result, and source URL. Deduplicate repeated IDs without losing all package
associations. This is metadata-only work, requires no rerun of the Maven tree
or product, and will identify the smallest set of dependencies that need
source-path review. Then send only confirmed range matches to targeted source
triage. Keep A05 and R7 open until that bounded matrix and product-identity
limitations are reflected in the current status.

**Disposition:** current A05 claim is supported as a completed bounded
dependency graph plus indexed known-advisory lookup, with two direct keys
triaged and one range discrepancy unresolved. Transitive range triage and
product identity completeness remain open. No new vulnerability, exploit,
product test result, or CVE attribution is established here.

## Coordinator follow-up — same day

After this independent review, the transitive lookup and range work completed:
the exact 127-coordinate deps.dev query returned keys for all 127, and the
review of all 92 distinct transitive GHSA records across 93
coordinate/advisory associations found every exact pinned version inside the
recorded affected range, with no unresolved records. See the
[transitive query](../2026-10-21-a05-transitive-advisories/README.md) and
[transitive range review](../2026-10-21-a05-transitive-range-review/README.md).
The earlier stale-snapshot observations above describe the state when the QA
review was made; the coordinator updated the current ROADMAP/STATUS snapshot.

The two direct keys also remain bounded as previously reviewed: POI's affected
parser path was not found in pinned source; the Actuator 3.2.x vendor/GHSA range
discrepancy remains unresolved and its vendor route precondition was not found.
Two read-only source-triage assignments are now reviewing transitive
preconditions and Kadrom code paths. A05/R7 remains open pending those results
and a bounded final disposition. No product test or finding is implied.

The source triage has since completed across all 92 transitive advisory keys.
It recorded one source-level Spring RFD lead in the conversation attachment
download path, while Nimbus OAuth2 parsing and several framework-specific
conditions remain unresolved or conditional. No product exploitability was
established. A narrow H2 in-memory check with synthetic conversation members
and inert attachment content is now in progress for the RFD lead; a separate
read-only Nimbus path review is also underway. The current
[STATUS](../../STATUS.md) reflects this later state. The former paragraph
describes the point at which this independent QA review was completed.

## Coordinator follow-up — 22 October 2026

The narrow H2 attachment check completed at the pinned Kadrom commit. It
asserted anonymous `401`, synthetic nonmember `403`, and member `200`, then
observed the inert body, `text/plain`, and the encoded Unicode attachment
header. The temporary test was removed and the product checkout was clean.
This confirms only the exercised response/header and membership behavior; no
browser interpretation, active content, or RFD exploitability was tested. See
the [local check](../2026-10-21-a05-rfd-local-check/README.md).

The Nimbus source/cached-bytecode review found no source-supported path from
the pinned OAuth2 userinfo configuration to the affected Nimbus parser. Source
JARs were absent; deployment overrides were not inspected. See the
[Nimbus review](../2026-10-21-a05-nimbus-path-review/README.md).

Two additional read-only, role-specific tasks are active: an A04 endpoint
coverage inventory against the selected two-account objective, and a focused
A05 source trace for previously conditional Micrometer/Spring advisory paths.
The technical evidence above closes this independent review's earlier stale
“in progress” notes, but these new reviews and public product-identity lookup
limitations still require an explicit bounded disposition. A05/R7 remain open;
no vulnerability or advisory-absence conclusion is established.
