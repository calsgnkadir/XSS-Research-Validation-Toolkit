# Değişiklik kaydı

## Unreleased — 2026-10-05

- HTTP modları ortak finding üreticisine taşındı; schema_version, finding_id,
  evidence_level ve unreviewed triage alanları tutarlı hale getirildi.
- Raw marker ve breakout varyant adı execution kanıtı sayılmaz. Flow JSON
  yanıtlarında hatalı EXECUTABLE çıktısı kaldırıldı. MIME türleri normalize edilir.
- HTTP modlarına `--json-out`, flow'a HTML raporu eklendi; HTML/JSON aynı finding
  kimliklerini taşır. Yeni sınıflar eski executable/breakout-req etiketlerini değiştirir.
- 12 regresyon, model/kullanım belgesi ve S01 kaydı eklendi. Tam paket 450 passed,
  36 skipped. DOM/attempt entegrasyonu, ayrıntılı hata modeli ve dedup açık.

## Önceki teslim — 2026-09-29

### Kalıcı stored blind takip

- Stored/stored-auto blind denemeleri gönderimden önce SQLite journal'a yazılır;
  yansıma olmadığında CID kaybolmaz. HTTP kodu, hata, attempt/run kimliği ve zaman saklanır.
- Ayrı `dxa_attempts.py` komutu hedefe tekrar göndermeden callback kontrolü yapar;
  eşleşen kayıt `resource-callback` olur. No-hit ve sorgu hatası ayrı görünür.
- JSON/HTML kontrol raporu, kullanım belgesi, 18 regresyon ve S01 çalışma kaydı eklendi.
- Tam test sonucu 438 passed, 36 skipped; genel finding şeması, browser execution,
  doğrulanmış oturum rolü ve diğer modların journal entegrasyonu açık kalır.

## Önceki teslimler — 2026-09-28

### Düzeltildi

- JSON canary gönderimi çözülmüş JSON verisini serializer üzerinden kodlar; kontrol karakterleriyle bozuk JSON üretilmez. Geçersiz şablon, NaN ve substitution sonrası anahtar çakışması HTTP gönderiminden önce reddedilir.
- JSON Content-Type artık istek başına ayarlanır; eşzamanlı JSON görevleri ortak EXTRA_HEADERS'ı değiştirmez. 950 payload round-trip ve yedi ek regresyon senaryosu eklendi; eski quote testi gerçek gönderim fonksiyonunu sınar.

- Callback isteği artık `proven-blind` yerine `resource-callback`; CLI ve HTML başka kullanıcı/JS execution iddiasında bulunmaz. Eksik/boş/uyuşmayan cid eşleştirmesi reddedilir; `evidence_level` kaydı eklenir. Ortak kanıt şeması henüz tamamlanmış değildir.
- `blind-fetch` gövdesi cookie yerine yalnız canary kimliğini gönderir.

- Bare `--dom` ziyaretinde alert/confirm/prompt/beforeunload artık `PROVEN-EXECUTABLE` değildir. `OBSERVED-DIALOG` olarak, taranan bir canary ile doğrulanmadığı açıklamasıyla gösterilir.
- Writeup 11'in JSON-only toplamı 75'ten 50'ye düzeltildi; mahrem'de reflection bulunduğu şeklindeki çelişki giderildi. Ham HTML raporları korundu.

### Eklendi

- Ana proje roadmap'i ve orijinal 76 dosyanın görev eşlemesi; rapor, kanıt, portfolyo, staj ve araştırma/CVE işleri ayrı kabul ölçütleriyle takip edilir.
- Callback için 19 ek regresyon senaryosu: eksik kimlik, beş aile/iki HTTP yöntemi, tarayıcısız HTTP isteği ve HTML metadata escaping. Önceki yanlış proof beklentileri düzeltildi.
- JavaScript kapalı yerel Chrome ile callback sınıflandırma kontrolü; S01 ilk öğrenme kaydı.

- Normal dialog, canary benzeri dialog metni ve dialog olmayan ziyaret için altı CLI regresyon senaryosu.
- Güncel durum, kanıt odaklı roadmap, tarihsel mesaj değerlendirmesi ve doğrulama kaydı.

### Açık

- Yansımasız blind takip, ortak execution kanıt modeli, bağlamsız breakout yükseltmesi, auth/rate/CSRF kusurları, browser entegrasyonu ve benchmark doğruluğu. Flow modundaki JSON response sınıflandırması ayrıca açıktır; bu düzeltme JSON request kodlaması içindir. Ayrıntı: ROADMAP.md.

### Uyumluluk

- `PROVEN_BLIND` sabiti ve yeni callback sonuçlarındaki `proven-blind` etiketi kaldırıldı; tüketiciler `RESOURCE_CALLBACK` / `resource-callback` kullanmalıdır. `upgrade_finding_with_blind_hit` fonksiyon adı çağıranlar için korundu, ancak artık yükseltilmiş açıklık kanıtı anlamına gelmez. Eski HTML çıktıları yeniden yazılmadı.

İlk geliştirme paketi `2703d1a` ile main dalına pushlandı. Sürüm etiketi yayımlanmadı.
README'ye test özeti eklendi; denetim ve doğrulama kanıtları depo içine taşındı.
