# Doğrulama kaydı — 2026-09-28

## Ana roadmap ve callback düzeltmesi — güncel teslim

- Callback/dinamik odaklı testler: **206 passed**.
- Tüm paket: **413 passed, 36 skipped, 1 warning**, 103.58 saniye. Atlanan 36 test Windows browser keşfi nedeniyle; cache yazma uyarısı var.
- 19 yeni callback regresyonu geçti; yanlış proof bekleyen önceki testler yeni gözlem semantiğine uyarlandı.
- JavaScript kapalı gerçek Chrome 154.0.8037.58: img isteği → 1 callback → 1 eşleşme → `severity=resource-callback`, `evidence_level=resource-callback`; JS proof iddiası yok.
- Canary id'si eksik/boş/farklı olduğunda eşleştirme reddedilir; HTTP yöntemi veya payload ailesi JS yürütme kanıtı sayılmaz.
- CLI help ve HTML resource-callback anlamını taşıyor; HTML'de istek metadata'sı escape ediliyor.

Kanıtlar: [tam test logu](../xss-audit/pytest-master-roadmap.log), [JUnit](../xss-audit/pytest-master-roadmap.xml),
[odaklı test logu](../xss-audit/pytest-callback-focused.log), [Chrome sonucu](../xss-audit/resource-callback-fix-browser.json),
[Chrome test scripti](../xss-audit/verify_resource_callback_fix.py), [örnek rapor](../xss-audit/resource-callback-report.html).

Sınır: bu teslimde gerçek canary execution motoru veya yansımasız kalıcı blind takip yapılmadı. Callback gözlemi ile açıklık/etki ayrı tutuldu; ortak kanıt şeması henüz tamamlanmadı.

## İlk geliştirme teslimi

- Yeni CLI regresyon dosyası: **6 passed**.
- Geliştirme kopyasının tüm test paketi: **394 passed, 36 skipped, 1 warning**, 68.83 saniye.
- Atlanan 36 test browser keşfi nedeniyle atlandı; Windows Chrome yolunun otomatik bulunması hâlâ açık iş. Bunlar geçmiş baseline'da açık Chrome yolu ile çalıştırılmıştı; bu teslimde yeniden çalışmış gibi sayılmıyor.
- Mevcut Chrome ile ayrı gerçek tarayıcı kontrolü: yalnız 127.0.0.1 üzerinde normal alert sayfası açıldı. **OBSERVED-DIALOG**, exit 0; **PROVEN-EXECUTABLE yok**. Test sürecinde browser yolu açık verildi; kaynakta platform keşfi değiştirilmedi.
- Pytest cache yazma uyarısı test başarısızlığı değildir.

Tekrarlama: pytest kurulu ortamda depo kökünden `python -m pytest -q -ra`.
Dar regresyon: `python -m pytest tools/dom-xss-analyzer/test_dom_cli_evidence.py -q`.

Bu çalışma alanındaki ham kanıtlar:

- [Tam test logu](../xss-audit/pytest-development.log)
- [JUnit sonucu](../xss-audit/pytest-development.xml)
- [Gerçek tarayıcı sonucu](../xss-audit/dom-dialog-fix-browser.json)
- [Yerel tarayıcı kontrol scripti](../xss-audit/verify_dom_dialog_fix.py)

Bu göreli bağlantılar yerel geliştirme klasörü yanındaki denetim klasörünü gösterir;
depo tek başına yayımlanmadan önce ilgili kanıtlar kalıcı repo/CI artifact konumuna taşınmalıdır.

## İlk teslimin sınırı (tarihsel)

Yalnız bare-visit dialog çıktısındaki yanlış proof iddiası düzeltildi. Yeni execution doğrulama motoru eklenmedi. Blind korelasyon, breakout severity, auth, JSON ve benchmark kusurları açık; ROADMAP'te ayrı kabul koşulları var.

Orijinal ZIP ve denetim kaynak kopyası korunmuştur. Çalışma klasörü ZIP'ten türediği için Git geçmişi içermez; commit/push veya yayımlanmış sürüm iddiası yoktur.
