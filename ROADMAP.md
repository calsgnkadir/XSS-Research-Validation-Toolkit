# Ana proje roadmap'i — XSS botu ve staj araştırması

16 Ekim güncel durum: R4 teknik teslimi ve R5/K01 teknik kabulü tamamlandı;
R6 ilk araştırma sürümü için release hazırlığı yapıldı, yayımlanmadı.
Bu turdaki yeniden kontroller de R4 için 57/57, R5 fixture/gate için 22/22
geçti. İnsan triage'ı, ikinci insan tekrarı ve scanner üstünlük sıralaması
kullanıcı kapsam kararıyla zorunlu kapanış ölçütü değildir. Sonuçlar genel ürün
doğruluğu veya vulnerability iddiası oluşturmaz. Sıradaki bot işi R9;
portfolyo/kanıt işleri ayrıca açıktır.

14–15 Ekim devam teslimi aşağıdaki tarihli kayıtlarda korunur; o tarihteki
“genel R4/R6 ve R5 ikinci insan kabulü açık” durumu 16 Ekim kapanışından önceki
durumdur, güncel devam noktası değildir. [Devam raporu](audit/2026-10-14-r3-r6-continuation/README.md).

## 14 Ekim 2026 — tarihli yetenek snapshot'ı

**Aşama:** araştırma amaçlı Python CLI ve rapor prototipi. Paketlenmiş release
henüz yok. R4 auth runner kodu **bec59b4**, R5/K01 aynı-host kanıt commit'i
**70093ff**; sonraki R5/R8/R6 kodu **d41c1cd** için CI ve ilgili indirilen
artifact kabulü geçti. Güncel HEAD ve açık işler [STATUS](STATUS.md) içindedir.
[Durum](STATUS.md) · [Doğrulama](VALIDATION.md) ·
[Corpus v3 kabulü](audit/2026-10-14-r4-corpus-v3/README.md).

| Soru / alan | Kanıtlanan durum | Sınır / kalan kabul |
|---|---|---|
| Bot gelişti mi? | Corpus 9'dan 14'e çıktı; kaynak/parametre/okuma/rol/frame eşlemesi ve CI artifact doğrulaması güçlendi. | Bu gelişme ölçüm güvenilirliğidir; gerçek ürünlerde başarı oranı henüz ölçülmedi. |
| XSS adayı bulabilir mi? | Statik aday analizi, HTTP reflection ve stored akışları, DOM/sink gözlemleri, oturum/CSRF desteği mevcut. | Her adayın bağlamı ve etkisi ayrıca incelenir; reflection açık kanıtı değildir. |
| JavaScript çalışmasını doğrulayabilir mi? | İzinli loopback lab'da submit→read→eşleşen canary execution; corpus 14/14, TP=7 FP=0 FN=0. | Yedi pozitif/yedi negatif kontrollü vaka; genel web veya ürün doğruluğuna genellenmez. |
| Blind/admin seviyesi | Stored/stored-auto attempt kaydı ve CID callback uzlaştırması mevcut. | Callback JS execution değildir; ayrı admin hesabı/yetki sınırı kabulü açık. |
| CVE araştırmasına yardım eder mi? | Aday toplama ve tekrar üretilebilir kanıt hazırlamaya yardımcı olabilir. | Yeni CVE keşfi doğrulanmadı. Ürün/sürüm, etkilenen rol, güvenlik etkisi, by-design/self-XSS ayrımı, yenilik ve fix/retest incelemesi gerekiyor. |
| Araçlarla karşılaştırma | Kapsam, bütçe ve kanıt eşitliğini tanımlayan protokol var. | Kontrollü rakip koşusu ve karşılaştırılabilir başarı ölçümü yok; üstünlük iddiası yok. |
| Test kanıtı | R4 auth runner etkili paket 215 passed; CI 3/3, artifact gate 169 test ve 14/14 corpus; auth kontrolleri 6/6. R5 K01 yeni venv 5/5. | Farklı paketlerin sayıları toplanmaz; bu belge güncellemesi yeni test koşusu değildir. |

**Son dar ilerleme:** auth/CSRF altı hata kontrolü gerçek browser ile, yedi
blind/admin adapter sınır testiyle birlikte 13/13 geçti; ayrı bounded CLI 6/6.
Ana benchmark runner entegrasyonu da yerel 215 birleşik test ve gerçek CLI 6/6
ile kabul edildi; bec59b4 uzak CI 38593458769 3/3 geçti ve indirilen
artifact 169 JUnit, proof 14/14, auth controls 6/6 kabul edildi.
[Runner kanıtı](audit/2026-10-14-r4-auth-runner/README.md).
[Önceki dar kanıt](audit/2026-10-14-r4-auth-blind-controls/README.md).
Engine entegrasyonu tamamladı; R5 QA aynı-host tekrarı yaptı. Aktif uzman yok.
Gerçek admin/blind fixture ve kontrollü kıyas açık.

**14 Ekim üçlü devam teslimi:** R5 için yeni Ubuntu/Python 3.12 K01
workflow'u ve artifact gate yazıldı; Windows'ta 104 birleşik regresyon
ve gate 5/5 doğrulandı; d41c1cd Linux run 38596197622 de başarılı:
13 JUnit, 5/5 proof ve indirilen artifact digest/kaynak hashleri eşleşti.
[R5 gate kanıtı](audit/2026-10-14-r5-linux-gate/README.md).
R8 açık encoder rebinding kaynaklı statik FN düzeltildi; 91 odaklı test
geçti. d41c1cd genel CI 38596197488 3/3 başarılı.
[R8 kanıtı](audit/2026-10-14-r8-rebound/README.md).
R6 geliştirici paketi temiz venv'de kuruldu, üç CLI help ve paketlenmiş
browser demo çalıştı; d41c1cd CI paket install/help adımı geçti.
Sürüm etiketi/yayın yok.
[R6 kanıtı](audit/2026-10-14-r6-package-scaffold/README.md).
Blind/admin ve araç kıyası bu turda ele alınmadı.

**Üç işin yeniden denetimi:** R8'de fonksiyondan önceki modül düzeyi encoder
atamasının gözden kaçtığı karşı örnek bulundu ve dar regresyonla düzeltildi.
R6 wheel temiz venv'e kaynak dizini dışında kuruldu; R5 ayrı agent yeni kanıtla
5/5 tekrarladı. 74cda81 için genel CI 38598901908 3/3 ve Linux K01
38598901721 geçti; indirilen K01 artifact'i kabul edildi. Bunlar ikinci insanın
temiz makine kabulü değildir.
[Yeniden denetim](audit/2026-10-14-three-work-recheck/README.md).

