# R4 exact scanner payload browser replay

Date: 2026-10-16. Roadmap: R4 controlled comparison. Native
`scanner_engine_specialist` task `/root/r4_closure`, base HEAD
`06c4e21570df8fbdad4ba45885dccf2b0dc28a54`. All browser requests in
this new experiment used disposable `127.0.0.1` fixtures and installed Chrome.
No external target, persistent app data, human triage, commit or push.

## Protocol and provenance

The comparator's original candidate run remains separate. New
`--proof-manifest` mode first verifies each completed row's report SHA-256,
canonical report shape and candidate count. Dalfox's reported `payload` must
equal exactly one string in fixture `stored_payloads`; dxadyn's reported
eight-hex canary ID must identify exactly one stored string. Missing or
ambiguous source attribution yields no proof attempt. These checks are in
`bench/r4_compare_local.py:279-317` and `bench/r4_cid_oracle.py`.

Each matched string is replayed **without editing its bytes** into two fresh,
single-comment local fixtures. A writer submits it, storage readback checks
equality, and a separate reader-admin browser session verifies its principal
and role before reading. The raw page is observed for a native JavaScript
`alert` dialog; the escaped page is the negative control. The observer only
listens for and dismisses dialogs and does not insert a canary or script.
Each replay fixture limits itself to 20 requests, 50 requests/second and a
30-second wall; browser observation is 500 ms. A failed storage, role, HTTP,
budget or browser window does not become a negative result. Output contains
payload SHA-256, statuses and counts, never raw payloads or session values.

The 16 October separate-session scanner manifest was attempted first and
rejected **before browser launch** because its current report artifact bytes
did not match a manifest SHA-256. Historical artifacts were not rewritten or
silently rehashed. The source for the successful replay is the imported,
previously gate-accepted run-02 at
`audit/r4-local-acceptance-resume/imported-run-02/comparison.json`, SHA-256
`b03aadbab9806ae93fdd6cd22359af0561cccda6b435271f0b699efc61b6ca10`.
All eight referenced report hashes matched at replay time. That scanner run
used the earlier fixture broker cookie, so its original scanner auth evidence
is narrower than the later separate-session run. The new browser replay uses
separate writer and reader-admin fixture logins. **No scanner was rerun** in
this experiment; these are fresh browser observations of exact historical
scanner-submitted strings, not browser visits during their original requests.

## Red before green and live result

Four new oracle counterexamples failed before implementation (missing
matching/replay functions); two manifest integration cases also failed before
implementation. After the changes:

```powershell
$env:DXA_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
py -3.10 -m pytest bench/test_r4_compare_local.py bench/test_r4_cid_oracle.py -q -p no:cacheprovider --tb=short
```

**54 passed**, zero failure/error/skip. Windows, Python 3.10, installed Chrome.
The focused suite includes actual loopback raw execution and escaped negative
control, plus report hash drift rejection before browser start.

Live command:

```powershell
py -3.10 bench/r4_compare_local.py --proof-manifest audit/r4-local-acceptance-resume/imported-run-02/comparison.json --output audit/r4-proof-experiment-2026-10-16/live-replay --browser 'C:\Program Files\Google\Chrome\Application\chrome.exe'
```

Result: eight scanner rows read, six exact report-to-storage candidates
replayed. Each raw/escaped replay completed with verified reader-admin role,
6–7 total requests per fixture and no budget rejection. The two Dalfox raw
candidate payloads produced native dialogs in the raw reader page and none in
the escaped control. The two dxadyn raw candidates produced no dialog in
either page and remain **inconclusive** because their benign marker is only a
reflection probe. The two Dalfox escaped-case candidate strings also produced
no dialog in either replay; their original candidate label remains
**inconclusive**, not a confirmed FP. dxadyn's two escaped scanner rows had
zero report candidates and no payload replay. Detailed status and per-payload
hashes: [proof-experiment.json](live-replay/proof-experiment.json), SHA-256
`220995ba4e257f6a0ab743787499aea4b3a617110075c6a4bf8c7624a13b556a`.

Source SHA-256 at this run:

| File | SHA-256 |
|---|---|
| `bench/r4_compare_local.py` | `a4c987df95cd4dd30265db55ed06fc8ae4f8420bf4ee97e31babc7dea4fc1020` |
| `bench/r4_cid_oracle.py` | `24b3b47e315abae575d40381a37d25ecb188c11afc2f088fc5e29fa5ee2df91b` |
| `bench/test_r4_compare_local.py` | `48a30d9287494e396a13b12700aa1202150792b09d90064875704bdaba14a45a` |
| `bench/test_r4_cid_oracle.py` | `b586d456853ebdbcba271c2cf6c698ff62796f8b4ad0ade88ad04c148cb719ce` |

## Coordinator final review

Coordinator review found that a failed escaped control could still be summarized
as a successful candidate replay, and the replay browser did not explicitly
block external HTTP traffic. The replay observer has no general browser-network
sandbox; WebSocket and other non-HTTP channels remain outside this R4 experiment
and belong to the separate R9 scope. A dedicated WebSocket negative-control
attempt timed out and was stopped; it is an unverified boundary, not a pass.

Candidate replay is reported only when every matched payload has a raw dialog
and a clean escaped control; all HTTP requests are restricted to the fixture
origin and service workers are blocked.

The Chrome-required focused suite was rerun after these changes:

```powershell
$env:DXA_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
py -3.10 -m pytest bench/test_r4_compare_local.py bench/test_r4_cid_oracle.py -q -p no:cacheprovider --tb=short
```

Result: **57 passed**, zero failure/error/skip. This includes the escaped
negative control, a blocked external HTTP resource attempt, benign-marker
inconclusive behavior, manifest hash rejection, unmatched-candidate handling,
failed-negative-control rejection and candidate/outcome separation.
The final replay was rerun into `final-run-02/` from the unchanged,
hash-accepted historical run-02 manifest. It read 8 scanner rows and replayed
6 exact report-to-storage candidates. Both Dalfox raw payloads produced a
dialog in the raw fixture and none in the escaped fixture. The other four
replays were inconclusive. Each browser window verified reader-admin and
stayed within 5–6 fixture requests; no external request was allowed. No scanner
was rerun. Final output SHA-256:
`18b1c5f4237698ff24f3cd7ef1854e6dd01fd21511c896a856a8e61bda40dc2a`.

Final source SHA-256: comparator `5aa729c66de4fe4f4fdae7bf6406b43619aab30b92e3831283ca444fc6fd19eb`,
oracle `f1282bd64c899d876c7fcf15e3c1b1a747d807b395ddc55b4a95723958b3337e`,
comparator tests `67db75ac1c3fa14539a5a8e603c9ee5ef5802389a2f56b0993d22ec7e717ab34`,
oracle tests `8fd7dcada3938fc47667c02d9fd53868cb2afc22db6d01214b8ced0decdbf8c2`.

## Acceptance boundary

This shows an executable **Dalfox-submitted payload shape** under a new
isolated replay and a working escaped negative control. It does not verify the
original scanner's browser session, source app vulnerability, general scanner
accuracy, candidate TP/FP/FN, or tool superiority. dxadyn's benign stored
marker has no execution proof. Historical scanner auth limitations and the
rejected separate-session report hash must remain visible. The later coordinator
scope decision in the main ROADMAP closes the R4 measurement deliverable at
this supported, candidate-only boundary; it does not accept a scanner ranking,
general accuracy score, original-session execution, or vulnerability finding.
