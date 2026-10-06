# Ana proje roadmap'i — XSS botu ve staj araştırması

6 Ekim 2026 güncellemesi. **Öncelik: bot → rapor ve kanıt → portfolyo → staj → araştırma/CVE.**
Bu belge bütün projenin ana iş listesidir. Aşağıdaki R/C/K/P/S/A kimlikleri görevleri izler;
STATUS yalnız kısa durum özeti, eski ROADMAP-LEGACY ise tarihsel kayıttır.

## Kapsam ve çalışma düzeni

Kaynaklar: ZIP'teki 76 dosyanın denetimi, iki eski sohbet metni ve kullanıcının son öncelikleri.
[Denetim raporu](audit/2026-09-28/DENETIM-RAPORU-TR.md) başlangıç bulgularını,
[dosya–görev eşlemesi](DOSYA-KAPSAM.md) bütün orijinal dosyaların hangi işte takip edildiğini gösterir.
Orijinal ZIP ve denetim kopyası korunur. Güncel Git çalışma alanı `xss-github`;
önceki `xss-bot-work` kopyası geliştirme kaynağı değildir.
ZIP dışındaki resmî staj PDF'leri önceki kapsam kararı uyarınca dahil değildir.

Sıra, mevcut teknik kapasiteyi düzeltmeye öncelik verir. Her bot düzeltmesinin testi ve kısa
öğrenme kaydı aynı teslimde tutulur; portfolyo vitrini ve CVE avı teknik açığın önüne geçmez.
Yeni dış hedef taraması, hesap açma, disclosure veya yayın bu roadmap oluşturulurken yapılmaz.

| Öncelik | Alan / kimlik | Başlangıç durumu | Alanın kapanışı |
|---|---|---|---|
| 1 | Bot R0–R4, R6, R8–R9 | R0 ilk teslim, R1 ve R2 kabul kapsamı tamam; sırada R3 | Doğru kanıt, güvenilir oturum, browser entegrasyonu, ölçüm ve kurulabilir sürüm |
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
3. R1 yansımasız blind takip — **stored/stored-auto için tamam**; ortak şema, DOM/statik/HTTP/journal raporları ve konservatif dedup — **tamam**. [Kapanış kanıtı](audit/2026-10-05-r1/R1-KAPANIS.md).
4. R2 JSON/auth/rate/CSRF HTTP kabulü — **tamam**. R8 sanitizer karşı örnekleri — **açık**.
5. R1 sonrası **K01-min**: tek yerel XSS vakası, manuel/browser canary kanıtı, negatif kontrol, fix ve retest. Tam R5/R6 kapanışı sayılmaz. R2→R3→R4 bot hattı devam eder.

R1'in aşağıdaki kabul kapsamı tamamlandı; botun tamamlandığı anlamına gelmez.
HTTP normal/flow/stored/header bulguları ortak üreticiye taşındı; JSON-only ve
ham marker'ın execution diye raporlanması giderildi. JSON/HTML aynı finding'leri
kullanıyor. [5 Ekim model ve sınırları](tools/dom-xss-analyzer/HTTP-EVIDENCE.md).
Sıradaki bot işi R3 gerçek canary execution ve browser oturum entegrasyonu.
Rapor C01–C13, kanıt K01–K05, portfolyo P01–P04, staj S01–S03 ve araştırma
A01–A05 kapsamdan çıkarılmadı; aşağıdaki kabul koşulları geçerlidir.

### Son kanıt ve teslim sırası

