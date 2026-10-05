# R1 kapanış kanıtları

Komut: `python -m pytest -q -ra -p no:cacheprovider --tb=short --junitxml=audit/2026-10-05-r1/pytest-r1.xml`

Sonuç: **479 passed, 36 skipped, 1 warning**, 87.53 saniye. Yeni gerçek Chrome
testi geçti; Chrome yolu testte açık verildi. 36 eski browser testi otomatik
keşif nedeniyle atlandı. Uyarı benchmark `datetime.utcnow()` kullanımına ait.

- [Kapanış matrisi](R1-KAPANIS.md)
- [Agent yorumu değerlendirmesi](AGENT-YORUMU.md)
- [Test logu](pytest-r1.log) ve [JUnit](pytest-r1.xml)
- Gerçek yerel Chrome testinin [JSON](chrome.json) ve [HTML](chrome.html) çıktısı

Chrome çıktıları son test çalışmasının `test_real_chrome_bare_dialog_uses_common_report`
geçici klasöründen kopyalandı; örnek olması için üretilmiş hayalî veri değildir.
Sadece loopback fixture, normal dialog ve sink gözlemi var; XSS execution proof yok.
Log/XML paylaşım kopyasında yerel repo yolu `[workspace]`, hostname `[host]`
olarak maskelendi. Sonuçlar ve süreler değiştirilmedi. Orijinal ZIP korunur.
