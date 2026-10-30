# R8 — bounded inline HTML message-source coverage

Base: `4708e967a6456617bcb169fc3eb626c2caf5d525`, the accepted receiver-fix
delivery. The user's requested sequence was honored: finish measured false
positives first, then strengthen XSS coverage. No new PyPI release was made.

## Change and limits

`.html`/`.htm` now obtain message provenance from supported direct window
message callbacks in actual executable inline scripts. The callback receiver,
physical source location and local value assignments are tracked within a
bounded flat body. Message source evidence is not inferred from ordinary HTML
text, comments, JSON/plain-text/external scripts, unrelated object.data, nested
receiver shadows or after parameter mutation/escape. Origin comparisons do not
clear candidates. Existing first-match source evidence is retained when a
supported second message sink occurs on the same physical line.

Malformed markup rejected by HTMLParser produces an explicit analysis error
while retaining generic sink matches. Existing JS-file broad message heuristics
are unchanged. This is not an HTML/JS execution engine or comprehensive data
flow. [Supported subset and exclusions](../../tools/dom-xss-analyzer/STATIC-SCOPE.md).

## Acceptance

- Independent 31-case inline regression baseline: **16 failed / 15 passed**.
- Final eight-file selected suite: **296 passed, zero failure/error/skip**.
  Includes inline messages, receiver bindings, dxa, static context/config,
  sanitizer, Python AST pilot and SARIF tests.
- Same-source project comparison repeated with the final scanner hash:
  scope A **22 -> 12**, exactly the five FormData/five router false alarms;
  scope B **129 -> 129**. No added candidate; 233/47 source hashes unchanged.
  One previously recorded vendor-directory skip remains in scope B. Raw code,
  paths and source-specific analysis remain ignored/private.
- No application, browser, target HTTP or fixture JavaScript was executed.
  Static candidates are not vulnerability counts, and the results do not
  establish application-wide safety or new CVE credit.

[Machine record and source hashes](result.json). Local Windows/Python 3.10.11
commands:

```text
py -3.10 .dxa/run_inline_acceptance.py --baseline
py -3.10 .dxa/run_inline_acceptance.py
.dxa/pypi-refresh-021/Scripts/python.exe -B .dxa/run_fp_project_comparison.py --accept-phase1
```

Engine specialist owned dxa.py and QA owned test_static_inline_messages.py.
The coordinator reviewed implementation and oracles, returned equality/parser/
same-line evidence risks, ran the final checks, and accepted the bounded result.
Workers were closed. The earlier research specialist scoped this phase without
claiming runtime execution. Hosted CI is separate from local acceptance and is
not claimed here. Published PyPI 0.2.1 remains unchanged.

Next R8 scope: bounded JSX anchor href candidate semantics with direct-source,
tracked-identifier, ordinary-text, fixed-URL and custom-component controls.
Leaflet and Jinja context work remain separate; no implementation is claimed.
