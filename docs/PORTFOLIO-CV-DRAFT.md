# XSS Research — CV and Portfolio Draft

**Status:** reviewed, evidence-bounded wording ready to adapt to a role and CV
format. This file is not an externally published portfolio. These bullets do
not assign a professional level or claim a new CVE.

## English

**Project:** Python XSS research CLI and controlled validation fixtures

- Evaluated the static analyzer on two owned application source scopes;
  reproduced and fixed FormData/router false positives with independent
  regressions and a comparison against unchanged source hashes. This was
  source analysis, not live deployment penetration testing or XSS discovery.

**Current release:** [`dxa-research-toolkit==0.2.1` on PyPI](https://pypi.org/project/dxa-research-toolkit/0.2.1/).
The release includes the offline SARIF CLI and E05 parser-context extension;
`v0.1.0` remains the historical GitHub Release.

- Built a repeatable stored-XSS proof/fix/retest in a disposable local fixture,
  using a CID-matched browser canary, separate writer and reader contexts,
  positive and negative controls, and HTML text-context output encoding.
- Measured a bounded `textarea`/RCDATA parser-context coverage gap in an XSS
  research CLI with a JavaScript-disabled Chromium oracle; added an inert probe
  and negative controls. Parser placement is kept separate from JavaScript
  execution and vulnerability confirmation.
- Reproduced a known Spring Security BCrypt byte-boundary behavior against a
  synthetic local account, added a 72 UTF-8-byte guard and regression coverage,
  and reviewed current dependency applicability. No CVE was assigned to the
  application.

## Türkçe

**Proje:** Python XSS araştırma CLI aracı ve kontrollü doğrulama fixture'ları

- Statik analiz aracını kendime ait iki uygulamanın kaynaklarında denedim;
  FormData/router yanlış alarmlarını bağımsız regresyonlar ve aynı kaynak
  hash'leri üzerinde önce/sonra karşılaştırmasıyla düzelttim. Bu çalışma canlı
  deployment pentesti veya yeni XSS keşfi değildir.

- Geçici yerel fixture üzerinde CID eşleşmeli browser canary'si, ayrı yazar ve
  okuyucu bağlamları, pozitif/negatif kontroller ve HTML metin bağlamında çıktı
  kodlamasıyla tekrar üretilebilir stored-XSS kanıtı, düzeltme ve retest akışı
  oluşturdum.
- JavaScript kapalı Chromium oracle'ı ile XSS araştırma aracında sınırlı bir
  `textarea`/RCDATA parser bağlamı kapsam açığını ölçtüm; inert probe ve negatif
  kontroller ekledim. Parser yerleşimini JavaScript çalışması ve doğrulanmış
  açıklık sonucundan ayrı tuttum.
- Sentetik yerel hesapta bilinen Spring Security BCrypt bayt sınırı davranışını
  tekrar ürettim; 72 UTF-8 bayt sınırı ve regresyon kapsamı ekleyip güncel
  bağımlılık uygunluğunu inceledim. Uygulamaya CVE atanmadı.

## Evidence and presentation notes

- [K01 article](K01-CASE-STUDY.md) presents the retained local proof/fix/retest.
- [Owned-source false-positive acceptance](../audit/2026-10-30-r8-receiver-fix/README.md)
  supports the source-evaluation bullet. These static source refinements are
  unreleased and are not included in published PyPI 0.2.1.
- [Historical CVE research review (Turkish)](CVE-RESEARCH-REVIEW-TR.md)
  distinguishes research experience, known-CVE reproduction, and unverified
  historical duplicate claims from personal discovery credit.

- **Primary case, K01:** [case brief](../audit/2026-10-24-portfolio-cases/k01-case.md)
  · [fixture/evidence](../cases/k01-stored-comment/README.md). The execution
  evidence is from the repository's disposable training fixture, not a
  third-party product.
- **Second case, E05:** [case brief](../audit/2026-10-24-portfolio-cases/e05-case.md)
  · [acceptance limits](../audit/2026-10-24-e05-context/README.md). It proves
  inert parser marker placement only; it does not prove JavaScript execution,
  a confirmed XSS vulnerability, impact, or general detection accuracy.
- **Short CVE example, BCrypt:** [case brief](../audit/2026-10-24-portfolio-cases/bcrypt-case.md).
  This reproduces known upstream Spring Security behavior in one local path;
  it is not a new application CVE or production-impact demonstration. Its
  supporting source/remediation records are internal and need review before
  public linking.
- The public toolkit release is `0.2.1`; E05 is included in that package.
  The `v0.1.0` GitHub Release is historical and does not include E05.
- Do not include private raw captures, credentials, real account data, or an
  application/company name without the owner's approval. Keep test counts out
  of claims about real-product coverage or personal certification.

## Short profile summary

**English:** Security research project focused on XSS source/sink analysis,
bounded HTTP and browser evidence, context-aware proof/fix/retest workflows,
and honest separation of reflection, parser observations, execution, and
vulnerability triage.

**Türkçe:** XSS kaynak/sink incelemesi, sınırlı HTTP ve browser kanıtı, bağlama
duyarlı proof/fix/retest akışları ve reflection, parser gözlemi, JavaScript
çalışması ile açıklık triage'ını ayrı tutan güvenlik araştırma projesi.
