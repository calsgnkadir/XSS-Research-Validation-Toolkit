# Değişiklik kaydı

## Unreleased — 2026-10-22 R7/A04–A05 continuation

- Bounded A04 local ownership coverage now includes the three candidate
  work-session GET routes and two business-owner listing GET routes. In the new
  isolated Kadrom lab, owner 1 received `200` for its attendance and roster;
  owner 2 received `403` on both. Only synthetic seed data was used; the new
  containers were stopped and the new volume retained. This is not product-wide
  coverage. See the [runtime audit](audit/2026-10-22-a04-owner-read-runtime/README.md)
  and [scope inventory](audit/2026-10-22-a04-scope-completeness/README.md).
- A05 source triage added the remaining Micrometer, X.509, BCrypt, Sort,
  multipart, and Tomcat WebSocket path conditions. BCrypt has a reproduced
  advisory-matching application behavior; practical account impact remains
  unverified. Sort's tested malformed request did not reproduce its advisory
  condition. Other applicability limits remain explicit. See the
  [source-path audit](audit/2026-10-22-a05-remaining-paths/README.md).
- A focused H2 follow-up confirmed the registration endpoint accepted a
  synthetic 73-byte password and a different-suffix login with the same first
  72 bytes authenticated to that account. The pinned
  `spring-security-crypto:6.2.4` is in the published affected range. This is an
  advisory-matching local defect candidate; real-account impact was not tested.
  See the [local check](audit/2026-10-22-a05-bcrypt-local-check/README.md) and
  [triage](audit/2026-10-22-a05-bcrypt-triage/README.md).
- One bounded local Sort request returned HTTP 500 for an invalid property;
  the following health check returned 200. No StackOverflow or availability
  effect was observed. See the
  [Sort check](audit/2026-10-22-a05-sort-local-check/README.md).
- Read-only A05 configuration reviews found checked-in Micrometer 1.12.5
  instrumentation prerequisites, while effective runtime beans and any DoS
  remain unverified. Multipart/Tomcat upload paths and byte limits are present;
  part-count, temp-file cleanup, and intermediary conditions remain unknown.
  Follow-up experts found no local Java process and the Docker Desktop Linux
  engine pipe was unavailable, so effective settings and container inventory
  could not be read. No runtime was started and no further request was sent.
  See the [Micrometer source review](audit/2026-10-22-a05-micrometer-config-review/README.md),
  [Micrometer runtime check](audit/2026-10-22-a05-micrometer-effective-review/README.md),
  [multipart source review](audit/2026-10-22-a05-multipart-config-review/README.md),
  and [multipart runtime check](audit/2026-10-22-a05-multipart-effective-review/README.md).
- RFD's harmless H2 check verifies only attachment response encoding and the
  exercised membership controls; Nimbus review found no source-supported path
  to its affected parser in the pinned OAuth2 config. A05/R7 remain open.

## 0.1.0 — 2026-10-21

- Published the `v0.1.0` GitHub Release with the validated wheel asset. The
  release tag points to `d7d1bd666ae4fe5643bf0574658d8d8a0f4411a0`; the wheel
  SHA-256 is `111a0f6c43c3d6710c9c30434fb402604cec9fa5ee69845a44b6d14023195399`.
  PyPI upload was explicitly excluded. See the
  [release audit](audit/2026-10-21-r6-release/README.md).

## Unreleased — 2026-10-21 A04/A05 follow-up

- Source review found candidate work-session GET routes for a bounded same-role
  ownership check, but Docker API permission denial again prevented safe runtime
  verification; no service was started and no request was sent.
