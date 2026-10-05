# Doğrulama kaydı — 2026-10-05

## R2 auth guard — güncel teslim

- Tam paket **496 passed, 36 skipped, 1 warning**, 89.38 saniye.
  36 eski browser testi otomatik keşif nedeniyle atlandı; benchmark utcnow
  uyarısı devam ediyor. Geçmiş sayılan testlere atlamalar dahil değil.
- 15 yeni regresyon: 401/403/429/500, eksik/null/boş/geçersiz token,
  eski cookie, form hata yanıtı ve CLI durma + ortak hata raporu.
- Odaklı auth/flow koşusu **49 passed**. İlk tam koşuda eksik dashboard'lu
  eski stored fixture başarısızdı; fixture tamamlandıktan sonra yukarıdaki
  tam koşu geçti. Üretimdeki HTTP hata kontrolü gevşetilmedi.
- [Test logu](audit/2026-10-05-r2-auth/pytest.log),
  [JUnit](audit/2026-10-05-r2-auth/pytest.xml),
  [davranış ve sınırlar](tools/dom-xss-analyzer/AUTH-LIMITS.md),
  [staj kaydı](staj/2026-10-05-r2-auth.md).

R2 ilk auth guard kabulü tamam; hedefe özel oturum/rol doğrulaması,
fractional rate ve CSRF sıralaması açık.

## K01-min stored yorum vakası — önceki teslim

- Yerel browser deneyi: **5/5 kontrol geçti**, Chrome 154.0.8037.93, Playwright
  1.63.0, Python 3.12.14. Savunmasız HTML'de ayrı okuyucu context'inde canary;
  aynı payload için fix sonrası, JS kapalı, JSON-only ve normal dialog negatifleri.
- Bot R1 raporu reflection/candidate seviyesinde kalır; vaka execution sonucu
  ayrı kaydedilir. Bu çalışma genel R3 execution motorunu tamamlamaz.
- İki HTTP fixture regresyonuyla tam paket: **481 passed, 36 skipped, 1 warning**,
  80.33 saniye. Atlamalar eski browser otomatik keşfi, uyarı benchmark utcnow.
- [Vaka ve tekrar üretim](cases/k01-stored-comment/README.md),
  [browser sonuçları](cases/k01-stored-comment/evidence/2026-10-05-verified/result.json),
  [fix diff](cases/k01-stored-comment/evidence/2026-10-05-verified/fix.diff),
  [pytest logu](audit/2026-10-05-k01/pytest.log), [JUnit](audit/2026-10-05-k01/pytest.xml).
- İlk browser denemesi route callback imza hatasıyla başarısız oldu; helper
  düzeltildikten sonraki 5/5 kaydı yayımlandı. Önceki başarısız çıktı yerel audit
  alanında korundu, başarılı deney sayısına katılmadı.

K01-min tamam. Yeni venv kurulumu/bağımsız temiz ortam tekrarı henüz doğrulanmadı;
tam R5'in bu kabul maddesi açık kaldı. Haricî ürün, oturum rolü veya CVE kanıtı yok.

## R1 kabul kapsamı kapanışı — önceki teslim

- Tam paket: **479 passed, 36 skipped, 1 warning**, 87.53 saniye.
- Önceki teslimin üzerine 29 kabul/regresyon örneği: dokuz ayrıştırma sınırı,
  aynı gözlemi kaybetmeden gruplama, bilinmeyen sink/rol, geçersiz şema ve
  kazanılmamış proof/rol iddiaları, maskeleme, ayrı hata/skip olayları, DOM/journal/
  statik/bridge adaptörleri, flow/auth-flow girdi hatası.
- **Gerçek yerel Chrome kontrolü geçti:** normal alert + innerHTML sink; yalnız
  candidate/sink-observed; aynı bulgu kimliği JSON ve HTML'de. Chrome yolu testte
  açık verildi. [JSON](audit/2026-10-05-r1/chrome.json), [HTML](audit/2026-10-05-r1/chrome.html).
- Eski 36 browser testi otomatik binary keşfi nedeniyle atlandı; bunlar geçmiş
  sayılmadı. Uyarı benchmark'taki `datetime.utcnow()` deprecation uyarısıdır.
- Ara kontrol: 259 odaklı test geçti; ilk tam paket 476 geçti. Son üç kapanış
  kontrolünden sonra 479 sonucu alındı. Arada otomatik onay incelemesi kullanım
  limitine takıldığı için bir test komutu hiç çalışmadı; sonuç diye sayılmadı.
- [Tam log](audit/2026-10-05-r1/pytest-r1.log), [JUnit](audit/2026-10-05-r1/pytest-r1.xml),
  [kabul testleri](tools/dom-xss-analyzer/test_r1_contract.py),
  [kapanış matrisi](audit/2026-10-05-r1/R1-KAPANIS.md),
  [resmî sözleşme](tools/dom-xss-analyzer/EVIDENCE-CONTRACT.md).

Bu sonuç R1'in raporlama/kanıt kabul kapsamını kapatır. R2 auth/rate/CSRF,
R3 execution/rol doğrulaması ve R4 benchmark doğruluğu tamamlandı sayılmaz.

## R1 HTTP kanıt modeli — önceki teslim

- Tam paket: **450 passed, 36 skipped, 1 warning**, 76.29 saniye.
- 12 yeni regresyon: yedi Content-Type × beş HTTP yolunun ortak sınıflandırması;
  üç yanlış bağlamda raw marker; encoded flow; gerçek localhost JSON echo üzerinde
  ayrı CLI sürecinin console/JSON/HTML çıktısı ve ortak finding kimliği.
- İlk odaklı çalışmanın sandbox ortamı localhost ve geçici dosyaları engelledi;
  aynı paket gerekli izinlerle **215 passed** verdi. Son JSON/HTML ekleri yukarıdaki
  tam paketle doğrulandı. Test beklentileri execution iddiasını korumak yerine
  reflection semantiğine güncellendi; negatif kontroller ayrıca eklendi.
- 36 browser testi otomatik Chrome keşfi nedeniyle atlandı. Yeni browser proof
  doğrulaması yapılmadı. Tek uyarı benchmark'ın `datetime.utcnow()` kullanımıdır.
- [Log](audit/2026-10-05/pytest-http-evidence.log),
  [JUnit](audit/2026-10-05/pytest-http-evidence.xml),
  [regresyon kaynağı](tools/dom-xss-analyzer/test_http_evidence.py),
  [model ve sınırlar](tools/dom-xss-analyzer/HTTP-EVIDENCE.md).

Genel R1 kapanmadı: DOM/attempt şeması entegrasyonu, sink/rol dedup ve bütün
hata/atlama olaylarının ortak raporu açık. HTTP reflection açıklık kanıtı değildir.

## R1 kalıcı stored blind takip — önceki teslim

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
