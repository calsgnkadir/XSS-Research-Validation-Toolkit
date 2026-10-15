# R6 installed-wheel readiness matrix

Run on 15 October 2026 from the existing checkout at base commit
`f12a7dd14dd29f02eff3fc9a018ddd6f41d98b49`, Python 3.10.11 / Windows.
The wheel was built from the current source with the existing local build venv,
then installed with `--no-index --no-deps` into a new isolated venv. The
commands below ran from `C:\xss`, outside the source checkout. No dependency
download or external target was used.

## Acceptance

The current wheel SHA-256 is
`929b8dd013eaec818c56e5ee89e40b5d076360b50e70984c60dd7ac880b5ac03`.
It reports version `0.0.0.dev0`, requires Python `>=3.10`, has no mandatory
dependencies, and declares the optional `browser` extra pinned to
`playwright==1.63.0`. It contains the expected nine Python modules and all
three console entry points.

The matrix passed all three installed `--help` commands and checked their
documented usage. `dxa` installed static config selected one high-confidence
finding; explicit `--min-confidence low` overrode config and returned two.
`dxadyn` was exercised against an ephemeral loopback HTTP fixture: config depth
1 crawled the child route, CLI depth 0 overrode it, JSON/HTML depth metadata
matched, and invalid config exited 2 without echoing a synthetic secret. The
`dxaprove` installed demo produced one matching browser canary in its
disposable loopback lab; its result remains `triage=unreviewed` and does not
confirm a vulnerability. `dxaprove --spec` is a separate proof input contract,
not a general scan config schema.

Focused static/dynamic config, mode, and report regressions: **109 passed**,
zero failures/errors/skips. These tests cover versioned JSON schema,
CLI/config/default precedence, safe escaping/redaction, and JSON/HTML output
identity. The exact command was:

```console
py -3.10 -m pytest tools/dom-xss-analyzer/test_dxa_config.py tools/dom-xss-analyzer/test_dxadyn_config.py tools/dom-xss-analyzer/test_dxadyn_report_identity.py tools/dom-xss-analyzer/test_r6_cli_modes.py -q -p no:cacheprovider --tb=short
```

The replay script and sanitized result are [check_release_matrix.py](check_release_matrix.py)
and [acceptance-final.json](acceptance-final.json). Earlier pre-documentation
run output is retained separately as `acceptance.json`; final evidence is the
`acceptance-final.json` file.

## Remaining gate

The package and documentation checks are locally ready, but the **overall R6
roadmap gate remains open**. ROADMAP R6 depends on R1–R5; broad R4 separate
admin-role/controlled-comparison acceptance and R5's independent human fresh
environment repeat are still open. The user deferred the R5 repeat for later.
No tag, publication, or release claim was made. The `0.0.0.dev0` package and
demo are development validation only; browser execution is not vulnerability
confirmation.