- Public GitHub REST returned empty issue/release/tag collections and zero exact
  Maven-filtered GHSA results. The repository advisory endpoint returned 404;
  NVD returned a 406 challenge and the exact-PURL OSV request failed before an
  HTTP response. A05 remains partial/inconclusive and R7 stays open. Existing
  Kadrom tests do not cover same-role GET ownership; no test was run. See the
  [A04 runtime follow-up](audit/2026-10-21-a04-runtime-followup/README.md),
  [A04 test inventory](audit/2026-10-21-a04-testability-followup/README.md),
  [A05 API follow-up](audit/2026-10-21-a05-public-records-followup/README.md),
  and [A05 OSV attempt](audit/2026-10-21-a05-osv-followup/README.md).

## Unreleased — 2026-10-21 R7 advisory lookup
- Exact-name GitHub Advisory/NVD searches surfaced no match, but exhaustive
  results could not be verified because official search/API pages were
  inaccessible. R7 remains inconclusive; this is not a “no advisory” finding.
  See the [R7 lookup](audit/2026-10-21-r7-advisory-lookup/README.md).

## Unreleased — 2026-10-21 R7 records and R6 release decision

- The R7 public-record/version review found no GitHub issues, tags or releases
  for the selected Kadrom repository in the public API results, and its POM
  identifies `0.0.1-SNAPSHOT`; the advisory check remains inconclusive because
  the advisory API/page could not be retrieved. A04 remains partial and A05's
  `no-candidate-observed` status remains limited to the tested routes.
- R6 remains on hold: the accepted 0.1.0 wheel predates a change to packaged
  `dxadyn.py`, so current source-to-wheel identity must be rebuilt and accepted
  before a tag is proposed. No tests or wheel rebuild were run in this review;
  no tag or publication was made. See the
  [R7/R6 decision audit](audit/2026-10-21-r7-r6-decision/README.md).

## Unreleased — 2026-10-21 bounded R7/A04 local role check

