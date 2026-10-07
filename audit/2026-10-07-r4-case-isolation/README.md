# R4 vaka hatası izolasyonu — 7 Ekim 2026

Başlangıç HEAD: `a979749b09d0eb70a41baafa9d9bb9f88cf8980d`.
Çalışma ağacı önceki turdan kirliydi; 14 takipli dosya değişikliği ve üç
takipsiz giriş korundu. Commit, push, dış yayın ve uzak CI yapılmadı.

## Önceki turun kabul incelemesi

Bu inceleme eski testleri yeni koşu olarak sunmaz. Önceki
`../2026-10-07-r4-native/acceptance.xml` dosyası 136 test, sıfır failure/error/skip
gösteriyor. Önceki corpus JSON'u 9/9 completed, TP=3 FP=0 FN=0 gösteriyor.
İnceleme başlangıcında mevcut runner, proof üreticisi ve fixture SHA256 değerleri
JSON provenance alanlarıyla eşleşti:

| Dosya | SHA256 |
|---|---|
| bench/run.py | d999ad31fefbfd24574662418f6e0f4b662937bdaf4d7fc6613188eee32d7c05 |
| tools/dom-xss-analyzer/dxaprove.py | c5e6c3b64c992b2d0f938bb8a3979c7190abde00832f6bb6ee25bdd31f8fd3eb |
| tools/dom-xss-analyzer/dxa_proof_lab.py | ed7e7d9ac780c23de2891042f14c0e5b4aa9a90b77b7ab79ec66aad63428ef1e |

Dokuz yerel vaka ve CI adımlarının eklenmesi kapsamındaki önceki dar teslim
destekleniyor. Uzak Linux CI ve gerçek ürün adapter'ı kabulü yok; genel R4 açık.

## Önceki dosya sahipliğinin değerlendirilmesi

Önceki audit yalnız son sahiplik tablosunu koruyor; ilk atama/devir kaydı yok.
Kayıtlı teknik gerekçe Security'nin bulduğu canary okuma hatasıdır:
koordinatör `dxaprove.py` ve `test_browser_proof.py` düzeltmesini üstlenmiştir.
Engine/QA'nın Python süreç erişim engeli, kabul testlerinin koordinatörce
çalıştırılmasını açıklar. Bu kayıtlar açık bir önceden yapılmış sahiplik devrini
kanıtlamaz; sapmanın tam zamanı ve ilk plandaki tüm ayrıntılar doğrulanamadı.

## Bu turun sınırı ve sahipliği

R4 crash/timeout/skipped kabul maddesinin dar alt işi: proof vaka çağrısından
çıkan yakalanabilir istisna bütün benchmark'ı ve sonuç dosyalarını kaybettirmesin.
Başlangıç kaynak bulgusu `bench/run.py:436` çağrısının `run_all:502` ve
`main:619` üzerinden rapor yazımını kesebilmesidir; ilk incelemede runtime
yeniden üretimi yapılmamıştı.

| Native agent | Görev / sahiplik |
|---|---|
| /root/r4_acceptance_review — qa_security_lab_specialist | İlk salt okunur kabul incelemesi tamamlandı; devam görevi yalnız bench/test_proof_adapter.py regresyonları |
| /root/r4_case_isolation — scanner_engine_specialist | Yalnız bench/run.py vaka istisnası sınırı; red regresyon kanıtı sonrası uygulama |
| /root — koordinatör | Entegrasyon, test koşuları, audit/staj, ROADMAP/STATUS/VALIDATION/CHANGELOG |

En fazla iki uzman aynı anda görevlendirildi. Storage, Report ve Security için
gereksiz yeni görev açılmadı. Native rol seçimi gerçek `agent_type` parametresiyle
yapıldı; generic fallback kullanılmadı. Testlerin yeni dosya yerine mevcut
adapter test dosyasında tutulması kullanıcıya uygulamadan önce bildirildi;
mevcut CI komutu bunları zaten kapsar.

Kabul: olağan istisna error; bildirilen TimeoutError/TimeoutExpired timeout;
başarısız vaka değerlendirilmez, kalan vaka çalışır, selected paydası korunur;
strict çıkış 1 ile JSON/Markdown yazılır. Ham hata mesajı/sır rapora veya konsola
taşınmaz; KeyboardInterrupt/SystemExit yutulmaz. Sert süreç sonlandırma veya
30 saniyelik süre sınırı bu turun kapsamı değildir.

## Yeni koşular ve kapanış

