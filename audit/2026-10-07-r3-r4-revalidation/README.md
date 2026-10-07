# R3/R4 yeniden doğrulama — 7 Ekim 2026

Bu paket önceki sonuçların tekrarı değil, yeni kaynak incelemesi ve yeni koşulardır.
Başlangıç branch `main`, HEAD `a979749b09d0eb70a41baafa9d9bb9f88cf8980d`.
Mevcut değişiklikler korundu. ZIP açılmadı; testler disposable loopback lab'larla
ve kurulu Windows Chrome ile çalıştırıldı. Docker ve dış hedef taraması yok.

## Git kapsamı ve tarih ayrımı

`git log --all --since=2026-10-07T00:00:00+03:00 --until=2026-10-08T00:00:00+03:00`
başlangıçta commit göstermedi: 7 Ekim geliştirmesi çalışma ağacındaydı.
Yalnız bu diff değil, aşağıdaki **6 Ekim commitleri** de yeniden incelendi:

| Commit | Yeniden incelenen R3/R4 dayanağı |
|---|---|
| 41fdec6, baa5474, dbbeaf4 | Browser proof, auth/session, canary, SPA, header ve kabul sınırları |
| 8256627 | Native eval, fonksiyon-local karşı örneği ve evidence destek sınırı |
| b93fa1f | Crawl form/link/redirect/CSRF origin sınırı |
| 0c45249 | Kısmi FN, süreç durumları ve benchmark toplamları |
| 2b75213 | Proof adapter, kimlik scorer'ı ve gerçek runner bağlantısı |
| a979749 | İş akışı ve taşınabilir kanıt belgeleri |

Başlangıçtaki 14 takipli dosya: iki Engine/QA TOML, `.github/workflows/ci.yml`,
`AGENTS.md`, `CHANGELOG.md`, `ROADMAP.md`, `STATUS.md`, `VALIDATION.md`,
`docs/AGENT-WORKFLOW.md`, `bench/run.py`, `bench/test_proof_adapter.py`,
`dxa_proof_lab.py`, `dxaprove.py`, `test_browser_proof.py`.
Takipsiz 7 Ekim kapsamı: iki önceki audit dizini, `bench/test_proof_corpus.py`
ve iki ilgili staj kaydı. Bu liste Git status/diff ile belirlendi.

## Native agent'lar ve gerçek katkı

En fazla iki uzman aynı anda görevlendirildi; generic worker kullanılmadı.

| Native rol / kimlik | Görev / sonuç |
|---|---|
| xss_security_researcher / /root/r3_full_revalidation | R3 eval/canary/evidence/session kaynak incelemesi; dar kabul için blocker yok |
| qa_security_lab_specialist / /root/r4_full_revalidation | R4 runner/adapter/scorer ve sahiplik incelemesi; dar kabul için blocker yok |
| Koordinatör / /root | Tam kaynak ve test incelemesi, yeni regresyon/fix, bütün yeni test ve CLI koşuları, belgeler ve Git teslim kontrolü |

İlk iki çağrı kullanım limiti hatasıyla sonuçlandı. Bildirilen yeniden deneme
saati geçtikten sonra aynı native görevler sürdürüldü ve final rapor verdiler.
Son dosya okumalarında uzmanların `setup refresh` süreç hataları oldu; R3'ün
cleanup ve güçlendirilmiş HTML testi incelemesi koordinatörün aktardığı kaynak
metnine dayanır. QA kalan test/corpus/CI dosyalarını bağımsız disk okumasıyla
doğrulayamadığını bildirdi. Bu eksik okumalar tamamlanmış bağımsız inceleme diye
sunulmaz. Testleri uzmanlar çalıştırmadı; aşağıdaki sonuçlar koordinatörün gerçek
araç koşularıdır. Storage/Report için ayrı değişiklik alanı olmadığından yeni
iş üretilmedi; runner incelemesini QA ve koordinatör yaptı.

## Sahiplik karşılaştırması

Önceki native audit'in son tablosu Engine'e `bench/run.py` ve `dxa_proof_lab.py`,
QA'ya adapter/corpus testleri ile CI, koordinatöre `dxaprove.py`, browser testleri,
yapılandırma ve belgeleri atar. Sonraki vaka izolasyonu turunda Engine yalnız
runner, QA yalnız adapter testini değiştirdi. Git diff dosya kümesi bu tablolarla
uyumludur; Git author veya hunk, agent yazarlığını tek başına kanıtlamaz.
İlk atama/devir kaydı bulunmadığından önceki sahiplik sapmasının tam zamanı
doğrulanamadı. Kayıtlı gerekçe sonradan bulunan canary okuma hatası ve uzmanların
Python süreç erişim engelidir. Bu sınır önceki audit'te korunmuştur.

