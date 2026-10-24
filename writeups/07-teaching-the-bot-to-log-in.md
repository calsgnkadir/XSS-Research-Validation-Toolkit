> **Historical implementation snapshot — not a current feature guide.** Versions, counts, classifications and target results below describe an earlier iteration. A static `HIGH` label is a heuristic priority, a sanitizer-name match does not prove sanitization, and zero HIGH findings do not establish safety. The Bludit/CVE association is not independently established for the version described. Check [current status](../STATUS.md), [CLI documentation](../tools/dom-xss-analyzer/README.md), and [R8 limits](../audit/2026-10-16-r8-current-review/README.md).

# Teaching the bot to log in and check bounded target candidates

> **TL;DR** — [Writeup 06](06-building-an-xss-bot.md) shipped the first
> version of the XSS bot: static (`dxa`) + dynamic (`dxadyn`) source→sink
> together in one command. The historical notes describe three workflow gaps:
> JSON-based login support, locating stored reflections, and heuristic static
> candidates that needed review. **Modern admins log in over JSON, not HTML forms**; **stored
> reflections don't always live where you tell them to**; and **static analysis
> on well-written code can produce many heuristic HIGH-priority candidates**.
> This writeup is the historical fix pass — session import for SPA logins (`--cookie` /
> `--header`), bounded post-submit link checking (`--auto-check`), two more
> submission shapes (`--json-body`, `--header-target`), a third static language
> (PHP), an escape-aware false-positive squelch, and a visual HTML report.
> None of it is a new class; all of it is what "makes it a tool you'd actually
> hand to someone else."

The interesting rule this pass illustrates: the difference between "toy" and
"tool" is almost never a new attack technique — it's what happens on the second,
tenth, and thousandth run against a real target that doesn't cooperate.

## Problem 1 — the admin doesn't have an HTML form to scrape

