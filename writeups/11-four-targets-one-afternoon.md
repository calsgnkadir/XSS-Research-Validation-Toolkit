> Güncel tamamlayıcı kanıt: [K01 yerel stored XSS, fix ve retest](../cases/k01-stored-comment/README.md). Bu vaka aşağıdaki tarihsel hedeflerin bağımsız doğrulaması değildir.

> **Historical report snapshot — count and proof limits.** The retained HTML reports contain 50 `json-only` rows across A/C2, zero reflected findings for B/C1, 78 static candidates in B1, and two Bludit rows (one `BREAKOUT-REQ`, one `EXECUTABLE` tool classification). They do not show 75 JSON findings, and D2 is not browser-execution proof. The reports are from 2026-09-26 and do not establish current target behavior, overall safety, or a confirmed Bludit vulnerability. See [C11](../ROADMAP.md), [report inventory](../audit/2026-09-28/DENETIM-RAPORU-TR.md), and [current status](../STATUS.md).

# Four targets in one afternoon: what v3.10 actually did in the wild

> **TL;DR** — After the [v3.10 pass](10-one-shape-was-never-enough.md)
> landed (payload variants + mutation options; the archived 101-test count is
> historical and not a current run),
> the bot got pointed at four running targets in one sitting: three
> own-code projects (`hotel-platform` React + Spring Boot, `mahrem`
> FastAPI + vanilla JS, `wallet-api` ASP.NET Core) and one deliberately
> vulnerable CMS (`Bludit 3.16.2` in local Docker). The three modern
> API-first projects returned what the historical tool classified as
> returned **50 rows classified `json-only`, 0
> `executable`, 0 `breakout-req`** — the Content-Type gate held; a
> reflection in a JSON response is not by itself a browser exploit. Bludit,
> the local target described in the old run, returned the historical v3.10
> classification: with `--variants body` the tag value scored `breakout-req` (the
> canary landed in `<title>` and the bot correctly said "escape needed
> first"); with `--variants title-breakout` on the *same target, same
> sink, same login* the report scored **`executable`**. This is a stored
> scanner classification. The archived output does not include independent
> JavaScript execution evidence, so it does not prove that the marker cleared
> title context or that an XSS was directly triggerable.

This writeup preserves a historical field report. The archived HTML files
are the evidence for the tool output; they do not independently verify every
target/setup assertion or browser execution described below. The files are
from **2026-09-26** and are linked here:
[`../reports/2026-09-26-v310-live/`](../reports/2026-09-26-v310-live/).

## The line-up

| Target | Stack | Why in the sample | Auth | Where the canary went |
|---|---|---|---|---|
| **hotel-platform** | React 18 + Spring Boot 3 + MySQL | Own project. Repeat target since [writeup 09](09-three-high-to-one-a-precision-journey.md). | Bearer JWT | `PUT /api/candidate/profile` → `fullName` |
| **mahrem** (ex health-blockchain) | FastAPI + vanilla JS front-end | Own project. Public HTML landing plus API. | none for public surface | reflected crawl + 4-header probe |
| **wallet-api** | ASP.NET Core 8 + PostgreSQL 18 | Own project. Pure JSON REST + Swagger. | Bearer JWT | `POST /api/Transactions/transfer` → `description` |
| **Bludit 3.16.2** | PHP CMS, reported local Docker target | Historical tags-field reflection report; CVE/root-cause and execution not independently verified. | session cookie via `--login` (reported) | `POST /admin/new-content` → `tags` (reported) |

Every command was `python dxadyn.py` from
[`tools/dom-xss-analyzer/dxadyn.py`](../tools/dom-xss-analyzer/dxadyn.py)
on a fresh clone; no local wrapper, no manual mutation.

## Test A — hotel-platform: 25 shapes, one right verdict

The command was one line (JWT captured beforehand, PUT dispatch, JSON
body, canary in `fullName`):

```bash
python dxadyn.py --stored \
  --header "Authorization: Bearer $JWT" \
  --method put --csrf-field "" \
  --target "http://localhost:8081/api/candidate/profile" \
  --json-body '{"fullName":"{CANARY}", "phone":"05551000000", ...}' \
  --check "http://localhost:8081/api/candidate/profile" \
  --variants all --waf-bypass
```

`--variants all --waf-bypass` = 5 variants × (1 + 4 mutations) = **25
distinct submits**, each with its own cid, its own marker, its own
verdict pass. The bot printed 25 finding rows, one per shape:

```
[JSON-ONLY] context=json-body                                    variant=body
[JSON-ONLY] context=json-body variant=body/case
[JSON-ONLY] context=json-body variant=body/split-cmt
[JSON-ONLY] context=json-body variant=body/whitespace
[JSON-ONLY] context=json-body variant=body/url-encode
[JSON-ONLY] context=json-body variant=title-breakout
[JSON-ONLY] context=json-body variant=title-breakout/case
...
[JSON-ONLY] context=json-body variant=url-scheme/url-encode

25 unique stored candidate(s) - 0 EXECUTABLE, 0 need a follow-on breakout.
```

Every canary landed in the response body (Spring's `Jackson` serialised
`fullName` back verbatim in the JSON DTO). Every content-type header
was `application/json`. Every variant, including the four `-breakout`
ones that would have upgraded on HTML, stayed `json-only`. That is
the v3.7 Content-Type gate holding under 25× pressure: **the browser
does not parse `application/json` as HTML**, so a stored reflection
there is not a browser-executable XSS, no matter which shape got in.

Would the operator want to know? Yes — a stored raw string in a JSON
response is still worth reviewing (a downstream client might feed it
into `dangerouslySetInnerHTML`), which is why the tool reports it at
all. But it is not scored as an exploit that fires in isolation, and
that discipline held.

## Test B — mahrem: 25 shapes × N inputs × 4 headers, zero reflections

Mahrem serves an HTML landing page and API endpoints. Its public
surface was probed with `--variants all --waf-bypass` at depth 2, plus
a header probe on the four common upstream headers a reverse-proxy
app tends to echo:

```bash
python dxadyn.py http://127.0.0.1:8000/ --depth 2 \
  --variants all --waf-bypass \
  --probe-headers "X-Forwarded-For,Referer,User-Agent,X-Real-IP"
```

Result:

```
[dxadyn] probing http://127.0.0.1:8000/ (depth=2) variants=[body,title-breakout,
  attr-breakout,script-breakout,url-scheme] +waf-bypass(x4/variant)
[dxadyn] header probe: X-Forwarded-For, Referer, User-Agent, X-Real-IP
No unencoded reflections found. (Inputs may be encoded, POST-guarded, or absent.)
```

Zero. Static side (dxa on the source repo) reported 78 JS medium-level
sinks — all in the vanilla JS front-end (`element.innerHTML =` patterns
that a review might harden but that had no observable server-echo
channel) — and **0 Python HIGH**. FastAPI + `JSONResponse` all the way
through, no server-side HTML templating, no header echo. This is the
tool doing the right thing when the target is genuinely quiet: it does
not manufacture findings to look busy.

## Test C — wallet-api: the same discipline on ASP.NET Core

Register a second user Bob (self-transfer is blocked by design — a
small bit of the app's own defense in depth), deposit some balance,
then transfer to Bob with `description="{CANARY}"`. `--variants all
--waf-bypass`, JWT auth:

```
[JSON-ONLY] context=json-body variant=body
[JSON-ONLY] context=json-body variant=body/case
...
[JSON-ONLY] context=json-body variant=url-scheme/url-encode

25 unique stored candidate(s) - 0 EXECUTABLE, 0 need a follow-on breakout.
```

Same shape as hotel-platform. The description string round-trips
through the `POST /transfer` handler, gets written to Postgres, comes
back in `GET /api/Transactions` — every time as a JSON string field
in an `application/json` body. Content-Type gate: `json-only`, 25 for 25.

The reflected pass on `/swagger/index.html` at depth 2 with header
probe returned zero. Swagger UI is a static page; the API endpoints
sit behind auth. Nothing to reflect.

## Test D — Bludit: the point of v3.10, in one before/after

The historical account says v3.10 was run against Bludit to observe its
variant-related severity label. It was not an independent browser execution
test, a new bug finding, or autonomous discovery: the operator provided the
target, login, fields and route template.

Two commands, minimal delta:

```bash
# Command 1: baseline (historical body variant)
python dxadyn.py --stored --auto-check \
  --auto-check-from 'http://localhost:8090/tag/{CID}-dxss' \
  --login http://localhost:8090/admin/login --user admin --pass labpass123 \
  --target http://localhost:8090/admin/new-content --target-field tags \
  --extra "title=v310demo1,slug=v310demo1$RND,content=b,type=published,..."
```

Output:

```
http://localhost:8090/tag/dxa406473f3-dxss  [BREAKOUT-REQ] context=title [auto]
1 unique stored candidate(s) - 0 EXECUTABLE, 1 need a follow-on breakout
```

The archived report labels the row `<title>` / `breakout-req`. This records
the scanner's context classification; the raw response bytes and browser DOM
are not independently preserved here.

```bash
# Command 2: same target, same login, one flag change
python dxadyn.py --stored --auto-check \
  --auto-check-from 'http://localhost:8090/tag/{CID}-title-dxss' \
  --variants title-breakout \
  --login ... --target ... --target-field tags \
  --extra ...
```

Output:

```
http://localhost:8090/tag/dxa8bbfada8-title-dxss  [EXECUTABLE] context=title
  variant=title-breakout [auto]
1 unique stored candidate(s) - 1 EXECUTABLE, 0 need a follow-on breakout
```

The historical output records a different payload shape and a different tool
label. The bot submitted
`dxa8bbfada8</title><dXsS>` as the tag value, Bludit slugified it to
`dxa8bbfada8-title-dxss` (angle brackets and slashes reduced to
dashes), and the `/tag/<slug>` page rendered:

```html
<title>tag: dxa8bbfada8</title><dXsS> | Bludit</title>
```

The writeup inferred that the browser would close the title at the injected
`</title>`, placing the marker in body context. The retained report does not
show parsed DOM or JavaScript execution. In the historical tool design,
`_apply_ct_gate` was described as seeing:

- `reflection = "unencoded"` (marker survived raw)
- `_is_html_response("text/html")` = True
- `variant = "title-breakout"` ends with `"-breakout"`

→ severity labelled `executable`. That label is not a browser oracle. Current
source does not make this upgrade based on the variant name; see the scope note
in [writeup 10](10-one-shape-was-never-enough.md).

This was the v3.10 design thesis: **payload shape can change the observed
response context.** Parser behavior and script execution still require a
browser check. The historical output alone does not state which verdict is true.
Before v3.10, the operator saw `breakout-req` on this exact target
and had to hand-craft a payload with `</title>` themselves. After
v3.10, the tool did that step and reported `executable`. That is a
minute of triage time saved per finding of this shape, and — more
importantly — a class of exploit that no longer requires operator
skill to *identify*.

## What the four archived reports record

- **The archived JSON responses were classified as JSON-only.** Hotel-platform and wallet stored runs contributed 25 rows each (50 total); mahrem returned no reflections. These observations are not a measured global false-positive rate or proof that the applications are secure.
- **Zero-finding runs are bounded observations.** Mahrem returned 0
  reflections across 25 × N inputs × 4 headers at depth 2. The tool
  report says "nothing reached that shape" in that run. This does not
  establish that the target was well-designed, safe, or free of other paths.
- **Variant-aware severity was exercised as a historical classification.** Bludit before v3.10:
  `breakout-req`. Bludit after v3.10, one CLI flag changed:
  `executable`. Same reported sink, different tool label. The archived
  reports do not include browser-execution proof.
- **The same tool was configured for different runtime stacks.** Target-specific URLs, fields, credentials and read locations were still required. This is not evidence of fully autonomous target discovery.

## Honest boundaries this run does *not* cross

- **None of these targets had a real WAF.** The four WAF-bypass
  mutations were fired for completeness (which is why the count is
  25, not 5), but this run did not prove they defeat a production
  rule set. The next honest test is a lab target behind ModSecurity
  with default OWASP CRS on.
- **Bludit version/CVE status is not established by these reports.** The
  historical target was labelled 3.16.2 and associated with a public CVE,
  but this repository does not preserve a vendor-fix comparison proving
  root-cause equivalence or patch status for that instance.
- **DOM XSS remained invisible.** All four targets have client-side
  JavaScript. A hash-based DOM XSS (`location.hash → innerHTML`)
  would not have been caught by any of these runs. This is the honest
  known gap; the fix is Playwright, and it is not shipped yet.
- **No blind-XSS out-of-band channel.** A canary that fires in an
  admin panel viewed by another user hours later stays invisible.

## Takeaway

Writeups 06–10 talked about what v3.10 *should* do. This one is a
plain field record of what the tool reported on 2026-09-26 against four
services. The three own-code projects had the archived scan outcomes above;
they were not established as clean. The Bludit report contains a row labelled
`executable`, but that label is not independent browser proof or vulnerability
triage.

Same source→sink framing, preserved as a dated tool-development record. The
historical test count is not current, and the archived `EXECUTABLE` label is
not evidence of confirmed execution.

---

*Hands-on, on authorized local targets. hotel-platform / mahrem /
wallet-api are the author's own projects. Bludit runs in a
namespaced Docker container. All raw HTML reports for this run are
in [`reports/2026-09-26-v310-live/`](../reports/2026-09-26-v310-live/).
Related: [writeup 06](06-building-an-xss-bot.md) (the Bludit sink,
first documented), [writeup 08](08-what-does-not-shout-matters.md)
(the CT gate this run relies on), [writeup 09](09-three-high-to-one-a-precision-journey.md)
(hotel-platform's static-side story), [writeup 10](10-one-shape-was-never-enough.md)
(the v3.10 rule the Bludit before/after actually proves).*
