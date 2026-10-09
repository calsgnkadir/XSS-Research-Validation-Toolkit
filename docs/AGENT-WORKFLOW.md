# Roadmap'e bağlı uzman çalışma düzeni

9 Ekim teslim istisnası: kullanıcı 8–9 Ekim çalışmalarının yeniden testinden sonra
koordinatöre commit ve GitHub push yetkisi verdi. Aşağıdaki önceki Git yasağı bu
teslime uygulanmaz; uzmanlar bağımsız Git teslimi yapmaz.

## 8 Ekim 2026 — geçerli geliştirme yetkisi

Kullanıcı ROADMAP'in uygulanabilir açık işlerini bağımlılık sırasıyla geliştirmeyi
onayladı. Aşağıdaki 6/7 Ekim yetki açıklamaları tarihsel kayıttır. Beş native
rolün kalıcı TOML sandbox değeri `workspace-write`; görevleri uygulama kodu ve
anlamlı regresyon yazmayı kapsar. Bu değer gerçek runtime yetkisi kanıtı değildir;
yazma ve test sonuçları görev kaydında ayrıca tutulur. Yeni ayarlar önceden
çalışan agent'a uygulanmış sayılmaz.

Koordinatör en fazla iki uzmanı eşzamanlı çalıştırır. Her atama roadmap kimliği,
özel dosya sahipliği, kabul koşulu ve yerel test sınırı içerir. Uzmanların bütün
diff'leri koordinatörce incelenir; hatalı/eksik teslim aynı uzmana geri gönderilir.
Bağımsız QA oracle'ı ve birleşik testler kabulün parçasıdır. Sırf beş rolü meşgul
etmek için iş yaratılmaz; uygun uygulama işi koordinatörde tutulmaz.

Security: güvenlik/context/confidence ve kod/test; Engine: scanner/scope/request/
runner/adapter; Storage: mevcut SQLite/callback/Docker ve test; Report: mevcut
HTML/JSON, güvenli çıktı ve kullanılabilirlik; QA: bağımsız oracle/fixture,
regresyon ve lab entegrasyonu. Ortak sözleşme ve ana roadmap koordinatördedir.

Commit, push, dış yayın, veri silme ve arka plan otomasyonu yapılmaz. Yalnız
izinli yerel/disposable lab test edilir. Madde başına tekrar onay istenmez.
Engeller ve kesinti öncesi ilerleme audit'e kaydedilir; duran görev aktif diye
sunulmaz. Ana plan ROADMAP'tir; audit görev kuyruğu ikinci roadmap değildir.

Bu belge agent çalıştıran bir yapılandırma değildir. Kalıcı proje talimatıdır;
gerçek sub-agent'lar mevcut oturumun collaboration araçlarıyla çağrılır.
Başlangıçta toplam dört eşzamanlı slot vardı: koordinatör + üç uzman.
Kapasite her oturumda değişebilir. Otomatik açılış veya zamanlanmış iş yoktur.

## Kalıcı tanım ile çalışan agent ayrımı

**7 Ekim 2026 güncellemesi:** Bu sohbetin beş native `agent_type` çağrısı
başarılıdır; [çağrı ve kapsam kaydı](../audit/2026-10-07-r4-native/README.md).
Aşağıdaki doğrulanamadı kayıtları önceki ortamın tarihsel durumudur.
Yeni geliştirme görevlerinde native rol kullanılır. Engine ve QA tanımları
proje kapsamında `workspace-write` olarak güncellendi; diğer üç rol read-only.
Eski çalışanlara yeni ayar uygulandığı varsayılmaz; görev sınırı ve gerçek
araç sonucu ayrıca kaydedilir. Genel sistem/ağ yetkisi genişletilmez.

### Tarihsel durum — 6 Ekim ortamı

Aşağıdaki rol seçici yokluğu ve geçici talimat aktarımı, 6 Ekim ortamına aittir;
7 Ekim'de doğrulanan native çağrıların güncel durumu değildir.

`.codex/agents/` altında beş mevcut TOML tanımı korunur: `xss_security_researcher`,
`scanner_engine_specialist`, `storage_docker_specialist`, `report_frontend_specialist`,
`qa_security_lab_specialist`. Dosya varlığı native invocation kanıtı değildir.
Mevcut oturumun `collaboration.spawn_agent` aracı custom-agent dosyası/rol seçme
parametresi sunmuyor: **CONFIGURATION EXISTS, BUT INVOCATION IS NOT VERIFIED**.

Geçici specialist çağrısına bu dosyayı okuma görevi vermek, Codex'in dosyayı
custom-agent configuration olarak yüklediğini kanıtlamaz. Böyle bir çağrı açıkça
geçici sub-agent olarak raporlanır. Bu Markdown ve AGENTS.md agent configuration
yerine geçmez. Aynı başarısız native kontrol sonraki oturumlarda tekrarlanmaz.
Yalnız ortamda yeni bir rol seçme yeteneği ortaya çıkarsa yeniden doğrulanabilir;
gerçek çağrı ve sonuç kaydedilmeden VERIFIED yazılmaz. Bu ayrı kurulum engeli
onaylı geliştirmeyi engellemez.

