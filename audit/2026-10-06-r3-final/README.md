# R3 ilk uçtan uca teslim — 6 Ekim 2026

Kapsam: loopback tek-origin lab, bir hesap/rol, HTTP auth+submit ve ayrı
browser context'inde kimlik/rol kontrolü ile CID execution gözlemi.
R1 modeli korunur; ayrı browser-proof/1 JSON/HTML kullanılır.

`test_browser_proof.py` içindeki **18 browser testi** ham/fixed/JSON/dialog,
iframe/gecikme/aşım, direct eval lexical scope, cookie/bearer, form CSRF,
JavaScript kapalı, gerçek href/fixed href, yanlış rol, cross-origin istek,
eksik browser, geçersiz scope ve tek komut artifact kontrollerini kapsar.
WebSocket engelleme denemesi takıldı ve kaldırıldı; bunun filtrelenmediği
[kapsam belgesinde](../../tools/dom-xss-analyzer/BROWSER-PROOF.md) açıklanır.

R3 odaklı browser koşusu 18/18 geçti. Tam paket **544 passed, 36 skipped,
1 warning**, 141.50 saniye.
[pytest logu](pytest.log), [JUnit](pytest.xml),
[tek komut demo JSON'u](demo/result.json), [HTML](demo/result.html).
Komut: `python -m pytest -q -ra -p no:cacheprovider --tb=short --junitxml=audit/2026-10-06-r3-final/pytest.xml`.

Testlerde `DXA_REQUIRE_BROWSER=1`; browser yoksa fail eder. 36 skip eski
`dxadom` testleridir; Chrome otomatik keşfedilmedi. Uyarı benchmark utcnow.
Windows'ta Chrome 154.0.8037.98 / Playwright 1.63.0 ile demo geçti.
Uzak Linux CI yapılandırıldı ama henüz sonucu alınmadı.

Tam R3 açık: SPA queue, eski observer, ortak kanıt şeması entegrasyonu,
yakalanan auth/CSRF aktarımı ve Linux çalışmasının doğrulanması.
