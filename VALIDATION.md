# Doğrulama kaydı — 2026-10-15

## 15 Ekim R4/R5/R6 devam kabulü

Başlangıç `8dd50acb80ed41bb2e44d4f1ab9defa9f1deca09`, Windows/Python 3.10.11.
R4 uzman gate/scorer/identity paketi 233; R5 uzman fixture/gate paketi 22 geçti.
Koordinatör R4/R5 birleşik paket 231 ve R6 etkilenen paket 304 geçti;
paketler örtüşür, toplam benzersiz test sayısı olarak toplanmaz.
Tüm bu koşularda sıfır hata/atlama. R5 yeni gerçek yerel CLI 5/5 kontrol ve
beş ayrı kapalı fixture portu: ikinci insan/fresh venv kabulü değil.
R6 rapor matrisi mock CLI testi; Docker tekrarına ihtiyaç olmadı.
Komutlar, hashler ve kapsam: [devam kabulü](audit/2026-10-15-r4-r5-r6-continuation/README.md),
[R4](audit/2026-10-15-r4-acceptance/README.md), [R5](audit/2026-10-15-r5-handoff/README.md).
Kod 9b6b7c3: genel CI 38640435614 3/3 başarılı; indirilen artifact güncel
gate ile 169 test, corpus14/14 TP7/FP0/FN0, auth6/6 geçti. K01 Linux
38640435613 başarılı; artifact22 test/proof5/5, ci profili ve gate kaynak
hashi doğrulandı. Her iki ZIP digest'i GitHub metadata ile eşleşti.
Uzak kanıtlar devam kabulündeki remote-r4/remote-r5-acceptance.json dosyalarında.

## 14 Ekim R3 header ve R6 CLI/rapor yerel kabulü

Başlangıç HEAD `d91238bfbfeb9736068dc6197738f464b5708312`.
Windows/Python 3.10.11, kurulu Chrome. Koordinatörün gerçek browser
`test_dxadom.py` koşusu **75 passed, 0 skipped**; etkilenen statik/dinamik/
kanıt paketinin birleşik koşusu **293 passed**, sıfır failure/error/skip.
Güncel wheel yeni venv'e kaynak dizini dışından kuruldu; üç CLI help exit 0,
BOM'lu config high exit 0, CLI low override bir adayla exit 1 ve JSON/HTML
aynı bulgu kimliği. Tam komutlar, yerel kaynak SHA-256 ve wheel digest'i
[acceptance.json](audit/2026-10-14-r3-r6-continuation/acceptance.json) içinde.
`git diff --check` geçti. Kod a0cf348 push edildi; genel CI 38637484190
3/3 başarılı. Kurulu CLI/analyzer/required artifact gate/opsiyonel browser
adımları success. K01 Linux 38637484214 başarılı; artifact bu turda
indirilmedi. [Uzak step kaydı](audit/2026-10-14-r3-r6-continuation/remote-ci.json).

## 14 Ekim üç işin bağımsız yeniden denetimi

R8: `py -3.10 -m pytest tools/dom-xss-analyzer/test_r8_sanitizer.py
tools/dom-xss-analyzer/test_static_context.py tools/dom-xss-analyzer/test_dxa.py
-q -p no:cacheprovider --tb=short` — **92 passed**; ilk yeni karşı örnek
eski kodda 1 failure verdi. Python 3.10.11/Windows. R6: mevcut build venv'iyle
wheel oluşturuldu; yeni `.dxa/r6-recheck-venv` içine wheel kuruldu ve kaynak
dizini dışından `dxa`, `dxadyn`, `dxaprove --help` çıkışları 0 oldu. Wheel dokuz
beklenen modülü içeriyor. R5: ayrı agent yeni loopback proof 5/5 yaptı;
12 kanıt ve üç kaynak SHA-256 değeri checkout ile eşleşti. Aynı Windows hostu,
mevcut Python; ikinci insan kabulü sayılmaz.
K01 gate testleri ayrıca `py -3.10 -m pytest cases/k01-stored-comment/test_fixture.py
cases/k01-stored-comment/test_repro_gate.py -q -p no:cacheprovider --tb=short`
komutuyla **13 passed** verdi.
[Komut/ortam/sınır](audit/2026-10-14-three-work-recheck/README.md).
74cda81 için genel CI 38598901908 3/3 başarılı; kurulu CLI, analyzer test
paketi ve zorunlu R3/R4 artifact gate adımları geçti.
[Uzak CI kaydı](audit/2026-10-14-three-work-recheck/remote-ci.json).
K01 Linux 38598901721 başarılı; indirilen artifact digest eşleşti,
JUnit 13/0 failure/error/skip, proof 5/5 ve kaynak/çıktı hashleri eşleşti.
[Uzak K01 kabulü](audit/2026-10-14-three-work-recheck/remote-k01-acceptance.json).
Aşağıdaki d41c1cd koşuları önceki teslimin tarihsel kanıtıdır.

## 14 Ekim R5 Linux gate, R8 ve R6 yerel kabulü

- R5+R8 birleşik etkilenen paket: 104 passed, sıfır failure/error/skip.
  Yeni K01 gate Windows Chrome çıktısında 5/5 ve beş kapalı portu kabul etti.
  [R5 komut/hash](audit/2026-10-14-r5-linux-gate/acceptance.json).
  d41c1cd için Linux run 38596197622 ve indirilen artifact geçti:
  13 JUnit sıfır failure/error/skip, K01 5/5 ve beş kapanan port, arşiv
  digest ve kaynak hashleri eşleşti.
  [Uzak kanıt](audit/2026-10-14-r5-linux-gate/remote-acceptance.json).
  İkinci kişi kabulü açık.
- R8 odaklı statik paket: 91 passed, sıfır failure/error/skip.
  [R8 komut/hash](audit/2026-10-14-r8-rebound/acceptance.json).
  d41c1cd genel CI 38596197488 3/3 başarılı; analyzer test step geçti.
