# Ana proje roadmap'i — XSS botu ve staj araştırması

28 Eylül 2026. **Öncelik: bot → rapor ve kanıt → portfolyo → staj → araştırma/CVE.**
Bu belge bütün projenin ana iş listesidir. Aşağıdaki R/C/K/P/S/A kimlikleri görevleri izler;
STATUS yalnız kısa durum özeti, eski ROADMAP-LEGACY ise tarihsel kayıttır.

## Kapsam ve çalışma düzeni

Kaynaklar: ZIP'teki 76 dosyanın denetimi, iki eski sohbet metni ve kullanıcının son öncelikleri.
[Denetim raporu](audit/2026-09-28/DENETIM-RAPORU-TR.md) başlangıç bulgularını,
[dosya–görev eşlemesi](DOSYA-KAPSAM.md) bütün orijinal dosyaların hangi işte takip edildiğini gösterir.
Orijinal ZIP ve denetim kopyası korunur. Mevcut çalışma alanı `xss-bot-work`.
ZIP dışındaki resmî staj PDF'leri önceki kapsam kararı uyarınca dahil değildir.

Sıra, mevcut teknik kapasiteyi düzeltmeye öncelik verir. Her bot düzeltmesinin testi ve kısa
öğrenme kaydı aynı teslimde tutulur; portfolyo vitrini ve CVE avı teknik açığın önüne geçmez.
Yeni dış hedef taraması, hesap açma, disclosure veya yayın bu roadmap oluşturulurken yapılmaz.

| Öncelik | Alan / kimlik | Başlangıç durumu | Alanın kapanışı |
|---|---|---|---|
| 1 | Bot R0–R4, R6, R8–R9 | R0 ilk teslim bitti; R1 devam ediyor | Doğru kanıt, güvenilir oturum, browser entegrasyonu, ölçüm ve kurulabilir sürüm |
| 2 | Rapor C01–C13; kanıt K01–K05 / R5 | 75→50 sayımı düzeldi; kalanlar açık | Her iddia kanıtlı veya kapsamı daraltılmış; yeniden üretim paketi |
| 3 | Portfolyo P01–P04 | Güncel giriş var; düzenleme açık | Üç seçilmiş vaka, dürüst yetenek ve sürüm anlatısı |
| 4 | Staj S01–S03 | Geçmiş teknik yazılar var; devam planı açık | Gerçek çalışmayla bağlantılı öğrenme kayıtları ve sonuç özeti |
| 5 | Araştırma/CVE A01–A05 / R7 | Plan ve doğrulanmamış tarihsel beyanlar | Ürün/sürüm/rol/yenilik/kanal doğrulaması; kanıtlı sonuç durumu |

Durum sözlüğü: **açık** iş yapılacak; **devam** bir kısmı doğrulandı; **tamam** kabul kanıtı var;
**kanıt bekliyor** tarihsel iddia bağımsız doğrulanamıyor; **ertelendi** kapsamdan silinmedi.
Eksik kanıt, geçmiş olayın yaşanmadığının kanıtı değildir. Toplam yüzde kullanılmaz.

## İlk çalışma paketi

1. R1 normal dialog yanlış pozitifi — **tamam**, altı regresyon ve yerel Chrome kaydı var.
2. R1 callback ≠ JS proof; cid eşleşmesi; gizli veri toplamayan beacon — **tamam**: HTTP ve JS kapalı Chrome negatif kontrolü; test kaydı VALIDATION.md.
3. R1 ortak evidence şeması, yansımasız blind deneme kaydı ve sonradan ilişkilendirme — **açık**.
4. R2 JSON/auth/rate ve R8 sanitizer karşı örnekleri — **açık**.
5. R3 uçtan uca browser + R4 güvenilir benchmark; ardından K01/R5 vaka paketi.

İlk iki küçük düzeltme R1'in veya botun tamamlandığı anlamına gelmez.

