# R6 dynamic CLI config and release preparation

Base checkout: `2abcd51`, main matched origin/main and was clean when work began.
The native Report specialist owns the dynamic CLI/config tests and this audit;
the coordinator owns progress documents, integration and Git delivery.

## Change and contract

`dxadyn --config FILE` reads a UTF-8 JSON object, including PowerShell UTF-8 BOM.
It accepts only:

```json
{"schema_version": 1, "depth": 1, "parallel": 1, "rate": 0}
```

| Key | Accepted value | Applicable mode | Default |
|---|---|---|---|
| schema_version | Integer 1, required | All | None |
| depth | Integer >= 0; boolean rejected | Reflected with positional URL | 0 |
| parallel | Integer >= 1; boolean rejected | Reflected or stored | 1 |
| rate | Finite JSON number >= 0; boolean rejected | HTTP modes, including auth | 0 (unlimited) |

Explicit CLI values take precedence over valid config values, then existing
defaults apply. An explicit zero remains an override. Config validation happens
before merging, so a CLI override cannot conceal an invalid config file.
Unknown keys, duplicate keys, bad version/types, unreadable/invalid JSON and
irrelevant tuning options return exit 2 before target/session/browser I/O or
report writes. Errors do not echo config paths, keys, values or raw content.
Targets, authentication, output paths and arbitrary scanner options are not
accepted config fields. A schema-only config is valid for DOM availability;
HTTP tuning on DOM is rejected. Static `dxa` config remains its separate
`min_confidence` contract; `dxaprove --spec` remains unchanged.

The CLI now rejects negative depth and parallel values below one instead of
silently clamping/ignoring them. Worker help states the existing HTTP session
serialization constraint; worker count is not an HTTP throughput promise.

## Validation and execution environment

The specialist's unrestricted local commands failed with a setup-refresh error;
the preapproved `Get-Content AGENTS.md` and `git status --short` worked. Source
and required documents were read through the GitHub connector at exact base
commit `2abcd51`, after the coordinator verified the clean local checkout.
Absolute-path `apply_patch` writes succeeded and the coordinator checked the
local diff. Test/build execution is performed by the coordinator and must be
reported as such, not as an independently executed specialist run.

First coordinator proxy run (before the final help regression):

```console
py -3.10 -m pytest tools/dom-xss-analyzer/test_dxadyn_config.py tools/dom-xss-analyzer/test_dxadyn_report_identity.py tools/dom-xss-analyzer/test_r6_cli_modes.py -q -p no:cacheprovider --tb=short
```

Result: **100 passed**, no failures/errors/skips. The final source adds one
help-contract regression. Final counts and source hashes are recorded by the
coordinator in the acceptance record after running that source.

`smoke_installed.py` exercises three installed entrypoint help commands and
the dynamic config from a temporary directory outside the checkout. A new
loopback fixture checks config depth 1 versus CLI override depth 0 using actual
GET routes and matching JSON/HTML metadata. It also checks invalid config
exit 2 and omission of a synthetic secret from the error. Each fixture is
shut down and its worker joined. The fixture has no XSS finding and is not
browser execution evidence. Run against a newly built wheel in a fresh venv:

```console
python audit/2026-10-15-r6-config-release/smoke_installed.py --bin-dir <venv-bin> --output <new-acceptance.json>
```

## Resumed validation - 15 October 2026

The resumed native Report specialist read the actual checkout at `C:/xss/xss-github`.
The default command runner still failed setup refresh, but explicitly approved
escalated commands succeeded. The earlier proxy-only limitation above is historical;
the following results were run by this resumed specialist, not the coordinator.
Product config/test sources needed no further edits after review.

- Focused config/report/mode package: **101 passed, 0 failures/errors/skips**,
  3.45 seconds. [JUnit](focused.xml), [command and source hashes](validation.json).
- A fresh wheel was installed without dependencies/index into a new venv.
  All three entrypoint help checks, config depth 1, CLI override depth 0 and
  invalid-config privacy rejection passed: **6 checks**. Both local HTTP fixture
  workers closed. Installed `dxadyn` was imported with `-I`, under the venv,
  and its SHA-256 equaled the tested source. [Installed acceptance](installed-acceptance.json).
- Build initially failed under system Python because `bdist_wheel` was unavailable.
  Rebuilding with existing `.dxa/r6-package-venv/Scripts/python.exe` succeeded:
  `-m pip wheel . --no-deps --no-build-isolation --wheel-dir .dxa/r6-resume-wheel`.
  Fresh install: `.dxa/r6-resume-install-venv/Scripts/python.exe -m pip install
  --no-index --no-deps .dxa/r6-resume-wheel/dxa_research_toolkit-0.0.0.dev0-py3-none-any.whl`.
  Wheel digest and its nine Python module names are in validation.json.
- The first installed smoke failed on the second case: the first case's report
  `config.json` overwrote the helper's tuning file with the same name. The CLI
  correctly rejected report-only fields. Renaming the helper input to `tuning.json`
  resolved this fixture defect; the final six-check result is the successful repeat.
- README now describes dynamic config scope and CLI precedence. The smoke wheel
  predates that documentation-only paragraph; it is local validation evidence,
  not a publication artifact. Runtime sources match the installed identity check.

No browser execution, independent-human reproduction or remote CI run is claimed
by this narrow package. The coordinator owns combined integration acceptance.

## Release boundary

Packaging remains `0.0.0.dev0`, Python >= 3.10, no mandatory dependencies,
with optional pinned `playwright==1.63.0`. The helper stays in `dxadyn`, already
included among the nine packaged modules; no packaging framework was added.
This delivery adds no tag or published release. The R6 roadmap release gate
still requires the broader R4 acceptance and R5 independent second-human
clean-environment result, plus review of the remaining overall CLI/config,
documentation and release acceptance. Automated local/CI checks cannot stand
in for the R5 human criterion. This config work adds no new CVE capability claim.
