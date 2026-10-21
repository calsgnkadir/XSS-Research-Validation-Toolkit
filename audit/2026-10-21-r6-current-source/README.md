# R6 current-source local revalidation — 21 October 2026

## Scope and environment

Revalidated the R6 `dxa-research-toolkit 0.1.0` candidate from toolkit commit
`6928fd6ffd8557a311b06b2b22f33fd6a2ac0b71` (`main`). The work rebuilt the
wheel, installed it offline into a fresh temporary virtual environment, ran
the installed-wheel gate, and ran focused tests for the changed `dxadyn.py`
module and its configuration/report identity behavior. No source or test files
were modified. No dependency was installed or downloaded; Docker, external
targets, tags, and publication were not used.

Environment: Windows 10.0.26200, Python 3.10.11, pytest 9.1.1, setuptools
65.5.0, wheel 0.48.0, Playwright 1.63.0 already present. Python's WindowsApps
launcher was denied in the default sandbox; the same existing interpreter ran
successfully with escalated local execution. This was an execution permission
issue, not a build or test failure.

## Wheel and installed gate

Build command (from repository root):

```powershell
py -3.10 -m pip wheel --no-deps --no-build-isolation --wheel-dir <temp> .
```

Build completed with exit code 0. Artifact:
temporary wheelhouse `r6-2026-10-22-current-source` (the retained temp-folder
label is copied exactly from the run) contained
`dxa_research_toolkit-0.1.0-py3-none-any.whl`.

Wheel SHA-256: `ffab49944876bca0b5362dd22c5a220aec62a09fbe962a390fcb16064c80ad91`.

The artifact was installed to a new Python 3.10 venv using
`pip install --no-index --no-deps <wheel>` (exit code 0). Gate command:

```powershell
<venv>\Scripts\python.exe bench/check_installed_cli.py `
  --bin-dir <venv>\Scripts --wheel <wheel> --output <temp>\acceptance.json
```

Gate output: `{"status": "passed", "cases": 7}`; exit code 0. The seven
checks cover all three installed CLI help entrypoints, static config override,
dynamic config/depth behavior, CLI depth override, and invalid-config rejection
without secret echo. The gate confirms the installed distribution identity and
version are `dxa-research-toolkit 0.1.0`; all nine shipped modules match across
current source, wheel, and installed venv. There were no failed, errored, or
skipped gate cases. Full machine-readable output is in
[`installed-wheel-gate.json`](installed-wheel-gate.json).

Changed module SHA-256, current source = wheel = installed venv:
`tools/dom-xss-analyzer/dxadyn.py` —
`6864971fbf0bd152bcbffef2a98c6fb783f8397447fabaa8f36c8876c31e509e`.
The gate JSON records hashes for all nine packaged modules and the wheel.

## Focused changed-module tests

Command:

```powershell
py -3.10 -m pytest tools/dom-xss-analyzer/test_dxadyn.py `
  tools/dom-xss-analyzer/test_dxadyn_report_identity.py `
  tools/dom-xss-analyzer/test_dxadyn_config.py `
  -q -p no:cacheprovider --tb=short
```

Completed: **271 passed** in 24.87 seconds; process exit code 0. No failures,
errors, skips, or timeouts were reported. This is a focused local regression
run, not the full analyzer suite.

## Hosted CI and limits

The coordinator independently observed current-commit hosted results:
[general CI run 39615470595](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/39615470595)
and [K01 Linux run 39615470859](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/39615470859)
both completed successfully. These hosted results are separate from the local
wheel gate and pytest run; this specialist did not query or download the CI
artifacts.

R6's current-source technical wheel and focused changed-module acceptance now
pass. This does not authorize or perform release tagging or package
publication; no tag or publication was made. The gate's loopback fixture is
not a vulnerability result or general scanner accuracy claim.