- R6 temiz venv core/browser extra kuruldu; üç entrypoint help ve paketlenmiş
  Chrome demo execution-observed geçti.
  [R6 komut/hash](audit/2026-10-14-r6-package-scaffold/acceptance.json).
  d41c1cd genel CI 38596197488 3/3 başarılı; paket install/help step geçti.
  [CI step kaydı](audit/2026-10-14-r6-package-scaffold/remote-ci.json).
  Release kabulü henüz alınmadı.

## 14 Ekim R5/K01 yeni venv tekrarı

Ayrı QA agentı Python 3.10.11 yeni venv, Playwright 1.63.0 ve kurulu Chrome
155.0.8059.79 ile disposable K01 proof CLI 5/5, exit 0 çalıştırdı.
Koordinatör 12 dosya hashini ve README diffini kontrol etti; fixture portları
5/5 kapalı. [Komut, ortam, hashler](audit/2026-10-14-r5-k01-clean-repeat/acceptance.json).
Bu bir pytest koşusu veya ikinci işletim sistemi kabulü değildir; genel R5 açık.

## 14 Ekim R4 auth kontrol runner entegrasyonu

Koordinatör birleşik etkilenen paket: 215 passed, sıfır failure/error/skip.
Gerçek Chrome runner CLI: altı kontrol ve altı cleanup geçti; ayrı mock
candidate skoru TP=1 FP=0 FN=0. [Komut, ortam, hash](audit/2026-10-14-r4-auth-runner/acceptance.json).
bec59b4 uzak CI 38593458769 3/3 başarılı; artifact digest eşleşti,
169 JUnit sıfır skip/error, proof 14/14 TP=7 FP=0 FN=0, auth controls
6/6 cleanup 6/6 ve canonical JSON/Markdown doğrulandı.
[Uzak kabul](audit/2026-10-14-r4-auth-runner/remote-acceptance.json). Bu sayılar önceki 193/527 koşularının yerine geçmez.

Son auth/blind dar teslim birleşik regresyonu: **193 passed**, sıfır hata/skip.

## 14 Ekim auth/CSRF hata kontrolleri

13 focused test geçti; ayrı sahipli/süre sınırlı CLI altı beklenen hata kontrolünü
6/6 kabul etti. Bunlar XSS TP/TN değildir. [Komut, ortam ve hashler](audit/2026-10-14-r4-auth-blind-controls/acceptance.json).
Yeni uzak CI kabulü bekliyor; önceki 527 sayısı bu yeni dosyaların testi değildir.

## 14 Ekim R4 corpus v3

- Base 61dde5c; Windows/Python 3.10.11, pytest 9.1.1, zorunlu Chrome.
- Bütün bench testleri + test_browser_proof.py + test_proof_cleanup.py:
  **527 passed**, sıfır failure/error/skip.
- BENCH_STRICT=1 gerçek CLI: **14/14, TP=7 FP=0 FN=0**, sıfır incomplete.
  JSON/canonical Markdown eşleşti; önceki 9-vaka sayıları tarihsel kaldı.
- Kaynak/çıktı hashleri, tam komut ve ortam
  [acceptance.json](audit/2026-10-14-r4-corpus-v3/acceptance.json) içinde.
- Docker kodu değişmedi; mevcut ürün kontrol regresyonları bu koşuya dahil.
  Canlı Docker/Bludit tekrar edilmedi. Kod 4331403 için uzak CI 38550538424
  3/3 başarılı; indirilen artifact gate 134 test, sıfır skip/error ve corpus
  14/14 TP=7 FP=0 FN=0 ile geçti. Commit kaynaklarının birebir LF byte
  kopyasıyla doğrulandı; yerel CRLF hashleri korunuyor.
  [Uzak kanıt](audit/2026-10-14-r4-corpus-v3/remote-acceptance.json).


## 14 Ekim R4 strict corpus artifact provenance gate

- Başlangıç commit'i `7ce1927e9ac7c2f24e3bbeccd91c87e7d5a29d60`.
  Windows 10 / Python 3.10.11 / pytest 9.1.1.
- İlk gate: **90/204 passed**. QA follow-up runtime karşı örnekleri eklendikten
  sonra güncel odaklı CI gate: **94 passed**; birleşik benchmark scorer, proof
  corpus ve artifact gate: **208 passed**, sıfır failure/error/skip.
- Gate artık `r4-proof.md`'yi zorunlu alıyor; Markdown çıktısını JSON raporun
  canonical render'ıyla birebir karşılaştırıyor. JSON'daki Python, platform,
  komut ve runner/scanner/fixture/corpus SHA-256 alanlarını geçerli kılıyor;
  source hashlerini checkout dosyalarıyla karşılaştırıyor. Yeni karşı örnekler
  eksik/malformed artifact, stale hash/komut ve JSON-Markdown score/identity
  uyuşmazlığını reddediyor.
- QA, Python/platform değerleri için makul ama CI dışı karşı örnekleri ekledi;
  gate artık Python 3.12/Linux'u zorunlu kılar. `7f67d53` için uzak run
  38475480351 üç job'da success ve indirilen artifact eski gate'ten geçti.
  Runtime sıkılaştırması `3ca474a` push edildi. Yeni run 38530419858 CI 3/3
  başarılı; indirilen artifact güncel gate ile geçti (JUnit 94 sıfır skip/error,
  corpus 9/9 TP=3 FP=0 FN=0, Python 3.12.15/Linux, kaynak hashleri eşleşti).
  [Yeni uzak kanıt](audit/2026-10-14-r4-provenance-gate/runtime-remote-acceptance.json).
- [Komutlar ve kaynak hashleri](audit/2026-10-14-r4-provenance-gate/acceptance.json),
  [yerel/uzak kanıt ve sınırlar](audit/2026-10-14-r4-provenance-gate/README.md).

- Devam koşusu (`7f67d53` + runtime/test diff): JSON ve Markdown birlikte
  değiştirilerek dört runtime regresyonu güçlendirildi. Eski gate bu dört
  yanlış beyanı kabul etti (4 regression failure), güncel gate reddetti (4 pass).
  Son birleşik JUnit: **208 passed**, sıfır failure/error/skip; 94 gate vakası
  bu toplamın içindedir. Kaynak ve JUnit hashleri acceptance.json içindedir.

