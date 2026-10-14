# R4 callback artifact consistency and remaining acceptance map

Base: `8dd50acb80ed41bb2e44d4f1ab9defa9f1deca09`.
Native Scanner Engine specialist owns only the CI gate, its tests, and this
audit directory. The coordinator owns integration and roadmap status.

## Reproduced gap and fix

The artifact gate re-adapted nested browser proof and compared findings, but
did not compare the reported callback summary with the fixture's recorded
CID hit count. An artifact could report zero, inflated, mistyped or absent
callback counts or a false/mistyped/absent callback flag and still pass with
matching canonical Markdown. This did not create an XSS TP: the fixture
remained an execution-negative control. It did permit contradictory evidence
to pass a gate advertised as validating report consistency.

Eight independently mutated JSON/Markdown pairs reproduced the old failure:
the gate returned success where rejection was expected. The gate now requires
an integer `callback_count` equal to the re-adapted fixture count and the exact
boolean `callback_observed`. A positive regression preserves multiple matching
callbacks as an execution-negative result; the count is not hardcoded to one.

## Acceptance mapping

| R4 acceptance | Current evidence | Remaining scope |
|---|---|---|
| Finding identity, partial detection TP=1/FN=2 | `bench/test_bench.py:61` identity scorer independently supplies three expected IDs, one correct observed ID and a wrong sink; checks TP=1/FP=1/FN=2. `bench/test_proof_identity_matrix.py:102` rejects wrong role/source/parameter/read. | Corpus identities are local fixture identities, not universal root-cause matching. |
| Error/timeout/skip excluded from scores and coverage explicit | `bench/test_proof_adapter.py:92` checks five incomplete statuses; `bench/test_proof_identity_matrix.py:162` and `:177` verify exclusion and Markdown denominator. Historical real-worker coverage remains in `bench/test_runner_isolation.py:94`. | Worker/browser lifecycle was not rerun for this artifact-only change. |
| JSON/resource callback not XSS TP | `bench/test_bench.py:68` rejects non-execution levels; fixed corpus includes JSON and JS-disabled resource callback negatives. Gate requires independently labelled negative execution and completed window. | Does not imply arbitrary JSON or callbacks are safe; only the labelled observation window is scored. |
| FP/FN fail required acceptance | `bench/test_proof_adapter.py:102` negative FP, `bench/test_proof_identity_matrix.py:144` completed positive miss, and artifact mutation tests. | Broad corpus and product accuracy remain open. |
| Artifact consistency | Existing canonical Markdown/source/runtime checks plus this callback-summary regression. | No cryptographic authentication of self-reported evidence; downloaded archive integrity and exact-commit checks are separate coordinator work. |
| Auth/CSRF controls | Historical six-case runner/remote evidence in `../2026-10-14-r4-auth-runner/README.md`; separate operational scores. | No new auth run or cross-account admin proof in this change. |

## Boundaries and next fixture

No Docker, external target, scanner or schema changes were needed. No live
browser/Docker rerun is claimed. Existing local/remote corpus evidence remains
historical; this delivery checks the artifact validator with synthetic records.
Broad R4 and controlled competitor comparison remain open. The next distinct
fixture, when resumed by the coordinator, is an explicitly separated
low-privilege submitter and admin reader with submitted CID correlation and
negative wrong-role/wrong-CID controls. It is not implemented or claimed here.

## Validation

Before the fix:
`py -3.10 -m pytest bench/test_ci_acceptance.py -q -p no:cacheprovider --tb=short -k callback_summary`
returned **8 failed, 101 deselected**; all failures were unexpected gate exit 0.

After the fix, the initial gate/scorer/adapter run returned **208 passed**.
The final expanded run and source hashes are recorded in `acceptance.json`.
No new hosted CI result is claimed by this specialist. Commit/push belongs to
the coordinator.