## Bot: ayrıntılı görevler ve kabul koşulları

### Teknik amaç

Stajda başlayan XSS çalışmasını, bir başkasının da kurup sonuçlarını inceleyebildiği güvenilir bir araştırma aracına dönüştürmek. Ana çıktı; **aday bulgu → bağlam ve oturum doğrulaması → zararsız execution kanıtı → düzeltme → tekrar test** zinciridir. CVE araştırması bu zinciri kullanır; CVE veya ödül almak sürüm kabul ölçütü değildir.

Öncelik: doğruluk ve kanıt, ardından kapsam, sonra hız ve dağıtım. Payload/test/dil sayısındaki artış tek başına başarı ölçüsü değildir. HTTP çekirdek hafif kalır; tarayıcı desteği isteğe bağlıdır.

### Bot teslimleri

| İş | Durum | Bağımlılık | Teslimat |
|---|---|---|---|
| R0 Durumu ve tarihsel iddiaları düzelt | İlk teslim tamamlandı | — | Güncel README, STATUS, roadmap, geçmiş metin değerlendirmesi |
| R1 Kanıt modelini düzelt | Başlandı: bare-visit dialog yanlış pozitifi giderildi | R0 | Ortak bulgu şeması, doğru etiketler, blind takip |
| R2 İstek/oturum güvenilirliği | Açık | R0; R1 şemasıyla uyumlu | JSON, auth, rate, CSRF ve eşzamanlılık düzeltmeleri |
| R3 Tarayıcı doğrulamasını bağla | Açık | R1 + R2 | Auth/stored/DOM tek işlem hattı |
| R4 Doğru benchmark ve CI | Açık | Sayaç düzeltmesi hemen; tam corpus R1–R3 sonrası | Bulgu kimliğiyle TP/FP/FN, gerçek hedef adapter'ı, kalıcı sonuç |
| R5 / K01 Tekrar üretilebilir XSS vaka çalışması | Açık | R3 + R4 | Temiz lab kurulumu, proof, fix, retest, staj yazısı |
| R6 Kullanılabilir ilk sürüm | Açık | R1–R5 | Paketleme, konfigürasyon, JSON/HTML, demo ve sürüm notu |
| R7 / A01–A05 Sınırlı gerçek ürün/CVE araştırması | Hazırlık; otomatik kanıta bağlı değil | Temiz repro ve program kapsamı | Bir ürün/rol için kontrollü araştırma ve dürüst triage kaydı |

R0 tamamlandı demek bütün tarihsel yazılar teknik olarak düzeltildi demek değildir. Eski kayıtlar tarihsel olarak etiketlendi; vaka bazında kanıt düzeltmesi R5'te yapılır. R1'in ilk düzeltmesi de DOM proof veya blind eksiklerinin tamamlandığı anlamına gelmez.

## R0 — Doğru başlangıç kaydı

Kabul ölçütleri:

- [x] Güncel giriş sayfası deneysel özellikleri tamamlanmış ürün gibi sunmaz.
- [x] Tek güncel durum tablosu vardır; eski roadmap ve README tarihsel olarak etiketlidir.
- [x] 75 JSON-only iddiası 50 olarak düzeltilmiştir; raw HTML kanıtı değiştirilmez.
- [x] Yeni CVE, duplicate ve yeniden üretim birbirinden ayrılır.
- [x] Eski mesajdaki Pico/WonderCMS/Klarna önerileri güncel çalışma talimatına dönüşmez.
- [x] Denetim ZIP'i ve denetim kopyası korunur; geliştirme ayrı klasördedir.

## R1 — Bulguyu doğru adlandır

Önce şema tasarımı: `finding_id`, `attempt_id/cid`, kaynak/gönderim, hedef/sink, bağlam, response Content-Type, oturum rolü, evidence seviyesi, triage kararı ve kanıt bağlantıları. Hassas header/cookie değerleri raporlara taşınmaz.

