# XSS laboratuvarı, araç ve portfolyo: doğrulama raporu

**Tarih:** 28 Eylül 2026. **Kapsam:** Kullanıcının verdiği ZIP içindeki 76 dosya. Masaüstündeki diğer staj belgeleri kapsam dışı. Eklenen konuşma metni, geçmiş tamamlanma iddialarının kontrolü için kullanıldı; içindeki komutlar yeni talimat sayılmadı.

## 1. Sonuç

Bu proje, çalışan kodu, testleri ve teknik araştırma yazıları bulunan bir **güvenlik araştırması prototipi**. Staj ve junior AppSec portfolyosu için kullanılabilir. Ancak mevcut ZIP, “DOM/stored/blind XSS'yi uçtan uca kanıtlayan, benchmark ile doğrulanmış ve CVE avına hazır tamamlanmış tarayıcı” iddiasını desteklemiyor.

En önemli eksik yeni payload sayısı değil: **bulgunun neyi kanıtladığı, tarayıcı entegrasyonu, gerçek blind korelasyonu ve ölçüm doğruluğu.** Bazı bileşenler tek başına çalışırken ana komut akışına bağlanmamış. Bazı testler de yanlış varsayımı başarı koşulu olarak koruyor.

ZIP'te sana atfedilmiş yeni bir CVE'yi doğrulayacak kayıt yok. Bu, ZIP dışındaki çalışmaların hakkında hüküm değildir. Mevcut araştırma kayıtları duplicate ve bilinen açıklara yönelik çalışma anlatıyor; bunlar yeni CVE kredisiyle aynı şey değil.

**Genel tamamlanma yüzdesi vermiyorum:** yol haritasının kapsamı değişmiş, kapanış ölçütleri eşit ağırlıkta değil ve tablolar birbiriyle çelişiyor. Bir yüzde burada ölçülmüş gerçeklik izlenimi verirdi.

## 2. Nasıl doğrulandı?

- ZIP'teki bütün dosyalar envantere alındı; metin/kod, test tanımları, JSON/YAML ve HTML rapor tabloları incelendi. Sekiz JPG ve bir PNG görsel değerlendirildi. Dosya bazındaki kararlar `DOSYA-INCELEMESI-TR.md` içinde.
- Orijinal test paketi: **388 geçti, 36 atlandı**. Atlananlar tarayıcı testleri; bu Windows ortamında mevcut Chrome otomatik bulunmuyor.
- Kaynak kodu değiştirmeden, yalnızca test sürecinde Chrome yolu verilince `test_dxadom.py`: **73 geçti**. Bunun 37'si ilk çalışmayla örtüşüyor. Böylece **424 ayrı mevcut test iki çalışmanın toplam kapsamıyla geçti**; bunu tek çalışmada varsayılan kurulumla 424 geçti diye sunmamak gerekir.
- Testler Python 3.12, ayrı denetim bağımlılık dizini ve mevcut Chrome 154.0.8037.58 ile çalıştırıldı. Pytest cache yazma uyarısı var; test başarısızlığı değil.
- Mevcut testlerden bağımsız, yerel mock/loopback kontrolleri ve gerçek Chrome denemeleri yapıldı. Bulgular `audit-checks.json` ve `browser-checks.json`; tekrar üretim kodu `audit_checks.py` ve `browser_checks.py` içinde.
- Gerçek Bludit/DVWA/WebGoat Docker uygulamaları bu denetimde başlatılmadı. Geçmiş özel projeler ZIP'te olmadığı için geçmiş hedef taramalarını yeniden çalıştırmak mümkün değildi. Üçüncü taraf hedef taraması yapılmadı.
- ZIP Git geçmişini içermiyor. Konuşmadaki commit/push iddiaları ve tarihsel test sayıları bu arşivden doğrulanamaz; bugünkü kodun varlığı doğrulanabilir.

## 3. Aşamaların gerçek durumu

“Uygulandı” kodun bulunması; “tamamlandı” belirtilen bitiş ölçütünün kanıtıyla sağlanması demektir.

