# Doğrulanmış durum

6 Ekim 2026. Güncel plan: [ROADMAP](ROADMAP.md). ZIP üzerinden başlayan düzeltmeler
`2703d1a` ile GitHub main dalına aktarıldı. Canlı GitHub API'si güncel README'yi
doğruladı; web arama sonuçları eski taranmış metni gösterebilir. Bu durum yeni
CVE veya tüm roadmap'in tamamlanması anlamına gelmez.

| Bileşen | Durum | Sınır |
|---|---|---|
| Statik regex analizi | Çalışan aday üretici | Sanitizer hard-clear FN ve dosya/kapsam eksikleri açık |
| HTTP reflected/stored/flow/auth | R2 HTTP kabulü tamam | JSON, hedefe özel auth-check, fractional rate, sıralı CSRF/stored ve error/skip kayıtları testli; browser aktarımı R3, origin sınırı R9 |
| Payload üretimi | 50 varyant, 18 mutation | 950 üretim; cid normalize edilince 895 farklı dize; çalışan exploit sayısı değil |
| Browser proof / DOM gözlemci | R3 loopback kabulü tamam | `dxaprove` auth→role→submit→read→CID, `dxadom` observer/eval, SPA route bütçesi ve allowlist header aktarımı testli; WebSocket/ağ sandbox kapsam dışı |
| DOM dialog çıktısı | **Düzeltildi** | Normal dialog OBSERVED-DIALOG; proof üretmiyor |
| R1 kanıt modeli | **Kabul kapsamı tamamlandı** | Statik/HTTP/DOM/journal ortak Finding/ReportEvent; konservatif sink/rol dedup; execution ve doğrulanmış rol üretilmez |
| Blind callback sınıflandırması | **Düzeltildi: resource-callback** | JS proof ve oturum kimliği kanıtı değildir |
| Kalıcı blind takip | **Stored/stored-auto için eklendi** | Yansımasız CID kaydı, sonradan kontrol, zaman ve rol etiketi; reflected/flow/DOM journal entegrasyonu ve doğrulanmış rol açık |
| Benchmark | 3 mock + 3 Docker tanımı | FN/error hesabı ve gerçek hedef adapter'ları eksik |
| Yeni CVE kredisi | ZIP'te doğrulanmış kanıt yok | Duplicate ve bilinen açık çalışmaları tarihsel yazar beyanı |
| AST / recon genişletme / ürün paketi | Plan | R1–R6 doğruluk ve kullanılabilirlik işleri önce |

## Kanıt tabanı

Orijinal arşiv denetimi: 388 passed + 36 browser skipped; mevcut Chrome yolu test sürecine verilince 73 browser modülü testi geçti (37 örtüşen + 36 ek). Toplam 424 ayrı eski test iki çalışmanın kapsamıyla geçti. Bu sonuçlar bütün ürün bitiş ölçütlerini doğrulamaz; denetim karşı örnekleri açık hatalar gösterdi.

Bu geliştirme tesliminin yeni test sonuçları [VALIDATION.md](VALIDATION.md) içinde tutulur. Önceki denetim raporu değişmez tarihsel baseline'dır; buradaki düzeltmeler onun sonrasına aittir.

## Sıradaki küçük teslim

R1 [madde bazında kapandı](audit/2026-10-05-r1/R1-KAPANIS.md).
K01-min [tek yerel vaka paketi](cases/k01-stored-comment/README.md) tamamlandı:
5/5 browser kontrolü, fix diff ve aynı payload ile retest. Bağımsız temiz ortam
tekrarı henüz yok; tam R5 açık. R2 [HTTP kabul kapsamıyla kapandı](audit/2026-10-06-r2/R2-KAPANIS.md).
R3 [loopback proof zinciriyle kapandı](audit/2026-10-06-r3-final/README.md);
WebSocket/genel ağ sandboxı R9'da. R4 ölçüm düzeltmeleri başladı: eksik FN,
timeout/error/skip ayrımı ve strict gate düzeltildi; execution adapter entegrasyonu
ve geniş corpus açık. [R4 ilk teslim](audit/2026-10-06-r4/README.md).
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
