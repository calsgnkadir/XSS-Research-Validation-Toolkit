# Doğrulanmış durum

28 Eylül 2026. Güncel plan: [ROADMAP](ROADMAP.md). Bu durum ZIP'ten oluşturulan yerel geliştirme kopyasına aittir; GitHub/commit/push doğrulaması değildir.

| Bileşen | Durum | Sınır |
|---|---|---|
| Statik regex analizi | Çalışan aday üretici | Sanitizer hard-clear FN ve dosya/kapsam eksikleri açık |
| HTTP reflected/stored/flow/auth | Çalışan prototip | JSON serializer, auth başarı kontrolü, rate/CSRF yarışları açık |
| Payload üretimi | 50 varyant, 18 mutation | 950 üretim; cid normalize edilince 895 farklı dize; çalışan exploit sayısı değil |
| DOM gözlemci | Deneysel | Bare visit; auth/stored proof entegrasyonu yok |
| DOM dialog çıktısı | **Düzeltildi** | Normal dialog OBSERVED-DIALOG; proof üretmiyor |
| Blind callback sınıflandırması | **Düzeltildi: resource-callback** | Sıkı cid eşleşmesi; JS proof iddiası ve cookie toplama kaldırıldı; yansımasız cid takip eksiği açık |
| Benchmark | 3 mock + 3 Docker tanımı | FN/error hesabı ve gerçek hedef adapter'ları eksik |
| Yeni CVE kredisi | ZIP'te doğrulanmış kanıt yok | Duplicate ve bilinen açık çalışmaları tarihsel yazar beyanı |
| AST / recon genişletme / ürün paketi | Plan | R1–R6 doğruluk ve kullanılabilirlik işleri önce |

## Kanıt tabanı

Orijinal arşiv denetimi: 388 passed + 36 browser skipped; mevcut Chrome yolu test sürecine verilince 73 browser modülü testi geçti (37 örtüşen + 36 ek). Toplam 424 ayrı eski test iki çalışmanın kapsamıyla geçti. Bu sonuçlar bütün ürün bitiş ölçütlerini doğrulamaz; denetim karşı örnekleri açık hatalar gösterdi.

Bu geliştirme tesliminin yeni test sonuçları [VALIDATION.md](VALIDATION.md) içinde tutulur. Önceki denetim raporu değişmez tarihsel baseline'dır; buradaki düzeltmeler onun sonrasına aittir.

## Sıradaki küçük teslim

R1: ortak evidence modeli, yansıma olmasa da gönderilmiş cid kaydı ve sonradan korelasyon. Bare dialog ve kaynak callback'inin yanlış proof sayılması düzeltildi; gerçek canary execution doğrulaması henüz yok. R2'de JSON/auth/rate sorunları ayrı küçük düzeltmeler halinde izlenir. Bu iki düzeltme R1'i tek başına kapatmaz.

## Ana proje kapsamı

Bot R0–R9; yazılar C01–C13; kanıt/savunma K01–K05; portfolyo P01–P04; staj S01–S03; araştırma/CVE A01–A05. Tam sıra ve kabul ölçütleri ROADMAP.md, orijinal 76 dosyanın eşlemesi DOSYA-KAPSAM.md içinde. S01 için [ilk gerçek geliştirme kaydı](staj/2026-09-28-kanit-siniflandirmasi.md) başlatıldı; resmî staj defteri doldurulmadı.

## Tarihsel veri

v3.10 HTML dosyaları: 50 JSON-only dinamik kayıt, 2 Bludit dinamik aday/sınıflandırma ve 78 statik MEDIUM aday. Bunlar bağımsız açıklık toplamı değildir. Boş tablodaki No findings satırı bulgu değildir.

Eski writeup, README ve roadmap metinleri güncel ürün taahhüdü olarak kullanılmaz. Tamamlanma yalnız roadmap'teki kabul koşullarının kanıtıyla güncellenir.
