# R8 — owned-source follow-up, 3 November 2026

Work started from `1c01c69` on main. The working tree was clean; after
`git fetch origin`, HEAD and origin/main differed by 0/0 commits.

## Active bounded work

Three native specialists are assigned exclusive ownership:

- Scanner engine: `tools/dom-xss-analyzer/dxa.py`.
- Independent QA: `tools/dom-xss-analyzer/test_static_r8_followup.py` and
  this directory's `measure.py`.
- XSS security: `tools/dom-xss-analyzer/STATIC-SCOPE.md`, after scope agreement.
- Coordinator: roadmap, status, validation, other audit artifacts and integration.

The selected gap must be measured against unchanged owner-provided source
before implementation. Private source, local paths and raw reports remain in
ignored `.dxa`; public reproducers use synthetic text only. No target runtime,
HTTP/browser tests, package publication or external targets are part of this work.

## Measured root cause and baseline

An unchanged owner-provided JavaScript source was high-confidence only in the
directory scan with its explicit sibling provider map. The single-file scan
was medium. A source-returning session helper tainted a role comparison used
only to select two fixed output strings. The generic sink matcher treated
that condition as output data. The owned source hash matched its prior
snapshot; private details are not copied here.

The agreed scope is fixed quoted-string arms with a simple JS condition,
plus bounded multiline sink extraction that retains later raw operands and
arguments. No helper is trusted as a sanitizer by its name.

Independent exact-base frozen suite: **13 failed / 33 passed**, no errors or
skips (46 tests). This followed an earlier non-final draft run, which is not
the accepted baseline. Base scanner SHA-256:
`c526399c1927ae529be35ad4a398b88ba4fbe8637f45952a5ac5ac4863d1c605`.
Frozen test SHA-256:
`29a0b3ea5de06a1ea879ef328526fb9b34e20d7064cc3c39d590f5f1bfd0576c`.
Twelve separately labeled source-signal examples yielded TP/FP/FN/TN
**8/4/0/0**; see `measurement-baseline.json`. Labels are not vulnerabilities
or general scanner accuracy.

## Final source acceptance

Review added ASI (automatic semicolon insertion), operator-boundary, opaque
syntax and literal-token controls. The final frozen **65-case** suite against the exact base
gave **16 failed / 49 passed**, zero errors/skips. Its final test identity is
in [baseline.json](baseline.json); the 46-case result above is intermediate.

The coordinator's final immutable thirteen-file suite gave **563 passed**,
zero failures/errors/skips, exit 0 (Windows / Python 3.10.11). Measurement
changed to TP/FP/FN/TN **8/0/0/4**, and the local CI self-scan passed. Source
and all selected test hashes were checked unchanged during this final run:
[result.json](result.json), [measurement-final.json](measurement-final.json).
An earlier draft integration run was rejected by the hash guard after edits
overlapped the run. Subsequent interim 558/561-test acceptances were superseded
after owned-source comparison and review found invented literal-token signals
in broad multiline recovery. Recovery now requires an actual conditional in
the original complete expression, declines opaque templates/slash constructs,
and masks literal tokens before matching recovered source/variable names.
Those interim runs are not the final acceptance evidence.

Reproduce final source acceptance from repository root:

```powershell
py -3.10 audit/2026-11-03-r8-followup/run_validation.py
```

The runner does not reexecute the historical baseline. Its exact scanner copy
and local JUnit outputs are preserved under ignored `.dxa/r8-followup-20261103`.
The historical scanner can also be recovered from Git commit `1c01c69`.
Python initially failed inside the sandbox before test collection; the actual
coordinator test commands ran with approved elevated Python access.

Engine implemented `dxa.py`; independent QA wrote the regression and labeled
measurement files; security measured the owned-source trigger and wrote the
scope description. The coordinator reviewed code/oracles, returned concrete
ASI counterexamples to the specialists, and ran combined acceptance. Native
role invocation was real; it does not independently prove TOML loader/runtime
permission inheritance. Persistent role configuration was preserved.

This is an unreleased source change. PyPI 0.2.2 is unchanged. Hosted CI has
not been checked; local tests do not imply application safety, execution,
confirmed XSS, or general scanner precision/recall.

## Owned-source comparison

The final scanner and exact baseline scanned the same authorized scope with
each version's project provider map. All **47 source hashes were unchanged**;
**129 candidates** remained. Only the measured condition-only signal changed
high to medium (high count 2 -> 1); every other compared row was identical.
There were no scan errors. The one existing excluded vendor-directory skip
remains and is not a successful clean scan. The other owned scope was not
rerun. [Sanitized comparison](owned-comparison.json) binds scanner identities;
full rows, target paths and source hashes remain private and ignored.

All three specialist tasks are complete; no background work remains active.
