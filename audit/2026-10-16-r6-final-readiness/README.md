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
directory. `bench/check_installed_cli.py` and application code were not edited
by this task. No release tag, publication, external target test, browser
execution claim, or vulnerability result is part of this check.

## Limits

This confirms installability and the bounded CLI/config behavior exercised by
the installed-wheel gate on this Windows/Python 3.10.11 host. It does not
validate browser execution, an end-user release workflow, broad scanner
accuracy, or a fresh hosted CI run. The wheel version remains `0.0.0.dev0`.
