# R4 coordinator result review — 16 October 2026

## Review scope

Coordinator review for the user's requested third step. This is a technical
coordinator review of local fixture evidence; it is not represented as an
independent human review. No external target is in scope. The review follows
`bench/COMPARISON-PROTOCOL.md`: scanner candidates, correlated browser
execution, and authorization/intended-behavior triage are separate judgments.

The existing equal-budget run-02 was the starting evidence. This turn added
separate role-bound scanner logins and a strict CID/browser oracle. The
coordinator independently reran the auth/fixture/comparator tests and checked
the new run manifest, report/log hashes, role checks, request accounting and
credential redaction. The new run did not produce scanner payloads the oracle
can correlate to browser execution; that result is recorded as inconclusive.

## Preliminary triage of existing run-02

| Scanner output | Observed | Coordinator disposition |
|---|---|---|
| dxadyn, raw case, both repeats | One high-confidence unencoded stored-body reflection candidate; `evidence_level=reflection`, `role_verified=false`, `session_check=not-requested` | Candidate only. Does not establish execution, separate-role impact, or a vulnerability. Requires exact candidate CID in the browser oracle and role/session evidence. |
| dxadyn, escaped case, both repeats | No findings | No candidate observed in that tool run. This alone is not a completed negative execution observation. |
| Dalfox, raw case, both repeats | One `V` assertion per report; payload contains a generated-looking class token and message says DOM verification successful | Not accepted as local execution proof: no trace binds this scanner-generated token to the independent browser event. Keep as unverified third-party assertion until exact-token correlation is demonstrated. |
| Dalfox, escaped case, both repeats | One `R` informational reflection per report, explicitly says executable position was not confirmed | Informational reflection, not execution and not a confirmed XSS finding. Do not silently count it as an XSS false positive; report the distinction from each tool's candidate semantics. |

The local purpose-built fixture's raw execution and escaped control are separate
fixture oracles. They cannot retroactively validate candidate payloads from
these scanner invocations. No TP/FP/FN, winner, or vulnerability claim is
derived from the existing run.

## Final coordinator triage and R4 disposition

The new authenticated run selected eight scanner invocations; all eight
completed, with zero errors, timeouts or incomplete rows. Every row passed
pre/post writer and reader-admin role checks and all four cross-role controls.
Each fixture counted eight authentication/setup requests and two post-checks
inside the same 200-request, 2-rps, concurrency-1, 120-second limits. Per-run
total requests ranged from 12 to 33. The coordinator recomputed the manifest
SHA-256 (`36413d8c5416f8e66ec4953f6db37a26c5a103b96b2264421dadd4e8ecd82fba`),
all referenced artifact hashes matched, and no session token pattern remained
in shared artifacts.

Case triage for the new run:

| Case and tool | Candidate observation | Exact submitted payload/browser correlation | Coordinator disposition |
|---|---|---|---|
| Raw, dxadyn (2 repeats) | 1 candidate each | Stored payload is a `dxa…<dXsS>` marker; it has no unique `?cid=` plus active JS proof assignment. | Candidate only; execution inconclusive. |
| Escaped, dxadyn (2 repeats) | 0 candidates | No scanner candidate CID to observe. | No candidate observed; not a browser-confirmed negative. |
| Raw, Dalfox (2 repeats) | 1 candidate each | Stored `dlx…` markers and `alert(1)` payloads do not bind a CID to the oracle's browser proof value. | Candidate only; tool assertion is not independently correlated execution. |
| Escaped, Dalfox (2 repeats) | 1 candidate each | Submitted strings lack the required CID-bound JS proof; oracle cannot establish execution or non-execution for that candidate. | Candidate only; not scored as FP or confirmed execution. |

The purpose-built raw/escaped browser fixture tests validate the harness only;
they cannot prove that a scanner candidate executed. The exact-CID oracle tests
passed 27/27 independently, and the coordinator auth/fixture/comparator suite
passed 30/30. No TP/FP/FN, accuracy score or winner is reported.

Overall R4 remains open. The ROADMAP also requires broader identity-level
scoring, incomplete-run handling, JSON/resource-callback exclusion, CI negative
gates and human triage. This is the coordinator's technical triage, not an
independent human review. R5's independent-person repeat remains deferred at
the user's request and was not treated as R4 evidence. This audit records local
evidence only; remote commit and CI status are maintained separately in
`STATUS.md`.
