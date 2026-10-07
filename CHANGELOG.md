# Değişiklik kaydı

## Unreleased — 2026-10-07

- R3/R4 yeniden doğrulaması: 681 passed, sıfır skip; gerçek Chrome strict
  corpus 9/9, TP=3 FP=0 FN=0. Önceki R3/R4 commitleri de yeniden incelendi.
- Cleanup exception sonrasında browser kapanışı ve HTTP oturum durumunun
  restorasyonu nested finally ile korunur; iki yeni gerçek browser regresyonu.
  JSON/HTML demo testi tam kanıt nesnesi eşitliğini doğrular.
- Ayrı CLI'da gerçek lab vaka hatası kalan vakayı/raporu kesmez; strict exit 1
  ve listener temizliği doğrulandı. Genel R4 ve uzak Linux CI kabulü açık.
- R4 proof vaka istisnası artık kalan vakaları ve JSON/Markdown yazımını kesmez;
  error/timeout skorlanmaz, strict kapısı başarısız döner. Ham exception mesajı
  dışarı aktarılmaz; süreç kesme sinyalleri korunur. Yeni kabul 146 passed ve
  gerçek Chrome CLI 9/9; hard timeout ve uzak CI kabulü açık.
- R4 loopback corpus 9 vakaya genişletildi; bağımsız oracle, eşleşen gerçek
  resource callback, title/textarea negatifleri, delayed/eval pozitifleri eklendi.
- Malformed/çelişkili proof reddedilir; canary okuma hatası tamamlanmış negatif
  sayılmaz. Yeni birleşik kabul 136 passed; strict CLI TP=3 FP=0 FN=0.
- Zorunlu browser CI işi corpus testlerini ve strict benchmark artifact'larını
  içerir; uzak CI sonucu henüz yok. Native çağrılar kaydedildi; Engine/QA
  proje yazma yapılandırması güncellendi, diğer roller salt okunur kaldı.

## Unreleased — 2026-10-06

- Reflected crawler form/link/redirect/CSRF trafiği başlangıç origin'ine
  sınırlandı; boş cookie jar korunuyor. Genel ağ sandbox'ı değildir.
- Direct eval fonksiyon kapsamını bozan hook kaldırıldı; destek sınırı
  ortak JSON/HTML operasyonel olayında gösteriliyor.
- R4 ayrı loopback proof-suite gerçek browser adapter'ını kimlik scorer'ına
  bağlar. Tamamlanmış pozitif miss FN sayılır; hata/eksik kanıt negatif sayılmaz.
  Son birleşik paket 339 passed; dört Chrome vakası TP=1 FP=0 FN=0.

- R3: ayrı `dxaprove` loopback komutu HTTP cookie/bearer auth ve JSON kimlik/rol
  kontrolünü browser'a aktarır, browser'da tekrar sınar; stored submit→read→CID
  execution gözlemini JSON/HTML olarak kaydeder. 21 gerçek Chrome kontrolü.
- Gözlem penceresi sonucu execution-observed/inconclusive/error; R1 Finding v1,
  triage ve role_verified iddiaları genişletilmedi. HTTP origin dışı istekler kapalı.
- R3 kabul kapsamı tamamlandı; WebSocket ve genel ağ sandbox'ı desteklenmiyor.
  Uzak Linux CI sonucu ve browser'dan otomatik header harvest ayrı operasyonlardır.
- R3 tam paket 544 passed, 36 skipped, 1 warning.
- R3 son odaklı Chrome paketi 21/21: SPA route budget, allowlist header ve
  direct eval lexical scope regressions. WebSocket scope dışı bırakıldı;
  Playwright context kapanışı bu denemede takıldı.
- R3 demo fixture'ı, `dxaprove` CLI'ı, sabit Playwright'lı zorunlu browser CI işi,
  audit kanıtı ve staj kaydı eklendi.
- R2 HTTP kabulü tamam: hedefe özel JSON kimlik/rol kontrolü ve rapor meta'sı,
  fractional rate, geçersiz rate reddi, sıralı CSRF/stored işlemleri ve hata olayları.