| İş | Son kabul kanıtı | Durum / sonraki kapı |
|---|---|---|
| R1 | 2026-10-05, [kapanış matrisi](audit/2026-10-05-r1/R1-KAPANIS.md) | Tamam; 479 passed, 36 skipped |
| R2 | 2026-10-06, [kapanış matrisi](audit/2026-10-06-r2/R2-KAPANIS.md) | HTTP kabul kapsamı tamam; browser oturum aktarımı R3'te |
| K01-min | 2026-10-05, [vaka ve 5/5 browser kontrolü](cases/k01-stored-comment/README.md) | Tamam; tam R5 bağımsız temiz ortam doğrulaması bekliyor |
| R3–R4 | Yeni kapanış kanıtı yok; 2026-09-28 audit baseline | Açık; browser zinciri ve ölçüm doğruluğu |
| C/P/S | 2026-10-05 S01 ve rapor altyapısı; vaka düzeltmeleri açık | Önce C01→C11→C05, sonra üç seçilmiş P01 vaka |
| A01–A05 | Yeni dış triage/CVE kanıtı yok | Kanıt bekliyor / plan; scope ve kaynak doğrulaması gerekli |

Kanıt tarihi belgeye son dokunulma tarihi değildir. Kabul kanıtı eklenmeyen iş
yalnız düzenleme yapıldığı için güncellenmiş sayılmaz. Her teslimde bu tabloya
bakılır; iki teslim boyunca ilerlemeyen aktif iş küçültülür veya gerekçesi yazılır.

İlk kaba efor varsayımı (taahhüt veya geçmiş çalışma saati değil): K01-min 1–2,
R2 auth/token 1–2, rate/CSRF 2–3 odaklı oturum. Bir oturum için 2–3 saat varsayılır;
ilk karşı örnekte tahmin yenilenir. R3/R4 ve kalan C/K işleri henüz parçalanmadığı
için toplam bitiş tarihi verilmez. Kullanıcı kapasitesi bilinmeden takvim üretilmez.

C önceliği: C01 XSS proof/fix, C11 araç doğruluğu, C05 iki hesaplı BOLA kanıtı.
C10 yalnız K01'i destekleyen payload/kanıt bölümleriyle aynı pakete alınır.
C02–C04 ve C06–C09 sonraki düzenleme sırasındadır; silinmez ve tamamlanmış sayılmaz.
C12/C13 ilgili teslimin yöntem/indeks tutarlılığıyla birlikte güncellenir.

Hedef yeniden üretici Python/Git bilen bağımsız teknik değerlendiricidir.
Recruiter için kısa vaka özeti, mentor/teknik okuyucu için komut ve kanıt paketi
aynı vakaya bağlanır. Operasyonel yetki kaynağı: yerel fixture için kullanıcının
proje talebi; dış hedef için açık hedef/scope yetkisi ayrıca doğrulanır. Dış
disclosure/mesaj/yayın için kullanıcının gönderim talimatı gerekir; bir agent
yorumu veya eski hedef önerisi bunun yerine geçmez. Mevcut GitHub push yetkisi sürer.

[Agent yorumunun ayrıntılı değerlendirmesi](audit/2026-10-05-r1/AGENT-YORUMU.md).

## Bot: ayrıntılı görevler ve kabul koşulları

### Teknik amaç

Stajda başlayan XSS çalışmasını, bir başkasının da kurup sonuçlarını inceleyebildiği güvenilir bir araştırma aracına dönüştürmek. Ana çıktı; **aday bulgu → bağlam ve oturum doğrulaması → zararsız execution kanıtı → düzeltme → tekrar test** zinciridir. CVE araştırması bu zinciri kullanır; CVE veya ödül almak sürüm kabul ölçütü değildir.

Öncelik: doğruluk ve kanıt, ardından kapsam, sonra hız ve dağıtım. Payload/test/dil sayısındaki artış tek başına başarı ölçüsü değildir. HTTP çekirdek hafif kalır; tarayıcı desteği isteğe bağlıdır.

### Bot teslimleri

| İş | Durum | Bağımlılık | Teslimat |
|---|---|---|---|
| R0 Durumu ve tarihsel iddiaları düzelt | İlk teslim tamamlandı | — | Güncel README, STATUS, roadmap, geçmiş metin değerlendirmesi |
| R1 Kanıt modelini düzelt | Tamam — kabul kapsamı ve sınırlar aşağıda | R0 | Resmî dataclass sözleşmesi, ortak rapor/olaylar, doğru etiketler, stored blind takip ve dedup |
| R2 İstek/oturum güvenilirliği | Tamam — HTTP kabul kapsamı | R0; R1 şemasıyla uyumlu | JSON, hedefe özel auth-check, rate, sıralı CSRF/stored ve hata olayları |
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