Önerilen evidence seviyeleri: `candidate`, `reflection`, `sink-observed`, `resource-callback`, `execution-confirmed`. Bunlar CVSS veya açıklık etkisi değildir. `execution-confirmed` için tarayıcı bağlamı ve o denemeye ait canary olayı gerekir; ayrıca self-XSS/by-design/yetki sınırı triage'ı yapılır. Marker dizesi veya dialog görülmesi tek başına yeterli değildir.

Kabul ölçütleri:

- [x] Bare `--dom` ziyaretindeki alert/confirm/prompt/beforeunload “proven” olmaz; içerik gözlem olarak korunur.
- [ ] HTML içindeki ham marker, bağlamı gerçekten kırmadan executable'a yükseltilmez.
- [ ] Aynı response normal, flow ve stored modlarında aynı sınıflandırmayı alır; JSON-only JS proof sayılmaz.
- [x] Callback tek başına resource-callback olur; JS kapalı img ile gerçek Chrome kontrolü ve bütün beş payload ailesi için HTTP negatif testleri var. Tam iframe/role fixture kapsamı R3/R4'te açık.
- [ ] Yansıma yokken bile gönderilmiş cid kaydı tutulur; sonradan gelen blind callback ilişkilendirilebilir.
- [ ] Scan bittikten sonra callback uzlaştırma yolu ve süre/oturum bilgisi vardır.
- [ ] HTML ve JSON aynı finding nesnesinden üretilir; hatalar ve atlamalar ayrı görünür.
- [ ] Dedup aynı submit/parametre/sink/bağlam/rolün kopyalarını gruplar, ham kanıtları korur; farklı rol veya sink birleştirilmez.

WonderCMS'teki 58→1 bir sayısal hedef değildir. Gerçek grup sayısı kanıt ve erişim politikasıyla belirlenir. Admin'in tasarlanmış HTML editörü ayrı bir security boundary aşmıyorsa “confirmed vulnerability” olmaz.

## R2 — Gönderim ve oturumu güvenilir yap

- [ ] Canary JSON nesnesine yerleştirilir ve JSON serializer kullanılır; mevcut 950 örneğin hepsi seçilen geçerli şablonda parse edilir, canary round-trip korunur.
- [ ] 401/403 veya eksik token auth başarısı sayılmaz; `Bearer None` kurulmaz. Önceden bulunan cookie tek başına login başarısı değildir.
- [ ] Auth sonrası hedefe özel oturum kontrolü yapılabilir; oturum rolü kaydedilir.
- [ ] 0.5/s gibi fractional rate ilerler; sıfır/negatif için açık doğrulama vardır; test gerçek uzun uyku gerektirmez.
- [ ] Request header'ları görev başına taşınır. Paralel gönderimlerde Content-Type karışmaz.
- [ ] Tek kullanımlık CSRF için refresh+submit ve gerekli stored submit+read işlemleri uygun şekilde sıralanır.
- [ ] Hata, timeout, rate-limit ve engelleme; “bulgu yok” durumundan ayrılır.
- [ ] R1/R2 negatif örnekleri bir sonraki sürümde zorunlu regresyondur.

## R3 — Tarayıcı ile gerçek doğrulama

- [ ] HTTP auth/flow sonucu tarayıcıya açık ve kontrollü biçimde aktarılır; doğru rol doğrulanır.
- [ ] Tek komutla local fixture'da submit→read→canary execution→rapor çalışır.
- [ ] Observer direct eval gibi hedef JavaScript semantiğini değiştirmez; desteklenmeyen hook için kapsam bilgisi verir.
- [ ] Gerçek href davranışı, iframe ve sınırlandırılmış gecikmeli olaylar test edilir; süre aşımı inconclusive olarak görünür.
- [ ] SPA rota adayları kapsam filtresinden geçerek kuyruğa eklenir; duplicate/loop bütçesi vardır.
- [ ] Yakalanan auth/CSRF header'ları gerektiğinde doğru origin/oturumla kullanılır, ham gizli değerler loglanmaz.
- [ ] Browser yolu açık seçilebilir; Windows/Linux kurulum ve başarısızlık açıklaması doğrulanır.

