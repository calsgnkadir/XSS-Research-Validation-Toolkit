# R4 — HTTP benchmark completion gate

Starting source: `3e34515774b16a20c99aa6761f425f2bb36aebdf`.
The coordinator fetched origin and verified a clean tree and 0/0 divergence.

## Root cause and bounded change

Source review found `bench/run.py::run_dxadyn` classified a run from console
summaries. `dxadyn.py` can print “No unencoded reflections found” and exit 0
after a failed fetch. Its structured R1 report separately records the transport
error. The old adapter discarded those events, called the observation completed,
and allowed the scorer to turn an unperformed positive case into an FN.

`run_dxadyn` now requests a fresh temporary `--json-out` report. Only the
expected reflected/stored R1 mode with well-formed candidate/event collections
can supply candidate counts. An error event returns `error`; a skip event or
nonzero skipped-submit counter returns `skipped`; missing/malformed reports
return `invalid`. These statuses do not enter TP/FP/FN scoring and fail strict
acceptance. This applies even when a partial run already has a candidate.
Timeouts and process failures retain their existing non-completed outcomes.
The legacy console parser retains display counts but cannot grant completion.

No scanner CLI exit-code contract or R1 schema was changed. Counts remain
candidate observations, never confirmed XSS or browser execution evidence.
Temporary reports are discarded after parsing; their raw content is not copied
to this public evidence package. External scanner adapters are outside this fix.

## Ownership and checks

Native `scanner_engine_specialist` task `http_fix` owned only `bench/run.py`,
`bench/test_http_completion.py`, and this audit note. Other workspace changes
belong to the coordinator/other specialists and are preserved. Persistent TOML
existence and reading it do not independently prove configuration inheritance.

After the first coordinator run exposed the old mock origin-root 404, ownership
was extended to `bench/mock_target.py` and `bench/test_bench.py`. Stored auto-check
always visits `/`; the fixture now serves a harmless 200 HTML index there.
The gate still rejects every error/skip. The integrated smoke test explicitly
selects all three mock cases and requires 3/3 completed, zero errors/skips and
strict acceptance, rather than allowing optional Docker skips in its surface.

The new regression file includes real disposable loopback connection refusal
for reflected and stored modes, real reflected/stored positives and an encoded
negative control, partial-report error/skip cases, malformed/missing reports,
and the old console-only false-completion trigger. A completed negative still
produces an FN when deliberately paired with a positive label.

The coordinator's first integration run was **111 passed, 2 failed** out of
113: both failures exposed the fixture's 404 root. This failed run is not
acceptance; the final fixture/gate combination must be rerun.

Command for the coordinator's acceptance run:

```powershell
py -3.10 -m pytest bench/test_http_completion.py bench/test_bench.py -q -p no:cacheprovider --tb=short
```

Specialist's first attempted `bench/test_bench.py` launch failed before Python
startup because WindowsApps execution was denied by the sandbox. It is not a
test result. The coordinator runs the authorized local checks and records the
actual outcome in the final pinned acceptance package. No external target,
Docker data mutation, package publication or hosted CI was run by this task.

Coordinator final frozen acceptance: **115 passed**, zero failure/error/skip,
including `bench/test_runner_isolation.py` alongside the two files above.
The earlier 114-pass intermediate run preceded collection of the added 404
control; the final 115-pass run includes it. Strict CLI smoke with exactly
`mock-reflected-easy,mock-reflected-escaped,mock-stored-guestbook` completed
3/3, TP/FP/FN 2/0/0, exit 0 (`BENCH_STRICT=1`, `--no-history`). Runtime
source and test hashes are bound in the final acceptance package.

Reviewed implementation commit: `ccdf661abae8a887c30e78e9cbf644133c7f686e`.
[Full local acceptance and reproducible commands](../2026-11-03-release-acceptance/README.md).