Evidence kategorileri: `candidate`, `reflection`, `sink-observed`, `resource-callback`.
Bunlar doğrusal merdiven, CVSS veya açıklık etkisi değildir. Gelecekteki
`execution-confirmed` için tarayıcı bağlamı ve o denemeye ait doğrulanmış canary
olayı gerekir; ayrıca self-XSS/by-design/yetki sınırı triage'ı yapılır. Mevcut v1
modeli bu desteklenmeyen etiketi ve doğrulanmış rol iddiasını reddeder.
Resmî [Finding/ReportEvent sözleşmesi](tools/dom-xss-analyzer/EVIDENCE-CONTRACT.md)
Python dataclass olarak uygulanır; ortak rapor çıkışında doğrulanır.

Kabul ölçütleri:

- [x] Bare `--dom` ziyaretindeki alert/confirm/prompt/beforeunload “proven” olmaz; içerik gözlem olarak korunur.
- [x] HTML içindeki ham marker executable'a yükseltilmez; varyant adı execution veya bağlamdan çıkma kanıtı sayılmaz. Yanlış bağlamdaki üç raw marker regresyonu var.
- [x] Aynı response normal, flow, stored, stored-auto ve header yollarında aynı sınıflandırmayı alır; JSON-only JS proof sayılmaz. Yedi Content-Type karşılaştırması var.
- [x] Callback tek başına resource-callback olur; JS kapalı img ile gerçek Chrome kontrolü ve bütün beş payload ailesi için HTTP negatif testleri var. Tam iframe/role fixture kapsamı R3/R4'te açık.
- [x] Stored/stored-auto: yansıma yokken bile cid gönderimden önce kalıcı tutulur; sonradan gelen blind callback ilişkilendirilebilir. Diğer modlarda kalıcı takip henüz yok.
- [x] Stored blind scan bittikten sonra ayrı callback kontrol komutu; run/attempt kimliği, zaman ve operatör rol etiketi var. Hedefe özel HTTP kontrolü R2 tamam; browser rol/oturum aktarımı R3 açık.
- [x] Statik, HTTP, static-guided, DOM ve journal ortak raporları aynı Finding/ReportEvent modelini kullanır; hata ve atlamalar ayrı görünür. Eski statik `--json` ham API'si korunur; ortak çıktı `--json-out` seçeneğidir.

- [x] Dedup aynı submit/parametre/sink/bağlam/rolün kopyalarını gruplar; özgün gözlemleri bellekte korur, girdileri değiştirmez. Farklı veya bilinmeyen rol/sink birleştirilmez. Paylaşım raporları hassas alanları maskeler.

5 Ekim kapanışı: [madde–test matrisi](audit/2026-10-05-r1/R1-KAPANIS.md),
[test sonuçları](VALIDATION.md), [staj kaydı](staj/2026-10-05-r1-kapanis.md).
R1 tamam, kabul edilmiş stored/stored-auto kalıcı blind takip kapsamıyla birlikte
kanıt modelinin tamamlanmasıdır. Reflected/header kalıcı blind journal genişlemesi,
HTTP oturum kontrolü R2 tamam; browser canary execution ve aktarım R3/R6 işidir.

WonderCMS'teki 58→1 bir sayısal hedef değildir. Gerçek grup sayısı kanıt ve erişim politikasıyla belirlenir. Admin'in tasarlanmış HTML editörü ayrı bir security boundary aşmıyorsa “confirmed vulnerability” olmaz.

## R2 — Gönderim ve oturumu güvenilir yap

