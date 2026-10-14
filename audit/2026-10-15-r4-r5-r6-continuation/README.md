# R4 / R5 / R6 continuation — 15 October 2026

Base checkout: `8dd50acb80ed41bb2e44d4f1ab9defa9f1deca09`, clean main matching
origin/main. Two native specialists were assigned: Scanner Engine owns the R4
artifact gate; QA Security Lab owns the R5 reproduction handoff. The coordinator
owns R6 CLI/report tests and the shared progress documents.

## R6 CLI and report acceptance

The dynamic CLI previously checked incompatible DOM modes after browser
discovery and could exit successfully for `--dom --stored` without a URL.
HTTP cookie/header/login options could also be ignored by a bare DOM visit.
The parser now rejects conflicting primary modes and HTTP session options
with DOM before browser discovery, session setup or output writes. A positional
URL with stored/flow is also rejected because those modes define their targets.
Bare `--dom` availability checking remains supported.

Thirteen mode tests cover rejection before I/O, absence of output artifacts,
secret-free errors and the supported availability command. Twenty-one report
matrix tests cover JSON-only, HTML-only and combined output for stored,
stored-auto, flow, DOM, successful auth-check, failed login and failed auth-flow.
They assert one normalized document, JSON equality, HTML renderer object
identity and operational error events. Existing reflected finding identity,
redaction and escaping tests remain part of acceptance. These are mocked CLI
branch tests, not new live scan/execution evidence.

Windows/Python 3.10.11: focused tests **68 passed**; affected combined suite
**304 passed**, no failures/errors/skips. Exact commands and source hashes are
in `acceptance.json`. R6 general config coverage, release packaging acceptance
and the release tag remain open. No release or new CVE is claimed.

## Specialist evidence

- R4: [artifact callback summary consistency](../2026-10-15-r4-acceptance/README.md).
- R5: [portable reproduction handoff](../2026-10-15-r5-handoff/README.md).

Coordinator review covered both specialist diffs and their negative oracles.
The combined R4 gate/scorer/adapter and R5 fixture/gate suite passed **231
tests**, zero failures/errors/skips. All three audit source-hash maps matched
the checkout; the R5 live acceptance record and all twelve ignored proof
artifact hashes matched the specialist's audit. `git diff --check` passed.
Specialist test totals overlap these runs and must not be added as unique tests.

R5 automated local/CI repetition does not fulfill independent second-human
acceptance. Docker was not required for these changes. Broad R4 coverage and
controlled competitor comparison remain open.

## Remote acceptance

Code commit `9b6b7c3c25088263be5969e962d155aa83ae13d1` was pushed; remote main
matched and the working tree was clean. General CI
[38640435614](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38640435614)
passed all three jobs. The downloaded `r3-browser-proof` ZIP digest matched
GitHub metadata; the exact committed gate accepted 169 tests with no skips/errors,
14/14 corpus (TP=7, FP=0, FN=0), canonical JSON/Markdown and source provenance,
and observed demo execution. Separate auth controls passed 6/6 with cleanup.
[R4 archive/member evidence](remote-r4-acceptance.json).

K01 Linux run
[38640435613](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38640435613)
passed. Its downloaded artifact digest matched GitHub metadata; JUnit showed
22 tests with no failures/errors/skips, proof 5/5 and five distinct closed
fixture ports recorded by CI. Profile `ci`, gate/source hashes and twelve proof
member hashes were checked against the commit/artifact.
[R5 archive/member evidence](remote-r5-acceptance.json).
Downloaded artifacts do not re-observe historical socket closure or establish
independent human acceptance. Hosted CI did not run Bludit Docker acceptance.
The local acceptance JSON's pending-push entry describes the earlier snapshot;
these remote records document its follow-up.
