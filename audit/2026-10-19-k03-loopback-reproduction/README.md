# K03 SQLi, JWT ve BOLA loopback tekrarı — 19 Ekim 2026

## Amaç ve tarihsel sınır

K03 envanterinde eksik kalan üç alanı, izinli yerel OWASP Juice Shop laboratuvarında tekrar gözlemledim. Bu paket yeni bir laboratuvar tekrarını kaydeder; eski Juice Shop oturumunun tarihini, sürümünü veya HTTP alışverişini geriye dönük doğrulamaz. Writeup 03–05'teki tarihsel olaylar yazar beyanı olarak kalır.

Hedef `OWASP Juice Shop 20.2.0`, Docker image ID `sha256:0cec496d878c6855a1c81694c9f91564082f418b84aece87538adb8850d2437e`. Konteynerde mount yoktu. İlk, dış ağa bağlı deneme image başlangıç health-check'inde alchemy.com erişilebilirliğini yokladı; deney istekleri yapılmadan bu konteyner durduruldu. İstek deneyleri `dxa-k03-internal-20261019` konteynerinde, Docker `--internal` ağı (`internal=true`) ve host'a publish edilmemiş port ile yapıldı. İstekler uygulama konteynerinin `127.0.0.1:3000` loopback'ine gitti. Dış hedef isteği gönderilmedi; dış health-check başarısız oldu. Test konteyneri durduruldu; izole Docker ağı kullanılmadan kayıt için boş duruyor, arka plan servisi çalışmıyor.

Ham HTTP capture; bu test için oluşturulmuş iki sentetik hesabın parolalarını, bearer/cookie token'larını ve yanıt gövdelerini içerir. Ham JSON yalnız yerel, gitignore kapsamındaki `.dxa/k03_private_capture_20261019.json` dosyasındadır ve **paylaşılmamalı/commit edilmemelidir**. Son koşudaki SHA-256: `f8858b7340f7bf4443ab94a2baa7494c43be9c241ab9aee3c0f7083c1e7d274f`. Eşlik eden `capture_local.js` her koşuda sentetik hesap ve parolaları rastgele üretir; ham dosyayı konteynerin `/tmp` dizinine yazar, konsola yalnız aşağıdaki gizli verisiz sonucu basar. Script SHA-256: `b85503c50e6942d5a05d6d5d8c37f979bc9679af8fb9869367ce51669c03a047`. Kaynak kodu ve lab sürümüne ait provenance hash'leri aşağıdadır.

## Maskeli gözlem özeti

| Alan | İstek / kontrol | Gözlenen | Sonuç sınırı |
|---|---|---|---|
| SQLi | Yanlış parolalı normal login: `POST /rest/user/login` | 401 | Negatif kontrol |
| SQLi | Login email alanında tarihsel şekil `' OR 1=1--`, yanlış parola | 200; ayrı `/rest/user/whoami` yanıtındaki email yerel admin hesabıyla eşleşti | Bu image'da login SQLi tekrarlandı. Sürüm/istek, tarihi belirsiz yazı 03 olayından ayrıdır. Kaynak `build/routes/login.js`, `req.body.email` değerini SQL metnine interpolate ediyor. |
| JWT | JWT `alg:none`, `data.id=1`, admin email; `GET /rest/user/whoami` | 200; yanıt kimliği admin ile eşleşti | Bu image'ın verifier'ında imzasız token kabul gözlemi. Değiştirilmiş RS256 imzası kontrolünde kimlik boş kaldı. Eski HS256 denemesinin neden başarısız olduğunu açıklamaz. |
| BOLA | A ve B ayrı sentetik hesaplar olarak kaydedildi; login sonrası `whoami` yanıtları hesapları ayırdı. B hesabına ürün eklendi. | A kendi sepetini 200 ile; aynı oturum B sepetini 200 ile okudu. İkinci yanıtta `UserId` B'ye eşleşti ve B'nin eklediği ürün döndü. Oturumsuz aynı okuma 401 verdi. | İki hesap/sahiplik ve negatif kontrol mevcut. Bu kontrollü yeni image davranışıdır; tarihsel ID 1–4 sonuçlarını doğrulamaz. |

Kontrol betiği B hesabının sepetine bir ürün ekler. Bu adım ikinci hesaba ait nesnenin yalnız boş sepet metaverisi değil, ona eklenen kontrollü laboratuvar kaydını içerdiğini gösterir. Gerçek kullanıcı verisi kullanılmadı.

## Tekrar üretim ve provenance

`capture_local.js` scriptini aynı 20.2.0 image ile dış egress'i kapalı, loopback-only laboratuvarda çalıştır. Örneğin betiği konteynere `docker cp` ile koyup `/nodejs/bin/node /tmp/k03_capture.js` biçiminde çalıştır. Betik her HTTP request/response çiftini konteynerde `/tmp/k03-private-capture.json` içine yazar; bu dosyayı yalnız gitignore kapsamındaki `.dxa/` klasörüne kopyala. Konsola token veya parola yazmaz. Kaydedilen ham capture'ın SHA-256 değeri bu audit'tedir. Bu sonuç tarihi eski hedefin değil, image digest ve kaynak hash'leri aşağıda verilen 20.2.0 tekrarının kanıtıdır.

| Image içi kaynak | SHA-256 |
|---|---|
| `package.json` | `e582b8e132fb6fa82e10f496e8ee55c8d9617f4ba19fc50ad87547bf8d281d87` |
| `build/routes/login.js` | `047045a8bbb4fd8a5af1f34e8339a37edb59d7dca9d5e5f6ec22044fd8b8c721` |
| `build/routes/basket.js` | `2ecc5259f8886d720d27899e69083e60cbc9482348e3c3ef662b706a3f266787` |
| `build/routes/currentUser.js` | `27efa0973dd94127a2938b34a2017edcce5923b2fde861f79dd3dda8a3e25e42` |
| `build/lib/insecurity.js` | `0f21e927a94a4cb9116f77b8bd7b883f5ba53813971bbfd8393f998e0fc63a0d` |

Bu test çalışmasında SQLi, JWT imzasız-token kabulü ve yatay BOLA yerel olarak gözlendi. Test kontrol ağı/paketi dışında genel Juice Shop sürüm davranışı, başka veritabanı/configuration, CVE aidiyeti, yazıların tarihsel sürümü, remediation veya fix/retest iddiası yoktur. K04 savunma önerilerinin eski hedefe uygulandığı kanıtlanmadı. Analyzer/benchmark/CI test paketi bu doküman tesliminde çalıştırılmadı.