| Aşama | ZIP'in desteklediği durum | Açık kalan konu |
|---|---|---|
| 0.1 Sink tekrarlarını azaltma | Uygulanmış, testli | Gerçek hedefteki eski/yeni karşılaştırma bağımsız tekrar edilemiyor. |
| 0.2 Ret/engelleme kayıtları | Uygulanmış | Her akışta aynı kapsam yok; flow ve tarayıcı akışları ayrı davranıyor. |
| 0.3 Sanitizer sezgisini düzeltme | **Kısmi; yeniden açılmalı** | Bilinen sanitizer yanında ham girdi kalınca taint tamamen silinebiliyor. |
| 0.4 Dosyalar arası basit taint | Regex tabanlı prototip | Modül/import çözümü ve gerçek kapsam analizi yok; isim çakışmaları mümkün. Bludit/Juice Shop ek bulgu DoD'si gösterilmemiş. |
| 0.5 Benchmark | **MVP iskeleti** | 20 hedef, doğrulanmış rakip karşılaştırması, doğru FN/FP hesabı ve yayımlanan CI geçmişi yok. |
| 1.1 Eşzamanlılık/rate/jitter | Uygulanmış; düzeltme gerekli | 0 < rate < 1 kilitlenmesi; paylaşılan header/CSRF ve stored okuma-yazma yarışları. |
| 1.2 Payload kütüphanesi | **Sayı hedefi revize edilerek uygulanmış** | 50 varyant, 18 dönüşüm; 950 üretim, 895 benzersiz normalize dize. Gerçek etki/bağlam ve hedef DoD'si doğrulanmamış. |
| 1.3 Workflow | JSON akış motoru var | HTTP hata ve eksik değişken kontrolü, verdict Content-Type tutarlılığı eksik; gerçek wallet zinciri kanıtı yok. |
| 1.4 CSRF yenileme | HTTP yardımcı akışında var | Paralel yenileme+gönderim tek işlem değil; flow/DOM ile birleşik davranış yok. Rails/Laravel hedef kanıtı yok. |
| 1.5 Macro auth | Uygulanmış, doğrulama hatalı | Başarısız giriş sonrası `Bearer None` ile authenticated=True olabiliyor. Üç gerçek hedef konfigürasyonu yok. |
| 2.1 Playwright | **Çalışan MVP** | Windows Chrome keşfi yok; belgede önerilen `dxa[browser]` paketlemesi ZIP'te yok. |
| 2.2 DOM sink tespiti | **Kısmi gözlemci** | Canary enjeksiyonuyla bütünleşmiyor; href hook çalışmıyor, eval davranış değiştiriyor, iframe/gecikmeli sink kaçıyor. |
| 2.3 JS çalıştırma kanıtı | **Tamamlanmamış** | Her dialog “PROVEN-EXECUTABLE”; taranan payload/cid ile ilişki aranmadığı için yanlış pozitif var. |
| 2.4 SPA keşfi | Rota çıkarıcı yazılmış | Bulunan rotalar tarama kuyruğuna eklenmiyor; çıktı olarak gösteriliyor. |
| 2.5 CSRF/auth header tespiti | Header gözlemcisi yazılmış | Sonraki gönderimlerde otomatik tekrar kullanım yok. |
| 3.1 Callback sunucusu | Yerel MVP çalışıyor | Callback kaydı tek başına JS kanıtı değil; dışa açık kullanım için erişim/veri sınırları eksik. |
| 3.2 Blind payload ailesi | Beş varyant uygulanmış | Görünmeyen sink'e gönderilen canary için bağımsız kalıcı takip eksik. |
| 3.3 Blind korelasyon/rapor | **Kısmi; temel anlam hatası var** | Yansıma bulunmadan callback bulguya dönüşmüyor; normal HTTP isteği XSS kanıtı sayılıyor; istenen dinamik JSON çıktı yok. |
| 4 AST analizi | Başlanmamış | Doğru biçimde queued; altı dilde sound analiz kapsamı aşırı geniş. |
| 5 Recon genişletmesi | Plan aşaması | Bazı mevcut link/form keşifleri var; planlanan alt alan/wordlist/bundle keşfi yok. |
| 6 Ürünleştirme | Plan aşaması | Mevcut CI, planlanan SARIF/config/plugin/paket/Marketplace teslimatı değildir. |
| 7.0 CVE altyapısı | **Compose ve runner iskeleti** | Login, uygulama kurulumu, doğru endpoint ve gerçek corpus çalıştırması eksik. |
| 7.1 Sistematik tarama | Kanıtı yok | Sprint `results.md` ve hedef notları arşivde yok. |
| 7.2–7.3 Yeni hedef/disclosure | Kanıtlanmış sonuç yok | Sprint planı var; yeni gönderim, kabul, advisory/credit kaydı yok. |

Roadmap'in ayrıntılı tablosu 0–3'ü DONE gösterirken son bölüm hâlâ Phase 1 için 1/5, sınıf açıkları için 0/3 ve m3/40 varyant yazıyor. Bu eski bloklar temizlenmeden tek bir doğru durum görünmüyor. README'deki 101 test/5 varyant gibi değerler de güncel değil. Phase 0–3 için vaat edilen ayrı güncel writeup'lar yok; 11 mevcut yazı daha eski gelişim anlatısını taşıyor.

