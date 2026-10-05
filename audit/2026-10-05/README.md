# 5 Ekim 2026 doğrulama kanıtı

Depo kökünde `python -m pytest -q -ra -p no:cacheprovider --junitxml=audit/2026-10-05/pytest-http-evidence.xml`
çalıştırıldı. Sonuç: **450 passed, 36 skipped, 1 warning**, 76.29 saniye.
Testler localhost erişimi ve geçici dosya yazımı gerektirir.

Paylaşım kopyalarında yerel çalışma yolu `[workspace]`, makine adı `[host]`
ile maskelendi. Test isimleri, sonuçlar ve süreler değiştirilmedi.
Orijinal ZIP ve önceki tarihli denetim kayıtları değiştirilmedi.

[Regresyonlar](../../tools/dom-xss-analyzer/test_http_evidence.py),
[kanıt modeli](../../tools/dom-xss-analyzer/HTTP-EVIDENCE.md),
[staj kaydı](../../staj/2026-10-05-http-kanit-modeli.md).