## 13 Ekim R4 Bludit runner bağlantısı

- `py -3.10 -m pytest bench/test_bench.py bench/test_bludit_adapter.py
  bench/test_bludit_ingress.py bench/test_bludit_runner.py
  bench/test_ci_acceptance.py bench/test_ci_self_scan.py
  bench/test_docker_safety.py bench/test_proof_adapter.py
  bench/test_proof_corpus.py bench/test_runner_isolation.py -q
  -p no:cacheprovider --tb=short`: **434 passed**, sıfır failure/error/skip;
  Python 3.10.11 / Windows.
- Gerçek opt-in `bench/run.py --targets mock-reflected-easy --bludit-control`
  koşusu: mock target ayrı candidate TP=1/FP=0/FN=0 (XSS accuracy değildir);
  Bludit raw/escaped davranışları beklenenle eşleşti, status ve cleanup
  `passed`. Ürün kontrolleri `product_controls` altında kaldı; scanner totals
  değişmedi. [Sanitized sonuç](audit/2026-10-13-r4-runner-live/result.json),
  [tekrar/limitler](audit/2026-10-13-r4-runner-live/README.md).
- Son Docker sayıları 15 container, 27 volume, 9 network; önceki lifecycle
  kabulindeki değerlerle aynı. Adapter kendi geçici projesinin cleanup'ını
  doğruladı. Commit `afcb7c1` için iki uzak CI çalışması 3/3 job success;
  [metadata](audit/2026-10-13-r4-runner-live/remote-delivery.json). Hosted CI
  bu yerel Bludit Docker kabulini çalıştırmadı ve artifact içerikleri bu turda
  incelenmedi.

## 13 Ekim R4 ingress ve gerçek ürün kabulü

- Aktif depo `C:\xss\xss-github`, başlangıç commit'i `02e8805`. Python
  3.10.11 / Windows, yerel Docker Desktop ve pinned Bludit imajı.
- `py -3.10 audit/2026-10-12-r4-ingress-live/run_validation.py`:
  **335 passed, sıfır failure/error/skip**, JUnit, komut ve sabit kaynak
  hashleri [acceptance.json](audit/2026-10-12-r4-ingress-live/acceptance.json).
- Aynı script `--live --browser <yerel Chrome yolu>`: gerçek kurulum, ayrı
  login, iki public browser kontrolü PASS; eksik browser ve enjekte edilmiş
  proof uyuşmazlığı doğru error. Üç cleanup PASS. Eski 15 container, 27 volume,
  9 network kimlik/ad setleri birebir korundu.
  [Live acceptance](audit/2026-10-12-r4-ingress-live/live-acceptance.json).
- Bu yalnız yerel ürün lifecycle kabulüdür; bench scorer ve uzak CI bu imajı
  çalıştırmaz. `e62bf34` için [uzak CI 38404107337](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38404107337)
  üç job success; artifact içerikleri bu koşuda indirilmedi.
  Önceki 268 ve engelli
  denemeler tarihsel kanıttır, bu koşuya eklenmez.

## 12 Ekim R4 ürün adapter taslağı — canlı kabul engelli

- Kod checkpoint'i `db96027` uzak main hash'iyle eşleşti. CI 38302697303 ve
  üç job success; yeni mock adapter regresyonları CI'da geçti. Bu koşunun
  artifact içerikleri indirilmedi, Docker ürün lifecycle'ı CI'da çalışmadı.
  [Uzak metadata](audit/2026-10-12-r4-product-adapter/remote-delivery.json).

- Koordinatör birleşik koşusu **268 passed, 26.46 s**, sıfır failure/error/skip;
  83 bağımsız yeni test bu sayıya dahildir. Python 3.10.11 / Windows.
  Başlangıç `d151a8a` + uncommitted kaynak hash'leri koşu boyunca sabit.
- Gerçek Docker üç başlangıçta `80/tcp: []` nedeniyle port kapısında durdu;
  her seferinde cleanup passed. İlk preflight denemesi normalize boş IPAM
  alanı yüzünden başlangıçtan önce durdu; guard boş IPAM'a göre düzeltildi.
- Gerçek installer/login/browser aşamaları çalışmadı; browser hata/negatif
  davranışı burada yalnız bağımsız mock testleridir. Canlı kabul verilmedi.
- Mevcut 15 container / 27 volume listesi birebir korundu. Yeni ürün adapter'ı
  benchmark scorer'ına bağlanmadı; R4 geniş kapsamı ve CI ürün kabulü açık.
- [Komut/hash/koruma](audit/2026-10-12-r4-product-adapter/acceptance.json),
  [JUnit](audit/2026-10-12-r4-product-adapter/acceptance.xml).

## 12 Ekim son kontrol — R9 uzak CI ve yeni çalışma kökü

- R9 8873aaf push ve uzak hash eşleşmesi; CI 38267306222 ve üç job success.
  [Uzak metadata](audit/2026-10-12-r9-report-privacy/remote-delivery.json).
  Bu koşunun artifact içeriği indirilmedi; R4 indirilen artifact kabulü ayrıdır.
- Yeni C:\xss\xss-github: **95 passed, 15.90 s**, sıfır failure/error/skip;
  bench/test_ci_acceptance.py ve test_report_privacy.py tekrarlandı.
  Önceki 185/126 sayılarına eklenmez. 1076 erişilebilir dosya hash'i ve Git
  durumu kopyalama öncesi/sonrası eşleşti. Kaynak işlem kilidi ve erişilemeyen
  cache nedeniyle eski OneDrive kopyası silinmedi.
  [Kontrol kaydı](audit/2026-10-12-relocation/README.md).

## 12 Ekim devamı — uzak R4 kabulü ve R9 rapor mahremiyeti

- `c5d5451` push ve uzak main eşleşmesi doğrulandı. CI **38233880679 success**;
  yeni zorunlu artifact kapısı success. Mevcut GitHub credential yalnız bellekte
  kullanılarak artifact indirildi; token kaydedilmedi/gösterilmedi.