### Önceki konuşmadaki m4/m5 kararı doğru muydu?

**İki yapay mutation eklememek doğru bir kapsam kararı.** Ayrı m5'in m4'e katılması da makul. Ancak `len == 18` testi “pratik doyum” ya da saldırı başarısı kanıtı değildir. “Artık sonraki işlere yaramaz” fazla kesin: iyi bağlam örnekleri DOM/blind doğrulama testlerine katkı verir; sırf sayıyı artırmak katkı garantilemez.

50 × (1+18) = 950 hesabı doğru. Fakat 55 üretim normalize edildiğinde tekrar ediyor; 895 benzersiz dize var. İki attribute varyantında 18 dönüşümün hiçbir etkisi yok. Bu sayı 950 farklı çalışan exploit anlamına gelmiyor. Bludit'te üç ayrı varyant ve Juice Shop artışı gibi özgün bitiş ölçütlerinin yerine geldiğini gösteren sonuçlar bulunmuyor. Dolayısıyla **“kütüphane genişletmesi kapandı” denebilir; “Phase 1 tamamen doğrulandı” denemez.**

## 4. En önemli teknik bulgular

### P1 — XSS kanıt etiketleri güvenilir değil

`dxadyn.py:2326–2370`: `--dom` ayrı bir erken dönüş dalı. Sayfayı ziyaret ediyor; stored/flow/auth-flow birleşimini desteklemiyor. Canary enjekte edip taranan bulguyu tarayıcıda doğrulayan ortak bir işlem hattı yok. `sink_hits_for()` ve `dialog_hits_for()` yardımcıları mevcut ama CLI bunlarla kanıt ilişkilendirmiyor.

**Gerçek tarayıcı deneyi:** Hiç enjeksiyon yapılmayan yerel sayfadaki `alert('Welcome to the demo')`, CLI'da `[PROVEN-EXECUTABLE]` oldu. Bu doğrudan yanlış pozitif. Normal uygulama dialog'u, test payload'ının çalıştığının kanıtı olamaz.

`dxadyn.py:945`: adı `-breakout` ile biten varyantlar, marker ham kaldığında bağlamın gerçekten kırıldığını göstermeden executable yükseltmesi alıyor. Örneğin title içindeki img biçimi title'ı kapatmıyorsa HTML metni olarak kalabilir. Mutasyon eklenen adlar aynı suffix kontrolüne girmediğinden etiket ayrıca tutarsızlaşır. Marker korunması ile JavaScript yürütülmesi ayrılmalı.

**Gerekli kapanış:** Ortak finding şeması; kaynak/sink/bağlam kaydı; zararsız tekil canary ile ilişkili execution olayı; negatif kontrol; stored ve auth oturumunun aynı tarayıcı doğrulamasına bağlanması. Kanıt gelmeyen kayıt “aday/ham yansıma/sink erişimi” olarak kalmalı.

### P1 — Blind XSS hem yanlış pozitif hem yanlış negatif üretiyor

`dxadyn.py:1147,1174,1358`: korelasyon yalnızca önceden oluşturulmuş yansıma bulgularını dolaşıyor. Gerçek blind durumda gönderim kullanıcıya geri yansımayıp yalnız yönetici ekranında açılırsa, canary için finding oluşmadığından callback değerlendirilmez.

**Tekrar üretim:** Callback sunucusunda eşleşen bir hit vardı; stored kontrol sayfasında yansıma yoktu. Sonuç: **callback=1, finding=0, yükseltme=0**.

Ters yönde sıradan bir HTTP GET kaydı `proven-blind` oldu. **Chrome'da JavaScript tamamen kapalıyken img yüklemesiyle callback geldi.** Dolayısıyla img/iframe/resource isteği JS çalıştığını kanıtlamaz. UA/IP/Referer de tek başına “başka kullanıcının oturumu” kanıtı değildir. HTML raporundaki bu kesin ifade düzeltilmeli.

**Gerekli kapanış:** Yansımalardan bağımsız gönderilmiş-cid kaydı; sonradan tekrar ilişkilendirme; “kaynak isteği görüldü” ve “JavaScript canary olayı doğrulandı” ayrımı. Callback kanıtı için cookie toplamak gereksiz; `blind-fetch` içindeki cookie aktarımı yerine zararsız kimlik sinyali yeterli.

### P1 — Tarayıcı gözlemcisi hedefi değiştiriyor veya olay kaçırıyor

