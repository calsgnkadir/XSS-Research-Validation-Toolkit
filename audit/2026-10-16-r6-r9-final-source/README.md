# R6 final wheel and R9 local continuation

Run date: 2026-10-16, Windows / Python 3.10.11. Tests and wheel acceptance
were run on the working tree based on `main` at
`f89058e74194f60de8ec9cd3db701e6c6254253c`, before delivery. The tested
source was then committed and pushed as `f4d8bdf50dcdd8fc93814e9d10adcab650a30d5a`;
the remote `main` hash was verified equal.

## R6 technical acceptance

R6 was rerun from the final R9 source after the `dxadyn.py` warning fix and
`dxa.py` credential-literal masking change. Run: 2026-10-16 15:14:57 UTC,
Windows 10.0.26200, Python 3.10.11, Playwright 1.63.0, Chrome 155.0.8059.82.
The rebuilt wheel is `dxa-research-toolkit 0.1.0`, SHA-256
`d1151704ba4c5e6dbe91696f632040ad528947bf97b04dc765b585ef6c3729ad`.

A fresh temporary venv reused the locally installed Playwright via
`--system-site-packages`; the toolkit wheel itself was installed offline with
`--no-index --no-deps`. The installed-wheel gate passed **7/7** with **0
failures, 0 errors, 0 skips**. It checked all installed CLI help entrypoints,
static configuration and CLI override, dynamic depth configuration,
installed/source/wheel byte identity for all nine shipped modules, bounded
loopback requests, HTML/JSON depth consistency, fixture cleanup, and invalid
configuration secret omission. The installed `dxaprove --demo` exited 0 with
`execution-observed`, `triage=unreviewed` on the built-in disposable
single-origin loopback fixture. This is browser execution evidence, not a
vulnerability confirmation. `dxa.py` source/wheel/installed SHA-256 is
`36bfc0f768edea63e0d167d3bf2b56df6da493b558229ccfa4a75fead27aca7a`; all nine
module hashes are recorded in `acceptance.json`.

Metadata was also read directly from the retained final wheel (no rebuild and
no gate rerun). Its SHA-256 matched the recorded artifact above. The wheel
contains `Name: dxa-research-toolkit`, `Version: 0.1.0`,
`Requires-Python: >=3.10`, `Provides-Extra: browser`, and
`Requires-Dist: playwright==1.63.0; extra == "browser"`. This metadata check
was made from the source delivery recorded as `f4d8bdf50dcdd8fc93814e9d10adcab650a30d5a`;
the audit checkout HEAD at inspection was `dcd019d93e852cf26f3d562b0fd5f35f2435e7d0`.
The exact wheel hash and metadata output are recorded in `acceptance.json`.
Exact successful commands:

```powershell
py -3.10 -m pip wheel --no-deps --no-build-isolation --wheel-dir <temp wheelhouse> .
py -3.10 -m venv --system-site-packages <temp venv>
<venv>\Scripts\python.exe -m pip install --no-index --no-deps <wheel>
<venv>\Scripts\python.exe bench/check_installed_cli.py --bin-dir <venv>\Scripts --wheel <wheel> --output <new gate JSON>
<venv>\Scripts\dxaprove.exe --demo --browser "C:\Program Files\Google\Chrome\Application\chrome.exe" --output <new output directory>
```

The [final-source gate result](r6-installed-wheel-gate-final-source.json) and
[packaged demo result](r6-packaged-demo-final-source.json) are retained; the
[acceptance manifest](acceptance.json) binds the new wheel and mapped source
hashes. No dependency download, release tag or package publication occurred.
Hosted CI ran after this source snapshot was pushed; its results are recorded
in the Git delivery section below. The local
R6 install and demo acceptance are complete for this candidate snapshot; the
ROADMAP release tag/publication row remains outside this local acceptance.
## R9 implementation slices and local tests

