# E05 — measured textarea parser-context extension

24 October 2026. Base toolkit commit:
`532be7ac01e82fbe0612749ead6d3cb39f0be7e9` plus this delivery's working changes.

The user assigned three native specialists with separate ownership: report
specialist for current-status reconciliation, QA for corpus/negative-control
analysis and an independent browser oracle, and security researcher for the
small production change and transport regressions. The coordinator reviewed
the changes, owns ROADMAP and CI integration, and ran acceptance. Native role
calls were observed; persistent TOML loader behavior was not independently tested.
All specialists completed their tasks; no background work remains.

## Result and evidence

The existing 50 non-blind families and their base plus 18 mutations (950
generated attempts) produced no `dxss` elements when parsed inside textarea
RCDATA in the independent Chromium fixture. The existing textarea-opening
family also leaves its marker inside RCDATA. One inert `textarea-breakout`
closing-tag probe now creates a marker element outside the textarea. Its
HTML-escaped counterpart, default body, title terminator and previous
textarea-opening probes produce no marker elements in the navigation controls.

- [Independent context matrix and browser oracle](coverage.md).
- [Root cause, implementation, baseline and acceptance commands](implementation.md).
- [Machine-readable totals and tested source hashes](result.json).
- [Separate CI/status reconciliation](../2026-10-24-status-reconciliation/README.md).

Before production changes, transport/unit selection failed 6/6; three failures
were registry lookup failures rather than parser observations. Independently,
the browser selection reproduced the missing context: **1 failed, 5 passed**.
After the change, the eight-file combined selection passed **381 tests, zero
failures/errors/skips**, including all six browser cases. Windows / Python
3.10.11 / pytest 9.1.1; `DXA_REQUIRE_BROWSER=1`, existing Chrome, page JavaScript
disabled for the parser oracle. This was a selected suite, not a full-suite run.

The coordinator added the independent oracle to the required browser CI job.
Delivery commit `77199075a271227bce7cb6386d571f34f0213b5d` was pushed;
subsequent fetch confirmed local HEAD equals origin/main. Hosted execution is
separate from local acceptance. [CI 40083275086](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/40083275086)
main, required authenticated-browser and optional browser jobs succeeded.
[K01 Linux 40083275084](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/40083275084)
succeeded. Hosted logs: main suite **887 passed / 62 skipped** (98.64s),
required negatives **94 passed** (23.68s), benchmark **522 passed** (16.26s),
installed gate **9 controls passed**. Required browser acceptance passed
**224 tests** (104.62s); strict corpus, auth controls, demo and zero-skip
evidence gate also succeeded. These are metadata/log observations; hosted
artifacts were not downloaded or independently reviewed. Skips are not passes.

The current source wheel was built without build isolation and installed
without dependencies into a new local venv under ignored `.dxa/e05-package/`.
`bench/check_installed_cli.py` ran installed entrypoints outside the source
tree: **9 controls passed**, all 11 packaged module hashes matched source and
wheel. Wheel SHA-256:
`a7c3e89fd9257d6c4b3d1129822d5dd435c58279b812f3092ea65fc42d5a35d8`.
Commands, from the repository root (use a fresh directory when reproducing):

```powershell
py -3.10 -m pip wheel --no-deps --no-build-isolation . --wheel-dir .dxa/e05-package/wheels
py -3.10 -m venv .dxa/e05-package/venv
& '.dxa/e05-package/venv/Scripts/python.exe' -m pip install --no-index --no-deps .dxa/e05-package/wheels/dxa_research_toolkit-0.1.0-py3-none-any.whl
py -3.10 bench/check_installed_cli.py --bin-dir .dxa/e05-package/venv/Scripts --wheel .dxa/e05-package/wheels/dxa_research_toolkit-0.1.0-py3-none-any.whl --output .dxa/e05-package/installed.json
```

The gate verifies the installed module hashes; the native parser oracle above
tests source behavior. No installed-wheel parser execution is inferred.

## Boundaries

This accepts one E05 context extension, not the entire deferred E05 area.
The measurement is parsed marker placement, not JavaScript execution, WAF
bypass, sanitizer soundness, vulnerability confirmation or a product accuracy
score. HTTP output remains reflection/unreviewed. Default selection remains
`body`; explicit selection or `--variants all` includes the new family.

Only synthetic loopback fixtures and inert browser documents were used. No
external target, reserved A05 multipart test, existing lab data, published
release asset or PyPI package was changed. The R3–R6 bounded acceptance remains
closed. This delivery is unreleased.