`dxadom.py:158`: global eval wrapper'ı doğrudan eval'in yerel kapsam davranışını değiştiriyor. Yerel değişkeni okuyan test sayfası normalde **42**, hook ile **localSecret is not defined** üretti. Gözlemci uygulamayı bozarsa tespit sonucunu da değiştirebilir.

`dxadom.py:182`: href setter `Location.prototype` üzerinde aranıyor. İncelenen Chrome'da descriptor doğrudan `location` üzerinde ve non-configurable; prototype üzerinde yok. Hook sessizce takılmıyor; testte href sink kaydı boş.

`BrowserSession.visit()` ana sayfanın yüklenme sonrası anlık kaydını topluyor. 500 ms gecikmeli sink ve alt iframe'deki sink kontrollü testte kaçtı. Açık jQuery `.html()` hook'u yok; bazı çağrıların innerHTML'ye dolaylı ulaşması eşdeğer kapsam garantisi değil. Her ziyarette yeni sayfa açılması oturum/uygulama durumunu sürdürmek açısından da ele alınmalı.

### P1 — Auth/flow yanlış başarı bildiriyor

`dxadyn.py:1950,2057`: HTTP 401/403 ve eksik JSONPath değeri kesin başarısızlık olarak doğrulanmıyor. Kontrolde eksik token, **Authorization: Bearer None** oldu ve `authenticated=True` döndü. Cookie varlığı da giriş öncesi cookie'den ayrılmalı.

Flow verdict dalı response Content-Type bilgisini genel severity kapısına taşımıyor. `application/json` içinde ham marker dönen yerel akış, **[EXECUTABLE]** yazdırdı. Aynı veri normal dinamik akışta JSON-only olarak ayrılmalıydı. Flow modunun çıkış kodu/rapor üretimi de ortak bulgu davranışıyla uyumlu değil.

**Gerekli kapanış:** Beklenen durum kodu ve auth sonrası bilinen oturum kontrolü; zorunlu değişkenin bulunmasını şart koşma; flow, HTTP ve DOM için tek verdict/çıktı mantığı.

### P1 — “Sanitized” sezgisi gerçek kaçırmayı testle koruyor

`dxa.py:585`: RHS içinde bilinen sanitizer adı görünmesi, yanındaki ham taint'i de temizleyebiliyor. `DOMPurify.sanitize(q) + q` örneğinde `q` tainted kaldı fakat `out` tainted olmadı. Sadece girdiyi geri döndüren `sanitize(x){return x}` adı da güven sinyali sayılabiliyor.

`test_dxa.py:336` içindeki `test_known_safe_funcs_hard_clear_even_if_residual_looks_tainted` bu davranışı özellikle bekliyor. Bu yüzden tüm testlerin yeşil olması doğruluk için yeterli değil. Sanitizer adı, kullanım bağlamı ve işlemin hangi alt ifadeyi temizlediği ayrı incelenmeli.

Ek sınır: `iter_files()` bazı template uzantılarını (.html/.twig/.jinja/.vue) seçmiyor; pattern varlığı gerçek dosya kapsamı demek değil. Thymeleaf testinin JSP uzantısı kullanması gerçek .html taramasını sınamıyor. C# desteği ile tam taint desteği aynı şey değil.

### P1 — Benchmark güvenilir performans ölçmüyor

`bench/run.py:264`: beklenen 3, bulunan 1 için **TP=1, FN=0** hesaplanıyor; sayım temelli aynı semantikte FN=2 olmalı. Daha sağlam yaklaşım sayıdan önce beklenen benzersiz bulgu kimliklerini eşlemek.

`_parse_dxadyn()` crash metnini `ok=True` sayabiliyor; JSON-only adayını XSS başarısı olarak sayan kontrol de geçti. DOM sayısı sabit 0. Hedefte stored beklentisi varsa runner yalnız stored yoluna giriyor; aynı hedefteki reflected/DOM beklentileri ölçülemiyor.

Corpus **3 mock + 3 Docker tanımı**. Planlanan 20 hedef yok; sprintte yazan own-hardened hedefi tanımlı değil. Docker satırları gerçek login/bootstrap/security level ve doğru gönderim/okuma URL'lerini içermiyor. Compose dosyasının bulunması çalışır XSS regresyonu demek değil.

CI browser işi `continue-on-error: true`; tüm browser testleri skip olsa bile zorunlu kanıt oluşmuyor. Benchmark strict modu FP artışını söz verilen biçimde kapatmıyor. Nightly/public trend/rakiplerin doğrulanmış sonuçları yok. Self-scan shell adımı sıfır çıkışta başarısız olur, ancak beklenen bulgu kodu ile crash gibi başka nonzero kodlarını ayırt etmiyor.

