# R4 benchmark comparison protocol

Status: protocol prepared; no competitor comparison is accepted or published by
this document. Current acceptance is the versioned loopback execution corpus.
The main plan and remaining criteria are in [ROADMAP](../ROADMAP.md).

## What is measured

Use stable corpus case/source/method/parameter/read-sink/role identities to
match observations. Random canary IDs correlate a single attempt with its
browser observation; they are not stable finding identities. Execution must
match the submitted CID and the case's explicitly allowed frame path.

Keep three result classes distinct:

- Candidate counts from HTTP/static/third-party CLI parsers.
- Correlated browser execution in labelled, bounded fixture windows.
- Human vulnerability triage including authorization and intended behavior.

A resource callback, raw reflection, ordinary dialog or scanner severity cannot
be upgraded to execution. Bludit admin-authored product controls stay in
`product_controls`, with by-design triage, outside execution TP/FP/FN.
The current external CLI parsers do not implement a common browser-proof
adapter; their counts cannot support an execution-accuracy ranking.

## Freeze the comparison before running

Record one manifest for all participants containing:

| Dimension | Required agreement / recorded value |
|---|---|
| Corpus | Version, ordered selected case IDs, definition hash, independent positive/negative labels and rationale |
| Target | Identical fixture bytes/image digest, bootstrap state and endpoint behavior; fresh owned lab per run |
| Identity | Same account, verified role, source, parameter, read sink and allowed frames; no pooling across roles |
| Session | Same auth/CSRF inputs and rotation policy; unsupported auth is an explicit coverage gap |
| Budget | Same wall-clock, request, concurrency, retry and observation limits, including setup cost convention |
| Runtime | Tool versions/commits, Python/OS/browser versions, configuration and source hashes |
| Order | Predeclared repetitions, order and seeds where used; retain failed attempts and all repeats |
| Review | The same evidence requirements and independent human triage rules; disagreement is recorded, not silently relabelled |

The current proof runner enforces a per-case wall budget and an observation
window; it does not establish equal request budgets across competing scanners.
Do not claim a controlled competitor comparison until this gap and the common
proof-adapter gap are resolved. No external target is authorized by this file.

## Coverage and denominators

For each scanner, `selected` is the number of requested labelled cases. Report
`completed / selected`; zero selected means N/A, not 100%. Completion requires
a valid proof or a completed negative observation window. Preserve error,
timeout, skipped, invalid and inconclusive adapter outcomes separately.
The mutually exclusive outcome counts must sum to selected.

Only completed/evaluated cases enter TP/FP/FN. Within a completed case:

- TP = expected identity set intersect observed correlated-execution identities.
- FP = observed identities outside the expected identity set.
- FN = expected identities missing from the observed set.

For expected `{a,b,c}` and observed `{a}`, TP=1, FP=0, FN=2. A duplicate `a`
does not add a TP. A completed positive window with no canary is FN. An
unfinished positive case contributes no TP/FP/FN and remains in the coverage
denominator; it is not a true negative or evidence of safety.

Example: 14 selected, 13 completed and one timeout gives coverage 13/14. Even
if the 13 evaluated cases have zero FP/FN, the strict run fails. Report the
missing case and its predeclared label so apparent accuracy cannot hide an
untested positive. This is an illustration, not a measured run.

If accuracy ratios are presented, precision is TP/(TP+FP) and recall is
TP/(TP+FN) over completed cases, always beside coverage and incomplete counts.
A zero metric denominator is N/A. Do not pool repeated attempts or product
controls into the finding denominator. Do not publish a winner based only on
evaluated-case accuracy when tools completed different scopes.

## Required artifacts and acceptance

Retain JSON, its canonical Markdown rendering, JUnit and demo proof, with
commands (credentials/private paths removed from shareable copies), source and
corpus hashes. Bind the CI evidence to the tested commit and inspect the
uploaded artifact; a green job alone is not content acceptance.

Required strict acceptance rejects FP, FN, any incomplete outcome and an empty
selection. Negative controls must exercise the intended rule independently:
when changing JSON provenance or identity, regenerate matching Markdown so an
unrelated rendering mismatch cannot make a broken rule appear tested.

A publication requires the frozen manifest, all attempt outcomes, coverage,
common evidence adapter, independent labels and human review. This protocol
alone closes no general R4 coverage or competitor-result checkbox.