**Kalan sıra:**
1. R4 genel corpus genişletmesi, blind/admin kimlik ve kanıt sınırları,
   eşit koşullu araç karşılaştırması. Auth/CSRF operasyonel hata kontrolleri
   dar kapsamda runner/CI kabulünü geçti.
2. R4 geniş corpus/coverage kabulü ve R3 otomatik header gözlemi.
3. R5/K01 bağımsız temiz ortam tekrarı; R6 kurulum/paketleme/release.
4. R8 analiz kapsamı, R9 operasyon sınırları; aşağıdaki C/K/P/S maddeleri.
5. A01–A05/R7 ürün bazlı araştırma ve CVE triage; yeni doğrulanmış CVE yok.

### Önceki ilerleme kayıtları

Aşağıdaki tarihli paragraflar ilgili teslim anını anlatır; güncel devam noktası
yukarıdaki özet ve STATUS'tur. Tarihsel açıklar daha sonraki dar kabullerle
ilerletilmiş olabilir; ana kabul kutuları aşağıda korunur.

9 Ekim ilerleme kaydı: R4 hard timeout/süreç temizliği, R8 statik context ve
R9 callback/Docker guard değişiklikleri tam yerel tekrarda **824 passed**;
ayrı K01 HTTP fixture **2 passed**, Chrome proof **9/9, TP=3 FP=0 FN=0**.
[Kabul ve kapsam](audit/2026-10-09-resume/README.md). Bu dar teslim genel
R4/R8/R9 kutularını kapatmaz; gerçek ürün bootstrap/port-discovery adapter'ı ve
uzak Linux CI artifact kabulü açık kalır. 11 Ekim kontrolde `5df2577` için
uzak CI/job sonuçları başarılı bulundu; artifact içerikleri henüz incelenmedi.
Güncel devam noktası [STATUS](STATUS.md); aşağıdaki 6–7 Ekim test sayıları tarihseldir.

13 Ekim dar R4 teslimi: sabit Bludit 3.16.2 yerel imajı için internal uygulama +
loopback Apache ingress adapter'ı gerçek Docker kabulünde kurulum, login ve
ham/escaped browser kontrolünü tamamladı. Eksik browser ve enjekte edilmiş
kontrol uyuşmazlığı güvenli hata; üç cleanup geçti, 15/27/9 mevcut Docker
kaynağı korundu. Birleşik **335 test sıfır skip**. [Kanıt](audit/2026-10-12-r4-ingress-live/README.md).
Gerçek ürün benchmark skorlayıcısına bağlanmadı; genel R4/R9 açık kalır.

12 Ekim dar teslim: zorunlu R3/R4 CI artifact kapısı yerelde JUnit sıfır-skip,
dokuz vaka tutarlılığı ve demo execution kontrolüyle doğrulandı.
[Yeni kanıt](audit/2026-10-12-r4-ci-acceptance/README.md). Uzak artifact API'si
HTTP 401 verdi; içerik kabulü ve yeni kapının uzak CI koşusu açık. Genel
R4/R9 kutuları değişmedi; Git teslimi kullanıcı tarafından sonradan onaylandı.

12 Ekim devamı: `c5d5451` uzak Linux CI ve indirilen artifact kabulü geçti:
94 test sıfır skip, dokuz vaka TP=3 FP=0 FN=0 ve demo execution-observed.
[Uzak kanıt](audit/2026-10-12-r4-ci-acceptance/remote/acceptance.json).
R9 ortak JSON/HTML raporlarında bilinen API/CSRF alanları ve HTTP(S) evidence
linkleri için maskeleme düzeltildi; [126 testlik dar kabul](audit/2026-10-12-r9-report-privacy/README.md).
Gerçek ürün adapter'ı ve genel R4/R9 kutuları açık kalır.

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
| 1 | Bot R0–R6, R8–R9 | R0–R6 teknik kapsam tamam (R6 adayı yayımlanmadı); R8 tamam; R9 açık | Doğru kanıt, güvenilir oturum, browser entegrasyonu, ölçüm, kurulabilir sürüm ve operasyon sınırları |
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
R3 browser proof komutu loopback demo, observer/eval, SPA route ve allowlist header
desteğiyle çalışıyor; WebSocket/genel ağ sandboxı bu komutun scope'u dışında.
Rapor C01–C13, kanıt K01–K05, portfolyo P01–P04, staj S01–S03 ve araştırma
A01–A05 kapsamdan çıkarılmadı; aşağıdaki kabul koşulları geçerlidir.

### Son kanıt ve teslim sırası

| İş | Son kabul kanıtı | Durum / sonraki kapı |
|---|---|---|
| R1 | 2026-10-05, [kapanış matrisi](audit/2026-10-05-r1/R1-KAPANIS.md) | Tamam; 479 passed, 36 skipped |
| R2 | 2026-10-06, [kapanış matrisi](audit/2026-10-06-r2/R2-KAPANIS.md) | HTTP kabul kapsamı tamam; browser oturum aktarımı R3'te |
| R3 | 2026-10-07, [yeniden doğrulama](audit/2026-10-07-r3-r4-revalidation/README.md) | Loopback kabulü PASS; eval/canary/evidence yeniden sınandı, cleanup/state restorasyonu düzeltildi |
| K01-min / R5 | [16 Ekim teknik kabul](audit/r5-final-acceptance-2026-10-16/README.md) | Tamam; temiz Windows venv 5/5 ve tarihsel Linux artifact gate 5/5; ikinci insan koşusu zorunlu kapsamdan çıkarıldı |
| R4 | [16 Ekim kapanış kanıtı](audit/r4-proof-experiment-2026-10-16/README.md) | **Kapsamlı teknik teslim tamamlandı:** kimlik scorer/gate, browser CI/artifact, Bludit lifecycle ve exact-payload replay kabul edildi. Ürün doğruluğu veya araç sıralaması iddiası yok. |
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