**Gerekli kapanış:** Bulgu kimliğiyle TP/FP/FN; scan-error ve skipped ayrı; JSON-only başarı sayılmasın; her sınıf için gerçek hedef akışı; CI'da gerekli browser testlerinin çalıştığının ve artifact saklandığının kontrolü.

### P2 — Payload üretimi, gönderim ve hız sınırı

- `_submit_json()` (`dxadyn.py:1490`) yalnız ters slash ve çift tırnak kaçırıyor. Kontrol karakterleri JSON string olarak doğru serialize edilmiyor. Basit `{CANARY}` string şablonunda **950 üretimin 336'sı geçersiz JSON** oldu. Bu sayı o şablon/parametre setine aittir; tüm isteklerin evrensel hata oranı değildir.
- Rate limiter kapasitesi doğrudan rate. **0.5 request/s** için token en fazla 0.5 oluyor ama gönderim 1 bekliyor; simülasyonda 10 saniye sonra hâlâ bekliyor. Fractional rate desteklenecekse kapasite en az 1 olmalı veya değer açıkça reddedilmeli.
- `_fetch_json()` paylaşılan EXTRA_HEADERS'ı değiştiriyor. Paralel görevlerde Content-Type ve oturum/CSRF durumları karışabilir. Stored hedef son kaydı üzerine yazıyorsa paralel submit/check farklı canary'leri kaybedebilir. Bunlar koddan görülen yarış riskleri; gerçek hedefte hata sıklığı ölçülmedi.
- Chrome HTML parse kontrolünde URL-encoded biçimler metin kaldı; split-comment biçimleri orijinal etikete dönüşmedi. `%00` gerçek NUL değil. Dönüşümler olası uygulama decode zincirlerini test edebilir, ancak doğrudan modern tarayıcı XSS etkisi gibi sunulmamalı.

### P2 — Kullanım ve çıktı sınırları

`--dom` dalı auth/cookie/header ayarlarının normal işlenmesinden önce dönüyor; algılanan header'lar yazdırılıyor ama otomatik replay edilmiyor. Kimlik bilgilerini konsola basmak yerine maskeleme gerekir. Callback servisi localhost için MVP; `/hits` erişimi ve geniş CORS, sınırsız okuma/istek boyutu davranışları nedeniyle doğrudan herkese açılacak servis olarak sunulmamalı. SQLite hata yutma ve doğrulanmamış proxy başlıkları kanıt kalitesini zayıflatabilir.

Compose portları yalnız 127.0.0.1'e bağlanacak biçimde sınırlandırılmalı; demo uygulamalar kasıtlı zayıf. Runner'ın `down -v` davranışı da laboratuvar verisini temizler ve açıkça belgelenmeli. Bu denetimde Docker çalıştırılmadı.

## 5. CVE durumu

| İddia | Değerlendirme |
|---|---|
| Yeni CVE kazandım / bu bot yeni CVE buldu | ZIP desteklemiyor. Roadmap'in eski özeti de credited novel CVE=0 diyor. |
| Patchstack tarafından doğrulanmış duplicate | `research/README.md` anlatıyor; maskelenmiş kabul yanıtı, kayıt numarası, tarih/ürün/sürüm yok. **Yazar beyanı; bu ZIP ile bağımsız doğrulanamadı.** |
| Bilinen SQLi'yi yeniden buldum | Araştırma metninde var; advisory kimliği ve yeniden üretim paketi olmadığı için bağımsız doğrulama sınırlı. |
| Bludit çalışması CVE-2026-4420 ile ilgili | Resmî kayıt var; yerel raporun o kök nedenle tam eşleşmesi sürüm/sink/PoC ile ayrıca kurulmalı. |
| v5.1 bütün XSS sınıflarını browser proof ile kapattı | Kod ve karşı örnekler nedeniyle yanlış. Sprint giriş metni düzeltilmeli. |

