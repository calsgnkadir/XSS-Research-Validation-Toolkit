# R2 auth guard teslimi — 5 Ekim 2026

Bu belge ilk guard tesliminin tarihsel kapsamıdır. 6 Ekim hedefe özel kontrol,
rate ve CSRF kapanışı için güncel [HTTP oturum sözleşmesi](SESSION-CONTRACT.md).

Auth-flow adımlarının son HTTP yanıtı 2xx olmalıdır. 401/403, 429, sunucu
hatası veya bağlantı hatası akışı durdurur; sonraki adım ve header kurulumu
çalışmaz. Normal araştırma `--flow` davranışı bu katı auth kontrolünden ayrıdır.
Redirect'ler mevcut urllib opener tarafından izlenir; redirect origin sınırı
R9'da hâlâ açıktır.

Auth header şablonunda kullanılan JSON değerleri mevcut, boş olmayan skaler
değerler olmalıdır. Eksik/null/boş/bool/object/list değerleri reddedilir;
`Bearer None` oluşturulmaz. Hata mesajı token değerini içermez.
Cookie akışı yalnız önceden mevcut cookie nedeniyle başarılı sayılmaz:
başarılı HTTP adımları yanında yeni veya değeri değişmiş cookie gerekir.
Form login'de 2xx olmayan yanıt başarısızdır; CLI exit 2 ile durur ve
`--json-out`/`--html` istenmişse ortak hata raporu yazar.

**Sınır:** API'deki eski `authenticated` bool alanı oturum kurulumu sezgisidir;
hedefin gerçekten oturum açtığını veya rolünü doğrulamaz. Yeni analytics cookie,
HTTP 200 login hata sayfası veya hata sayfasına redirect hedefe özel kontrol
olmadan güvenilir auth kanıtı olamaz. Bu ikinci R2 maddesi henüz açık.
Cookie rotation aynı isim/değerle olursa katı kontrol başarısız sayabilir.
Başarısız API çağrısı geçmiş oturum durumunu geri almaz; çağıran error sonucunda
durmalı ve farklı kullanıcı denemeleri için ayrı opener/header durumu kurmalıdır.
CLI başarısız login sonrası tarama yapmaz; oturum ayrı CLI çalışmasına taşınmaz.

Yerel HTTP negatif/pozitif kontrolleri: `test_auth_guards.py`, mevcut
`test_flow.py` bearer/cookie ve sonraki isteğe aktarım kontrolleri.
Sonraki sıra: hedefe özel oturum kontrolü ve rol etiketi → fractional rate →
CSRF refresh+submit sıralaması. Genel R2 tamamlanmadı.
