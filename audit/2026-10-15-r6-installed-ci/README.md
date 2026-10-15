# R6 installed-wheel CI gate

Base commit: `521efae94f70cd96da538210474c6f52dc844317`.
Coordinator delivery on Windows / Python 3.10.11, 15 October 2026.

CI previously installed the package but only ran help commands. The reusable
`bench/check_installed_cli.py` now runs from a temporary directory outside the
checkout, verifies all nine imported modules live inside the supplied venv,
and matches their bytes to both source and the supplied wheel. CI builds a
wheel, installs it offline into a fresh venv, runs this mandatory check and
uploads the wheel with its SHA-256-bound JSON result.

Local validation built a fresh wheel using the existing build environment,
created `.dxa/r6-ci-venv`, and installed the wheel with `--no-index --no-deps`.
Seven checks passed: three CLI help commands, static config override, dynamic
config depth, explicit CLI depth override, and invalid config without secret
echo. Dynamic JSON/HTML depth and fixture thread cleanup were verified.
All nine installed/source/wheel hashes matched. No browser execution is
claimed by this new gate; the prior packaged browser-demo evidence is separate.

```console
py -3.10 bench/check_installed_cli.py --bin-dir .dxa/r6-ci-venv/Scripts --wheel .dxa/r6-ci-wheel/dxa_research_toolkit-0.0.0.dev0-py3-none-any.whl --output audit/2026-10-15-r6-installed-ci/acceptance.json
```

A second wheel with changed `dxa.py` bytes was rejected with exit 1 and
`dxa wheel mismatch`, before a success artifact could be written. Original
installed wheel and source were preserved. See `negative-control.json`.
The test helper derives from the historical R6 installed smoke script;
historical evidence and scripts were not rewritten.

This is development package readiness, not release approval. Version remains
`0.0.0.dev0`. R4 comparison acceptance and the deferred R5 independent human
repeat remain separate requirements. No release tag or publication occurred.
Remote CI run **38790053904** completed successfully (all three jobs).
The Linux installed-wheel step passed all seven checks and uploaded the wheel
plus acceptance JSON as artifact `r6-installed-package`, ID `12000435488`,
ZIP SHA-256 `a19a550578ad31a377b427633948a60fb1d1bd6a74f37742bcaf327c08c3cb7b`.
The GitHub artifact connector returned a file reference rather than local ZIP
bytes, so its contents were not independently reopened; job logs and metadata
were checked. The required browser artifact gate passed 186 tests with zero
skips/errors and corpus17/17 TP8 FP0 FN0. See [remote-ci.json](remote-ci.json).
