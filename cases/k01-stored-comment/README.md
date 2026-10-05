# K01-min — Stored yorum: ham HTML → execution → encoding → retest

5 Ekim 2026. **Yerel eğitim fixture'ı, k01-v1.0.** Gerçek üründe yeni açık/CVE
bulunduğu veya botun genel execution doğrulamasının tamamlandığı iddiası değildir.
Bu vaka, staj araştırmasının güncel ve tekrar çalıştırılabilir teknik çıktısıdır.

## Kısa sonuç

Yorum alanının ürün davranışı düz metin göstermektir. Savunmasız renderer,
kaydedilen kullanıcı metnini HTML içine kodlamadan birleştiriyor. Anonim bir
istemcinin kaydettiği canary payload'ı, ayrı temiz okuyucu browser context'inde
çalıştı. HTML metin bağlamında output encoding uygulandığında aynı payload
çalışmadı; karakterleri silinmeden düz metin olarak kaldı.

| Kontrol | Browser canary | Sonuç |
|---|---|---|
| Savunmasız HTML, JS açık | Beklenen CID | Execution gözlendi |
| Savunmasız HTML, JS kapalı | Yok | Raw marker tek başına JS proof değil |
| Düzeltilmiş HTML, JS açık | Yok | Aynı payload düz metin; img elementi oluşmadı |
| JSON yanıtı, JS açık | Yok | Bot json-only; raw marker XSS proof değil |
| Sıradan uygulama alert'i | Yok | Dialog tek başına canary execution değil |

**5/5 kontrol geçti.** [Makine kaydı](evidence/2026-10-05-verified/result.json),
[fix diff](evidence/2026-10-05-verified/fix.diff). Python 3.12.14,
Playwright 1.63.0, Chrome 154.0.8037.93, Windows üzerinde çalıştırıldı.

## Kaynak → depolama → sink

1. `prove.py` yalnız 127.0.0.1 üzerinde rastgele boş portta yeni fixture başlatır.
2. Yazar istemci `POST /comments` ile `comment` form alanını gönderir. Test sunucusu
   metni yalnız bellekte saklar; HTTP 201 döner.
3. Ayrı Playwright context'i `GET /comments` ile okur. Enjeksiyon bu okuyucuya
   query parametresi veya `page.evaluate(payload)` yoluyla verilmez.
4. [Savunmasız renderer](render_vulnerable.py) metni `<article>` içine ham koyar.
   Payload'daki yerel 404 resmin `onerror` handler'ı yalnız `window.__k01=CID` atar.
5. Test, mevcut `window.__k01` değerini okuyup rastgele tarama CID'siyle eşleştirir.
   Bu okuma payload çalıştırmaz. Pozitif kontrolde canary için en çok 3 saniye beklenir.

İki ayrı gerçek kullanıcı hesabı veya doğrulanmış rol yoktur. Yazar HTTP istemcisi
ve temiz okuyucu context'i farklıdır; bu, anonim ortak yorum modelinde stored
yolunu gösterir. Yetkili/admin oturumu, yetki yükseltme veya hassas veri erişimi
kanıtlanmadı. Burada düz metin kuralı olduğu için HTML çalışması by-design değildir.

## Düzeltme ve sınırı

[Düzeltilmiş renderer](render_fixed.py) HTML **metin** bağlamında
`html.escape(comment, quote=True)` kullanır. Girdi saklama biçimi aynı kalır;
değişiklik çıktı noktasındadır. Retest aynı CID ve payload ile yapılır.

Bu düzeltme JS string, CSS veya URL bağlamları için evrensel çözüm değildir.
HTML zengin metin desteği istenseydi farklı bir ürün sözleşmesi ve sanitizer
politikası gerekirdi. Fixture özellikle düz metin yorumla sınırlıdır.

## Temiz kurulumdan tekrar çalıştırma

Python 3.10+ ve Git gerekir. Depo kökünden; aşağıdaki Windows komutlarında yeni
bir sanal ortam ve kanıt klasörü kullanılır:

```powershell
python -m venv .venv-k01
.venv-k01\Scripts\python -m pip install -r cases/k01-stored-comment/requirements-proof.txt
.venv-k01\Scripts\python -m playwright install chromium
.venv-k01\Scripts\python cases/k01-stored-comment/prove.py --output .dxa/k01-new-run
```

Linux/macOS'ta `.venv-k01/bin/python` kullanılır. Alternatif olarak kurulu Chrome
yolunu ver; depodaki kanıt bu seçenekle üretildi:

```powershell
python cases/k01-stored-comment/prove.py --browser "C:\Program Files\Google\Chrome\Application\chrome.exe" --output .dxa/k01-chrome-run
```

Normal Python çalıştırmasını kullan; `-O` ile assertion kontrollerini devre dışı
bırakma. Output dizini önceden varsa komut durur; önceki kanıtı ezmez.
Browser/Playwright yoksa deney başarısız olur, geçmiş sayılmaz. Ağ dış hedefe
yöneltilemez; browser istekleri fixture origin'iyle sınırlandırılır.

Depodaki çalışmada mevcut Python/browser ortamı kullanıldı; yukarıdaki yeni venv
kurulumu bağımsız bir ikinci kişi tarafından henüz denenmedi. Bu yüzden K01-min
vaka teslimi tamam, tam R5 temiz-ortam kabulü ayrı doğrulama bekler.

## Kanıt dosyaları ve tekrar test

Her kontrol için form request JSON'u, HTTP response metni, HTTP bot sınıflandırması,
browser canary sonucu ve tek POST sayacı saklanır. `result.json` çalıştırılan
script/renderer SHA-256 değerlerini, ortam sürümlerini ve aynı payload'ı içerir.
Request/response dosyaları yalnız sentetik CID içerir; token, cookie veya gerçek
kullanıcı verisi yoktur. Hash değerleri o çalışmadaki dosya baytlarına aittir.

Negatif browser kontrolleri load sonrası 500 ms gözlem penceresidir; yalnız bu
senkron fixture'ı kapsar. Genel gecikmeli/iframe XSS yokluğu sonucu çıkarılmaz.
JSON ve normal dialog kontrolleri eski yanlış proof davranışına karşı negatif
örneklerdir; ilgili bot düzeltmeleri R1'de yapılmıştı, bu teslimde tekrar yapılmış
gibi sayılmaz. R1 sözleşmesine `execution-confirmed` enjekte edilmez; case-specific
browser sonucu ayrı alandadır. Fixture kapanınca bellek verisi silinir.

Pytest kurulu ortamda HTTP regresyonları:

```console
python -m pytest cases/k01-stored-comment/test_fixture.py -q
```

[Ana roadmap](../../ROADMAP.md), [R1 sözleşmesi](../../tools/dom-xss-analyzer/EVIDENCE-CONTRACT.md),
[staj kaydı](../../staj/2026-10-05-k01-vaka.md).