Tarihsel agent inceleme notu, yerel kopyada korunup kamuya açık depodan çıkarılmıştır.

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
| R3 Tarayıcı doğrulamasını bağla | Tamam — loopback proof pipeline | R1 + R2 | Auth/stored/DOM, observer, SPA route ve kontrollü browser kanıtı |
| R4 Doğru benchmark ve CI | **Tamam — 16 Ekim teknik kapsam kararı** | R1–R3 | Kimlik bazlı ölçüm, hata/timeout kapsamı, doğrulanmış artifact, eşit bütçeli loopback koşusu ve exact-payload browser replay |
| R5 / K01 Tekrar üretilebilir XSS vaka çalışması | **Tamam — 16 Ekim teknik kabul** | R3 + R4 | Temiz lab kurulumu, proof, fix, retest, staj yazısı; ikinci insan tekrarı zorunlu kapsamdan çıkarıldı |
| R6 Kullanılabilir ilk sürüm | Teknik hazırlık tamam; release adayı yayımlanmadı | R1–R5 | Paketleme, konfigürasyon, JSON/HTML, demo ve sürüm notu |
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
- [x] Callback tek başına resource-callback olur; JS kapalı img ile gerçek Chrome kontrolü ve bütün beş payload ailesi için HTTP negatif testleri var. Iframe/role fixture kapsamı R3'te kabul edildi.
- [x] Stored/stored-auto: yansıma yokken bile cid gönderimden önce kalıcı tutulur; sonradan gelen blind callback ilişkilendirilebilir. Diğer modlarda kalıcı takip henüz yok.
- [x] Stored blind scan bittikten sonra ayrı callback kontrol komutu; run/attempt kimliği, zaman ve operatör rol etiketi var. Hedefe özel HTTP kontrolü R2 ve browser rol/oturum aktarımı R3 tamam.
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
- [x] 401/403 veya eksik token auth başarısı sayılmaz; `Bearer None` kurulmaz. Önceden bulunan cookie tek başına login başarısı değildir. [Test ve sınırlar](tools/dom-xss-analyzer/AUTH-LIMITS.md); başarısız form login CLI'ı exit 2 ile durdurur. Hedefe özel HTTP sözleşme kontrolü ve browser aktarımı tamam.
- [x] Auth sonrası hedefe özel oturum kontrolü yapılabilir; JSON kimlik/rol sözleşmesi eşleştirilir, kontrol sonucu ve operatör rol etiketi kaydedilir. Genel role_verified iddiası üretilmez.
- [x] 0.5/s gibi fractional rate ilerler; CLI 0=sınırsız, negatif/sonlu olmayan değer hata; fake-clock testi gerçek uzun uyku gerektirmez.
- [x] JSON gönderiminin Content-Type ayarı istek başına taşınır; iki eşzamanlı JSON isteği ortak EXTRA_HEADERS'ı değiştirmez. Paylaşılan oturumun sıralaması aşağıdaki maddede tamamlandı.
- [x] Tek kullanımlık CSRF refresh+submit ve stored submit+read ortak oturum kilidiyle sıralanır; stored-auto her canary sonrasında okur. Tek oturumda paralel hız artışı yoktur.
- [x] Hata, timeout, rate-limit ve engelleme ortak error/skip olaylarıyla “bulgu yok” durumundan ayrılır.
- [x] R1/R2 negatif örnekleri ana pytest paketinde ve ayrıca zorunlu CI adımındadır. Uzak CI sonucu yerel test başarısı sayılmaz.

6 Ekim [kapanış matrisi](audit/2026-10-06-r2/R2-KAPANIS.md),
[kullanım ve sınırlar](tools/dom-xss-analyzer/SESSION-CONTRACT.md).

## R3 — Tarayıcı ile gerçek doğrulama — tamam

7 Ekim yeniden doğrulaması: tüm analyzer/bench paketi 681 passed, sıfır skip;
cleanup hatası sonrası browser kapanışı ve oturum durumunun geri yüklenmesi
iki karşı örnekle düzeltildi. JSON/HTML tam nesne eşitliği sınandı.
[Yeni kabul paketi](audit/2026-10-07-r3-r4-revalidation/README.md).

- [x] Loopback tek-origin demo için HTTP auth ve operatörce tanımlı kimlik/rol sözleşmesi browser'a aktarılır ve browser'da tekrar kontrol edilir. Aynı hesap/rol; ayrı iki hesaplı yetki testi değildir; R1 role_verified false kalır. [Kanıt](tools/dom-xss-analyzer/BROWSER-PROOF.md).
- [x] Tek komutla loopback fixture'da submit→read→CID canary execution gözlemi→JSON/HTML raporu çalışır; finding/confirmed iddiası üretmez.
- [x] Fonksiyon içindeki direct eval karşı örneği doğrulandı ve eval hook kaldırıldı; native lexical scope korunur. Eval gözlemi desteklenmez ve JSON/HTML operasyonel olayında açıkça belirtilir. Önceki global-scope test yeterli değildi; 6 Ekim agent turu bu kabul kanıtını düzeltir.
- [x] Gerçek href tıklaması, same-origin iframe ve sınırlandırılmış gecikme test edilir; gözlem penceresi aşımı inconclusive olur. about:blank/srcdoc kapsam dışı.
- [x] SPA rota adayları same-origin filtresinden geçerek kuyruğa eklenir; duplicate ve route budget vardır.
- [x] Browser'a yalnız allowlist edilmiş auth/CSRF header'ları aktarılır; ham değerler rapora yazılmaz. Browser trafiğinden otomatik header harvest bu komutta yapılmaz; `dxadom.extract_auth_headers` ayrı gözlem çıktısıdır.
- [x] Browser yolu açık seçilebilir; Windows Chrome ile doğrulandı, sabit Playwright Chromium Linux CI işi eklendi. Uzak CI sonucu bu teslimde alınmış sayılmaz.

R3 dışında kalan işler R4'e (Linux CI ve header gözlemi) ve R9'a (WebSocket/genel ağ sandboxı)
taşındı; R3 loopback kabulü bunları tamamlanmış saymaz.

Tek bir hook'a güvenmek yerine kaynak girdisi ve olay arasındaki ilişki kaydedilir. Unrelated application dialog, konsol çıktısı veya random cid benzeri metin proof olamaz.

## R4 — Küçük, doğru ve tekrar üretilebilir ölçüm — tamam (sınırlandırılmış teknik kapsam)

**16 Ekim kapanış kararı:** R4'ün teknik teslimatı tamamlandı. Sabit corpus ve
kimlik bazlı scorer, eksik/timeout kapıları, zorunlu browser CI ve indirilen
artifact doğrulaması, Bludit lifecycle/runner, ayrı auth kontrolleri ve exact
scanner payload replay kapısı kanıtlandı. Son Chrome paketi 57/57 geçti; yeni
replay 8 tarihsel satırı inceledi, altı eşleşen adayı yeniden oynattı; iki
Dalfox raw payload raw fixture'da dialog üretti, escaped kontroller üretmedi.
Diğer adaylar inconclusive kaldı. Kaynak run tarihsel ve broker-cookie
kapsamındadır; yeni scanner koşusu yapılmadı. HTTP dışı browser kanalları ve
WebSocket için genel ağ sandboxı R9 kapsamındadır; bu R4 replay'i böyle bir
garanti vermez.

