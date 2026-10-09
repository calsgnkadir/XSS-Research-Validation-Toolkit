# Doğrulanmış durum

## 9 Ekim 2026 güncel teslim

8–9 Ekim değişiklikleri yeniden test edildi: **824 analyzer/bench testi + 2 ayrı
K01 HTTP testi geçti**, hata/skip yok. Gerçek Chrome strict corpus **9/9,
TP=3 FP=0 FN=0**. [Yeni kanıt](audit/2026-10-09-resume/README.md).
R4 hard timeout ve süreç temizliği yerel Windows kabulü geçti. R8 sanitizer
provenance/context ve dosya/scope düzeltmeleri, R9 callback sınırları ve Docker
veri koruma guard'ları testli. Gerçek Docker ürün kurulumu/login adapter'ı,
uzak Linux CI ve genel R4/R8/R9 kapanışı açık. Aşağıdaki 7 Ekim özeti tarihseldir.

7 Ekim 2026. Güncel plan: [ROADMAP](ROADMAP.md). Tarihsel Git teslimi: ZIP üzerinden başlayan düzeltmeler
`2703d1a` ile GitHub main dalına aktarıldı. Canlı GitHub API'si güncel README'yi
doğruladı; web arama sonuçları eski taranmış metni gösterebilir. Bu durum yeni
CVE veya tüm roadmap'in tamamlanması anlamına gelmez.

| Bileşen | Durum | Sınır |
|---|---|---|
| Statik regex analizi | Çalışan aday üretici | Sanitizer hard-clear FN ve dosya/kapsam eksikleri açık |
| HTTP reflected/stored/flow/auth | R2 HTTP kabulü tamam | JSON, hedefe özel auth-check, fractional rate, sıralı CSRF/stored ve error/skip kayıtları testli; browser aktarımı R3, origin sınırı R9 |
| Payload üretimi | 50 varyant, 18 mutation | 950 üretim; cid normalize edilince 895 farklı dize; çalışan exploit sayısı değil |
| Browser proof / DOM gözlemci | R3 loopback kabulü; eval karşı örneği düzeltildi | `dxaprove` auth→role→submit→read→CID; native eval korunur, eval hook desteklenmez ve raporda belirtilir; WebSocket/ağ sandbox kapsam dışı |
| DOM dialog çıktısı | **Düzeltildi** | Normal dialog OBSERVED-DIALOG; proof üretmiyor |
| R1 kanıt modeli | **Kabul kapsamı tamamlandı** | Statik/HTTP/DOM/journal ortak Finding/ReportEvent; konservatif sink/rol dedup; execution ve doğrulanmış rol üretilmez |
| Blind callback sınıflandırması | **Düzeltildi: resource-callback** | JS proof ve oturum kimliği kanıtı değildir |
| Kalıcı blind takip | **Stored/stored-auto için eklendi** | Yansımasız CID kaydı, sonradan kontrol, zaman ve rol etiketi; reflected/flow/DOM journal entegrasyonu ve doğrulanmış rol açık |
| Benchmark | Legacy aday corpus'u + 9 yerel execution fixture'ı | Proof adapter kimlik scorer'ına bağlı; vaka istisnası error/timeout olarak ayrılır. Hard timeout, geniş corpus, gerçek ürün adapter'ı ve uzak CI açık |
| Yeni CVE kredisi | ZIP'te doğrulanmış kanıt yok | Duplicate ve bilinen açık çalışmaları tarihsel yazar beyanı |
| AST / recon genişletme / ürün paketi | Plan | R1–R6 doğruluk ve kullanılabilirlik işleri önce |

## Kanıt tabanı

Orijinal arşiv denetimi: 388 passed + 36 browser skipped; mevcut Chrome yolu test sürecine verilince 73 browser modülü testi geçti (37 örtüşen + 36 ek). Toplam 424 ayrı eski test iki çalışmanın kapsamıyla geçti. Bu sonuçlar bütün ürün bitiş ölçütlerini doğrulamaz; denetim karşı örnekleri açık hatalar gösterdi.

Bu geliştirme tesliminin yeni test sonuçları [VALIDATION.md](VALIDATION.md) içinde tutulur. Önceki denetim raporu değişmez tarihsel baseline'dır; buradaki düzeltmeler onun sonrasına aittir.

## Sıradaki küçük teslim

7 Ekim son yeniden doğrulama: **681 passed, 0 failure/error/skip**; Windows
Chrome ile `test_dxadom` 73 test dahil bütün analyzer/bench paketi yeniden koştu.
R3 cleanup/state restorasyonunda bulunan hata iki red regresyondan sonra
düzeltildi. R3 loopback ve R4 yerel runner/adapter kapsamı **PASS**.
Yeni strict corpus **9/9, TP=3 FP=0 FN=0**; gerçek vaka hatası ve eksik browser
CLI kontrolleri rapor yazıp exit 1 verdi. [Yeni audit](audit/2026-10-07-r3-r4-revalidation/README.md).
Genel R4, hard timeout, gerçek ürün adapter'ı ve uzak CI kabulü açık kalır.
Aşağıdaki 7 Ekim turları tarihsel sonuçlardır; yeni koşu yerine kullanılmaz.

