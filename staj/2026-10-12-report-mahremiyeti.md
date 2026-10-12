# 12 Ekim — paylaşım raporunda credential sınırı

R9 incelemesinde ortak JSON/HTML exporter'ın API-key/CSRF alanlarını ve
evidence_links URL sırlarını atladığı sahte değerlerle yeniden üretildi.
Bilinen alan listesi ve URL-listesi temizliği düzeltildi. Girdi değişmezliği,
kanıt kategorileri, HTML escaping ve credential olmayan metadata korundu.

Report uzmanı kod/test yazdı; kullanım limiti sonrası ana ajan incelemeyi
ve doğrulamayı tamamladı. Aynı iki regresyon eski kodda başarısız, yeni
126-test paketinde başarılı oldu. İlk hatalı dosya adı nedeniyle hiç test
koşmayan deneme başarı sayılmadı. Genel maskeleme garantisi verilmedi.

R4'te mevcut GitHub oturumuyla artifact erişimi de çözüldü. Gerçek uzak Linux
JUnit/corpus/demo verisi kontrol edildi; CI yeşilliği ile içerik kabulü ayrı
kaydedildi. [R9 kanıtı](../audit/2026-10-12-r9-report-privacy/README.md).