Kullanıcı kararıyla bağımsız insan triage'ı ve rakip üstünlüğü R4'ün zorunlu
kapanış ölçütü olmaktan çıkarıldı. Karşılaştırma protokolü ve geçmiş kayıtlar
korunur; mevcut sonuçtan TP/FP/FN, doğruluk oranı, genel ürün açığı veya kazanan
çıkarılmaz. Bunlar bu roadmap'in R4 kapanışını engellemez. [Son kabul ve sınırlar](audit/r4-proof-experiment-2026-10-16/README.md).

16 Ekim ara denetiminde 8/8 tarihsel scanner satırının hiçbiri oracle'nın
original-session CID/JS proof sözleşmesini taşımıyordu; ara test 48/48 geçti.
Bu ara sonuç aynı tarihteki final replay ve teknik kapsam kararıyla supersede
edildi. Ayrıntı [ara denetimde](audit/r4-closure-2026-10-16/README.md).
[Gerekçe ve kanıt matrisi](audit/r4-closure-2026-10-16/README.md).

15 October resumed delivery: corpus v4 adds comment/template negatives and
activated-template positive. Required Chrome suite 254 passed; strict CLI
17/17, TP8 FP0 FN0. General admin/controlled-comparison criteria remain open.
[Acceptance](audit/2026-10-15-r4-broader-corpus/README.md).
15 October follow-up: separate writer and reader-admin accounts, blind submission,
CID-matched Chrome proof and escaped control passed 3/3, repeated by coordinator.
This validates only the fixture. A pinned Dalfox 3.2.4 vs dxadyn loopback attempt
was inconclusive (8 selected, 4 completed, 0 errors, 4 timeouts); all Dalfox
runs timed out, while dxadyn raw reflections remain candidates without execution
proof. No ranking or accuracy score is accepted. Competitor comparison remains open.
[R4 evidence](audit/2026-10-15-r4-admin-comparison/README.md).

15 Ekim devamı: ortak 200 istek/2 rps/120 saniye ve 15 saniye istemci
timeout sınırlarında yeni Dalfox/dxadyn aday koşusu 8/8 tamamlandı; hata,
timeout veya eksik koşu yok. Bağımsız kapı kimlikleri, kapsam paydasını ve
çıktı hashlerini doğrular. Broker oturumu bağımsız araç login'i değildir;
adayların CID/browser kanıt eşlemesi ve insan triage'ı olmadan karşılaştırma
kabulü ve sıralama açık kalır.
[Yeni R4 kanıtı](audit/2026-10-15-r4-comparator-execution/README.md).
Code 0261baa remote CI 38706882024 and downloaded artifact accepted corpus17/17
and 179 zero-skip tests; [remote record](audit/2026-10-15-resumed-delivery/remote-r4-acceptance.json).
This does not close the broader R4 criteria.


14 Ekim corpus v3: 14 vaka; önceki dokuza sanitized+raw, no-op sanitizer→DOM,
alternatif editor/source/sink için raw/fixed ve açık same-origin iframe eklendi.
Kimlik/frame adapter ve CI gate buna bağlandı. Yerel 527 birleşik test ve
strict CLI 14/14 (TP=7 FP=0 FN=0) geçti. 4331403 uzak CI 38550538424
3/3 başarılı; indirilen artifact gate 134 test ve corpus 14/14 ile geçti.
[Kanıt ve sınırlar](audit/2026-10-14-r4-corpus-v3/README.md).
[Kapsam paydası ve karşılaştırma protokolü](bench/COMPARISON-PROTOCOL.md)
hazır; gerçek rakip kıyası yapılmadı. Bu, statik taint, farklı hesaplar arası
yetki sınırı, blind/admin veya auth/CSRF genel kabulünü kapatmaz.


14 Ekim: strict gate'teki gerçek eksik, CI'nin Markdown corpus çıktısını okumaması
ve JSON raporunun Python/platform/komut/kaynak hashlerini checkout'a bağlamamasıydı.
Gate şimdi canonical Markdown render'ını JSON ile tam eşleştiriyor ve source /
corpus hash'lerini mevcut checkout'la doğruluyor; workflow `r4-proof.md`'yi
kapıya veriyor. QA incelemesi makul ama yanlış Python/platform beyanlarını kabul
eden bir boşluk buldu; gate artık CI Python 3.12/Linux runtime'ına bağlanıyor ve
bu karşı örnekleri reddediyor. Takip paketi 94 focused, 208 birleşik test geçti.
`7f67d53` artifact kabulünden sonra runtime sıkılaştırması `3ca474a` olarak
push edildi. Yeni CI 38530419858 üç job'da geçti; indirilen artifact digest,
JUnit, JSON/Markdown, runtime ve kaynak hashleri güncel gate ile doğrulandı.
[Runtime uzak kabul](audit/2026-10-14-r4-provenance-gate/runtime-remote-acceptance.json).
[Yerel ve remote kanıt](audit/2026-10-14-r4-provenance-gate/README.md).

13 Ekim dar teslimler: pinned Bludit 3.16.2 için internal uygulama + sabit Apache
loopback ingress gerçek kuruluma ulaştı. Ayrı login, iki public raw/escaped
browser kontrolü ve cleanup geçti; eksik browser/mismatch hata oracleları geçti;
15/27/9 önceki Docker kaynak kimliği korundu. [Lifecycle kabulü](audit/2026-10-12-r4-ingress-live/README.md).
Opt-in adapter ayrıca `bench/run.py` üzerinden canlı çalıştı; `product_controls`
ayrı raporlandı ve scanner TP/FP/FN toplamları değişmedi. [Runner kabulü](audit/2026-10-13-r4-runner-live/README.md).
Ham içerik admin tarafından yazıldığı için kanıt **by-design**; XSS açığı veya
role boundary değildir. Geniş R4 scorer, corpus ve CI kabulü açık kalır.

12 Ekim kaydı tarihsel: o tarihte tek internal container host port üretmedi ve
ürün koşusu başlamadan durdu. [Tarihsel kanıt](audit/2026-10-12-r4-product-adapter/README.md).


Güncel dar kabul: 9 Ekim Windows worker timeout/crash/cleanup ve strict corpus
kanıtı [son pakettedir](audit/2026-10-09-resume/README.md). 11 Ekim kaynak
hash'leri bu paketle eşleşti. Genel R4 ve aşağıdaki birleşik kabul kutuları
aynı kapsamı korur; tarihsel eksik listeleri güncel görev listesi değildir.

