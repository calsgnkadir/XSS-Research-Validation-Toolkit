# R4 doğrulama ve native uzman turu — 7 Ekim 2026

Başlangıç HEAD: `a979749b09d0eb70a41baafa9d9bb9f88cf8980d`; çalışma ağacı temiz.
Mevcut depo kullanıldı. Önceki masaüstü sohbeti varsayılmadı; güncel kaynak,
ROADMAP, STATUS, VALIDATION ve son audit/staj kaydı okundu. Kullanıcı eski
iş listesinin yeniden uygulanmamasını, kabul testlerinin tekrar çalıştırılmasını
ve ardından R4 corpus/CI işinin sürdürülmesini onayladı. Commit/push yok.

## Bu sohbetin native çağrı kanıtı

Tarih: 7 Ekim 2026 (oturum tarihi; çağrıların saat bilgisi araç sonucunda yok).
Kurulum kontrolü bu geliştirme turunda tekrarlanmadı. Önceki mesajlardaki gerçek
`collaboration.spawn_agent` sonuçları aşağıda kaydedildi. Tümü `fork_turns="none"`;
rol seçimi `agent_type` ile yapıldı, görev adı rol yerine kullanılmadı.

| agent_type | Dönen görev | Sonuç / kapsam |
|---|---|---|
| xss_security_researcher | /root/role_probe_1 | Başarılı; XSS kanıt ayrımı ve analiz yetkisini özetledi |
| scanner_engine_specialist | /root/role_probe_2 | Başarılı; scope/istek/keşif/adapter uzmanlığını özetledi |
| storage_docker_specialist | /root/role_probe_3 | Başarılı; SQLite/callback/Docker risk incelemesini özetledi |
| report_frontend_specialist | /root/role_probe_4 | Başarılı; HTML/mahremiyet/kanıt sunumunu özetledi |
| qa_security_lab_specialist | /root/role_probe_5 | Başarılı; oracle/benchmark/CI durum ayrımını özetledi |

Bu çağrılarda proje okuma/yazma ve araç kullanımı yasaktı; geliştirme veya test
katkısı sayılmazlar. Geçersiz rol kontrolünün tam hatası:
`unknown agent_type 'olmayan_test_agent'`.
İlk `/root/native_role_probe` çağrısı da başarılıydı; gizli talimatın birebir
paylaşımı reddedildiğinden TOML ilk-cümle eşleşmesi doğrulanmadı. Sonraki beş
rolün native çağrı başarısı bundan ayrı kanıttır. Önceki başarısız/eksik
kontroller `../2026-10-06-agent-review/README.md` içinde korunur.

## Yapılandırma ve yetki

