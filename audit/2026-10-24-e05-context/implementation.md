# E05 — textarea RCDATA marker probe

Date: 2026-10-24. Base: `532be7ac01e82fbe0612749ead6d3cb39f0be7e9`.
Native role: `xss_security_researcher`; coordinator owns integration/acceptance.

## Scope and root cause

The existing `PAYLOAD_VARIANTS` registry includes a closing-title marker and
an opening `textarea-onfocus-breakout` shape, but no closing-textarea marker.
An opening element spelling remains textarea RCDATA when inserted into an
already open textarea. The bounded E05 candidate is an inert
`textarea-breakout` probe: `CID</textarea><dXsS>`. It contains no JavaScript.

The implementation owns `dxadyn.py`, `test_e05_context.py`, this record, and
the coordinator-approved cardinality update in `test_json_transport.py`.
Independent QA owns the coverage matrix and browser parser oracle. No external
target, A05 multipart scenario, existing Docker volume or release is involved.
The accepted R4 scope remains closed; this is an optional context extension.

## Baseline regression

Before changing production, the coordinator ran:

```powershell
py -3.10 -m pytest tools/dom-xss-analyzer/test_e05_context.py -q -p no:cacheprovider --tb=short
```

Windows / Python 3.10.11 / pytest 9.1.1, elevated coordinator execution:
**6 failed**, no skips, 1.44 seconds. The production generator silently falls
back to the body shape for the previously unknown variant; the mutation and
real-loopback suffix assertions catch that fallback. The three Content-Type
checks fail at the missing registry key, not at classification. They are not
browser parser evidence. The specialist's own sandbox attempt could not start
WindowsApps Python (`Access denied`); no test ran in that attempt.

The coordinator then ran the independent QA oracle before changing production:

```powershell
$env:DXA_REQUIRE_BROWSER='1'
py -3.10 -m pytest bench/test_e05_context_coverage.py -q -p no:cacheprovider --tb=short
```

Chrome `C:\Program Files\Google\Chrome\Application\chrome.exe` with page
JavaScript disabled: **1 failed, 5 passed**, no skips, 9.16 seconds. The raw
loopback positive control produced zero `dxss` elements because the unknown
variant fell back to the body probe. The independent legacy baseline parsed
all 50 existing families with their base plus 18 mutations (950 generated
attempts) in inert native-browser `DOMParser` documents; none produced a
`dxss` element from textarea RCDATA. Escaped, body, title and old textarea-opening
navigation controls passed. These are bounded parse-tree observations, not
JavaScript execution evidence.

## Implemented change and limits

The single inert closing-textarea probe preserves paired mutation marker
matching and CID isolation. Both CLI `--variants all` paths and explicit-name
validation already enumerate the registry dynamically. Default selection stays
`body`; users select the new family explicitly or through `all`. Related CLI
help describes inert RCDATA probing instead of suggesting execution. The
existing JSON transport test's fixed 950-attempt quota now derives its expected
size from the variant/mutation registries; every generated value still passes
through the real JSON submit function and is compared byte-for-byte after
decoding. No transport coverage was removed.

HTTP findings stay `html-reflection` / `reflection` / `unreviewed`, with the
first CID's estimated `textarea` context. Raw response survival does not prove
that a browser parsed an element, ran JavaScript or found a vulnerability.
The independent browser oracle separately tests marker-element reach outside
textarea, with escaped and wrong-context controls.

## After-change acceptance

The coordinator ran the combined selection under the same elevated Windows /
Python 3.10.11 environment with `DXA_REQUIRE_BROWSER=1`:

```powershell
py -3.10 -m pytest tools/dom-xss-analyzer/test_e05_context.py bench/test_e05_context_coverage.py tools/dom-xss-analyzer/test_dxadyn.py tools/dom-xss-analyzer/test_http_evidence.py tools/dom-xss-analyzer/test_json_transport.py tools/dom-xss-analyzer/test_blind_journal.py tools/dom-xss-analyzer/test_r1_contract.py tools/dom-xss-analyzer/test_sarif.py -q -p no:cacheprovider --tb=short --junitxml=.dxa/e05-acceptance.xml
```

Result: **381 passed**, zero failures/errors/skips, 43.01 seconds. The same
independent loopback browser positive now observes one `dxss` marker element
outside textarea; encoded/default/wrong-close-tag controls still observe none.
The exhaustive legacy parse-tree baseline remains unchanged. HTTP transport,
Content-Type classifications, JSON transport for every generated attempt,
blind journal, shared R1 and SARIF regressions are included in this selection.
This was a selected suite, not the full project suite. No new hosted-CI result
or installed-wheel result is inferred from it; coordinator integration tracks
those separately.

Tested source SHA-256 values (raw working bytes):

| File | SHA-256 |
|---|---|
| `tools/dom-xss-analyzer/dxadyn.py` | `36bf8ad8780771893efd50e0c595b1560a7b01629d4693cc1a1de08ca8bfb199` |
| `tools/dom-xss-analyzer/test_e05_context.py` | `cffbe65f1addf3e3ebf9aa5ce74921262499eb7075ee182bbdeaa80224a5229e` |
| `tools/dom-xss-analyzer/test_json_transport.py` | `7ac2a89fb4f1415ee734ec5574cf99e42f5fb7d428612960ec2d8f516b15c17b` |

Independent QA reviewed the narrow diff and positive/negative oracles. The
coordinator remains responsible for final acceptance, shared documentation and
Git delivery. No specialist commit or push was performed.
