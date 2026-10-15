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
`jaeles`, and `arjun`; no executable was found. The installed Python package
inventory exposed Playwright and Requests as support libraries, but no
competitor scanner. The repository's own scanner is the system under test and
was not treated as a competitor. No tool was installed or downloaded, and no
competitor was run. Consequently there is no equal-budget comparison or frozen
comparison manifest, and the ROADMAP R4 competitor criterion remains open.
The existing protocol remains the comparison contract; this audit does not
claim a winner or scanner superiority.

## Scope mapping

- ROADMAP R4: separate authenticated accounts, writer-to-admin blind stored
  submission/read path, independent HTTP and browser oracles, CID correlation,
  fixed negative, and disposable cleanup are covered by this narrow fixture.
- ROADMAP R4: controlled competitor comparison remains open because no local
  comparator was available and the protocol's common proof adapter/budget
  parity are not established.
- R5 independent human repetition remains deferred and open.
