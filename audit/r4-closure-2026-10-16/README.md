# R4 scanner candidate ↔ browser proof closure review

Date: 2026-10-16. Roadmap ID: R4 controlled competitor comparison. Native role:
`scanner_engine_specialist`, task `/root/r4_closure`. Base HEAD:
`d9db15ba2094b44c27870a311959de1d1dad15f6`. This is a source and
previously recorded local artifact review, plus a fresh focused regression run.
No scanner comparison or hosted CI was rerun for this review.

## Root cause and evidence

The comparator invokes dxadyn with `--variants body` and Dalfox with its own
payload generation (`bench/r4_compare_local.py:57-76`). It records report
finding counts separately from exact fixture storage readback (`:203`, `:225`),
and explicitly labels the output candidate-only (`:259-265`). The selected
dxadyn `body` suffix is a benign markup marker (`dxadyn.py:85`, `:532-554`),
so even an unescaped reflection does not imply JavaScript execution.

The strict oracle accepts a storage CID only when the *same stored string*
contains one `?cid=` value and a matching `window.__dxaProof='CID'` assignment
(`bench/r4_cid_oracle.py:11-27`). It observes that value in a separate
reader-admin browser context; the oracle never inserts code (`:130-184`). With
no eligible CID, a completed scanner run is inconclusive (`:80-81`).

I inspected the previously accepted, bounded loopback run at
`audit/2026-10-16-r4-separate-scanner-auth/run-01/comparison.json` (SHA-256
`81f292648af269e12d8b9e6073c74d69fe33a91a18709e9e716f2c2543e4d087`).
The manifest reports 8/8 completed scanner runs, under the shared request and
session limits. A content-shape count over its `stored_payloads` found:

| Scanner / case, two repeats each | Stored strings per repeat | Strings with `?cid=` | Strings with `window.__dxaProof=` | Report candidates per repeat |
|---|---:|---:|---:|---:|
| dxadyn / raw | 1 | 0 | 0 | 1 |
| dxadyn / escaped | 1 | 0 | 0 | 0 |
| Dalfox / raw | 6 | 0 | 0 | 1 |
| Dalfox / escaped | 9 | 0 | 0 | 1 |

These are counts of stored syntax in a historical scanner run, not new
execution tests. All eight rows lack the oracle's required CID binding. The
Dalfox escaped report row therefore cannot be called a confirmed FP, and the
dxadyn raw row cannot be called an execution TP. A separate harness canary
would prove the fixture, not the scanner's own submitted payload. Rewriting a
scanner payload after its run would change the tested attempt. Merely adding
IDs or parsing stdout cannot establish JS execution for the actual strings.

## Disposition and remaining acceptance

There is no source-only correction in the assigned comparator/oracle files
that can make these existing scanner submissions CID-bound executable proof
without changing scanner payload generation and the comparison protocol. I
therefore made no product-code change. An honest future R4 experiment needs a
predeclared, equal payload/proof protocol for both scanners, exact attribution
of each scanner submission, an isolated reader-admin browser observation for
each candidate, and retained error/timeout/negative-control accounting. Any
custom payload injection must be checked against each tool's real supported
options and compared as a new experiment. Human triage of role, context and
security impact remains a distinct acceptance requirement. No tool ranking,
XSS TP/FP/FN, vulnerability, or overall R4 closure follows from this review.

## Fresh validation

Command, from the repository root with `DXA_BROWSER` set to the installed
Chrome executable:

```powershell
py -3.10 -m pytest bench/test_r4_compare_local.py bench/test_r4_cid_oracle.py -q -p no:cacheprovider --tb=short
```

Result: **48 passed**, zero failures, errors or skips. The test set includes
the authorized disposable loopback browser positive and escaped control; these
are fixture-oracle tests, not scanner execution evidence. Python 3.10 on
Windows. Current source SHA-256: comparator
`8e393273e385209f76bfa1e2d3038f068d59b968174ddb9f1bc3abbc7d88dd52`,
oracle `cc1004fdda4f13a3ec5e4f3c0237865a00fa28e8f60ac315b6abab93210fb6d1`,
comparator test `c262d413dca8fdec6784596eae701c14a67aa7b8ac1483ff2a9e9f872d694d28`,
oracle test `e13805b07cea3ebd7ee80da2ed9f2f51a8d1fd318465a6734a2ff954a8be4eae`.
No external target, persistent lab data, commit or push was involved.