`dxadyn --login` (writeup 06) fetches the login page, grabs the CSRF token from
a hidden `<input>`, POSTs credentials, follows the redirect. That's exactly the
1998 shape and it's exactly what most admins **used to** look like. Modern
admins (Grav's `admin2`, most React/Vue/Svelte-shell dashboards) render a
mostly-empty HTML shell and log in over a JSON call to `/api/v1/…`. No form,
no CSRF `<input>` — no purchase for scripted login.

Two flags close this without adding a real browser dependency:

```
--cookie "sid=abc; csrf=xyz"                     # attach one Cookie header to everything
--header 'Authorization: Bearer eyJ...'          # repeatable; bearer / X-CSRF / anything
```

The mechanism is a one-line change in `fetch()`: every request merges a shared
`EXTRA_HEADERS` dict on top of `User-Agent`. The user logs in **through their
own browser** (which handles the SPA, OAuth, MFA, whatever), copies the
session cookie out of DevTools, pastes it once, and every subsequent request
`dxadyn` makes rides that session. This is the **escape hatch every scanner
eventually adds** because the alternative — scripting five vendors' JS login
flows — is a full-time job.

A regression test opens a real HTTP echo server and asserts the header arrives
on the wire; no more silent "it looked like it worked."

## Problem 2 — the payload lands somewhere you didn't guess

The v2 stored mode required `--check http://target/tag/...` — the operator had
to *know* which page would carry the payload. Bludit's `/tag/<slug>` is a
classic example: the URL is derived from the tag value, and the theme doesn't
even link to it, so you either look at the source of the CMS or you guess.

`--auto-check` removes that. After the submit, `dxadyn` fetches a small set of
seeds (the submit's landing page, the target's origin `/`, and any
`--auto-check-from` URLs the operator passes), extracts every same-host `<a
href>` one hop out, and **verdicts every page whose body actually contains the
canary id**. No more guessing where the tag/comment/post surfaces. On Bludit's
CVE-2026-4420-shape tag stored XSS the full pipeline is:

```
login → submit admin/new-content (tags = canary) → crawl 33 pages → verdict
                                                → /tag/<slug> UNENCODED [auto]
```

Bludit's `alternative` theme is a good stress test because it *never* links to
`/tag/<slug>`. Auto-check would find nothing on its own. The `--auto-check-from
http://target/tag/{CID}-dxss` template covers this case honestly: the operator
tells the bot the URL *shape*, the bot fills in the canary id and probes it.
This is a bounded link-checking workflow: it cannot discover an orphan URL it
has never seen unless an operator supplies a route template. A verdict tightening ("markup
must follow the canary immediately, not somewhere near it") kills the false
positive where the canary lands inside a slug URL and the attribute's closing
`"` looks like an attribute breakout.

## Problem 3 — one submission shape isn't enough

`--target-field` posts an HTML form. The other two shapes real targets use are
**JSON body** (SPA admins) and **an HTTP header value** (headers that later
render into a page). v3.4 adds both, wired into the same `probe_stored` and
`probe_stored_auto` — the auto-crawler doesn't care how the canary was submitted,
only where it surfaces.

```
--json-body '{"tags":"{CANARY}","title":"probe"}'   # SPA / REST admin path
--header-target True-Client-IP                      # stored header injection
```

`{CANARY}` inside a JSON template is JSON-string-safe substituted (the canary's
`"` gets escaped so the template stays valid JSON); the header path uses the
same `EXTRA_HEADERS` hook as `--cookie`. The header shape is Finding #8's class
in this repo's Juice Shop assessment — the two-step `True-Client-IP` →
`lastLoginIp` render — with the manual steps automated.

## PHP joins JS/C# on the static side

`dxa` used to only read JS/TS and C#/.NET. Anything PHP-heavy (Bludit,
WordPress plugins, small self-hosted CMSes) got zero coverage and the bridge
(`dxa2dyn`) produced zero hints. v3.4 (co-committed) added PHP sinks
(`echo`/`print` of `$vars`, `<?= $var ?>`, Blade `{!! !!}`, Twig `|raw`, printf
family), PHP sources (`$_GET`/`$_POST`/`$_REQUEST`/`$_COOKIE`/`$_SERVER`/
`$_FILES`, `php://input`, Laravel `Request::input(...)` / `request()->…`,
Symfony `$request->…`), and — the interesting piece — **PHP taint** running on
the same bounded fix-point that JS uses, with a per-language `ASSIGN` regex.
A word-boundary bug had to be fixed en route (Python's `\b` doesn't treat `$`
as a word boundary; `(?<!\w)` lookbehind works for both PHP and JS identifiers).

The historical run reported `dxa` on Bludit's `bl-kernel/` (~110 PHP files) as
**260 findings, 0 HIGH**. This is a version-specific heuristic count, not a
validated expected number or evidence that all flows are safe. A recognizable
`Text::htmlEncode()` call does not prove every output path is correctly encoded.
On a plugin from a hobby developer with a `echo $_GET['q']` in it, the same
tool would fire HIGH and be right. The number a bot returns on well-written
code is as important as the number on bad code; if the well-written case is
noisy, no one uses the tool.

## Shutting up: the false-positive squelch

The first version of the escape-aware HIGH → MEDIUM downgrade did *"if there
is an escape call on this line, silence the finding."* That was too aggressive
against minified single-line blobs (jQuery's line 2 is 90 KB; `encodeURIComponent`
appears in it *somewhere*, so every real finding on that line got silenced).
The fix: **proximity.** The escape call must be within ~200 characters of the
sink's match position, and lines longer than 500 characters (minified) skip the
squelch entirely — they need eyes-on review anyway.

Regression numbers on the seeded example corpus + Bludit:

- `safe.php`  HIGH = 0 (escape sits next to the sink — silenced correctly)
- `vulnerable.php`  HIGH = 5 (no escape near the sink — unchanged)
- Bludit `bl-kernel/`  HIGH = 4 (jQuery's real `innerHTML` from `location.hash`
  is no longer silenced by a distant `encodeURIComponent`; recovered)

This is what "engineered" means, one drop at a time: catch a false pattern, add
a specific counter-heuristic, keep the corpus of what should and should not fire
in tests so the next change doesn't undo it.

## Visual output: `--html`

`dxa` had a self-contained HTML report from the beginning; `dxadyn` only wrote
text. `--html FILE` closes that. The two tools now share visual language — dark
GitHub-ish theme, severity/confidence badges, origin column
(`reflected` / `stored` / `stored-auto` / `dxa-guided`) — so the pair look like
one product. The Bludit run above renders as one `[HIGH]` `[unencoded]` row with
the canary URL, submit + check HTTP codes, and a warning strip that says exactly
what it says in the text output: *"reflection is not proof of execution — confirm
each HIGH in the browser (the surrounding HTML context decides whether the
payload actually runs)."* A screenshot of this report is what goes into a
portfolio.

## What "professional" honestly means (and doesn't)

After this pass:

| Class | Covered | How |
|-------|---------|-----|
| Reflected XSS | ✅ | `dxadyn <url>` |
| Reflected header XSS | ✅ | `--probe-headers` |
| Stored reflection checks | ✅ | `--stored --check` or bounded `--auto-check`; orphan routes need operator hints |
| Stored XSS (JSON API path) | ✅ | `--json-body` |
| Stored header injection (two-step) | ✅ | `--header-target` |
| SPA / bearer-token targets | ✅ | `--cookie` / `--header` |
| Static: JS / C# / PHP source → sink | ✅ | `dxa` |
| Static-guided dynamic probing | ✅ | `dxa2dyn`; candidate generation does not establish execution |
| DOM XSS via `location.hash` / `postMessage` | ❌ | needs a headless browser (Playwright) |
| Blind XSS (fires elsewhere / later) | ❌ | needs an out-of-band callback server |
| Payload mutation / WAF bypass | ❌ | this historical workflow used one canary shape; no WAF bypass result |
| Sink-context awareness (`<title>` vs `<body>`) | ⚠️ | flags reflection, not executability |
| Concurrency, rate-limit, robots.txt | ❌ | sequential; polite-crawl not implemented |

This list is a historical capability description, not an accuracy assessment.
It does not establish broad detection coverage or validate every listed mode.
The current tool's supported scope and evidence meanings are in the
[CLI documentation](../tools/dom-xss-analyzer/README.md). The blind spots above
aren't excuses; they are the *reasons* an interview conversation about this
tool has a second half. *"Why not headless?"* opens the door to a real
discussion about coverage vs deployment cost that a candidate who has thought
about the trade-off can defend.

## Takeaway

Between writeup 06 and this one, the historical implementation added session
header import, additional submission formats, and bounded checks of linked or
operator-supplied URLs. It did not discover arbitrary targets or prove browser
execution. Review still depends on the configured scope, the response context,
and separate browser evidence where execution is claimed.

---

*Historical author report: OWASP Bludit 3.16.2 in local Docker
(`localhost:8090`, admin credentials seeded via the login-plugin CLI), plus
seeded `examples/` corpus (safe.php / vulnerable.php / vulnerable.js /
vulnerable.cs / vulnerable.cshtml). Tool sources:
[`tools/dom-xss-analyzer/dxa.py`](../tools/dom-xss-analyzer/dxa.py),
[`dxadyn.py`](../tools/dom-xss-analyzer/dxadyn.py), and the bridge
[`dxa2dyn.py`](../tools/dom-xss-analyzer/dxa2dyn.py) — the historical account
lists 44 pytest cases; this is not a current test result. The Bludit/CVE-2026-4420
association is a reported similarity only; root-cause equivalence and
autonomous end-to-end execution are not independently verified here.*
