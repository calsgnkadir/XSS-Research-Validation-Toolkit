# R1 kabul kaydı

5 Ekim 2026. Kapsam: gözlemi doğru adlandırmak, ortak rapor sözleşmesi, kabul edilmiş
stored blind takip ve kimliği koruyan dedup. R2/R3/R4/R5'in tamamlanması değildir.

| Kabul koşulu | Uygulama ve doğrulama |
|---|---|
| Bare dialog proof değil | Önceki DOM CLI regresyonları; yeni gerçek yerel Chrome'da dialog→candidate ve sink→sink-observed, ortak JSON/HTML |
| Raw marker executable olmaz | test_http_evidence: yanlış bağlamdaki üç marker; test_dxadyn varyant matrisleri |
| Aynı HTTP response aynı sınıf | Yedi Content-Type × beş HTTP yolu; static-guided JSON karşı örneği |
| Callback yalnız ağ kanıtı | Önceki beş aile/iki HTTP yöntemi regresyonları ve JS kapalı Chrome negatif kontrolü; v1 execution-confirmed reddeder |
| Yansımasız stored CID korunur | test_blind_journal: beş aile, paralel yazma, başarısız gönderim, kalıcı kayıt ve yeniden açma |
| Tarama sonrası ilişkilendirme | İki ayrı CLI süreci; yalnız bir hedef POST, sonradan callback, zaman/run/attempt/rol etiketi |
| Resmî şema ve ortak rapor | Finding/ReportEvent; statik, HTTP, DOM, static-guided ve journal adapter'ları; JSON/HTML kimlik eşleşmesi |
| Hata/atlamalar ayrı | Empty report + timeout/401; browser unavailable; browser hatası; static missing input; flow/auth-flow dosya hatası; journal query-error |
| Dedup kimlik korur | Farklı sink/URL/rol/submit/parametre/context/attempt/evidence ayrı; bilinmeyenler ayrı; aynı anahtar gözlemleri korunur, girdiler değişmez |
| Hassas rapor alanları | Header/cookie ve URL değerleri maskelenir; DOM/statik içerik parmak izi; test sırları JSON/HTML'de bulunmaz |

Komut ve son sonuç [VALIDATION](../../VALIDATION.md) içindedir.
[Kabul testleri](../../tools/dom-xss-analyzer/test_r1_contract.py),
[sözleşme](../../tools/dom-xss-analyzer/EVIDENCE-CONTRACT.md).

Kalan ürün işi: doğrulanmış rol, gerçek canary execution, auth/rate/CSRF,
benchmark FN/error hesabı, kurulum/browser keşfi ve proof→fix→retest vaka paketi.
36 eski browser testinin otomatik keşif nedeniyle atlanması ayrıca görünürdür;
yeni explicit-Chrome kabul testi bunların çalıştırıldığı iddiası değildir.