1. Sandbox Python başlatımı erişim engeliyle durdu; test başlamadı. Araç izniyle
   aynı komut çalıştırıldı. Bu çevre hatası ürün sonucu sayılmadı.
2. Düzeltme öncesi yeni regresyonlar: **8 failed, 2 passed, 39 deselected,
   1.72 s**, exit 1. [JUnit](before.xml). Dört exception türü hem run_all hem
   CLI girişinde rapor yazılmadan dışarı çıktı; iki süreç kesme kontrolü geçti.
   JUnit içindeki sentinel metin yapay test verisidir, gerçek sır değildir.
3. Düzeltme sonrası birleşik kabul: **146 passed, 78.86 s**, exit 0,
   failure/error/skip sıfır. [JUnit](acceptance.xml), başlangıç
   `2026-10-07T17:35:01.923502+03:00`. Bu yeni koşudur; önceki 136 test sonucu
   yeniden adlandırılmadı. XML suite süresi 78.842 s; konsol 78.86 s.
4. Yeni gerçek Chrome strict CLI: **9/9 completed, TP=3 FP=0 FN=0**,
   error/timeout/skipped/invalid/inconclusive sıfır, exit 0, wall 17.23 s.
   [JSON](corpus-results.json), [Markdown](corpus-results.md).

Komutlar depo kökünde çalıştırıldı; eski kanıt dosyalarının üzerine yazılmadı:

```powershell
py -3.10 -m pytest bench/test_proof_adapter.py -k proof_case -q -p no:cacheprovider --tb=short --junitxml=audit/2026-10-07-r4-case-isolation/before.xml
$env:DXA_REQUIRE_BROWSER='1'
py -3.10 -m pytest tools/dom-xss-analyzer/test_crawl_scope.py tools/dom-xss-analyzer/test_browser_proof.py bench/test_bench.py bench/test_proof_adapter.py bench/test_proof_corpus.py -q -p no:cacheprovider --tb=short --junitxml=audit/2026-10-07-r4-case-isolation/acceptance.xml
$env:BENCH_STRICT='1'
py -3.10 bench/run.py --proof-suite --browser 'C:\Program Files\Google\Chrome\Application\chrome.exe' --no-history --out audit/2026-10-07-r4-case-isolation/corpus-results.md
```

## Kabul kararı ve kalanlar

Dar vaka istisnası izolasyonu **tamamlandı**. Kök neden ve düzeltme
`bench/run.py:436–450`; bağımsız regresyonlar
`bench/test_proof_adapter.py:188,196,215`. İstisna enjeksiyonlu CLI testleri
gerçek main/scorer/renderer yolunu aynı Python sürecinde çalıştırır; bunlar
OS sürecinin crash/kill veya zorunlu zaman aşımı deneyleri değildir. Ayrı CLI
koşusu normal dokuz browser vakasının çalıştığını doğrular. Koşular örtüşür,
test sayıları toplanmaz; tüm depo testi ve uzak Linux CI yapılmadı.

Engine yalnız atanan runner dosyasını, QA yalnız atanan adapter test dosyasını
yazdı. İkisinin de kendi test çalıştırma iddiası yoktur; yeni koşular
koordinatörce çalıştırıldı. QA son salt okunur incelemesinde bloklayan bulgu
bildirmedi. Bu turda dosya sahipliği devri veya eşzamanlı aynı dosya yazımı yok.

Son runner SHA256: `c65598ecee5872b4baf79dea6160f5d875000545dba2ddbcdb1d04cdde3278b7`.
Adapter testi SHA256: `3edaccf308361644c3b5c6e95f789e09af7126b5942b1fc929965e4e65caa31a`.
Scanner/fixture hash'leri başlangıçla aynı; runner hash'i yeni corpus JSON'u
ile eşleşiyor. Git diff whitespace kontrolü geçti.

R4 genel olarak açık: 30 saniyelik hard timeout/süreç sonlandırma ve alt süreç
temizliği, hatalı adapter dönüş nesnesinin genel doğrulaması, sabit gerçek ürün
adapter'ı, geniş sanitizer/rol/iframe corpus'u ve uzak Linux CI kabul kanıtı
kapanmadı. Sonraki dar runner işi hard timeout için süreç yaşam döngüsü ve
temizlik kabulünün tasarlanmasıdır; bu turda uygulandığı iddia edilmez.
Her iki uzman görevi tamamlandı; bu turun test/CLI komutları exit sonucu verdi.
