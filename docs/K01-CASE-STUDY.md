# Stored XSS in a comment renderer: proof, output encoding, and retest

A comment feature should display a reader's words as plain text. In K01, a
deliberately vulnerable local training fixture, the renderer instead treated
stored input as HTML. A comment submitted by an anonymous HTTP client executed
a small JavaScript canary when a separate browser context later read it.
Encoding the comment at the HTML output point preserved the original text
and prevented the payload from creating an element.

This case follows **ROADMAP K01 / R5**. It presents retained repository evidence;
no new test run was performed for this article. It concerns the project's own
disposable `k01-v1.0` lab, with synthetic input and in-memory storage. It is not
a newly discovered production vulnerability or a CVE.

## The problem: stored text crossed an HTML boundary

The feature's contract is plain-text comments. The vulnerable renderer places
the stored comment inside an `<article>` without encoding it. The browser
therefore parses attacker-controlled markup where the application intended
text. The root cause is at the output boundary: accepting and storing a string
does not make that string safe to interpret as HTML.

The complete path is small enough to inspect:

1. The fixture starts on a fresh `127.0.0.1` port.
2. An HTTP writer submits the `comment` form field to `POST /comments` and
   receives HTTP 201. The fixture stores the string in memory.
3. A new reader browser context loads `GET /comments`.
4. The vulnerable renderer inserts the stored string into the HTML response.
5. The browser interprets the injected image element and runs its error handler.

The writer uses Python's HTTP client; the reader uses a clean Playwright
context. The payload is not supplied through the reader's query string or
executed by passing payload text to `page.evaluate`. This separation establishes
the stored submission-to-read path. It does not establish two authenticated
users or a privilege boundary: this fixture has no real accounts or roles.

Sources: [fixture and product contract](../cases/k01-stored-comment/README.md),
[request and browser harness](../cases/k01-stored-comment/prove.py), and
[vulnerable renderer](../cases/k01-stored-comment/render_vulnerable.py).

## Proof: match the browser canary to the submitted comment

The harness creates a random correlation identifier (CID) and includes it in
the comment. The payload's image points to `/missing` on the fixture itself.
Its error handler only assigns that CID to `window.__k01`; it does not collect
credentials, access user data, or contact an external callback service.

After loading the stored comment, the harness reads the existing browser
global and compares it with the submitted CID. In the positive control, it
waits up to three seconds for that exact match. Reading the global observes
the payload's effect; the observation does not evaluate the payload itself.

A CID appearing in an HTTP response would establish reflection. The matching
value in the browser global supplies the additional, case-specific execution
evidence. The HTTP classifier still reports its own reflection or candidate
result; the harness does not upgrade an R1 finding to `execution-confirmed`.
This distinction follows the repository's
[evidence contract](../tools/dom-xss-analyzer/EVIDENCE-CONTRACT.md) and
[HTTP evidence model](../tools/dom-xss-analyzer/HTTP-EVIDENCE.md). The separate
[browser-proof contract](../tools/dom-xss-analyzer/BROWSER-PROOF.md) also keeps
execution observation distinct from vulnerability triage; K01 uses its own
case artifact rather than claiming that separate command was run here.

## Negative controls: challenge the interpretation

The same CID and payload are used across five controls, each with a fresh
fixture and exactly one comment POST. The retained clean Windows repeat
records all five passing:

| Control | Recorded browser observation | What it establishes |
|---|---|---|
| Vulnerable HTML, JavaScript enabled | Submitted CID observed | Positive execution control for the stored path |
| Vulnerable HTML, JavaScript disabled | No canary | Raw markup alone is not JavaScript execution proof |
| Fixed HTML, JavaScript enabled | No canary; exact text preserved; no injected image | The output fix blocks this payload while preserving content |
| JSON-only response | No canary; HTTP classification remains `json-only` | A marker in JSON is insufficient evidence of HTML execution |
| Ordinary application alert | Dialog observed, no canary | An unrelated dialog must not count as a successful payload |

