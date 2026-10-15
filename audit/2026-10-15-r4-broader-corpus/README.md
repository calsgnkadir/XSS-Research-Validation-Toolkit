# R4 corpus v4: inert and activated markup contexts

Starting checkout: `2abcd51` on main. This delivery extends the disposable
loopback execution corpus from 14 to 17 cases, with eight positive and nine
negative labels. It does not establish a vulnerability count or product
accuracy, and does not close general R4.

## New independent labels

| Case | Context | Expected matching execution |
|---|---|---|
| proof-comment | Submitted image remains inside an HTML comment, with no closing comment sequence | No |
| proof-template | Submitted image exists only in inert template content | No |
| proof-template-activated | Application imports template content into the active document | Yes |

All three use the same authenticated reader account, POST `/comments`, field
`comment`, read `/comments`, and a 400 ms observation window. The payload is
unchanged. The activated fixture imports the template subtree; only the
submitted image handler assigns the CID. Neither scanner nor fixture helper
assigns the expected CID through browser evaluation.

The corpus is versioned `loopback-proof/4` with `proof-v4:` stable identities.
An independent test label table, HTTP response/state oracle and native browser
DOM oracle exercise the contexts separately from the scanner's status.
The browser oracle checks inactive versus active image counts, retained
template content, and the exact submitted canary value.

## Validation status

Resumed native Scanner Engine specialist reviewed the preserved implementation;
no additional application/test source changes were needed. Ordinary sandbox
execution failed with `helper_unknown_error`; explicit approved escalated
execution worked in the active checkout. No remote scanning or Git writes.

On 15 October 2026, Windows/Python 3.10.11 and installed Chrome:

- Required-browser regression: **254 passed**, zero failure/error/skip,
  166.45 seconds. [JUnit](pytest.xml).
- Separate strict CLI: **17/17 completed, TP=8 FP=0 FN=0**, zero incomplete
  outcomes, exit 0. [JSON](r4-proof.json), [Markdown](r4-proof.md).
- JSON/Markdown exact renderer match and `strict_failed == False` verified.
- Source and shareable artifact hashes are in [acceptance.json](acceptance.json).
  Source files remained unchanged throughout the completed runs.

Commands from repository root (browser path represented by `<local-chrome>`):

```powershell
$env:DXA_REQUIRE_BROWSER='1'
$env:DXA_BROWSER='<local-chrome>'
py -3.10 -m pytest bench/test_ci_acceptance.py bench/test_proof_adapter.py bench/test_proof_corpus.py bench/test_proof_identity_matrix.py tools/dom-xss-analyzer/test_browser_proof.py tools/dom-xss-analyzer/test_proof_cleanup.py -q -p no:cacheprovider --tb=short --junitxml=audit/2026-10-15-r4-broader-corpus/pytest.xml
$env:BENCH_STRICT='1'
py -3.10 bench/run.py --proof-suite --browser '<local-chrome>' --no-history --out audit/2026-10-15-r4-broader-corpus/r4-proof.md
```

Shareable JUnit omits the hostname attribute. JSON command metadata replaces
only the local browser executable path; Markdown was re-rendered from that
JSON. Outcomes, timings, source hashes and proof observations are unchanged;
artifact hashes cover these shareable copies. This is local Windows acceptance,
not the Linux/Python 3.12 CI artifact gate. Remote CI is coordinator-owned.

## Remaining scope

This is a single-account fixture expansion. Separately authenticated low-role
submission and admin read, general blind/admin coverage, controlled competitor
comparison, and broader R4 acceptance remain open. A completed negative window
does not prove a real target safe. Docker and external targets were not used.