7 Ekim tarihsel doğrulama: yeni tam paket 681 passed, sıfır skip. Ayrı Chrome CLI
9/9, TP=3 FP=0 FN=0; eksik browser ve gerçek lab içinde enjekte edilen vaka
hatası rapor üreterek strict exit 1 verdi. R4 yerel kapsam PASS; genel roadmap
kapanışı değil. [Yeni sonuçlar](audit/2026-10-07-r3-r4-revalidation/README.md).

7 Ekim ikinci dar teslim: proof vaka istisnası tüm raporu kesmez; error/timeout
skorlanmadan kaydedilir, kalan vakalar sürer ve strict kapısı başarısız olur.
Yeni birleşik kabul 146 passed, skip yok; gerçek Chrome CLI 9/9, TP=3 FP=0 FN=0.
Sert süre sınırı ve süreç sonlandırma bu teslimde uygulanmadı; genel R4 kabul
kutuları açık kalır. [Kabul ve sahiplik kaydı](audit/2026-10-07-r4-case-isolation/README.md).

7 Ekim ilerlemesi: `loopback-proof/2` dokuz yerel vaka (3 pozitif, 6 negatif),
bağımsız etiket/fixture kontrolleri ve JS-kapalı gerçek callback negatifi eklendi.
Yeni birleşik kabul 136 passed; strict CLI 9/9, TP=3 FP=0 FN=0.
Zorunlu browser CI yoluna test/strict benchmark/artifact adımları bağlandı;
uzak CI çalıştırılmadığından aşağıdaki CI kabul kutuları açık tutulur.
Gerçek ürün adapter'ı ve geniş sanitizer/rol kapsamı tamamlanmadı.
[Kanıt ve sınırlar](audit/2026-10-07-r4-native/README.md).

6 Ekim ilk teslim: eksik FN hesabı, süreç timeout/error ayrımı, seçilen/tamamlanan/
atlanan hedef sayıları, FP ve eksik koşuda strict gate, JSON/Markdown artifact
düzeltildi. Kimlik bazlı execution eşleme fonksiyonu regresyon testlidir; mevcut
CLI adapter'ı hâlâ aday sayar, bu nedenle gerçek XSS TP/FP/FN kabulü kapanmadı.
[Teslim ve kalanlar](audit/2026-10-06-r4/README.md).

6 Ekim ikinci teslim: ayrı `--proof-suite` raw/fixed/JSON/dialog loopback
fixture'larını gerçek `dxaprove.run` üzerinden kimlik scorer'ına bağlar.
CID/frame/source/rol doğrulaması, tamamlanmış pozitif miss için FN ve
error/invalid ayrımı testlidir. Legacy aday sayaçları ayrı kalır. Bu dört
fixture tam corpus, gerçek ürün adapter'ı veya uzak CI kapanışı değildir.
Bu tarihsel çalışma/kanıt paketi yerel kopyada korunup kamuya açık depodan çıkarılmıştır.

Önce aşağıdaki sentetik fixture matrisi, ardından tek gerçek uygulama adapter'ı. 20 yarım hedef yerine kurulumdan rapora çalışan küçük corpus.

R3'ten devreden doğrulama işleri:

- [x] Uzak Linux CI işi ve artifact sonucu yerel Windows başarısından ayrı kaydedilir ([14 Ekim remote kabul](audit/2026-10-14-r4-provenance-gate/remote-acceptance.json)).
- [x] Browser trafiğinden allowlist edilmiş auth/CSRF header adları ayrı gözlem çıktısı olarak doğrulandı; ham değer rapora girmez. Bu gözlem token/rol doğrulaması veya header replay değildir ([yerel Chrome kabulü](audit/2026-10-14-r3-r6-continuation/README.md)).

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

- [x] Yerel scorer kabulü: bulgu kimliği bazlı eşleme; beklenen 3, bulunan doğru 1 için TP=1/FN=2. [16 Ekim kanıtı](audit/r4-local-acceptance-resume/README.md). Gerçek scanner adayı execution eşlemesi değildir.
- [x] Yerel scorer kabulü: crash/timeout/skipped `ok` veya true negative sayılmaz; kapsama paydası açıklanır. [16 Ekim kanıtı](audit/r4-local-acceptance-resume/README.md).
- [x] Yerel scorer kabulü: JSON-only ve sadece resource-callback, doğrulanmış XSS TP'sine katılmaz. [16 Ekim kanıtı](audit/r4-local-acceptance-resume/README.md).
- [x] Yerel gate kabulü: bilinen negatif fixture'da FP, zorunlu pozitif fixture'da FN CI kapısını düşürür. [16 Ekim kanıtı](audit/r4-local-acceptance-resume/README.md). Bu turda uzak CI yeniden çalıştırılmadı.
- [x] Gerekli browser işi continue-on-error değildir; uzak JUnit sıfır skip ile gate'ten geçti (14 Ekim).
- [x] Sabit uygulama digest'i, bootstrap/login ve endpoint'ler; disposable teardown doğrulandı (13 Ekim Bludit lifecycle kabulü). Bu, scorer entegrasyonunu veya genel R4'ü kapatmaz.
- [x] JSON/Markdown sonuçları ve ortam/sürüm/komut bilgileri CI artifact olarak saklanır ve indirilen içerik gate'ten geçti (14 Ekim).
- [x] Araç kıyasının yayın eşiği ve sonuç sınırı kaydedildi; güncel aday/replay kanıtıyla sıralama yayımlanmıyor. Kullanıcı kararıyla insan triage/üstünlük ölçümü zorunlu kapanıştan çıkarıldı; kanıtsız üstünlük iddiası yapılmayacak. [Karar](audit/r4-proof-experiment-2026-10-16/README.md).

15 Ekim R4 artifact kapısı, callback sayısı/varlığı özetini nested fixture
kanıtıyla türü dahil eşleştiriyor. Sekiz yanlış JSON/Markdown çifti önce hatayı
üretti; dar düzeltme kabul edildi. Genel corpus/admin ve karşılaştırma açık.
[R4 kabul eşlemesi](audit/2026-10-15-r4-acceptance/README.md).

## R5 — Stajın devamı olan güçlü vaka — tamam (teknik kabul)

**16 Ekim kapanış kararı:** Yeni izole Windows venv'de K01 gate **5/5** browser
kontrolü ve **5/5** ayrı port cleanup ile geçti; proof paketindeki 12 artifact,
3 kaynak ve gate hash'i eşleşti. Tarihsel indirilen Linux artifact gate'i de
5/5 proof ve 13/13 sıfır-skip test kaydı içeriyor. Farklı commit/ortamlara ait
kanıtların provenance sınırları audit'te belirtilmiştir. Kullanıcı kararıyla
başka bir insanın tekrarı zorunlu kapanıştan çıkarıldı; form opsiyonel tarihsel
kayıt olarak boş saklanır. [Teknik kabul](audit/r5-final-acceptance-2026-10-16/README.md).

