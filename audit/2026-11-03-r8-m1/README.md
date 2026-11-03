# R8-M1 — single-behavior measurement study

Work started on 3 November 2026 from `220bbd2`. The working tree already
contained coordinator-authored ROADMAP/STATUS/CHANGELOG changes adding M1.
Those changes are preserved. This record tracks the current task under the
main ROADMAP; it is not a separate backlog.

## Assignment and selection gate

Three native role invocations used exclusive ownership; all tasks are complete:

| Task / role | Ownership | Initial acceptance |
|---|---|---|
| m1_engine / scanner_engine_specialist | dxa.py, test_m1_parser_boundaries.py, engine-notes.md | Root cause and bounded scope; implementation waited for selection and baseline |
| m1_qa / qa_security_lab_specialist | test_static_m1.py, measure.py, cases and split/baseline artifacts here | Independent labels and development/evaluation separation before implementation |
| m1_security / xss_security_researcher | problem-selection.md, STATIC-SCOPE.md JSX section, private inspection artifacts | Actual authorized-source trigger, sanitized reproducer and source identity |
| Coordinator | Shared progress records, integration and acceptance | Review oracle, source/evaluation integrity and measured claim |

Native role invocation does not independently prove TOML loading or runtime
permission inheritance. Existing persistent role definitions are preserved.
No specialist commits or pushes independently.

The suggested Python helper-chain loss is an existing synthetic limitation,
but no matching Python HTML sink was found in the authorized owned scopes.
It is therefore **not selected for implementation**. Its provisional corpus
is private/ignored and is not accepted experiment evidence.

## Selected behavior and actual baseline

A simple JSX anchor `href={target}` is found without a style prop but omitted
when an unrelated prop has an object expression, such as `style={{color:'navy'}}`.
The opening-tag scan rejects nested braces anywhere, even outside href. In
two owner-source anchors this loses a review candidate. The actual values
are guarded; this is **not missed XSS** or a claim of unsafe URL control.

Coordinator static-only baseline command:
`py -3.10 .dxa/r8-m1/security_jsx_baseline.py` (approved elevated Python), exit 0.
Both owner anchors: expected 1 candidate, observed 0; source hashes unchanged.
Synthetic development pair: flat href 1/1; same href with style object 0/1.
Private exact source identities and rows are preserved; source is never run.
Base scanner SHA-256:
`5401e79a676bb4b7deed4b9ca0233c93591718c498e6a37573160519672c5a4c`.
An exact scanner copy is preserved in ignored `.dxa/r8-m1/baseline-dxa.py`.

Fresh directory inventory at this same scanner identity: scope A has 233 files,
20 candidates, 0 HIGH source signals and 0 events; scope B has 47 files,
129 candidates, 1 HIGH and one known excluded vendor-directory skip. Source
hashes were unchanged throughout both scans. The skip is not a clean result.
These counts describe inputs/observations, not vulnerability or user benefit.

Only authorized local source inspection/static analysis is in scope. No app,
HTTP/browser, package publication, target code modification or external target.
Private source/paths/raw reports stay in ignored `.dxa`. Initial Python attempts
failed before startup due sandbox WindowsApps access; no tests passed thereby.

## Frozen measurement and final acceptance

The 19-case corpus and split manifest were frozen before implementation:
6 development, 10 separate evaluation, 3 unsupported-boundary controls.
Baseline development TP/FP/FN/TN = 1/0/2/3; evaluation = 0/0/6/4;
boundary = 0/0/0/3. These labels mean review-candidate presence, not XSS.
All cases completed with no errors/skips. See [baseline.json](baseline.json).
Manifest SHA-256:
`cb7ee6b8d3699594073fb6e5c983cf73a9f5bc883bd7bc5a3508131734a6ddea`.

Implementation was authorized only after this freeze. It is limited to
balanced unrelated expression props; nested href expressions, spreads and
custom/namespaced components retain their declared limits. No evaluation
specifics are given to the engine before implementation is frozen.

The initial implementation passed development and 70 existing/design checks.
Source review then found duplicate-href ambiguity. Engine added its guard
and six design controls **before first evaluation**. The revised version
passed development and 76 existing/design checks. These are intermediate
development results, not additional independent evaluation successes.
`final-development.json` and `final-development-v2.json` bind both versions.

Final scanner SHA-256:
`1d3baa91fcf85e60d1be0e8bc4da06c99442e34b89ffe8b868190b3d985a70b4`.
First final evaluation restored all six previously omitted review candidates
in ten separate cases while preserving four negative controls. Development
became TP/FP/FN/TN 3/0/0/3; evaluation 6/0/0/4; boundary exclusions unchanged.
Zero observed errors/skips/property mismatches: [final.json](final.json).
No code change followed evaluation. The shared filesystem permits only a
documented withholding process, not a technically blind external experiment.

Coordinator's immutable fifteen-file selected acceptance: **607 passed**, zero
failures/errors/skips, pytest/measurement/local CI self-scan exit 0. All selected
source/test/corpus/runner hashes stayed unchanged: [result.json](result.json).
QA independently checked case identities and current acceptance hashes without
rerunning tests. Security reviewed all added real-source rows and their guards.

Directory comparison on identical 233/47 source inventories: A 20->23, exactly
three added medium JSX href candidates; B 129->129. No previous rows removed
or changed, no scan errors. B's known excluded vendor-directory skip remains;
no safe conclusion is drawn for that directory. A third same-behavior example
was found during selection and is not claimed as unseen. Actual URLs have
guards in reviewed source; more candidate rows can increase manual review.
[Sanitized comparison](owned-comparison.json). Raw rows/source remain ignored.

Repeat source acceptance (writes fresh ignored run artifacts):

```powershell
py -3.10 audit/2026-11-03-r8-m1/run_validation.py
```

Initial historical commands were `measure.py --freeze --scanner
.dxa/r8-m1/baseline-dxa.py`, then the same runner with `--out baseline.json`.
The private base copy can be recovered from Git `220bbd2`. First final command
was `py -3.10 audit/2026-11-03-r8-m1/measure.py --out
audit/2026-11-03-r8-m1/final.json`; output files refuse overwrite. The combined
acceptance command used `run_validation.py --out .../result.json`. Repeated
measurement in acceptance is explicitly a repeat of the frozen evaluation.

[One-page case and scoped CV draft](../../docs/R8-M1-CASE-STUDY.md) records the
problem, attempt, outcome, remaining failures and individual role contributions.
Nested actual href expressions, spreads, generic JSX/TSX/guard analysis remain
unsupported. Case counts are not general accuracy, confirmed XSS, CVE or user
time saved. This is unreleased source; PyPI 0.2.2 is unchanged. Hosted CI was
not checked. No active background work remains.
