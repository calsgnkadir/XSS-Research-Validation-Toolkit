# Denetim ve doğrulama kanıtları — 28 Eylül 2026

Bu klasör ZIP'in başlangıç denetimini ve ilk iki düzeltmenin sonuçlarını saklar.
Denetim raporundaki “henüz düzeltilmedi” ifadeleri o başlangıç anına aittir;
güncel durum için [STATUS](../../STATUS.md), [CHANGELOG](../../CHANGELOG.md)
ve [VALIDATION](../../VALIDATION.md) kullanılır.

- [Tam denetim](DENETIM-RAPORU-TR.md) ve [76 dosya incelemesi](DOSYA-INCELEMESI-TR.md).
- `audit-checks.json`, `browser-checks.json`: başlangıç karşı örnekleri.
- `pytest-development.*`: ilk dialog düzeltmesi — 394 passed, 36 skipped.
- `pytest-master-roadmap.*`: callback düzeltmesi — 413 passed, 36 skipped.
- `pytest-json-transport.*`: JSON gönderimi düzeltmesi — 420 passed, 36 skipped.
- `pytest-callback-focused.log`: odaklı 206 test.
- `dom-dialog-fix-browser.json`, `resource-callback-fix-browser.json`: yerel Chrome kontrolleri.
- `resource-callback-report.html`: düzeltilmiş rapor örneği (GitHub kaynak görünümü; indirip tarayıcıda açılabilir).

Yayımlama kopyalarında yerel kullanıcı dizini `[workspace]` olarak maskelendi;
inceleme tablosundaki dosya bağlantıları depo göreli yoluna çevrildi. Sonuçlar
yeniden üretilmiş gibi tarihlenmedi. Tarihsel browser kontrolleri sabit Windows
Chrome yolu kullanmıştı; varsayılan browser keşfinin düzeltildiği iddia edilmiyor.
Denetim raporu yereldeki ek script/envanter dosyalarına da isimle atıf yapar;
bu klasör tüm yerel denetim çalışma ortamı veya bağımlılık paketi değildir.
