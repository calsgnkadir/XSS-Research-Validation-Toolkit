# Local research demo

This guide installs the `0.1.0` research candidate and runs two disposable
loopback demonstrations. Nothing here targets a public site. The built-in
`dxaprove` demo shows a matching canary event in its own fixture; the K01 case
shows one stored-comment payload before and after output encoding.
The version's [release notes](../CHANGELOG.md) are preparation only; current
[project status and limitations](../STATUS.md) remain authoritative.

## Requirements

- Python 3.10 or later
- Git and a checkout of this repository
- Playwright 1.63.0 and its Chromium browser, installed by the commands below

Run these commands from the repository root. On Windows PowerShell:

```powershell
py -3.10 -m venv .venv-portfolio
.venv-portfolio\Scripts\python.exe -m pip install ".[browser]"
.venv-portfolio\Scripts\python.exe -m playwright install chromium
New-Item -ItemType Directory -Force .dxa | Out-Null
```

On macOS or Linux, use:

```console
python3 -m venv .venv-portfolio
.venv-portfolio/bin/python -m pip install '.[browser]'
.venv-portfolio/bin/python -m playwright install chromium
mkdir -p .dxa
```

## Demo 1: installed package and its own fixture

Choose a new output directory; the command refuses to overwrite an existing
one.

```powershell
.venv-portfolio\Scripts\dxaprove.exe --demo --output .dxa/portfolio-demo-2026-10-17
```

On macOS or Linux:

```console
.venv-portfolio/bin/dxaprove --demo --output .dxa/portfolio-demo-2026-10-17
```

Expected result: `execution-observed`, exit code 0, with `result.json` and
`result.html` in the output directory. This means the demo observed its own
CID in the built-in single-origin loopback fixture. The recorded triage is
`unreviewed`; it is not a vulnerability finding or a claim about scanner
accuracy. For a fresh run, choose a new output path rather than deleting the
previous evidence.

## Demo 2: K01 stored comment, fix and retest

The case starts separate, disposable local fixtures for its five controls. It
preserves its new evidence directory and stops if that directory already
exists.

```powershell
.venv-portfolio\Scripts\python.exe cases/k01-stored-comment/check_repro.py `
  --profile local --output .dxa/k01-portfolio-demo-2026-10-17
```

On macOS or Linux, run:

```console
.venv-portfolio/bin/python cases/k01-stored-comment/check_repro.py \
  --profile local --output .dxa/k01-portfolio-demo-2026-10-17
```

Expected result: exit code 0, `5/5` controls and `5/5` fixture ports closed.
The positive control uses a fresh CID; JavaScript-disabled, fixed-output,
JSON-only and ordinary-dialog controls are negative controls. The fixed
renderer applies HTML text-context encoding. This is a local training fixture,
not a real product, CVE, privilege escalation, or general bot-execution claim.

The [K01 case record](../cases/k01-stored-comment/README.md) explains its
source, storage, reader context, fix, limitations and historical acceptance.
The existing accepted run and hashes are in
[`audit/r5-final-acceptance-2026-10-16`](../audit/r5-final-acceptance-2026-10-16/README.md).
The wheel metadata, clean-venv gate and packaged demo evidence are in the
[R6/R9 final-source audit](../audit/2026-10-16-r6-r9-final-source/README.md).

## Evidence boundaries

- Do not replace `--profile local` with `--profile ci` on Windows. The CI
  profile requires Linux and Python 3.12.
- Browser absence, timeout, error or partial output is a failed run, not a
  negative result. Keep each run's result directory for review.
- `execution-observed` belongs only to that run's local fixture. Triage remains
  separate; a callback, reflection or dialog alone is not execution proof.
- The `0.1.0` candidate is not tagged or published. Installation from this
  checkout does not mean it is available from PyPI.
- Product coverage, broad detection accuracy, reverse-proxy/DNS deployment,
  external targets and non-HTTP network isolation are outside this demo.
