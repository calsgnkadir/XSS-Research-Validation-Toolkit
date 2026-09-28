# Geliştirme kaydı — 28 Eylül 2026

Görevler: R1, C13 ve S01. Bu teknik çalışma günlüğüdür; resmî staj formu veya onay kaydı değildir. Saat/süre beyanı yapılmadı.

## Amaç

XSS botunun gözlenen bir olayı, kanıtlamadığı bir açıklık gibi sunmasını önlemek. Önceliği bot olan ana proje planına rapor, kanıt, portfolyo, staj ve araştırma işlerini dahil etmek.

## Bulgular ve yapılan iş

Önceki denetimde sıradan uygulama alert'i PROVEN-EXECUTABLE oluyordu. İlk düzeltmede bare ziyaret dialog'ları OBSERVED-DIALOG olarak ayrıldı; altı regresyon ve yerel Chrome ile doğrulandı.

Bu teslimde HTTP callback'in proven-blind sayılması düzeltildi. Eşleşen callback resource-callback olarak kaydediliyor. CID boş veya farklıysa finding değiştirilmez. UA/IP/Referer, kurban oturumu kimliği veya JavaScript kanıtı sayılmaz. Blind fetch deneme payload'ı gizli cookie yerine yalnız canary kimliğini gönderiyor.

CLI help, durum mesajı ve HTML raporu aynı anlamı taşıyacak şekilde güncellendi. Önceden hatalı davranışı bekleyen testler düzeltildi; 19 yeni regresyon senaryosu eklendi. Genel kanıt modeli ve görünmeyen sink için kalıcı deneme kaydı açık kaldı.

## Deney ve kanıt

- Odaklı callback + dinamik test paketi: 206 passed.
- Normal HTTP istemcisiyle callback: browser veya JS olmadan resource-callback; test paketi içinde.
- Chrome 154.0.8037.58, JavaScript kapalı: img yüklemesi bir callback oluşturdu; sonuç resource-callback. [JSON kayıt](../audit/2026-09-28/resource-callback-fix-browser.json).
- [Örnek HTML raporu](../audit/2026-09-28/resource-callback-report.html) execution veya başka kullanıcı iddiası içermiyor.
- Tam test paketi sonucu [VALIDATION](../VALIDATION.md) içinde; atlanan testler başarı gibi sayılmaz.

## Öğrenilen

Bir ağ isteği kaydı, JavaScript çalışması ve yetki sınırını aşan güvenlik açığı üç farklı iddiadır. Kanıt seviyesi ile etki/triage ayrı tutulmalıdır. Testin yeşil olması yetmez: test yanlış kabulü koruyabilir. Negatif kontrol, hangi sonucun çıkarılamayacağını da doğrular.

## Sonraki iş

R1 ortak şema ve gönderilmiş deneme kaydı; ardından R2 auth/JSON/rate ve R8 sanitizer düzeltmeleri. Bu kayıt yeni CVE veya tüm blind XSS desteği tamamlandı iddiası değildir.

## Ek çalışma — GitHub tutarlılığı ve R2 JSON gönderimi

GitHub'ın canlı README'si ile web arama aracının eski taranmış görünümü ayrıldı.
README'ye test/skip özeti eklendi; denetim ve sonuç dosyaları depo içine taşındı,
yerel dosya yollarına giden kanıt bağlantıları düzeltildi.

R2'de JSON gövdesi önce çözümlenip canary değerleri yerleştiriliyor, sonra JSON
serializer ile kodlanıyor. Denetimde bozulabilen kontrol karakterleri dahil 950
deneme gerçek gönderim fonksiyonundan geçirilerek geri okunuyor. İç içe değerler,
geçersiz şablonlar ve eşzamanlı Content-Type kullanımı ayrı testlerle denetlendi.
Bu değişiklik yanıtın XSS olup olmadığına karar veren flow sınıflandırmasını düzeltmez.
Güncel tam test sonucu VALIDATION.md'dedir; R1, auth ve CSRF işleri açık kalır.
