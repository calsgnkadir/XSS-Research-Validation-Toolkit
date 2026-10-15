# R4 two-account admin fixture and local comparison inventory

Base checkout: `f12a7dd14dd29f02eff3fc9a018ddd6f41d98b49`, branch `main`.
This is a bounded R4 fixture delivery. R5's independent-human repeat was
explicitly deferred and was not used as evidence here.

## Two-account blind stored path

`bench/r4_admin_fixture.py` starts a new HTTP server on `127.0.0.1` with a
random port and an in-memory store. Separate cookie jars authenticate a
`writer` and `reader-admin`. The writer can submit `/comments` and receives only
`accepted`; the response does not include the stored body or CID. The writer
cannot read `/admin/comments`. The reader-admin can read stored submissions but
cannot submit. Anonymous read is 401. These status and store assertions form an
HTTP authorization/state oracle independent of any scanner output.

`bench/test_r4_two_account_fixture.py` submits a random CID in an image error
handler payload. The browser test signs in as reader-admin, reads the stored
page, and checks the existing `window.__dxaProof` value equals that exact CID;
the test does not execute the payload via page evaluation. The escaped route is
the fixed negative control and must not expose the CID as executed proof. The
fixture binds only to loopback, uses no persistent data, shuts down its server,
and joins its thread during test cleanup.

## Local validation

Command (local Windows, Python 3.10.11, Playwright 1.63.0, Chrome 155.0.8059.79):

```powershell
$env:DXA_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
py -3.10 -m pytest bench/test_r4_two_account_fixture.py -q -p no:cacheprovider --tb=short --junitxml=audit/2026-10-15-r4-admin-comparison/pytest.xml
```

Result: **3 passed, 0 failed, 0 skipped**. Two parameterized browser cases
covered raw execution and escaped no-execution; one HTTP case checked account
separation and blind submit. The initial test runs failed on test-fixture
credential mapping and cookie parsing; both fixture-only defects were fixed
before the passing run. Hashes and runtime are in [acceptance.json](acceptance.json).

This proves the behavior of the purpose-built local fixture, not a real product,
scanner accuracy, privilege escalation, or a vulnerability in any target.

## Competitor comparison status

The local PATH inventory checked `xsstrike`, `dalfox`, `wapiti`, `nikto`,
`jaeles`, and `arjun`; initially no executable was found. A checksum-verified,
temporary Dalfox 3.2.4 release binary was then downloaded to `%TEMP%` after
approval. It was not installed system-wide. The attempted comparison uses that
binary against repository `dxadyn`; raw commands, logs, and run records are in
[`candidate-comparison/`](candidate-comparison/).

The comparator was Dalfox v3.2.4 (release commit `da19527`), downloaded as a
temporary Windows x86_64 release asset. The official asset SHA-256 was
`28100d9355a1c767facd571a180d08b87d4de61167b3db99d56e4d8a6601d69a`; the
extracted executable SHA-256 is recorded in the run manifest. The temp copy was
removed after the experiment. OAST was disabled and proxy variables were
removed for scanner subprocesses; the fixture bound only to `127.0.0.1`.

The first experiment is **inconclusive**. Of 8 selected runs, 4 completed and
4 timed out (see `comparison.json` for per-run accounting). Both escaped
`dxadyn` control runs completed with zero candidates. The two raw `dxadyn` runs
printed one stored HTML reflection candidate each and exited 1. Source review
confirmed that exit 1 is dxadyn's documented finding status; because both runs
also had non-empty structured findings, they are completed candidate scans,
not errors. This is candidate evidence only, not browser execution or a
confirmed vulnerability. All four Dalfox runs timed out at the outer 20-second
limit. They generated 28 request attempts each: 20 forwarded requests and 8
local 429 budget rejections, despite one-request concurrency and the configured
2 requests/second rate. The harness records selected/completed/error/timeout
separately and tests finding-exit, budget, timeout, and error outcomes.

The fixture enforces the same maximum forwarded request count (20), rate
(2/s), concurrency (1), and outer process wall limit (20s) for each tool. The
client request timeout differs (Dalfox 2s, dxadyn 15s), and the tool behavior
under the shared request gate also differed. Scanner inputs use the same
ephemeral broker cookie, which maps internally to writer and reader-admin
fixture roles; this is not independent login/session coverage. The scanner
candidate output is not correlated with scanner-generated CIDs or the separate
browser execution oracle, so there is no TP/FP/FN score or tool ranking. The
browser oracle remains separate from these candidate rows. ROADMAP R4's
competitor-comparison acceptance remains open.

## Scope mapping

- ROADMAP R4: separate authenticated accounts, writer-to-admin blind stored
  submission/read path, independent HTTP and browser oracles, CID correlation,
  fixed negative, and disposable cleanup are covered by this narrow fixture.
- ROADMAP R4: a pinned competitor was attempted on loopback, but the comparison
  is inconclusive because all Dalfox runs timed out and exceeded the attempt
  budget; common proof adapter and independent authentication requirements also
  remain unsatisfied.
- R5 independent human repetition remains deferred and open.
