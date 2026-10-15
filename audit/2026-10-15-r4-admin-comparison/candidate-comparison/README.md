# R4 bounded competitor attempt — 15 October 2026

## Result

This experiment is **inconclusive** and does not satisfy R4 competitor
acceptance. It selected eight tool/case/repetition runs: four completed and
four timed out. Both dxadyn escaped-control runs completed with zero candidates.
Its two raw runs emitted one stored HTML reflection candidate each and exited
1. Source review confirmed that dxadyn uses exit 1 for findings; paired with
each non-empty JSON report, these are completed candidate scans. They do not
prove browser execution. All four Dalfox runs hit the 20-second outer process
timeout and exceeded the scanner request-attempt budget. No TP/FP/FN score or
tool ranking is valid.

## Setup and boundaries

Dalfox v3.2.4 release commit `da19527` was downloaded to a temporary directory
after approval, verified against the official release asset SHA-256
`28100d9355a1c767facd571a180d08b87d4de61167b3db99d56e4d8a6601d69a`, and
removed after the run. The executable hash, adapter/test/fixture hashes,
runtime, case order, and per-run outcome accounting are in
[`comparison.json`](comparison.json). OAST was not enabled; scanner subprocess
proxy variables were removed. Every target was a new fixture bound to
`127.0.0.1` with a new in-memory store and ephemeral broker cookie.

The corpus contains a raw positive and escaped negative for the existing
writer-to-reader-admin stored path. Both scanners received the same bridge
cookie. The fixture maps it internally to two roles; this is not independent
authentication or real login coverage. A separate local Chrome oracle tests
the same raw/escaped behavior, but scanner candidates are not correlated to
the browser's random CID and cannot be scored as execution accuracy.

Each run had a server-side limit of 20 forwarded requests, 2 requests/second,
one in-flight request, a 20-second wall window, and a 20-second outer process
timeout. Dalfox attempted 28 requests per run: 20 were forwarded and eight
received local 429 budget rejections. Its retry behavior continued until the
outer timeout. Client request timeouts also differed (Dalfox 2 seconds,
dxadyn 15 seconds). These tool/runtime differences and failed runs make this
an operational failure record, not a controlled accuracy comparison.

## Reproduction and artifacts

After obtaining and verifying the same temporary Dalfox asset, run from the
repository root:

```powershell
py -3.10 bench/r4_compare_local.py --dalfox <verified-dalfox.exe> --output <new-output-directory>
py -3.10 -m pytest bench/test_r4_compare_local.py -q -p no:cacheprovider --tb=short
```

The exact observed output, status codes, sanitized commands, and scanner logs
are retained under `runs/`. Initial focused validation passed 8/8 before a
post-run source review corrected the interpretation of dxadyn exit 1. The
coordinator added a regression for that finding exit and split browser tests
into their CI module. Final combined validation passed **9/9** comparator,
accounting, and browser-oracle tests on Python 3.10.11, Playwright 1.63.0, and
local Chrome 155.0.8059.79. These tests validate accounting and fixture
behavior; they do not turn incomplete Dalfox runs or reflection candidates
into execution findings.

## Acceptance still open

The R4 protocol requires completed, comparable runs and common proof handling.
This experiment lacks scanner-generated CID correlation, independent scanner
authentication, and matching per-request timeout behavior; Dalfox also
exceeded the attempt budget and timed out. Do not publish a winner or scanner
accuracy claim from these records. The two-account fixture and its browser
oracle remain separate evidence; R5's independent-human repeat remains
deferred as requested.