Tek bir hook'a güvenmek yerine kaynak girdisi ve olay arasındaki ilişki kaydedilir. Unrelated application dialog, konsol çıktısı veya random cid benzeri metin proof olamaz.

## R4 — Küçük, doğru ve tekrar üretilebilir ölçüm

Önce aşağıdaki sentetik fixture matrisi, ardından tek gerçek uygulama adapter'ı. 20 yarım hedef yerine kurulumdan rapora çalışan küçük corpus.

| Kontrol | Beklenti |
|---|---|
| JSON'da ham marker | Reflection/JSON-only; XSS değil |
| HTML body ve uygun kırılma bağlamları | Sink ve gerekiyorsa ilişkili execution |
| Title içinde kapanmayan marker | Execution yok |
| Escape edilmiş çıktı | Pozitif XSS yok |
| Normal uygulama alert'i | Observation |
| JS kapalı callback img | Resource-callback |
| Kullanıcıya yansımayan admin sink | Gönderilmiş cid ile sonradan ilişkilendirme |
| 401 ve token yok | Auth error |
| Sanitized(q) + raw q / identity sanitizer | Taint kaybolmaz |
| Farklı kullanıcı/rol/sink | Dedup birleştirmez |
| Gecikmeli/iframe sink | Tanımlı kapsamda yakalanır veya sınır açıkça raporlanır |

Kabul ölçütleri:

- [ ] Bulgu kimliği bazlı eşleme; beklenen 3, bulunan doğru 1 için TP=1/FN=2.
- [ ] Crash/timeout/skipped `ok` veya true negative sayılmaz; kapsama paydası açıklanır.
- [ ] JSON-only ve sadece resource-callback, doğrulanmış XSS TP'sine katılmaz.
- [ ] Bilinen negatif fixture'da FP, zorunlu pozitif fixture'da FN CI'ı düşürür.
- [ ] Gerekli browser işi continue-on-error değildir; skip sayısı doğrulanır.
- [ ] Sabit uygulama sürümü/digest, bootstrap/login ve doğru endpoint'ler vardır; teardown veri etkisi belgelenir.
- [ ] JSON/Markdown sonuçları ve ortam/sürüm/komut bilgileri CI artifact olarak saklanır.
- [ ] Rakip kıyaslaması ancak aynı kapsam, auth, bütçe ve insan triage'ı sağlandığında yayımlanır.

## R5 — Stajın devamı olan güçlü vaka

İlk vaka için mevcut yetkili laboratuvar veya minimal yerel fixture kullanılabilir. Teslimat: hedef sürümü, kaynak→sink izi, iki rol gerekiyorsa hesap A/B kontrolü, tam komut, maskeli request/response, cid ile proof, negatif kontrol, fix diff ve aynı testin fix sonrası sonucu.

- [ ] Temiz ortamdan başka biri tekrar üretebilir.
- [ ] Çalıştırılmayan kısım ve gözlenmeyen davranış açık yazılır.
- [ ] Staj kaydı “amaç, yöntem, bulgu, hata, düzeltme, öğrenilen” akışını izler.
- [ ] En az bir false-positive/false-negative karşı örneği ve çözümü belgelenir.
- [ ] Önceki writeup'lara düzeltme/kanıt bağlantıları eklenir; eski rapor değiştirilmez.

## R6 — Kullanılabilir ilk sürüm