- Uzak Linux/Python 3.12.15: JUnit **94 passed, sıfır failure/error/skip**,
  corpus **9/9 TP=3 FP=0 FN=0**, demo execution-observed. İndirilen içerik
  yerelde yeni kapıdan exit 0 ile geçti; runner/scanner/fixture hash'leri uzak
  commit blob'larıyla eşleşti. [Kanıt](audit/2026-10-12-r4-ci-acceptance/remote/acceptance.json).
- R9 koordinatör kabulü: **126 passed, 37.09 s**, sıfır failure/error/skip;
  Python 3.10.11 / pytest 9.1.1 / Windows. Yeni privacy, R1, HTTP, DOM CLI ve
  blind/journal regresyonları. [Komut/hash](audit/2026-10-12-r9-report-privacy/acceptance.json).
- Aynı iki privacy regresyonu eski `c5d5451` exporter'ı bellekte yüklenince
  beklendiği gibi **2 failed** verdi; yeni pakette geçiyor. İlk yanlış dosya
  adıyla yapılan denemede test koşmadı; acceptance.xml bu başarısız girişimin
  kaydıdır, acceptance-final.xml 126 testlik gerçek kabuldür.
- Uzman limitinden sonra R9 test ve son inceleme koordinatörce tamamlandı;
  bağımsız R9 specialist QA finali yok. Genel R4/R9 kapatılmadı.

## 12 Ekim 2026 — R4/R9 zorunlu CI artifact kapısı (ilk yerel kabul)

- HEAD `471ce977aa843a7286cff8ac86aa993edaf548cf` + commit edilmemiş değişiklikler.
  Python 3.10.11 / pytest 9.1.1 / Windows / Playwright 1.63.0, Chrome 155.0.8059.39.
- Gerçek zorunlu browser paketi: **94 passed, 93.37 s**, failure/error/skip yok.
  Ayrı strict corpus **9/9 completed, TP=3 FP=0 FN=0**, tüm incomplete sayaçları
  sıfır; ayrı demo execution-observed. Yalnız loopback fixture kullanıldı.
- Koordinatör birleşik kapı/self-scan/bench/adapter regresyonları:
  **185 passed, 23.24 s**, failure/error/skip yok. QA'nın 72 testi bunun içindedir;
  ayrı tekrarlar toplanmaz. Yeni kapı gerçek 94-test JUnit/corpus/demo çıktısını geçti.
