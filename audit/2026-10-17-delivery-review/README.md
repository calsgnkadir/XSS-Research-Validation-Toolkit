# Son teslimlerin bağımsız incelemesi — 17 Ekim 2026

İncelenen kaynak: `451361b9f8faef3f328b13468d8d3f6a040c7d2c`.
Başlangıçta `main` temizdi; `git fetch origin` sonrası HEAD/upstream eşit,
ahead/behind `0/0`. Bu tur yeni roadmap uygulaması başlatılmadı.

## Gerçek uzman görevleri

- Native `qa_security_lab_specialist`, `commit_test_audit`: commit diffleri,
  test provenance, yerel kayıtlar ve CI oracle sınırı. Salt okunur; test koşmadı.
- Native `report_frontend_specialist`, `roadmap_evidence_audit`: C/K/P/S
  kapanışları, belge iddiaları ve roadmap sırası. Salt okunur; test koşmadı.
- Koordinatör: Git/uzak CI doğrulaması, yeniden test ve artifact incelemesi.

## Commit incelemesi

| Commit | Doğrulanan kapsam | Genel CI / K01 Linux run ID |
|---|---|---|
| `3a386ee` | İki test fixture/mock düzeltmesi | `38977151511` / `38977151588` |
| `740e5bc` | R9 kabul belgeleri | `38977663772` / `38977663831` |
| `362d4d6` | C/K/P belgeleri/kanıtları; dxadyn footer ve tek regresyon | `38981902539` / `38981902461` |
| `3ef8499` | Hosted CI kayıtları | `38982247229` / `38982247201` |
| `451361b` | P02/P03/S01/S03 ve son test belgeleri | `38984494777` / `38984494765` |

Tablodaki on workflow sonucu GitHub API'den bu tur sorgulandı: hepsi success.
Sorguların daraltılmış sonucu ve son HEAD job/step durumları
[`ci-summary.json`](ci-summary.json) içinde korunur. Son HEAD:
[genel CI](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38984494777),
[K01 Linux](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38984494765).
Son HEAD'in üç genel job'ı ve K01 job/step sonuçları ayrıca success.
Son HEAD ile `3ef8499` arasında analyzer/bench/fixture uygulama farkı yok.
788→789 farkı `test_render_html_json_only_is_reflection_not_execution`
eklenmesiyle tutarlı. Eski başarısız `221baa5` koşusu sonraki başarıyla silinmez.

## Bulgular

1. **C10 editoryal takip:** `writeups/10-one-shape-was-never-enough.md:110`
   eski marker/execution yükseltmesini, `:161` split-cmt parser birleşmesini
   anlatıyor. Giriş, execution iddiasını geri çekiyor ve snippet'in tarihsel
   olduğunu söylüyor; gövdedeki hatalı yaklaşımın yerinde açıkça etiketlenmesi
   hâlâ gerekli. Bu mevcut scanner'ın execution yükselttiği anlamına gelmez;
   güncel `_apply_ct_gate()` varyant adına göre böyle bir yükseltme yapmıyor.
2. **C13 eski durum metni:** `README.md:33` mevcut teslimi yalnız yerel test
   sonucuyla sunuyor; `362d4d6` ve son HEAD için hosted başarı artık doğrulandı.
3. **Düşük önem, tablo:** incelenen HEAD'in `ROADMAP.md` Son kanıt ve teslim
   sırası tablosundaki C/K/P satırı üç başlığa karşı dört hücre içeriyordu.
   İnceleme kaydını işlerken üç hücreye düzeltildi; C10/C13 takipleri işlendi.
4. **Kapanış kapsamı:** `362d4d6` C03/C10/P04 kabul metinlerini de daralttı.
   K03 ham SQLi/JWT/BOLA yeniden üretimi değil kanıt envanteri, K04 tarihsel
   remediation retesti değil dokümantasyon kabulü. P04 yerel kurulum kabulü;
   bağımsız ikinci insan tekrarı gösterilmedi. Eski geniş ölçütlerin tamamı
   karşılanmış gibi sunulmamalı.
5. **Eski çıktı saklama sınırı:** önceki final retest klasöründe yalnız README
   var. Yerel `.dxa/last-r3-r4-pytest.xml` 218/0/0/0 sonucu, smoke/proof JSON'ları
   ve K01 hashleri uzman tarafından doğrulandı; bunlar yeni test koşusu değil.
6. **CI oracle sınırı:** `.github/workflows/ci.yml` tam DOM job'ında
   `continue-on-error: true` kullanıyor. Workflow success tek başına DOM
   kabulü değildir. Bu tur son job'ın kendisi de success olarak sorgulandı.

## Yeni doğrulamalar

Windows/Python 3.10.11, kaynak `451361b`; testler yalnız mevcut yerel
fixture'ları kullanır. İlk sandbox çağrısı Python sürecini başlatamadı;
yetkili çalışma ortamında yeniden çalıştırıldı. Uygulama/test kodu değişmedi.
Sürümler ayrıca sorgulandı: Python **3.10.11**, Playwright **1.63.0**,
pytest **9.1.1**.

```powershell
py -3.10 -m pytest tools/dom-xss-analyzer -q -rs -p no:cacheprovider --tb=short --junitxml=.dxa/review-20261017-analyzer.xml
```

Yeni sonuç: **789 passed, 38 skipped, 0 failed**, 169.74 saniye. 827 test
toplandı. 38 skip'in tamamı `test_dxadom.py` içinde otomatik browser keşfinin
Chromium bulamaması; bunlar başarı sayılmadı. Hostname kaldırılmış
[`analyzer-junit.xml`](analyzer-junit.xml) ve
[`analyzer-skips.json`](analyzer-skips.json) saklandı.