- [ ] Tek kurulum komutu ve opsiyonel browser extra gerçekten paketlenir; sürüm etiketi/CHANGELOG vardır.
- [ ] Config önceliği CLI > config > varsayılan olarak testlidir.
- [ ] JSON şeması sürümlüdür; HTML aynı kanıttan üretilir; rapor test girdisini güvenli escape eder.
- [ ] Belgelenmiş CLI seçenekleri help ile uyumludur; unsupported birleşimler açık hata verir.
- [ ] Demo sonucu temiz ortamda elde edilir; known limitations ve fixture kapsamı görünürdür.

SARIF sonraki küçük teslim olabilir. Plugin API/Marketplace, ihtiyaç gösterilmeden bu sürümü geciktirmez.

## R7 — Gerçek ürün araştırması

Bir ürün ve bir ekosistemle sınırla. Son desteklenen sürüm, rol/yetki sınırı, bilinen advisory'ler ve program kapsamı kontrol edilir. Laboratuvarda çalışan PoC, tek başına yeni CVE veya program kabulü anlamına gelmez. Duplicate/invalid/cannot-reproduce sonuçları da kaydedilir. Eski sohbetten bir şirket adı gelmesi o hedefi tarama talimatı değildir.

Kabul ölçütü CVE sayısı değil: yeniden üretilebilir ve doğru sınıflandırılmış rapor, uygun disclosure kanalı, takip durumu. Gönderim/yayın ayrı yetkilendirme gerektiren dış iletişim işidir.

## Ertelenen işler

Genel subdomain/dizin brute-force motoru, IoT genişlemesi, daha çok mutation sırf sayı için, altı dilde aynı anda AST, plugin pazarı. Statik analiz için önce mevcut sanitizer FN düzeltmesi ve dosya kapsamı; sonra tek dilde AST prototipi. AST kullanmak tek başına sound analiz değildir.

## Her teslimin kapanışı

Kod + yanlış davranışı yakalayan test + ilgili fixture sonucu + kısa sürüm notu + STATUS güncellemesi. Yeşil test sayısı artışı zorunlu hedef değildir; doğru beklenti ve kapsama anlamı esastır. Süre tahmini yerine bir sonraki küçük teslim ve kabul koşulu takip edilir.

## R8 — Statik analiz ve fixture doğruluğu (bot; açık)

Dosyalar: `dxa.py`, `test_dxa.py`, `examples/safe.py`, diğer dil fixture'ları.

- [ ] `sanitize(q) + q` ve identity sanitizer taint'i yok etmez; mevcut hard-clear test oracle'ı düzeltilir.
- [ ] Sanitizer bağlamı ve temizlenen alt ifade değerlendirilir; Markup/SafeString benzeri güven işaretleyicileri encoder sanılmaz.
- [ ] Dosyalar arası isim/kapsam çakışması negatif fixture'ı vardır; regex destek sınırı yazılır.
- [ ] .html/.twig/.jinja/.vue kapsamı gerçekte desteklenen dosyalarla test edilir; JSP'ye gizlenmiş template testi yeterli sayılmaz.
- [ ] C# sink tespiti ile taint desteği ayrı belgelenir; dil desteği tek sayı ile eşitmiş gibi sunulmaz.
- [ ] `safe.py` template kaynağına girdi birleştirmez; template parametresi kullanır; SSTI ve XSS ayrı test beklentileridir.
- [ ] AST sonraki genişlemede tek dil ile başlar; pozitif/negatif etiketli corpus üzerinde ölçülür; temiz projede açık bulma kotası yoktur.

## R9 — Operasyon, kapsam ve tekrar üretim (bot; açık)

Dosyalar: callback servisi, CLI, bench compose dosyaları, README/CI.