- Selected the user's Kadrom repository as a local-only research scope and
  pinned the run to commit `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. Two
  seeded synthetic accounts produced expected own-list, cross-role and
  unauthenticated results. No candidate was observed in those routes; same-role
  IDOR and other routes remain untested. Known-record lookup was inconclusive
  because the advisory/issue pages were unavailable to the browsing source.
  R7 remains open. See the [A04 audit](audit/2026-10-21-a04-kadrom/README.md).

## Unreleased — 2026-10-21 R7/A03 evidence-label correction

- The historical sprint procedure now distinguishes CID-matched browser
  `execution-observed` from callback-only `resource-callback`; neither alone
  establishes a vulnerability. No product scope or target was selected, and
  no lab or product test was run. See the A04 readiness note in the
  [R7/K03/K04 audit](audit/2026-10-20-r7-k03-k04-followup/README.md).
- The second read-only QA review matched the private K03 capture and script
  hashes and the 17-record masked summary. It was not a Docker or product
  rerun; historical sessions, CVE attribution, and remediation remain
  unsupported.

## Unreleased — 2026-10-20 R7 prep, K03 evidence review and K04 correction

- R7/A01 historical Patchstack duplicate and SQLi/CVE outcomes are labeled as
  author-reported where their supporting packages are absent. The historical
  sprint plan no longer implies current disclosure-program eligibility or a
  universal 90-day deadline. Official CVE-2026-4420 provenance is linked; the
  local Bludit 3.16.2 result is not attributed to that CVE.
- QA reviewed the private K03 capture locally and matched its recorded hashes
  and masked SQLi/JWT/BOLA observations. Raw credentials/tokens remain private;
  no lab rerun was performed.
- K04 review found and corrected the remaining recursive-sanitizer recommendation
  and inaccurate `textContent` escaping statement in writeup 01. Historical
  remediation was not retested. No local analyzer/browser suite was run; hosted
  general CI passed 3/3 jobs and the separate K01 Linux workflow passed for
  commit `366b01c`.

## Unreleased — 2026-10-19 C10/C13, S02 and K03 continuation

- C10 body wording and dynamic probe source comments, plus C13 README
  provenance, now match the reviewed `451361b` evidence; no new CI run is
  claimed. S02 maps all 11 writeups to
  skills, evidence limits, work type, and C/K items.
- K03 has a new isolated OWASP Juice Shop 20.2.0 loopback reproduction for
  SQLi, unsigned JWT acceptance and two-account basket access, with negative
  controls, image/source hashes and a masked summary. Historical writeup
  sessions remain distinct. Raw request/response data with synthetic local
  credentials and tokens stays under ignored `.dxa/`.
- No analyzer regression suite ran locally for these document, source comment
  and lab updates. Commits `c58c74b` and `2650ede` were pushed; all four hosted
  jobs passed on both. The exact scope and evidence are in
  `audit/2026-10-19-k03-loopback-reproduction/README.md`.

## Unreleased — 2026-10-17 portfolio and evidence review

- P02/P03 closeout: README now describes the bounded experimental Python CLI,
  and writeups 06–10 are grouped as one historical tool-development series.
  Generated corpus totals are not described as exploit or execution counts.
- S01/S03 session and continuation notes include the final local retest matrix,
  hosted workflow outcomes, and the local artifact-provenance limitation. S02
  remains open.
- Final source commit `3ef8499` local retest: analyzer 789 passed/38 skipped;
  selected benchmark acceptance 520 passed; required Chrome acceptance
  218/218; DOM Chrome 80/80; K01 fixture tests 22/22 and local profile 5/5.
  Details and scope are in `audit/2026-10-17-final-commit-retest/README.md`.

- C01–C13 writeups and methodology now separate author-reported history from
  retained evidence; the writeup index no longer repeats old target, accuracy,
  WAF-bypass, or execution claims as current proof.
- K02 publication-safe screenshot copies mask account/token/cookie data while
  preserving originals. K03 records missing raw SQLi/JWT/BOLA evidence. K04
  aligns defense and methodology language. K05 adds a separate, qualified
  preview for archived JSON-only, Bludit, and static reports; raw reports are
  unchanged.
- P01 curates three bounded evidence paths. P04 was installed in a clean
  Python 3.10 environment; the package demo returned `execution-observed` and
  K01 local reproduction passed 5/5 controls with 5/5 fixture ports closed.
  No package release or historical target finding is claimed.
- Final local analyzer suite after the report-renderer regression: 789 passed,
  38 skipped, zero failures (Windows/Python 3.10.11). Hosted CI for this source
  commit passed; artifact contents were not independently inspected.

## 0.1.0 — 2026-10-21 (GitHub Release; PyPI yayını hariç)

- İlk kurulabilir araştırma sürümü için paket sürümü `0.1.0` seçildi. Temel
  kurulum, üç CLI, config önceliği/validasyonu, JSON/HTML raporları ve isteğe
  bağlı pinned Playwright browser extra belgelenip kurulu wheel üzerinden
  doğrulandı.
- Installed-wheel kabul kapısı dağıtım adını/sürümünü ve üç console-script
  eşlemesini de denetliyor; 7/7 CLI/config kontrolleri ve dokuz modül için
  kaynak/wheel/kurulu kopya hash eşleşmesi geçti.
- R4 teknik kabul ve R5/K01 vaka kanıtı release önkoşulu olarak kaydedildi.
  R8 regex kapsamı, R9 ağ/operasyon sınırları ve genel scanner doğruluğu bu
  sürümün iddiası değildir. XSS sonuçları aday veya sınırlı lab kanıtı olarak
  kalır; genel ürün doğruluğu/başarılı CVE iddiası yoktur.
- R8 adds a bounded Python AST pilot for syntax-level sources and ordinary or
  tuple/list assignment flow. A tiny labeled positive/negative corpus catches
  one prior false negative and one false positive; this is not an accuracy
  benchmark or a sound-analysis claim.
- Güncel kaynakta wheel/gate kabulü 7/7, değişen `dxadyn` odaklı regresyonlar
  271/271 geçti; dokuz modül kaynak/wheel/kurulum hashleri eşleşti. Wheel
  GitHub Release varlığı olarak dağıtılır; PyPI'ye yüklenmez. Tag, Release URL'si
  ve final artifact hash'i STATUS/VALIDATION kayıtlarında tutulur. Final wheel
  SHA-256: `111a0f6c43c3d6710c9c30434fb402604cec9fa5ee69845a44b6d14023195399`.
- 21 Ekim'de `v0.1.0` tag'i commit `d7d1bd6`'ya işaret edecek şekilde push edildi
  ve [GitHub Release](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/releases/tag/v0.1.0)
  yayımlandı. Hosted genel CI ve K01 Linux işleri başarılıydı; PyPI'ye yükleme
  yapılmadı. Ayrıntı: [R6 release audit](audit/2026-10-21-r6-release/README.md).

## Unreleased — 2026-10-16 local R4/R5 follow-up

- The 17 October `221baa5` hosted run passed the opt-in DOM browser harness and
  K01 Linux workflow, but failed the analyzer and required browser proof jobs.
  Logs were not retrievable (HTTP 403). Two test-only fixes followed: a
  loopback HTTP fixture for the direct-eval proof and a complete stored-auto
  report mock. The local required Chrome selection passed 218/218 and the full
  analyzer suite passed 788 with 38 skips. Commit `3a386ee` then passed all
  three general CI jobs and K01 Linux; details are in VALIDATION.md.

- R9 local DOM test fixtures now use threaded HTTP servers with explicit
  shutdown/join checks. The full Chrome `test_dxadom.py` suite passed 80/80;
  this fixes local test-fixture contention only and does not alter browser
  scope or analyzer behavior. Hosted CI is pending for this change.
- R6 final 0.1.0 wheel metadata was inspected directly: the browser extra pins
  Playwright 1.63.0. No wheel rebuild, release tag, or package publication was
  performed for this metadata inspection.

- R6 static CLI now rejects duplicate JSON config keys before scanning; a
  reproduced ambiguity regression is included. Focused config/mode/report
  suite: 110 passed. README installation steps now separate the base CLI,
  optional pinned browser extra and disposable loopback demo.
- Current-source R6 wheel installed offline into a fresh venv and passed the
  seven-check installed CLI gate; all nine source/wheel/installed module hashes
  matched. Wheel SHA-256 and environment/build caveat are in the R6 audit.
  No hosted CI, release tag or publication was performed in this recheck.

- R4 technical scope closed after the exact stored-payload replay gate was
  tightened for fail-closed outcomes and loopback-only HTTP browser requests.
  Final Chrome suite: 57 passed; final replay: 8 rows, 6 exact candidates,
  two Dalfox raw payloads observed in raw fixtures and no escaped execution.
  No scanner rerun, accuracy score, TP/FP/FN or ranking is claimed. The
  WebSocket negative-control attempt timed out and is outside R4 replay scope;
  no general browser network sandbox is claimed.
- R5 technical acceptance closed with a fresh Windows venv run: 5/5 controls,
  5/5 fixture ports closed, and all proof/source/gate hashes matched. The user
  removed independent-human repetition as a mandatory closeout condition.
- Review commit `06c4e21` is on origin/main (CI 38879831807 and K01
  38879831825 succeeded). Final technical closeout `01a89e3` is also on
  origin/main; CI 38887832797 and K01 38887832998 succeeded. Artifact contents
  for either push were not downloaded.

- Earlier interim reviews recorded the original-session CID gap and the
  pending second-person repeat. The final R4 replay and user-directed R5
  technical scope decision below supersede those interim statuses.

- Code/evidence commit `157a438` was pushed and remote main hash verified.
  General CI 38806623338 passed all three jobs; K01 Linux 38806623393 passed.
  Artifact contents were not independently downloaded in this follow-up.

- Final R4 review fixed two further v3 gate gaps (credential angle values and
  Dalfox canonical report shape). Three regressions failed first; focused
  tests passed 132/132 after correction. Coordinator final-source combined
  rerun passed 372/372 after an initial Windows loopback connection abort.
- Scoped `.gitattributes` rules preserve byte-bound R4/R5 proof artifacts
  through Git's Windows newline filtering.

- Imported the pending R4 comparison acceptance gate into the user-selected
  OneDrive copy. Fixed v3 timeout, credential metadata and missing cookie
  argument validation after four counterexamples reproduced the defects.
- Verified the affected R4 suite with required Chrome: 368 passed, zero
  failure/error/skip. Revalidated 8/8 historical candidate artifacts; no
  fresh scanner execution or candidate browser proof was established.
- Repeated K01 locally: 5/5 controls, five closed fixture ports and 22 focused
  tests passed. The independent second-person repeat remains deferred.
- Source hashes and local evidence are under `audit/r4-local-acceptance-resume/`
  and `audit/r5-local-closure-resume/`. Git delivery and hosted CI are recorded
  above, separately from the local test results.

## Unreleased — 2026-10-15

- R4 bounded candidate comparison now completes eight runs with equal limits;
  output reuse, partial reports and pacing past the wall limit are rejected.
  An independent artifact gate checks coverage, identity and report hashes.
  Candidate results remain separate from browser proof and accuracy ranking.

- R6 mandatory CI builds a wheel and checks all nine installed module hashes,
  CLI help and static/dynamic config behavior from outside the checkout.
  The wheel and hash-bound acceptance JSON are retained together; mismatched
  wheels and optimized checker execution are rejected. No release tag.

- R4 corpus v4 adds inert comment/template and activated-template controls;
  stable identities, independent browser oracle and CI gate cover 17 cases.
- R6 dynamic CLI accepts strict versioned HTTP tuning config, preserves CLI
  precedence and rejects irrelevant settings before I/O. Installed smoke helper
  uses separate config/report filenames. No release tag is created.
- R5 independent-human result form is available; acceptance remains pending.
- R4 adds a two-account blind stored loopback fixture with CID browser oracle;
  a pinned Dalfox 3.2.4 vs dxadyn loopback attempt is inconclusive (four
  completed candidate scans and four Dalfox timeouts); no ranking is claimed.
  Comparator accounting tests and the separate browser oracle are added to CI.
- R6 installed-wheel readiness matrix covers all three CLI help contracts,
  static/dynamic config behavior, and the packaged loopback proof demo. The
  version remains a developer build; R4/R5 prerequisites and release gate stay open.

- R4 gate, callback özetini fixture gözlemiyle eşleştirir.
- R5 K01 gate yerel runtime profili ve browser seçeneğiyle çalışır;
  optimize Python'u reddeder, varsayılan CI şartları korunur.
- R6 dinamik CLI çakışan modları ve DOM ile HTTP oturum seçeneklerini
  işlem öncesi reddeder; JSON/HTML rapor dalları için regresyon matrisi eklendi.

## Unreleased — 2026-10-14

- R6 paketleme taslağı: Python çekirdeği ve üç CLI entrypoint için yerel
  kurulum; opsiyonel browser extra Playwright sürümünü sabitler. Temiz venv'de
  kurulum/help ve paketlenmiş yerel demo kontrolü yapıldı. Bu bir release değil.


- R4 loopback-proof/3, beş yeni bağlamla 14 vakaya çıktı. Alternatif
  source/sink/role ve frame eşlemesi, bağımsız oracle testleri ve CI gate
  güncellendi. Kapsam paydası ve karşılaştırma protokolü açıklandı.
  Yerel 527 test ve strict 14/14 kabulü; [sınırlar](audit/2026-10-14-r4-corpus-v3/README.md).

- R4 CI kapısı JSON/Markdown tutarlılığını ve kaynak/corpus hashlerini
  doğrular; runtime follow-up Python 3.12/Linux dışındaki beyanları reddeder.
  Dar kabul ve uzak koşu sınırları [audit kaydında](audit/2026-10-14-r4-provenance-gate/README.md); genel R4 açık.

## Unreleased — 2026-10-13

- R4 Bludit ingress, internal uygulama + loopback sabit reverse proxy ile
  gerçek kurulum/login/raw-escaped browser kontrolünden geçti. Üç disposable
  koşuda hata ve temizlik kontrolleri, 335 regresyon ve mevcut Docker veri
  koruması doğrulandı. Genel R4 ve benchmark entegrasyonu açık.
  [Yerel kabul](audit/2026-10-12-r4-ingress-live/README.md).

## Unreleased — 2026-10-12

- Deneysel pinned Bludit adapter taslağı, 83 bağımsız guard/lifecycle/rapor testi
  ve CI test bağlantısı eklendi; birleşik 268 test geçti. Gerçek Docker host
  port mapping oluşmadığından ürün kabulü engelli; genel R4 kapanmadı.
  [Kanıt ve sınır](audit/2026-10-12-r4-product-adapter/README.md).

- R9 ortak JSON/HTML paylaşım raporları bilinen API/CSRF credential alanlarını
  ve evidence_links HTTP(S) URL sırlarını maskeler; ham girdiler ve kanıt
  sınıflandırması korunur. 126 regresyon geçti; genel konsol/serbest metin
  mahremiyeti kapanışı değildir.
- R4/R9 zorunlu CI kapısı JUnit sıfır-skip/hata, tam dokuz fixture'ın
  kanıt/skor tutarlılığı ve demo execution sonucunu denetler. Exit 0 dönen
  inconclusive demo kabul edilmez; ayrı opt-in browser job korunur.
- [Yerel kabul ve uzak erişim sınırı](audit/2026-10-12-r4-ci-acceptance/README.md).
  Yeni uzak Linux artifact içeriği ayrıca doğrulandı; genel R4/R9 kapanışı değildir.

## Unreleased — 2026-10-11

- R9 self-scan CI kapısı crash/import hatasını beklenen bulgu diye kabul etmez;
  fresh JSON raporu, çıkış kodu, source/sink tutarlılığı ve hata/skip kayıtları
  birlikte denetlenir. Gerçek CLI ve bağımsız karşı örneklerle 143 test geçti.
- Devamlılık Git ve belge sözleşmesine bağlandı: STATUS tek güncel devam
  noktası, eski metin audit'te; tarihsel yetki/durum çelişkileri düzeltildi.
  Beş mevcut custom-agent tanımı korundu.
- [Kanıt ve sınırlar](audit/2026-10-11-continuity/README.md). Genel R4/R9,
  gerçek ürün adapter'ı ve uzak artifact kabulü bu teslimle kapanmaz.

## Unreleased — 2026-10-09

- R4 browser proof worker'ları parent deadline ve sahip olunan süreç ağacıyla
  izole edilir; timeout/crash/malformed çıktı sonraki vakayı kesmez. Cleanup
  hatası başarı sayılmaz; Docker teardown yalnız benzersiz projeye uygulanır,
  volume silmez ve hata durumunu raporlar.
- R8 sanitizer adı taint'i silmez; ham provenance ve HTML mitigation ayrıdır.
  Dosya/import ve Python scope sınırları, template uzantıları ve güvenli Python
  örneği düzeltildi; regex ve C# sınırları STATIC-LIMITS.md içinde belgeli.
- R9 callback read/body/limit/CORS sınırları, görünür SQLite hataları ve minimal
  HTTP kayıtları eklendi. Eski SQLite verisi korunur. Compose loopback, immutable
  local image ve benzersiz proje önkoşullarına geçirildi.
- Yeni tekrar: 824 analyzer/bench + 2 K01 HTTP testi geçti; Chrome strict corpus
  9/9, TP=3 FP=0 FN=0. Gerçek Docker ürün adapter'ı ve uzak CI kabulü açık.
  [Kanıt](audit/2026-10-09-resume/README.md).

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