- Callback storage no longer records client IP/X-Forwarded-For. New SQLite
  files use exclusive creation; existing callback/journal files receive
  read-only schema validation and are not repaired or rewritten. Callback and
  journal regressions: **103 passed**. The narrower callback boundary set
  passed **82** tests: loopback bind, Host/Origin/Sec-Fetch read gate,
  collection-only CORS, CID/list/body limits, timeout/incomplete body handling,
  proxy-header/privacy checks, generic SQLite 503, and legacy DB preservation.
- Bare DOM browser visits require a literal loopback IP, enforce exact
  same-origin HTTP scope, block redirects before following them, and report
  blocked/unsupported WebSocket attempts without retaining paths or query
  strings. The new direct/redirect/WebSocket and previously failing dialog/XHR
  regressions passed together: **5 passed** on Chrome / Playwright 1.63.
- Mutation no-op/repeated shapes are reported as shape accounting, not bypass
  coverage. Stored-auto seeds are same-origin, count against the page budget,
  and report seed sources and multiple-canary totals; manual check URLs cannot
  be mixed with autonomous discovery. Browser decode-chain fixture and full
  dynamic suite after privacy fix: **175 passed**; context matrix tests then
  passed in `test_dxadyn.py` **182/182** and `test_dxadyn.py` +
  `test_http_evidence.py` **194/194**.
- Compose documentation and static tests distinguish Docker daemon readiness
  from target application acceptance and verify pinned images/loopback binds.
  CI self-scan/acceptance plus compose suite: **133 passed**.
- The shared JSON/HTML evidence adapter's privacy suite passed **23** tests:
  known credential keys, URL userinfo/query/fragment, event URLs, escaping,
  and non-mutation. It does not guarantee redaction of arbitrary free text,
  custom secret keys, or path segments. CLI regressions now mask values in
  clearly credential-labeled assignments and Authorization Bearer literals in
  both legacy `dxa --json` snippets and terminal snippets; unrelated source
  and the finding-list schema remain unchanged. A malformed `dxadyn --header`
  warning also no longer echoes the supplied value. The `dxa.py` and `dxa2dyn`
  bridge suites passed **58/58**, including verification that parameter-hint
  extraction survives redaction. `--json-out` omits raw source and retains its
  fingerprint. Arbitrary free text/custom field names remain outside the
  redaction guarantee.

### Intermittent full DOM suite results

The complete `test_dxadom.py` suite did not finish with a clean pass in four
runs: **77 passed / 3 failed** (dialog alert, dialog timestamp, XHR auth),
**79 passed / 1 failed** (`test_route_capture_pushstate`), and **78 passed / 2
failed** (dialog prompt, mixed runtime/static route capture), then **70 passed /
10 failed** in a further isolated 270.63-second run. The last run failed on
page-error, DOM sink, dialog, and eval observations; most failures showed
fixture-side `ConnectionAbortedError`, and two had `goto` 15-second timeouts.
The two latest previously failing cases passed together in a focused rerun
**2/2**. A narrow rerun of the four latest failures then passed **6/10**; its
 four failing cases (`document.write`, prompt, multiple dialogs, and onerror
dialog) passed immediately afterward in a focused rerun **4/4**. Their fixture
servers again reported `ConnectionAbortedError`. The browser specialist found
no deterministic `route.fetch` or context-shutdown defect and made no code
change. This was the status before the 17 October fixture follow-up below.

## R9 DOM fixture follow-up — 2026-10-17

The browser specialist used isolated A/B trials to locate the intermittent
failures in serial local HTTP test fixtures. The prompt test failed **5/5**
with the serial dialog server and passed **5/5** with a threaded dialog server.
The `document.write` sink test failed **5/5** against its serial fixture, with
the fixture reporting `ConnectionAbortedError`. Request diagnostics exposed
only local paths and were removed after the cause was isolated.