- [ ] Callback kayıt erişimi, CORS, istek boyutu, limit doğrulaması, proxy başlığı güveni ve SQLite hata görünürlüğü için yerel/dışa açık çalışma sınırı tanımlanır ve test edilir.
- [ ] Auth/CSRF/cookie/API key konsol ve raporda maskelenir; callback kanıtı gizli veri toplamadan çalışır.
- [ ] Aynı-origin/kapsam ve redirect sınırı belirtilir; desteklenmeyen CLI birleşimleri URL yokken de doğru hata verir.
- [ ] Variant adıyla context kararı, ilk cid/çoklu reflection, yorum/textarea/style bağlamı ve marker kesilmesi için testler vardır.
- [ ] Mutation tekrarları/no-op dönüşümleri raporlanır; URL/entity decode zinciri browser fixture'ıyla ölçülür, sayı doyum kanıtı sayılmaz.
- [ ] Stored auto keşfinde çoklu canary ve seed sınırları ölçülür; elle sağlanan hedef ile otonom keşif ayrılır.
- [ ] Docker readiness daemon ve uygulama seviyesinde ayrılır; bootstrap/login/lesson ve own-hardened adapter'ı olmadan hedef hazır sayılmaz.
- [ ] Compose portları yerel arayüzle sınırlı, sürümler sabit; `down -v` veri etkisi açık ve kontrollüdür.
- [ ] Self-scan beklenen finding exit kodu ile crash'i ayırır; browser skip ve bench FP/error CI tarafından denetlenir.
- [ ] Paket/runtime sürümü, komut, ortam ve kaynak provenance kayıtlıdır; commit/push iddiası yalnız gerçek Git kontrolüyle yapılır.

## Rapor düzeltmeleri — C01–C13

Hepsi **açık**; C11'de sayım ve elle konfigürasyon düzeltmesi **kısmen tamam**.
Başlığa tarihsel uyarı eklemek aşağıdaki teknik düzeltmeleri tamamlamaz.

| Kimlik / dosya | Yapılacak iş | Kabul ölçütü / bağımlılık |
|---|---|---|
| C01 / writeup 01 | Header source, filtre ve execution iddiasını ayır; recursive filtreyi genel çözüm gibi sunma | Kaynak/filtre kanıtı ayrı; execution için K01 veya açık “doğrulanmadı”; savunma K04 ile tutarlı |
| C02 / writeup 02 | postMessage yokluğu, server-trusted veri, Trusted Types createHTML/enforcement ve CSP directive yorumlarını düzelt | İncelenen yol/süre/kapsam yazılı; kanıtsız güvenli/erişilemez hükmü yok; K02 |
| C03 / writeup 03 | Gerçek SQLi demosunu UNION/blind teorisinden ayır; email/admin ve parser varsayımlarını düzelt | Her bölüm deney/teori diye etiketli; sürüm/istek ve sonuç eşleşir |
| C04 / writeup 04 | JWT başarı/başarısızlık, newline hipotezi ve SPKI/PKCS#8 terminolojisi | Gözlem ile neden hipotezi ayrı; kanıt yoksa neden kesin değil |
| C05 / writeup 05 | İki hesap/aynı nesne yetki kontrolü; yatay BOLA ile privilege escalation ayrımı | A/B kontrol çifti ve beklenen/gerçek yanıt veya açık kanıt eksiği; K03 |
| C06 / writeup 06 | Seed/URL yardımı ile otonom keşfi ve tarihsel sürümü ayır | Komut girdileri görünür; desteklenmeyen discovery iddiası yok |
| C07 / writeup 07 | 0 HIGH≠güvenli; sanitizer adı≠fonksiyon analizi; Bludit aidiyetini düzelt | R8 sınırlarıyla uyumlu; login başarı iddiası R2 kanıtına bağlı |
| C08 / writeup 08 | Ham JSON≠HTML injection/XSS; çok URL≠çok açık; Pico/WonderCMS sonuçlarını daralt | İncelenen sink/kapsam belli; by-design ve yetki sınırı triage edilmiş |
| C09 / writeup 09 | 3→1 düşüşünü precision ölçümü sanma; sanitizer FN ve kalan HIGH yorumunu düzelt | R8 karşı örneği ve R4 ölçümü bağlantılı; aday/doğrulanmış ayrımı |
| C10 / writeup 10 | Marker/mutation/execution ayrımı; ineffective/legacy şekilleri etiketle | Gerçek parser pozitif/negatif kontrolü; 950 çalışan exploit iddiası yok |
| C11 / writeup 11 | 50 JSON-only; B sıfır; Bludit etiketi≠proof; yerel patch ve hedef ayarları | Ham rapor sayımı doğru; version+komut+fix diff+browser kanıtı veya sınır; K01/K05 |
| C12 / methodology.md | Kaynak→sink→kanıt yöntemini gerçek uygulama sınırlarıyla düzelt | Network/DOM birbirini dışlayan kategoriler gibi sunulmaz; belirsizlik ve negatif kontrol yazılı |
| C13 / tüm README/indeksler | Güncel durum, sürüm/test sayısı, linkler ve eski DONE blokları | Her güncel iddia STATUS/VALIDATION'a bağlı; tarihsel beyan güncel başarı olarak görünmez; P01 |

