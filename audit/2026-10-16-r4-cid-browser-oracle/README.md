# R4 exact-CID browser correlation adapter

Date: 2026-10-16. Roadmap: R4, specifically scanner candidate ↔ correlated browser execution; overall R4 remains open.

## Delivered

`bench/r4_cid_oracle.py` defines a small adapter over the comparison fixture's exact post-scan `stored_comments()` values and independent browser observations. It extracts a candidate CID only when the same identifier occurs in both a `?cid=` resource URL and a `window.__dxaProof='CID'` JavaScript assignment in that exact stored payload. Scanner JSON labels and stdout are never proof inputs. The adapter de-duplicates identities, rejects wrong case/path/role observations, distinguishes error/timeout/skipped/incomplete, and requires a completed reader-admin browser window before a missing execution can count as a negative. An escaped candidate that executes fails its negative control.

`observe_reader_admin()` accepts only plain HTTP loopback origins. It puts the supplied reader token in an HttpOnly cookie in a fresh Playwright context, verifies `/session/reader-admin` returns the expected principal and role, visits `/admin/comments`, and reads an existing `window.__dxaProof` value. It does not generate, evaluate, or inject a canary. Returned rows contain role labels, CID and outcome only; the token and URLs are not returned.

## Verification

Command: `py -3.10 -m pytest bench/test_r4_cid_oracle.py -q -p no:cacheprovider --tb=short`
Environment: Windows, Python 3.10, local Playwright Chromium, loopback-only fixture.
Result: **27 passed** (including actual reader-admin Chromium execution and escaped negative control). `py_compile` for the module and test passed; `git diff --check` passed.

Source SHA-256 at handoff:

- `bench/r4_cid_oracle.py`: `3f024e020ad787482ab85421cf9b50c6c373209b04782f75d88740c72cb644b8`
- `bench/test_r4_cid_oracle.py`: `e13805b07cea3ebd7ee80da2ed9f2f51a8d1fd318465a6734a2ff954a8be4eae`

## Limits

The browser integration test submits a purpose-built fixture canary to demonstrate the observer and adapter contract. It is a harness test, not a scanner result, and must not be used to upgrade any scanner finding.

Source inspection of `tools/dom-xss-analyzer/dxadyn.py:83-99,532-553` shows its ordinary stored candidate is a short `dxa` CID followed by context/probe text such as `"<dXsS>`; it does not bind that CID to a browser-visible JavaScript proof value. It therefore remains **inconclusive** under this adapter. A raw reflection, candidate label, or a separate harness canary cannot fill that gap. Dalfox candidates likewise remain inconclusive unless the exact submitted payload itself carries a recoverable CID-bound proof and the separate reader browser observes that same CID. No scanner accuracy score or R4 closure is claimed.

No external target was used. This audit records only this owned loopback fixture contract and source analysis; it does not replace the main ROADMAP or imply remote CI acceptance.
