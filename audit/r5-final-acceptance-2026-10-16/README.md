# R5/K01 technical acceptance — 16 October 2026

Roadmap IDs: **R5 / K01**. Starting HEAD was
`06c4e21570df8fbdad4ba45885dccf2b0dc28a54`, clean `main`, equal to
upstream. This native QA agent cannot supply a second independent human in
this session. No person was contacted and the human result form remains blank.
The user's 16 October scope decision permits replacing that mandatory R5
condition with technical acceptance while preserving the historical request
and unfulfilled form.

## New local run

Only the repository's disposable `127.0.0.1` K01 fixture was exercised.
Windows, Python 3.10.11, pinned Playwright 1.63.0 and installed Chrome
155.0.8059.82 were observed. A new isolated venv at `.dxa/v` installed the
pinned dependency from the pip cache. The short path matters: an initial venv
at `.dxa/r5-final-venv-20261016` was created, but package installation failed
with Windows `No such file or directory` at Playwright's long gallery path.
That failed installation produced no proof and is not a negative control.
The short-path retry completed successfully.

```powershell
py -3.10 -m venv .dxa/v
.dxa\v\Scripts\python.exe -m pip install -r cases/k01-stored-comment/requirements-proof.txt
.dxa\v\Scripts\python.exe cases/k01-stored-comment/check_repro.py --profile local --browser 'C:\Program Files\Google\Chrome\Application\chrome.exe' --output .dxa/r5-final-proof-20261016
```

The gate returned **exit 0**, **5/5 browser controls** and **5/5 distinct
closed fixture ports**. The new output was copied byte for byte to
[`proof/`](proof/acceptance.json). The five controls were vulnerable HTML
with matching CID, JS disabled, fixed HTML with the same payload, JSON-only,
and a normal application dialog. `check_repro.py:33`–`:129` checks the shared
CID and payload, exact HTTP representation and classification, one POST per
case, source/fix hashes and port closure. These are fixture browser results,
not a product vulnerability or scanner execution claim.

After copying, SHA-256 verification found **0 mismatches** across all 12
proof members, three case sources and `check_repro.py` gate hash in
`proof/acceptance.json`. The imported HTTP classifier is additionally bound
here: `tools/dom-xss-analyzer/dxadyn.py` SHA-256
`35e3b524141ac4971772949893ccd14f61ee5311ee1e55d2c91ba554e748c497`.
The generated package was checked for personal paths, credentials and external
URLs; only synthetic CID/payload and temporary loopback URLs were found.
The scoped `.gitattributes` keeps the hash-bound proof bytes unchanged by
Git newline conversion.

Other agents edited benchmark files after the initially clean status; this
specialist did not edit or stage those files. The acceptance hashes identify
the K01 source used by this run. No case code defect was reproduced, so no
application or gate test was changed. This turn did not rerun pytest.

## Technical R5 criterion and limits

| Criterion | Evidence | State |
|---|---|---|
| Reproducible local fixture and fix | New `proof/acceptance.json` and 12 members; exit 0, 5/5 controls, 5/5 closed ports, byte and source hashes | Pass on current Windows source |
| Independent clean environment | [Linux workflow acceptance](../2026-10-14-r5-linux-gate/remote-acceptance.json): downloaded artifact digest and members, 5/5 proof, 13 JUnit tests with zero failure/error/skip | Pass for historical `d41c1cd` source; not a human run |
| Regression gate and incomplete run behavior | [Prior local JUnit](../r5-local-closure-resume/regression.xml): 22 tests, zero failure/error/skip; `test_repro_gate.py:181` rejects missing acceptance after failure | Historical automated evidence; not rerun here |
| Another human from clean checkout | [Blank form](../../cases/k01-stored-comment/INDEPENDENT-REPEAT.md) | Unfulfilled, retained as optional follow-up under user's revised scope |

Accepted ROADMAP R5 closeout: require a clean Windows venv and separate Linux
environment, the same five positive/negative browser controls, source and
proof hashes, fix/retest and fixture cleanup. The new Windows run plus the
recorded Linux artifact acceptance satisfy that technical criterion. The
different Linux commit is an explicit provenance limit; the coordinator
should keep current HEAD Linux CI job status separate from artifact-content
verification. CI, agent runs and hash matches do not establish a second
person's identity. The archived port result is a live gate observation, not
a socket state that can be rechecked later. No external target, release,
commit or push was performed by this specialist.
