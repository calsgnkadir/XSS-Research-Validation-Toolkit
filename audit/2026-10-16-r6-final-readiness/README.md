# R6 installed-wheel final readiness check

Run date: 2026-10-16 (Windows, Python 3.10.11). Branch `main` was at base
HEAD `f1fb6556b930d683b7b47fd0c6b04d6f8703053b`, equal to the locally read
`origin/main` ref. `git fetch origin` could not write `.git/FETCH_HEAD`
(`Permission denied`), so no fresh remote-ref verification or hosted CI result
is claimed. During this shared-worktree task, other coordinator edits appeared
in README/ROADMAP/STATUS/VALIDATION and later in `dxa.py` and its config test.
They were preserved. The acceptance JSON's nine module digests bind the source
snapshot actually compared to the built wheel; this is not evidence that the
committed HEAD alone was tested.

## Result

The fresh `0.0.0.dev0` wheel was built to `%TEMP%\r6-final-readiness\wheelhouse`,
installed with `--no-index --no-deps` into a new venv under `%TEMP%`, and checked
from `%TEMP%\r6-final-readiness\work`, outside the source checkout. The gate
passed all **7/7** checks: three CLI help entrypoints, static config override,
dynamic config depth, explicit CLI depth override, and invalid config rejection
without secret echo. The dynamic cases also confirmed matching JSON/HTML depth,
expected loopback routes, and fixture-thread cleanup. There were **0 failures,
0 errors, 0 skips** in this script run (it is not pytest and has no skip result
type). All nine packaged modules imported from the venv and their bytes matched
both the current source snapshot and wheel.

Wheel SHA-256: `0edea5d639183f2088739241ec9b985cb7a39f0b43e33cc73a1ec8494675a07f`.
Full per-module hashes and check results are in [acceptance.json](acceptance.json).

## Commands and build-tool caveat

The first offline wheel attempt failed at metadata preparation with
`error: invalid command 'bdist_wheel'`; the system Python had setuptools 65.5.0
but no `wheel` package. To complete the requested build, `wheel==0.48.0` was
installed into the system Python environment from a locally cached artifact;
pip output showed no network download. That global Python environment was
modified and was not reverted. No further packages were installed. The retry
then built the wheel successfully. This initial failed attempt is retained in
the record; it is not counted as a passing run.

Successful build:

```powershell
py -3.10 -m pip wheel --no-deps --no-build-isolation --wheel-dir $wheelhouse .
```

Fresh install and gate (all paths below were under `%TEMP%`, with the final
output written to this audit directory):

```powershell
py -3.10 -m venv $venv
& "$venv\Scripts\python.exe" -m pip install --no-index --no-deps $wheel
& "$venv\Scripts\python.exe" "$repo\bench\check_installed_cli.py" `
  --bin-dir "$venv\Scripts" --wheel $wheel `
  --output "$repo\audit\2026-10-16-r6-final-readiness\acceptance.json"
```

The checker ran with its working directory set to the temporary `work`
directory. The original readiness run did not edit
`bench/check_installed_cli.py` or application code. A follow-up acceptance
review later added distribution metadata checks; see below. No release tag,
publication, external target test, browser execution claim, or vulnerability
result is part of this check.

## Limits

This confirms installability and the bounded CLI/config behavior exercised by
the installed-wheel gate on this Windows/Python 3.10.11 host. It does not
validate browser execution, an end-user release workflow, broad scanner
accuracy, or a fresh hosted CI run. The initial readiness wheel version was
`0.0.0.dev0`; the later `0.1.0` release-candidate check is recorded below.

## Acceptance metadata follow-up

Source review found the original checker verified shipped module bytes and
exercised installed script launchers, but did not verify wheel `METADATA`
identity/version or that `entry_points.txt` mapped the expected three CLI
commands. A wheel with matching module bytes but unrelated project metadata
could therefore satisfy those earlier checks. The checker now requires one
`.dist-info/METADATA` for `dxa-research-toolkit`, a nonempty version, and the
exact `dxa`, `dxadyn`, and `dxaprove` console-script mappings. It also compares
the installed distribution name/version with the supplied wheel and records
that identity in result JSON.

On 2026-10-16, the metadata helper ran against the existing wheel and returned
`dxa-research-toolkit` version `0.0.0.dev0`. This was a helper-level check only;
the full installed CLI gate was not rerun after this edit. Reusing the old venv
failed because its base Python path was unavailable; a new venv was created,
but its interpreter had the same issue. An offline `pip --target` install
succeeded in a temporary directory without a global install, but did not
provide the interpreter layout needed to rerun the complete gate. Hosted CI
has not run with this follow-up.

## Coordinator verification of the metadata follow-up

Run date: 2026-10-16, Windows / Python 3.10.11. After the R8 Python AST pilot
was integrated, the coordinator rebuilt the selected `0.1.0` wheel from the
current working tree in `%TEMP%`, installed it offline into a fresh venv, and
ran the full checker from that venv. The updated gate passed **7/7** checks,
including `dxa-research-toolkit` metadata and matching installed version
`0.1.0`. All nine module hashes matched current source, wheel, and installed
copies. Wheel SHA-256:
`bde6f6cdba1190f2bee30e5b02499f7a4717a943a503e1686e1f73680535aba9`;
the refreshed [acceptance.json](acceptance.json) binds this final result.

The run used only an offline temporary venv; no global package install was
performed for this rerun. It is local Windows evidence, not hosted CI. The
version and release-specific changelog are prepared, but the wheel was not
tagged or published.

## Hosted verification for R6 delivery

Commit `401e6bf6848a95986ba26eccd51127600712a4b3` was pushed to `origin/main`
and the remote branch hash matched. General CI run
[38894634586](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38894634586)
completed with all three jobs successful. The `dom-xss-analyzer tests` job
includes the new synthetic wheel metadata regressions; the required browser
proof job and opt-in browser job also succeeded. K01 Linux run
[38894634507](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38894634507)
completed successfully. These are workflow results; downloaded artifact
contents were not independently inspected. No PyPI publication or Git release
tag was made.
