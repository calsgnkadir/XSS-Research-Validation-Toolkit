# R5/K01 closure review — 16 October 2026

Roadmap IDs: **R5 / K01**. This is a review of the existing local and Linux
evidence at `d9db15ba2094b44c27870a311959de1d1dad15f6`; it is **not** a new
browser reproduction or a second person's run. The working tree was clean at
the start of this review. No case implementation, fixture, CI, or human form
was changed.

## Acceptance matrix

| Criterion | Evidence checked | Result |
|---|---|---|
| Fixed fixture and repeat command | `cases/k01-stored-comment/README.md:63`, `check_repro.py:132`, `audit/r5-local-closure-resume/proof/acceptance.json` | Existing local gate records k01-v1.0, runtime and source hashes; instruction is actionable. |
| Submit, stored read and CID execution | `prove.py:26`, `prove.py:76`, `prove.py:142`, `check_repro.py:92`, existing `proof/result.json` | Existing loopback run recorded the matching vulnerable CID and one POST per control. This review did not replay it. |
| Fix and negative controls | `render_fixed.py:6`, `check_repro.py:74`, `check_repro.py:92`, `test_repro_gate.py:52`, `:59` | Existing run reports fixed, JS-disabled, JSON-only and normal-dialog negatives. The gate rejects forged execution and HTTP proof promotion. |
| Cleanup and incomplete runs | `check_repro.py:115`, `test_repro_gate.py:94`, `:181`, existing acceptance | Existing live gate recorded five distinct closed ports. A failed proof cannot write acceptance. Archived files cannot independently recheck past socket state. |
| Local regression | `audit/r5-local-closure-resume/regression.xml` | Historical run: 22 tests, 0 failures, 0 errors, 0 skipped. No pytest rerun in this review. |
| Linux automation | `.github/workflows/k01-repro.yml:16`–`:31`; `STATUS.md:9` and `VALIDATION.md:10` | Commit `157a438` K01 workflow `38806623393` is recorded successful. Its artifact contents were not independently downloaded in that follow-up. Earlier run `38706882018` has a recorded downloaded-artifact hash gate in `audit/2026-10-15-resumed-delivery/remote-r5-acceptance.json`; it belongs to a different commit. CI is not a human repeat. |
| Independent human | `ROADMAP.md:456`, `cases/k01-stored-comment/INDEPENDENT-REPEAT.md:3`, `:55` | **Open and deferred.** The form remains unfilled. No second person's clean checkout, new venv, run output or review was supplied. |

The existing local proof package has 12 proof members, three case source
hashes and one gate hash. On this review, `Get-FileHash -Algorithm SHA256`
matched all 16 values in `proof/acceptance.json` against the current files.
That checks byte integrity of this historical package, not its independent
execution or the identity of an operator. The Linux acceptance record was
read, not queried or rerun. No new CI status is claimed for HEAD `d9db15b`.

## Decision and next evidence

The R5/K01 automated local scope is already supported by the prior run and
regressions. Source and handoff review found no concrete instruction defect
requiring a case edit. The remaining ROADMAP R5 condition is a different
person's clean environment reproduction. The person should follow
`INDEPENDENT-REPEAT.md` with a new output directory, record a full commit hash,
starting status, runtime, exact command and exit code, and submit that run's
`result.json`, `fix.diff`, ten request/response files and `acceptance.json`.
The coordinator can then compare source and member hashes, CID/control
results, and the person's explanation. A failed install, timeout, absent
artifact, or skipped control remains an incomplete run; it does not establish
a negative XSS result. This review leaves the form blank and R5 open.
