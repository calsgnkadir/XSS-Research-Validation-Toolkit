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

## Yerel başlangıç

Depo kökünde:

```console
python tools/dom-xss-analyzer/dxa.py --help
python tools/dom-xss-analyzer/dxadyn.py --help
python -m pytest -q
```

Pytest kurulu değilse test ortamına ayrıca kurulmalıdır. `--dom` şu an bir
URL ziyaretini gözlemler; stored/auth-flow ile birleşik doğrulama değildir.
`dxadyn` ana modlarından `--dom`, `--stored` ve `--flow` birlikte seçilemez.
Stored/flow hedefini kendi seçeneklerinden alır; yanına positional URL verilmez.
`--dom` HTTP oturum seçeneklerini (`--login`, `--auth-flow`, `--auth-check`,
`--cookie`, `--header`, `--csrf-refresh`, `--csrf-header`) kabul etmez.
Bu desteklenmeyen birleşimler ağ/browser işlemi ve rapor yazımı başlamadan
exit 2 verir. Oturumlu browser proof için `dxaprove` kullanılır.
R6 araştırma paketi taslağı depo kökünden bir sanal ortamda kurulabilir:

    python -m pip install .
    python -m pip install ".[browser]"
    python -m playwright install chromium
    dxa --help
    dxadyn --help
    dxaprove --help

Browser extra Playwright 1.63.0 kurar; browser binary ayrı kurulur veya yerel
Chrome yolu açıkça verilir. Paket adı dxa-research-toolkit, geliştirici sürümü
0.0.0.dev0 yalnız test amaçlıdır. PyPI yayını, Git release etiketi ve R6 genel
kabulü yapılmadı. Eski doğrudan Python komutları çalışmayı sürdürür.
Tarama örneklerini kendi yerel fixture'ların veya açıkça yetkili hedeflerin üzerinde çalıştır.

Kurulumdan sonra paketlenmiş loopback demo şu şekilde çalıştırılabilir:

    dxaprove --demo --browser "<chrome-yolu>" --output <yeni-kanit-dizini>

Demo kendi disposable loopback fixture'ını açıp kapatır. `execution-observed`
yalnızca fixture'daki canary gözlemidir; vulnerability triage sonucu değildir.
Başka bir izinli loopback lab için `dxaprove --spec <yerel-json>` kullanılır;
bu proof sözleşmesi `dxa` ve `dxadyn` tarama config'lerinden ayrıdır.

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
