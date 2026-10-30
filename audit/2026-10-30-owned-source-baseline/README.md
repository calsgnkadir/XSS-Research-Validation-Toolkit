# Bounded owner-authorized source review and scanner baseline

Roadmap: R7/A04 source review; R8 measured scanner follow-up. Base toolkit
commit `1b2f7853f9bb84612cd9aa8e9a36984f259a83a0`, clean main matching
origin/main after fetch. The user authorized source review of two owned local
projects. Their code, raw reports, paths and source-specific analysis remain
private in ignored `.dxa/owned-review-20261030/`; none is published here.

Three native roles completed disjoint private reports: security researcher,
report specialist and QA lab specialist. Coordinator reviewed representative
source chains, ran installed PyPI 0.2.1 static analysis, and executed synthetic
source-only comparisons. Workers were closed. Role invocation is observed;
TOML loader behavior is not independently established.

No application/server/browser was started, no target HTTP request was sent,
and no application file or data was changed. This is bounded source review,
not comprehensive application acceptance or a vulnerability/CVE finding.

## Measured generic scanner limitations

Installed 0.2.1 dxa bytes equal checkout dxa.py, SHA-256
`2561203de267961cc3e247aa3708b29bca82f903d6a0e4fdb1ccb68e9ec6b718`.
Python 3.10.11 / Windows. Sixteen inert source fixtures were scanned; their
contents were never executed. Twelve coordinator assertions verified the
existing baseline behavior, including limitations, not fixes or app security:

| Synthetic source shape | Observed baseline | Control |
|---|---|---|
| FormData instance `.append(...)` | jquery-html false positive | real jQuery append still reported |
| `const location = useLocation()` | navigation false positive | actual location navigation still reported |
| JSX variable `href={next}` | no candidate | property `.href = next` reported high |
| Leaflet `bindPopup(label)` | no candidate | innerHTML of same source reported high |
| Jinja interpolation inside JS template string | no candidate | ordinary HTML interpolation also has no candidate |
| Same message listener / innerHTML in .html vs .js | medium/no source vs high/postMessage.data | ordinary object.data has no message source |

Inline HTML with location.hash -> innerHTML is reported high, like its .js
comparison. It is incorrect to claim HTML inline scripts are never scanned.
Missing generic candidates do not establish exploitable vulnerabilities.

## Follow-up acceptance (not implemented)

Within R8, prioritize bounded disambiguation of known FormData receivers and
React location bindings. Preserve true jQuery HTML and real location assignment/
navigation positives; do not clear unknown receivers by name alone. JSX/Leaflet
coverage needs explicit candidate semantics and context/guard controls before
implementation. Do not turn encoder names into global safety proofs.

No runtime/test code changed, no pytest or browser suite reran, and hosted CI
was not checked. Private source/hash manifests and commands are retained for
local continuation; public evidence intentionally contains only generic shapes.