Native seçim doğrulanana kadar desteklenen çalışma yöntemi şudur: koordinatör
görevlendirmeden önce ilgili `.codex/agents/<rol>.toml` dosyasını okur; rolün
developer instructions metnini, somut iş sınırını, düzenlenebilecek dosyaları,
gerçek araç yetkisini ve kabul ölçütünü geçici `collaboration` çalışana aktarır.
Bu yöntem native TOML yüklemesi değildir. TOML'deki model/sandbox ayarları
kendiliğinden uygulanmış varsayılmaz; çalışan aracın gerçekten verdiği yetkiler
geçerlidir. Her teslimde rol dosyası, geçici agent adı, gerçek katkı ve test
sonucu audit/staj kaydına yazılır.

| Rol | Gerçek proje alanı | Sınır / çıktı |
|---|---|---|
| Koordinatör | Ana ROADMAP, kanıt kayıtları, ortak sözleşmeler, entegrasyon | Görev/bağımlılık seçimi, çelişki çözümü, dosya sahipliği, son kontrol ve kullanıcıya teslim |
| XSS Security Researcher | dxa.py, dxadom.py, dxaprove.py, dxa_evidence.py; R1/R3/R8, K/C/A | Source/sink/context, encoding/sanitizer ve evidence incelemesi. Canary execution ayrı, vulnerability triage ayrı. Yeni CVE varsaymaz. |
| Scanner Engine Specialist | dxadyn.py, dxa2dyn.py; R2/R4/R8/R9 | Discovery, request, rate, dedup, olay/rapor adapter'ı. UI veya veri şemasına izinsiz yayılmaz. |
| Backend + Database + Docker Specialist | dxa_callback.py, dxa_attempts.py, bench/targets; R9 ve R4 gerçek lab adapter'ı | Stdlib callback HTTP servisi, doğrudan SQLite kayıtları ve Compose. Genel ürün backend'i, ORM veya queue varmış gibi davranmaz. |
| Security Dashboard + Frontend Specialist | Mevcut HTML renderer'ları, reports/preview, README ve vaka sunumu; K05/P/R6 | Şu an dashboard yok. Rapor okunabilirliği, evidence/severity ayrımı, escaping ve hassas veri görünürlüğünü inceler; yeni frontend eklemez. |
| QA + Security Lab Specialist | bench/, test_*.py, cases/, CI ve audit; R4/R5/R9 | Pozitif/negatif oracle, hata/skip kapsamı, temiz ortam tekrar üretimi, CI artifact kanıtı. Yalnız izinli lab. |

## Görevlendirme sözleşmesi

Koordinatör her göreve şunları yazar: roadmap kimliği; depo ve başlangıç commit'i;
analiz mi onaylı uygulama mı; okunacak/düzenlenebilecek dosyalar; yasak kapsam;
beklenen çıktı; test izni ve sınırı. Analizde bütün uzmanlar salt okur.

Uzman çıktısı: incelenen kapsam; doğrulanmış özellikler; dosya:satır kanıtlı
sorunlar; ayrı şüpheler ve doğrulama adımı; roadmap eşlemesi; önerilen en küçük
teslim. Çalıştırılmayan test ve görülmeyen CI sonucu açıkça belirtilir.

Koordinatör bulguları doğrular, mükerrerleri birleştirir ve mevcut audit kaydına
işler. ROADMAP'in yerine ikinci backlog kurulmaz. Görev kaydı ilgili audit
belgesinde rol/görev/durum/kanıt olarak tutulur; öğrenme kaydı ilgili staj
belgesine bağlanır. Bir specialist'in iddiası tek başına kabul kanıtı değildir.

## Onay sonrası geliştirme akışı

1. Roadmap'ten küçük kabul kapsamı seç; çalışma ağacını ve dosya sahipliğini kaydet. Native seçim doğrulanmadıysa ilgili rol TOML'sini oku ve görev metnine aktar.
2. Security kanıt sözleşmesini, Engine adapter'ı, QA karşı örnekleri inceler.
   Depolama/Docker veya rapor değişmiyorsa ilgili uzmanı çağırmak zorunlu değildir.
3. Bağımsız dosyalar paralel; ortak dosyalar sırayla veya yalnız koordinatörce düzenlenir.
4. Kök neden düzeltmesini ilgili regresyonla doğrula; sonuçları ve sınırları kaydet.
5. Koordinatör entegrasyon, diff ve gerçek test çıktısını kontrol eder; roadmap
   durumunu yalnız kanıt varsa ilerletir. Git işlemlerini uzmanlar bağımsız yapmaz.

Kullanıcı R9 yerel scope, R3 eval karşı örneği ve R4 adapter/runner için sınırlı
geliştirmeyi onayladı. Bu kapsamda rutin adımlar yeniden onay beklemez;
kapsam dışı geliştirme ve dış yayın için mevcut yetki sınırları korunur.