16 Ekim ara denetimi tarihsel proof hashlerini eşleştirdi; o sırada yeni
browser/CI koşusu yapmamıştı. Aynı gün sonraki temiz-vnev koşusu ve teknik
kapsam kararı bu ara notu supersede eder. [Ara kabul matrisi](audit/r5-closure-2026-10-16/README.md).

Historical 15 October handoff: [independent-repeat form](cases/k01-stored-comment/INDEPENDENT-REPEAT.md)
was left unfilled. On 16 October the user removed a second-person run from
mandatory R5 closeout; this historical open status is superseded and the form
remains optional. No second-person execution is claimed.


15 Ekim: `check_repro.py --profile local --browser ...` taşınabilir kabul
komutu eklendi; varsayılan CI Linux/Python 3.12 şartını koruyor. Her iki profil
tam runtime beyanını kontrol eder; optimize Python reddedilir. Yeni yerel
5/5 kontrol ve kapalı port kabulü, ikinci insan tekrarı değildir.
[R5 teslim](audit/2026-10-15-r5-handoff/README.md).

Linux clean workflow ve bağımsız artifact gate kodu eklendi; yerel Windows
gate 5/5, uzak Linux run 38596197622 5/5 ve artifact kabulü geçti.
İkinci kişi kabulü o tarihte ayrı açıktı; kullanıcı 16 Ekim'de bunu zorunlu
R5 kapanış ölçütünden çıkardı.
[Dar R5 kanıtı](audit/2026-10-14-r5-linux-gate/README.md).


**K01-min tamam:** [stored yorum vakası](cases/k01-stored-comment/README.md).
14 Ekim aynı Windows hostunda yeni Python venv, pinned Playwright ve mevcut
Chrome ile bağımsız agent tekrarında 5/5 kontrol ve 5/5 fixture teardown geçti.
[Koşu kanıtı](audit/2026-10-14-r5-k01-clean-repeat/README.md).
Bu 14 Ekim kaydı 16 Ekim teknik kapanış kararından öncedir.
Kaydetme→ayrı okuyucu context'i→canary, aynı payload ile encoding sonrası retest,
JS kapalı/JSON/normal dialog negatif kontrolleri; request/response, fix diff,
ortam sürümleri ve kaynak hash'leri mevcut. Yeni CVE/gerçek ürün bulgusu değildir.
Temiz Windows ve Linux ortam koşuları var. Bağımsız ikinci kişi tekrarı
yapılmadı; kullanıcı kararıyla bu R5 kapanış şartı değildir.

İlk vaka için mevcut yetkili laboratuvar veya minimal yerel fixture kullanılabilir. Teslimat: hedef sürümü, kaynak→sink izi, iki rol gerekiyorsa hesap A/B kontrolü, tam komut, maskeli request/response, cid ile proof, negatif kontrol, fix diff ve aynı testin fix sonrası sonucu.

- [x] Temiz Windows venv ve ayrı Linux artifact gate teknik tekrarı kabul edildi; kullanıcı kararıyla bağımsız ikinci insan şartı zorunlu ölçütten çıkarıldı, boş form tarihsel/isteğe bağlı tutuldu. [Kabul ve sınır](audit/r5-final-acceptance-2026-10-16/README.md).
- [x] K01-min için çalıştırılmayan kısım ve gözlenmeyen davranış açık yazılır.
- [x] K01-min staj kaydı amaç, yöntem, bulgu, hata, düzeltme, öğrenilen akışını izler.
- [x] JSON ham marker ve normal dialog false-positive karşı örnekleri; R1 çözümü ve yeni browser negatif kontrolleri belgelenir.
- [x] Writeup 01/10/11'e güncel vaka bağlantısı eklendi; eski rapor değiştirilmedi. Yazıların bütün C düzeltmeleri tamamlandı sayılmaz.

## R6 — Kullanılabilir ilk sürüm

16 Ekim R6: README kurulum/config/demo kapsamı ve temiz wheel kabulü gözden
geçirildi. Metadata kapısındaki eksik dağıtım kimliği/entry point kontrolü
eklenip regresyonlandı; son wheel temiz Windows venv'e offline kuruldu ve 7/7
kontrol geçti, dokuz modül kaynak/wheel/kurulu kopya hashleri eşleşti.
[16 Ekim R6 kabulü](audit/2026-10-16-r6-final-readiness/README.md).
İlk araştırma sürümü `0.1.0` seçildi ve bu sürüme özel changelog hazırlandı.
Release tag'i ve dış paket yayını yapılmadı; bunlar için ayrıca açık yayın
yetkisi ve son kabul gerekir.

16 Ekim son kaynak tekrarında, R9 çalışma ağacındaki dokuz modülle `0.1.0`
wheel yeniden üretildi; temiz geçici venv kurulum/CLI kapısı **7/7** geçti,
source/wheel/install modül hashleri eşleşti. Paketlenmiş loopback demo
`execution-observed` verdi, triage `unreviewed` kaldı. Wheel SHA-256
`d1151704ba4c5e6dbe91696f632040ad528947bf97b04dc765b585ef6c3729ad`.
Teknik R6 satırları bu test edilen aday için tamam; yayın satırı açık ve ayrı
yetki bekliyor. Bu yerel R9 değişiklikleri commit/push veya yeni hosted CI
değildir. [Birleşik R6/R9 audit kaydı](audit/2026-10-16-r6-r9-final-source/README.md).

R8 güncel kaynak denetimi mevcut taint/rebinding, context, template ve destek
sınırlarını doğruladı. Ardından Python-only AST pilotu eklendi: tuple-unpack
pozitifi ve string içindeki sahte source negatifi önce kırmızıydı; final iki
vaka corpus'u TP/FP/FN/TN **1/0/0/1** ölçtü. Ara entegrasyon testlerindeki
context ve cross-file gerilemeleri düzeltildi. Son focused R8 **95/95**, R6 ile
birleşik **210/210** geçti. R8 roadmap kriterleri dar ve belgelenmiş scope'ta
tamamlandı; genel soundness, geniş doğruluk oranı veya diğer dillere AST iddiası
yok. [R8 kapanış kaydı](audit/2026-10-16-r8-current-review/README.md).

