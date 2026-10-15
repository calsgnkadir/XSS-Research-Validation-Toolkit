# R5 bağımsız insan tekrarı — sonuç formu

Durum: **BEKLİYOR — bu dosya doldurulmamış teslim şablonudur.**
Otomatik CI ve AI ajanı koşuları ikinci insan kabulünü karşılamaz.
Bu formun depoda bulunması bir tekrarın yapıldığı anlamına gelmez.

## Uygulama

Bağımsız uygulayıcı, [temiz kurulum komutlarını](README.md#temiz-kurulumdan-tekrar-çalıştırma)
kendi temiz checkout ve yeni sanal ortamında uygular. Başlamadan önce commit
ve çalışma ağacını kaydeder. `--profile local` ve yeni bir output dizini kullanır.
Mevcut kanıtı kopyalamak veya yalnız CI sonucunu okumak tekrar sayılmaz.

Başarıda exit 0 ve yeni `acceptance.json` birlikte bulunmalıdır. Başarısız
kurulum/deney de kaydedilir; hata veya timeout, negatif XSS kontrolü değildir.
Üretilen on request/response dosyası, `result.json`, `fix.diff` ve
`acceptance.json` aynı koşuya ait olmalıdır. Browser yolu, kullanıcı adı ve
terminaldeki kişisel yollar paylaşım öncesinde ayıklanır; proof dosyaları
değiştirilirse yeni hashler ve değişiklik gerekçesi ayrıca belirtilir.

## Uygulayıcının dolduracağı alanlar

| Alan | Değer |
|---|---|
| Uygulayıcı takma adı / inceleme referansı (e-posta gerekmez) | BEKLİYOR |
| Tarih ve saat dilimi | BEKLİYOR |
| Tam Git commit hash'i | BEKLİYOR |
| Başlangıç `git status --short` çıktısı | BEKLİYOR |
| Temiz checkout ve yeni venv nasıl oluşturuldu? | BEKLİYOR |
| İşletim sistemi, Python, Playwright, browser sürümü | BEKLİYOR |
| Kullanılan komut (kişisel yollar maskeli) | BEKLİYOR |
| Exit kodu ve kanıt dizini/arşiv referansı | BEKLİYOR |
| Kurulum veya çalıştırma sırasında alınan yardım / sapmalar | BEKLİYOR |

| Kontrol | Beklenen | Gözlenen |
|---|---|---|
| Vulnerable, JS açık | Aynı CID için canary çalışır | BEKLİYOR |
| JS kapalı | Canary çalışmaz | BEKLİYOR |
| Fixed/escaped | Aynı payload ile canary çalışmaz | BEKLİYOR |
| JSON-only | Ham marker XSS execution sayılmaz | BEKLİYOR |
| Normal dialog | Uygulama dialog'u canary proof sayılmaz | BEKLİYOR |
| Cleanup | Beş ayrı fixture portu kapanır | BEKLİYOR |

Uygulayıcı açıklaması: BEKLİYOR. Deneyi kendiniz çalıştırdığınızı, geçmiş
çıktı yerine bu koşunun kanıtlarını verdiğinizi ve farkları açıklayın.

## Koordinatör incelemesi

İnsan çıktısı geldikten sonra commit/gate/source ve proof üye hashleri,
beş kontrolün CID eşlemesi, runtime ve exit sonucu birlikte incelenir.
Arşivden geçmiş socket durumunu yeniden gözlemleyemeyiz; cleanup canlı gate'in
kaydıdır. Temiz ortam ve uygulayıcının bağımsızlığı insan beyanı olarak ayrıca
değerlendirilir; hash eşleşmesi bunu otomatik olarak doğrulamaz.

İnceleme sonucu / kanıt bağlantısı: **BEKLİYOR**.
R5 roadmap kabulü bu alanlar ve gerçek kanıt incelenene kadar açık kalır.
