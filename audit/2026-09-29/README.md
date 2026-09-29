# 29 Eylül 2026 doğrulama kanıtı

Depo kökünden `python -m pytest -q -ra --junitxml=audit/2026-09-29/pytest-blind-journal.xml`
çalıştırıldı. Sonuç: 438 passed, 36 skipped, 1 warning; 76.57 saniye.

Bu paylaşım kopyalarında yerel çalışma yolu `[workspace]`, makine adı `[host]`
ile maskelendi. Test isimleri, sonuçlar ve süreler değiştirilmedi.
Tarama veritabanları veya kimlik bilgileri kanıt paketine alınmadı.

18 yeni regresyonun kaynağı
[test_blind_journal.py](../../tools/dom-xss-analyzer/test_blind_journal.py).
Süreçler arası yerel HTTP testi callback'in geç gelmesini ve hedefe tekrar POST
yapılmamasını kontrol eder. Gerçek tarayıcı execution testi değildir.

[Kapsam ve sınırlar](../../VALIDATION.md),
[kullanım](../../tools/dom-xss-analyzer/BLIND-JOURNAL.md),
[staj öğrenme kaydı](../../staj/2026-09-29-blind-takip.md).