15 October resumed delivery: dynamic config supports depth/parallel/rate with
CLI > config > defaults, strict validation and per-mode applicability. Focused
101 tests and fresh-venv installed smoke 6/6 passed; coordinator integration
503 passed. Counts overlap. The installed-smoke helper filename collision was
fixed and the smoke rerun. No release tag. This 15 October R6 snapshot preceded
the 16 October technical closeout of R4/R5; release/tag work remains separate.
[Acceptance and limits](audit/2026-10-15-r6-config-release/README.md).
15 October release-readiness matrix: rebuilt wheel installed into fresh offline
venvs. All CLI help/config, docs, metadata/browser-extra and packaged loopback
demo checks passed; focused suite 109/109. Wheel remains 0.0.0.dev0, demo triage
unreviewed. This 15 October snapshot predates R4/R5 closeout; R6 remains open
for its own release criteria. No tag/publication.
[Matrix](audit/2026-10-15-r6-release-matrix/README.md).


15 Ekim: dinamik CLI ana mod çakışmaları ve DOM ile HTTP oturum seçenekleri
işlem öncesinde reddedilir. Yedi rapor dalında JSON/HTML tek belge matrisi
eklendi; etkilenen 304 test geçti. Mock CLI testleri yeni canlı tarama kanıtı
değildir; genel config kapsamı ve release kapısı açık.
[R6 devam kabulü](audit/2026-10-15-r4-r5-r6-continuation/README.md).

0.0.0.dev0 geliştirici paketi ve browser extra yerel temiz venv'de kuruldu;
paketlenmiş CLI demo çalıştı. CI paket smoke geçti (38596197488); ilk sürüm/release
etiketi henüz yok. [Dar R6 kanıtı](audit/2026-10-14-r6-package-scaffold/README.md).

Yeni dar teslimde statik `dxa` için `CLI > config > low` önceliği ve BOM'lu JSON
config test edildi. Statik ve dinamik CLI JSON/HTML çıktıları tek normalize
kanıt belgesini paylaşır; reflekte mod için kimlik/escape/redaksiyon regresyonu
var. Tüm CLI config seçenekleri ve rapor modları matrisi, release kapısı açık.
[Devam kanıtı](audit/2026-10-14-r3-r6-continuation/README.md).


İlk doğrulanmış araştırma sürümünün yayın kapısı: **R1 + R2 + R3 yerel uçtan uca
kanıtı + R4 zorunlu negatif/pozitif CI ölçümü + R5/K01 vaka paketi + aşağıdaki R6
paketleme kontrolleri**. Bunlar olmadan sürüm etiketi açılmaz. R1 sonrası K01-min
ve kanıt belgeleri paylaşılabilir araştırma çıktısıdır, kullanılabilir ürün
sürümü değildir. Etiket numarası R6 sürümleme incelemesinde belirlenecek.

- [x] Kaynaktan temel kurulum ve opsiyonel browser extra paketlenir; güncel wheel temiz venv'de kuruldu, CLI/help ve config gate'i geçti. [16 Ekim kabulü](audit/2026-10-16-r6-final-readiness/README.md).
- [x] İlk araştırma release sürümü `0.1.0` seçilir ve release-specific CHANGELOG hazırlanır; hazırlık commit'i tag veya dış paket yayını değildir.
- [ ] Release tag'i veya dış paket yayını yalnız son kabul ve açık release yetkisiyle yapılır.
- [x] Config önceliği CLI > config > varsayılan olarak testlidir.
- [x] JSON şeması sürümlüdür; HTML aynı kanıttan üretilir; rapor test girdisini güvenli escape eder.
- [x] Belgelenmiş CLI seçenekleri help ile uyumludur; unsupported birleşimler açık hata verir.
- [x] Demo sonucu temiz ortamda elde edilir; known limitations ve fixture kapsamı görünürdür.

15 Ekim: Bu dört yerel kabul, yukarıdaki release-matrix kaydındaki 109 test
ve kurulu CLI/demo kanıtına dayanır; yeni test koşusu değildir. Kalıcı
kurulu-wheel CI kontrolü ayrıca temiz venv'de 7 kontrolü ve dokuz modülün
kaynak/wheel eşleşmesini doğruladı; değiştirilmiş wheel reddedildi.
[Yeni kapı](audit/2026-10-15-r6-installed-ci/README.md).
Paket 0.0.0.dev0; etiket/yayın açık kalır. R4/R5 bağımlılığı 16 Ekim teknik
kapanış kararıyla karşılandı; R6'nın kendi release ölçütleri hâlâ sürüyor.

SARIF sonraki küçük teslim olabilir. Plugin API/Marketplace, ihtiyaç gösterilmeden bu sürümü geciktirmez.

## R7 — Gerçek ürün araştırması

Bir ürün ve bir ekosistemle sınırla. Son desteklenen sürüm, rol/yetki sınırı, bilinen advisory'ler ve program kapsamı kontrol edilir. Laboratuvarda çalışan PoC, tek başına yeni CVE veya program kabulü anlamına gelmez. Duplicate/invalid/cannot-reproduce sonuçları da kaydedilir. Eski sohbetten bir şirket adı gelmesi o hedefi tarama talimatı değildir.

Kabul ölçütü CVE sayısı değil: yeniden üretilebilir ve doğru sınıflandırılmış rapor, uygun disclosure kanalı, takip durumu. Gönderim/yayın ayrı yetkilendirme gerektiren dış iletişim işidir.

## Ertelenen işler

Genel subdomain/dizin brute-force motoru, IoT genişlemesi, daha çok mutation sırf sayı için, altı dilde aynı anda AST, plugin pazarı. Statik analiz için önce mevcut sanitizer FN düzeltmesi ve dosya kapsamı; sonra tek dilde AST prototipi. AST kullanmak tek başına sound analiz değildir.

## Her teslimin kapanışı

Kod + yanlış davranışı yakalayan test + ilgili fixture sonucu + kısa sürüm notu + STATUS güncellemesi. Yeşil test sayısı artışı zorunlu hedef değildir; doğru beklenti ve kapsama anlamı esastır. Süre tahmini yerine bir sonraki küçük teslim ve kabul koşulu takip edilir.

## R8 — Statik analiz ve fixture doğruluğu (bot; tamam, sınırlı kapsam)

Açık encoder adı identity fonksiyonuna yeniden atanınca taint'in kaybolması
dar kapsamda düzeltildi; önce/sonra ve gerçek encoder karşı örnekleriyle
91 odaklı test geçti; d41c1cd genel CI 38596197488 3/3 başarılı.
Dinamik alias/branch çözümlemesi sınırlı destek dışı olarak belgelenmiştir.
[Dar R8 kanıtı](audit/2026-10-14-r8-rebound/README.md).