Only `tools/dom-xss-analyzer/test_dxadom.py` changed. All local fixture servers
now use `ThreadingHTTPServer`; teardown shuts down and closes each server,
joins the serving thread, and asserts it exited. Browser scope and test oracles
are unchanged; `dxadom.py` has no diff. On base checkout
`dcd019d93e852cf26f3d562b0fd5f35f2435e7d0`, the historical failure/scope
selection passed **14/14** (66 deselected, 58.68 seconds), then the full Chrome
suite passed **80/80** with zero failures or skips in 91.29 seconds. The updated
test file SHA-256 is
`a53e3e6a1c8273336f9e1a82d3575a3c041b5613786b8c76cd407889398a3879`.
This is local test-fixture stability evidence, not a production analyzer fix.
At the time of this result the fixture change was uncommitted, so it had no
hosted CI result; R9 remains open pending Git delivery and hosted validation.

The first dynamic suite run also had one jitter-bound failure while other
long-running tests were executing; an isolated full rerun passed **175/175**.
Treat that failure as environment contention, not a code pass; it remains in
the run history.

The local validations do not complete general R9. Callback checks use
loopback and temporary/in-memory SQLite; production reverse-proxy/DNS
deployment was not tested. The declared browser contract does not promise a
general non-HTTP sandbox; WebSocket is blocked/reported and other non-HTTP
channels are explicitly unsupported, so a separate adapter is not required by
this scope. Docker fixtures without target-specific bootstrap/login/lesson
adapters remain explicitly unready; this is the accepted operational guard,
not proof those targets work. Scoped report/credential masking and the
variant/context matrix have local test acceptance. At this snapshot R9 remained
open because the newly passing local DOM fixture change still needed Git
delivery and hosted CI; the final delivery below supersedes that status.
The previous full-suite failures remain historical run results; the 17 October
threaded-fixture rerun is the current local DOM acceptance.

## Local-only follow-up before final delivery — 2026-10-17

The R9 threaded-fixture DOM test change was delivered as commit
`221baa5621fc26a8eb581b4d88410b2e0a66e77b`; `origin/main` matched. Its
general CI run `38974413648` had opt-in Playwright success, while the analyzer
and required authenticated browser proof jobs failed. K01 Linux run
`38974413706` succeeded. Job log retrieval returned HTTP 403, so the exact
hosted failure causes and artifact contents were not verified.

After that CI run, two test-only fixes were added locally: the direct-eval
browser proof uses a disposable literal-loopback HTTP fixture, and the
stored-auto report-mode mock supplies the real probe's full metadata contract.
The direct-eval isolated regression changed from 1 failure to 1 pass; the exact
11-file Chrome acceptance suite then passed **218/218**. The full analyzer
suite passed **788**, skipped **38**, failed **0** in 183.55 seconds on Windows
Python 3.10.11. Quiet pytest output did not identify the skipped tests. At that
point the two files were not part of `221baa5` and had no hosted result. This
interim state was superseded by the final delivery below.

## Final R9 delivery — 2026-10-17

The two test-only fixes and their validation records were delivered as commit
`3a386eefbfa61e494f1bcb2ae6dadcf4d1c4bf7f`; the remote `main` ref matched.
General CI [run 38977151511](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38977151511)
passed all three jobs. K01 Linux
[run 38977151588](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38977151588)
passed. The bounded R9 hosted acceptance is complete. CI artifacts were not
independently downloaded, and the declared scope does not claim a general
non-HTTP network sandbox, reverse-proxy/DNS deployment proof, or general
product accuracy.

## Source hashes

The SHA-256 digests for modified source, tests, and documentation are in
[`acceptance.json`](acceptance.json). The tested source was delivered in commit
`f4d8bdf50dcdd8fc93814e9d10adcab650a30d5a` and the remote hash matched. General
CI run `38923418347` had the opt-in browser harness succeed but the analyzer
test and required authenticated browser proof jobs fail; K01 Linux run
`38923418259` succeeded. Failed logs and artifacts were not independently
retrieved, so no specific failure cause or artifact contents are claimed. This
source-hash and CI record describes the older `f4d8bdf` snapshot. The later
`221baa5` and `3a386ee` deliveries and final DOM/R9 acceptance are recorded in
the dated follow-ups above.
