# Değişiklik kaydı

## Unreleased — 2026-09-28

### Düzeltildi

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

- Yansımasız blind takip, ortak execution kanıt modeli, bağlamsız breakout yükseltmesi, auth/JSON/rate kusurları, browser entegrasyonu ve benchmark doğruluğu. Ayrıntı: ROADMAP.md.

### Uyumluluk

- `PROVEN_BLIND` sabiti ve yeni callback sonuçlarındaki `proven-blind` etiketi kaldırıldı; tüketiciler `RESOURCE_CALLBACK` / `resource-callback` kullanmalıdır. `upgrade_finding_with_blind_hit` fonksiyon adı çağıranlar için korundu, ancak artık yükseltilmiş açıklık kanıtı anlamına gelmez. Eski HTML çıktıları yeniden yazılmadı.

Henüz sürüm etiketi, commit veya push yapılmadı.
