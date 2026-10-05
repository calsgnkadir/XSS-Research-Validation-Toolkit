# Kalıcı blind deneme takibi

29 Eylül 2026 — R1'in stored/stored-auto alt teslimi. Callback bir ağ isteğidir;
JavaScript execution, başka kullanıcının oturumu veya doğrulanmış açıklık değildir.

## Yerel kullanım

Depo kökünden callback sunucusunu ayrı terminalde başlat:

```console
python tools/dom-xss-analyzer/dxa_callback.py --port 9999 --db .dxa/callbacks.db
```

Kendi yerel laboratuvarındaki gerçek gönderim ve okuma yollarını kullan:

```console
python tools/dom-xss-analyzer/dxadyn.py --stored --target http://127.0.0.1:8090/submit --target-field body --check http://127.0.0.1:8090/read --variants blind-img --blind-callback http://127.0.0.1:9999 --blind-journal .dxa/blind-attempts.sqlite3 --session-role editor --html .dxa/scan.html
```

`/submit`, `/read` ve `body` örnektir; bu komut hazır bir lab kurmaz.
CLI journal yolunu ve `run_id` değerini gösterir. `--auto-check` ile de çalışır.
Tarama bitince veya daha sonra callback sunucusunu yeniden sorgula:

```console
python tools/dom-xss-analyzer/dxa_attempts.py --journal .dxa/blind-attempts.sqlite3 --blind-callback http://127.0.0.1:9999 --json-out .dxa/blind-result.json --html .dxa/blind-result.html
```

İsteğe bağlı `--run-id ID` yalnız bir taramayı seçer. Callback adresi kayıttaki
adresle eşleşmelidir; farklı adres sıfır kayıt döndürür. Bu komut hedef sayfayı
ziyaret etmez, payload göndermez; her CID için bir `/hits/<cid>` sorgusu yapar.
`--timeout` sorgu başına ağ zaman aşımıdır (varsayılan 2 saniye), bekleme penceresi
değildir. Yeni callback için komutu tekrar çalıştır. Çıkış kodu 0 sorgular tamamlandı,
2 sorgu/argüman/dosya hatasıdır; 0 hedefin güvenli veya savunmasız olduğunu söylemez.

## Kaydın anlamı

- Her blind deneme gönderimden önce SQLite'a commit edilir; CID tekildir.
- `prepared`: gönderime hazırlanıldı. Süreç burada kesilirse isteğin gidip gitmediği bilinmez.
- `response-received`: HTTP yanıtı alındı; 403 gibi reddedilme kodları ayrıca korunur.
- `error`: gönderim sonucu alınamadı veya istisna oluştu. Uzak sistemin isteği hiç
  işlemediği sonucunu çıkarmak mümkün değildir.
- `candidate`: deneme kaydı var; açıklık kanıtı yok. Yansıma görülmeyen deneme kaybolmaz.
- `resource-callback`: CID ve zaman eşleşen HTTP isteği var; JS proof yok.
- `not-queried`, `no-hit`, `query-error`, `matched` callback sorgusunun durumlarıdır.
  Son sorgu başarısız olsa da önceki callback kanıtı korunur.
- `session_role` operatör etiketidir; araç bu rolün oturumunu doğrulamaz.
- Zamanlar Unix saniyesidir. Callback sunucusu ve istemci saatleri senkron olmalıdır.
  Denemeden eski veya istemci saatinden 5 saniyeden fazla ilerideki hit kabul edilmez.

## Kapsam ve gizlilik

Journal payload, form değerleri, header/cookie, callback gövdesi, IP, UA veya Referer
saklamaz. Hedef URL'de kullanıcı bilgisi, query değerleri ve fragment çıkarılır;
hostname, path, query anahtarları, alan adı ve operatör rol etiketi korunur. Bunlar
da hassas olabilir: yayınlamadan önce incele. `.dxa/` Git tarafından yok sayılır.
Callback sunucusunun kendi veritabanı ayrı, daha geniş bir ham kayıttır.

Journal, gönderim/callback kaydıdır; bulunan bütün reflection/sink URL'lerini
arşivlemez. Tarama sırasındaki başarılı `--blind-wait` eşleşmesi journal'a da
yazılır. Canlı poller sorgu hatasını ortak raporun events listesine yazar;
journal'daki callback_state için ayrıntılı güncellemeyi yukarıdaki ayrı kontrol
komutu yapar. Canlı başarısız sorguda journal `not-queried` kalabilir.

JSON ve HTML kontrol raporu aynı [R1 Finding/ReportEvent modelinden](EVIDENCE-CONTRACT.md)
çıkar. JSON `attempts`, ortak `findings` listesinin uyumluluk alias'ıdır;
SQLite journal depolama formatı korunmuştur. Browser execution ve doğrulanmış
rol R2/R3 işleridir; ortak rapor ve konservatif dedup R1'de tamamlandı.
Kayıt ekleme hatası gönderimi durdurur; journal yazılamıyorsa sessizce taramaya geçilmez.

Regresyonları çalıştır:

```console
python -m pytest tools/dom-xss-analyzer/test_blind_journal.py -q
```

Testler yalnız yerel HTTP fixture'ları kullanır. Ayrı tarama ve uzlaştırma
süreçleri arasındaki callback ile hedefin yalnız bir POST aldığını denetler.
