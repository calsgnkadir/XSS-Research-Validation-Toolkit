# XSS Research Lab & Bot

An experimental Python CLI toolkit for XSS research and evidence collection.
Project work combines static source/sink candidate analysis, bounded HTTP
reflection checks, and browser observations in controlled labs. Reports keep
those observations separate from CID-matched JavaScript execution and from
vulnerability triage. The project is a research-support prototype, not a
general-purpose autonomous scanner.

**Project summary:** The work focuses on implementing and validating a
repeatable analysis workflow: inspect candidate source/sink paths, observe
bounded HTTP/browser behavior, preserve evidence boundaries, and test fixes in
local fixtures. The retained acceptance includes controlled corpus and
loopback-fixture checks; it does not establish broad real-world detection
accuracy, independent product findings, competitor superiority, or newly
discovered CVEs. Install the package with:

```console
python -m pip install dxa-research-toolkit
```

The accepted `0.1.0` wheel remains available through the historical
[GitHub Release](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/releases/tag/v0.1.0).
Current tag and artifact status is recorded in [STATUS](STATUS.md). Use the
tools only on systems you own or are explicitly authorized to test.

## Current status

This is an experimental research toolkit, not a general-purpose vulnerability
scanner. The `v0.1.0` GitHub Release remains available as a historical release;
this source checkout includes later changes. Bounded acceptance
for R0–R6, the Python AST pilot (R8), and the declared operational scope (R9)
is complete. E05's measured textarea parser-context extension is accepted
within its narrow scope. A04 is bounded complete for the selected local GET
routes. A05's selected advisory dispositions have now been rebound to current
Kadrom source `eb031a1`; the regenerated 248-coordinate dependency tree matches
the prior query hash, with no new applicable candidate among the reviewed leads.
A05 remains partial: one malformed multipart cleanup fixture passed, while
deployment-wide and broader runtime conditions remain open. The local authorized
Kadrom checkout exists, but no current-source app deployment or active proxy/WAF
was available for those checks. A fresh isolated runtime attempt built the
current JAR, but host-to-MySQL connectivity failed before the app bound its
health port; no health/auth requests were sent. R7's bounded local research is complete; this
does not establish vulnerability absence. See the [A05 runtime attempt](audit/2026-10-24-a05-isolated-runtime/README.md).
Current handoff, open work and evidence limits are in [STATUS](STATUS.md), the
[roadmap](ROADMAP.md), and the [validation log](VALIDATION.md).
The current feature-freeze decision, CVE-source roles, and evidence-based CV
wording are in the [CVE and portfolio review](audit/2026-10-24-cve-portfolio-review/README.md).

On 24 October, an independent K03 replay completed 17 requests against the
existing local Juice Shop 20.2.0 image in an internal-only lab; it reproduced
the documented SQLi-shaped login, unsigned JWT, and synthetic cross-account
basket behaviors. This is a new training-lab replay, not validation of the old
sessions or a CVE finding. K04 source review found that the pinned image's
current login-IP sanitizer path does not match the historical regex
reassembly claim, so no faithful K04 runtime retest was run. See the separate
[K03](audit/2026-10-24-k03-independent-retest/README.md) and
[K04](audit/2026-10-24-k04-independent-retest/README.md) records.
Three evidence-based case drafts for K01, E05, and the known BCrypt issue are in
the [portfolio preparation audit](audit/2026-10-24-portfolio-cases/README.md).
The concise [CV draft](docs/PORTFOLIO-CV-DRAFT.md) is separate from the
supporting evidence. K04's local artifact search found no matching historical
Juice Shop source/image; its retest remains blocked on that artifact.
The follow-up found no faithful local K04 image for a runtime retest and no
currently running current-source Kadrom deployment for broad A05 checks; see
[K04 testability](audit/2026-10-24-k04-retest-followup/README.md) and
[K04 local artifact search](audit/2026-10-24-k04-artifact-search-retest/README.md),
and [A05 environment readiness](audit/2026-10-24-a05-authorized-environment/README.md).

The A05/E05 evidence delivery is `e56ae60` on `main`; local HEAD matched
`origin/main` when checked. Its
[hosted CI](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/40086961102)
analyzer, required authenticated-browser and optional dxadom-browser jobs
completed successfully; [K01 Linux CI](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/40086961111)
also succeeded. These are hosted job results; artifacts were not downloaded
for independent review. The latest local E05 selected acceptance passed
**381 tests with zero skips** and its installed CLI gate passed **9 controls**;
the A05 parser fixture passed **1 test**. These bounded checks are not broad
detection-accuracy or vulnerability-discovery measurements. See the respective
[E05 evidence](audit/2026-10-24-e05-context/README.md) and
[A05 evidence](audit/2026-10-24-a05-multipart-cleanup/README.md).

## Selected evidence-backed cases

- **Stored XSS proof → fix → retest:** [K01 local fixture](cases/k01-stored-comment/README.md)
  records one CID-matched browser execution, four negative controls, HTML text
  encoding, and retest. It is a training fixture, not a product/CVE claim.
