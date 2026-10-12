# 12 Ekim — R9 ortak rapor mahremiyeti dar teslimi

Başlangıç `c5d5451cc81dc94ce65aab330e3925a3a6150c04`. Kullanıcı ana ajan
incelemesi ardından commit/push ve sonunda OneDrive dışına taşıma istedi.

## Kök neden ve kapsam

`tools/dom-xss-analyzer/dxa_evidence.py:18` eski PRIVATE_KEYS listesi
api_key/csrf_token gibi bilinen credential alanlarını kapsamıyordu.
`:42` liste yolu evidence_links için URL bağlamını kaybediyordu. Beklenen:
ortak JSON/HTML paylaşım kopyası credential değerlerini içermez. Gözlenen:
yalnız sahte sentinel içeren fixture'da API/CSRF değerleri ve HTTP(S) linkin
userinfo/query/fragment değerleri iki çıktıda da kalıyordu. Bu yeniden
üretilmiş hata; gerçek kullanıcı sırrı veya dış hedef kullanılmadı.

Düzeltme açık credential alan listesini genişletir, URL key casing'ini
normalleştirir ve evidence_links HTTP(S) öğelerine mevcut safe_url uygular.
Girdiler değişmez, evidence/triage/role_verified semantiği korunur, yerel
linkler ve credential olmayan alan-adı/sayaç metadata'sı korunur.
Genel serbest metin/konsol, özel credential alan adı veya HTTP(S) dışı link
mahremiyeti kapanışı değildir; R9 birleşik kutusu açık kalır.

## Gerçek sahiplik ve limit

- Native Report `/root/r9_report_privacy`: dxa_evidence.py ve yeni
  test_report_privacy.py; kök neden sentinel deneyi, uygulama ve test yazımı.
- Native QA `/root/r4_acceptance_qa`: R4 son incelemesini tamamladı; ayrı R9
  QA turu kullanım limitine takıldı, final veya QA-review dosyası üretmedi.
- Report finali de limitte kesildi. Koordinatör gerçek dosyaları devraldı,
  diff ve oracle'ları inceledi, eski kod karşı örneğini ve yeşil paketi çalıştırdı.
  Bağımsız R9 specialist QA tamamlandı iddiası yok. Arka plan çalışanı yok.

## Yeni doğrulama

- Windows/Python 3.10.11/pytest 9.1.1: **126 passed, 37.09 s**;
  sıfır failure/error/skip. [JUnit](acceptance-final.xml), [komut ve kaynak
  SHA-256](acceptance.json). Yalnız yerel test/fixture; browser kurulumu ve Docker yok.
- Aynı API-key ve evidence-link regresyonları eski commit'in exporter'ı
  git show ile yalnız bellekte yüklendiğinde **2 failed**. [Özet](before-summary.json),
  [JUnit](before.xml), [repro script](reproduce_before.py). Script beklenen
  iki başarısızlığı gördüğü için exit 0 döner; pytest'in kendisi exit 1'dir.
- İlk komut olmayan test_evidence_model.py adını içerdi: hiçbir test koşmadı.
  [İlk kayıt](acceptance.xml) korunur ve başarı sayılmaz; doğru komut
  acceptance-final.xml üretmiştir.
- 23 yeni test bilinen credential alanları, nested değerler, JSON/HTML,
  HTTP(S) evidence linkleri, IPv6/boş query, input immutability, case handling,
  HTML escaping ve idempotence kontrolünü mevcut 103 regresyonla birleştirir.
- JUnit hostname alanları paylaşım kopyasından çıkarıldı. Red test çıktıları
  yalnız açıkça FAKE olarak adlandırılmış sentinel içerir. Kaynak hash'leri
  koşu sonrası alındı; koordinatör bu dosyalarda koşu sırasında değişiklik
  olmadığını kontrol etti. Eski 185/94 sayıları yeni 126'ya eklenmez.

## Sonraki kapı

Yeni teslimin uzak CI sonucu ayrıca izlenecek. R4 yeni uzak artifact kabulü
[tamamlandı](../2026-10-12-r4-ci-acceptance/remote/acceptance.json); gerçek ürün
bootstrap/login/port-discovery adapter'ı açık. Taşıma için kullanıcının mevcut
xss klasörünün tam yolu bekleniyor; başka depo ezilmeyecek.
