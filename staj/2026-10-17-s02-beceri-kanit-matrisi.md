# S02 — 11 yazının beceri ve kanıt matrisi

17 Ekim 2026. Amaç, mevcut 01–11 yazılarında anlatılan beceriyi o beceriyi
destekleyen dosyalarla eşleştirmektir. Ana kabul ölçütü [ROADMAP S02](../ROADMAP.md)
içindedir; bu belge yeni bir iş planı oluşturmaz. Kaynak temel
`451361b9f8faef3f328b13468d8d3f6a040c7d2c` ve çalışma ağacındaki
[son teslim incelemesi](../audit/2026-10-17-delivery-review/README.md) okundu.

Bu teslim belge incelemesidir: test, tarama, browser veya Docker koşusu
yapılmadı. Aşağıdaki paketler önceki kabul kayıtlarına bağlantıdır; bugünün
yeni test sonucu olarak sunulmaz. Çalışma saati, yeni CVE, scanner başarı
oranı veya harici hedef yetkisi çıkarılmaz.

## Okuma anahtarı

- **Teori:** Yazıdaki mekanizma ve savunma açıklaması; tek başına deney kanıtı
  değildir.
- **Tarihsel deney:** Yazarın anlattığı hedef gözlemi. Eşleşen ham kanıt yoksa
  yazar beyanı olarak kalır; ekran görüntüsündeki challenge sonucu ham HTTP
  alışverişi ve kimlik kontrolünün yerine geçmez.
- **Araç geliştirme:** Uygulama, hata ayıklama ve rapor tasarımı anlatısı.
  Güncel kaynak ve regresyon paketi beceriyi ayrıca destekleyebilir; eski
  sürümün çıktısını veya tarihsel hedef sonucunu geriye dönük doğrulamaz.
- **Mevcut kanıt:** Korunmuş dosya veya kabul kaydı. Reflection, sink gözlemi,
  callback, browser execution ve vulnerability triage ayrı değerlendirilir.

Beceri sütunu konu eşlemesidir; yazara verilmiş puan, sertifika veya deney
başarı onayı değildir. **Test** kontrol/oracle tasarımını, **hata ayıklama**
gözlemden neden ayırmayı, **raporlama** iddiayı kanıt sınırıyla yazmayı belirtir.

## Yazı → beceri → çalışma türü (11/11)

