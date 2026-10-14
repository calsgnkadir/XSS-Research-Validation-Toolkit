# R4 auth failure and blind/admin boundary controls

Six disposable loopback controls cover login rejection, HTTP identity mismatch,
browser role mismatch, missing CSRF token, rejected CSRF token and session expiry
after submission. Real Chrome proof must stop at the exact expected stage,
with expected submit/persistence counters and zero reads. Expected failures
are control acceptance only; the adapter leaves XSS accuracy unevaluated.

Local focused tests: **13 passed**, zero failures/errors/skips. The standalone
CLI uses six owned workers, each with a 30-second deadline and descendant
cleanup; real CLI acceptance **6/6**, exit 0. It requires a new output file.
[Commands and hashes](acceptance.json), [control evidence](controls.json).
Existing benchmark runner execution corpus remains 14 cases; this standalone
failure-control CLI is not yet integrated into runner report/scoring schemas.
Required browser CI now includes the two new regression modules; fresh remote
acceptance remains pending.

Seven adapter tests cover wrong admin labels, callback/admin-visit event
substitution, matching callback without execution and foreign CID rejection.
These are evidence-boundary regressions, not a separate-admin-account blind
XSS execution fixture. Cross-account/admin acceptance remains open.

Engine supplied the initial fixture then hit its usage limit. QA also stopped
at that limit before writing files. The coordinator reviewed and completed
the fixture tests, blind/admin tests and bounded CLI. No active specialists
remain from this assignment; no completed independent final QA is claimed.
Docker was not rerun.

## Controlled comparison readiness

Coordinator inspection: Get-Command dalfox,xsstrike,zap,go returned no PATH
entries. This does not establish machine-wide absence. Existing DalFox and
XSStrike adapters in bench/run.py use CLI output parsing and skip if executables
are unavailable. No comparator versions, installation or live comparison
are claimed. Auth, request budget and equivalent proof semantics must be
established under [the protocol](../../bench/COMPARISON-PROTOCOL.md) before
ranking results. Installing/configuring a comparator and running an equivalent
local corpus remain open; there is no measured tool superiority or new CVE.

Combined new-controls/adapter/identity/artifact-gate regression: **193 passed**, zero failures/errors/skips.