Engine ve QA TOML dosyalarında `sandbox_mode="workspace-write"` ve koordinatörün
atadığı dosyalarda onaylı uygulama/test talimatı kullanıldı. Security, Storage
ve Report read-only kaldı; gereksiz yazma yetkisi verilmedi. Model değiştirilmedi.
[Resmî yapılandırma kaynağı](https://learn.chatgpt.com/docs/agent-configuration/subagents)
custom agent TOML içinde sandbox ayarını destekler; runtime üst sınırı ayrıca
geçerlidir. Koordinatör ortamı workspace-write, `.codex` ise korumalı okuma
alanı olarak bildirilmiştir; ayar düzenlemesi apply_patch ile başarılı oldu.
Yeni ayar eski çalışanlara yüklenmiş sayılmaz; yeni görevler yeni native çağrıdır.

## Doğrulama ve çalışma kaydı

İlk `python` komutu PATH'te bulunamadı. `py -3.10` Store Python yolunu buldu
ancak sandbox içinde process başlatma erişim engeli verdi. Aynı kabul komutu
araç üzerinden alınan izinle yeniden başlatıldı; bu çevre hatası test başarısı
veya ürün regresyonu değildir.

## Gerçek geliştirme katkıları ve dosya sahipliği

Yeni görevler de gerçek `agent_type` ve `fork_turns="none"` ile çağrıldı.
Rol modeli değiştirilmedi, generic fallback kullanılmadı.

| Native rol / görev | Dosya sahipliği | Gerçek katkı |
|---|---|---|
| xss_security_researcher / r4_oracle_review | Salt okunur kaynak incelemesi | Bağımsız corpus beklentileri; yutulan frame okuma hatası ve malformed proof riskini buldu; son diff'i inceledi |
| scanner_engine_specialist / r4_corpus_implementation | bench/run.py, dxa_proof_lab.py | Dokuz vaka, kimlik/oracle metadata, callback sayacı, adapter yapısal kontrolleri; dosya yazmaları araçta başarılı |
| qa_security_lab_specialist / r4_qa_ci | test_proof_adapter.py, test_proof_corpus.py, ci.yml | Scanner'dan bağımsız beklentiler, gerçek browser runner/JS-kapalı callback, zorunlu CI/artifact adımları; yazmalar başarılı |
| Koordinatör | dxaprove.py, test_browser_proof.py; yapılandırma ve belgeler | Gözlem-hatası karşı örneğini çalıştırdı ve düzeltti; entegrasyon, gerçek yerel testler ve kanıt kaydı |

Engine ve QA'nın kendi Python denemeleri process erişim engeliyle test başlamadan
durdu; onların test başarısı iddiası yoktur. Koordinatör izinli komutla testleri
çalıştırdı. Başarılı dosya yazmaları gerçek proje yazma yetkisinin kanıtıdır;
bu, TOML'nin eski çalışanlara yeniden yüklendiği veya tüm sandbox ayarlarının
yalnız TOML'den geldiği iddiası değildir. Storage/Report için gereksiz yeni iş açılmadı.

## Yeni kabul sonuçları

1. Değişiklik öncesi scope + R3 + benchmark + adapter: **89 passed, 51.61 s**,
   exit 0, skip yok. Bu yeni koşudur; önceki 339 test sayısı kullanılmadı.
2. Gözlem-hatası karşı örneği, düzeltmeden önce: **1 failed, 21 deselected,
   2.62 s**, exit 1. Playwright frame canary okuması hata vermesine rağmen
   `inconclusive` dönüyordu. Bu, R4'te tamamlanmış negatif sayılabiliyordu.
3. Düzeltme sonrası birleşik kabul: **136 passed, 80.88 s**, exit 0, skip yok.
   [JUnit](acceptance.xml). No-proof ile başarısız/hiç başarılı olmayan okuma
   artık `canary-observation-failed` error üretir; normal negatif olayı üretilmez.
4. Gerçek CLI/Chrome strict corpus: **9 selected / 9 completed, TP=3 FP=0 FN=0**,
   error/timeout/skipped/invalid/inconclusive sayaçları 0; exit 0, toplam wall
   18.58 s. [JSON](corpus-results.json), [Markdown](corpus-results.md).

Koşular örtüşür; test sayıları toplanmaz. Tam depo testi veya uzak Linux CI
koşusu değildir. Scope ve eval düzeltmeleri yeniden yazılmadı.

Komutlar (depo kökü; Windows Store Python başlatımı için araç izni kullanıldı):

```powershell
$env:DXA_REQUIRE_BROWSER='1'
py -3.10 -m pytest tools/dom-xss-analyzer/test_crawl_scope.py tools/dom-xss-analyzer/test_browser_proof.py bench/test_bench.py bench/test_proof_adapter.py -q -p no:cacheprovider --tb=short
py -3.10 -m pytest tools/dom-xss-analyzer/test_browser_proof.py -k failed_canary_reads -q -p no:cacheprovider --tb=short
py -3.10 -m pytest tools/dom-xss-analyzer/test_crawl_scope.py tools/dom-xss-analyzer/test_browser_proof.py bench/test_bench.py bench/test_proof_adapter.py bench/test_proof_corpus.py -q -p no:cacheprovider --tb=short --junitxml=audit/2026-10-07-r4-native/acceptance.xml
$env:BENCH_STRICT='1'
py -3.10 bench/run.py --proof-suite --browser 'C:\Program Files\Google\Chrome\Application\chrome.exe' --no-history --out audit/2026-10-07-r4-native/corpus-results.md
```

## Kapsam ve kalan işler

Corpus `loopback-proof/2`: raw/delayed/eval pozitif; fixed/JSON/dialog/title/
textarea/resource-callback negatif. Etiketler fixture semantiğinden önceden
belirlendi; testte bağımsız sabit harita ve HTTP içerik/state kontrolleri vardır.
Callback negatifi ancak aynı CID'nin yerel HTTP isteği gerçekten görüldüyse
tamamlanır; ayrıca JavaScript kapalı gerçek Chrome kontrolü geçti.
Bu fixture callback servisi veya genel blind journal kabulü değildir.

Zorunlu `r3-proof` CI işi R4 testlerini ve strict CLI'ı çalıştıracak; her durumda
JUnit/JSON/Markdown yükleme adımı var. **Uzak CI çalıştırılmadı**, branch protection
ayarı değiştirilmedi, uzak artifact görülmedi. R4 bütünü tamamlandı sayılmaz.
Sabit gerçek ürün adapter'ı, daha geniş sanitizer/rol/iframe corpus'u ve uzak
Linux kabul kanıtı açık. In-process proof için sert 30 saniye timeout uygulanmış
değildir; 400 ms pencere navigation sonrasında başlar. Konservatif okuma-hatası
kontrolü geçici frame hatalarını da negatif kabul dışında bırakabilir.

Kaynak incelemesi ile runtime kanıtı ayrıldı. Canary execution gözlemi güvenlik
açığı veya yeni CVE triage'ı değildir. Docker/veri/otomatik başlangıç değişikliği,
dış hedef taraması, commit veya push yapılmadı.
