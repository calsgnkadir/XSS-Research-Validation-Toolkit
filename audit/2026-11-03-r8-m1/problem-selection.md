# R8-M1 — real-source selection gate

3 November 2026; scanner base `220bbd2`. This records problem selection and
the final owned-source comparison; synthetic evaluation acceptance is recorded
separately by QA/coordinator. Private source and target locations
remain under ignored `.dxa/r8-m1` and the earlier owned-review records.

## Suggested Python helper chain: not selected

The prior synthetic helper-chain miss is real historical evidence of a bounded
scanner limitation. It does not establish a current problem in an owner project.
The two previously authorized scopes were checked for relevance: scope A is a
JavaScript/JSX frontend; scope B's Python backend uses JSON responses and static
file delivery in the inspected routes. A targeted current-source search for
`Markup`, `HTMLResponse`, `render_template`, `render_to_string`, `mark_safe`,
`HttpResponse`, Jinja and `Template(` found no match in scope B's Python/HTML
files. This is a scoped search, not proof that every possible HTML path is absent.
No corresponding Python HTML-sink chain has been demonstrated. The Python
helper extension therefore does not pass M1's real-source selection gate.

## Remaining JavaScript HIGH row: no narrow mitigation selected

The earlier remaining HIGH source-confidence row leads through an API response,
a week renderer, a map callback and a separate slot renderer. Inspected display
values pass through HTML encoders. A simple name-based suppression would be
unsound: the actual encoder returns non-string values unchanged. Typed-string
assumptions and multi-function output contexts would need separate validation.
This is not the bounded single-return Python case and is not selected merely
because a high-priority candidate remains. Source-confidence false signal,
false vulnerability verdict and safe application are different claims.

Exact private file:line references and unchanged source identities are retained
in the private review; the inspected renderer's SHA-256 matches that prior
snapshot. The coordinator's fresh static inspection retained 20 candidates on
233 files in scope A and 129 candidates on 47 files in scope B. Scope A had
zero HIGH rows and scope B one; source hashes remained unchanged during the
scan. Scope A had no events; scope B retained its known vendor exclusion event.
These counts are an inventory, not a precision/recall or safety measurement.

## Selected behavior: unrelated JSX style object hides a flat href candidate

Fresh current-source findings omit two real intrinsic anchor tags whose `href`
is a flat identifier expression but whose separate `style` prop contains an
object. Other flat anchors in the same source are reported. Inspection of
`dxa.py:1678` through `dxa.py:1690` shows the cause: depth greater than one
anywhere in the opening tag sets `unsupported`, then discards the whole tag.
The href itself need not contain nested braces to trigger this exclusion.

Sanitized DEVELOPMENT pair (never executed):

```jsx
const view = <a href={target}>go</a>;
const view = <a href={target} style={{color:'navy'}}>go</a>;
```

Expected behavior is one medium source-confidence `jsx-href` review candidate
in each separate example. The narrow extension should skip the balanced object
expression of the unrelated prop without treating its contents as href or as a
source. It does not require nested href support, spread-prop resolution, general
JSX parsing or validation/guard inference. Strict existing rejection boundaries
must be retained wherever ambiguity could change the actual href binding.

The coordinator's targeted static baseline completed successfully. Both selected
owner anchors yielded zero candidates instead of one, with unchanged file hashes;
the development flat anchor yielded one candidate and its style-object counterpart
zero. No events occurred in those targeted scans. The private frozen artifact is
`security-jsx-baseline.json`; source/test fixture contents were never executed.
Further source inspection identified a third same-behavior occurrence: the same
flat href expression appears once without style (reported) and once with a style
object (omitted) in one source file. This extra occurrence was discovered during
selection, not reserved as an unseen evaluation example.

This was a documented parser coverage limitation, now selected as one measured
usability behavior under R8-M1. The actual two URL values have guards in the
reviewed source: recovering their candidate rows does not establish a missing
XSS finding. The user effect being measured is review-candidate coverage;
additional candidates can increase manual review work, and no time saving is
claimed. The selection gate required the synthetic baseline and independent
evaluation split to be frozen before implementation. The coordinator owns
those records.

## Runtime evidence and next decision

The specialist's current `py -3.10` static-scan attempt failed before interpreter
startup with WindowsApps access denied. It produced no scan/test result. A
private static-only inspection script was supplied and the coordinator ran it
successfully, recording provider bindings, full local findings and before/after
source hashes, with only aggregate counts on stdout. It never imports/executes
target apps. A separate targeted baseline script was supplied; that script
refuses to overwrite its frozen baseline artifact.

Implementation was gated on the selected behavior's reproduced baseline and
a frozen development/evaluation split. Successful candidate recovery alone is
not a successful security assessment or a general coverage improvement claim.
No HTTP reflection, callback, browser execution, confirmed XSS, new CVE,
general precision/recall or measured user-time benefit is established.

## Final independent source review and owned comparison

The security source review found an ambiguous duplicate-href case in the first
development implementation. The engine added a guard for every duplicate href,
including fixed and bare forms, before the first separate evaluation run. That
review was development-stage refinement; no evaluation case was disclosed to
the engine. Read-only review of the revised guard found it consistent with the
documented scope. Coordinator execution, rather than this source review, supplies
the actual regression-run evidence.

The final scanner SHA-256 is
`1d3baa91fcf85e60d1be0e8bc4da06c99442e34b89ffe8b868190b3d985a70b4`.
The coordinator ran the guarded source-comparison script successfully. The
security specialist inspected all three added private rows: they are exactly
the two selected flat href/style-object anchors and the third selection-time
occurrence described above. Scope A changed 20 -> 23 total candidates and
8 -> 11 JSX-href candidates; all three additions are medium source-confidence.
Scope B remained at 129 candidates. No existing row was removed or changed.
All 233/47 source identities matched the frozen baseline before and after.
Scope A had no error/skip events; scope B retained one known vendor skip and
no errors. The scanner and frozen baseline hashes stayed unchanged during
comparison. [Sanitized counts and identities](owned-comparison.json).

Source review confirms guarded HTTP(S) and fixed-origin URL construction in
the two selected cases, and fixed `mailto:` construction with encoded subject
and body in the third. Runtime behavior was not tested. These recovered rows
are additional review candidates, not newly discovered vulnerabilities.

The comparison records a copy of the first discovery/scan event list before a
second file enumeration checks the ending source inventory. Consequently the
known vendor discovery skip is counted once; the verification enumeration's
duplicate skip does not inflate scan-event totals. Any ending inventory/hash
mismatch causes the runner to fail before writing a successful comparison.