| Yazı | Beceri odağı | Teori | Tarihsel deney | Araç geliştirme | C/K bağı |
|---|---|---|---|---|---|
| [01 — Filtering isn't protection](../writeups/01-filtering-is-not-protection.md) | XSS; hata ayıklama; test; raporlama | Filtre dönüşümü, HTML sink'i, bağlama uygun encoding ve savunma sınırı | Juice Shop header→Last Login IP ve filtre gözlemleri; execution anlatısı bağımsız doğrulanmadı | Yazı araç geliştirme teslimi değil; K01 ayrı tamamlayıcı vaka | C01; K01/K02/K04 |
| [02 — DOM XSS assessment](../writeups/02-dom-xss-assessment-react-spa.md) | XSS; hata ayıklama; test; raporlama | Source→sink, erişilebilir durumlar, Trusted Types/CSP ve negatif gözlem sınırı | Anonim SPA bundle/message incelemesi yazar beyanı | Elle inceleme metodolojisi; güncel DOM observer kabulü ayrı | C02/C12; K02 |
| [03 — SQL injection](../writeups/03-sql-injection.md) | SQLi; hata ayıklama; test; raporlama | Sorgu yapısı/veri ayrımı, parametre bağlama, UNION ve blind örnekleri | Login Admin ve Academy çalışma anlatısı; eşleşen ham alışveriş yok | SQLi scanner geliştirilmiş olduğu iddia edilmiyor | C03; K03/K04 |
| [04 — JWT forgery](../writeups/04-jwt-forgery.md) | JWT; hata ayıklama; test; raporlama | `alg:none`, RS256→HS256 karışması, algoritma/key politikası | Unsigned JWT başarı beyanı; key-confusion girişimi başarısız anlatılıyor, nedeni bilinmiyor | JWT doğrulayıcı veya exploit aracı teslimi değil | C04; K03/K04 |
| [05 — IDOR/BOLA](../writeups/05-idor-bola.md) | BOLA; hata ayıklama; test; raporlama | Authentication/authorization, aynı nesnede A/B hesabı ve deny kontrolü | Basket ID değişimi ve farklı UserId anlatısı; sahiplik eşlemesi yok | BOLA tarayıcı geliştirme kanıtı değil | C05; K03/K04 |
| [06 — Building an XSS bot](../writeups/06-building-an-xss-bot.md) | XSS; hata ayıklama; test; raporlama | Statik/dinamik source→sink ve canary sınırı | Eski yerel Bludit anlatısı; execution, otonom keşif ve CVE aidiyeti doğrulanmadı | `dxa`/`dxadyn` ilk tasarımı; route seed operatör girdisi | C06/C12; K01/K05 |
| [07 — Teaching the bot to log in](../writeups/07-teaching-the-bot-to-log-in.md) | XSS; hata ayıklama; test; raporlama | Oturum, CSRF, keşif ve sanitizer sezgisi sınırı | Tarihsel Bludit/statik sayımlar; 0 HIGH güvenlik kanıtı değil | Cookie/header, JSON/header gönderim, crawl ve HTML rapor geliştirme anlatısı | C07/C12; K04/K05 |
| [08 — What does not shout](../writeups/08-what-does-not-shout-matters.md) | XSS; hata ayıklama; test; raporlama | Content-Type, bağlam, dedup ve çok URL/tek açık ayrımı | Eski JSON yanıtları ve hedef sayımları; precision ölçümü yok | Response sınıflandırma, dedup, HTTP yöntemleri ve Java heuristikleri | C08/C12; K05 |
| [09 — Three HIGH to one](../writeups/09-three-high-to-one-a-precision-journey.md) | XSS; hata ayıklama; test; raporlama | Sanitizer adı/etkisi ayrımı, FP/FN riski, labeled corpus gereği | Eski 3→1 aday azalması; kalan HIGH doğrulanmış açık değil | Heuristik ve sink-family dedup değişikliği anlatısı | C09; K05 |
| [10 — One shape was never enough](../writeups/10-one-shape-was-never-enough.md) | XSS; hata ayıklama; test; raporlama | Varyant, mutation, parser bağlamı ve execution ayrımı | Eski Bludit etiketleri; WAF bypass veya 950 çalışan exploit kanıtı yok | Payload üretimi ve tarihsel severity kuralı; güncel kanıt sözleşmesi ayrı | C10; K01/K04/K05 |
| [11 — Four targets](../writeups/11-four-targets-one-afternoon.md) | XSS; hata ayıklama; test; raporlama | Arşiv sonuçlarını Content-Type ve kanıt seviyesine göre yorumlama | Korunmuş rapor satırları mevcut; bugünkü hedef durumu ve güvenlik sonucu değil | Eski araç konfigürasyonunun vaka anlatımı; yeni geliştirme/koşu değil | C11/C13; K01/K05 |

## Yazı → mevcut kanıt → eksik kanıt (11/11)

Her satırda önce yazının kendi tarihsel dayanağı, varsa ardından bağımsız
tamamlayıcı güncel beceri kanıtı verilir. Tamamlayıcı fixture aynı ürün,
sürüm veya eski olayın tekrarı sayılmaz.

| Yazı | Mevcut kanıt ve gösterdiği sınır | Eksik kanıt / kullanılamayan sonuç |
|---|---|---|
| 01 | [K02 ekran görüntüsü envanteri](../screenshots/README.md), [maskeli yayın kopyaları](../screenshots/publication/README.md): header/alan/filtre bağlamı. Tamamlayıcı [K01 vaka paketi](../cases/k01-stored-comment/README.md) ve [browser sonucu](../cases/k01-stored-comment/evidence/2026-10-05-verified/result.json): ayrı yerel fixture'da proof/fix/negatif kontroller. | Tarihsel Juice Shop nested-tag payload'ına eşleşen browser canary, exact sürüm ve fix/retest yok. K01 bu boşluğu tarihsel hedef adına kapatmaz. |
| 02 | [Yazının kapsam notu](../writeups/02-dom-xss-assessment-react-spa.md), [C/K incelemesi](../audit/2026-10-17-k-evidence/README.md): metodoloji ve kanıt boşluğu. Tamamlayıcı [R3 browser kabulü](../audit/2026-10-06-r3-final/README.md) ayrı loopback akışını belgeler. | Hedef yetki kaydı, bundle hash/snapshot, etkin response header/policy, route/durum envanteri, message zamanı ve source→sink trace yok. Anonim SPA güvenli sayılamaz; yerel R3 sonucu bunu doğrulamaz. |
| 03 | [SQLi yazısı](../writeups/03-sql-injection.md), [K03 envanteri](../audit/2026-10-17-k-evidence/README.md) ve [scoreboard yayın kopyası](../screenshots/publication/01-scoreboard-solved-challenges.png): açıklama, yazar beyanı ve geniş challenge-UI bağlamı. | Exact hedef/sürüm, maskeli SQLi istek/yanıtı, login öncesi/sonrası kimlik, negatif kontrol, DB/parser davranışı ve fix/retest yok. UNION/blind bölümleri deney sonucu değil. |
| 04 | [JWT yazısı](../writeups/04-jwt-forgery.md) ve [K03 envanteri](../audit/2026-10-17-k-evidence/README.md): algoritma karışması açıklaması ve başarı/başarısızlık beyanlarının ayrımı. | Maskeli token alışverişi, doğrulanmış önce/sonra kimlik, exact build/verifier politikası, değişmiş imza için negatif kontrol ve fix/retest yok. RS256→HS256 başarısı veya newline/key-format kök nedeni çıkarılamaz. |
| 05 | [BOLA yazısı](../writeups/05-idor-bola.md), [K03 envanteri](../audit/2026-10-17-k-evidence/README.md), [scoreboard yayın kopyası](../screenshots/publication/01-scoreboard-solved-challenges.png): anlatı ve challenge-UI bağlamı. | A/B kimliği ve nesne sahipliği, aynı B nesnesine B ve A oturumlarıyla eşleşen istek/yanıtlar, unauthenticated/forbidden kontrolü ve fix/retest yok. Farklı UserId veya HTTP 200 tek başına BOLA kanıtı değil; vertical escalation gösterilmedi. |
| 06 | [Arşiv raporların kapsamlı özeti](../reports/publication-preview.html) eski sınıflandırmaları gösterir. Tamamlayıcı [R1 kapanış matrisi](../audit/2026-10-05-r1/R1-KAPANIS.md) güncel observation/report davranışını, [K01](../cases/k01-stored-comment/README.md) ayrı execution vakasını destekler. | Eski build'e bağlı tam submit→read→browser proof, otonom orphan-route keşif kanıtı ve vendor root-cause/fix karşılaştırması yok. Bludit/CVE eşlemesi doğrulanmış sayılmaz. |
| 07 | [Tarihsel yazı](../writeups/07-teaching-the-bot-to-log-in.md); tamamlayıcı [R2 auth/CSRF kapanışı](../audit/2026-10-06-r2/R2-KAPANIS.md) ile [R8 sınır incelemesi](../audit/2026-10-16-r8-current-review/README.md): oturum kontrolleri ve heuristik sınırları ayrı kayıtlı. | Eski Bludit koşusunun build/hash, tam kimlik/istek seti ve etiketlenmiş bağımsız oracle'ı yok. Sanitizer-name sezgisi sanitization ispatı veya 0 HIGH güvenlik sonucu üretmez. |
| 08 | [K05 envanteri](../audit/2026-10-17-k-evidence/README.md), [rapor önizlemesi](../reports/publication-preview.html) arşiv JSON/static satırlarını sınırlar. Tamamlayıcı [HTTP kanıt sözleşmesi](../tools/dom-xss-analyzer/HTTP-EVIDENCE.md) ve [regresyon kaynağı](../tools/dom-xss-analyzer/test_http_evidence.py) response sınıflandırmasını tanımlar. | Tarihsel 58 sayfası için sink/rol/kök neden oracle'ı, JSON→DOM downstream execution akışı ve temsil edici doğruluk ölçümü yok. Satır birleştirme benzersiz açık sayımı değildir. |
| 09 | [Yazının tarihsel çıktı anlatısı](../writeups/09-three-high-to-one-a-precision-journey.md), [R8 karşı örnek incelemesi](../audit/2026-10-16-r8-current-review/README.md), [K05 statik rapor envanteri](../audit/2026-10-17-k-evidence/README.md): aday, sanitizer heuristiği ve false-negative sınırları. | 3→1 öncesi/sonrası için bağımsız etiketlenmiş temsil edici corpus ve TP/FP/FN paydası yok. Kalan HIGH için execution/triage yok; precision artışı veya genel soundness iddiası yapılamaz. |
| 10 | [Tarihsel varyant yazısı](../writeups/10-one-shape-was-never-enough.md), [HTTP sözleşmesi](../tools/dom-xss-analyzer/HTTP-EVIDENCE.md), [K05 legacy etiket envanteri](../audit/2026-10-17-k-evidence/README.md). Tamamlayıcı [K01 kontrolleri](../cases/k01-stored-comment/README.md) reflection/execution ayrımını ayrı fixture'da destekler. | Eski D2 etiketine bağlı browser canary/fix-retest ve gerçek WAF bypass kontrolü yok. C10 marker/severity/parser metin düzeltmesinin kabulü koordinatör incelemesine bağlıdır; bu matris editoryal düzeltmeyi tarihsel execution kanıtına dönüştürmez. |
| 11 | [K05 envanteri](../audit/2026-10-17-k-evidence/README.md) ve [arşiv önizlemesi](../reports/publication-preview.html): 50 JSON-only satır, 78 statik aday ve iki Bludit sınıflandırması. Tamamlayıcı [R4 exact-payload replay](../audit/r4-proof-experiment-2026-10-16/README.md) ayrı raw/escaped loopback deneyidir. | Arşiv D2 için bağlı browser-proof yok; tüm eski hedeflere ait bugünkü tekrar/triage yok. R4 replay'i tarihsel scanner/browser ziyareti değildir; scanner karşılaştırma üstünlüğü, güvenlik veya yeni CVE çıkarılmaz. |

## Ortak kanıt okuma ve devam notu

Raporlama becerisi; [R1 kanıt modeli](../tools/dom-xss-analyzer/EVIDENCE-CONTRACT.md),
[HTTP modeli](../tools/dom-xss-analyzer/HTTP-EVIDENCE.md),
[browser proof sınırı](../tools/dom-xss-analyzer/BROWSER-PROOF.md),
[yöntem](../methodology.md) ve [savunma rehberi](../defense/README.md) ile
ilişkilidir (C12/C13, K04/K05). Tarihsel sürüm etiketleri bu sözleşmelerin
güncel garantisi gibi kullanılamaz.

Hata ayıklama ve test becerisi için ayrı incelenebilir örnekler; K01'in
vulnerable/fixed ve negatif kontrolleri, R8'in sanitizer/taint karşı örnekleri
ve [R9 browser fixture düzeltmesi](../audit/2026-10-16-r6-r9-final-source/README.md)
içindedir. Son mevcut kaynak koşularının completed/failed/error/skip
ayrımı [VALIDATION](../VALIDATION.md) ve
[son teslim denetimi](../audit/2026-10-17-delivery-review/README.md) üzerinden
okunur. Bu matris test sayılarından ürün doğruluğu veya bireysel yetkinlik
puanı türetmez.

**S02 belge kapsamı:** 11/11 yazı için beceri, teori/deney/araç geliştirme,
mevcut kanıt, eksik kanıt ve C/K bağı yukarıda gösterildi. 06–10 aynı araç
geliştirme serisidir; beş bağımsız başarı ölçümü sayılmaz. C10/C13 editoryal
takiplerinin kabulü koordinatöre aittir. SQLi/JWT/BOLA için bu matriste bağlı
tarihsel ham kanıt eksikleri korunur; 19 Ekim'de kabul edilen yeni loopback
tekrarı sürüm, source hash, kontroller ve sınırlamalarıyla
[K03 audit'ine](../audit/2026-10-19-k03-loopback-reproduction/README.md)
eklendi. Bu yeni yerel fixture, eski Juice Shop olayının ham kaydı olarak
sunulmamalıdır.

Bu belge S02'nin öğrenme ve kanıt eşleme teslimidir. K03 tarihsel ham kanıt,
K04 eski hedef remediation retesti ve R7 yetkili araştırma kapsamı boşluklarını
kapatmaz. ROADMAP/STATUS kabul işaretleri koordinatör incelemesiyle güncellenir.

## 19 Ekim 2026 belge kabul kontrolü

01–11 kaynak yazıları ve bağlı K02/K03/K05 envanteriyle matris karşılaştırıldı.
Her iki tabloda da 01–11 kimlikleri birer kez bulunur: **11/11 + 11/11**;
56 göreli bağlantının dosya hedefi bulundu, eksik hedef yok. Bağlantı kontrolü
dosyanın varlığını doğrular; tarihsel hedef sonucunu veya artifact'in bütün
içeriğini yeniden doğrulamaz. Maskeli ekran görüntüleri korunmuş UI/alan
bağlamıdır; çıkarılmış yanıt verisini veya A/B kimliğini ispatlamaz.

Önceki paralel görev ifadeleri kalıcı kabul sınırlarına dönüştürüldü. S02'nin
belge kabul ölçütü karşılanır: XSS/SQLi/JWT/BOLA ile hata ayıklama, test ve
raporlama becerileri; teori/tarihsel deney/araç geliştirme ayrımı; mevcut ve
eksik kanıtlar; C/K bağları iki tabloda gösterilir. Ana ROADMAP/STATUS kabulü
koordinatöre aittir. Bu kontrol yeni SQLi/JWT/BOLA paketi kabul etmez; yeni
yerel kanıt eski olayın ham kaydı sayılamaz.

Dosya henüz untracked olduğu için `git diff --check -- <dosya>` içerik
denetimi sayılmadı; ayrıca dosyada satır sonu boşluğu ve merge-conflict
işareti arandı, sorun bulunmadı. Bunlar belge kontrolleridir; uygulama testi,
CI sorgusu, tarama, browser/Docker koşusu veya geçmiş kanıtın yeniden üretimi
yapılmadı.
