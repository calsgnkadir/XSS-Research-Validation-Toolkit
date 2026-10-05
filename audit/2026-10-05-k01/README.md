# K01 doğrulama paketi

Browser deneyinin kanıtları [vaka klasöründe](../../cases/k01-stored-comment/evidence/2026-10-05-verified/result.json).
Beş kontrolün hepsi geçti. HTTP fixture regresyonları tam pytest paketine eklendi.
Tam paket: **481 passed, 36 skipped, 1 warning**, 80.33 saniye.
Komut: `python -m pytest -q -ra -p no:cacheprovider --tb=short --junitxml=audit/2026-10-05-k01/pytest.xml`

[Log](pytest.log), [JUnit](pytest.xml). Paylaşım kopyasında yerel repo yolu
`[workspace]`, hostname `[host]` ile maskelenir; sonuç/süre değiştirilmez.
Browser deneyinin request/response dosyalarında yalnız sentetik yerel canary var.
`fix.diff` bir unified diff olduğundan boş context satırlarındaki tek boşluk korunur.
