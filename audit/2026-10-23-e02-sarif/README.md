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

Delivery commit `119d7acd837072b1b5f95549780f78e36682dd0b` was pushed to
`origin/main`; a subsequent fetch confirmed HEAD equals origin/main. General
CI run `39952400914` and K01 Linux run `39952400880` started for that exact SHA.
K01 Linux, required proof and optional browser jobs completed successfully.
The main analyzer job failed **880 passed / 62 skipped / 1 failed**: Git's
line-ending normalization changed the original CRLF schema bytes to LF on
Linux, breaking the strict provenance digest. `git ls-files --eol` confirmed
`i/lf w/crlf`. The follow-up adds a narrowly scoped `.gitattributes -text`
rule and re-stages the original upstream bytes; the digest oracle remains
strict. The Linux installed-package gate passed all nine controls before the
test-suite failure. No downloaded-artifact review is claimed.

After applying the attribute and explicitly re-staging the schema, Git reported
`i/crlf w/crlf attr/-text`. The staged blob and raw working file both had Git
object ID `534d35da2b8450502d9256a6c699dfe40f5b1ed5`, proving the index holds
the exact verified file bytes. The file-scoped whitespace rule recognizes CRLF
without disabling other whitespace checks. Focused follow-up command
`py -3.10 -m pytest tools/dom-xss-analyzer/test_sarif.py -q -p no:cacheprovider --tb=short`
passed **116/116** in 27.46s. Runtime source and strict digest oracle are unchanged
from the 468-test local acceptance; this follow-up corrects Git checkout bytes.

Fix commit `9769a20002c81270b17d1ec192a9b2fa4e33bfc2` was pushed and verified
equal to origin/main after fetch. General CI `39954873774` main job succeeded:
**881 passed / 62 skipped**, then 94 required negative controls and 522
benchmark tests passed. Installed-wheel acceptance passed nine controls;
self-scan and strict benchmark smoke steps also succeeded. K01 Linux
`39954873803` and optional browser job succeeded. Required authenticated-browser
job was still running at this check. These are hosted step/log observations;
artifacts were not downloaded or reviewed.

The vendored OASIS schema validates SARIF structure offline, not hosting-service
support. No code-scanning upload, browser execution, vulnerability confirmation,
external target scan, release replacement or PyPI publication occurred. Raw
URLs, reasons, observations, evidence links and identifiers are omitted.
Only safe relative file paths with positive integer lines become locations;
absolute static paths retain result rows without a location. Relative paths
can still contain private names. See [SARIF.md](../../tools/dom-xss-analyzer/SARIF.md).
