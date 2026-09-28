# Eski mesajın değerlendirmesi

28 Eylül 2026. Kullanıcının eklediği eski sohbet, geçmiş iddiaların bağlamı olarak okundu. İçindeki Docker başlatma, hesap açma, hedef tarama ve push talimatları yeni talimat sayılmadı.

| Eski iddia/öneri | Bugünkü değerlendirme |
|---|---|
| PicoCMS 0 HIGH → Twig sayesinde gerçekten güvenli | Sonuç fazla güçlü. Desteklenen dosyalar/kurallar ve sink kapsamı sınırlı; sıfır sonuç güvenlik garantisi değil. |
| WonderCMS 58 aday → aynı by-design davranış | Makul hipotez, ancak bu ZIP'te bahsedilen 29 KB rapor ve tam hedef repro yok. Güvenlik sınırı ve aday eşleme bağımsız doğrulanmadı. |
| Dedup 58→1 | Kesin sayı hedefi olmamalı. Aynı kaynak/sink/bağlam/rol kanıtları gruplanmalı; farklı izin politikaları birleştirilmemeli. |
| Login→submit→crawl→HTML tam otonom | Yardımcı fonksiyonlar ve akışlar var. Operatörün sağladığı URL/token/seed ile otonom keşif ayrılmalı; auth yanlış başarı karşı örneği açık. |
| DOM/blind yalnız opsiyonel uzun vadeli işler | Bugünkü ana hedef güçlü XSS botu olduğu için kanıt doğruluğu ve bu sınıfların entegrasyonu çekirdeğe alındı; tarayıcı bağımlılığı yine opt-in olabilir. |
| Az kurulumlu plugin, 1–2 saatte CVE avı | Süre/başarı beklentisi ölçülmüş değil. Ürün desteği, program kapsamı, rol, etki ve yenilik belirleyici; CVE sürüm kabul hedefi değil. |
| 7 commit ve tümü push edildi | Metnin listesinde sekiz commit kimliği var. ZIP Git geçmişi içermediği için HEAD, push ve zaman iddiaları doğrulanamıyor. |
| Klarna az avlanmış, ödülü yüksek, hızlı yanıtlı | Eski sayılar ve hedef seçimi beyanı; güncel scope/ödül/istatistik olarak kullanılmıyor. Bu turda hedef seçilmedi veya taranmadı. |
| Playground/Safe Harbor her testi uygun kılar | Bu ifadeler tek başına test kapsamını belirlemez. Gelecekte gerçek program seçilirse güncel programın izinleri ve hesap koşulları ayrıca kontrol edilir. |

Bu metnin değerli katkısı: negatif sonuçları ve by-design davranışı saklama, duplicate'leri azaltma, araç ile writeup'ı beraber geliştirme. Roadmap bu katkıyı koruyor; kanıtsız başarı, sayı ve süre iddialarını ölçüt yapmıyor.