- [x] Canary çözülmüş JSON nesnesine yerleştirilip JSON serializer ile gönderilir; mevcut 950 örnek seçilen geçerli şablonda parse edilir ve canary round-trip korunur. İç içe değerler ve kontrol karakterleri testli; geçersiz şablon gönderilmez.
- [x] 401/403 veya eksik token auth başarısı sayılmaz; `Bearer None` kurulmaz. Önceden bulunan cookie tek başına login başarısı değildir. [Test ve sınırlar](tools/dom-xss-analyzer/AUTH-LIMITS.md); başarısız form login CLI'ı exit 2 ile durdurur. Hedefe özel HTTP sözleşme kontrolü aşağıda tamam; browser aktarımı R3 açık.
- [x] Auth sonrası hedefe özel oturum kontrolü yapılabilir; JSON kimlik/rol sözleşmesi eşleştirilir, kontrol sonucu ve operatör rol etiketi kaydedilir. Genel role_verified iddiası üretilmez.
- [x] 0.5/s gibi fractional rate ilerler; CLI 0=sınırsız, negatif/sonlu olmayan değer hata; fake-clock testi gerçek uzun uyku gerektirmez.
- [x] JSON gönderiminin Content-Type ayarı istek başına taşınır; iki eşzamanlı JSON isteği ortak EXTRA_HEADERS'ı değiştirmez. Paylaşılan oturumun sıralaması aşağıdaki maddede tamamlandı.
- [x] Tek kullanımlık CSRF refresh+submit ve stored submit+read ortak oturum kilidiyle sıralanır; stored-auto her canary sonrasında okur. Tek oturumda paralel hız artışı yoktur.
- [x] Hata, timeout, rate-limit ve engelleme ortak error/skip olaylarıyla “bulgu yok” durumundan ayrılır.
- [x] R1/R2 negatif örnekleri ana pytest paketinde ve ayrıca zorunlu CI adımındadır. Uzak CI sonucu yerel test başarısı sayılmaz.

6 Ekim [kapanış matrisi](audit/2026-10-06-r2/R2-KAPANIS.md),
[kullanım ve sınırlar](tools/dom-xss-analyzer/SESSION-CONTRACT.md).

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

**K01-min tamam:** [stored yorum vakası](cases/k01-stored-comment/README.md).
Kaydetme→ayrı okuyucu context'i→canary, aynı payload ile encoding sonrası retest,
JS kapalı/JSON/normal dialog negatif kontrolleri; request/response, fix diff,
ortam sürümleri ve kaynak hash'leri mevcut. Yeni CVE/gerçek ürün bulgusu değildir.
Tam R5'in bağımsız temiz ortam tekrarı henüz yapılmadı; aşağıdaki ilk madde açık.

İlk vaka için mevcut yetkili laboratuvar veya minimal yerel fixture kullanılabilir. Teslimat: hedef sürümü, kaynak→sink izi, iki rol gerekiyorsa hesap A/B kontrolü, tam komut, maskeli request/response, cid ile proof, negatif kontrol, fix diff ve aynı testin fix sonrası sonucu.

- [ ] Temiz ortamdan başka biri tekrar üretebilir.
- [x] K01-min için çalıştırılmayan kısım ve gözlenmeyen davranış açık yazılır.
- [x] K01-min staj kaydı amaç, yöntem, bulgu, hata, düzeltme, öğrenilen akışını izler.
- [x] JSON ham marker ve normal dialog false-positive karşı örnekleri; R1 çözümü ve yeni browser negatif kontrolleri belgelenir.
- [x] Writeup 01/10/11'e güncel vaka bağlantısı eklendi; eski rapor değiştirilmedi. Yazıların bütün C düzeltmeleri tamamlandı sayılmaz.

## R6 — Kullanılabilir ilk sürüm

İlk doğrulanmış araştırma sürümünün yayın kapısı: **R1 + R2 + R3 yerel uçtan uca
kanıtı + R4 zorunlu negatif/pozitif CI ölçümü + R5/K01 vaka paketi + aşağıdaki R6
paketleme kontrolleri**. Bunlar olmadan sürüm etiketi açılmaz. R1 sonrası K01-min
ve kanıt belgeleri paylaşılabilir araştırma çıktısıdır, kullanılabilir ürün
sürümü değildir. Etiket numarası R6 sürümleme incelemesinde belirlenecek.

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
