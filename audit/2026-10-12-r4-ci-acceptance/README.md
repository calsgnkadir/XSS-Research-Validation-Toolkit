# 12 Ekim — R4/R9 CI artifact kabul kapısı

Başlangıç HEAD/main `471ce977aa843a7286cff8ac86aa993edaf548cf`; bu sohbetin
fetch karşılaştırması 0/0, bu görevde `ls-remote` aynı uzak main'i doğruladı.
Önceden staged STATUS, VALIDATION ve 11 Ekim audit README/remote-delivery
korundu. Kullanıcının güncel **commit/push yapma** talimatı geçerli; index'e
dokunulmadı. Yeni değişiklikler yereldir.

**Sonraki kullanıcı talimatı:** ana ajan incelemesi sonrası commit/push ve
ardından OneDrive dışına taşıma açıkça onaylandı. Yukarıdaki ve aşağıdaki
Git yasağı ifadeleri ilk yerel kabul anına aittir. [Son inceleme](prepush-review.md)
yeni koşu değil, kayıtlı test ve kaynak eşleşmesi kontrolüdür.

## Uzak inceleme ve engel

GitHub API run 38171311413, head 471ce97 ve üç job success sonucunu yeniden
doğruladı. [Metadata](remote-check.json). `r3-browser-proof` artifact
11714213394 indirmesi kimlik doğrulamasız HTTP 401 verdi. GitHub CLI bulunmadı;
computer-use tarayıcı envanteri boştu. Token/parola alınmadı. Artifact
içerikleri indirilmedi, uzak skip veya test toplamı doğrulanmadı. Bu kontrol
yeni bir Linux CI çalıştırması değildir; geçmiş yeşil job genel kabul sayılmaz.

## Kök neden ve somut teslim

- Kaynak incelemesi, R4/R9: `.github/workflows/ci.yml` zorunlu JUnit üretirken
  sıfır-skip içeriğini ayrıca kontrol etmiyordu. Beklenen: zorunlu atlama CI'ı
  düşürür. Yeni `bench/check_ci_acceptance.py:32` kayıtları, sayaçları, zorunlu
  dört modülü ve yinelenen test kimliklerini denetler.
- Kaynak incelemesi, R4: `tools/dom-xss-analyzer/dxaprove.py:299` inconclusive
  için exit 0 döndürebilir. Beklenen: CI demosu eşleşmiş execution içerir.
  Yeni kapı demo proof içeriğini denetler; bağımsız CLI regresyonunda
  inconclusive rapor exit 1 ile reddedildi. Üreticinin CLI sözleşmesi değişmedi.
- Yeni kapı dokuz sabit fixture kimliği/etiketi, nested canary kanıtı,
  satır/skor/toplam tutarlılığı ve callback negatif kontrolünü doğrular.
  Raporun Git commit provenance'ını veya vulnerability triage'ını doğrulamaz.
- Zorunlu `r3-proof` job'ına kapı eklendi. Ayrı opt-in `browser-tests` işinin
  continue-on-error ayarı korundu. Genel browser kapsamı kapatılmadı.

## Native uzmanlar ve sahiplik

| Rol / gerçek çağrı | Özel dosya sahipliği | Sonuç |
|---|---|---|
| Engine `/root/r4_ci_gate` | ci.yml, bench/check_ci_acceptance.py | Uygulama ve CI bağlantısı tamam |
| QA `/root/r4_acceptance_qa` | bench/test_ci_acceptance.py | 72 bağımsız subprocess oracle'ı tamam |
| Koordinatör | İlerleme belgeleri, audit/staj, entegrasyon | Diff/oracle incelemesi, ek negatif test geri bildirimi, gerçek Chrome ve birleşik kabul |

İki rol gerçek `agent_type` ile çağrıldı; en fazla iki uzman eşzamanlı çalıştı.
Kalıcı TOML dosyaları değişmedi. Sandbox helper setup hatası, ardından standart
yükseltilmiş komutlarla başarılı okuma/test ve apply_patch yazmaları ayrı
runtime kanıtlarıdır. İki uzman görevi tamamlandı; arka planda çalışma yok.

## Yeni yerel kabul

Windows, Python 3.10.11, pytest 9.1.1, Playwright 1.63.0,
Chrome 155.0.8059.39. Docker ve dış hedef taraması yok.

- [Browser JUnit](browser-acceptance.xml): **94 passed, 93.37 s**, sıfır
  failure/error/skip. Zorunlu CI'daki dört test modülü gerçek Chrome ile koştu.
