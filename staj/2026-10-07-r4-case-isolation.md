# Benchmark vaka hatasını sonuçtan ayırmak — 7 Ekim 2026

Önceki kabul kaydını yeni test gibi sunmadan, JUnit/corpus dosyalarını mevcut
kaynak hash'leriyle karşılaştırdık. Dokuz vakalık yerel teslim destekleniyordu;
uzak CI ve genel R4 kapanışı hâlâ yoktu.

Sonraki küçük işte proof vaka çağrısından çıkan istisnanın bütün rapor üretimini
kesebildiğini ele aldık. QA bağımsız testleri, Engine yalnız runner düzeltmesini
yazdı; koordinatör önce yanlış davranışı çalıştırdı: 8 failed, 2 passed.
Düzeltme sonrası yeni birleşik koşu 146 passed, sıfır skip; ayrı Chrome CLI
9/9 tamamlandı, TP=3 FP=0 FN=0.

Başarısız vakayı sıfır bulgulu başarılı vaka saymak yerine error/timeout olarak
tutmak, kapsama paydasını ve kalan vakaları korur. Ham exception içeriği
raporlanmaz. İstisna yakalamak donmuş süreci süre sonunda durdurmak değildir;
hard timeout ve süreç temizliği ayrı kabul ister.

[Sahiplik, yeniden üretim komutları ve kanıtlar](../audit/2026-10-07-r4-case-isolation/README.md).
Bu kayıt çalışma saati, resmî staj formu veya güvenlik açığı/CVE iddiası değildir.
