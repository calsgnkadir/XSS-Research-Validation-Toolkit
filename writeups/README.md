> **Historical / experimental reference — 2026-09-28 audit.** Capability and completion claims below are not a current guarantee. See [verified status](../STATUS.md) and [current acceptance criteria](../ROADMAP.md). A raw marker, scanner severity, callback or zero findings alone does not establish execution, a vulnerability or safety.

# Writeups and selected cases

This index separates three reviewable evidence paths from the historical
writeup series. The paths have different purposes and do not imply broad
scanner accuracy or a new vulnerability discovery.

## Selected portfolio cases

| Case | What it shows | Evidence and boundary |
|---|---|---|
| [K01 stored-comment proof → fix → retest](../cases/k01-stored-comment/README.md) | A local stored-XSS training fixture with one matching CID and a context-appropriate output-encoding fix | Five browser controls and fixture cleanup; not a product or CVE claim |
| [R9 browser-fixture regression](../audit/2026-10-16-r6-r9-final-source/README.md) | A measured failure in serial HTTP test fixtures and the threaded-fixture correction | Full local Chrome DOM suite 80/80; measures harness reliability, not detection accuracy |
| [R4 exact-payload replay](../audit/r4-proof-experiment-2026-10-16/README.md) | Historical scanner candidates replayed with a separate writer and reader-admin in raw/escaped loopback fixtures | Two Dalfox candidates produced dialogs in raw fixtures; other replays are inconclusive; no new scanner run or ranking |

[Reproduce the package demo and K01 case](../docs/PORTFOLIO-DEMO.md).

## Historical writeup series

These notes preserve the original practice and field-assessment material. The
06–10 entries form one tool-development series; their repeated historical
outcome claims are not separate measurements or current acceptance results.
See each writeup's evidence status and the related C/K roadmap items.

| # | Title | Focus | Historical basis and current evidence boundary |
|---|-------|-------|-----------------------------------------------|
| 01 | [Why filtering isn't protection: a nested-tag bypass mechanism](01-filtering-is-not-protection.md) | Sanitizer / mutation | The regex is an illustrative mechanism; retained screenshots show header-to-field/filter context, not execution or the historical route's implementation. |
| 02 | [Assessing DOM XSS in a hardened React SPA (a field methodology)](02-dom-xss-assessment-react-spa.md) | DOM XSS / source→sink audit | Historical author-reported assessment; exact bundle, headers, scope and reproducible proof are not retained here. |
| 03 | [SQL Injection: when your input becomes part of the query](03-sql-injection.md) | SQL injection | Historical Juice Shop challenge claim; UNION/blind sections are explanatory, with no matching request/response package. |
| 04 | [Forging JWTs: `alg:none` and RS256→HS256 key confusion](04-jwt-forgery.md) | JWT / authentication | Historical author-reported challenge; raw request/response and server verification trace are absent. |
| 05 | [IDOR / BOLA: the server checks who you are, not what's yours](05-idor-bola.md) | Access control / BOLA | Historical basket-ID claim remains unverified; a separate bounded Juice Shop replay documents two synthetic accounts, same-session cross-account basket access, and an anonymous 401 control. |
| 06–10 | [Tool-development series](06-building-an-xss-bot.md): [06](06-building-an-xss-bot.md) · [07](07-teaching-the-bot-to-log-in.md) · [08](08-what-does-not-shout-matters.md) · [09](09-three-high-to-one-a-precision-journey.md) · [10](10-one-shape-was-never-enough.md) | From static/dynamic workflow and session handling through report classification, candidate heuristics, and payload-variant experiments | Historical implementation snapshots, not separate success measurements. Old candidate counts, generated payload totals, labels, and target outcomes do not establish accuracy, autonomous discovery, JavaScript execution, CVE verification, or WAF bypass. The current bounded scope is summarized in the [project status](../STATUS.md) and [roadmap](../ROADMAP.md). |
| 11 | [Four targets in one afternoon: what v3.10 actually did in the wild](11-four-targets-one-afternoon.md) | Historical report review | Archived 50 JSON-only rows and two Bludit classifications; the legacy `EXECUTABLE` label has no attached browser-proof artifact and is not a current finding. |

> These writeups mix local training, historical tool-development notes, and
> anonymized field-assessment claims. This index does not independently validate
> every underlying claim or establish current authorization. See the relevant
> C/K roadmap item and evidence record before reusing a claim.