- Tek cookie jar'da HTTP işlemleri sıralıdır; stored-auto her canary sonrasında
  okur. CSRF'siz stored form açık konfigürasyon ister; benchmark adapter'ı güncellendi.
- 30 yeni kabul testi, zorunlu R1/R2 CI adımı ve kapanış/staj belgeleri eklendi.
  Tam paket 526 passed, 36 skipped, 1 warning. Browser aktarımı R3'te açıktır.

## Unreleased — 2026-10-05

### R2 auth guard ilk teslimi

- Auth adımlarında 2xx dışı yanıtlar sonraki adımı/header kurulumunu durdurur;
  eksik/null/boş ve yapısal token değerleri reddedilir.
- Önceden mevcut cookie yeni login kanıtı sayılmaz. Başarısız form login
  taramayı exit 2 ile durdurur ve istenen ortak hata raporunu yazar.
- 15 regresyon eklendi; eski stored fixture'a eksik oturum kontrollü dashboard
  eklendi. Hedefe özel oturum/rol, rate ve CSRF kabulü açık kalır.

### K01-min vaka paketi

- Yerel stored yorum fixture'ı, savunmasız/düzeltilmiş renderer ve yalnız loopback
  çalışan browser deney script'i eklendi. Aynı canary ile 5/5 kontrol geçti.
- Request/response, ortam sürümleri, kaynak hash'leri, fix diff ve vaka/staj
  belgeleri eklendi. Writeup 01/10/11 güncel vakaya bağlandı; tarihsel raporlar korunur.
- İki HTTP regresyonuyla tam paket 481 passed, 36 skipped. Genel R3 execution
  motoru ve tam R5 bağımsız temiz ortam kabulü tamamlandı sayılmaz.

### R1 kapanışı

- Finding/ReportEvent dataclass sözleşmesi; statik, HTTP, static-guided, DOM ve
  journal adapter'ları. JSON/HTML aynı kimlikleri, gözlemleri ve olayları taşır.
- Dedup gönderim/sink/bağlam/rol sınırlarını korur; bilinmeyen kimliği birleştirmez.
  Yinelenen özgün gözlemler bellekte korunur; paylaşım kopyası maskelenir.
- Ağ/flow/callback/browser/statik hata ve atlamaları ayrı olaylar olarak raporlanır.
- Statik ortak rapor `--json-out`; eski `--json` liste API'si korunur. DOM JSON/HTML
  desteği eklendi. Journal JSON `attempts`, ortak `findings` ile uyumlu alias oldu.
- 29 yeni kabul testi, gerçek Chrome negatif kontrolü, kapanış matrisi ve staj kaydı.
  Tam sonuç 479 passed, 36 skipped; R2/R3 ürün işleri açık.

### Önceki HTTP alt teslimi

- HTTP modları ortak finding üreticisine taşındı; schema_version, finding_id,
  evidence_level ve unreviewed triage alanları tutarlı hale getirildi.
- Raw marker ve breakout varyant adı execution kanıtı sayılmaz. Flow JSON
  yanıtlarında hatalı EXECUTABLE çıktısı kaldırıldı. MIME türleri normalize edilir.
- HTTP modlarına `--json-out`, flow'a HTML raporu eklendi; HTML/JSON aynı finding
  kimliklerini taşır. Yeni sınıflar eski executable/breakout-req etiketlerini değiştirir.
- 12 regresyon, model/kullanım belgesi ve S01 kaydı eklendi. Tam paket 450 passed,
  36 skipped. DOM/attempt entegrasyonu, ayrıntılı hata modeli ve dedup açık.

## Önceki teslim — 2026-09-29

### Kalıcı stored blind takip

- Stored/stored-auto blind denemeleri gönderimden önce SQLite journal'a yazılır;
  yansıma olmadığında CID kaybolmaz. HTTP kodu, hata, attempt/run kimliği ve zaman saklanır.
