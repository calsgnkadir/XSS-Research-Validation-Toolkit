# R4 bounded comparator execution ? 15 October 2026

Base: `521efae94f70cd96da538210474c6f52dc844317`. This is candidate comparison,
not browser-execution accuracy, human vulnerability triage or a ranking.

## Root cause and corrections

Pinned Dalfox 3.2.4 `scan --help` states that `--scan-timeout` bounds injection
only; analysis runs beforehand. HTTP429 is always retried, and the payload
cap excludes other phases. The previous20-request/20-second experiment entered
budget rejection/retry and timed out. The revised explicit parameter scan adds
`--skip-discovery --encoders none`; all participants receive identical hard
limits:200 forwarded requests,2 requests/second, concurrency1,120-second wall
and outer process limits,15-second client request timeout. These limits and
tool flags were fixed before run-01; fresh fixtures isolate every repeat.

The harness now rejects existing output directories before running any binary,
verifies `--version`, emits schema /2 with per-row identity and sanitized
artifact SHA256 links, and rechecks wall expiry after server pacing sleep.
Reports with partial-scan metadata or error/skip events cannot complete.

Official pinned [Dalfox source](https://github.com/hahwul/dalfox/blob/v3.2.4/src/main.rs#L449)
defines exit0 clean,1 findings,2 error. Run-01 incorrectly treated Dalfox exit1
as error; its original manifest and artifacts remain unchanged. Corrected
known-tool exit handling was tested and run-02 is a new experiment, not a
reclassification represented as a new run. Dalfox's raw V and escaped R
labels remain third-party candidate assertions, never execution proof.

## Tool provenance and diagnostic deviation

Official release archive `dalfox-v3.2.4-windows-x86_64.zip` SHA256:
`28100d9355a1c767facd571a180d08b87d4de61167b3db99d56e4d8a6601d69a`.
The archive was checksum-verified and extracted under ignored `.dxa`; no
system installation or background service was created. Binary SHA and actual
`dalfox 3.2.4` version output are in each manifest. No OAST option was enabled.
The first guessed archive name returned404 and was replaced by the exact
asset name from the official release API.

A diagnostic command incorrectly used positional `version` instead of
`--version`. Dalfox interpreted it as `http://version/`, reported DNS resolution
failure and no findings. No reachable external target was scanned. This was
not part of either comparison, was not retried, and is not counted as a lab
result. All subsequent scanner commands used verified option syntax and
explicit127.0.0.1 fixture targets.

## Validation and remaining scope

`py -3.10 -m pytest bench/test_r4_compare_local.py bench/test_r4_comparison_fixture.py -q -p no:cacheprovider --tb=short`
passed20 tests, zero failures/errors/skips (Python3.10.11; installed Playwright
Chromium fallback). Meaningful regressions cover preserved old output, wrong
version, unknown-tool exit1, pinned findings exit1, partial reports, and a
paced POST crossing the wall deadline without writing its body.

Run command (each output must be new):
`py -3.10 bench/r4_compare_local.py --dalfox <verified-binary> --output <new-directory>`.
Run-01 is retained as a failed accounting attempt; run-02 is the final source
run. Source/test hashes and command/runtime evidence are in the manifests.

Both scanners use the same ephemeral fixture broker cookie, not independent
scanner login flows. Scanner-generated payloads are not bound to a common
CID/browser proof adapter. Retry implementations differ; server budgets cover
all attempted work but do not make internal strategies identical. The
separate raw/escaped browser fixture oracle is not candidate proof. General
R4 comparison acceptance stays open; R5 human repeat remains deferred.

## Final live result and post-run review

Run-02 completed8/8, errors0, timeouts0, incomplete0 (exit0). Both raw
dxadyn runs returned1 reflection candidate, both escaped runs0. Dalfox
returned1 candidate in each run: raw V assertions and escaped informational
R reflections. These are not FP/TP counts. All budgets stayed within limits.

After run-02, coordinator review requested defensive handling of malformed
event containers/invalid UTF8 and masking an absolute report output path in
the command manifest. These parser/privacy safeguards were unit tested after
the live run; its recorded adapter hash intentionally identifies the pre-review
source that actually ran. The live experiment was not repeated for these
malformed-input safeguards.

Final post-review focused validation: **25 passed**, zero failures/errors/skips.
Coordinator integration with the independent QA gate and existing CI acceptance
module: **207 passed**, zero failures/errors/skips. The QA checker separately
passed **72 tests**; these suites overlap and are not additive.
Final source hashes: post-review-sources.json. Live source hashes remain in run-02/comparison.json.