## Kanıt ve savunma — K01–K05 (açık)

| Kimlik | Dosyalar / iş | Kabul ölçütü |
|---|---|---|
| K01 / R5 | XSS vaka paketi; writeup 01/10/11, reports, araştırma labı | Sabit sürüm, temiz kurulum, tam komut, masked request/response, cid-browser proof, negatif kontrol, fix diff, retest; proof yoksa aday |
| K02 | screenshots 01–08 + report-preview.png ve indeks | Her görselin source/filtre/challenge/proof seviyesi yazılı; eksik CSP/dialog kanıtı açık; token/cookie/hash maskeli yayın kopyası; orijinal arşiv korunur |
| K03 | SQLi/JWT/BOLA vakalarının kanıt envanteri | Anlatılan her sonucun kanıt bağlantısı veya “mevcut değil” durumu; iki kullanıcı kontrolü gerektiğinde ayrı kayıt; teori deney sayılmaz |
| K04 | defense/README.md, methodology, writeup savunmaları | Bağlama uygun encoding ve sanitizer; CSP ek savunma; HttpOnly XSS/authenticated action önlemez; recursive filtre genellemesi yok; teknik kaynaklar düzeltme sırasında doğrulanır |
| K05 | reports/*.html, dinamik HTML/JSON üretici, preview'lar | 50 JSON-only + 2 Bludit kayıt + 78 statik aday doğru etiketli; No findings satırı sayılmaz; varyant/evidence/rol/kök neden görünür; raw eski raporlar değişmez |

## Portfolyo — P01–P04 (açık; giriş sayfası ilk düzenlemesi yapıldı)

| Kimlik | İş | Kabul ölçütü |
|---|---|---|
| P01 | README/writeup indeksini üç seçilmiş vaka etrafında düzenle | XSS proof→fix, ölçülmüş bot hatası→regresyon, authz/araştırma vakası; birincil/ikincil bağlantılar anlaşılır; C/K kapanışlarına bağlı |
| P02 | 06–10'u araç geliştirme serisi olarak grupla, tekrarları azalt | Tarihsel içerik korunur; aynı başarı beş ayrı başarı gibi sunulmaz; gereksiz dosya silinmez |
| P03 | CV/proje tanımını gerçek yetenekle sınırla | 950 exploit/tam otomatik proof/rakip üstünlüğü/yeni CVE iddiası kanıtsız yok; deneysel destek ve rol açık |
| P04 | Paylaşılabilir demo ve ilk sürüm paketi | Başka biri kurulumu ve vakayı tekrarlar; release note + limitations + kanıt linki var; R6/K01/K05; yayın/push otomatik varsayılmaz |

## Stajın devamı — S01–S03 (açık)

| Kimlik | İş | Kabul ölçütü |
|---|---|---|
| S01 — başlandı | Geliştirme oturumu öğrenme kayıtları | Gerçek tarih, amaç, yapılan işlem, test kanıtı, hata, çözüm, öğrenilen ve kalan iş; çalışma saati/başarı uydurulmaz |
| S02 | Mevcut 11 yazıyı beceri ve kanıt matrisiyle ilişkilendir | XSS/SQLi/JWT/BOLA, debugging, test, raporlama becerileri kanıtlı; teori/deney/araç geliştirme ayrı; C/K'ya bağlı |
| S03 | Teknik devam özeti ve teslim kontrolü | Önce/sonra yetenek, ölçülen fark, sınırlamalar ve sonraki adım; resmi okul formatı/onay şartı biliniyormuş gibi doldurulmaz; dış staj PDF'leri kapsam dışı |

## Araştırma ve CVE — A01–A05 (açık / tarihsel kanıt bekliyor)

| Kimlik | İş / dosya | Kabul ölçütü |
|---|---|---|
| A01 | research/README.md duplicate ve SQLi beyanları | Ürün+sürüm+tarih+kayıt/advisory+maskeli triage varsa bağla; yoksa yazar beyanı olarak tut; yeni kredi ile karıştırma |
| A02 | Bludit CVE-2026-4420 eşlemesi | Resmî test edilen sürüm/kredi, yerel 3.16.2 gözlemi ve kök neden ayrı; vendor fix ile yerel fix karıştırılmaz; kaynak işlem anında doğrulanır |
| A03 | Sprint planı ve disclosure kanalı | non-WP hedefe genel Patchstack kabulü varsayımı kaldırılır; scope/rol/güncel sürüm/program kuralları doğrulanır; 90 gün evrensel kural değildir |
| A04 | Tek gerçek ürün araştırması / R7 | Yetkili lokal temiz kurulum, kaynak→sink, role/boundary, bilinen kayıt kontrolü, bağımsız PoC; admin-only/by-design otomatik bug veya otomatik risksiz sayılmaz |
| A05 | Sonuç ve takip kaydı | submitted/valid/duplicate/invalid/cannot-reproduce ayrı ve kanıtlı; boş sprint results.md tamamlanmış iş sayılmaz; dış gönderim/yayın açık yetkiyle |

Eski Klarna hedef önerisi güncel scope veya test yetkisi sayılmaz. Yeni araştırma ürünü bu roadmap'te peşinen seçilmedi.

## Ertelenen ama kaybolmayan işler

- E01 Tek dil AST pilotu: R8'in ölçümü sonrası; diğer dillere yalnız kapsam kanıtıyla genişleme.
- E02 SARIF: R6'nın ortak kanıt şeması sonrası; schema validation ve doğru seviye eşlemesi.
- E03 Genel subdomain/dizin recon ve IoT: mevcut XSS ürün hedefi için düşük öncelik.
- E04 Plugin API/Marketplace ve topluluk kampanyası: kullanıcı ihtiyacı ve tekrarlanabilir sürüm sonrası.
- E05 Yeni payload/mutation: yeni ölçülmüş bağlam kapsaması varsa; sayı kotası veya 18'in matematiksel doyum iddiası yok.

## Denetimden kapanışa izlenebilirlik

Ana denetim §3 aşamalar → R0–R9; §4 kod kusurları → R1–R4/R8/R9;
§5 CVE → A01–A05; §6 yazılar → C01–C13 ve K01–K05;
§7 portfolyo → P01–P04; §8 kapanış sırası → bu ana öncelik sırası.
76 dosyanın tek tek görev eşlemesi DOSYA-KAPSAM.md içindedir; bulgusuz/destekleyici dosyalara gereksiz düzeltme zorlanmaz.

Kapanan her görev: değişen dosya + kabul testi/kanıt + tarih + CHANGELOG kaydı.
Uyarı etiketi eklemek, yalnız test sayısı artırmak veya bir helper yazmak tamamlanma değildir.
