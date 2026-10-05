# R1 kanıt sözleşmesi v1

5 Ekim 2026. Resmî model [dxa_evidence.py](dxa_evidence.py) içindeki
`Finding` ve `ReportEvent` Python dataclass'larıdır. Dış bağımlılık gerektirmez.
`normalize()` ve `report()` tüm ortak rapor çıkışlarında modeli doğrular.

## Finding

| Alan | Tip / anlam |
|---|---|
| schema_version | 1 |
| finding_id | Boş olmayan string; aynı JSON/HTML nesnesinin kimliği |
| attempt_id, canary_id | String veya null; bare DOM/statik gözlemde enjeksiyon uydurulmaz |
| source | Gönderim URL/yöntem/parametre veya kaynak dosya/satır nesnesi |
| sink | Okuma URL/kimlik veya kaynak dosya/satır/sink nesnesi |
| context, content_type | String; bilinmeyen değer açık tutulur |
| session_role, role_verified | Operatör rol etiketi; v1'de doğrulanmış rol yok, false |
| evidence_level | candidate, reflection, sink-observed veya resource-callback |
| triage | unreviewed, candidate, by-design, self-xss veya rejected |
| evidence_links | String listesi; kanıt yoksa boş, link uydurulmaz |
| observations | Gözlem nesneleri listesi; dedup sırasında kaybolmaz |

Seviyeler sıralı bir güvenlik etkisi merdiveni değildir. Callback, JavaScript
execution kanıtına dönüşmez. `execution-confirmed` ve doğrulanmış rol mevcut
üreticilerde desteklenmez; v1 doğrulayıcısı bunları reddeder. R3 gerçek proof
üreticisini eklerken sözleşme sürümü ve negatif kontroller birlikte değişmelidir.

Eski flat HTTP/attempt alanları uyumluluk için korunur. Finding kimliği tekrar
taramalar arasında kök neden kimliği değildir. Kaynak/sink şemasında bilinmeyen
özellikler boş/unknown kalır; bilinmeyen kimlik eşit sayılmaz.

## Rapor ve olaylar

Rapor zarfı: `schema_version`, `mode`, `findings`, `events`, `meta`, `skipped_submits`.
Her `ReportEvent` için event_id, observed_at, stage, kind (error/skip/info), reason,
url, status ve canary_id vardır. HTTP erişim hatası, 401/403/429/5xx, probe skip,
flow yükleme/istek hatası, callback sorgu hatası, browser yokluğu/ziyaret hatası ve
statik dosya okuma/keşif/filtre atlamaları bulgulardan ayrı gösterilir.
Bir isteğin HTTP ve probe aşamaları ayrı olay üretebilir; olay sayısı benzersiz
istek veya açık sayısı değildir. Dosyaya yazma izni yoksa rapor üretilemez;
CLI hatası rapor dosyası oluşturulduğu anlamına gelmez.

R2'nin auth başarı kriteri, token/rate/CSRF davranışı değişmedi. R1 hata olayını
görünür yapar; R2 isteğin ve oturumun doğru yürütülmesini düzeltir.

## Dedup ve mahremiyet

Gruplama anahtarı: attempt/cid + gönderim kimliği + sink kimliği/URL + bağlam +
rol + varyant + response türü + reflection/evidence/triage. Bilinmeyen sink veya
rol birleştirilmez. Aynı CID farklı URL'leri aynı açık yapmaz. Aynı anahtardaki
kopyaların özgün gözlem nesneleri bellekte korunur; girdiler değiştirilmez.
Bu konservatif yaklaşım daha fazla satır bırakabilir. Satır sayısını küçültmek
kabul ölçütü değildir; parser tabanlı sink çözümleme R3/R8 genişlemesidir.

Rapor paylaşım kopyasında bilinen header/cookie/token alanları, URL kullanıcı
bilgisi/query değerleri/fragment maskelenir. DOM argümanı/dialog ve statik kod
satırları hassas veri taşıyabileceğinden ortak rapora içerik yerine SHA-256
parmak izi ve konum/olay metadata'sı konur. Hash, içeriğin geri kazanılmasını veya
execution'ı sağlamaz. Yerel kaynak ve browser ham özetleri değiştirilmez.
Dosya yolları, alan/rol adları ve operatör notları hâlâ özel bilgi içerebilir;
maskeleme genel amaçlı bütün sırları bulma garantisi değildir.

## Kullanım ve uyumluluk

- HTTP/DOM: `dxadyn.py ... --json-out report.json --html report.html`
- Statik: `dxa.py SOURCE --json-out report.json --html report.html`
- Statik yönlendirmeli HTTP: `dxa2dyn.py SOURCE URL --json-out report.json --html report.html`
- Blind uzlaştırma: `dxa_attempts.py --journal DB --blind-callback URL --json-out report.json --html report.html`

Statik `--json` eski ham liste API'sidir (dxa2dyn uyumluluğu); ortak ve maskeli
rapor için `--json-out` kullanılır. Journal SQLite formatı aynı kalır;
uzlaştırma JSON'undaki `attempts`, `findings` listesinin uyumluluk alias'ıdır.
HTML ve JSON aynı adapter/model üzerinden aynı kimlikleri ve gözlemleri taşır.

R1'in kalıcı blind gönderim kabul kapsamı stored/stored-auto'dur. Reflected/header
blind gönderimlerin kalıcı journal kapsamı genişletilmedi. Bare DOM visit ve
statik analiz canary göndermediği için attempt kimliği uydurulmaz. Oturumdan
tarayıcıya birleşik gönderim→execution akışı R3'tür.

[Kabul testleri](test_r1_contract.py), [tam doğrulama](../../VALIDATION.md),
[madde bazında kapanış](../../audit/2026-10-05-r1/R1-KAPANIS.md).
