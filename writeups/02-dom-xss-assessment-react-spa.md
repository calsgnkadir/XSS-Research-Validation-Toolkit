> **Historical assessment account — scope and evidence limit.** This is an author-reported assessment of one anonymized public application. Its target identity, exact scope authorization, bundle snapshot, response headers, route inventory and reproducible evidence are not retained here for independent review. The statements below describe that historical account only; they do not establish that the application was safe or that the findings generalize. See the [audit](../audit/2026-09-28/DENETIM-RAPORU-TR.md), [status](../STATUS.md), and [roadmap](../ROADMAP.md).

# Assessing DOM XSS in a hardened React SPA (a field methodology)

> **TL;DR** — React normally encodes values interpolated as text in JSX, but
> that does not rule out reflected XSS in other contexts and says **nothing by
> itself** about DOM XSS, because a DOM XSS
> lives entirely in the browser: the app's own JavaScript takes a client-side
> **source** (URL fragment, `postMessage`, `referrer`) and hands it to a
> **sink** (`innerHTML`, `document.write`, `eval`). This writeup is the method I
> used to assess one anonymized e-commerce SPA — a **source → sink** audit
> described as static + dynamic. The historical negative observations are limited
> to one reported page/build and do not conclude that the application was safe.

> **Target anonymised on purpose.** The site is a live e-commerce React/Next.js
> app on a public bug-bounty program. No vulnerability was found and none is
> disclosed here; I keep the name out as basic disclosure hygiene. The value of
> this writeup is the *method*, which is identical on any target.

## Why reflected-XSS reasoning does not carry over

The historical account says the site's search reflection appeared encoded in
the inspected server-rendered response (`<` → `&lt;`, `"` → `&quot;`). This is
consistent with encoding on that observed path; the response and tested build
are not retained, and it says nothing about other templates, routes or client
rendering.

DOM XSS is a different bug in a different place:

```
reflected XSS:  attacker input --> SERVER builds HTML --> browser renders   (React encodes here)
DOM XSS:        attacker input --> browser JS builds/HTML --> DOM sink       (React never sees this)
```

One possible client-side source is the **URL fragment** (`location.hash`, the
`#...` part). Browsers do not include the fragment in the HTTP request target,
but client code can read it, transform it, and send data derived from it in a
later request. A server-side sanitizer cannot protect a purely client-side path
that never reaches the server; it also does not follow that every fragment-to-
DOM flow is exploitable. The source, transformations, sink and browser parsing
context must be traced.
That is why "reflected is safe" tells you nothing here, and why this pass was
worth doing.

## The method: source → sink, the same idea as the repo's linter

This is the exact model behind this repository's
[`dom-xss-analyzer`](../tools/dom-xss-analyzer/) and
[`methodology.md`](../methodology.md): locate the **sources**, locate the
**sinks**, and prove whether any source *reaches* a sink. The tool does it on
source you own; here I do it by hand on a live, minified bundle. Same reasoning,
two settings.

**The sinks I looked for** (the value becomes markup/JS):

| Sink | Why it's dangerous |
|------|--------------------|
| `.innerHTML` / `.outerHTML` | assigned string is parsed as HTML |
| `insertAdjacentHTML` | same, positional |
| `document.write` | writes raw HTML into the document |
| `eval` / `Function()` | string executed as code |
| React `dangerouslySetInnerHTML` | opt-out of React's escaping |

**The sources I looked for** (attacker-controllable, client-side):

| Source | Notes |
|--------|-------|
| `location.hash` | the prize — never reaches the server |
| `location.search` | often handled server-side, still worth tracing |
| `document.referrer` | attacker sets it via a linking page |
| `window.name` | survives cross-navigation, classic vector |
| `postMessage` (`addEventListener("message", …)`) | cross-frame data, frequently unchecked |

## Pass 1 — static: search the bundles

In DevTools → **Sources**, a project-wide search (`Ctrl+Shift+F`) over the
loaded JavaScript for each sink and source above. The bundle is minified, but the
tokens that matter don't rename: `location.hash`, `innerHTML`, and the browser
APIs stay literal even after minification, so text search still finds them.

What the historical author account reported (not independently reproducible
from retained bundle/response evidence):

- **`insertAdjacentHTML`** and **`window.name`** — *zero* matches. Two vectors
  eliminated immediately.
- **`innerHTML`** — many matches, but all inside the **React runtime**, analytics
  SDKs, or wrapped in **Trusted Types** (`typeof trustedTypes`, `createHTML(…)`).
  None was `element.innerHTML = <a source>`.
