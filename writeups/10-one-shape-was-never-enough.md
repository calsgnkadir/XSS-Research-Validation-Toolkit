> Güncel tamamlayıcı kanıt: [K01 yerel stored XSS, fix ve retest](../cases/k01-stored-comment/README.md). Bu vaka aşağıdaki tarihsel hedeflerin bağımsız doğrulaması değildir.

> **Historical variant-design snapshot — execution claim withdrawn.** This writeup describes an early implementation and its payload-shape experiments. Marker survival, a `-breakout` name, HTML response, or a `dxadyn` severity label does not prove parser escape or JavaScript execution. The archived Bludit D2 report is explicitly only an `EXECUTABLE` scanner classification; independent browser proof and a fix/retest are absent. The 950/variant count is not 950 working exploits or WAF bypasses. See [C10](../ROADMAP.md), the [audit](../audit/2026-09-28/DENETIM-RAPORU-TR.md), and [current evidence limits](../tools/dom-xss-analyzer/EVIDENCE-CONTRACT.md).

# One shape was never enough: payload variants and WAF testing hypotheses

The details below preserve a historical feature proposal/report and are not a
current contract. In the current `dxadyn.py`, `_apply_ct_gate()` classifies an
HTML observation through `_severity(reflection, context)`; the `variant`
argument does not upgrade a label to execution. Therefore the variant-upgrade
snippet and expected test result below do not describe current source behavior.
No stored report here demonstrates that a WAF was bypassed or that the marker
executed in a browser.

> **TL;DR** — Up through v3.9 the bot sent exactly one canary shape:
> `cid"<dXsS>`. A value inside `<title>` / `<script>` / an HTML attribute
> could receive the legacy `breakout-req` label. That marker and label
> provide no browser execution evidence. The historical v3.10 notes proposed
> variants and mutations; they do not establish parser escape or execution.
> **Payload variants** send five context-tuned shapes (body, title-break,
> attr-break, script-break, url-scheme) — each with its own cid so
> verdicts stay separately attributable. A marker surviving raw is still a
> reflection observation, not proof that a parser reached an executable
> position. The archived `EXECUTABLE` output is a tool label, not browser
> proof. **Payload mutations** add alternate strings; their presence does not
> demonstrate bypass of any WAF. Same
> flags work in reflected + stored + header-probe modes; total shapes
> per round in that snapshot was `variants × (1 + 4 if waf-bypass else 1)`.

The historical design expanded the strings submitted to a target. Its
retained reports measure reflections and scanner classifications; they do
not establish additional executable contexts or successful WAF bypasses.

## What one shape couldn't tell you

Writeup 09 reported a historical scanner HIGH count changing from 3 → 1;
that is a classification change, not a confirmed-vulnerability measurement.
The title-context scenario from [writeup 06](06-building-an-xss-bot.md)
motivated the variant proposal. Its reported response shape was:

```html
<title>tag: <STORED_VALUE> | Site</title>
```

Send the historical body-shape canary `cid"<dXsS>`, and the response has:

```html
<title>tag: dxaXX"<dXsS> | Site</title>
```

`<dXsS>` survives raw. `verdict()` says **unencoded**. `find_context()`
says **title**. The v3.5 severity ladder says **breakout-req** — the
marker is present in title text. That legacy label does not establish how
the complete document parses or whether any event handler can execute.

If you send `cid</title><dXsS>` instead, the response becomes:

```html
<title>tag: dxaXX</title><dXsS> | Site</title>
```

In this isolated HTML example, `</title>` can end the title element.
`<dXsS>` itself contains no JavaScript or event handler. Its raw presence
does not prove execution, and substituting a different payload would require
a separate browser observation under the actual document and policy.
The historical `executable` classification based on the variant name was
an unsupported upgrade; it has been withdrawn.

## The five payload variants

The historical five-entry `PAYLOAD_VARIANTS` dictionary used
`(suffix_appended_to_cid, marker_that_must_survive_raw)`. The following
strings describe marker probes, not five working execution payloads:

```
body            cid"<dXsS>               (default; body/free context)
title-breakout  cid</title><dXsS>        (title-closing probe)
attr-breakout   cid"><dXsS>              (quote/markup probe)
script-breakout cid';<dXsS>//            (legacy string probe; not valid JS proof)
url-scheme      cidjavascript:/*<dXsS>*/ (legacy ineffective URL-execution probe)
```