- [Strict corpus](proof.json): **9/9 completed, TP=3 FP=0 FN=0**;
  error/timeout/skipped/invalid/inconclusive sıfır. [Markdown](proof.md).
- [Demo](demo/result.json): execution-observed; [HTML](demo/result.html).
- [Birleşik JUnit](integration.xml): **185 passed, 23.24 s**, sıfır
  failure/error/skip. QA'nın 72 testi bu sayıya dahildir.
- Yeni kapı gerçek browser/JUnit/corpus/demo çıktısını exit 0 ile kabul etti.
  [Komut sonuçları ve SHA-256](acceptance.json). Hash'ler birleşik koşu boyunca
  sabit; bu manifest daha önce aynı oturumda yapılan browser koşusu öncesinde
  alınmış hash olarak sunulmaz. 11 Ekim manifestindeki 28 giriş, geliştirme
  öncesi kontrol anında eşleşti; bu yeni tam ürün testi değildir.

Browser ve demo komutları (depo kökü, mevcut kanıtın üzerine yazmayın):

```powershell
$env:DXA_REQUIRE_BROWSER='1'
$env:DXA_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
py -3.10 -m pytest tools/dom-xss-analyzer/test_browser_proof.py tools/dom-xss-analyzer/test_proof_cleanup.py bench/test_proof_adapter.py bench/test_proof_corpus.py -q -p no:cacheprovider --tb=short --junitxml=audit/2026-10-12-r4-ci-acceptance/browser-acceptance.xml
$env:BENCH_STRICT='1'
py -3.10 bench/run.py --proof-suite --browser 'C:\Program Files\Google\Chrome\Application\chrome.exe' --no-history --out audit/2026-10-12-r4-ci-acceptance/proof.md
py -3.10 tools/dom-xss-analyzer/dxaprove.py --demo --browser 'C:\Program Files\Google\Chrome\Application\chrome.exe' --output audit/2026-10-12-r4-ci-acceptance/demo
py -3.10 audit/2026-10-12-r4-ci-acceptance/run_validation.py
```

run_validation.py mevcut acceptance/integration dosyalarının üzerine yazmayı
reddeder. JUnit hostname metadata'sı çıkarıldı; sonuçlar değişmedi. Ham
credential/cookie veya kullanıcı profili yolu paylaşım kanıtına eklenmedi.

## Devam noktası

### Sonraki doğrulama — uzak kabul tamam

Kullanıcı izniyle `c5d5451cc81dc94ce65aab330e3925a3a6150c04` commit/push
yapıldı ve uzak main hash'i eşleşti. CI 38233880679 ve yeni zorunlu artifact
kapısı success. [Uzak metadata](remote-delivery.json).

Git Credential Manager'ın mevcut github.com kimliği sadece bellekte kullanıldı;
token çıktıya/dosyaya yazılmadı, imzalı artifact indirme URL'sine aktarılmadı.
Kimlik doğrulamasız 401 engeli böyle çözüldü. Yeni artifact 11740350906 içeriği
indirildi; [arşiv/member hash ve kabul](remote/acceptance.json).
Linux/Python 3.12.15 JUnit **94/0 failure/0 error/0 skip**, strict corpus
**9/9 TP=3 FP=0 FN=0**, demo execution-observed. Yerel kapı bu indirilen
dosyaları exit 0 ile kabul etti. Runner/scanner/fixture SHA-256'ları commit
blob'larıyla eşleşti. JUnit hostname çıkarıldı; ham kopya yalnız yerel .dxa'da.
Corpus hash ortamda eklenen browser_path nedeniyle yerel explicit-Chrome
corpus hash'iyle eşit olmak zorunda değildir; her dosyanın özgün hash'i kayıtlıdır.

Aşağıdaki paragraf ilk yerel kabul anının durumudur; son uzak sonuç yukarıdadır.

Yetkili artifact erişimiyle eski uzak koşunun içerik kabulü bekliyor. Yeni
kapının uzak koşusu da yapılmadı; commit/push yasağı korunuyor. R4 gerçek ürün
bootstrap/login/port-discovery, R9 rapor mahremiyeti ve genel ağ sınırları açık.
Erişim engeli sürerse bağımsız Report mahremiyet işi sırada. ROADMAP kutuları
bu dar yerel teslim nedeniyle kapatılmadı.