These are historical results from the
[14 October clean local repeat](../audit/2026-10-14-r5-k01-clean-repeat/README.md),
with [machine acceptance](../audit/2026-10-14-r5-k01-clean-repeat/acceptance.json)
and [per-control results](../audit/2026-10-14-r5-k01-clean-repeat/proof/result.json).
That repeat used a new Python 3.10.11 environment, Playwright 1.63.0, and
installed Chrome 155.0.8059.79 on the same Windows machine.

## The fix: encode at the HTML text output point

The renderer change is deliberately narrow:

```python
# Vulnerable
value = comment

# Fixed
value = html.escape(comment, quote=True)
```

The stored input stays unchanged. At rendering time, HTML-significant
characters become text representations rather than markup delimiters.
The fixed control checks both security behavior and functionality: the CID
does not execute, the comment's text equals the complete original payload,
and there is no image element inside the comment.

The [fixed renderer](../cases/k01-stored-comment/render_fixed.py) and retained
[exact fix diff](../cases/k01-stored-comment/evidence/2026-10-05-verified/fix.diff)
show the change. This remedy fits an HTML **text** context. JavaScript strings,
CSS, URLs, and rich-text features require their own context and product rules;
this result does not validate encoding for those contexts.

## Reproduce the local case

The following commands come from the
[K01 reproduction guide](../cases/k01-stored-comment/README.md). Run them from
the repository root with Python 3.10+ and Git, using a new virtual environment
and an output directory that does not already exist:

```powershell
python -m venv .venv-k01
.venv-k01\Scripts\python -m pip install -r cases/k01-stored-comment/requirements-proof.txt
.venv-k01\Scripts\python -m playwright install chromium
.venv-k01\Scripts\python cases/k01-stored-comment/check_repro.py --profile local --output .dxa/k01-new-run
```

On Linux or macOS, use `.venv-k01/bin/python` in place of the Windows
interpreter path. To use installed Chrome, the guide provides this alternative;
replace `<chrome-yolu>` with the browser executable path:

```powershell
.venv-k01\Scripts\python cases/k01-stored-comment/check_repro.py --profile local --browser "<chrome-yolu>" --output .dxa/k01-chrome-run
```

The harness only targets its own loopback fixture. Use normal Python, without
`-O`: the gate rejects optimized execution because it disables assertions.
Missing browser dependencies, timeouts, and incomplete output are failed
reproductions, not successful negative controls.

A successful gated reproduction requires exit 0 and a newly generated
`acceptance.json`. The evidence includes `result.json`, `fix.diff`, and ten
request/response files. The gate checks shared CID/payload, HTTP results,
source and artifact hashes, one POST per control, and five distinct closed
fixture ports. Record the checkout commit and working-tree state alongside
the run. Review local paths and output before sharing a new evidence package.

## What the evidence supports—and where it stops

The [16 October technical acceptance](../audit/r5-final-acceptance-2026-10-16/README.md)
records a later clean Windows run with five passing browser controls and
five closed fixture ports. It also links the retained
[Linux workflow acceptance](../audit/2026-10-14-r5-linux-gate/README.md), whose
downloaded artifact was checked separately. Those runs have distinct source
provenance; they should not be presented as one new experiment.

The technical record demonstrates a repeatable stored-XSS proof, a root-cause
fix, and a same-input retest in this lab. It does not measure general scanner
accuracy, establish privileged access, or identify a third-party product issue.
The negative observations last 500 ms after page load and cover this
synchronous fixture; they do not prove the absence of delayed or iframe XSS.
Historical port-closure records describe the live run and cannot be recreated
by inspecting an archived file.

An automated Linux run is a separate environment, not an independent human
reproduction. The [independent-repeat form](../cases/k01-stored-comment/INDEPENDENT-REPEAT.md)
remains unfulfilled, as explicitly preserved in the technical acceptance.
The [portfolio evidence brief](../audit/2026-10-24-portfolio-cases/k01-case.md)
places this work within the same bounded claim: local fixture browser proof,
negative controls, context-appropriate encoding, and retained retest evidence.