Kurulu Chrome `155.0.8059.82`, Playwright `1.63.0` ile `DXA_BROWSER` açıkça
seçildi ve `DXA_REQUIRE_BROWSER=1` kullanıldı. Tam DOM + gerekli R3/R4 seçimi:

```powershell
$env:DXA_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
$env:DXA_REQUIRE_BROWSER='1'
py -3.10 -m pytest tools/dom-xss-analyzer/test_dxadom.py tools/dom-xss-analyzer/test_browser_proof.py tools/dom-xss-analyzer/test_proof_cleanup.py bench/test_proof_adapter.py bench/test_proof_corpus.py bench/test_proof_identity_matrix.py bench/test_auth_failure_corpus.py bench/test_blind_admin_contract.py bench/test_auth_failure_runner.py bench/test_r4_two_account_fixture.py bench/test_r4_comparison_fixture.py bench/test_r4_cid_oracle.py -q -rs -p no:cacheprovider --tb=short --junitxml=.dxa/review-20261017-browser.xml
```

Yeni sonuç: **298 passed, 0 skipped, 0 failed**, 246.16 saniye. Aynı koşuda
tam DOM **80/80**, diğer 11 dosyalı gerekli R3/R4 seçimi **218/218**.
[`browser-junit.xml`](browser-junit.xml) hostname kaldırılarak saklandı.

CI workflow'undaki 10 dosyalı benchmark/kabul matrisi aynı kaynakta yeniden
çalıştırıldı (`DXA_BROWSER` ve `DXA_REQUIRE_BROWSER=1` ile):

```powershell
py -3.10 -m pytest bench/test_bench.py bench/test_proof_adapter.py bench/test_ci_self_scan.py bench/test_ci_acceptance.py bench/test_bludit_adapter.py bench/test_bludit_ingress.py bench/test_r4_compare_local.py bench/test_r4_comparison_acceptance.py bench/test_r4_scanner_sessions.py bench/test_check_installed_cli.py -q -rs -p no:cacheprovider --tb=short --junitxml=.dxa/review-20261017-benchmark.xml
```

Yeni sonuç: **520 passed, 0 skipped, 0 failed**, 91.74 saniye.
[`benchmark-junit.xml`](benchmark-junit.xml) hostname kaldırılarak saklandı.
Her tarihsel commit için ayrı checkout/test yapılmadı: son kaynak yeniden
test edildi; belirtilen beş teslimin kendi hosted sonuçları ayrıca sorgulandı.

### Son HEAD'in indirilen CI artifact'leri

- R3/R4 artifact `12081943388`, run `38984494777` indirildi. Mevcut
  `bench/check_ci_acceptance.py`, indirilen JUnit/corpus/Markdown/demo üzerinde
  exit 0 verdi: **218 test, sıfır skip/error; corpus 17/17, TP=8 FP=0 FN=0;
  JSON/Markdown provenance eşleşti; demo execution observed**.
- K01 artifact `12082159084`, run `38984494765` indirildi. JUnit **22/22**,
  failure/error/skip sıfır. Acceptance'taki 12 proof hash'i, üç kaynak hash'i
  ve gate hash'i mevcut dosyalarla eşleşti. Beş kontrolün beklenen/observed
  canary sonuçları uyumlu: yalnız vulnerable execution; diğer dördü negatif.
  Kaydedilen ortam Linux/Python 3.12.15/Playwright 1.63.0/Chromium 153.0.8010.12.
  5/5 port cleanup CI'nin kayıtlı sonucudur; bugünkü yerel port durumu uzak
  çalışmanın cleanup kanıtı olarak kullanılmadı. Tam K01 validate fonksiyonu
  bu incelemede yeniden çalıştırılmadı; bu hash/JUnit/kontrol incelemesidir.
- ZIP SHA-256: R3 `5b5a9db5228f7c9e5ca57a3ba4d75b845aec4d4507f792519247cd2331ed5c3d`;
  K01 `2ef486c23af99e2fbe2079ab7701f1c02796378cf9fea73e22e02e31e10225df`.
  Ham paketler yalnız yerel `.dxa/review-451361b-*` altındadır; indirme
  adresleri veya ham HTTP içerikleri paylaşım kaydına konmadı.

R3/R4 bağımsız kabul komutu:

```powershell
py -3.10 bench/check_ci_acceptance.py --junit .dxa/review-451361b-r3/r3-r4-pytest.xml --corpus .dxa/review-451361b-r3/r4-proof.json --corpus-markdown .dxa/review-451361b-r3/r4-proof.md --demo .dxa/review-451361b-r3/r3-proof/result.json
```

Yeni sonuçlar eski 789/38, 520, 218 ve 80 beyanlarından ayrı tutulur.
Farklı paketlerin test sayıları toplanmaz; kontrollü corpus sonucu ürün
doğruluk oranı değildir.

## Bu turun dosya/Git durumu

Uygulama ve test kaynakları değiştirilmedi. İnceleme kanıtı, VALIDATION,
STATUS ve ROADMAP takip bilgileri yerelde güncellendi. Yeni commit/push
yapılmadı; uzak son teslim hâlâ `451361b`. İnceleme başlamadan temiz olan
çalışma ağacı şimdi bu denetim kayıtlarını içeriyor. `git diff --check` geçti.

## Devam sırası

Önce C10/C13 editoryal takipleri ve tablo; sonra S02'nin 11 yazılık
beceri/kanıt matrisi. R7/A01–A05 yetkili ürün/kapsam seçimi bekliyor.
R6 teknik kabulü tamam, tag/dış yayın açık. R8/R9 mevcut sınırlı teknik
kabulünü koruyor. Bu tur ürün doğruluğu, yeni bulgu veya CVE iddiası yok.