**Legacy/ineffective shapes:** `script-breakout` does not close an HTML
script element, and the literal `<dXsS>` is not executable JavaScript.
For `url-scheme`, the CID precedes `javascript:`, so the URL does not begin
with the `javascript:` scheme. The suffix also contains only a comment,
with no executable canary. Neither shape proves script or URL execution.
The current separate [R3 browser proof](../tools/dom-xss-analyzer/BROWSER-PROOF.md)
uses an executable CID-matched canary; its `href` option performs a real
click and uses `void(...)`. That is not the marker probe shown here.

The CID is `dxa` plus eight random hex characters. The suffix is appended
to it; `verdict()` looks for the marker immediately after a returned CID.
Separate CIDs distinguish attempts, not independent vulnerabilities, and
do not establish parallel HTTP execution. Context parsing and executable
behavior cannot be inferred from the suffix name.

CLI:

```bash
--variants title-breakout,attr-breakout          # pick specific ones
--variants all                                   # every registered variant
--variants body                                  # default = historical
```

`make_canaries_for(variants)` yields `(vname, cid, canary, marker)` tuples
one after the other. Every probe path — stored, stored-auto, reflected
crawl, header probe — iterates the yield, so *anywhere* a canary was
being made, N canaries are made now.

## Historical variant-aware severity: withdrawn upgrade rule

**Obsolete implementation excerpt — do not copy as a current contract.**
The old rule inferred parser escape and execution from the variant name
and raw marker. Neither input establishes those facts. The current
`_apply_ct_gate()` does not perform this upgrade:

```python
def _apply_ct_gate(reflection, context, content_type, variant="body"):
    if _is_html_response(content_type):
        if reflection == "unencoded" and variant.endswith("-breakout"):
            return context, "executable"
        return context, _severity(reflection, context)
    ...
```

The `executable` return above is a legacy false inference. Current HTTP
classification reports `html-reflection` for an unencoded HTML marker,
including a `title-breakout` marker. A JSON response is `json-only` and
remains a reflection observation; later DOM consumption would need separate
analysis. See the [HTTP evidence contract](../tools/dom-xss-analyzer/HTTP-EVIDENCE.md).

**Historical test excerpt — the first expectation is obsolete and must
not be restored.** These snippets are not newly run test evidence:

```python
def test_ct_gate_breakout_variant_upgrades_to_executable():
    ctx, sev = dxadyn._apply_ct_gate("unencoded", "title", "text/html",
                                     variant="title-breakout")
    assert sev == "executable"

def test_ct_gate_breakout_variant_does_not_bypass_json_downgrade():
    ctx, sev = dxadyn._apply_ct_gate("unencoded", "body", "application/json",
                                     variant="title-breakout")
    assert sev == "json-only"
```

## Historical WAF-bypass mutation hypotheses

Some targets sit behind a regex WAF that anchors on the literal marker
(`<dXsS>` or common event handlers). If the base variant is blocked, no
variant may reach the observed response and the tool can go silent — an
ambiguous result. The historical `--waf-bypass` option added four string
transforms; their names do not establish WAF bypass or equivalent parsing:

```
case        <dXsS> -> <DxSs>          (case-swap)
split-cmt   <dXsS> -> <d<!---->XsS>   (legacy ineffective tag-reconstruction claim)
whitespace  <dXsS> -> <dXsS  >        (extra trailing space in tag)
url-encode  <dXsS> -> %3CdXsS%3E      (URL-encoded angle brackets)
```

**`split-cmt` correction:** inserting a comment-like string inside a tag
name does not make the HTML parser reassemble the original `<dXsS>` tag.
Raw survival of `<d<!---->XsS>` proves only that those bytes returned.
URL-encoded brackets likewise require an observed decoding step before any
HTML interpretation can be inferred. No retained WAF/browser comparison
demonstrates bypass for these transforms.

Each mutation gets its own fresh cid (re-embedded via a single
`.replace(cid, mut_cid, 1)`), so the four mutations of a single variant
have four independent verdicts. Output tags the mutation on the variant
name: `body/case`, `title-breakout/split-cmt`, etc.

Historical fan-out math: `len(variants) × (1 + 4 if waf-bypass else 1)`. So
`--variants all --waf-bypass` = 5 × 5 = 25 submits per stored round.
This is the five-variant/four-mutation snapshot only. The current registry
has expanded; 25 is not its present attempt count or a bypass count.
Transforms can be no-ops or duplicates for particular variants; current
`_mutation_outcomes()` records that distinction. Fresh CIDs alone do not
make wire shapes meaningfully different.

Two historical test excerpts (the four-name/five-output expectations are
snapshot-specific, not current registry assertions or new test results):