- [Komut ve kaynak hash'leri](audit/2026-10-12-r4-ci-acceptance/acceptance.json),
  [kapsam ve browser komutları](audit/2026-10-12-r4-ci-acceptance/README.md).
  Hash'ler birleşik koşu boyunca sabitti; daha önceki browser koşusunun öncesinde
  alınmış yeni hash iddiası yok. JUnit hostname alanları paylaşım için çıkarıldı.
- Uzak `471ce97` CI metadata'sı yeniden success; artifact indirmesi HTTP 401.
  İçerik/uzak skip kabulü yapılmadı. Yeni kapı uzak CI'da çalışmadı;
  commit/push yok. Genel R4/R9 ve ürün adapter'ı açık.

## 11 Ekim 2026 — R9 CI self-scan ve devamlılık

- Yeni koordinatör kabulü: **143 passed, 13.21 s**, exit 0; failure/error/skip
  yok. Python 3.10.11 / pytest 9.1.1 / Windows; browser ve Docker kullanılmadı.
  `bench/test_ci_self_scan.py`, `bench/test_bench.py`, `test_dxa.py` ve
  `test_static_context.py` birlikte çalıştı. Gerçek examples self-scan exit 0.
- Başlangıç commit'i `5df2577` + bu teslimin çalışma ağacı. Test edilen kaynak,
  fixture, CI ve beş agent tanımı SHA-256'ları koşu boyunca sabit:
  [komut/ortam/hash](audit/2026-10-11-continuity/acceptance.json),
  [JUnit](audit/2026-10-11-continuity/acceptance.xml),
  [tekrar üretim script'i](audit/2026-10-11-continuity/run_validation.py).
- QA'nın ayrı 20 testlik koşusu birleşik 143'e dahildir; sayılar toplanmaz.
  Eski Bash gate'in RuntimeError/ModuleNotFoundError'ı exit 0'a çevirdiği
  [yeniden üretildi](audit/2026-10-11-continuity/qa-legacy-gate-retry.json).
- Önceki 9 Ekim paketindeki 43 kaynak hash'i mevcut dosyalarla eşleşti;
  824 testlik eski JUnit incelendi. Yeni tam 824 test koşusu yapılmadı.
- Uzak **başlangıç commit'i** `5df2577` için
  [CI 37934071361](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/37934071361)
  ve üç job başarılı; iki artifact metadata'sı görüldü. İçerik/skip sayısı bu
  kontrolde doğrulanmadı. Bu sonuç yeni değişikliğin uzak CI sonucu değildir.
- [Denetim, görev sahipliği ve kapsam](audit/2026-10-11-continuity/README.md).
- Yeni kod commit'i `471ce977aa843a7286cff8ac86aa993edaf548cf` uzak main ile
  doğrulandı. [Yeni CI 38171311413](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38171311413)
  ve üç job **success**; self-scan/regresyon, zorunlu R3 ve strict R4 adımları
  başarılı. [Job/adım metadata'sı](audit/2026-10-11-continuity/remote-delivery.json).
  Artifact içeriği/skip sayısı ayrıca incelenmedi; indirme API'si HTTP 401 döndü.
  Bu kayıt yerel 143 sonucundan ayrıdır, uzak test toplamı iddia edilmez.

## 9 Ekim 2026 — 8–9 Ekim değişikliklerinin tam tekrarı

- Analyzer ve bench: **824 passed, 309.10 s**, exit 0; failure/error/skip yok.
- Ayrı K01 HTTP fixture: **2 passed, 1.20 s**, exit 0.
- Gerçek Chrome strict proof corpus: **9/9 completed, TP=3 FP=0 FN=0**, exit 0.
- Python 3.10.11, pytest 9.1.1, Playwright 1.63.0, Chrome 155.0.8059.39.
  Kaynak hash'leri koşu boyunca sabit; browser zorunlu, Docker lab kapalı.
- R4 süreç izolasyonu, R8 statik context ve R9 callback/Docker guard testleri
  dahil. Docker guard testleri gerçek kurulum/login kabulü değildir; uzak CI
  bu yerel sonuçla doğrulanmaz. Eski hedefli koşular bu sayılara eklenmez.
- [Komutlar, JUnit, kaynak hash'leri ve sınırlar](audit/2026-10-09-resume/README.md).

## 7 Ekim 2026 — R3/R4 baştan sona yeniden doğrulama

- Yeni ilk tam koşu: 679 passed, 213.46 s; sonradan eklenen cleanup regresyonları
  bu koşuda yoktu. Yeni cleanup karşı örneği: **2 failed**, 4.48 s, exit 1.
- Düzeltme sonrası yeni tam analyzer/bench paketi: **681 passed, 223.96 s**,
  exit 0; failure/error/skip sıfır. `test_dxadom` 73, browser proof 22,
  cleanup 2, scope 11, benchmark 43, adapter 49, corpus 21 dahil.
  [JUnit](audit/2026-10-07-r3-r4-revalidation/acceptance-final.xml),
  [bütün modül sayımları](audit/2026-10-07-r3-r4-revalidation/test-summary.json).
- Gerçek Chrome 155.0.8059.39, Playwright 1.63.0, Python 3.10.11 kullanıldı;
  audit bootstrap açık Windows Chrome yolunu test sürecinde dxadom'a verdi.
- Yeni ayrı strict CLI: **9/9, TP=3 FP=0 FN=0**, exit 0, wall 16.32 s.
  Eksik browser: 9 error/0 completed/exit 1. Gerçek lab exception: 2 selected,
  1 completed/1 error/exit 1; iki listener kapandı ve JSON/MD üretildi.
  R3 demo exit 0 ve JSON/HTML nesne eşitliği doğrulandı.
- R3 mevcut loopback kapsamı PASS; R4 7 Ekim yerel kapsamı PASS. Genel R4,
  hard timeout ve uzak Linux CI açık; sonuçlar örtüşür, sayılar toplanmaz.
  [Komutlar, kaynak incelemesi ve sınırlar](audit/2026-10-07-r3-r4-revalidation/README.md).

## 7 Ekim 2026 — R4 vaka istisnası izolasyonu

- Önceki kabul paketindeki 136 test ve 9/9 sonucu dosyalardan incelendi;
  runner/scanner/fixture hash'leri başlangıç kaynaklarıyla eşleşti.
- Yeni regresyonların düzeltme öncesi koşusu: **8 failed, 2 passed,
  39 deselected, 1.72 s**, exit 1. [JUnit](audit/2026-10-07-r4-case-isolation/before.xml).
- Yeni birleşik yerel kabul: **146 passed, 78.86 s**, exit 0, skip yok.
  [JUnit](audit/2026-10-07-r4-case-isolation/acceptance.xml).
- Yeni strict Chrome CLI: **9/9 completed, TP=3 FP=0 FN=0**, diğer durum
  sayaçları sıfır, exit 0, wall 17.23 s.
  [JSON](audit/2026-10-07-r4-case-isolation/corpus-results.json).
- İstisna enjeksiyonları aynı süreçte gerçek main/scorer/renderer akışını
  doğrular; hard timeout veya OS crash/kill testi değildir. Uzak CI yapılmadı.
  Koşular örtüşür; sayılar toplanmaz. [Komutlar ve sınırlar](audit/2026-10-07-r4-case-isolation/README.md).

## 7 Ekim 2026 — native R4 corpus/CI turu

- Değişiklik öncesi scope/R3/benchmark/adapter: **89 passed, 51.61 s**, skip yok.
- Frame canary okuma hatası karşı örneği düzeltmeden önce **1 failed,
  21 deselected**: error yerine inconclusive üretiliyordu.
- Son birleşik kabul: **136 passed, 80.88 s**, skip yok, exit 0.
  [JUnit](audit/2026-10-07-r4-native/acceptance.xml).
- Strict gerçek Chrome CLI: **9/9 completed, TP=3 FP=0 FN=0**, error/skip yok,
  exit 0. [JSON](audit/2026-10-07-r4-native/corpus-results.json).
- Bağımsız oracle, JS-kapalı gerçek callback ve malformed/incomplete kontrolleri
  dahil. Koşular örtüşür; sayılar toplanmaz. Uzak CI çalıştırılmadı.
- [Komutlar, roller ve sınırlar](audit/2026-10-07-r4-native/README.md).

Aşağıdaki kayıtlar önceki teslimlerin sonuçlarıdır.

## Push öncesi belge temizliği doğrulaması

Her dosya ayrı olarak bir kez `python -m pytest <dosya> -q -p no:cacheprovider
--tb=short` ile çalıştırıldı. Sayılar birleştirilmez. Yerel loglar
`.dxa/prepush/` altındadır; depoda yoktur, aynı komutla yeniden üretilebilir.

| Dosya | Sonuç |
|---|---|
| tools/dom-xss-analyzer/test_crawl_scope.py | 11 passed |
| tools/dom-xss-analyzer/test_dxadyn.py | 169 passed |
| tools/dom-xss-analyzer/test_r2_contract.py | 30 passed |
| tools/dom-xss-analyzer/test_auth_guards.py | 15 passed |
| tools/dom-xss-analyzer/test_browser_proof.py | 21 passed |
| tools/dom-xss-analyzer/test_dxadom.py | 37 passed, 36 skipped |
| tools/dom-xss-analyzer/test_r1_contract.py | 30 passed |
| tools/dom-xss-analyzer/test_dom_cli_evidence.py | 6 passed |
| bench/test_bench.py | 43 passed |
| bench/test_proof_adapter.py | 14 passed |

11 belgenin yerel bağlantı hedefleri kontrol edildi; eksik hedef yok.
`git diff --check` temiz. Testlerde standart Chrome yolları değiştirilmedi:
`test_browser_proof.py` DXA_BROWSER destekler; `test_r1_contract.py` içindeki
Chrome testi desteklemez. İkincisine aynı ortam değişkeninin eklenmesi öneridir,
bu teslimde uygulanmadı. Eski browser discovery skip'leri kapanmış sayılmaz.

## Sınırlı multi-agent geliştirme turu — tarihsel 6 Ekim koşusu

- Birleşik scope/HTTP/auth/browser/rapor/benchmark paketi: **339 passed,
  86.51 saniye**. Log/JUnit yerel çıktıdır, depoda yoktur;
  [yeniden üretim komutu](audit/2026-10-06-multi-agent-round1/README.md#önce-hata-sonra-düzeltme).
- Chrome proof-suite: dört seçilen/dört tamamlanan, TP=1 FP=0 FN=0,
  strict exit 0. JSON/Markdown yerel çıktıdır, depoda yoktur;
  [yeniden üretim komutu](audit/2026-10-06-multi-agent-round1/README.md#r4-ölçüm-kanıtı).
- Eval global-scope testi yeterli değildi: fonksiyon-local karşı örnek önce
  başarısız oldu; hook kaldırılınca 21 browser testi geçti. Ortak JSON/HTML
  raporunda eval gözleminin desteklenmediği artık açıkça kayıtlıdır.
- Bu tur tam depo veya uzak CI koşusu değildir. Önceki 36 browser skip'in
  tamamının çözüldüğü iddia edilmez. [Kapsam ve katkılar](audit/2026-10-06-multi-agent-round1/README.md).

## R3 ilk browser zinciri — tarihsel teslim

- Önceki tam paket **544 passed, 36 skipped, 1 warning**, 141.50 saniye.
  R3 değişikliklerinden sonra odaklı browser paketi **21/21 geçti**;
  route budget, header allowlist ve direct eval kontrolleri dahil.
- Loopback demo: HTTP/browser kullanıcı+rol kontrolü, stored submit 201, read
  200 ve eşleşen CID; Chrome 154.0.8037.98, Playwright 1.63.0.
- Negatifler: fixed/JSON/dialog/JS disabled, yanlış rol, cross-origin request,
  gecikme penceresi, eksik browser ve geçersiz scope. href, iframe, delayed,
  eval lexical-scope, cookie/bearer ve CSRF olumlu kontroller de var.
- [R3 test logu](audit/2026-10-06-r3-final/pytest.log),
  [JUnit](audit/2026-10-06-r3-final/pytest.xml),
  [demo JSON](audit/2026-10-06-r3-final/demo/result.json),
  [HTML](audit/2026-10-06-r3-final/demo/result.html),
  [kapsam/sınırlamalar](tools/dom-xss-analyzer/BROWSER-PROOF.md).
- WebSocket filtreleme denemesi takıldı ve kaldırıldı. Yeni browser komutu
  HTTP/redirect'i same-origin kısıtlar; WebSocket/ağ sandbox desteği yok.
  R3 kabul scope'u tamam; uzak Linux CI henüz çalıştırılıp doğrulanmadı.
- 36 eski dxadom browser testi mevcut binary keşfinde atlandı; R3 yeni testleri
  DXA_REQUIRE_BROWSER=1 ile skip edemez. Uyarı benchmark utcnow kullanımı.

## R2 HTTP kabul kapanışı — güncel teslim

- **526 passed, 36 skipped, 1 warning**, 112.13 saniye. 30 yeni R2 kabul
  testi: hedefe özel oturum sözleşmesi, rol kaydı, CLI hata duruşu, fractional
  rate, tek kullanımlık CSRF ve stored sırası, hata olayları ve desteklenmeyen birleşimler.
- 36 eski browser testi otomatik binary keşfi nedeniyle atlandı; geçmiş sayılmadı.
  Uyarı benchmark datetime.utcnow kullanımıdır. GitHub CI sonucu henüz doğrulanmadı.
- [Kapanış matrisi](audit/2026-10-06-r2/R2-KAPANIS.md),
  [log](audit/2026-10-06-r2/pytest.log), [JUnit](audit/2026-10-06-r2/pytest.xml).
- İlk tam koşudaki CSRF'siz guestbook konfigürasyon eksiği hedefe özel
  csrf_field ayarıyla düzeltildi. Paylaşılan HTTP oturumunda sıralama davranışı
  belgelenmiştir; eski paralel hız iddiası güncel kabul değildir.

## R2 auth guard — önceki teslim

- Tam paket **496 passed, 36 skipped, 1 warning**, 89.38 saniye.
  36 eski browser testi otomatik keşif nedeniyle atlandı; benchmark utcnow
  uyarısı devam ediyor. Geçmiş sayılan testlere atlamalar dahil değil.
- 15 yeni regresyon: 401/403/429/500, eksik/null/boş/geçersiz token,
  eski cookie, form hata yanıtı ve CLI durma + ortak hata raporu.
- Odaklı auth/flow koşusu **49 passed**. İlk tam koşuda eksik dashboard'lu
  eski stored fixture başarısızdı; fixture tamamlandıktan sonra yukarıdaki
  tam koşu geçti. Üretimdeki HTTP hata kontrolü gevşetilmedi.
- [Test logu](audit/2026-10-05-r2-auth/pytest.log),
  [JUnit](audit/2026-10-05-r2-auth/pytest.xml),
  [davranış ve sınırlar](tools/dom-xss-analyzer/AUTH-LIMITS.md),
  [staj kaydı](staj/2026-10-05-r2-auth.md).

R2 ilk auth guard kabulü tamam; hedefe özel oturum/rol doğrulaması,
fractional rate ve CSRF sıralaması açık.

## K01-min stored yorum vakası — önceki teslim

- Yerel browser deneyi: **5/5 kontrol geçti**, Chrome 154.0.8037.93, Playwright
  1.63.0, Python 3.12.14. Savunmasız HTML'de ayrı okuyucu context'inde canary;
  aynı payload için fix sonrası, JS kapalı, JSON-only ve normal dialog negatifleri.
- Bot R1 raporu reflection/candidate seviyesinde kalır; vaka execution sonucu
  ayrı kaydedilir. Bu çalışma genel R3 execution motorunu tamamlamaz.
- İki HTTP fixture regresyonuyla tam paket: **481 passed, 36 skipped, 1 warning**,
  80.33 saniye. Atlamalar eski browser otomatik keşfi, uyarı benchmark utcnow.
- [Vaka ve tekrar üretim](cases/k01-stored-comment/README.md),
  [browser sonuçları](cases/k01-stored-comment/evidence/2026-10-05-verified/result.json),
  [fix diff](cases/k01-stored-comment/evidence/2026-10-05-verified/fix.diff),
  [pytest logu](audit/2026-10-05-k01/pytest.log), [JUnit](audit/2026-10-05-k01/pytest.xml).
- İlk browser denemesi route callback imza hatasıyla başarısız oldu; helper
  düzeltildikten sonraki 5/5 kaydı yayımlandı. Önceki başarısız çıktı yerel audit
  alanında korundu, başarılı deney sayısına katılmadı.

K01-min tamam. Yeni venv kurulumu/bağımsız temiz ortam tekrarı henüz doğrulanmadı;
tam R5'in bu kabul maddesi açık kaldı. Haricî ürün, oturum rolü veya CVE kanıtı yok.

## R1 kabul kapsamı kapanışı — önceki teslim

- Tam paket: **479 passed, 36 skipped, 1 warning**, 87.53 saniye.
- Önceki teslimin üzerine 29 kabul/regresyon örneği: dokuz ayrıştırma sınırı,
  aynı gözlemi kaybetmeden gruplama, bilinmeyen sink/rol, geçersiz şema ve
  kazanılmamış proof/rol iddiaları, maskeleme, ayrı hata/skip olayları, DOM/journal/
  statik/bridge adaptörleri, flow/auth-flow girdi hatası.
- **Gerçek yerel Chrome kontrolü geçti:** normal alert + innerHTML sink; yalnız
  candidate/sink-observed; aynı bulgu kimliği JSON ve HTML'de. Chrome yolu testte
  açık verildi. [JSON](audit/2026-10-05-r1/chrome.json), [HTML](audit/2026-10-05-r1/chrome.html).
- Eski 36 browser testi otomatik binary keşfi nedeniyle atlandı; bunlar geçmiş
  sayılmadı. Uyarı benchmark'taki `datetime.utcnow()` deprecation uyarısıdır.
- Ara kontrol: 259 odaklı test geçti; ilk tam paket 476 geçti. Son üç kapanış
  kontrolünden sonra 479 sonucu alındı. Arada otomatik onay incelemesi kullanım
  limitine takıldığı için bir test komutu hiç çalışmadı; sonuç diye sayılmadı.
- [Tam log](audit/2026-10-05-r1/pytest-r1.log), [JUnit](audit/2026-10-05-r1/pytest-r1.xml),
  [kabul testleri](tools/dom-xss-analyzer/test_r1_contract.py),
  [kapanış matrisi](audit/2026-10-05-r1/R1-KAPANIS.md),
  [resmî sözleşme](tools/dom-xss-analyzer/EVIDENCE-CONTRACT.md).

Bu sonuç R1'in raporlama/kanıt kabul kapsamını kapatır. R2 auth/rate/CSRF,
R3 execution/rol doğrulaması ve R4 benchmark doğruluğu tamamlandı sayılmaz.

## R1 HTTP kanıt modeli — önceki teslim

- Tam paket: **450 passed, 36 skipped, 1 warning**, 76.29 saniye.
- 12 yeni regresyon: yedi Content-Type × beş HTTP yolunun ortak sınıflandırması;
  üç yanlış bağlamda raw marker; encoded flow; gerçek localhost JSON echo üzerinde
  ayrı CLI sürecinin console/JSON/HTML çıktısı ve ortak finding kimliği.
- İlk odaklı çalışmanın sandbox ortamı localhost ve geçici dosyaları engelledi;
  aynı paket gerekli izinlerle **215 passed** verdi. Son JSON/HTML ekleri yukarıdaki
  tam paketle doğrulandı. Test beklentileri execution iddiasını korumak yerine
  reflection semantiğine güncellendi; negatif kontroller ayrıca eklendi.
- 36 browser testi otomatik Chrome keşfi nedeniyle atlandı. Yeni browser proof
  doğrulaması yapılmadı. Tek uyarı benchmark'ın `datetime.utcnow()` kullanımıdır.
- [Log](audit/2026-10-05/pytest-http-evidence.log),
  [JUnit](audit/2026-10-05/pytest-http-evidence.xml),
  [regresyon kaynağı](tools/dom-xss-analyzer/test_http_evidence.py),
  [model ve sınırlar](tools/dom-xss-analyzer/HTTP-EVIDENCE.md).

Genel R1 kapanmadı: DOM/attempt şeması entegrasyonu, sink/rol dedup ve bütün
hata/atlama olaylarının ortak raporu açık. HTTP reflection açıklık kanıtı değildir.

## R1 kalıcı stored blind takip — önceki teslim

- Tam paket: **438 passed, 36 skipped, 1 warning**, 76.57 saniye.
- 18 yeni regresyon: stored/stored-auto yansımasız beş aile, gönderim hatası,
  canlı ve süreç kapandıktan sonra callback, eşzamanlı kalıcı yazma, tekrar
  kontrol, CID/zaman/endpoint/run ayrımı, yanlış yanıt, mahremiyet ve rapor escaping.
- İki CLI süreci + localhost HTTP fixture: tarama kapanır, callback daha sonra gelir,
  ayrı kontrol komutu aynı attempt kimliğine bağlar; hedef **yalnız bir POST** alır.
- JSON ve HTML kontrol raporu aynı attempt listesinden oluşturulur.
- Ara odaklı çalışma **220 passed**; son dört ek test ve canlı callback kalıcılığı
  yukarıdaki tam pakette doğrulandı.
- 36 browser testi mevcut otomatik Chrome keşfi sorunu nedeniyle atlandı.
  Bu teslim yeni browser execution doğrulaması yapmadı. Tek uyarı benchmark'taki
  `datetime.utcnow()` kullanımının deprecation uyarısıdır.
- [Test logu](audit/2026-09-29/pytest-blind-journal.log),
  [JUnit](audit/2026-09-29/pytest-blind-journal.xml),
  [test kaynağı](tools/dom-xss-analyzer/test_blind_journal.py),
  [tekrar üretim ve sınırlar](tools/dom-xss-analyzer/BLIND-JOURNAL.md).

Sınır: journal yalnız stored/stored-auto blind gönderim/callback kaydıdır;
bütün reflection/sink bulgularının ortak şeması değildir. Rol operatör etiketidir.
Callback JavaScript execution veya açıklık kanıtı değildir. Genel R1 açık kalır.

## R2 JSON gönderimi — önceki teslim

- Tam paket: **420 passed, 36 skipped, 1 warning**, 69.03 saniye.
- 36 browser testi otomatik Chrome keşfi nedeniyle atlandı; browser entegrasyonu tamamlandı sayılmıyor.
- Yeni yedi regresyon senaryosu: 950 payload'ın gerçek submit fonksiyonunda JSON round-trip'i; iç içe değer/anahtar ve kontrol karakterleri; üç geçersiz JSON durumu; anahtar çakışması; iki eşzamanlı JSON isteğinde ortak header izolasyonu.
- Eski quote testi elle escape algoritmasını kopyalamak yerine gerçek submit fonksiyonunun çıktısını kontrol ediyor.
- Odaklı JSON + dinamik test çalışması 176 geçti; son quote testi değişikliği yukarıdaki tam pakette doğrulandı.
- Kanıtlar: [test logu](audit/2026-09-28/pytest-json-transport.log), [JUnit](audit/2026-09-28/pytest-json-transport.xml).

Önceki 413 test sonucu callback teslimine aittir. JSON request kodlaması düzeltildi;
flow modundaki response/XSS sınıflandırması, auth ve CSRF açık kalır.

## Ana roadmap ve callback düzeltmesi — önceki teslim

- Callback/dinamik odaklı testler: **206 passed**.
- Tüm paket: **413 passed, 36 skipped, 1 warning**, 103.58 saniye. Atlanan 36 test Windows browser keşfi nedeniyle; cache yazma uyarısı var.
- 19 yeni callback regresyonu geçti; yanlış proof bekleyen önceki testler yeni gözlem semantiğine uyarlandı.
- JavaScript kapalı gerçek Chrome 154.0.8037.58: img isteği → 1 callback → 1 eşleşme → `severity=resource-callback`, `evidence_level=resource-callback`; JS proof iddiası yok.
- Canary id'si eksik/boş/farklı olduğunda eşleştirme reddedilir; HTTP yöntemi veya payload ailesi JS yürütme kanıtı sayılmaz.
- CLI help ve HTML resource-callback anlamını taşıyor; HTML'de istek metadata'sı escape ediliyor.

Kanıtlar: [tam test logu](audit/2026-09-28/pytest-master-roadmap.log), [JUnit](audit/2026-09-28/pytest-master-roadmap.xml),
[odaklı test logu](audit/2026-09-28/pytest-callback-focused.log), [Chrome sonucu](audit/2026-09-28/resource-callback-fix-browser.json),
[örnek rapor](audit/2026-09-28/resource-callback-report.html). Otomatik regresyonlar
`tools/dom-xss-analyzer/test_blind_correlation.py` içindedir.

Sınır: bu teslimde gerçek canary execution motoru veya yansımasız kalıcı blind takip yapılmadı. Callback gözlemi ile açıklık/etki ayrı tutuldu; ortak kanıt şeması henüz tamamlanmadı.

## İlk geliştirme teslimi

- Yeni CLI regresyon dosyası: **6 passed**.
- Geliştirme kopyasının tüm test paketi: **394 passed, 36 skipped, 1 warning**, 68.83 saniye.
- Atlanan 36 test browser keşfi nedeniyle atlandı; Windows Chrome yolunun otomatik bulunması hâlâ açık iş. Bunlar geçmiş baseline'da açık Chrome yolu ile çalıştırılmıştı; bu teslimde yeniden çalışmış gibi sayılmıyor.
- Mevcut Chrome ile ayrı gerçek tarayıcı kontrolü: yalnız 127.0.0.1 üzerinde normal alert sayfası açıldı. **OBSERVED-DIALOG**, exit 0; **PROVEN-EXECUTABLE yok**. Test sürecinde browser yolu açık verildi; kaynakta platform keşfi değiştirilmedi.
- Pytest cache yazma uyarısı test başarısızlığı değildir.

Tekrarlama: pytest kurulu ortamda depo kökünden `python -m pytest -q -ra`.
Dar regresyon: `python -m pytest tools/dom-xss-analyzer/test_dom_cli_evidence.py -q`.

Bu çalışma alanındaki ham kanıtlar:

- [Tam test logu](audit/2026-09-28/pytest-development.log)
- [JUnit sonucu](audit/2026-09-28/pytest-development.xml)
- [Gerçek tarayıcı sonucu](audit/2026-09-28/dom-dialog-fix-browser.json)
- Otomatik CLI regresyonları: `tools/dom-xss-analyzer/test_dom_cli_evidence.py`.

Bu bağlantılar depodaki tarihsel kanıtlara gider. Yerel kullanıcı dizinleri paylaşım
kopyalarında maskelendi; test sonuçları değiştirilmedi. Eski denetim scriptlerinin
tümü bu kanıt paketine dahil değildir; paket açıklaması `audit/2026-09-28/README.md` içindedir.

## İlk teslimin sınırı (tarihsel)

Yalnız bare-visit dialog çıktısındaki yanlış proof iddiası düzeltildi. Yeni execution doğrulama motoru eklenmedi. Blind korelasyon, breakout severity, auth, JSON ve benchmark kusurları açık; ROADMAP'te ayrı kabul koşulları var.

Orijinal ZIP ve denetim kaynak kopyası korunmuştur. İlk düzeltmeler `2703d1a`
ile Git geçmişine ve GitHub main dalına aktarıldı. Sürüm etiketi oluşturulmadı.
