# R8-M1 QA method — 3 November 2026

The selected problem is omission of intrinsic JSX flat href review candidates
when an unrelated prop has object braces. It is based on the coordinator's
real-source reproducer; no unsafe/XSS label is assigned. The selected synthetic
corpus contains six development, ten separate evaluation and three unsupported
actual-href-expression boundary cases. `cases.json`, `measure.py` and
`test_static_m1.py` implement this study; coordinator freeze/baseline execution
is required before the implementation owner edits the scanner.

The earlier unselected Python helper-chain prototypes were moved to private
ignored `.dxa/r8-m1/qa-provisional/`. They remain provisional design work and
are not the selected study, baseline or acceptance evidence.

## Independence requirements

1. Select the behavior from an authorized real-source reproducer before
   constructing the study. Publish only a sanitized description and synthetic
   counterpart; private source and raw reports remain ignored.
2. Define labels from the intended observable behavior, not from current
   scanner output. The selected labels describe jsx-href candidate presence;
   line/confidence and source isolation are additional invariants. These are
   neither XSS labels nor judgments that programs are safe. Review labels
   independently of the fix.
3. Freeze case sources, expected labels, split membership, selection rationale
   and base-scanner SHA-256 before any implementation change. Include controls
   with raw inputs, fixed inputs and explicit unsupported boundaries.
4. Give the engine owner only the real reproducer and development split.
   Keep evaluation specifics withheld until implementation SHA-256 is frozen.
   A shared filesystem is not a technical secrecy boundary: this establishes
   a documented process only. Do not claim externally blind evaluation.
5. Run evaluation once against the frozen implementation. If results cause
   changes, record that exposure and classify reruns as development feedback;
   the original evaluation set no longer supports an unseen-case claim.
6. Report every case and counts per split, with candidate preservation,
   error/timeout/skip disposition and unsupported cases. In this candidate
   presence study a missing expected candidate is FN; a crash is a distinct
   error. Property mismatches are separate from candidate-presence counts.
7. Separate regression verification from effectiveness measurements. These
   purposive small cases estimate behavior only on the selected examples;
   they cannot establish general accuracy, user time saved or vulnerability
   discovery performance.

## Smallest selected-study artifact set

- `cases.json`: synthetic inputs, labels, split membership, rationale.
- `split-manifest.json`: immutable case/source hashes and base identity.
- `measure.py`: same runner for both scanner versions, no target execution.
- `baseline.json` and `final.json`: every observation and per-split summaries.
- One meaningful collected regression module under the scanner tests, added
  only when a real behavior and acceptance scope are selected.
- Coordinator-owned one-page case/README: problem, before/after, failures,
  limitations, role contributions and links to the machine-readable evidence.

## Actual runtime result

Initial draft file writes and moves succeeded. The three Python prototypes are
preserved in private ignored storage; no unused Python scanner test remains.
The attempted Python-chain command at its original draft path,
`py -3.10 audit/2026-11-03-r8-m1/measure.py --freeze`, failed before
Python startup with WindowsApps access denied. No manifest was created, no
baseline or test ran, no permission expansion was requested, and no CI result
was inspected. The coordinator halted selection of this helper-chain draft
because an owned-source trigger had not been confirmed. The selected JSX
study's freeze, baseline and final execution records are separate from that
earlier startup failure and are recorded by the coordinator.

## Frozen baseline and oracle review

The coordinator completed the JSX freeze and baseline before authorizing engine
edits. Baseline per-split TP/FP/FN/TN: development 1/0/2/3; separate evaluation
0/0/6/4; boundary 0/0/0/3. These are candidate-presence/scope labels. All 19
synthetic scans completed, with zero errors/skips/timeouts. Baseline case
details remain withheld from the engine; no selected corpus/manifest/runner
edits followed the freeze.

The independent regression oracle checks exact jsx-href candidate count,
physical href line, confidence and source-isolation properties. Three
development-only export checks enforce existing candidate/unreviewed R1
metadata. Boundary exclusions are not safe-program judgments. The existing
JSX regression suite remains necessary to protect other supported syntax.

`property_mismatches` includes candidate-count mismatches as well as metadata
violations; it must not be added to FN/FP as independent failures. Zero
skips/timeouts in this synchronous fixed-input runner describes completed
synthetic scans, not discovery coverage of real projects. The final evaluation
must wait until the engine's scanner SHA-256 is frozen. If an evaluation failure
causes a fix, disclose exposure and retain the original result rather than
calling subsequent runs unseen evaluation.
