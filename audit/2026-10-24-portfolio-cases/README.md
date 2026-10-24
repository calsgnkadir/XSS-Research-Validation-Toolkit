# Portfolio case drafts — evidence-backed, 24 October 2026

Prepared from retained local audits for the coordinator. No new tests, target
requests, or external communications were performed for this document. These
are case summaries to adapt for a portfolio/CV; they are not new acceptance
claims. Keep each item's evidence type and limits with the summary.

## Curated order

1. **Primary case — K01 stored XSS proof/fix/retest:** [K01 case brief](k01-case.md).
2. **Second case — E05 textarea parser context:** [E05 case brief](e05-case.md).
   The measured evidence is inert parser placement; JavaScript execution and a
   confirmed XSS vulnerability were not established.
3. **Short CVE-applicability example — BCrypt:** [BCrypt case brief](bcrypt-case.md).
   This matches an already assigned Spring Security CVE; no CVE was assigned to
   Kadrom.

The sections below preserve the initial combined drafts. The three briefs above
are the selected order for a concise portfolio; they carry the evidence and
limits needed for each claim.

## Case 1 — Stored XSS proof, output-encoding fix, and retest

**Roadmap:** K01 / R5. **Target and authorization:** the repository's own
disposable `k01-v1.0` loopback training fixture. The fixture stores synthetic
comment text in memory; it is not a production application or third-party
target.

**Question and method:** can an anonymous writer's stored comment execute in a
separate clean reader browser when the renderer inserts it as raw HTML, and
does the intended plain-text fix stop the same input? A CID canary was submitted
once and observed only by reading the existing browser global; payload code was
not passed to `page.evaluate`.

**Expected and observed:** raw HTML plus JavaScript enabled produced the
matching CID in the reader. JavaScript-disabled, fixed-renderer and JSON-only
controls produced no CID. The fixed renderer uses HTML text-context escaping
(`html.escape(comment, quote=True)`), preserving the text while preventing an
`img` element from being created. The retained clean local repeat passed 5/5
controls.

**Evidence type:** fixture-level browser execution proof, positive and negative
controls, exact fix diff, and local repeat. See [K01 case](../../cases/k01-stored-comment/README.md),
[repeat record](../2026-10-14-r5-k01-clean-repeat/README.md), and the
[fix evidence](../../cases/k01-stored-comment/evidence/2026-10-05-verified/fix.diff).

**Limits:** this is a by-design vulnerable training fixture with synthetic
content, not a new real-product XSS/CVE discovery. The negative observation is
bounded by the fixture's synchronous 500 ms window. No privileged/admin role or
cross-user authorization boundary was tested. This demonstrates a reproducible
proof/fix/retest workflow; it does not certify broad scanner accuracy.

## Case 2 — Measuring and covering a textarea parser context

**Roadmap:** E05. **Target and authorization:** inert local browser documents
and synthetic parser fixtures belonging to this toolkit. Page JavaScript was
disabled for the parser oracle; no external target was contacted.

**Question and method:** do the current generated probe families place a marker
outside HTML `textarea` RCDATA, and is that parser context represented by the
tool's probe selection? The prior 50 families and 18 mutations (950 generated
attempts) were measured first; an inert closing-tag probe was then checked
against escaped and wrong-context controls in Chromium.

**Expected and observed:** before the extension, those 950 attempts produced
no marker element outside the textarea. The new inert probe produced one
parsed marker; its HTML-escaped form, default body, title control, and prior
textarea-opening controls produced none. The source selection passed 381 tests
with zero failures, errors, or skips, including the browser cases.

**Evidence type:** bounded parser-placement measurement, browser oracle with
JavaScript disabled, negative controls, and selected local regression suite.
See [E05 acceptance and limits](../2026-10-24-e05-context/README.md),
[coverage matrix](../2026-10-24-e05-context/coverage.md), and
[implementation/result details](../2026-10-24-e05-context/implementation.md).

**Limits:** marker placement is not JavaScript execution, vulnerability
confirmation, WAF bypass, sanitizer assurance, or a product accuracy score.
HTTP evidence remains reflection/unreviewed. This is a measured analyzer
context extension and should be presented as such.

## Case 3 — Known BCrypt boundary behavior, remediation, and applicability review

