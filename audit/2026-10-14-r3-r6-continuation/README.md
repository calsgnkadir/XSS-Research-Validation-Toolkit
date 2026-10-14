# R3 header observation and R6 CLI/report continuation — 14 October 2026

Starting checkout: `d91238bfbfeb9736068dc6197738f464b5708312` on clean
`main`, equal to `origin/main`. Two native specialists worked on separate
files; the coordinator owned `dxa.py`, integration, and project documents.

| Owner | Roadmap task | Owned implementation |
|---|---|---|
| Scanner Engine | R3/R4 browser header observation | `dxadom.py`, `test_dxadom.py` |
| Report Frontend | R6 shared JSON/HTML evidence | `dxadyn.py`, `test_dxadyn_report_identity.py` |
| Coordinator | R6 static CLI config and shared report | `dxa.py`, `test_dxa_config.py`, docs and integration |

## Findings and changes

R3: code review at `dxadom.py:530-544,620-626` showed that the browser
summary retained every XHR/fetch header value and a separate map of raw
auth/CSRF values. That observation was not an authenticated-session proof.
The new summary retains only allowlisted header names, origin, path-only
route, and presence. URL userinfo/query/fragment and header values stay out
of the summary. `dxadyn --dom` prints names with an explicit no-replay limit.
Live positive/negative tests use only 127.0.0.1 fixtures. A path may itself
contain sensitive application data, so any shared summary still needs review.
Header presence does not prove token validity, role, CSRF protection or JS
execution. This change does not add automated header replay.

R6 report: `dxadyn` formerly normalized findings separately for JSON and HTML,
and reflected/stored metadata could differ between them. The CLI now builds
one versioned evidence document when output is requested and renders both
formats from it. No-output runs still skip normalization. The reflected CLI
regression checks one document call, shared finding ID/observations/metadata,
HTML escaping, credential redaction, and unchanged input. Other modes retain
their existing regression coverage; a full mode-by-mode report acceptance
matrix remains open. The static `dxa` CLI also builds one document for JSON
and HTML.

R6 config: the static `dxa` CLI now accepts a versioned JSON config with
`min_confidence`; precedence is CLI > config > built-in `low`. Unknown keys,
bad versions/types and unreadable JSON fail with exit 2 without echoing
content. A clean-wheel CLI trial exposed a Windows PowerShell UTF-8 BOM
failure. A red regression captured it; `utf-8-sig` loading fixed it. This
config contract is limited to `dxa`; full R6 config precedence across all
entrypoints and release packaging remain open.

## Local acceptance

Windows, Python 3.10.11. The coordinator ran real installed Chrome against
the local fixture by adding the executable path to `dxadom._CHROMIUM_HINTS`
in memory before importing the test module: **75 passed, zero skipped**.
The affected static/dynamic/evidence suite passed **293**, zero
failures/errors/skips:

```text
py -3.10 -m pytest tools/dom-xss-analyzer/test_dxa_config.py tools/dom-xss-analyzer/test_dxa.py tools/dom-xss-analyzer/test_r8_sanitizer.py tools/dom-xss-analyzer/test_dxadyn_report_identity.py tools/dom-xss-analyzer/test_dxadyn.py tools/dom-xss-analyzer/test_http_evidence.py tools/dom-xss-analyzer/test_r1_contract.py tools/dom-xss-analyzer/test_dom_cli_evidence.py -q -p no:cacheprovider --tb=short
```

The exact Chrome command and source hashes are in [acceptance.json](acceptance.json).
The two test totals are separate suites. `git diff --check` passed.

The updated 0.0.0.dev0 wheel was built from this checkout (SHA-256
`febb6d8171339cec78472ebd1e302849125e4b50a43e04715fe6d1c9c3a59ca5`),
installed into a new Python 3.10 venv, and run outside the source directory.
Installed `dxa`, `dxadyn`, `dxaprove --help` all exited 0. A BOM-prefixed
config selected high confidence and returned no findings (exit 0); an
explicit CLI low override returned one static candidate (exit 1), with the
same finding ID in JSON and HTML. Browser extra/demo was not repeated for
this wheel. The prior packaged browser demo remains historical evidence.

The code commit `a0cf34847fea69ebd19a71e97dbc550c3954986c` was pushed;
remote `main` matched and the worktree was clean. [Remote CI](remote-ci.json)
run 38637484190 passed all three jobs. The installed CLI, analyzer suite,
required R3/R4 artifact gate and optional real-browser harness steps were
successful. K01 Linux run 38637484214 also passed. Its artifact was not
downloaded again for this delivery; the K01 source was unchanged and its
independently inspected artifact belongs to the earlier recheck.

This delivery does not change R4's corpus scores, claim a real product
vulnerability/CVE, close the R5 second-human repeat, or release R6.