- **Tooling failure → regression:** [R9 browser-fixture follow-up](audit/2026-10-16-r6-r9-final-source/README.md)
  records serial fixture failures, the threaded-server correction, and the
  full local Chrome DOM suite. This measures fixture reliability, not scanner
  accuracy.
- **Controlled research replay:** [R4 exact-payload replay](audit/r4-proof-experiment-2026-10-16/README.md)
  checks stored scanner candidates in separate writer/reader-admin loopback
  fixtures with escaped controls. Some outcomes remain inconclusive; it is not
  a fresh scanner comparison or a vulnerability ranking.

[Install and run the local demos](docs/PORTFOLIO-DEMO.md).

Stored/stored-auto blind denemeleri artık yansıma olmasa da kalıcı kaydedilir;
tarama sonrası callback kontrolü ve JSON/HTML kayıt raporu vardır.
[Kullanım ve kapsam](tools/dom-xss-analyzer/BLIND-JOURNAL.md). Callback, JS proof değildir.

HTTP modları ortak bulgu üreticisi kullanır: ham marker ve JSON yanıtı execution
sayılmaz. `--json-out` ve `--html` aynı finding'leri raporlar.
[Kanıt modeli ve uyumluluk değişiklikleri](tools/dom-xss-analyzer/HTTP-EVIDENCE.md).

Source checkouts also provide offline [SARIF 2.1.0 export](tools/dom-xss-analyzer/SARIF.md):
`dxa-sarif evidence.json --output evidence.sarif`. Results preserve observation
and triage categories as review records, without vulnerability severity or
execution claims. This addition is unreleased; the existing release asset is unchanged.

**R1 kabul kapsamı tamamlandı:** resmî kanıt sözleşmesi, statik/HTTP/DOM/journal
ortak raporları, hata/atlama olayları ve rol/sink ayrımını koruyan dedup.
[Madde bazında kapanış](audit/2026-10-05-r1/R1-KAPANIS.md).
R2 HTTP kabulü tamam: [oturum kontrolü, rate ve CSRF sözleşmesi](tools/dom-xss-analyzer/SESSION-CONTRACT.md).
R3 loopback browser proof, observer direct eval, SPA route bütçesi ve allowlist header aktarımı kabul edildi; WebSocket/genel ağ sandboxı kapsam dışı.
[R3 demo ve kapsam](tools/dom-xss-analyzer/BROWSER-PROOF.md).

**İlk güncel vaka:** [K01 stored yorum — execution → fix → retest](cases/k01-stored-comment/README.md).
Yerel fixture'da ayrı okuyucu tarayıcısıyla 5/5 kontrol geçti; aynı payload output
encoding sonrası düz metin kaldı. Bu vaka kanıtıdır; genel bot execution motoru değildir.

[Denetim raporu](audit/2026-09-28/DENETIM-RAPORU-TR.md) ve
[dosya bazında inceleme](audit/2026-09-28/DOSYA-INCELEMESI-TR.md) depoda bulunur.