```python
def test_make_canaries_for_waf_bypass_multiplies_by_five():
    out = list(dxadyn.make_canaries_for(["body"], waf_bypass=True))
    assert len(out) == 5
    assert out[0][0] == "body"                    # base first
    assert {t[0] for t in out[1:]} == {"body/case", "body/split-cmt",
                                        "body/whitespace", "body/url-encode"}

def test_waf_mutations_return_named_triples():
    triples = dxadyn._waf_mutations('dxaAAAA"<dXsS>', '<dXsS>')
    names = [t[0] for t in triples]
    assert names == ["case", "split-cmt", "whitespace", "url-encode"]
```

## Everywhere, not somewhere

The historical design threaded `--variants` and `--waf-bypass` through
these probe paths:

- **Stored mode** (`--stored --check` or `--stored --auto-check`):
  each variant × mutation is a separate submit, own cid, own verdict.
  Auto-check crawls candidate pages once and grades each candidate
  against every submitted cid — one HTTP fetch per candidate, N
  verdicts, cheap.
- **Reflected mode** (`crawl(url, depth, variants=, waf_bypass=)`):
  `probe_form` and `probe_link` iterate variants × field / variants ×
  param. The `crawl()` dedup key now includes the variant name, so a
  body + attr-breakout reflection on the same param stays as two rows
  (different attempts; neither row establishes an exploit).
- **Header probe** (`--probe-headers` + `--variants`): each header × each
  variant × each mutation is a separate probe. Bludit-shape stored
  header XSS (`True-Client-IP` → Last Login IP) can now be tried with
  a different marker shape. This is a historical scenario proposal, not a
  retained browser execution result.

## Scope boundaries of the historical pass

The following boundaries describe the old proposal. Current DOM inspection,
callback journaling and browser proof are documented separately in
[STATUS](../STATUS.md); they do not retroactively validate old observations.

- **`--waf-bypass` is opt-in.** The four mutations are not defaults
  because a 5× cost multiplier on every stored round is aggressive
  bandwidth on friendly targets. It exists for the case where the base
  clearly isn't reaching (all reflections silent, but you know user
  data lands somewhere).
- **DOM observations were outside this snapshot.** The historical probes
  inspected server response bodies and did not drive a browser. A
  `location.hash` → `innerHTML` path requires separate browser analysis;
  a sink name alone does not establish execution. The current observer and
  CID-matched proof command are separate implementations.
- **Blind observations were outside this snapshot.** It had no callback
  server or out-of-band channel. A delayed read by another user could go
  unobserved; the current callback journal does not retroactively prove it.
- **The historical variant gate covered HTML responses.** JSON reflections
  stayed `json-only` regardless of variant; this classified the HTTP response.
  A future round could add JSON-specific *client-side* variants (a value
  that a React frontend hands to `dangerouslySetInnerHTML`), but that
  needs browser rendering to verify — same Playwright thread.

The original note reported **101 pytest cases**, ten added tests and zero
third-party dependencies for that snapshot. A matching run/commit package
is not attached here; these are historical author-reported counts, not a
new test run or the current dependency/test inventory. The generated
950-shape total mentioned in the series is also a registry/attempt count,
not 950 distinct working exploits, verified parser behaviors or WAF bypasses.

## Takeaway

Alternate marker shapes can reveal different reflection observations.
Silence remains inconclusive: it does not identify the filtering stage or
prove safety. A returned marker also does not prove parser escape or
execution. The historical change from `breakout-req` to `executable` was a
scanner label change whose execution implication has been withdrawn.

Current execution evidence needs an actual executable canary and a matching
browser observation. Vulnerability impact still requires separate triage.
The [K01 local fixture](../cases/k01-stored-comment/README.md) demonstrates
that evidence chain and fix/retest for its own controlled case; it does
not validate the historical Bludit or WAF claims in this note.

---

*Hands-on, on authorized local targets and fixtures only. Reference:
[writeup 06 (Bludit tag-XSS)](06-building-an-xss-bot.md) for the
title-context scenario this variant addresses; [writeup 09 (hotel-platform
3 → 1)](09-three-high-to-one-a-precision-journey.md) for the precision
work that preceded this shape-diversity pass; and
[writeup 08 (what doesn't shout matters)](08-what-does-not-shout-matters.md)
for the historical Content-Type gate discussion. Current tool sources:
[`tools/dom-xss-analyzer/dxa.py`](../tools/dom-xss-analyzer/dxa.py) +
[`dxadyn.py`](../tools/dom-xss-analyzer/dxadyn.py) +
[`dxa2dyn.py`](../tools/dom-xss-analyzer/dxa2dyn.py). Current test provenance
and dependency scope: [VALIDATION](../VALIDATION.md) and
[installation guide](../docs/PORTFOLIO-DEMO.md).*
