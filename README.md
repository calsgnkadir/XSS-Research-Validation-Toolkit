# XSS Research Lab & Bot

This is a research prototype for finding and validating possible cross-site scripting (XSS) issues.
It combines source-code review, HTTP reflection checks, and browser observations in controlled labs.
Reports keep observations and evidence separate from confirmed JavaScript execution.
Use it only on systems you own or are explicitly authorized to test.
The project includes repeatable test cases and fix-and-retest examples.
It does not claim broad detection accuracy or confirmed new vulnerability discoveries.

Stajda başlayan web güvenliği çalışmalarının devamı: kaynak→sink incelemesi,
Python ile XSS aday tespiti ve tekrar üretilebilir laboratuvar doğrulaması.
Amaç, sonuçlarını kanıtla açıklayan ve başka bir araştırmacının da çalıştırabildiği bir araç geliştirmek.

**Güncel durum:** araştırma prototipi. Statik ve HTTP analizleri çalışıyor;
Playwright ve blind callback parçaları deneysel. Otomatik sınıflandırmaların
tamamı doğrulanmış XSS anlamına gelmez. Yeni CVE kredisi bu arşivden doğrulanmış değildir.

**Doğrulama — 6 Ekim 2026:** 544 test geçti, 36 browser testi otomatik
Chrome keşfi nedeniyle atlandı. Bu sayı tüm XSS sınıflarının doğrulandığı
anlamına gelmez. Normal dialog ve JavaScript kapalı callback karşı örnekleri
mevcut Chrome ile ayrıca kontrol edildi. [Test sonuçları ve kanıtlar](VALIDATION.md).

Stored/stored-auto blind denemeleri artık yansıma olmasa da kalıcı kaydedilir;
tarama sonrası callback kontrolü ve JSON/HTML kayıt raporu vardır.
[Kullanım ve kapsam](tools/dom-xss-analyzer/BLIND-JOURNAL.md). Callback, JS proof değildir.

HTTP modları ortak bulgu üreticisi kullanır: ham marker ve JSON yanıtı execution
sayılmaz. `--json-out` ve `--html` aynı finding'leri raporlar.
[Kanıt modeli ve uyumluluk değişiklikleri](tools/dom-xss-analyzer/HTTP-EVIDENCE.md).

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
| dxa.py | JS/TS, C#, PHP, Java ve Python için regex kaynak/sink adayları | Destek diller arasında eşit değil; AST/sound data-flow değil |
| dxadyn.py | HTTP reflection/stored, form/JSON/header, auth/flow ve HTML rapor | JSON gönderimi düzeltildi; auth, flow sınıflandırması ve severity sorunları açık |
| dxadom.py | Playwright ile sayfa/sink/dialog/route/header gözlemi | Gözlem≠canary ile ilişkili execution proof |
| dxa_callback.py | Yerel callback kayıt ve sorgulama | Eşleşen istek resource-callback; JavaScript proof değil |
| dxa2dyn.py | Statik adaydan dinamik parametre önerisi | Tam otomatik kaynak→sink ispatı değil |

50 temel varyant ve 18 mutation, 950 üretim oluşturur; cid çıkarılınca
895 benzersiz dize vardır. Bu sayılar çalışan exploit veya WAF bypass sayısı değildir.
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
