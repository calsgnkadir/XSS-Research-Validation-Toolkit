# R4 separate scanner sessions — 16 October 2026

Base revision: `185083658865701851611dea556aab2f326cd6c1`. This local delivery
adds independently authenticated writer and reader-admin sessions to each
scanner run in the bounded R4 loopback comparison.

## Session and authorization contract

Each per-tool/per-case/repetition fixture creates fresh random writer and
reader-admin passwords, then performs two login requests. It receives two
distinct random session tokens. Before the scanner starts, role-specific
identity GETs must return the exact expected principal and role. Four negative
controls then verify that writer cannot read admin comments, reader-admin
cannot submit, and neither token authenticates as the other role. The same
identity checks run after scanning. A failed role check makes the run
incomplete.

The scanner CLIs accept a single cookie-header argument, so each scanner is
given both independently issued cookie names:
`writer_session=<token>; admin_session=<token>`. The fixture authorizes POST
`/comments` only from the writer cookie and GET `/admin/comments` only from
the reader-admin cookie. It never maps one bridge token to both identities.
The raw values are kept in memory only and are redacted from safe commands,
stdout, stderr and scanner reports before artifacts are hashed. Role evidence
records principal hashes, role labels and pre/post pass flags; it contains no
cookie values.

All login, identity-check, cross-role-control, scanner and post-check requests
share the same per-run fixture limits: 200 requests, 2 requests/second,
concurrency 1, 120-second fixture wall limit and 15-second scanner request
timeout. Each run used eight preflight requests (two logins, two exact-role
checks, four negative controls), then two postflight role checks. Thus scanner
work and auth setup are included in the common request/rate/wall budget.

The fixture binds to `127.0.0.1`, stores comments in memory and shuts down
after every run. No outside target or persistent application data was used.

## Live result

The cached Dalfox v3.2.4 executable was verified before use:

- version output: `dalfox 3.2.4`
- SHA-256: `5a48b938792c81ed610a2bcfde36827dcbc6c41cc2292c60fcc06c13a4b2ad3f`
- official release archive SHA-256, as recorded in the prior R4 audit:
  `28100d9355a1c767facd571a180d08b87d4de61167b3db99d56e4d8a6601d69a`

Command:

```powershell
py -3.10 bench/r4_compare_local.py --dalfox .dxa/r4-dalfox-execution/bin/dalfox-v3.2.4-windows-x86_64/dalfox.exe --output audit/2026-10-16-r4-separate-scanner-auth/run-01
```

Result: selected 8, completed 8, error 0, timeout 0, incomplete 0. Every run
passed writer and reader-admin identity checks before and after scanning and all
four cross-role controls. Each run's setup and post-check request counts are
visible in [comparison.json](run-01/comparison.json). Total requests ranged
from 12 to 33 per run; no fixture budget was exceeded.

The candidate output was:

| Tool | Raw case | Escaped case | Runs |
|---|---:|---:|---:|
| dxadyn | 1 candidate | 0 candidates | both repeats completed |
| Dalfox | 1 candidate | 1 candidate | both repeats completed |

These are scanner candidate counts. The escaped-case Dalfox row is a reported
candidate, not a confirmed false positive under the shared browser oracle.
Scanner-generated payloads are not automatically promoted to execution proof.
The exact stored strings are retained in the manifest for the separate CID
adapter; any payload without a unique embedded CID bound to executable code
remains inconclusive.

Manifest SHA-256:
`36413d8c5416f8e66ec4953f6db37a26c5a103b96b2264421dadd4e8ecd82fba`.
The manifest contains hashes for per-run stdout, stderr and report artifacts.
All credential strings are redacted before hashing. A regression checks that
the writer token, reader-admin token and full pair do not survive redaction.

The live manifest records adapter SHA-256
`da5958cce49c057980f68068ff3ead5ac5fff2efeabcf63c02527af2a6e3844e`,
fixture SHA-256
`9657633f2e7ea82a6e67ab481f8ee1fe75c4ce0cd97c89ed47550bf75cf442fe`, and
comparison-test SHA-256
`9a9ca2913603f8e0c823696e0eb54239c0198292bea1072c664e941624e7f294`.
After that run, the adapter gained a secret-free request trace containing only
method, fixture path, status and budget-rejection flag. This reporting-only
addition does not alter requests or session behavior; the focused suite was
rerun afterward. The 8/8 live result belongs to the adapter hash recorded in
the manifest, not the later trace-only source hash below.

## Local validation and source hashes

Focused command:

```powershell
py -3.10 -m pytest bench/test_r4_scanner_sessions.py bench/test_r4_comparison_fixture.py bench/test_r4_compare_local.py -q -p no:cacheprovider --tb=short
```

Result: 30 passed, 0 failures, 0 errors, 0 skips (Python 3.10 on Windows).

| File | SHA-256 |
|---|---|
| `bench/r4_comparison_fixture.py` | `9657633f2e7ea82a6e67ab481f8ee1fe75c4ce0cd97c89ed47550bf75cf442fe` |
| `bench/r4_scanner_sessions.py` | `0870bc9d838f18071c17ad3ce17dc2e2730e0af1e0a81393bda275e30ce72e03` |
| `bench/r4_compare_local.py` | `e56f46f7af860c85cda768cfa255894d21c1803fb2ef2ac1f4d8e02fdea8fed4` |
| `bench/test_r4_comparison_fixture.py` | `98a6d11ef6d318d26c2676b86e3914e634959b6ab0e5fad9e4e7774dfa3fc9cf` |
| `bench/test_r4_compare_local.py` | `9a9ca2913603f8e0c823696e0eb54239c0198292bea1072c664e941624e7f294` |
| `bench/test_r4_scanner_sessions.py` | `ae97cd0b877dcefe5f2526b86e3914e634959b6ab0e5fad9e4e7774dfa3fc9cf` |

## Limits

The local accounts prove the fixture's role separation and each CLI's use of
the supplied cookies. They do not represent a production identity provider or
independent operator-managed accounts. The cookie pair must be supplied as one
CLI option because both scanners expose one global cookie-header input; the
fixture enforces the relevant role separately at each endpoint. Request counts
and retry behavior differ between tools within the same shared limits.

This work does not establish a general R4 accuracy score or tool ranking.
Exact scanner-payload/CID browser correlation and independent human triage
remain separate acceptance gates. R5's independent-human repetition remains
deferred.
