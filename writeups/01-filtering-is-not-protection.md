> Güncel tamamlayıcı kanıt: [K01 yerel stored XSS, fix ve retest](../cases/k01-stored-comment/README.md). Bu vaka aşağıdaki tarihsel hedeflerin bağımsız doğrulaması değildir.

> **Historical lab account — evidence limit.** This writeup records the author's 2026-09-28 local Juice Shop experiment. The archived screenshots show the header value reaching the Last Login IP field, but do not show a successful JavaScript canary. Treat the source/header path as an observation and the XSS/execution story below as **not independently verified by the retained evidence**. See the [audit](../audit/2026-09-28/DENETIM-RAPORU-TR.md), [current status](../STATUS.md), and [acceptance scope](../ROADMAP.md).

# Why filtering isn't protection: the nested-tag sanitizer bypass

> **TL;DR** — A single-pass filter that *deletes* dangerous substrings can be
> defeated by making the deletion itself assemble a new dangerous tag. Removing
> `<script>…</script>` from the right input leaves a working `<iframe>` behind.
> The act of sanitising is what builds the payload.

This is one of the first bugs that changed how I think about input handling. I
hit it while working the *Server-side XSS Protection* path on OWASP Juice Shop
(local, authorized) — it appears twice in this repository's findings: the
feedback comment (Finding 2) and the `True-Client-IP` header → Last Login IP page
(Finding 8), both behind the *same* server-side filter.

## The defense that feels reasonable

A very common instinct is: *"XSS is `<script>`, so strip `<script>`."* So the
server runs something like:

```js
// single pass, remove <script>…</script>
clean = dirty.replace(/<script.*?>.*?<\/script>/gi, '');
```

It looks safe. `<script>alert(1)</script>` in, empty string out. Ship it.

## Why it fails: deletion can *create* a tag

The filter reasons about the string it was **given**. It does not reason about
the string it **leaves behind**. Feed it this:

```
<<script>Foo</script>iframe src="javascript:alert(`xss`)">
```

Walk it as the filter does. It scans for `<script>…</script>` and finds exactly
one complete block — `<script>Foo</script>` — and removes it. `Foo` is just
inert filler to make the block well-formed. What is left?

```
<iframe src="javascript:alert(`xss`)">
```

Before sanitising, that leading `<` and the trailing `iframe src=…>` were **not**
a tag — the `<script>` block sat between them and broke them apart. After
sanitising, the two fragments fuse into a valid, live `<iframe>`. The filter did
not miss the payload; **the filter assembled it.**

This is a *mutation* example: filtering can change how a parser interprets the
remaining bytes. It illustrates why a string replacement rule is not, by itself,
a reliable HTML sanitizer. The exact Juice Shop payload and browser execution
described here are historical author-reported results; the retained screenshots
show a normal header value being stored and filtered payloads returning blank,
not the successful nested-tag execution claimed in the narrative.

## Why it then executes

Two small facts do the rest:

1. **`javascript:` URLs run.** `<iframe src="javascript:…">` executes its script
   when the iframe loads — no `<script>` tag needed.
2. **`<script>` inserted via `innerHTML` is inert, but event handlers and URL
   schemes are not.** That is why bypasses reach for `onerror`, `onload`, or
   `javascript:` rather than a raw `<script>` — a different, still-live code path.

In general, if an unsafe transformation leaves an executable construct in an
HTML-parsing sink, the browser may parse and execute it. That is a mechanism
description, **not a retained reproduction result for this Juice Shop path**.
The archived header screenshots do not demonstrate an iframe load, JavaScript
execution, or a confirmed finding.

## The pattern, generalised

The nested-tag trick is one shape of a bigger rule: **a blocklist that deletes
can be re-formed.** Classic siblings:

- `<scr<script>ipt>alert(1)</scr<script>ipt>` → strip both `<script>` tokens →
  `<script>alert(1)</script>` reassembles.
- Filters that lower-case, trim, or entity-decode *after* their check, so the
  value the check saw is not the value that renders.

Every one of these is the same failure: **one pass, no re-check, input ≠ output.**

## The fix that actually holds

Stop trying to enumerate "bad." Two controls do the real work:

1. **Context-aware output encoding — the default.** If the value only needs to be
   *text*, render it as text (`textContent`, template auto-escaping). `textContent`
   places the value in a text node instead of parsing it as markup. Most "sanitisation" is
   solving a problem you created by choosing an HTML sink for text.

2. **Allowlist parsing for genuine rich HTML.** If users truly need some HTML,
   parse it into a DOM, keep only a known-safe set of tags/attributes, drop the
   rest, using the correct output context and a maintained parser-based allowlist
   library — **DOMPurify**, `sanitize-html` — never a hand-rolled regex. Add
   regression tests for supported markup and avoid transforming sanitized output
   afterward.

Then layer defense in depth; neither control replaces correct output handling:

- **CSP** with a narrow `script-src`, nonces/hashes where appropriate, and no
  unsafe inline execution can reduce impact. It is defense in depth, not proof
  that injection is harmless or that all script-capable paths are blocked.
- **`HttpOnly`, `Secure`, and suitable `SameSite` cookie settings** reduce
  cookie theft and cross-site request risk. `HttpOnly` does not stop injected
  script from acting through the victim's authenticated page or reading
  non-cookie data.

Repeatedly applying a sanitizer until output appears stable is not a general
security fix: parser behavior, namespaces, decoding and later transformations
can still differ. For rich HTML, use a maintained parser-based allowlist
sanitizer in the correct context, and avoid modifying sanitized output later.

## Takeaway

**Filtering guesses at every dangerous input and always misses one — sometimes
the one it makes itself.** Encoding and allowlist parsing decide what output is
*allowed to be*, which is a question with a finite, correct answer. If you find
yourself writing `.replace(/<script>/…)`, you are defending the wrong layer.

---

*Historical account: OWASP Juice Shop via Docker was described as the target.
The retained evidence supports the header-to-field data path and filter
observations, but not successful execution; no current retest is claimed. See
the repository [README](../README.md) for project navigation.*
