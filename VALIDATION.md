# Doğrulama kaydı — 2026-09-29

## R1 kalıcı stored blind takip — güncel teslim

- Tam paket: **438 passed, 36 skipped, 1 warning**, 76.57 saniye.
- 18 yeni regresyon: stored/stored-auto yansımasız beş aile, gönderim hatası,
  canlı ve süreç kapandıktan sonra callback, eşzamanlı kalıcı yazma, tekrar
  kontrol, CID/zaman/endpoint/run ayrımı, yanlış yanıt, mahremiyet ve rapor escaping.
- İki CLI süreci + localhost HTTP fixture: tarama kapanır, callback daha sonra gelir,
  ayrı kontrol komutu aynı attempt kimliğine bağlar; hedef **yalnız bir POST** alır.
- JSON ve HTML kontrol raporu aynı attempt listesinden oluşturulur.
- Ara odaklı çalışma **220 passed**; son dört ek test ve canlı callback kalıcılığı
  yukarıdaki tam pakette doğrulandı.
- 36 browser testi mevcut otomatik Chrome keşfi sorunu nedeniyle atlandı.
  Bu teslim yeni browser execution doğrulaması yapmadı. Tek uyarı benchmark'taki
  `datetime.utcnow()` kullanımının deprecation uyarısıdır.
- [Test logu](audit/2026-09-29/pytest-blind-journal.log),
  [JUnit](audit/2026-09-29/pytest-blind-journal.xml),
  [test kaynağı](tools/dom-xss-analyzer/test_blind_journal.py),
  [tekrar üretim ve sınırlar](tools/dom-xss-analyzer/BLIND-JOURNAL.md).

Sınır: journal yalnız stored/stored-auto blind gönderim/callback kaydıdır;
bütün reflection/sink bulgularının ortak şeması değildir. Rol operatör etiketidir.
Callback JavaScript execution veya açıklık kanıtı değildir. Genel R1 açık kalır.

## R2 JSON gönderimi — önceki teslim

- Tam paket: **420 passed, 36 skipped, 1 warning**, 69.03 saniye.
- 36 browser testi otomatik Chrome keşfi nedeniyle atlandı; browser entegrasyonu tamamlandı sayılmıyor.
- Yeni yedi regresyon senaryosu: 950 payload'ın gerçek submit fonksiyonunda JSON round-trip'i; iç içe değer/anahtar ve kontrol karakterleri; üç geçersiz JSON durumu; anahtar çakışması; iki eşzamanlı JSON isteğinde ortak header izolasyonu.
- Eski quote testi elle escape algoritmasını kopyalamak yerine gerçek submit fonksiyonunun çıktısını kontrol ediyor.
- Odaklı JSON + dinamik test çalışması 176 geçti; son quote testi değişikliği yukarıdaki tam pakette doğrulandı.
- Kanıtlar: [test logu](audit/2026-09-28/pytest-json-transport.log), [JUnit](audit/2026-09-28/pytest-json-transport.xml).

Önceki 413 test sonucu callback teslimine aittir. JSON request kodlaması düzeltildi;
flow modundaki response/XSS sınıflandırması, auth ve CSRF açık kalır.

## Ana roadmap ve callback düzeltmesi — önceki teslim

- Callback/dinamik odaklı testler: **206 passed**.
- Tüm paket: **413 passed, 36 skipped, 1 warning**, 103.58 saniye. Atlanan 36 test Windows browser keşfi nedeniyle; cache yazma uyarısı var.
- 19 yeni callback regresyonu geçti; yanlış proof bekleyen önceki testler yeni gözlem semantiğine uyarlandı.
- JavaScript kapalı gerçek Chrome 154.0.8037.58: img isteği → 1 callback → 1 eşleşme → `severity=resource-callback`, `evidence_level=resource-callback`; JS proof iddiası yok.
- Canary id'si eksik/boş/farklı olduğunda eşleştirme reddedilir; HTTP yöntemi veya payload ailesi JS yürütme kanıtı sayılmaz.
- CLI help ve HTML resource-callback anlamını taşıyor; HTML'de istek metadata'sı escape ediliyor.

Kanıtlar: [tam test logu](audit/2026-09-28/pytest-master-roadmap.log), [JUnit](audit/2026-09-28/pytest-master-roadmap.xml),
[odaklı test logu](audit/2026-09-28/pytest-callback-focused.log), [Chrome sonucu](audit/2026-09-28/resource-callback-fix-browser.json),
[örnek rapor](audit/2026-09-28/resource-callback-report.html). Otomatik regresyonlar
`tools/dom-xss-analyzer/test_blind_correlation.py` içindedir.

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

- [Tam test logu](audit/2026-09-28/pytest-development.log)
- [JUnit sonucu](audit/2026-09-28/pytest-development.xml)
- [Gerçek tarayıcı sonucu](audit/2026-09-28/dom-dialog-fix-browser.json)
- Otomatik CLI regresyonları: `tools/dom-xss-analyzer/test_dom_cli_evidence.py`.

Bu bağlantılar depodaki tarihsel kanıtlara gider. Yerel kullanıcı dizinleri paylaşım
kopyalarında maskelendi; test sonuçları değiştirilmedi. Eski denetim scriptlerinin
tümü bu kanıt paketine dahil değildir; paket açıklaması `audit/2026-09-28/README.md` içindedir.

## İlk teslimin sınırı (tarihsel)

Yalnız bare-visit dialog çıktısındaki yanlış proof iddiası düzeltildi. Yeni execution doğrulama motoru eklenmedi. Blind korelasyon, breakout severity, auth, JSON ve benchmark kusurları açık; ROADMAP'te ayrı kabul koşulları var.

Orijinal ZIP ve denetim kaynak kopyası korunmuştur. İlk düzeltmeler `2703d1a`
ile Git geçmişine ve GitHub main dalına aktarıldı. Sürüm etiketi oluşturulmadı.