- Ayrı `dxa_attempts.py` komutu hedefe tekrar göndermeden callback kontrolü yapar;
  eşleşen kayıt `resource-callback` olur. No-hit ve sorgu hatası ayrı görünür.
- JSON/HTML kontrol raporu, kullanım belgesi, 18 regresyon ve S01 çalışma kaydı eklendi.
- Tam test sonucu 438 passed, 36 skipped; genel finding şeması, browser execution,
  doğrulanmış oturum rolü ve diğer modların journal entegrasyonu açık kalır.

## Önceki teslimler — 2026-09-28

### Düzeltildi

- JSON canary gönderimi çözülmüş JSON verisini serializer üzerinden kodlar; kontrol karakterleriyle bozuk JSON üretilmez. Geçersiz şablon, NaN ve substitution sonrası anahtar çakışması HTTP gönderiminden önce reddedilir.
- JSON Content-Type artık istek başına ayarlanır; eşzamanlı JSON görevleri ortak EXTRA_HEADERS'ı değiştirmez. 950 payload round-trip ve yedi ek regresyon senaryosu eklendi; eski quote testi gerçek gönderim fonksiyonunu sınar.

- Callback isteği artık `proven-blind` yerine `resource-callback`; CLI ve HTML başka kullanıcı/JS execution iddiasında bulunmaz. Eksik/boş/uyuşmayan cid eşleştirmesi reddedilir; `evidence_level` kaydı eklenir. Ortak kanıt şeması henüz tamamlanmış değildir.
- `blind-fetch` gövdesi cookie yerine yalnız canary kimliğini gönderir.

- Bare `--dom` ziyaretinde alert/confirm/prompt/beforeunload artık `PROVEN-EXECUTABLE` değildir. `OBSERVED-DIALOG` olarak, taranan bir canary ile doğrulanmadığı açıklamasıyla gösterilir.
- Writeup 11'in JSON-only toplamı 75'ten 50'ye düzeltildi; mahrem'de reflection bulunduğu şeklindeki çelişki giderildi. Ham HTML raporları korundu.

### Eklendi

- Ana proje roadmap'i ve orijinal 76 dosyanın görev eşlemesi; rapor, kanıt, portfolyo, staj ve araştırma/CVE işleri ayrı kabul ölçütleriyle takip edilir.
- Callback için 19 ek regresyon senaryosu: eksik kimlik, beş aile/iki HTTP yöntemi, tarayıcısız HTTP isteği ve HTML metadata escaping. Önceki yanlış proof beklentileri düzeltildi.
- JavaScript kapalı yerel Chrome ile callback sınıflandırma kontrolü; S01 ilk öğrenme kaydı.

- Normal dialog, canary benzeri dialog metni ve dialog olmayan ziyaret için altı CLI regresyon senaryosu.
- Güncel durum, kanıt odaklı roadmap, tarihsel mesaj değerlendirmesi ve doğrulama kaydı.

### Açık

- Yansımasız blind takip, ortak execution kanıt modeli, bağlamsız breakout yükseltmesi, auth/rate/CSRF kusurları, browser entegrasyonu ve benchmark doğruluğu. Flow modundaki JSON response sınıflandırması ayrıca açıktır; bu düzeltme JSON request kodlaması içindir. Ayrıntı: ROADMAP.md.

### Uyumluluk

- `PROVEN_BLIND` sabiti ve yeni callback sonuçlarındaki `proven-blind` etiketi kaldırıldı; tüketiciler `RESOURCE_CALLBACK` / `resource-callback` kullanmalıdır. `upgrade_finding_with_blind_hit` fonksiyon adı çağıranlar için korundu, ancak artık yükseltilmiş açıklık kanıtı anlamına gelmez. Eski HTML çıktıları yeniden yazılmadı.

İlk geliştirme paketi `2703d1a` ile main dalına pushlandı. Sürüm etiketi yayımlanmadı.
README'ye test özeti eklendi; denetim ve doğrulama kanıtları depo içine taşındı.