- **`dangerouslySetInnerHTML`** — React-internal plus a few app components
  (coupon text, promo "nudge" text) fed by **server-provided strings**, not by
  any URL/message input.
- **`document.write`** — a single hit, writing into an **iframe sandbox's**
  `contentDocument`, not fed by user input.
- **`location.hash` / `document.referrer`** — present, but **where** matters:
  almost all were third-party analytics (Bing, LINE, Clarity, GTM, Criteo) that
  read them for *tracking* — `encodeURIComponent(referrer)`, `return
  location.hash`, `-1 !== location.hash`. The site's own reads *returned or
  compared* the value; none flowed into an HTML sink.

The single most important observation: **sources exist, sinks exist, but no
source is wired to a sink.** DOM XSS needs the two to meet on one data path.
Here they never touch.

Two controls were discussed in the historical account; neither is independently
verified for the target by retained artifacts:

- **Trusted Types.** `trustedTypes` / `createHTML` references show API use or
  awareness in the inspected bundle, not enforcement. Enforcement requires the
  effective response policy (including `require-trusted-types-for 'script'`)
  and a compatible browser; neither is retained here.
- **CSP.** A reported `frame-src` block shows that a frame request was blocked
  under that policy. It does not establish a restrictive `script-src` or block
  all script paths; the effective CSP header is not retained.

## Pass 2 — dynamic: instrument the one live source

Static reading of minified code can miss a flow that only exists at runtime. The
one source with real listeners in the app's own code was `postMessage`, so I
confirmed it live. A **read-only** one-liner in the console registers a logging
listener — no page code is modified, nothing is sent anywhere:

```js
window.addEventListener('message', e => console.log('[msg]', e.origin, e.data), true);
```

(`addEventListener` returns `undefined` — that's the listener installing
correctly, not an error.) Then interact with the page — scroll, let carousels and
banners load, let widgets initialise — and watch the console.

The author reported that no `[msg]` event fired during the observed interaction
window. This does not show that no message can ever arrive, that all routes and
states were covered, or that listeners are unreachable. The listeners the
static search found were described as infrastructure — a
`MessageChannel`/`MessagePort` pair and a `setImmediate` polyfill — rather than
an observed `e.data → sink` path. This is a bounded negative observation, not
proof that the source is dead.

## The verdict, and why a negative result counts

The historical writeup labels its result **clean**. The supportable conclusion
is narrower: the author reported no source-to-sink path in one inspected bundle
and no message during one observed interaction window.

| Method | Result |
|--------|--------|
| Static source→sink search | author reported no path in the inspected bundle |
| Live `postMessage` instrumentation | author reported no message in one interaction window |
| Structural defenses | API markers and one reported frame block; policy enforcement not retained |

That historical account is not enough to conclude the application was clean.
At most, it records a bounded negative observation on one reported page and
one interaction window. A negative result needs the tested build/routes,
reachable states, source/sink traces, browser policy and time window recorded;
unobserved paths remain unknown.

It is also honest about scope: this covers **one page's bundle**. DOM XSS more
often hides on heavier, more dynamic views (product detail, account, search
filters) that ship different JavaScript, or in third-party widgets — the natural
next targets, assessed the same way.

## What made this target hard (the defensive lesson)

These are general defensive practices, not verified characteristics of the
anonymized target:

1. Framework output encoding protects values only where the renderer handles
   them in the intended context; review raw-render paths separately.
2. Trusted Types can enforce typed HTML sinks only when a restrictive policy is
   actually delivered and enforced.
3. CSP is defense in depth; inspect effective directives rather than infer
   script protection from a blocked frame request.
4. A token's absence from one bundle snapshot is bounded evidence, not proof
   that no route, lazy chunk, dependency or runtime state uses the sink.

## Takeaway

Reflected-safe is not DOM-safe: they are different bugs in different places.
Assess DOM XSS by enumerating sources and sinks, tracing transformations, and
checking reachable paths at runtime. A negative result applies only to the
tested build, routes, states, controls and observation window; it does not prove
that no path exists elsewhere.

---

*The original author stated this was performed under a public bug-bounty
program. Because target, scope record and reproduction artifacts are not
retained, that authorization and result cannot be independently checked from
this repository. No current target activity is claimed. The methodology mirrors this repository's
[`dom-xss-analyzer`](../tools/dom-xss-analyzer/) and [`methodology.md`](../methodology.md).*
