# Geliştirme kaydı — 29 Eylül 2026

Görevler: R1, C13, K05'in rapor altyapısı ve S01. Teknik çalışma kaydıdır;
resmî staj onayı, çalışma saati veya bağımsız açıklık bulma beyanı değildir.

Önceki JSON gönderimi düzeltmesi GitHub main'deydi. Sıradaki hata: stored bot
yalnız okuma sayfasında canary gördüğünde finding üretiyordu. Yansıma olmayan
blind denemelerin CID listesi kayboluyor, tarama sonrası ilişkilendirme yapılamıyordu.

SQLite journal eklenerek deneme gönderimden önce commit edildi. Stored ve
stored-auto akışları bu kaydı kullanıyor. Gönderim/yanıt durumu, attempt/run
kimliği, zaman ve operatörün verdiği rol etiketi saklanıyor. Ayrı CLI, yalnız
callback sunucusunu sorgulayıp aynı kayıtlardan JSON ve HTML üretiyor.

Kontroller: beş blind ailesinin yansımasız denemeleri, reddedilen gönderimler,
istisnalar, eşzamanlı yazma, tekrar açma, CID/zaman eşleşmesi, sorgu hatası,
tekrarlı kontrol, rapor escaping ve hassas URL parçalarının çıkarılması.
İki ayrı CLI süreciyle yerel fixture deneyi, tarama kapandıktan sonraki
callback'in korunmasını ve hedefe ikinci POST yapılmamasını kontrol ediyor.
İlk odaklı çalışmada iki test, fixture'a eksik argüman verdiği için hata verdi;
fixture kullanımı düzeltildi. Ürün hatası gibi kaydedilmedi.

Sonuç ve test kanıtı [VALIDATION](../VALIDATION.md) içinde.
[Kullanım ve sınırlar](../tools/dom-xss-analyzer/BLIND-JOURNAL.md) tekrar üretimi açıklar.

Öğrenilen: gönderimin yapılması, ağ callback'i, JavaScript execution ve güvenlik
sınırının aşılması ayrı iddialardır. Süreç kapanınca bellekteki sonuç kaybolur;
gönderimden önce kalıcı kayıt, belirsiz yarım kalmış denemeleri de görünür kılar.
`no-hit` sonucu güvenli anlamına gelmez; sorgu hatası ayrıca raporlanmalıdır.

Kalan: bütün modlar için ortak finding şeması, flow/ham marker sınıflandırması,
doğrulanmış rol, browser execution ve yeniden üretilebilir proof→fix→retest vakası.
Yeni CVE araştırması veya dış hedef taraması yapılmadı.