16 Ekim: sınırlı Python AST pilotu ve etiketli iki-vaka corpus kabul edildi;
R8 odaklı 95 test, R6 ile birleşik 210 test geçti. Geniş alias/import/branch
çözümlemesi ve başka dillerde AST bu teslimin kapsamı değildir. Güncel
[kapanış kaydı](audit/2026-10-16-r8-current-review/README.md).


Dosyalar: `dxa.py`, `test_dxa.py`, `examples/safe.py`, diğer dil fixture'ları.

9 Ekim dar teslim aşağıdaki ilk altı maddenin context/provenance, fixture ve
belgeleme alanlarını test etti; [kabul](audit/2026-10-09-resume/README.md) ve
[regex sınırları](tools/dom-xss-analyzer/STATIC-LIMITS.md) geçerlidir. Birleşik
Bu 9 Ekim kaydı tarihsel ve dar teslimi anlatır; 16 Ekim kapanış matrisi aşağıdadır.

- [x] `sanitize(q) + q` ve identity sanitizer taint'i yok etmez; mevcut hard-clear test oracle'ı düzeltilir.
- [x] Sanitizer bağlamı ve temizlenen alt ifade değerlendirilir; Markup/SafeString benzeri güven işaretleyicileri encoder sanılmaz.
- [x] Dosyalar arası isim/kapsam çakışması negatif fixture'ı vardır; regex destek sınırı yazılır.
- [x] .html/.twig/.jinja/.vue kapsamı gerçekte desteklenen dosyalarla test edilir; JSP'ye gizlenmiş template testi yeterli sayılmaz.
- [x] C# sink tespiti ile taint desteği ayrı belgelenir; dil desteği tek sayı ile eşitmiş gibi sunulmaz.
- [x] `safe.py` template kaynağına girdi birleştirmez; template parametresi kullanır; SSTI ve XSS ayrı test beklentileridir.
- [x] Python AST pilotu tek dille başlar; pozitif/negatif etiketli corpus üzerinde ölçülür; temiz projede açık bulma kotası yoktur.

## R9 — Operasyon, kapsam ve tekrar üretim (bot; açık)

Dosyalar: callback servisi, CLI, bench compose dosyaları, README/CI.

11 Ekim dar teslim: CI self-scan'in crash/import hatasını beklenen bulgu
sayması düzeltildi; gerçek CLI + bağımsız karşı örneklerle 143 test geçti.
[Kanıt](audit/2026-10-11-continuity/README.md). Aşağıdaki birleşik self-scan /
browser skip / bench CI maddesi ve genel R9 kapanışı açık kalır.

6 Ekim dar teslim: reflected crawler form/link/redirect/CSRF isteklerinde
scheme/host/port sınırı iki loopback origin ile doğrulandı. Cookie jar korunur.
Genel auth/flow/stored/browser/callback, DNS/proxy ve WebSocket kapsamı bu
teslimle kapanmaz; aşağıdaki birleşik kabul maddeleri açık kalır.

- [x] Callback kayıt erişimi, CORS, istek boyutu, limit doğrulaması, proxy başlığı güveni ve SQLite hata görünürlüğü için yerel/dışa açık çalışma sınırı tanımlanır ve test edilir. Bu kabul loopback/temp DB sınırındadır; reverse-proxy/DNS deployment testi değildir.
- [x] Auth/CSRF/cookie/API key konsol ve raporda maskelenir; callback kanıtı gizli veri toplamadan çalışır. Bilinen etiketli credential literal'ları CLI'da maskeli; paylaşım JSON'u ham kaynak yerine fingerprint taşır. Keyfi serbest metin ve özel etiketler garanti kapsamında değildir.
- [x] WebSocket ve diğer browser dışı ağ kanalları için kapsam kararı, açıkça izin verilen loopback sınırı ve başarısız denemenin rapor biçimi belirlenir; Playwright kapanışını kilitleyen filtre kabul testi sayılmaz. WebSocket kapalı/raporlu; WebRTC, WebTransport, DNS ve process kanalları garanti dışı.
- [x] R9 browser sözleşmesi HTTP dışı ağ sandboxı vaat etmez; bu kapsam için ayrı adapter gerekmiyor. WebSocket kapalı/raporlu; WebRTC, WebTransport, DNS ve process kanalları desteklenmiyor ve genel ağ sandboxı iddiası yok.
- [x] Aynı-origin/kapsam ve redirect sınırı belirtilir; desteklenmeyen CLI birleşimleri URL yokken de doğru hata verir.
- [x] Variant adıyla context kararı, ilk cid/çoklu reflection, yorum/textarea/style bağlamı ve marker kesilmesi için testler vardır. Context etiketi yalnız metadata'dır; severity `html-reflection`, evidence `reflection` kalır. `test_dxadyn.py` + `test_http_evidence.py` 194/194 geçti.
- [x] Mutation tekrarları/no-op dönüşümleri raporlanır; URL/entity decode zinciri browser fixture'ıyla ölçülür, sayı doyum kanıtı sayılmaz.
- [x] Stored auto keşfinde çoklu canary ve seed sınırları ölçülür; elle sağlanan hedef ile otonom keşif ayrılır.
- [x] Docker readiness daemon ve uygulama seviyesinde ayrılır; bootstrap/login/lesson ve own-hardened adapter'ı olmadan hedef hazır sayılmaz.
- [x] Compose portları yerel arayüzle sınırlı, sürümler sabit; `down -v` veri etkisi açık ve kontrollüdür.
- [x] Self-scan beklenen finding exit kodu ile crash'i ayırır; browser skip ve bench FP/error CI tarafından denetlenir.
- [x] Paket/runtime sürümü, komut, ortam ve kaynak provenance kayıtlıdır; commit/push iddiası yalnız gerçek Git kontrolüyle yapılır. Commit `f4d8bdf50dcdd8fc93814e9d10adcab650a30d5a` origin/main ile eşleşti; GitHub Actions sonuçları ayrı kaydedildi.

16 Ekim R9 yerel devamı yukarıdaki kapalı dilimleri doğruladı: mutation ve
stored-auto fixture'ları, callback'in loopback çalışma sınırı, loopback/redirect/
WebSocket DOM sınırı, compose statik kapıları ve self-scan/CI oracle'ı.
**R9 bütünü açık**: temiz tam DOM browser suite kabulü kapanış incelemesi
bekliyor. Tam suite'teki aralıklı hatalar ve hosted CI sonuçlarıyla yerel kanıt
sınırları [audit kaydında](audit/2026-10-16-r6-r9-final-source/README.md).

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