- [Güncel durum ve sınırlar](STATUS.md)
- [Ana proje roadmap'i: bot, rapor/kanıt, portfolyo, staj, araştırma/CVE](ROADMAP.md)
- [76 dosyanın görev eşlemesi](DOSYA-KAPSAM.md)
- [Test ve doğrulama kaydı](VALIDATION.md)
- [Değişiklik kaydı](CHANGELOG.md)
- [Eski mesajın değerlendirmesi](HISTORY-NOTES.md)

## Araçlar

| Bileşen | İşlev | Sınır |
|---|---|---|
| `dxa.py` | Static source/sink candidates, with a bounded Python AST pilot | Language coverage differs; this is not general sound data-flow analysis |
| `dxadyn.py` | HTTP reflection, stored checks, and bounded same-origin discovery | Findings are candidates/reflections; they do not alone establish XSS |
| `dxadom.py` | Playwright page, sink, dialog, route, and header observations | Bounded loopback adapter; observation is distinct from CID-matched execution |
| `dxa_callback.py` | Local callback collection and lookup | A matched callback is `resource-callback`, not JavaScript execution |
| `dxa2dyn.py` | Parameter hints from static candidates | A hint is not a complete source-to-sink proof |

Payload corpus metadata includes 50 base variants and 18 mutation definitions.
The historical generator count of 950 payload strings (895 after removing
CID-specific uniqueness) describes generated test inputs only; it is not a
count of working exploits, successful executions, WAF bypasses, or findings.
HTTP/statik çekirdek stdlib kullanır; testler pytest, tarayıcı gözlemcisi Playwright ve uygun browser gerektirir.

## Yerel kurulum ve smoke kontrolü

Python 3.10 veya üstü gerekir. Depo kökünde temel CLI'ları sanal ortama kurup
yardım ekranlarını kontrol et:

```console
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install .
dxa --help
dxadyn --help
dxaprove --help
```

macOS/Linux:

```console
source .venv/bin/activate
python -m pip install .
dxa --help
dxadyn --help
dxaprove --help
```

Temel kurulumun zorunlu çalışma zamanı bağımlılığı yoktur. Browser proof demo'su
için aynı ortamda isteğe bağlı, `playwright==1.63.0` sürümüne sabitlenmiş
browser extra'yı kur ve Chromium binary'sini ayrıca yükle:

```console
python -m pip install ".[browser]"
python -m playwright install chromium
dxaprove --demo --output demo-evidence
```

Demo kendi geçici loopback fixture'ını açıp kapatır. Yeni bir çıktı klasörü
kullan. `execution-observed` yalnız bu fixture'daki canary gözlemidir; açıklık
triage'ı veya genel tarayıcı doğruluğu değildir. İzinli başka bir loopback lab
için `dxaprove --spec <yerel-json>` kullanılabilir; bu proof sözleşmesi `dxa`
ve `dxadyn` tarama config'lerinden ayrıdır. Tarama komutlarını yalnız kendi
yerel fixture'larında veya açıkça yetkili hedeflerde çalıştır.

Depo metadata'sında ilk araştırma sürümü `dxa-research-toolkit 0.1.0` olarak
seçilmiştir. Bu checkout sürüm ve release notlarını hazırlar; PyPI yayını veya
Git release etiketi yapıldığı anlamına gelmez. Ürün deneysel bir araştırma
yardımcısıdır; kapsam ve kanıt sınırları için aşağıdaki notları ve ilgili audit
kayıtlarını inceleyin. CLI'ları kaynak dosyalarından doğrudan çalıştırmak da
mümkündür.

`dxadyn` için `--dom`, `--stored` ve `--flow` ana modları birlikte seçilemez.
Stored/flow hedefi kendi seçeneklerinden verilir; positional URL eklenmez.
`--dom` HTTP oturum seçeneklerini (`--login`, `--auth-flow`, `--auth-check`,
`--cookie`, `--header`, `--csrf-refresh`, `--csrf-header`) kabul etmez.
Desteklenmeyen birleşimler ağ/browser işlemi ve rapor yazımı başlamadan exit 2
verir. Oturumlu browser proof için `dxaprove` kullanılır.

Statik `dxa` CLI için isteğe bağlı JSON config örneği:

```json
{"schema_version": 1, "min_confidence": "medium"}
```

`dxa <yerel-kaynak> --config scan.json` komutunda öncelik
`--min-confidence` > config > varsayılan `low` şeklindedir. Bu dar config
sözleşmesi yalnız statik CLI için geçerlidir; dosyaya oturum bilgisi koymayın.

Dynamic `dxadyn` has a separate, limited HTTP tuning config:

```json
{"schema_version": 1, "depth": 1, "parallel": 1, "rate": 0}
```

For an authorized local target, `dxadyn <local-url> --config http.json --depth 0`
uses explicit CLI values before config, then defaults (`depth=0`, `parallel=1`,
`rate=0`, unlimited). Depth applies to reflected mode, parallel to reflected/stored,
and rate to HTTP modes. DOM rejects HTTP tuning. Worker count does not promise
parallel HTTP throughput; shared-session HTTP transactions remain serialized.

UTF-8 BOM is supported. Unknown/duplicate fields, invalid types/version, negative
depth/rate, parallel below one, nonfinite rate and irrelevant mode settings return
exit 2 before target/session/browser I/O. CLI overrides cannot hide invalid config.
Targets, credentials and output paths are not config fields. `dxaprove --spec`
retains its separate proof contract.
[Config scope and validation](audit/2026-10-15-r6-config-release/README.md).

## Staj ve araştırma kayıtları

- [11 tarihsel teknik yazı](writeups/README.md): XSS, SQLi, JWT, BOLA ve araç geliştirme.
- [Ham v3.10 raporları](reports/2026-09-26-v310-live/README.md): 50 JSON-only,
  iki Bludit dinamik kayıt ve 78 statik MEDIUM aday; bağımsız açık toplamı değil.
- [Görseller](screenshots/README.md): çalışma ve bazı challenge/source/filtre adımlarının kanıtı;
  tüm anlatılan execution sonuçlarının bağımsız ispatı değil.
- [Araştırma kayıtları](research/README.md): tarihsel duplicate/yeniden üretim beyanları;
  kabul kayıtları ve yeni CVE kredisi bu ZIP'ten bağımsız doğrulanamıyor.

Güncel bir vaka için sürüm, komut, maskeli request/response, canary proof,
negatif kontrol ve fix sonrası retest birlikte yayımlanacak. Geçmiş iddiaların
kanıt seviyesi STATUS ve roadmap tarafından sınırlandırılır.

## Öncelik

Doğru kanıt modeli → güvenilir oturum/istek → tarayıcı entegrasyonu → doğru
benchmark → tekrar üretilebilir XSS vakası → kullanılabilir sürüm.
Genel recon, çok dilli AST ve plugin ekosistemi bu zincirin önüne geçmez.

[MIT lisansı](LICENSE). [Eski README](README-LEGACY.md) yalnız tarihsel kayıttır.
