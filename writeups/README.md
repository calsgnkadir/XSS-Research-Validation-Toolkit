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

These mechanism-first notes preserve the original practice and field-assessment
material. Their historical labels and claims are not a current independent
acceptance; see each writeup's evidence status and the related C/K roadmap items.

| # | Title | Class | Historical basis and current evidence boundary |
|---|-------|-------|----------|
| 01 | [Why filtering isn't protection: the nested-tag sanitizer bypass](01-filtering-is-not-protection.md) | Sanitizer / mutation | Historical Juice Shop exercise; retained screenshots show request/filter context, not browser execution or a current product finding. |
| 02 | [Assessing DOM XSS in a hardened React SPA (a field methodology)](02-dom-xss-assessment-react-spa.md) | DOM XSS / source→sink audit | Historical author-reported assessment; exact bundle, headers, scope and reproducible proof are not retained here. |
| 03 | [SQL Injection: when your input becomes part of the query](03-sql-injection.md) | SQL injection | Historical Juice Shop challenge claim; UNION/blind sections are explanatory, with no matching request/response package. |
| 04 | [Forging JWTs: `alg:none` and RS256→HS256 key confusion](04-jwt-forgery.md) | JWT / authentication | Historical author-reported challenge; raw request/response and server verification trace are absent. |
| 05 | [IDOR / BOLA: the server checks who you are, not what's yours](05-idor-bola.md) | Access control / BOLA | Historical author-reported basket-ID observation; no same-object, two-account request/response pair is retained. |
| 06 | [Building an XSS bot: encoding a methodology as code](06-building-an-xss-bot.md) | Tooling / automation | Historical build diary; old counts are not current suite results, autonomous discovery proof, or CVE verification. |
| 07 | [Teaching the bot to log in, find its own targets, and shut up](07-teaching-the-bot-to-log-in.md) | Tooling / session handling | Historical implementation notes; old HIGH counts and login claims are not current product validation. |
| 08 | [What the bot doesn't shout about is what makes it useful](08-what-does-not-shout-matters.md) | Tooling / reporting | Historical report-count exercise; JSON-only output and URL counts do not establish vulnerabilities or precision. |
| 09 | [Three HIGH to one: a precision journey on real code](09-three-high-to-one-a-precision-journey.md) | Tooling / candidate filtering | Historical candidate reduction, not a precision score; a remaining HIGH is still a candidate. |
| 10 | [One shape was never enough: payload variants and WAF bypass](10-one-shape-was-never-enough.md) | Tooling / variants and mutations | Historical variant labels do not establish parser acceptance, execution, or WAF bypass; current gate behavior is described in the writeup. |
| 11 | [Four targets in one afternoon: what v3.10 actually did in the wild](11-four-targets-one-afternoon.md) | Tooling / historical report review | Archived 50 JSON-only rows and two Bludit classifications; the legacy `EXECUTABLE` label has no attached browser-proof artifact and is not a current finding. |

> The series contains a mix of local training, historical tool-development
> notes, and anonymized field-assessment claims. This index does not independently
> validate every underlying claim or establish current authorization. See the
> relevant C/K roadmap item and evidence record before reusing a claim.
