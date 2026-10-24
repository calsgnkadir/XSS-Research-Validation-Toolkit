# XSS Research — CV and Portfolio Draft

**Status:** draft text based on retained local evidence. Adapt the wording to
the actual role and CV format. These bullets describe bounded work; they do
not assign a professional level or claim a new CVE.

## English

**Project:** Python XSS research CLI and controlled validation fixtures

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

- **Primary case, K01:** [case brief](../audit/2026-10-24-portfolio-cases/k01-case.md)
  · [fixture/evidence](../cases/k01-stored-comment/README.md). The execution
  evidence is from the repository's disposable training fixture, not a
  third-party product.
- **Second case, E05:** [case brief](../audit/2026-10-24-portfolio-cases/e05-case.md)
  · [acceptance limits](../audit/2026-10-24-e05-context/README.md). It proves
  inert parser marker placement only; it does not prove JavaScript execution,
  a confirmed XSS vulnerability, impact, or general detection accuracy.
- **Short CVE example, BCrypt:** [case brief](../audit/2026-10-24-portfolio-cases/bcrypt-case.md)
  · [current-source disposition](../audit/2026-10-24-a05-source-refresh/README.md).
  This reproduces a known upstream Spring Security CVE in one local path; it is
  not a new application CVE or production-impact demonstration.
- The public toolkit release is `v0.1.0`; E05 changes are in later unreleased
  source. Do not imply the released wheel contains E05.
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