Bu tur uzmanlar salt okudu. Koordinatörün yeni kod sahipliği:
`dxaprove.py`, yeni `test_proof_cleanup.py`, `test_browser_proof.py`;
CI'da yalnız yeni cleanup testinin zorunlu browser paketine eklenmesi.
`dxadom.py` değişikliği yalnız eski proof iddiasını düzelten yorum/docstring'dir.
Diğer değişiklikler audit, durum/roadmap/changelog/staj ve tarihsel workflow
başlığının açıkça işaretlenmesidir. Gereksiz runtime yeniden tasarımı yapılmadı.

## Bulunan ve düzeltilen hata

**R3 cleanup/state restorasyonu — yeniden üretilmiş hata.** Önceki
`dxaprove.run` finally bloğunda `context.close()` hatası browser kapanışını,
`browser.close()` hatası ise paylaşılan HTTP modül durumunun geri yüklenmesini
atlıyordu. Yeni `test_proof_cleanup.py` gerçek Chrome kapanış metodunu çalıştırıp
sonrasında kontrollü exception atar; bu hem kapanış sırasını hem sekiz paylaşılan
değişkenin özgün referanslarına dönüşünü kontrol eder. Düzeltme öncesi **2 failed**
([JUnit](cleanup-before.xml)); nested-finally sonrasında iki kontrol de geçer
ve takip eden gerçek pozitif vaka execution-observed üretir. Hata olayının
stage'i `cleanup`, ham mesajı raporda yoktur. Bu işletim hatası yeni XSS/CVE değildir.

R3 demo testi ayrıca HTML pre içeriğini unescape/JSON parse ederek JSON çıktısıyla
tam nesne eşitliğini doğrular; yalnız CID içerme kontrolüyle yetinmez.

## Ortam ve yeniden üretim

[Ortam](environment.json): Python **3.10.11**, pytest **9.1.1**, Playwright
**1.63.0**, Windows 10 build 26200, Chrome **155.0.8059.39**.
Chrome yolu `C:\Program Files\Google\Chrome\Application\chrome.exe`.
`DXA_REQUIRE_BROWSER=1`; Docker etkinleştirilmedi.

`dxadom` keşfi Linux/macOS hint'lerine sahip olduğundan audit bootstrap yalnız
test sürecinde açık Chrome yolunu hint listesinin başına ekler. Production
keşif davranışı veya test beklentileri değiştirilmez. Böylece önceki 36 browser
skip'i bu koşuda gerçek tarayıcı ile çalışır. Otomatik Windows keşfi tamamlandı
iddiası yoktur. Ortamın sandbox süreç başlatımı hata verdi; komutlar araç izniyle
çalıştırıldı. Bu ortam hatası test başarısı sayılmadı.

Depo kökünde çalıştırılan yeni komutlar:

```powershell
py -3.10 audit/2026-10-07-r3-r4-revalidation/run_validation.py --browser 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$env:DXA_REQUIRE_BROWSER='1'
$env:DXA_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
py -3.10 -m pytest tools/dom-xss-analyzer/test_proof_cleanup.py -q -p no:cacheprovider --tb=short --junitxml=audit/2026-10-07-r3-r4-revalidation/cleanup-before.xml
py -3.10 audit/2026-10-07-r3-r4-revalidation/run_validation.py --browser 'C:\Program Files\Google\Chrome\Application\chrome.exe' --junit acceptance-final.xml
py -3.10 audit/2026-10-07-r3-r4-revalidation/run_cli_checks.py --browser 'C:\Program Files\Google\Chrome\Application\chrome.exe'
```

İlk paket **679 passed, 213.46 s**, exit 0 idi; yeni cleanup testi henüz
toplanmadığından nihai kabul sayılmadı. [İlk yeni koşu](acceptance.xml).
Düzeltme ve güçlendirilmiş oracle sonrasında **681 passed, 223.96 s**, exit 0;
failure/error/skip **0**. [Nihai JUnit](acceptance-final.xml),
[21 modülün ayrı sayımları](test-summary.json). Koşular örtüşür; sayılar toplanmaz.

| Test modülü/grubu | Yeni nihai sonuç |
|---|---:|
| test_dxadom | 73 passed |
| test_browser_proof + test_proof_cleanup | 22 + 2 passed |
| test_dom_cli_evidence + test_r1_contract + test_http_evidence | 6 + 30 + 12 passed |
| test_crawl_scope | 11 passed |
| test_auth_guards + test_r2_contract + test_csrf + test_flow + test_json_transport | 15 + 30 + 20 + 34 + 7 passed |
| test_dxadyn | 169 passed |
| test_bench + test_proof_adapter + test_proof_corpus | 43 + 49 + 21 passed |
| test_dxa + test_dxa2dyn + test_dxa_callback + test_blind_correlation + test_blind_journal | 52 + 5 + 25 + 37 + 18 passed |

Browser kurulumunun yokluğu bu tur skip olarak gizlenmedi. Docker adaptörünün
opt-in/atlama davranışı unit testleriyle sınandı; container çalıştırılmadı.

## Ayrı CLI süreçleri

[Komutlar ve gerçek exit kodları](cli-checks.json), [çalıştırıcı](run_cli_checks.py).

