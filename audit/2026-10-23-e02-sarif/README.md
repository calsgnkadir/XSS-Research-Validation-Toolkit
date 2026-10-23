# E02 — bounded SARIF 2.1.0 export

Date: 2026-10-23. Toolkit base: `f0f42868fd05b1d7b5ba3a0228cf464b04fd5320`.
The initial local SARIF edits were preserved and completed. This implements
ROADMAP E02; it does not reopen R3–R6 or run the reserved A05 multipart test.

## Parallel implementation and review

Three native specialists were invoked with separate ownership:

| Task | Native role | Owned files |
|---|---|---|
| Export and evidence semantics | `report_frontend_specialist` | `dxa_sarif.py`, `SARIF.md` |
| CLI, packaging, CI | `scanner_engine_specialist` | `dxa.py`, `dxadyn.py`, `dxa2dyn.py`, `dxa_sarif_cli.py`, `pyproject.toml`, CI workflow; later installed CLI gate and its tests |
| Independent regression oracle | `qa_security_lab_specialist` | `test_sarif.py`, vendored schema and provenance README |

The coordinator reviewed production diffs, negative-control oracles and
packaging checks, and owns roadmap/status/validation integration. Native role
invocation was observed; independent TOML loader behavior was not verified.
Specialists did not commit or push. Their initial Python attempts could not
start because sandbox access to WindowsApps Python was denied. The coordinator
used approved elevated execution for the local acceptance run.

## Root causes and resulting behavior

The initial exporter silently ignored malformed events, allowed incomplete
envelopes, and marked skip-only reports successful. Strict saved-R1 validation
now rejects invalid input; errors and skips mark the SARIF invocation
unsuccessful. All four observation categories and five triage states remain
metadata on `review` / `none` results. Random finding IDs are represented only
by a correlation hash in properties, never cross-run SARIF fingerprints.

The offline `dxa-sarif` command converts a saved common report without a scan.
Invalid input returns 2 without replacing an existing output. Existing scanner
commands also accept `--sarif-out`; static-guided HTML reuses the same common
document. The installed package gate now checks four entrypoints and all 11
shipped modules against the source and wheel hashes, and executes offline
conversion outside the source tree.

## Acceptance evidence

Reproduce from the repository root:

```powershell
py -3.10 audit/2026-10-23-e02-sarif/run_validation.py
```

Windows / Python 3.10.11. The nine-file selection passed **468 tests**, with
zero failures, errors or skips. It includes all 116 SARIF cases plus existing
static, HTTP, shared-evidence, auth-contract, config and packaging regressions.
The first focused run was 115 passed / 1 failed: the missing-event-kind test
failed inside its helper before reaching production validation. QA corrected
the helper; the combined run exercises production rejection successfully.

The reproducible runner builds a wheel, installs it without dependencies in a
new temporary virtual environment, runs the installed acceptance gate and
writes [result.json](result.json) with test totals, module/source hashes and
the wheel digest. Installed checks use synthetic offline input and the gate's
existing loopback fixture only. Raw logs, temporary paths and wheel files are
not part of this evidence package. Local acceptance is separate from hosted CI.

## Boundaries

The vendored OASIS schema validates SARIF structure offline, not hosting-service
support. No code-scanning upload, browser execution, vulnerability confirmation,
external target scan, release replacement or PyPI publication occurred. Raw
URLs, reasons, observations, evidence links and identifiers are omitted.
Only safe relative file paths with positive integer lines become locations;
absolute static paths retain result rows without a location. Relative paths
can still contain private names. See [SARIF.md](../../tools/dom-xss-analyzer/SARIF.md).
