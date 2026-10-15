# R5/K01 local closure evidence — 15 October 2026

The native QA specialist reran the existing K01 gate from the user-selected
OneDrive working copy. At execution time this copy had no `.git`; no test-time
commit identity or clean checkout is claimed. The tested bytes are identified by `validation.json` and
the live gate's `proof/acceptance.json`. The old C: worktree was not modified.

## Current run

```powershell
py -3.10 cases/k01-stored-comment/check_repro.py --profile local --browser 'C:\Program Files\Google\Chrome\Application\chrome.exe' --output audit/r5-local-closure-resume/proof
py -3.10 -m pytest cases/k01-stored-comment/test_fixture.py cases/k01-stored-comment/test_repro_gate.py -q -p no:cacheprovider --tb=short --junitxml=audit/r5-local-closure-resume/regression.xml
```

Both commands returned exit 0. The live gate passed **5/5 controls**, with
**5 distinct closed loopback fixture ports**. The existing focused regression
suite passed **22 tests in 13.40 seconds**, zero failures/errors/skips. These
are separate observations, not 27 independent browser controls.

Runtime: Windows, Python 3.10.11, Playwright 1.63.0, installed Chrome
155.0.8059.79. No fresh venv was created for this run. The normal shell helper
failed before launch with `helper_unknown_error: setup refresh had errors`;
the system's explicit escalation flow allowed the necessary commands. This
is an execution setup issue, not a failed or skipped fixture test.

`proof/` contains the new result, five request/response pairs, fixed renderer
diff and live acceptance record. Source, gate and all 12 proof member hashes
matched on post-run inspection. The fixture data is synthetic; requests have
no credentials or real user data. The generated JUnit hostname attribute was
removed for sharing; test counts and results were preserved. No application
or test implementation changed because this review found no reproducible
defect requiring a fix.

## ROADMAP R5/K01 acceptance matrix

| Criterion | Evidence and observed result | State |
|---|---|---|
| Fixed target/version and repeat commands | `prove.py:82`, `README.md:63`, live `proof/acceptance.json`: k01-v1.0 and exact runtime; hashes in validation record | Local scope verified |
| Source → storage → independent reader | `prove.py:26`, `prove.py:105`, `prove.py:118`: urllib POST and fresh browser context; exactly one POST per case | Verified for anonymous shared comments |
| CID browser execution | `prove.py:132`, `check_repro.py:91`, `proof/result.json`: vulnerable case observed the submitted CID | Verified for this fixture |
| Fixed output and same-payload retest | `render_fixed.py:6`, `prove.py:137`, `check_repro.py:88`, `proof/fix.diff`: escaped text preserved, no img, no canary | Verified |
| Negative controls, no proof promotion | `check_repro.py:70`, `check_repro.py:99`, `proof/result.json`: JS-disabled, fixed, JSON and normal-dialog controls had no canary; HTTP labels remain separate | Verified |
| Request/response and cleanup | `check_repro.py:73`, `check_repro.py:114`, new request/response files and live acceptance: 5/5 ports closed | Verified at live execution time |
| Unexecuted/unobserved scope explicit | `cases/k01-stored-comment/README.md:39` and `:121`: no account-role or real-product claim; synchronous 500 ms negative window | Existing documentation verified |
| Internship learning record | `staj/2026-10-05-k01-vaka.md:3`: aim, method, failure, fix, retest and learning | Existing historical record verified, not a new experiment |
| JSON/dialog false-positive examples | `prove.py:101`, `prove.py:140`, `proof/result.json`; relevant gate regressions in `test_repro_gate.py:52` and `:59` | Current local checks passed; R1 fix is historical |
| Writeups 01/10/11 link current case | Each named writeup's line 1 links K01 and limits historical-target implications | Existing links verified |
| Another independent person reproduces from clean environment | `cases/k01-stored-comment/INDEPENDENT-REPEAT.md:3`; no person supplied evidence in this run | **Open, deferred by user** |

Code paths in the table are relative to `cases/k01-stored-comment/` unless
otherwise stated. ROADMAP remains the source of truth; this is evidence for
the coordinator's local-scope acceptance, not a replacement work plan.

## Limits and recommendation

The applicable automated local K01 scope is ready for coordinator acceptance.
General R5's independent-person criterion remains open and deferred; its form
remains unfilled. An agent run is not a second person. Historical Linux CI
evidence in `audit/2026-10-14-r5-linux-gate/` was read, not rerun or newly
verified remotely. No new CI, external target, release, commit or push occurred.
No authenticated two-account boundary, CVE or general scanner efficacy is
claimed. Port closure is the live gate's observation; archive inspection alone
cannot recreate historical socket state.

## Final delivery review

After the run, the coordinator restored Git metadata at HEAD
`df967d506e8c37033ed6aa2c2e367a7aa0ec20dc`. All ten source digests in the
run manifest still matched; Git reported no differences for the case code,
its imported modules or K01 workflow. This is a later provenance check, not
a retroactive claim that the test used a clean checkout.

Source inspection of `.github/workflows/k01-repro.yml:12` through `:31`
confirmed Python 3.12, pinned Playwright, Chromium installation, both current
test modules, default CI gate and always-uploaded proof/JUnit artifacts.
No workflow code change is required by this evidence-only delivery. Actual
future CI execution remains unverified; no new tests or proof were rerun.

The final share review found only synthetic CID/payload and loopback URLs in
proof files; no credentials, personal user paths or JUnit hostname. The
installed Chrome path in the command is a generic system path. The package
contains no browser profile, cache, database or large output.

A delivery integrity issue was reproduced: `core.autocrlf=true` would change
CRLF proof bytes during Git clean, invalidating the recorded SHA-256 hashes
after checkout. This directory's `.gitattributes` uses `* -text` to preserve
the exact evidence bytes. Raw and Git-filtered blob hashes now match for
every file in this package. This changes artifact handling only; fixture
code and test results are unchanged.

Commit scope for this specialist is the complete
`audit/r5-local-closure-resume/` package, including `.gitattributes`. There
are no case implementation edits. R5's applicable local technical scope is
verified; independent-person clean reproduction is the only deferred general
R5 criterion. The coordinator owns the corresponding main-plan update.