CVE-2026-4420 için CERT Polska 7 Nisan 2026 tarihli kayıtta **3.17.2 ve 3.18.0** sürümlerini doğruluyor ve **Yassin Abdelrazek** adına kredi veriyor. ZIP'in 3.16.2 deneyi bu duyurunun doğruladığı sürümler arasında değil; bundan 3.16.2 güvenlidir sonucu da çıkmaz. Duyuru diğer sürümlerin test edilmediğini belirtir. Yerelde uygulanan fix, yayımlanmış vendor fix'i olarak sunulmamalı. [Resmî duyuru](https://cert.pl/en/posts/2026/04/CVE-2026-4420/).

Sprintteki “non-WordPress hedefte Patchstack-valid bulgu” minimum hedefi, genel Patchstack Bug Bounty programının WordPress core/plugin/theme kapsamıyla uyumsuz. Ayrı bir VDP/program açıkça o ürünü kapsamıyorsa doğru vendor/CNA kanalı seçilmeli. Eski sürüm regresyonu ile güncel sürümde yeni açık araştırması ayrılmalı. [Patchstack program kuralları](https://patchstack.com/articles/bug-bounty-guidelines-rules/).

CVE çalışmasına başlamak için bütün roadmap'i bitirmek gerekmez. Kaynak incelemesi, yetki sınırı, temiz kurulumda bağımsız PoC ve doğru disclosure kanalı gerekir. Araç şu anda aday üretimine yardımcı olabilir; kendi `PROVEN` etiketleri insan doğrulamasının yerine geçemez. “Tek eksik timing” açıklaması da bu teknik eksikleri hesaba katmadığı için doğru değil.

## 6. Staj yazıları ve raporlar

ZIP'teki içerik bir **teknik çalışma günlüğü / vaka arşivi**. Gün/görev/onay gibi resmî staj defteri şartlarını bu kapsamda değerlendirmedim; kullanıcı dış PDF'leri özellikle kapsam dışında bıraktı.

| Yazı | Korunacak değer | Düzeltilecek iddia/kanıt |
|---|---|---|
| 01 Filtering is not protection | Header kaynağını takip ve filtre davranışı | Ekran görüntüleri başarılı JS yürütmesini göstermiyor. “Confirmed” sonuç için son kanıt eksik. Tekrarlı sanitizer'ı genel güvenlik çözümü gibi sunma. |
| 02 DOM XSS assessment | Negatif araştırma sürecinin belgelenmesi | Dinleme sırasında mesaj görülmemesi kaynağın erişilemezliğini kanıtlamaz. createHTML kullanımı enforcement kanıtı değil; frame-src script yürütme politikası değildir. “İncelenen yolda bulgu yok” sınırında kalmalı. |
| 03 SQL injection | Lab bulgusu ve savunma bağlantısı | Gösterilmeyen UNION/blind senaryolar teorik olarak açıkça ayrılmalı; yorumla keyword bölme her SQL parser'da çalışmaz. |
| 04 JWT forgery | Başarılı/başarısız deneyleri ayırma | RS/HS başarısızlığının newline sebebi kanıtlanmadıysa hipotez olarak kalmalı. Public key format terminolojisi netleştirilmeli. |
| 05 IDOR/BOLA | Nesne sahipliği ve authorization açıklaması | İki farklı kullanıcıyla aynı nesne için kontrol çifti eklenmeli. Yatay erişim, kanıtsız admin privilege escalation gibi sunulmamalı. |
| 06 Building a bot | Araç geliştirme hikâyesi | Kullanıcının verdiği seed/endpoint'in sağladığı keşif ile otonom keşif ayrılmalı; tarihsel özellik/sayılar versiyonla etiketlenmeli. |
| 07 Teaching login | Oturumlu test yaklaşımı | Sıfır HIGH güvenli uygulama demek değil. Sanitizer adı tanıma, fonksiyon gövdesini analiz etmek değildir. Bludit OWASP projesi diye adlandırılmamalı. |
| 08 What does not shout | JSON-only ayrımı, olumsuz sonuç disiplini | JSON'da ham veri tek başına HTML injection/XSS değil; son HTML sink gerekir. Çok sayıda URL aynı kök neden veya farklı politika olabilir. |
| 09 Three HIGH to one | Duplicate temizliği ve mühendislik günlüğü | Üçten bire düşüş tek başına precision artışı ölçmez. Sanitizer sezgisi FN yaratıyor; bir kalan HIGH da doğrulanmış XSS değil, inceleme adayı. |
| 10 One shape was never enough | Bağlam çeşitliliği motivasyonu | Dönüşüm sayısı, marker korunması ve executable ayrılmalı. Byte dönüşümünü tarayıcının gerçekten parse ettiği yapıyla doğrulamak gerek. |
| 11 Four targets | Ham HTML raporlarını saklaması | **75 JSON-only yanlış; dosyalarda 50 var.** B hedefinde 25 bulgu yok. Bludit executable etiketi tek başına browser proof değil. |

### HTML raporlarının gerçek sayımı

| Dosya | Gerçek bulgu satırı | Anlamı |
|---|---:|---|
| A-hotel-platform-25shape | 25 | JSON-only kayıt; 25 bağımsız XSS değil. |
| B1-mahrem-static | 78 | Statik MEDIUM aday; 78 doğrulanmış açıklık değil. |
| B2-mahrem-reflected | 0 | Tablodaki “No findings” satırı sonuç açıklaması. |
| C1-wallet-reflected | 0 | Aynı şekilde bulgu yok. |
| C2-wallet-stored-25shape | 25 | JSON-only kayıt. |
| D1-bludit-body-breakout-req | 1 | Breakout-required aday. |
| D2-bludit-title-breakout-EXECUTABLE | 1 | Aracın executable sınıflandırması; bağımsız JS proof yok. |

Bu sette **50 JSON-only + 2 Bludit dinamik kayıt**, ayrıca 78 statik aday var. Bunları toplayıp “130 açık” demek de yanlış olur. Aynı kök neden/varyant tekrarları ayrılmalı. HTML raporlarında varyant alanının görünmemesi 25 satırlık sonuçları okuyucu için belirsizleştiriyor. `parsed-reports.json` ham tablo sayıları boş-tablo açıklama satırlarını da içerir; yukarıdaki tabloda bunlar ayıklandı.

### Ekran görüntüleri neyi gösteriyor?

- 01: Bazı Juice Shop challenge başarı bildirimleri; bütün scoreboard ya da tüm anlatılan XSS/JWT aşamaları değil.
- 02: Profil alanları; gerçek CSP response header'ı veya başarılı CSP bypass değil.
- 03, 07, 08: Payload denenmiş, ilgili lastLoginIp boş dönmüş. Filtre/ret davranışı kanıtı; successful bypass kanıtı değil.
- 04: Burp HTTP geçmişi; çalışma sürecini destekliyor.
- 05: Last Login IP arayüzü; execution kanıtı yok.
- 06: `True-Client-IP: 1.2.3.4` değerinin kaydedildiği görülüyor. Kaynak kanalının doğrulanması için en net görsel.
- `report-preview.png`: Tarihsel statik rapor örneği; güncel bot yeteneği/precision ölçümü değil.

Bu sınırlar “yapılmadı” demek değil; **arşivdeki kanıt, anlatılan sonucun tamamını bağımsız doğrulatmıyor** demek. Burp görsellerindeki lab token/cookie/hash alanları yayımlanırken maskelenmeli; burada canlı hesap sızıntısı varsayılmıyor.

Savunma anlatısında bağlama uygun çıktı kodlama, gerektiğinde bakımı yapılan HTML sanitizer ve güvenli DOM API'leri esas olmalı. HttpOnly tek başına XSS'yi ya da kullanıcının yetkisiyle işlem yapılmasını önlemez; CSP ilave savunmadır. [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html).

## 7. Portfolyoda gereksiz olan ne?

**76 dosyanın varlığı sorun değil.** Asıl risk aynı başarıyı farklı yazılarda büyüterek tekrar etmek ve deneysel parçaları tamamlanmış ürün gibi sunmak.

**Koru:** Kaynak kodu, anlamlı testleri, mock hedefleri, karşı örnekleri, SQLi/JWT/BOLA lab yazılarını, ham raporları ve dürüst duplicate/olumsuz sonuç kayıtlarını. Bunlar çalışmanın izini gösteriyor. Dosya silmek yerine güncel ana sayfadan tarihsel arşive bağlantı ver.

**Öne çıkar:** Üç vaka: (1) bir uçtan uca kaynak→sink→zararsız browser proof→fix→retest, (2) ölçülmüş FP/FN üzerinden araç düzeltmesi, (3) oturum/authorization veya disclosure süreci. Diğer yazılar gelişim arşivinde kalsın. 06–10'u ayrıca beş eşdeğer büyük başarı gibi sunmak yerine tek araç geliştirme serisine bağla.

**Şimdilik ertele:** Yeni mutation sayısı hedefleri; altı dili aynı anda AST'ye taşıma; genel subdomain/dizin brute-force motoru; IoT yönüne genişleme; plugin API ve Marketplace yayını; sonuçtan önce yıldız/kullanıcı/CVE kupası hedefleri. Bunlar kötü fikir olduğu için değil, mevcut doğrulama açığını kapatmadığı için düşük öncelikli.

**Erteleme:** Tek kurulum yolu, paket/sürüm bilgisi, güncel README, doğru JSON çıktısı ve kanıt alanları. Bunlar başka birinin projeyi çalıştırmasını doğrudan kolaylaştırır. SARIF, doğrulanmış bulgu modeli oturduktan sonra anlamlı.

CV/README için bugün savunulabilir ifade:

> Yetkili laboratuvar ortamlarında XSS, SQLi, JWT ve erişim kontrolü üzerine araştırma yaptım. Python ile regex tabanlı statik analiz, HTTP yansıma/kalıcılık testleri, deneysel Playwright gözlemcisi ve callback toplama bileşenleri geliştirdim. Test ve teknik vaka belgeleri oluşturdum; otomatik bulgu sınıflandırmasının sınırlarını karşı örneklerle değerlendirdim.

“950 çalışan payload”, “tüm XSS türlerini otomatik kanıtlıyor”, “DalFox seviyesinde ölçülmüş”, “yeni CVE bulmuş araç” ifadeleri mevcut kanıtla kullanılmamalı. Staj çalışmasının değeri bu abartılı ifadelere bağlı değil.

## 8. Önerilen kapanış sırası ve kabul ölçütleri

1. **Önce doğru durum kaydı.** Tek status tablosu; deneysel/kısmi/tamamlandı ayrımı; README sayıları; writeup 11'de 75→50; CVE beyanlarının kanıt düzeyi. Bitiş: bütün belgeler aynı sürümü ve sınırlamayı anlatır.
2. **Yanlış kanıtı durdur.** Dialog canary korelasyonu; callback/resource/JS ayrımı; bağımsız blind canary kayıtları; bağlamı kırmadan executable yükseltmeyi kaldır. Bitiş: normal alert, JS kapalı img, title içi ham marker negatif; gerçek kontrollü canary pozitif; görünmeyen admin sink callback'i kaybolmaz.
3. **Gönderim ve oturumu sağlamlaştır.** JSON serializer, 401/403, eksik token, auth sonrası doğrulama, fractional rate, request başına header/CSRF durumu. Bitiş: 950 örnek geçerli JSON; yanlış login kesin hata; 0.5/s ilerler; paralel testte state karışmaz.
4. **Tarayıcıyı tek bulgu akışına bağla.** Auth/stored replay, rota kuyruğu, frame/gecikme kapsamı, semantiği bozmayan gözlem. Bitiş: CLI'dan tek komutla kontrollü fixture'da submit→read→cid proof→HTML/JSON kanıtı.
5. **Küçük ama doğru benchmark kur.** Önce pozitif/negatif ve farklı bağlamları içeren az sayıda deterministik hedef; sonra bir gerçek ürün. Bitiş: eksik 2 bulgu FN=2; crash başarı sayılmaz; yanlış pozitif CI'ı düşürür; sonuç artifact'i saklanır.
6. **Tek güçlü portfolyo vakası yayımla.** Sabit hedef sürümü, tam komut, anonimleştirilmiş request/response, browser proof, negatif kontrol, fix diff ve tekrar test. Bitiş: başka biri temiz kurulumdan sonucu tekrarlar.
7. **Ardından sınırlı CVE araştırması.** Bir ekosistem/ürün, güncel kapsam/sürüm, rol ve etki doğrulaması, bilinen kayıt karşılaştırması. Yeni CVE ve ödül sonucu garanti veya bitiş yüzdesi olarak kullanılmaz.

AST'ye geçiş faydalı olabilir; önce tek dil ve açık destek sınırı seçilmeli. AST kullanmak kendiliğinden “sound” analiz sağlamaz. “Kendi güvenli projelerinde en az bir yeni açık bulmalı” bitiş ölçütü kaldırılmalı: gerçekten temiz hedefte sıfır doğru sonuçtur. Doğru hedef, etiketli pozitif/negatif fixture'larda ölçülen recall ve precision'dır.

## 9. Kanıt dosyaları

- `inventory.json`: 76 dosyanın boyutu, SHA-256 özeti, satır sayısı; test isimleri ve assertion konumları.
- `DOSYA-INCELEMESI-TR.md`: her orijinal dosya için tek tek inceleme kararı.
- `pytest-baseline.log/.xml`: 388 passed + 36 skipped.
- `pytest-browser.log/.xml`: Chrome yolu verilmiş 73 passed.
- `audit_checks.py` / `audit-checks.json`: deterministik karşı örnekler.
- `browser_checks.py` / `browser-checks.json`: gerçek Chrome karşı örnekleri.
- `parsed-reports.json`: HTML raporlarının çıkarılmış metin ve tabloları.

Orijinal ZIP ve kaynak dosyalar düzeltilmedi. Bu teslimat **denetim ve önceliklendirme** çalışmasıdır; yukarıdaki kusurlar henüz giderilmiş değildir.