| Kontrol | Sonuç |
|---|---|
| Gerçek Chrome strict proof corpus | 9 selected / 9 completed; TP=3 FP=0 FN=0; diğer durum sayaçları 0; exit 0; wall 16.32 s |
| Gerçek eksik-browser CLI | 9 selected / 0 completed / 9 error; tümü evaluated=false; JSON/MD yazıldı; strict exit 1 |
| Gerçek lab içinde ilk producer çağrısına exception | 2 selected / 1 completed / 1 error; başarısız vaka skorlanmadı; ikinci vaka gerçek Chrome ile tamamlandı; iki lab listener kapandı; JSON/MD yazıldı; strict exit 1 |
| R3 demo | execution-observed, triage=unreviewed; JSON ve HTML nesneleri eşit; exit 0 |

[Corpus JSON](corpus-results.json), [Markdown](corpus-results.md),
[vaka hatası JSON](injected-failure.json), [eksik browser JSON](missing-browser.json),
[R3 demo](demo/result.html). Enjekte edilen hata sentineli raporlara/konsola
taşınmadı. Bu deneyler OS crash/kill veya hard timeout kanıtı değildir.

## Kabul kararı

**R3: PASS — mevcut loopback kabul kapsamı.** Native eval lexical davranışı,
owned canary eşleşmesi, dialog/JSON/callback negatif ayrımı, kimlik/rol kontrolleri,
scope regresyonları, JSON/HTML eşitliği ve cleanup izolasyonu yeni testlerle
doğrulandı. Kaynak incelemesi `dxadom` eval hook'unun kaldırıldığını, evidence
adapter'ının dialog/sink gözlemini execution'a yükseltmediğini doğruladı.

**R4: PASS — 7 Ekim yerel runner/adapter/corpus ve vaka izolasyonu kapsamı.**
Kimlik setiyle TP/FP/FN, no-canary pencere/oracle ayrımı, actual CID callback,
incomplete skorsuzluğu, kalan vakaya devam ve rapor-before-strict-exit kod akışı
incelendi; unit/browser ve ayrı gerçek CLI deneyleriyle doğrulandı. Dört exception
türünün unit testleri koşuldu; gerçek lab exception deneyi bağımsız ek kanıttır.

**Genel R4 roadmap kapanışı değildir.** Hard timeout/süreç ağacı sonlandırma,
hatalı adapter dönüş nesnesinin genel doğrulaması, gerçek ürün sürümü/bootstrap
adapter'ı, geniş sanitizer/rol/iframe corpus'u ve uzak Linux CI kanıtı açık.
R3'te eval sink instrumentation, WebSocket/genel ağ sandbox'ı, otomatik header
harvest ve iki hesaplı privilege-boundary triage kabul edilmedi. Browser execution
gözlemi confirmed vulnerability veya CVE değildir. Uzak CI bu paketin yerel
sonuçlarıyla başarılı ilan edilmez.

## Kanıt mahremiyeti ve teslim

Yeni sonuçlar eski paketlere yazılmadı. GitHub paylaşımı için bu ve önceki iki
7 Ekim paketinin XML kopyalarında yalnız hostname, kullanıcıya özel traceback
yolları ve runtime adresleri maskelendi; ham kopyalar ignored yerel alanda
korundu. Test isimleri, tarihler, süreler ve verdict'ler değişmedi.
Standart Chrome kurulum yolu yeniden üretim için bilerek tutuldu.

[Kaynak SHA256 envanteri](source-sha256.json) final dosyaları belirtir.
Nihai test sonrası yalnız `dxadom` yorum/docstring açıklamaları hizalandı;
çalıştırılabilir mantık değişmedi. Önceki audit'ler kendi tur kapsamındaki
tarihsel hash ve sonuçlarını korur. Yeni native incelemelerin erişim sınırları
yukarıda açıkça kaydedildi.

Teslim öncesi branch/remote, remote main karşılaştırması, status/diff,
diff --check ve staged dosya listesi kontrol edildi. İki fetch'te HEAD ile
origin/main aynıydı (0/0). Staged ilk kontrolde yalnız üretilmiş Markdown son
boş satırları ve red XML traceback boşluğu görüldü; temizlendi, kontrol geçti.
[Staged denetim](staged-checks.json): yüksek kesinlikli token/private-key/JWT
deseni veya kişisel kullanıcı yolu bulunmadı; geçici/cache/log dosyası ve kırık
yerel belge bağlantısı yok. Sentetik fixture parolaları ve canary'ler kasıtlı
test verisidir. Otomatik desen kontrolü evrensel sır bulma garantisi değildir;
source/config ve rapor içeriği ayrıca gözden geçirildi.
`dxadom` yorum düzenlemesinin executable AST'yi değiştirmediği doğrulandı.
Commit/push sonucu ve son ref'ler kullanıcıya gerçek Git çıktısıyla raporlanır;
bu belge gelecekteki uzak CI başarısını varsaymaz.