**Roadmap:** A05 / R7. **Target and authorization:** the user's authorized
local Spring application checkout, tested with its in-memory H2 test profile
and one synthetic account. No real account, external service, or production
deployment was used. Omit the private application name from a public portfolio
unless the owner has approved naming it.

**Question and method:** does the pinned Spring Security BCrypt path treat a
73-byte login as equivalent to the first 72 bytes used to create a synthetic
hash? The bounded local test sent exactly the 72-byte password and the same
value plus one byte through the login controller, then recorded only status and
whether the principal matched.

**Expected and observed:** the 72-byte control authenticated, as expected. The
73-byte value also returned HTTP 200 for the same synthetic principal. The
tested dependency baseline was Spring Boot 3.2.5 / Spring Security 6.2.4, which
was in the published affected range for the already assigned
[Spring Security CVE-2025-22228](https://spring.io/security/cve-2025-22228/).
The remediation aligned the application to Boot 4.1.1 / Security 7.1.1 and
enforced a 72 UTF-8-byte policy before hashing/authentication paths. Regression
coverage included the 72/73-byte boundary. Before a later test-only addition,
the relevant combined selector passed 51/51 and the full local Maven suite
passed 665/665. After adding a positive exact-72-byte multibyte password-change
regression, an auth-only selector passed 37/37; the full suite was not rerun
after that test-only change. Current source reconciliation rebound the selected
advisory review to `eb031a1`; no new applicable candidate
was identified in that selected list.

**Evidence type:** one synthetic-account H2/MockMvc reproduction, retained
source remediation and regression records, full local suite record, and a
later source/dependency disposition. See [bounded reproduction](../2026-10-22-a05-bcrypt-local-check/README.md),
[remediation](../2026-10-22-a05-bcrypt-remediation/README.md), and
[current-source reconciliation](../2026-10-24-a05-source-refresh/README.md).

**Limits:** this reproduced a known upstream library behavior in one local
authentication path; it did not prove practical account takeover, every
advisory precondition, or impact in production. The remediation is not
deployment evidence; existing-account recovery/rollout and production runtime
were not tested. No CVE was assigned to the application, and A05 remains
partial. Do not label this a newly discovered CVE.

## CV wording drafts

Use only the bullets whose scope and release status match the material linked
in the CV or portfolio. Keep the local-case context visible.

**English**

- Built and validated a Python XSS research workflow using a CID-matched
  stored-XSS proof, context-aware browser observations, negative controls, and
  a text-context output-encoding fix in a disposable local fixture.
- Measured a previously unrepresented HTML textarea parser context with an
  inert browser oracle and integrated the probe with regression coverage;
  distinguished parsed-marker observations from JavaScript execution proof.
- Reproduced a known Spring Security BCrypt byte-boundary behavior against a
  synthetic local account, added UTF-8 byte-length guards and regression tests,
  and documented current dependency applicability; no application CVE was
  assigned.

**Türkçe**

- Geçici yerel fixture üzerinde CID eşleşmeli stored-XSS kanıtı, negatif
  kontroller ve HTML metin bağlamında çıktı kodlaması düzeltmesiyle tekrar
  üretilebilir bir XSS araştırma akışı geliştirdim.
- HTML `textarea` parser bağlamını inert browser oracle ile ölçüp regresyon
  kapsamına ekledim; marker yerleşimini JavaScript çalıştırma kanıtından ayrı
  tuttum.
- Sentetik yerel hesapta bilinen Spring Security BCrypt bayt sınırı
  davranışını tekrar ürettim, UTF-8 bayt sınırı denetimi ve regresyon testleri
  ekledim, güncel bağımlılık uygunluğunu belgeledim; uygulamaya CVE atanmadı.

## Presentation checklist

- Link each claim to the cited sanitized audit/fix; never attach private raw
  request/response captures, tokens, cookies, real account data, or ignored
  `.dxa` files.
- State that K01 and the parser oracle are local training fixtures. State that
  the BCrypt result matches a known library CVE and is not an application CVE.
- The public toolkit artifact is `v0.1.0`; later E05/source changes are
  unreleased. Do not imply that the current source is included in that release.
- Do not turn the 14-case benchmark, test totals, generated-probe counts, or
  case outcomes into general-purpose detection accuracy, exploit-count,
  severity, or professional-certification claims.