7 Ekim ikinci tur: önceki kabul dosyaları ve üç kaynak hash'i karşılaştırıldı;
önceki dar teslim destekleniyor. Yeni R4 vaka istisnası düzeltmesi öncesi
8 regresyon başarısız oldu; düzeltme sonrası **146 passed**, skip yok.
Yeni gerçek Chrome CLI **9/9, TP=3 FP=0 FN=0**. Engine/QA atanan ayrı dosyaları
yazdı; koordinatör testleri çalıştırdı ve kayıtları güncelledi. Commit/push yok.
[Kabul, sahiplik değerlendirmesi ve açık işler](audit/2026-10-07-r4-case-isolation/README.md).
Sıradaki dar runner işi sert süre sınırı ve süreç temizliği kabulüdür; uzak CI,
sabit gerçek uygulama adapter'ı ve geniş corpus da açık kalır.

Aşağıdaki sayılar önceki 7 Ekim turunun sonuçlarıdır.

7 Ekim güncellemesi: önceki scope/R3/R4 kabulü yeni koşuda **89 passed**.
R4 corpus 9 vakaya genişletildi; son paket **136 passed**, skip yok;
gerçek Chrome strict runner **TP=3 FP=0 FN=0**, 9/9 tamamlandı.
Zorunlu browser CI yoluna corpus/adapter ve artifact adımları eklendi;
**uzak CI çalıştırılmadı**, R4 genel kapanışı açık.
Beş native çağrı bu sohbette doğrulandı; yeni geliştirmede Engine/QA yazdı,
Security salt okunur inceledi. [Güncel kanıt](audit/2026-10-07-r4-native/README.md).
Sonraki kapı uzak CI kanıtı ve sabit gerçek uygulama adapter'ıdır;
sanitizer/rol/iframe corpus kapsamı da açıktır.

Aşağıdaki 6 Ekim turu ve native doğrulanamadı açıklaması tarihsel kayıttır.

Son sınırlı tur: reflected crawler scope kontrolü, fonksiyon-local eval
karşı örneği ve R4 loopback adapter tamamlandı. **339 passed**, dört gerçek
Chrome benchmark vakasında TP=1 FP=0 FN=0. [Testler, gerçek agent katkıları
ve sınırlar](audit/2026-10-06-multi-agent-round1/README.md).
Native custom-agent yükleme doğrulanmadı; rol dosyasından açık talimat aktarımıyla
geçici collaboration çalışanları kullanıldı. Beş kalıcı tanım korundu.
Sonraki R4 işi corpus kapsamını genişletmek ve CI kabul kanıtını tamamlamak.
R9 genel ağ kapsamı bu turla kapanmadı. Aşağıdaki sayılar önceki teslimlerdir.

R1 [madde bazında kapandı](audit/2026-10-05-r1/R1-KAPANIS.md).
K01-min [tek yerel vaka paketi](cases/k01-stored-comment/README.md) tamamlandı:
5/5 browser kontrolü, fix diff ve aynı payload ile retest. Bağımsız temiz ortam
tekrarı henüz yok; tam R5 açık. R2 [HTTP kabul kapsamıyla kapandı](audit/2026-10-06-r2/R2-KAPANIS.md).
R3 [loopback proof zinciriyle kapandı](audit/2026-10-06-r3-final/README.md);
WebSocket/genel ağ sandboxı R9'da. R4 ölçüm düzeltmeleri başladı: eksik FN,
timeout/error/skip ayrımı ve strict gate düzeltildi; ikinci turda yerel execution
adapter bağlandı, geniş corpus açık. [R4 ilk teslim](audit/2026-10-06-r4/README.md).
Son paket: **544 passed, 36 skipped, 1 warning**; [kanıt](VALIDATION.md).
Yeni gerçek Chrome testi normal dialog/sink olaylarını ortak raporda kontrol etti;
eski 36 browser testinin atlanma durumu değişmedi.
S01 [R1 kapanış kaydı](staj/2026-10-05-r1-kapanis.md) eklendi.

## Ana proje kapsamı

Bot R0–R9; yazılar C01–C13; kanıt/savunma K01–K05; portfolyo P01–P04; staj S01–S03; araştırma/CVE A01–A05. Tam sıra ve kabul ölçütleri ROADMAP.md, orijinal 76 dosyanın eşlemesi DOSYA-KAPSAM.md içinde. S01 için [ilk gerçek geliştirme kaydı](staj/2026-09-28-kanit-siniflandirmasi.md) başlatıldı; resmî staj defteri doldurulmadı.

S01'e [29 Eylül blind takip kaydı](staj/2026-09-29-blind-takip.md) eklendi.
Rapor/kanıt için kullanım, yerel süreçler arası test ve JSON/HTML çıktı altyapısı
ilerledi. K01-min proof→fix→retest paketi tamam; üç vakalık portfolyo açık;
yeni dış hedef taraması veya CVE başvurusu yapılmadı.

## Tarihsel veri

v3.10 HTML dosyaları: 50 JSON-only dinamik kayıt, 2 Bludit dinamik aday/sınıflandırma ve 78 statik MEDIUM aday. Bunlar bağımsız açıklık toplamı değildir. Boş tablodaki No findings satırı bulgu değildir.

Eski writeup, README ve roadmap metinleri güncel ürün taahhüdü olarak kullanılmaz. Tamamlanma yalnız roadmap'teki kabul koşullarının kanıtıyla güncellenir.
