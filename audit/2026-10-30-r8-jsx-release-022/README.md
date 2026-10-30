# R8 JSX URL candidates and PyPI 0.2.2

Base source: `accbec2f815353f2c6b8d20380e05b3ddfcbcddb`. User instruction:
develop JSX URL-source tracking with parallel agents, then publish accepted
runtime improvements. Existing PyPI 0.2.1 files cannot be replaced; 0.2.2 is
the new distribution containing all three accepted static-source changes:

1. Bounded native FormData / React router false-positive disambiguation.
2. Bounded executable inline HTML message-source tracking.
3. Bounded intrinsic JSX/TSX anchor href URL-control candidates.

[PyPI 0.2.2](https://pypi.org/project/dxa-research-toolkit/0.2.2/) is published.
[Final production verification](publication.json) records matching description,
wheel/sdist SHA-256, eleven module hashes and twelve installed CLI checks.
`acceptance.json` remains the prepublication local acceptance snapshot.
Source delivery `a192b7373677b5c7b538c52de080fa576030398e` was pushed and
verified against origin/main. Historical 0.2.1 artifact hashes are unchanged.

## JSX behavior and independent acceptance

The new `jsx-href` sink reports supported nonliteral intrinsic anchor hrefs:
direct/tracked source evidence is high confidence, unknown expressions medium.
Physical href lines are preserved, including multiline attributes. Fixed
literal URLs, ordinary JSX text, inert strings/comments and custom components
are excluded. A validation helper's name does not clear tracked provenance.
Closed sibling function locals do not taint a later component parameter.

Opening-tag and provenance contexts are bounded to 32 KiB. Spreads, nested
braces, full AST/control-flow, all JSX props, component rendering, URL scheme
validation, Leaflet and Jinja context analysis are not promised. A candidate
does not establish a dangerous scheme, JavaScript execution or vulnerability.
[Supported scope](../../tools/dom-xss-analyzer/STATIC-SCOPE.md).

- Final independent JSX baseline: **26 failed / 28 passed** on the base commit.
- Combined nine-file local suite: **350 passed, zero failure/error/skip**.
  Covers JSX, inline messages, receiver bindings, dxa, context/config,
  sanitizer, Python AST pilot and SARIF.
- Same-source comparison retained all prior source candidates and all ten
  reviewed false-alarm removals. Scope A: released baseline 22, prior source
  12, current 20 (eight new medium JSX candidates). Scope B remains 129.
  The 233/47 source hashes match earlier inputs. One known vendor skip remains.
  These are candidate counts, not new vulnerabilities or accuracy measurements.
- App source, paths, raw reports and detailed triage remain ignored/private.
  No target application/browser/HTTP execution occurred.

[Acceptance, source hashes and local installed proof](acceptance.json).
Coordinator commands (Windows / Python 3.10.11):

```text
py -3.10 .dxa/run_jsx_acceptance.py --baseline
py -3.10 .dxa/run_jsx_acceptance.py
.dxa/pypi-refresh-021/Scripts/python.exe -B .dxa/run_jsx_project_comparison.py
.dxa/pypi-refresh-021/Scripts/python.exe -m build --outdir .dxa/release-022-dist
.dxa/pypi-refresh-021/Scripts/python.exe -B .dxa/release_022_local.py
```

## Packaging and verification

Twine validates wheel/sdist descriptions. Archive checks exclude local caches,
environment/credential paths and database/key artifacts. The wheel's eleven
module files equal source; wheel/sdist descriptions equal docs/PYPI-README.md.
Fresh venv installation is tested from outside the source tree with isolated
imports. Twelve installed checks cover four help entry points and eight inert
source cases: receiver exclusions, genuine sinks, inline message, JSX/TSX
source tracking/unknown/control cases, and explicit malformed-HTML error.
Fixture source is never executed. Published hashes and a production-PyPI
installation were verified separately after upload.

The first production install only saw 0.2.0/0.2.1 and failed. A subsequent
normal simple-index/release JSON check confirmed 0.2.2 visibility; a fresh
production venv then installed it with no cache or dependencies and passed all
twelve checks. The first failed attempt is not counted as a successful install.

Three native roles worked in parallel with disjoint ownership: engine dxa.py,
QA test_static_jsx_href.py, and report specialist package metadata/description/
static scope. Coordinator reviewed code and oracles, returned sibling-scope
provenance risks, ran acceptance, reviewed package contents and owns release
publication. All workers were closed; native invocation is observed, TOML
loader behavior is not separately established. Hosted CI is separate from
local acceptance; no hosted result is claimed in this record.
