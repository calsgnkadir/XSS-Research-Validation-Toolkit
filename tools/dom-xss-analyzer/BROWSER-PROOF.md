# R3 — oturumlu yerel browser kanıtı

6 Ekim 2026. `dxaprove.py` HTTP auth→kimlik/rol kontrolü→browser aktarımı→stored
submit→browser read→CID gözlemi→JSON/HTML zinciridir. Loopback R3 kabulü tamamdır;
R4/R9'a taşınan ağ ve CI işleri bu komutun kapsamı değildir.
R1 Finding v1 sözleşmesini değiştirmez: ayrı `dxa-browser-proof/1` kayıtlarında
`execution-observed`, `inconclusive` veya `error` üretir. Execution gözlemi
tek başına confirmed vulnerability, yetki aşımı veya yeni CVE demek değildir.

## Tek komutluk demo

Python 3.10+, `pip install playwright==1.63.0` ve browser gerekir. Depo kökünde:

```console
python -m playwright install chromium
python tools/dom-xss-analyzer/dxaprove.py --demo --output .dxa/r3-demo
```

Windows'ta kurulu Chrome açıkça seçilebilir:

```powershell
python tools/dom-xss-analyzer/dxaprove.py --demo --browser "C:\Program Files\Google\Chrome\Application\chrome.exe" --output .dxa/r3-chrome
```

Demo yeni loopback portunda fixture açar ve sonunda kapatır; yorum yalnız
bellekte tutulur. Yeni output dizini gerekir; önceki kanıtın üzerine yazılmaz.
JSON ve escape edilmiş HTML aynı kayıttan üretilir. Browser bulunmazsa yazma
yapılmadan `browser-start/browser-unavailable`, exit 2 ve hata raporu üretilir.
Inconclusive exit 0 olabilir; otomasyon `status` alanını da kontrol etmelidir.
Linux varsayılan Playwright kurulumu CI'da zorunlu job olarak tanımlandı;
yerel Windows sonucu uzak Linux çalışması kanıtı değildir.

## Başka yetkili yerel lab

`--demo` yerine `--spec config.json` kullan. Bütün URL'ler aynı açık origin'de,
localhost/127.0.0.1/::1 üzerinde olmalıdır. Örnek şema:

```json
{
  "origin": "http://127.0.0.1:8080",
  "auth_flow": {"steps": [{"url": "http://127.0.0.1:8080/login", "method": "POST", "body": {"user": "alice", "password": "LOCAL-LAB-PASSWORD"}}]},
  "session_check": {"url": "http://127.0.0.1:8080/me", "expect": {"$.user": "alice", "$.role": "reader"}},
  "role_path": "$.role",
  "submit": {"url": "http://127.0.0.1:8080/comments", "field": "comment", "csrf_field": ""},
  "read_url": "http://127.0.0.1:8080/comments",
  "variant": "image",
  "observe_ms": 1000
}
```

Auth-flow R2 bearer extraction biçimini de kabul eder. Browser'a sadece bu
akışın oluşturduğu cookie'ler ve açık auth header aktarılır; sayfa trafiğinden
gizli header toplanmaz. Cookie path/secure/HttpOnly korunur; oturum kısa ömürlü
browser context'ine taşınır. HTTP ve browser kimlik kontrolü aynı beklenen
kullanıcı/rolü ister; gönderimden sonra cookie rotation tekrar aktarılıp
browser kontrolü yenilenir. Kontrol başarısızsa sonraki aşama durur.

Form CSRF gerekiyorsa `csrf_field` gerçek hidden input adı olmalıdır; token
yoksa submit durur. Genel header CSRF yenileme ve yakalanan browser header'larının
HTTP'ye geri aktarımı bu komutta henüz yoktur. Config dosyası credential
içerebilir; otomatik raporlanmaz. Raporlarda ham cookie/token/body yoktur.

## Kanıt ve sınırlar

- Rastgele CID HTTP ile gönderilir. Browser payload'ı evaluate etmez; var olan
  `window.__dxaProof` değerini okur. `image` onerror canary'si varsayılandır;
  `href` seçeneği yalnız kendi CID'sinin linkine gerçek tıklama yapar ve
  javascript URL'sinin string completion'ını `void(...)` ile önler.
- Aynı-origin URL'li iframe ve tanımlı gecikme penceresi testlidir. about:blank,
  srcdoc ve cross-origin frame kanıt kapsamı dışıdır. Pencere 100–10000 ms;
  zamanında canary yoksa sonuç inconclusive, güvenli olduğu hükmü değildir.
- Bu yol eval/Function/sink hook kurmaz; doğrudan eval'in lexical scope testi
  geçer. Observer/eval düzeltmesi R3 kabul paketinde testlidir.
- Browser HTTP istekleri ve HTTP redirect'ler tek origin ile sınırlanır;
  service worker kapalıdır. WebSocket ve diğer browser dışı ağ kanalları
  filtrelenmez. Komutu yalnız disposable loopback lab'da çalıştır; bu bir ağ
  sandbox'ı veya gerçek ürün tarama aracı değildir.
- Tek hesap aynı rolle HTTP ve browser'da kullanılır. İki hesap/rol arasında
  privilege boundary testi yoktur; triage daima unreviewed kalır.
- SPA rota kuyruğu ve allowlist header aktarımı kabul edildi. Browser'dan
  otomatik header harvest ve Linux CI sonuç doğrulaması R4 işidir; WebSocket ve
  genel ağ sandboxı R9 operasyon kapsamındadır.

[Test ve demo kanıtı](../../audit/2026-10-06-r3-final/README.md).
