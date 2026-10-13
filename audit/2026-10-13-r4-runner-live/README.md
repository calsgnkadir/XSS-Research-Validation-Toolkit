# R4 Bludit runner integration — local acceptance

## Result

The explicit Bludit product-control adapter is connected to `bench/run.py`.
It runs only with `--bludit-control` and an explicit existing
`--bludit-browser` executable. CI refuses to launch it. The product controls
are emitted under `product_controls`, with `triage=by-design`, and remain
outside scanner rows, scorer inputs and TP/FP/FN totals.

On 13 October 2026 the runner CLI completed one local mock benchmark target
and the disposable pinned Bludit lifecycle. The mock target retained its own
candidate-count result (TP=1, FP=0, FN=0; not confirmed XSS accuracy). Bludit's
admin-authored raw control executed and its escaped control did not; both
matched their expected behavior. Teardown passed. These are product behavior
controls, not a vulnerability or role-boundary finding.

The sanitized [JSON report](result.json) and [Markdown report](result.md)
contain the separate product-control record. Credential, canary, project,
output path, and browser observation data are not included in the control row.

## Reproduction and verification

From the repository root on Windows with the pinned Bludit image already
available, Docker running and local Chrome installed:

```powershell
py -3.10 bench/run.py --targets mock-reflected-easy --bludit-control `
  --bludit-browser 'C:\Program Files\Google\Chrome\Application\chrome.exe' `
  --out audit/2026-10-13-r4-runner-live/result.md --no-history
```

The directly related benchmark regression suite passed **434 tests**, with
zero failures, errors or skips (Python 3.10.11, Windows):

```powershell
py -3.10 -m pytest bench/test_bench.py bench/test_bludit_adapter.py `
  bench/test_bludit_ingress.py bench/test_bludit_runner.py `
  bench/test_ci_acceptance.py bench/test_ci_self_scan.py `
  bench/test_docker_safety.py bench/test_proof_adapter.py `
  bench/test_proof_corpus.py bench/test_runner_isolation.py `
  -q -p no:cacheprovider --tb=short
```

After the live run, Docker inventory remained at 15 containers, 27 volumes
and 9 networks, matching the pre-run lifecycle acceptance counts. The adapter
reported cleanup passed. The prior lifecycle acceptance also recorded exact
pre/post identity-set matches; this runner integration did not add a second
private inventory snapshot.

## Limits

This does not close general R4: the strict positive/negative corpus gate,
broader coverage/accounting criteria, CI artifact acceptance for this new
product-control report, and comparable-tool methodology remain open. Hosted
CI has not tested this runner integration and does not run the local Bludit
Docker image. See [ROADMAP](../../ROADMAP.md) and
[VALIDATION](../../VALIDATION.md) for remaining work.
