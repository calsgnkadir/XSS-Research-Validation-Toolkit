# R4 ölçüm altyapısı — 6 Ekim 2026

İlk teslim; R4 bütünü tamamlanmadı.

Doğrulama: `python -m pytest bench/test_bench.py -q -p no:cacheprovider --tb=short`
ile **43 passed**, 8.47 saniye. Uzak Linux CI sonucu bu teslimde doğrulanmadı.

- Beklenen 3, bulunan 1 için artık TP=1/FN=2.
- Kimlik bazlı eşleme yanlış sink'i FP, eksik kimliği FN sayar; kopyaları birleştirir.
- Execution eşlemesi yalnız canary eşleşmiş browser execution gözlemini kabul eder.
  Reflection, aday ve resource-callback execution TP değildir.
- Timeout, çökme, tanınmayan çıktı ve skip değerlendirme dışında ayrı sayılır.
  Seçilen/tamamlanan sayıları raporda bulunur; bunlar true negative sayılmaz.
- Strict gate FP, FN, hata, timeout, skip ve boş koşuda başarısız olur.
- CI açıkça üç mock hedefi seçer; Markdown/JSON sonucu artifact olarak saklar.

Yerel benchmark üç hedefi tamamladı: **aday ölçümünde TP=2/FP=0/FN=0**.
Bu rakamlar doğrulanmış XSS doğruluğu değildir. CLI adapter'ı hâlâ eski aday
özetini okur; kimlik bazlı execution scorer henüz bu adapter'a bağlanmadı.
[JSON](benchmark.json), [Markdown](benchmark.md).

Kalanlar: structured bulgu adapter'ı ve geniş fixture matrisi, gerçek uygulama
bootstrap/login adapter'ı, R8 sanitizer karşı örnekleriyle ölçüm, Linux CI sonucu,
browser header gözlemi. R3 browser kanıtı ayrıca tutulur; sayılar birleştirilmez.
