# Ana proje roadmap'i — XSS botu ve staj araştırması

**23 Ekim güncel durum — A04 / A05 / R7 / R3–R6:** A04'ün roadmap'teki seçilmiş GET
rotaları için bounded kabulü tamamlandı; ürün-geneli güvenlik iddiası değildir.
BCrypt'in 72 UTF-8 bayt düzeltmesi ve Boot 4.1.1 / Security 7.1.1 yükseltmesi
sonrasında önceki kaynakta 665/665 Kadrom testi geçti; güncel test-only commit
`1276892` ile toplam verify 770/770 geçti. Boot 4 uyumluluğu için Resilience4j
2.4.0 Boot 4 modülü ve AspectJ starter eklendi; testlerde H2 2.4.240'ın
Hibernate enum CHECK hatası 2.3.232 test sürümüyle giderildi. Son Maven ağacının
248 koordinatlık OSV querybatch snapshot'ında 248 yanıt satırı ve 0 eşleşme
vardı; bu “CVE yok” veya üretim ağacı sonucu değildir. Ayrıntı:
[remediation](audit/2026-10-22-a05-bcrypt-remediation/README.md) ·
[bağımlılık taraması](audit/2026-10-22-a05-dependency-refresh/README.md).
Kadrom main `1276892`'ye test-only multipart kontrolü push edildi; bu source'ta
yerel verify 725 unit + 45 integration ve GitHub Actions 39919982298 geçti.
Sonra temiz checkout `b374095`'e fast-forward oldu; GitHub Actions 39925048373
bu güncel kaynak için başarılı. `b374095` ve bu oturumun üç yerel değişikliği
üzerinde Maven verify 739 unit + 45 integration ile geçti. A04/A05 değişiklikleri
`0ea07ed77c9d2edfc8a3e4394d3ab3700ca69de0` olarak push edildi; Actions
`39928860888` aynı SHA için geçti. [Teslim kaydı](audit/2026-10-23-a04-a05-current-source-regressions/README.md).
Önceki
`d96b835`
backend hatasının public log erişimi 403 olduğu için kök neden bilinmiyor.
Multipart olağan işlevsel testleri 6/6 geçti; malformed parser cleanup hâlâ
doğrulanmadı. A05 Sort invalid-property HTTP 500 için dar 400 düzeltmesi ve
3 kontrol geçti; bu DoS/CVE düzeltmesi iddiası değil. R7 bounded yerel
araştırması güncel applicability disposition ile tamamlandı. Kadrom kaynak
kimliği `b374095`, public tag/release veya formel destek politikası yok;
desteklenen semver yayın iddiası yok. Güncel 248-coordinate OSV sorgusu 248
satır/0 eşleşme verdi; bu üretim ağacı veya CVE yokluğu kanıtı değil. Owner
report workspace'e teslim edildi; dış disclosure yapılmadı.
[R7 kimliği](audit/2026-10-23-r7-source-identity/README.md).
R3/R4/R5/R6 kabul kapsamı tamam; [uzlaştırma](audit/2026-10-22-r3-r6-acceptance-reconciliation/README.md).

**19 Ekim devamı:** C10/C13 ve S02 belge kabulü tamamlandı. K03 SQLi/JWT/BOLA
kontrolleri yerel Juice Shop 20.2.0 imajında yeni, sürümlü ham HTTP kaydıyla
tekrarlandı; bu geçmiş writeup olaylarının doğrulanması veya K04 remediation
retesti değildir. Kanıt ve sınırlar
[K03 audit'inde](audit/2026-10-19-k03-loopback-reproduction/README.md).

**20 Ekim takip:** K03 capture QA tarafından salt-okunur hash/claim kontrolünden
geçti; K04 writeup 01'de kalan recursive sanitizer ve `textContent` açıklama
çelişkisi düzeltildi. R7/A01–A03 tarihsel iddia ve CVE sınırları güncellendi;
R7 ürün araştırması için seçilmiş, açıkça yetkili kapsam hâlâ gerekli. Ayrıntı:
[takip kaydı](audit/2026-10-20-r7-k03-k04-followup/README.md).

**21 Ekim R7/A04:** Kullanıcının seçtiği yerel ürün kapsamı için koordinatör,
kullanıcıya ait Kadrom deposunu `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`
commit'inde inceledi. Bir aday ve bir işletme sentetik hesabıyla uygulama listesi
role/sahiplik sınırı tekrarlandı: kendi listeleri 200 ve tüm satırlar ilgili
hesapla eşleşti; çapraz rol 403, oturumsuz 401. Bu sınırlı koşuda bulgu adayı
gözlenmedi; aynı rol IDOR'u ve diğer uçlar test edilmedi. Bilinen kayıt sayfaları
araçta cache miss verdiği için A04/A05 ve R7 açık kalıyor. Ayrıntı:
[A04 Kadrom kaydı](audit/2026-10-21-a04-kadrom/README.md). K03 uzmanı hash/capture
incelemesini tamamladı; K03 kapsamı kabul edildi, tarihsel oturum/CVE/remediation
iddiaları doğrulanmış sayılmıyor.

**21 Ekim R7/R6 incelemesi:** Kadrom upstream main `ba38bd3` sürümü test edilen
`ae4aebbf` parent'ından yalnız frontend ayarıyla ayrılıyor; GitHub issue API boş,
`0.0.1-SNAPSHOT` ürün release'i değil. Advisory API erişimi inconclusive. A04/A05
incelemesi mevcut iki-rol kanıtını kısmi ve `no-candidate-observed` sonucunu
sınırlı buldu. R6'nın kabul edilmiş `0.1.0` wheel'inden sonra `dxadyn.py`
değişti; güncel kaynak hash'i wheel kabulinden farklı. Karar: güncel wheel/gate
yenilenene kadar release tag'i beklet; ayrıca açık yayın yetkisi gerekir.
[R7/R6 incelemesi](audit/2026-10-21-r7-r6-decision/README.md).

**21 Ekim R6/R7 devamı:** Güncel `6928fd6` kaynağından 0.1.0 wheel yeniden
üretildi; kurulum ve installed-wheel gate 7/7, değişen `dxadyn` odaklı testler
271/271 geçti, dokuz paket modülünün source/wheel/install hashleri eşleşti.
Aynı commit'in genel CI ve K01 Linux işleri de başarılı. Bu R6 teknik kabulünü
güncel kaynak için yeniler; tag/yayın için ayrı açık kullanıcı yetkisi gerekir.
R7 exact-name GitHub Advisory/NVD aramaları eşleşme göstermedi, fakat resmi
sonuçlar erişilemedi ve arama toplamı doğrulanamadı; advisory yokluğu
çıkarılamaz, R7 açık kalır. [R6 kanıtı](audit/2026-10-21-r6-current-source/README.md) ·
[R7 arama kaydı](audit/2026-10-21-r7-advisory-lookup/README.md).

**21 Ekim R6 release:** Kullanıcının yetkisiyle `v0.1.0` anotasyonlu tag'i
`d7d1bd6` commit'ine push edildi; final wheel GitHub Release'e yüklendi ve
GitHub API digest'i yerel SHA-256 ile eşleşti. PyPI'ye yükleme yapılmadı.
[R6 release kaydı](audit/2026-10-21-r6-release/README.md).

**21 Ekim A04/A05 takip:** Aynı-rol ID tabanlı work-session GET uçları ve
aday-ID sahiplik filtresi kaynakta bulundu; Docker API izin hatası nedeniyle
lab güvenlik durumu doğrulanamadı ve runtime isteği gönderilmedi. A05 resmi
GitHub/NVD API kontrolü erişilemez kaldı; indeksli sonuçlar kapsamlı olmadığından
bilinen kayıt durumu inconclusive. R7 açık; test adayı veya advisory yokluğu
iddia edilmiyor. [A04 aynı-rol takip](audit/2026-10-21-a04-same-role-followup/README.md) ·
[A05 kayıt takibi](audit/2026-10-21-a05-known-records-followup/README.md).

**21 Ekim A04/A05 devamı:** İkinci Docker read-only inspect denemesi de permission
denied ile engine durumunu alamadı; servis ve HTTP isteği çalıştırılmadı. GitHub
public REST üzerinden issues/releases/tags boş, dört exact Maven GHSA filtresi
boş döndü; repo-özel advisory 404. NVD 406 challenge verdi, CVE.org query
render etmedi. A05 kısmi/inconclusive, A04 runtime testi bekliyor; R7 açık.
[A04 runtime](audit/2026-10-21-a04-runtime-followup/README.md) ·
[A05 resmi API takibi](audit/2026-10-21-a05-public-records-followup/README.md).

**21 Ekim A04/A05 ek devamı:** Kadrom'daki mevcut unit/integration testleri
aynı-rol work-session GET sahipliğini doğrulamıyor; izole ve doğrudan ilgili test
bulunmadığından çalıştırma veya test ekleme yapılmadı. Exact PURL ile tek resmi
OSV sorgusu HTTP yanıtı alınmadan bağlantı hatası verdi. A04 runtime ve A05
known-record doğrulaması açık; R7 açık.
[A04 test envanteri](audit/2026-10-21-a04-testability-followup/README.md) ·
[A05 OSV denemesi](audit/2026-10-21-a05-osv-followup/README.md).

**21 Ekim A04/A05 devamı:** QA, eski stopped Kadrom konteynerlerini başlatmanın
Flyway V19 tablo düşürme, startup ALTER, DemoSeeder ve scheduler veri etkileri
olabileceğini doğruladı; eski volume korunuyor. Yeni project/volume/internal
network adları Docker'da boş, izole Compose config'i port yayınlamıyor. Yalnız
bu yeni volume'a sentetik work-session kontrolü eklendikten sonra, iki adayla
list/active/batch GET karşılaştırmasının altı oracle'ı beklenen sonuçla
eşleşti; yeni konteynerler durduruldu, volume korundu. Normal clock-in akışı ve
ürün test suite'i çalıştırılmadı. CVEProject resmi belgelerinde Maven/PURL
lookup doğrulanamadı ve beta Swagger şeması erişilemedi; A05 inconclusive.
[A04 runtime](audit/2026-10-21-a04-same-role-runtime/README.md) · [A04 startup](audit/2026-10-21-a04-startup-safety-review/README.md) ·
[A04 Docker config](audit/2026-10-21-a04-docker-config-followup/README.md) ·
[A05 CVEProject](audit/2026-10-21-a05-cveproject-alternate-followup/README.md).

**21 Ekim R7/A05 güncel devam:** Kullanıcının seçtiği Kadrom yerel kapsamı
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c` sürümüne sabitlenmiştir. Offline
Maven çözümlemesi 21 doğrudan compile/runtime kökünü verdi. Pozitif kontrollü
deps.dev v3 sorgusunda POI 5.3.0 ve Actuator starter 3.2.5 için advisory anahtarı
döndü; POI parser'ına kullanıcı OOXML girdisi ulaşan kaynak yolu bulunmadı,
Actuator GHSA sürüm aralığı ile Spring vendor sürüm listesi çelişiyor ve vendor'ın
route önkoşulu kaynakta görülmedi. 127 transitif bağımlılığın pozitif kontrollü
sorgusu tamamlandı; 18 satırda 92 distinct advisory anahtarı var. Resmî GHSA
sayfalarının aralık kontrolünde 93 koordinat-advisory eşleşmesinin tamamı sabit
sürümü etkilenmiş aralıkta gösterdi. İki kaynak taraması toplam 92 distinct
anahtarın tamamını kapsadı. Spring RFD için ek/indirme akışı kaynakta olası
koşulları karşılıyor; zararsız local doğrulama yapılmadı ve aday doğrulanmış
bulgu değil. Nimbus/Micrometer ve birkaç Spring/Tomcat koşulu kaynakta açık
kalmış durumda. A05/R7 açık; ürün açığı, istismar veya advisory yokluğu sonucu
çıkarılmadı. Ayrıntı:
[etkin ağaç](audit/2026-10-21-a05-effective-dependency-tree/README.md) ·
[21 kök sorgusu](audit/2026-10-21-a05-managed-direct-advisories/README.md) ·
[transitif aralık](audit/2026-10-21-a05-transitive-range-review/README.md) ·
[Spring/Tomcat kaynak taraması](audit/2026-10-21-a05-spring-tomcat-source-review/README.md) ·
[diğer kaynak taraması](audit/2026-10-21-a05-other-source-review/README.md) ·
[POI triage](audit/2026-10-21-r7-poi-source-triage/README.md) ·
[Actuator triage](audit/2026-10-21-r7-actuator-source-triage/README.md).

**22 Ekim R7/A05 devamı:** Önceki Spring RFD kaynağı adayı için Kadrom'un
pinned commit'inde yalnız H2 in-memory ve inert dosya kullanan odaklı kontrol
geçti: anonim `401`, üye olmayan `403`, üye `200`; UTF-8 dosya adı encoded
`Content-Disposition` ile döndü. Bu, browser yorumu veya RFD istismarı kanıtı
değildir. Nimbus yapılandırma/source/JAR incelemesi, bu pinned OAuth2 yolunda
etkilenebilir Nimbus parser'a giden bir zinciri desteklemedi; kaynak JAR'ları
mevcut değildi ve deployment override'ları incelenmedi. A04 kaynak/test
envanteri iki ek business-owner ID GET yolunu (`attendance`, `roster`) önceki
runtime karşılaştırmasının dışında buldu. Yeni disposable lab'da owner1 kendi
listing'i için `/attendance` 200 (boş kayıt) ve `/roster` 200 (3948 bayt XLSX)
aldı; owner2 iki yolda da 403 aldı. Yeni backend/MySQL durduruldu ve volume
korundu; eski volume'a dokunulmadı. Bu, test edilen A04 yolları için bounded
kabul, ürün-geneli sonuç değil. [A04 ek runtime](audit/2026-10-22-a04-owner-read-runtime/README.md).
A05 source triage'i BCrypt login ve Spring Data Sort için
plausible input path buldu; multipart/Micrometer koşulları belirsiz, X.509 range
verisi çelişkili. Odaklı H2 login kontrolünde 72-byte ve aynı ilk 72 byte'ı
paylaşan tek 73-byte input aynı synthetic principal için `200` aldı; testte
hash ilk testte doğrudan 72-byte değerden kuruldu. Takip testi gerçek
registration endpoint'inin bir 73-byte ASCII değeri kabul ettiğini ve farklı
suffix'li girişin aynı hesapta başarılı olduğunu gösterdi. Pinned
`spring-security-crypto:6.2.4`, CVE-2025-22228/GHSA-mg83-c7gq-rv5c etkilenen
aralığında; bu, yerel uygulama yolunda advisory ile eşleşen kusur adayıdır.
Gerçek kullanıcı etkisi/hesap ele geçirme kanıtlanmadı. [BCrypt kontrolü](audit/2026-10-22-a05-bcrypt-local-check/README.md) ·
[BCrypt triage](audit/2026-10-22-a05-bcrypt-triage/README.md) ·
[resmî GHSA](https://github.com/advisories/GHSA-mg83-c7gq-rv5c).
Bir sentetik hesapla tek Sort isteği 231 karakterlik malformed property için
HTTP 500 verdi (`UnknownPathException`); sonraki health kontrolü 200, StackOverflow
gözlenmedi. Bu, advisory DoS koşulunu doğrulamaz. [Sort kontrolü](audit/2026-10-22-a05-sort-local-check/README.md) ·
[A04 kapsam incelemesi](audit/2026-10-22-a04-scope-completeness/README.md) ·
[A05 kalan source yolları](audit/2026-10-22-a05-remaining-paths/README.md).
A04 seçilmiş rotalarda bounded tamam; A05/R7 açık. Sonuç yeni CVE iddiası veya
gerçek hesap ele geçirme kanıtı değildir; ürün-kimliği advisory araması inconclusive.
[RFD kontrolü](audit/2026-10-21-a05-rfd-local-check/README.md) ·
[Nimbus incelemesi](audit/2026-10-21-a05-nimbus-path-review/README.md).

**22 Ekim A05 config takibi:** Salt okunur kaynak/config incelemesinde pinned
`micrometer-core:1.12.5`, Actuator/Prometheus bağımlılıkları ve checked-in local,
test, production profilleri Micrometer advisory önkoşullarını kaynak düzeyinde
destekliyor; etkin runtime bean'leri, deployed override'lar ve DoS davranışı
doğrulanmadı. Multipart/Tomcat için Spring MVC 6.1.6 ve Tomcat 10.1.20 ile upload
yolu ve 20/25 MB YAML limitleri var; part-count, geçici dosya cleanup ve proxy/WAF
koşulları belirlenmedi. Bu koşullar için malformed istek çalıştırılmadı. [Micrometer
incelemesi](audit/2026-10-22-a05-micrometer-config-review/README.md) ·
[multipart incelemesi](audit/2026-10-22-a05-multipart-config-review/README.md).
Docker açılmadan önceki 22 Ekim iki uzman takibi salt okunur runtime kontrolünde mevcut Java app
bulamadı; Docker Desktop Linux engine pipe'i erişilebilir değildi. Bu yüzden
container envanteri bilinmiyor ve Micrometer effective bean/metric ile
Tomcat connector/part-count/temp cleanup ayarları doğrulanmadı. Runtime
başlatılmadı, build/test/request yapılmadı. [Micrometer runtime](audit/2026-10-22-a05-micrometer-effective-review/README.md) ·
[multipart runtime](audit/2026-10-22-a05-multipart-effective-review/README.md).

**22 Ekim üç ajan devamı:** Kullanıcının güncel talimatı üç uzmanın eşzamanlı
çalışmasıdır; eski iki uzman sınırı yerel talimatlarda üçe güncellendi.
Yeni offline Crypto 6.2.4 assay'inde farklı Unicode suffix çiftleri (73/74/75
UTF-8 bayt, 72/72/73 UTF-16 birimi) aynı ilk 72 baytla eşleşti; packaged policy
kabulü ve 72 bayt doğru/yanlış kontrolüyle toplam 9 BCrypt çağrısı yapıldı.
Bu yeni bir Unicode endpoint tekrarı değildir. R7 için [owner-review raporu](research/kadrom-local-triage.md)
hazırlandı; dış gönderim veya ürün düzeltmesi yapılmadı. Multipart specialist'i
runtime öncesi otomatik cyber-risk kontrolüyle durdu; test yeniden çalıştırılmadı,
yeni kaynaklar oluşmadı, taslaklar yerelde korundu. A04 bounded tamam; A05/R7 açık.
[Kabul/koordinasyon](audit/2026-10-22-three-agent-continuation/README.md) ·
[UTF-8 assay](audit/2026-10-22-a05-bcrypt-utf8/README.md) ·
[Multipart engeli](audit/2026-10-22-a05-multipart-bounded/README.md).

**22 Ekim Docker sonrası A05:** Yeni internal network ve yeni MySQL volume'larıyla,
host portu yayınlamadan iki diagnostic context çalıştırıldı. HTTP observation
filtresi kayıtlı ve normal GET metriği `0→1`. Etkin multipart file/request
limitleri `20.971.520/26.214.400` bayt, eşik `0`; temp ve connector değerleri
okundu, part-count getter'ları yok. Ayrı koşuda tek gövdesiz `A05CHECK` isteği
`400`, metrik yöntemi `UNKNOWN`; normal health önce/sonra `200` oldu. Ham özel
yöntem etiketi veya DoS yeniden üretilmedi; parser cleanup/proxy koşulları test
edilmedi. Aynı cached image/JAR kullanıldı ve base/dev/prod YAML hash'leri
pinned kaynakla eşleşti; diagnostic launcher farklıdır ve tam source/build
eşdeğerliği yeniden üretilmedi. Yeni konteynerler durduruldu, yeni/eski
volume'lar korundu. Security'nin resmî kayıt takibinde Actuator/X.509 sürüm
çelişkileri ve ürün-kimliği sorgularının inconclusive durumu sürdü. A04 bounded
tamam; A05/R7 açık. [Preflight](audit/2026-10-22-a05-runtime-preflight/README.md) ·
[Yöntem kontrolü](audit/2026-10-22-a05-micrometer-method-check/README.md) ·
[Advisory](audit/2026-10-22-a05-advisory-disposition/README.md) ·
[QA](audit/2026-10-22-a05-runtime-qa/README.md).

17 Ekim tarihli durum snapshot'ı: R4/R5 teknik kapanışı, R6 yerel paket kabulü, R8 bounded
pilot ve R9 operasyon/CI kabulü tamamlandı;
R6 ilk araştırma sürümü için release hazırlığı yapıldı, yayımlanmadı.
Bu turdaki yeniden kontroller de R4 için 57/57, R5 fixture/gate için 22/22
geçti. İnsan triage'ı, ikinci insan tekrarı ve scanner üstünlük sıralaması
kullanıcı kapsam kararıyla zorunlu kapanış ölçütü değildir. Sonuçlar genel ürün
doğruluğu veya vulnerability iddiası oluşturmaz. Bot işlerinde R7/A01–A05 için
yetkili araştırma kapsamı seçimi açık. 17 Ekim'de C/K/P, S01 ve S03 kabulü
kaydedildi; C10/C13 editoryal takipleri ve S02 matrisi 19 Ekim'de ayrıca kabul edildi.

14–15 Ekim devam teslimi aşağıdaki tarihli kayıtlarda korunur; o tarihteki
“genel R4/R6 ve R5 ikinci insan kabulü açık” durumu 16 Ekim kapanışından önceki
durumdur, güncel devam noktası değildir. [Devam raporu](audit/2026-10-14-r3-r6-continuation/README.md).

## 14 Ekim 2026 — tarihli yetenek snapshot'ı

**Aşama:** araştırma amaçlı Python CLI ve rapor prototipi. Paketlenmiş release
henüz yok. R4 auth runner kodu **bec59b4**, R5/K01 aynı-host kanıt commit'i
**70093ff**; sonraki R5/R8/R6 kodu **d41c1cd** için CI ve ilgili indirilen
artifact kabulü geçti. Güncel HEAD ve açık işler [STATUS](STATUS.md) içindedir.
[Durum](STATUS.md) · [Doğrulama](VALIDATION.md) ·
[Corpus v3 kabulü](audit/2026-10-14-r4-corpus-v3/README.md).

| Soru / alan | Kanıtlanan durum | Sınır / kalan kabul |
|---|---|---|
| Bot gelişti mi? | Corpus 9'dan 14'e çıktı; kaynak/parametre/okuma/rol/frame eşlemesi ve CI artifact doğrulaması güçlendi. | Bu gelişme ölçüm güvenilirliğidir; gerçek ürünlerde başarı oranı henüz ölçülmedi. |
| XSS adayı bulabilir mi? | Statik aday analizi, HTTP reflection ve stored akışları, DOM/sink gözlemleri, oturum/CSRF desteği mevcut. | Her adayın bağlamı ve etkisi ayrıca incelenir; reflection açık kanıtı değildir. |
| JavaScript çalışmasını doğrulayabilir mi? | İzinli loopback lab'da submit→read→eşleşen canary execution; corpus 14/14, TP=7 FP=0 FN=0. | Yedi pozitif/yedi negatif kontrollü vaka; genel web veya ürün doğruluğuna genellenmez. |
| Blind/admin seviyesi | Stored/stored-auto attempt kaydı ve CID callback uzlaştırması mevcut. | Callback JS execution değildir; ayrı admin hesabı/yetki sınırı kabulü açık. |
| CVE araştırmasına yardım eder mi? | Aday toplama ve tekrar üretilebilir kanıt hazırlamaya yardımcı olabilir. | Yeni CVE keşfi doğrulanmadı. Ürün/sürüm, etkilenen rol, güvenlik etkisi, by-design/self-XSS ayrımı, yenilik ve fix/retest incelemesi gerekiyor. |
| Araçlarla karşılaştırma | Kapsam, bütçe ve kanıt eşitliğini tanımlayan protokol var. | Kontrollü rakip koşusu ve karşılaştırılabilir başarı ölçümü yok; üstünlük iddiası yok. |
| Test kanıtı | R4 auth runner etkili paket 215 passed; CI 3/3, artifact gate 169 test ve 14/14 corpus; auth kontrolleri 6/6. R5 K01 yeni venv 5/5. | Farklı paketlerin sayıları toplanmaz; bu belge güncellemesi yeni test koşusu değildir. |

**Son dar ilerleme:** auth/CSRF altı hata kontrolü gerçek browser ile, yedi
blind/admin adapter sınır testiyle birlikte 13/13 geçti; ayrı bounded CLI 6/6.
Ana benchmark runner entegrasyonu da yerel 215 birleşik test ve gerçek CLI 6/6
ile kabul edildi; bec59b4 uzak CI 38593458769 3/3 geçti ve indirilen
artifact 169 JUnit, proof 14/14, auth controls 6/6 kabul edildi.
[Runner kanıtı](audit/2026-10-14-r4-auth-runner/README.md).
[Önceki dar kanıt](audit/2026-10-14-r4-auth-blind-controls/README.md).
Engine entegrasyonu tamamladı; R5 QA aynı-host tekrarı yaptı. Aktif uzman yok.
Gerçek admin/blind fixture ve kontrollü kıyas açık.

**14 Ekim üçlü devam teslimi:** R5 için yeni Ubuntu/Python 3.12 K01
workflow'u ve artifact gate yazıldı; Windows'ta 104 birleşik regresyon
ve gate 5/5 doğrulandı; d41c1cd Linux run 38596197622 de başarılı:
13 JUnit, 5/5 proof ve indirilen artifact digest/kaynak hashleri eşleşti.
[R5 gate kanıtı](audit/2026-10-14-r5-linux-gate/README.md).
R8 açık encoder rebinding kaynaklı statik FN düzeltildi; 91 odaklı test
geçti. d41c1cd genel CI 38596197488 3/3 başarılı.
[R8 kanıtı](audit/2026-10-14-r8-rebound/README.md).
R6 geliştirici paketi temiz venv'de kuruldu, üç CLI help ve paketlenmiş
browser demo çalıştı; d41c1cd CI paket install/help adımı geçti.
Sürüm etiketi/yayın yok.
[R6 kanıtı](audit/2026-10-14-r6-package-scaffold/README.md).
Blind/admin ve araç kıyası bu turda ele alınmadı.

**Üç işin yeniden denetimi:** R8'de fonksiyondan önceki modül düzeyi encoder
atamasının gözden kaçtığı karşı örnek bulundu ve dar regresyonla düzeltildi.
R6 wheel temiz venv'e kaynak dizini dışında kuruldu; R5 ayrı agent yeni kanıtla
5/5 tekrarladı. 74cda81 için genel CI 38598901908 3/3 ve Linux K01
38598901721 geçti; indirilen K01 artifact'i kabul edildi. Bunlar ikinci insanın
temiz makine kabulü değildir.
[Yeniden denetim](audit/2026-10-14-three-work-recheck/README.md).

**Kalan sıra:**
1. R4 genel corpus genişletmesi, blind/admin kimlik ve kanıt sınırları,
   eşit koşullu araç karşılaştırması. Auth/CSRF operasyonel hata kontrolleri
   dar kapsamda runner/CI kabulünü geçti.
2. R4 geniş corpus/coverage kabulü ve R3 otomatik header gözlemi.
3. R5/K01 bağımsız temiz ortam tekrarı; R6 kurulum/paketleme/release.
4. R8 analiz kapsamı, R9 operasyon sınırları; aşağıdaki C/K/P/S maddeleri.
5. A01–A05/R7 ürün bazlı araştırma ve CVE triage; yeni doğrulanmış CVE yok.

### Önceki ilerleme kayıtları

Aşağıdaki tarihli paragraflar ilgili teslim anını anlatır; güncel devam noktası
yukarıdaki özet ve STATUS'tur. Tarihsel açıklar daha sonraki dar kabullerle
ilerletilmiş olabilir; ana kabul kutuları aşağıda korunur.

9 Ekim ilerleme kaydı: R4 hard timeout/süreç temizliği, R8 statik context ve
R9 callback/Docker guard değişiklikleri tam yerel tekrarda **824 passed**;
ayrı K01 HTTP fixture **2 passed**, Chrome proof **9/9, TP=3 FP=0 FN=0**.
[Kabul ve kapsam](audit/2026-10-09-resume/README.md). Bu dar teslim genel
R4/R8/R9 kutularını kapatmaz; gerçek ürün bootstrap/port-discovery adapter'ı ve
uzak Linux CI artifact kabulü açık kalır. 11 Ekim kontrolde `5df2577` için
uzak CI/job sonuçları başarılı bulundu; artifact içerikleri henüz incelenmedi.
Güncel devam noktası [STATUS](STATUS.md); aşağıdaki 6–7 Ekim test sayıları tarihseldir.

13 Ekim dar R4 teslimi: sabit Bludit 3.16.2 yerel imajı için internal uygulama +
loopback Apache ingress adapter'ı gerçek Docker kabulünde kurulum, login ve
ham/escaped browser kontrolünü tamamladı. Eksik browser ve enjekte edilmiş
kontrol uyuşmazlığı güvenli hata; üç cleanup geçti, 15/27/9 mevcut Docker
kaynağı korundu. Birleşik **335 test sıfır skip**. [Kanıt](audit/2026-10-12-r4-ingress-live/README.md).
Gerçek ürün benchmark skorlayıcısına bağlanmadı; genel R4/R9 açık kalır.

12 Ekim dar teslim: zorunlu R3/R4 CI artifact kapısı yerelde JUnit sıfır-skip,
dokuz vaka tutarlılığı ve demo execution kontrolüyle doğrulandı.
[Yeni kanıt](audit/2026-10-12-r4-ci-acceptance/README.md). Uzak artifact API'si
HTTP 401 verdi; içerik kabulü ve yeni kapının uzak CI koşusu açık. Genel
R4/R9 kutuları değişmedi; Git teslimi kullanıcı tarafından sonradan onaylandı.

12 Ekim devamı: `c5d5451` uzak Linux CI ve indirilen artifact kabulü geçti:
94 test sıfır skip, dokuz vaka TP=3 FP=0 FN=0 ve demo execution-observed.
[Uzak kanıt](audit/2026-10-12-r4-ci-acceptance/remote/acceptance.json).
R9 ortak JSON/HTML raporlarında bilinen API/CSRF alanları ve HTTP(S) evidence
linkleri için maskeleme düzeltildi; [126 testlik dar kabul](audit/2026-10-12-r9-report-privacy/README.md).
Gerçek ürün adapter'ı ve genel R4/R9 kutuları açık kalır.

6 Ekim 2026 güncellemesi. **Öncelik: bot → rapor ve kanıt → portfolyo → staj → araştırma/CVE.**
Bu belge bütün projenin ana iş listesidir. Aşağıdaki R/C/K/P/S/A kimlikleri görevleri izler;
STATUS yalnız kısa durum özeti, eski ROADMAP-LEGACY ise tarihsel kayıttır.

## Kapsam ve çalışma düzeni

Kaynaklar: ZIP'teki 76 dosyanın denetimi, iki eski sohbet metni ve kullanıcının son öncelikleri.
[Denetim raporu](audit/2026-09-28/DENETIM-RAPORU-TR.md) başlangıç bulgularını,
[dosya–görev eşlemesi](DOSYA-KAPSAM.md) bütün orijinal dosyaların hangi işte takip edildiğini gösterir.
Orijinal ZIP ve denetim kopyası korunur. Güncel Git çalışma alanı `xss-github`;
önceki `xss-bot-work` kopyası geliştirme kaynağı değildir.
ZIP dışındaki resmî staj PDF'leri önceki kapsam kararı uyarınca dahil değildir.

Sıra, mevcut teknik kapasiteyi düzeltmeye öncelik verir. Her bot düzeltmesinin testi ve kısa
öğrenme kaydı aynı teslimde tutulur; portfolyo vitrini ve CVE avı teknik açığın önüne geçmez.
Yeni dış hedef taraması, hesap açma, disclosure veya yayın bu roadmap oluşturulurken yapılmaz.

| Öncelik | Alan / kimlik | Başlangıç durumu | Alanın kapanışı |
|---|---|---|---|
| 1 | Bot R0–R9 | R0–R6 tamam; `v0.1.0` GitHub Release yayımlandı (PyPI hariç). R8 bounded pilot ve R9 bounded operasyon/CI kabulü tamam; R7 source kimliği ve yerel advisory taraması bounded tamam | Doğru kanıt, güvenilir oturum, browser entegrasyonu, ölçüm, kurulabilir sürüm ve operasyon sınırları |
| 2 | Rapor C01–C13; kanıt K01–K05 / R5 | 19 Ekim C10/C13 düzenlemesi tamam; K03 yerel sürümlü tekrarları var; eski saha iddiaları ayrıca sınırlandı | İddia sınırları, yayın kopyaları, K01, K03 yeni loopback kanıtı ve arşiv rapor etiketleri kaydedildi; yeni tekrar eski tarihsel seansı doğrulamaz |
| 3 | Portfolyo P01–P04 | P01–P04 tamam | Üç seçilmiş kanıt yolu, temiz kurulum ve yerel tekrar; proje tanımı sınırlı ve 06–10 tarihi seri olarak gruplanmış |
| 4 | Staj S01–S03 | S01/S02/S03 tamam | Oturum kaydı, teknik devam özeti ve 11 yazılık beceri/kanıt matrisi hazır |
| 5 | Araştırma/CVE A01–A05 / R7 | A04 seçilmiş GET rotaları önceki runtime kanıtıyla bounded kabul edildi; yeni source'ta üç work-session GET için kalıcı iki hesaplı HTTP regresyonu geçti. BCrypt ve ordinary multipart 6/6 önceki test edilen source'ta geçti; `b374095` + bu oturum değişiklikleri full verify 739 unit + 45 integration olarak geçti. A05 Sort malformed alanı için 3/3 geçti; bu advisory DoS düzeltme kanıtı değildir. 24 Ekim'de current `eb031a1` için parser cleanup bir küçük embedded Tomcat/Spring fixture testinde 1/1 geçti; full app/auth/proxy veya genel parser garantisi değildir. Seçilmiş A05 advisory version/source disposition güncel; bounded R7 tamam, 248 satır/0 eşleşme önceki query'nin aynı graph'a bound edilmiş sonucu ve “CVE yok” kanıtı değil | Tek fixture sonucu ve sınırlarını kaydet; A05 wider disposition partial; dış disclosure yok |

Durum sözlüğü: **açık** iş yapılacak; **devam** bir kısmı doğrulandı; **tamam** kabul kanıtı var;
**kanıt bekliyor** tarihsel iddia bağımsız doğrulanamıyor; **ertelendi** kapsamdan silinmedi.
Eksik kanıt, geçmiş olayın yaşanmadığının kanıtı değildir. Toplam yüzde kullanılmaz.

## İlk çalışma paketi

1. R1 normal dialog yanlış pozitifi — **tamam**, altı regresyon ve yerel Chrome kaydı var.
2. R1 callback ≠ JS proof; cid eşleşmesi; gizli veri toplamayan beacon — **tamam**: HTTP ve JS kapalı Chrome negatif kontrolü; test kaydı VALIDATION.md.
3. R1 yansımasız blind takip — **stored/stored-auto için tamam**; ortak şema, DOM/statik/HTTP/journal raporları ve konservatif dedup — **tamam**. [Kapanış kanıtı](audit/2026-10-05-r1/R1-KAPANIS.md).
4. R2 JSON/auth/rate/CSRF HTTP kabulü — **tamam**. R8 sanitizer karşı örnekleri ve sınırlı Python AST pilotu — **tamam**; genel soundness iddiası yok.
5. R1 sonrası **K01-min**: tek yerel XSS vakası, manuel/browser canary kanıtı, negatif kontrol, fix ve retest. Tam R5/R6 kapanışı sayılmaz. R2→R3→R4 bot hattı devam eder.

R1'in aşağıdaki kabul kapsamı tamamlandı; botun tamamlandığı anlamına gelmez.
HTTP normal/flow/stored/header bulguları ortak üreticiye taşındı; JSON-only ve
ham marker'ın execution diye raporlanması giderildi. JSON/HTML aynı finding'leri
kullanıyor. [5 Ekim model ve sınırları](tools/dom-xss-analyzer/HTTP-EVIDENCE.md).
R3 browser proof komutu loopback demo, observer/eval, SPA route ve allowlist header
desteğiyle çalışıyor; WebSocket/genel ağ sandboxı bu komutun scope'u dışında.
Rapor C01–C13, kanıt K01–K05, portfolyo P01–P04, staj S01–S03 ve araştırma
A01–A05 kapsamdan çıkarılmadı; aşağıdaki kabul koşulları geçerlidir.

### Son kanıt ve teslim sırası

| İş | Son kabul kanıtı | Durum / sonraki kapı |
|---|---|---|
| R1 | 2026-10-05, [kapanış matrisi](audit/2026-10-05-r1/R1-KAPANIS.md) | Tamam; 479 passed, 36 skipped |
| R2 | 2026-10-06, [kapanış matrisi](audit/2026-10-06-r2/R2-KAPANIS.md) | HTTP kabul kapsamı tamam; browser oturum aktarımı R3'te |
| R3 | 2026-10-07, [yeniden doğrulama](audit/2026-10-07-r3-r4-revalidation/README.md) | Loopback kabulü PASS; eval/canary/evidence yeniden sınandı, cleanup/state restorasyonu düzeltildi |
| K01-min / R5 | [16 Ekim teknik kabul](audit/r5-final-acceptance-2026-10-16/README.md) | Tamam; temiz Windows venv 5/5 ve tarihsel Linux artifact gate 5/5; ikinci insan koşusu zorunlu kapsamdan çıkarıldı |
| R4 | [16 Ekim kapanış kanıtı](audit/r4-proof-experiment-2026-10-16/README.md) | **Kapsamlı teknik teslim tamamlandı:** kimlik scorer/gate, browser CI/artifact, Bludit lifecycle ve exact-payload replay kabul edildi. Ürün doğruluğu veya araç sıralaması iddiası yok. |
| C/K/P/S02 | [17 Ekim C/K/P kabulü](audit/2026-10-17-p01-p04/README.md); [19 Ekim K03 tekrarı](audit/2026-10-19-k03-loopback-reproduction/README.md); [S02 matrisi](staj/2026-10-17-s02-beceri-kanit-matrisi.md) | C10/C13 ve S02 tamam. K03 envanterine yeni sürümlü loopback tekrarları eklendi; historical writeup session'ları hâlâ author-reported. Diğer C/K/P kabulleri kendi sınırlarında korunuyor. |
| A01–A05 / R7 | 20–24 Ekim tarihsel iddia düzeltmeleri, [A04/A05 current-source regresyonları](audit/2026-10-23-a04-a05-current-source-regressions/README.md), [A05 parser cleanup](audit/2026-10-24-a05-multipart-cleanup/README.md), [R7 kaynak kimliği](audit/2026-10-23-r7-source-identity/README.md) ve [güncel disposition](audit/2026-10-23-a05-current-source-disposition/README.md) | A01–A03 tarihsel/author-reported sınırlarında; A04 seçilmiş GET kapsamı bounded tamam. BCrypt remediation ve dar Sort 500→400 regresyonu kabul edildi; advisory DoS veya gerçek hesap etkisi iddiası yok. Bounded R7 yerel araştırma ve workspace owner raporu tamam. A05 parser cleanup current `eb031a1` üzerindeki tek fixture'da geçti; full app/auth/proxy, diğer parser koşulları ve daha geniş dependency/advisory disposition kapsam dışında; A05 genel kalemi kısmi. Önceki 248-coordinate OSV sonucu aynı kayıtlı graph ile ilişkilendirildi, yeniden koşulmadı ve CVE yokluğu kanıtı değil. |

Kanıt tarihi belgeye son dokunulma tarihi değildir. Kabul kanıtı eklenmeyen iş
yalnız düzenleme yapıldığı için güncellenmiş sayılmaz. Her teslimde bu tabloya
bakılır; iki teslim boyunca ilerlemeyen aktif iş küçültülür veya gerekçesi yazılır.

İlk kaba efor varsayımı (taahhüt veya geçmiş çalışma saati değil): K01-min 1–2,
R2 auth/token 1–2, rate/CSRF 2–3 odaklı oturum. Bir oturum için 2–3 saat varsayılır;
ilk karşı örnekte tahmin yenilenir. R3/R4 ve kalan C/K işleri henüz parçalanmadığı
için toplam bitiş tarihi verilmez. Kullanıcı kapasitesi bilinmeden takvim üretilmez.

C önceliği: C01 XSS proof/fix, C11 araç doğruluğu, C05 iki hesaplı BOLA kanıtı.
C10 yalnız K01'i destekleyen payload/kanıt bölümleriyle aynı pakete alınır.
C02–C04 ve C06–C09 sonraki düzenleme sırasındadır; silinmez ve tamamlanmış sayılmaz.
C12/C13 ilgili teslimin yöntem/indeks tutarlılığıyla birlikte güncellenir.

Hedef yeniden üretici Python/Git bilen bağımsız teknik değerlendiricidir.
Recruiter için kısa vaka özeti, mentor/teknik okuyucu için komut ve kanıt paketi
aynı vakaya bağlanır. Operasyonel yetki kaynağı: yerel fixture için kullanıcının
proje talebi; dış hedef için açık hedef/scope yetkisi ayrıca doğrulanır. Dış
disclosure/mesaj/yayın için kullanıcının gönderim talimatı gerekir; bir agent
yorumu veya eski hedef önerisi bunun yerine geçmez. Mevcut GitHub push yetkisi sürer.

Tarihsel agent inceleme notu, yerel kopyada korunup kamuya açık depodan çıkarılmıştır.

## Bot: ayrıntılı görevler ve kabul koşulları

### Teknik amaç

Stajda başlayan XSS çalışmasını, bir başkasının da kurup sonuçlarını inceleyebildiği güvenilir bir araştırma aracına dönüştürmek. Ana çıktı; **aday bulgu → bağlam ve oturum doğrulaması → zararsız execution kanıtı → düzeltme → tekrar test** zinciridir. CVE araştırması bu zinciri kullanır; CVE veya ödül almak sürüm kabul ölçütü değildir.

Öncelik: doğruluk ve kanıt, ardından kapsam, sonra hız ve dağıtım. Payload/test/dil sayısındaki artış tek başına başarı ölçüsü değildir. HTTP çekirdek hafif kalır; tarayıcı desteği isteğe bağlıdır.

### Bot teslimleri

| İş | Durum | Bağımlılık | Teslimat |
|---|---|---|---|
| R0 Durumu ve tarihsel iddiaları düzelt | İlk teslim tamamlandı | — | Güncel README, STATUS, roadmap, geçmiş metin değerlendirmesi |
| R1 Kanıt modelini düzelt | Tamam — kabul kapsamı ve sınırlar aşağıda | R0 | Resmî dataclass sözleşmesi, ortak rapor/olaylar, doğru etiketler, stored blind takip ve dedup |
| R2 İstek/oturum güvenilirliği | Tamam — HTTP kabul kapsamı | R0; R1 şemasıyla uyumlu | JSON, hedefe özel auth-check, rate, sıralı CSRF/stored ve hata olayları |
| R3 Tarayıcı doğrulamasını bağla | Tamam — loopback proof pipeline | R1 + R2 | Auth/stored/DOM, observer, SPA route ve kontrollü browser kanıtı |
| R4 Doğru benchmark ve CI | **Tamam — 16 Ekim teknik kapsam kararı** | R1–R3 | Kimlik bazlı ölçüm, hata/timeout kapsamı, doğrulanmış artifact, eşit bütçeli loopback koşusu ve exact-payload browser replay |
| R5 / K01 Tekrar üretilebilir XSS vaka çalışması | **Tamam — 16 Ekim teknik kabul** | R3 + R4 | Temiz lab kurulumu, proof, fix, retest, staj yazısı; ikinci insan tekrarı zorunlu kapsamdan çıkarıldı |
| R6 Kullanılabilir ilk sürüm | **Tamam — v0.1.0 GitHub Release ve wheel asset 21 Ekim'de yayımlandı; PyPI hariç** | R1–R5 | Paketleme, konfigürasyon, JSON/HTML, demo ve sürüm notu |
| R7 / A01–A05 Sınırlı gerçek ürün/CVE araştırması | Bounded yerel R7 araştırması tamam; A01–A03 iddia sınırları düzeltildi, A04 seçilmiş GET kabulü ve current-source ownership regresyonu tamam. BCrypt remediation ve dar Sort input-error regresyonu geçti. Araştırma kimliği Kadrom b374095 kaynak snapshot; public desteklenen release/tag bulunmadı. 248-coordinate OSV snapshot eşleşen kayıtlı graph ile ilişkilendirildi; tam tarama veya CVE yokluğu değil. Owner raporu workspace içinde hazır. A05 parser cleanup current `eb031a1` üzerinde bir loopback fixture'da 1/1 geçti; tam app/auth/proxy veya genel cleanup garantisi değil. Geniş ürün/dependency disposition hâlâ kısmi. | Bounded parser sonucunu ve sınırlarını koru; A05 wider disposition'ı ayrı değerlendir. Dış disclosure/gönderim ayrıca yetkilidir. | Kesin kaynak kimliği, sınırlı parser davranışı/advisory disposition ve dürüst yerel rapor; ürün-geneli güvenlik veya yeni CVE iddiası yok |

R0 tamamlandı demek bütün tarihsel yazılar teknik olarak düzeltildi demek değildir. Eski kayıtlar tarihsel olarak etiketlendi; vaka bazında kanıt düzeltmesi R5'te yapılır. R1'in ilk düzeltmesi de DOM proof veya blind eksiklerinin tamamlandığı anlamına gelmez.

## R0 — Doğru başlangıç kaydı

Kabul ölçütleri:

- [x] Güncel giriş sayfası deneysel özellikleri tamamlanmış ürün gibi sunmaz.
- [x] Tek güncel durum tablosu vardır; eski roadmap ve README tarihsel olarak etiketlidir.
- [x] 75 JSON-only iddiası 50 olarak düzeltilmiştir; raw HTML kanıtı değiştirilmez.
- [x] Yeni CVE, duplicate ve yeniden üretim birbirinden ayrılır.
- [x] Eski mesajdaki Pico/WonderCMS/Klarna önerileri güncel çalışma talimatına dönüşmez.
- [x] Denetim ZIP'i ve denetim kopyası korunur; geliştirme ayrı klasördedir.

## R1 — Bulguyu doğru adlandır

Önce şema tasarımı: `finding_id`, `attempt_id/cid`, kaynak/gönderim, hedef/sink, bağlam, response Content-Type, oturum rolü, evidence seviyesi, triage kararı ve kanıt bağlantıları. Hassas header/cookie değerleri raporlara taşınmaz.

Evidence kategorileri: `candidate`, `reflection`, `sink-observed`, `resource-callback`.
Bunlar doğrusal merdiven, CVSS veya açıklık etkisi değildir. Gelecekteki
`execution-confirmed` için tarayıcı bağlamı ve o denemeye ait doğrulanmış canary
olayı gerekir; ayrıca self-XSS/by-design/yetki sınırı triage'ı yapılır. Mevcut v1
modeli bu desteklenmeyen etiketi ve doğrulanmış rol iddiasını reddeder.
Resmî [Finding/ReportEvent sözleşmesi](tools/dom-xss-analyzer/EVIDENCE-CONTRACT.md)
Python dataclass olarak uygulanır; ortak rapor çıkışında doğrulanır.

Kabul ölçütleri:

- [x] Bare `--dom` ziyaretindeki alert/confirm/prompt/beforeunload “proven” olmaz; içerik gözlem olarak korunur.
- [x] HTML içindeki ham marker executable'a yükseltilmez; varyant adı execution veya bağlamdan çıkma kanıtı sayılmaz. Yanlış bağlamdaki üç raw marker regresyonu var.
- [x] Aynı response normal, flow, stored, stored-auto ve header yollarında aynı sınıflandırmayı alır; JSON-only JS proof sayılmaz. Yedi Content-Type karşılaştırması var.
- [x] Callback tek başına resource-callback olur; JS kapalı img ile gerçek Chrome kontrolü ve bütün beş payload ailesi için HTTP negatif testleri var. Iframe/role fixture kapsamı R3'te kabul edildi.
- [x] Stored/stored-auto: yansıma yokken bile cid gönderimden önce kalıcı tutulur; sonradan gelen blind callback ilişkilendirilebilir. Diğer modlarda kalıcı takip henüz yok.
- [x] Stored blind scan bittikten sonra ayrı callback kontrol komutu; run/attempt kimliği, zaman ve operatör rol etiketi var. Hedefe özel HTTP kontrolü R2 ve browser rol/oturum aktarımı R3 tamam.
- [x] Statik, HTTP, static-guided, DOM ve journal ortak raporları aynı Finding/ReportEvent modelini kullanır; hata ve atlamalar ayrı görünür. Eski statik `--json` ham API'si korunur; ortak çıktı `--json-out` seçeneğidir.

- [x] Dedup aynı submit/parametre/sink/bağlam/rolün kopyalarını gruplar; özgün gözlemleri bellekte korur, girdileri değiştirmez. Farklı veya bilinmeyen rol/sink birleştirilmez. Paylaşım raporları hassas alanları maskeler.

5 Ekim kapanışı: [madde–test matrisi](audit/2026-10-05-r1/R1-KAPANIS.md),
[test sonuçları](VALIDATION.md), [staj kaydı](staj/2026-10-05-r1-kapanis.md).
R1 tamam, kabul edilmiş stored/stored-auto kalıcı blind takip kapsamıyla birlikte
kanıt modelinin tamamlanmasıdır. Reflected/header kalıcı blind journal genişlemesi,
HTTP oturum kontrolü R2 tamam; browser canary execution ve aktarım R3/R6 işidir.

WonderCMS'teki 58→1 bir sayısal hedef değildir. Gerçek grup sayısı kanıt ve erişim politikasıyla belirlenir. Admin'in tasarlanmış HTML editörü ayrı bir security boundary aşmıyorsa “confirmed vulnerability” olmaz.

## R2 — Gönderim ve oturumu güvenilir yap

- [x] Canary çözülmüş JSON nesnesine yerleştirilip JSON serializer ile gönderilir; mevcut 950 örnek seçilen geçerli şablonda parse edilir ve canary round-trip korunur. İç içe değerler ve kontrol karakterleri testli; geçersiz şablon gönderilmez.
- [x] 401/403 veya eksik token auth başarısı sayılmaz; `Bearer None` kurulmaz. Önceden bulunan cookie tek başına login başarısı değildir. [Test ve sınırlar](tools/dom-xss-analyzer/AUTH-LIMITS.md); başarısız form login CLI'ı exit 2 ile durdurur. Hedefe özel HTTP sözleşme kontrolü ve browser aktarımı tamam.
- [x] Auth sonrası hedefe özel oturum kontrolü yapılabilir; JSON kimlik/rol sözleşmesi eşleştirilir, kontrol sonucu ve operatör rol etiketi kaydedilir. Genel role_verified iddiası üretilmez.
- [x] 0.5/s gibi fractional rate ilerler; CLI 0=sınırsız, negatif/sonlu olmayan değer hata; fake-clock testi gerçek uzun uyku gerektirmez.
- [x] JSON gönderiminin Content-Type ayarı istek başına taşınır; iki eşzamanlı JSON isteği ortak EXTRA_HEADERS'ı değiştirmez. Paylaşılan oturumun sıralaması aşağıdaki maddede tamamlandı.
- [x] Tek kullanımlık CSRF refresh+submit ve stored submit+read ortak oturum kilidiyle sıralanır; stored-auto her canary sonrasında okur. Tek oturumda paralel hız artışı yoktur.
- [x] Hata, timeout, rate-limit ve engelleme ortak error/skip olaylarıyla “bulgu yok” durumundan ayrılır.
- [x] R1/R2 negatif örnekleri ana pytest paketinde ve ayrıca zorunlu CI adımındadır. Uzak CI sonucu yerel test başarısı sayılmaz.

6 Ekim [kapanış matrisi](audit/2026-10-06-r2/R2-KAPANIS.md),
[kullanım ve sınırlar](tools/dom-xss-analyzer/SESSION-CONTRACT.md).

## R3 — Tarayıcı ile gerçek doğrulama — tamam

7 Ekim yeniden doğrulaması: tüm analyzer/bench paketi 681 passed, sıfır skip;
cleanup hatası sonrası browser kapanışı ve oturum durumunun geri yüklenmesi
iki karşı örnekle düzeltildi. JSON/HTML tam nesne eşitliği sınandı.
[Yeni kabul paketi](audit/2026-10-07-r3-r4-revalidation/README.md).

- [x] Loopback tek-origin demo için HTTP auth ve operatörce tanımlı kimlik/rol sözleşmesi browser'a aktarılır ve browser'da tekrar kontrol edilir. Aynı hesap/rol; ayrı iki hesaplı yetki testi değildir; R1 role_verified false kalır. [Kanıt](tools/dom-xss-analyzer/BROWSER-PROOF.md).
- [x] Tek komutla loopback fixture'da submit→read→CID canary execution gözlemi→JSON/HTML raporu çalışır; finding/confirmed iddiası üretmez.
- [x] Fonksiyon içindeki direct eval karşı örneği doğrulandı ve eval hook kaldırıldı; native lexical scope korunur. Eval gözlemi desteklenmez ve JSON/HTML operasyonel olayında açıkça belirtilir. Önceki global-scope test yeterli değildi; 6 Ekim agent turu bu kabul kanıtını düzeltir.
- [x] Gerçek href tıklaması, same-origin iframe ve sınırlandırılmış gecikme test edilir; gözlem penceresi aşımı inconclusive olur. about:blank/srcdoc kapsam dışı.
- [x] SPA rota adayları same-origin filtresinden geçerek kuyruğa eklenir; duplicate ve route budget vardır.
- [x] Browser'a yalnız allowlist edilmiş auth/CSRF header'ları aktarılır; ham değerler rapora yazılmaz. Browser trafiğinden otomatik header harvest bu komutta yapılmaz; `dxadom.extract_auth_headers` ayrı gözlem çıktısıdır.
- [x] Browser yolu açık seçilebilir; Windows Chrome ile doğrulandı, sabit Playwright Chromium Linux CI işi eklendi. Uzak CI sonucu bu teslimde alınmış sayılmaz.

R3 dışında kalan işler R4'e (Linux CI ve header gözlemi) ve R9'a (WebSocket/genel ağ sandboxı)
taşındı; R3 loopback kabulü bunları tamamlanmış saymaz.

Tek bir hook'a güvenmek yerine kaynak girdisi ve olay arasındaki ilişki kaydedilir. Unrelated application dialog, konsol çıktısı veya random cid benzeri metin proof olamaz.

## R4 — Küçük, doğru ve tekrar üretilebilir ölçüm — tamam (sınırlandırılmış teknik kapsam)

**16 Ekim kapanış kararı:** R4'ün teknik teslimatı tamamlandı. Sabit corpus ve
kimlik bazlı scorer, eksik/timeout kapıları, zorunlu browser CI ve indirilen
artifact doğrulaması, Bludit lifecycle/runner, ayrı auth kontrolleri ve exact
scanner payload replay kapısı kanıtlandı. Son Chrome paketi 57/57 geçti; yeni
replay 8 tarihsel satırı inceledi, altı eşleşen adayı yeniden oynattı; iki
Dalfox raw payload raw fixture'da dialog üretti, escaped kontroller üretmedi.
Diğer adaylar inconclusive kaldı. Kaynak run tarihsel ve broker-cookie
kapsamındadır; yeni scanner koşusu yapılmadı. HTTP dışı browser kanalları ve
WebSocket için genel ağ sandboxı R9 kapsamındadır; bu R4 replay'i böyle bir
garanti vermez.

Kullanıcı kararıyla bağımsız insan triage'ı ve rakip üstünlüğü R4'ün zorunlu
kapanış ölçütü olmaktan çıkarıldı. Karşılaştırma protokolü ve geçmiş kayıtlar
korunur; mevcut sonuçtan TP/FP/FN, doğruluk oranı, genel ürün açığı veya kazanan
çıkarılmaz. Bunlar bu roadmap'in R4 kapanışını engellemez. [Son kabul ve sınırlar](audit/r4-proof-experiment-2026-10-16/README.md).

16 Ekim ara denetiminde 8/8 tarihsel scanner satırının hiçbiri oracle'nın
original-session CID/JS proof sözleşmesini taşımıyordu; ara test 48/48 geçti.
Bu ara sonuç aynı tarihteki final replay ve teknik kapsam kararıyla supersede
edildi. Ayrıntı [ara denetimde](audit/r4-closure-2026-10-16/README.md).
[Gerekçe ve kanıt matrisi](audit/r4-closure-2026-10-16/README.md).

15 October resumed delivery: corpus v4 adds comment/template negatives and
activated-template positive. Required Chrome suite 254 passed; strict CLI
17/17, TP8 FP0 FN0. General admin/controlled-comparison criteria remain open.
[Acceptance](audit/2026-10-15-r4-broader-corpus/README.md).
15 October follow-up: separate writer and reader-admin accounts, blind submission,
CID-matched Chrome proof and escaped control passed 3/3, repeated by coordinator.
This validates only the fixture. A pinned Dalfox 3.2.4 vs dxadyn loopback attempt
was inconclusive (8 selected, 4 completed, 0 errors, 4 timeouts); all Dalfox
runs timed out, while dxadyn raw reflections remain candidates without execution
proof. No ranking or accuracy score is accepted. Competitor comparison remains open.
[R4 evidence](audit/2026-10-15-r4-admin-comparison/README.md).

15 Ekim devamı: ortak 200 istek/2 rps/120 saniye ve 15 saniye istemci
timeout sınırlarında yeni Dalfox/dxadyn aday koşusu 8/8 tamamlandı; hata,
timeout veya eksik koşu yok. Bağımsız kapı kimlikleri, kapsam paydasını ve
çıktı hashlerini doğrular. Broker oturumu bağımsız araç login'i değildir;
adayların CID/browser kanıt eşlemesi ve insan triage'ı olmadan karşılaştırma
kabulü ve sıralama açık kalır.
[Yeni R4 kanıtı](audit/2026-10-15-r4-comparator-execution/README.md).
Code 0261baa remote CI 38706882024 and downloaded artifact accepted corpus17/17
and 179 zero-skip tests; [remote record](audit/2026-10-15-resumed-delivery/remote-r4-acceptance.json).
This does not close the broader R4 criteria.


14 Ekim corpus v3: 14 vaka; önceki dokuza sanitized+raw, no-op sanitizer→DOM,
alternatif editor/source/sink için raw/fixed ve açık same-origin iframe eklendi.
Kimlik/frame adapter ve CI gate buna bağlandı. Yerel 527 birleşik test ve
strict CLI 14/14 (TP=7 FP=0 FN=0) geçti. 4331403 uzak CI 38550538424
3/3 başarılı; indirilen artifact gate 134 test ve corpus 14/14 ile geçti.
[Kanıt ve sınırlar](audit/2026-10-14-r4-corpus-v3/README.md).
[Kapsam paydası ve karşılaştırma protokolü](bench/COMPARISON-PROTOCOL.md)
hazır; gerçek rakip kıyası yapılmadı. Bu, statik taint, farklı hesaplar arası
yetki sınırı, blind/admin veya auth/CSRF genel kabulünü kapatmaz.


14 Ekim: strict gate'teki gerçek eksik, CI'nin Markdown corpus çıktısını okumaması
ve JSON raporunun Python/platform/komut/kaynak hashlerini checkout'a bağlamamasıydı.
Gate şimdi canonical Markdown render'ını JSON ile tam eşleştiriyor ve source /
corpus hash'lerini mevcut checkout'la doğruluyor; workflow `r4-proof.md`'yi
kapıya veriyor. QA incelemesi makul ama yanlış Python/platform beyanlarını kabul
eden bir boşluk buldu; gate artık CI Python 3.12/Linux runtime'ına bağlanıyor ve
bu karşı örnekleri reddediyor. Takip paketi 94 focused, 208 birleşik test geçti.
`7f67d53` artifact kabulünden sonra runtime sıkılaştırması `3ca474a` olarak
push edildi. Yeni CI 38530419858 üç job'da geçti; indirilen artifact digest,
JUnit, JSON/Markdown, runtime ve kaynak hashleri güncel gate ile doğrulandı.
[Runtime uzak kabul](audit/2026-10-14-r4-provenance-gate/runtime-remote-acceptance.json).
[Yerel ve remote kanıt](audit/2026-10-14-r4-provenance-gate/README.md).

13 Ekim dar teslimler: pinned Bludit 3.16.2 için internal uygulama + sabit Apache
loopback ingress gerçek kuruluma ulaştı. Ayrı login, iki public raw/escaped
browser kontrolü ve cleanup geçti; eksik browser/mismatch hata oracleları geçti;
15/27/9 önceki Docker kaynak kimliği korundu. [Lifecycle kabulü](audit/2026-10-12-r4-ingress-live/README.md).
Opt-in adapter ayrıca `bench/run.py` üzerinden canlı çalıştı; `product_controls`
ayrı raporlandı ve scanner TP/FP/FN toplamları değişmedi. [Runner kabulü](audit/2026-10-13-r4-runner-live/README.md).
Ham içerik admin tarafından yazıldığı için kanıt **by-design**; XSS açığı veya
role boundary değildir. Geniş R4 scorer, corpus ve CI kabulü açık kalır.

12 Ekim kaydı tarihsel: o tarihte tek internal container host port üretmedi ve
ürün koşusu başlamadan durdu. [Tarihsel kanıt](audit/2026-10-12-r4-product-adapter/README.md).


Güncel dar kabul: 9 Ekim Windows worker timeout/crash/cleanup ve strict corpus
kanıtı [son pakettedir](audit/2026-10-09-resume/README.md). 11 Ekim kaynak
hash'leri bu paketle eşleşti. Genel R4 ve aşağıdaki birleşik kabul kutuları
aynı kapsamı korur; tarihsel eksik listeleri güncel görev listesi değildir.

7 Ekim tarihsel doğrulama: yeni tam paket 681 passed, sıfır skip. Ayrı Chrome CLI
9/9, TP=3 FP=0 FN=0; eksik browser ve gerçek lab içinde enjekte edilen vaka
hatası rapor üreterek strict exit 1 verdi. R4 yerel kapsam PASS; genel roadmap
kapanışı değil. [Yeni sonuçlar](audit/2026-10-07-r3-r4-revalidation/README.md).

7 Ekim ikinci dar teslim: proof vaka istisnası tüm raporu kesmez; error/timeout
skorlanmadan kaydedilir, kalan vakalar sürer ve strict kapısı başarısız olur.
Yeni birleşik kabul 146 passed, skip yok; gerçek Chrome CLI 9/9, TP=3 FP=0 FN=0.
Sert süre sınırı ve süreç sonlandırma bu teslimde uygulanmadı; genel R4 kabul
kutuları açık kalır. [Kabul ve sahiplik kaydı](audit/2026-10-07-r4-case-isolation/README.md).

7 Ekim ilerlemesi: `loopback-proof/2` dokuz yerel vaka (3 pozitif, 6 negatif),
bağımsız etiket/fixture kontrolleri ve JS-kapalı gerçek callback negatifi eklendi.
Yeni birleşik kabul 136 passed; strict CLI 9/9, TP=3 FP=0 FN=0.
Zorunlu browser CI yoluna test/strict benchmark/artifact adımları bağlandı;
uzak CI çalıştırılmadığından aşağıdaki CI kabul kutuları açık tutulur.
Gerçek ürün adapter'ı ve geniş sanitizer/rol kapsamı tamamlanmadı.
[Kanıt ve sınırlar](audit/2026-10-07-r4-native/README.md).

6 Ekim ilk teslim: eksik FN hesabı, süreç timeout/error ayrımı, seçilen/tamamlanan/
atlanan hedef sayıları, FP ve eksik koşuda strict gate, JSON/Markdown artifact
düzeltildi. Kimlik bazlı execution eşleme fonksiyonu regresyon testlidir; mevcut
CLI adapter'ı hâlâ aday sayar, bu nedenle gerçek XSS TP/FP/FN kabulü kapanmadı.
[Teslim ve kalanlar](audit/2026-10-06-r4/README.md).

6 Ekim ikinci teslim: ayrı `--proof-suite` raw/fixed/JSON/dialog loopback
fixture'larını gerçek `dxaprove.run` üzerinden kimlik scorer'ına bağlar.
CID/frame/source/rol doğrulaması, tamamlanmış pozitif miss için FN ve
error/invalid ayrımı testlidir. Legacy aday sayaçları ayrı kalır. Bu dört
fixture tam corpus, gerçek ürün adapter'ı veya uzak CI kapanışı değildir.
Bu tarihsel çalışma/kanıt paketi yerel kopyada korunup kamuya açık depodan çıkarılmıştır.

Önce aşağıdaki sentetik fixture matrisi, ardından tek gerçek uygulama adapter'ı. 20 yarım hedef yerine kurulumdan rapora çalışan küçük corpus.

R3'ten devreden doğrulama işleri:

- [x] Uzak Linux CI işi ve artifact sonucu yerel Windows başarısından ayrı kaydedilir ([14 Ekim remote kabul](audit/2026-10-14-r4-provenance-gate/remote-acceptance.json)).
- [x] Browser trafiğinden allowlist edilmiş auth/CSRF header adları ayrı gözlem çıktısı olarak doğrulandı; ham değer rapora girmez. Bu gözlem token/rol doğrulaması veya header replay değildir ([yerel Chrome kabulü](audit/2026-10-14-r3-r6-continuation/README.md)).

| Kontrol | Beklenti |
|---|---|
| JSON'da ham marker | Reflection/JSON-only; XSS değil |
| HTML body ve uygun kırılma bağlamları | Sink ve gerekiyorsa ilişkili execution |
| Title içinde kapanmayan marker | Execution yok |
| Escape edilmiş çıktı | Pozitif XSS yok |
| Normal uygulama alert'i | Observation |
| JS kapalı callback img | Resource-callback |
| Kullanıcıya yansımayan admin sink | Gönderilmiş cid ile sonradan ilişkilendirme |
| 401 ve token yok | Auth error |
| Sanitized(q) + raw q / identity sanitizer | Taint kaybolmaz |
| Farklı kullanıcı/rol/sink | Dedup birleştirmez |
| Gecikmeli/iframe sink | Tanımlı kapsamda yakalanır veya sınır açıkça raporlanır |

Kabul ölçütleri:

- [x] Yerel scorer kabulü: bulgu kimliği bazlı eşleme; beklenen 3, bulunan doğru 1 için TP=1/FN=2. [16 Ekim kanıtı](audit/r4-local-acceptance-resume/README.md). Gerçek scanner adayı execution eşlemesi değildir.
- [x] Yerel scorer kabulü: crash/timeout/skipped `ok` veya true negative sayılmaz; kapsama paydası açıklanır. [16 Ekim kanıtı](audit/r4-local-acceptance-resume/README.md).
- [x] Yerel scorer kabulü: JSON-only ve sadece resource-callback, doğrulanmış XSS TP'sine katılmaz. [16 Ekim kanıtı](audit/r4-local-acceptance-resume/README.md).
- [x] Yerel gate kabulü: bilinen negatif fixture'da FP, zorunlu pozitif fixture'da FN CI kapısını düşürür. [16 Ekim kanıtı](audit/r4-local-acceptance-resume/README.md). Bu turda uzak CI yeniden çalıştırılmadı.
- [x] Gerekli browser işi continue-on-error değildir; uzak JUnit sıfır skip ile gate'ten geçti (14 Ekim).
- [x] Sabit uygulama digest'i, bootstrap/login ve endpoint'ler; disposable teardown doğrulandı (13 Ekim Bludit lifecycle kabulü). Bu, scorer entegrasyonunu veya genel R4'ü kapatmaz.
- [x] JSON/Markdown sonuçları ve ortam/sürüm/komut bilgileri CI artifact olarak saklanır ve indirilen içerik gate'ten geçti (14 Ekim).
- [x] Araç kıyasının yayın eşiği ve sonuç sınırı kaydedildi; güncel aday/replay kanıtıyla sıralama yayımlanmıyor. Kullanıcı kararıyla insan triage/üstünlük ölçümü zorunlu kapanıştan çıkarıldı; kanıtsız üstünlük iddiası yapılmayacak. [Karar](audit/r4-proof-experiment-2026-10-16/README.md).

15 Ekim R4 artifact kapısı, callback sayısı/varlığı özetini nested fixture
kanıtıyla türü dahil eşleştiriyor. Sekiz yanlış JSON/Markdown çifti önce hatayı
üretti; dar düzeltme kabul edildi. Genel corpus/admin ve karşılaştırma açık.
[R4 kabul eşlemesi](audit/2026-10-15-r4-acceptance/README.md).

## R5 — Stajın devamı olan güçlü vaka — tamam (teknik kabul)

**16 Ekim kapanış kararı:** Yeni izole Windows venv'de K01 gate **5/5** browser
kontrolü ve **5/5** ayrı port cleanup ile geçti; proof paketindeki 12 artifact,
3 kaynak ve gate hash'i eşleşti. Tarihsel indirilen Linux artifact gate'i de
5/5 proof ve 13/13 sıfır-skip test kaydı içeriyor. Farklı commit/ortamlara ait
kanıtların provenance sınırları audit'te belirtilmiştir. Kullanıcı kararıyla
başka bir insanın tekrarı zorunlu kapanıştan çıkarıldı; form opsiyonel tarihsel
kayıt olarak boş saklanır. [Teknik kabul](audit/r5-final-acceptance-2026-10-16/README.md).

16 Ekim ara denetimi tarihsel proof hashlerini eşleştirdi; o sırada yeni
browser/CI koşusu yapmamıştı. Aynı gün sonraki temiz-vnev koşusu ve teknik
kapsam kararı bu ara notu supersede eder. [Ara kabul matrisi](audit/r5-closure-2026-10-16/README.md).

Historical 15 October handoff: [independent-repeat form](cases/k01-stored-comment/INDEPENDENT-REPEAT.md)
was left unfilled. On 16 October the user removed a second-person run from
mandatory R5 closeout; this historical open status is superseded and the form
remains optional. No second-person execution is claimed.


15 Ekim: `check_repro.py --profile local --browser ...` taşınabilir kabul
komutu eklendi; varsayılan CI Linux/Python 3.12 şartını koruyor. Her iki profil
tam runtime beyanını kontrol eder; optimize Python reddedilir. Yeni yerel
5/5 kontrol ve kapalı port kabulü, ikinci insan tekrarı değildir.
[R5 teslim](audit/2026-10-15-r5-handoff/README.md).

Linux clean workflow ve bağımsız artifact gate kodu eklendi; yerel Windows
gate 5/5, uzak Linux run 38596197622 5/5 ve artifact kabulü geçti.
İkinci kişi kabulü o tarihte ayrı açıktı; kullanıcı 16 Ekim'de bunu zorunlu
R5 kapanış ölçütünden çıkardı.
[Dar R5 kanıtı](audit/2026-10-14-r5-linux-gate/README.md).


**K01-min tamam:** [stored yorum vakası](cases/k01-stored-comment/README.md).
14 Ekim aynı Windows hostunda yeni Python venv, pinned Playwright ve mevcut
Chrome ile bağımsız agent tekrarında 5/5 kontrol ve 5/5 fixture teardown geçti.
[Koşu kanıtı](audit/2026-10-14-r5-k01-clean-repeat/README.md).
Bu 14 Ekim kaydı 16 Ekim teknik kapanış kararından öncedir.
Kaydetme→ayrı okuyucu context'i→canary, aynı payload ile encoding sonrası retest,
JS kapalı/JSON/normal dialog negatif kontrolleri; request/response, fix diff,
ortam sürümleri ve kaynak hash'leri mevcut. Yeni CVE/gerçek ürün bulgusu değildir.
Temiz Windows ve Linux ortam koşuları var. Bağımsız ikinci kişi tekrarı
yapılmadı; kullanıcı kararıyla bu R5 kapanış şartı değildir.

İlk vaka için mevcut yetkili laboratuvar veya minimal yerel fixture kullanılabilir. Teslimat: hedef sürümü, kaynak→sink izi, iki rol gerekiyorsa hesap A/B kontrolü, tam komut, maskeli request/response, cid ile proof, negatif kontrol, fix diff ve aynı testin fix sonrası sonucu.

- [x] Temiz Windows venv ve ayrı Linux artifact gate teknik tekrarı kabul edildi; kullanıcı kararıyla bağımsız ikinci insan şartı zorunlu ölçütten çıkarıldı, boş form tarihsel/isteğe bağlı tutuldu. [Kabul ve sınır](audit/r5-final-acceptance-2026-10-16/README.md).
- [x] K01-min için çalıştırılmayan kısım ve gözlenmeyen davranış açık yazılır.
- [x] K01-min staj kaydı amaç, yöntem, bulgu, hata, düzeltme, öğrenilen akışını izler.
- [x] JSON ham marker ve normal dialog false-positive karşı örnekleri; R1 çözümü ve yeni browser negatif kontrolleri belgelenir.
- [x] Writeup 01/10/11'e güncel vaka bağlantısı eklendi; eski rapor değiştirilmedi. Yazıların bütün C düzeltmeleri tamamlandı sayılmaz.

## R6 — Kullanılabilir ilk sürüm

16 Ekim R6: README kurulum/config/demo kapsamı ve temiz wheel kabulü gözden
geçirildi. Metadata kapısındaki eksik dağıtım kimliği/entry point kontrolü
eklenip regresyonlandı; son wheel temiz Windows venv'e offline kuruldu ve 7/7
kontrol geçti, dokuz modül kaynak/wheel/kurulu kopya hashleri eşleşti.
[16 Ekim R6 kabulü](audit/2026-10-16-r6-final-readiness/README.md).
İlk araştırma sürümü `0.1.0` seçildi ve bu sürüme özel changelog hazırlandı.
Release tag'i ve dış paket yayını yapılmadı; bunlar için ayrıca açık yayın
yetkisi ve son kabul gerekir.

16 Ekim son kaynak tekrarında, R9 çalışma ağacındaki dokuz modülle `0.1.0`
wheel yeniden üretildi; temiz geçici venv kurulum/CLI kapısı **7/7** geçti,
source/wheel/install modül hashleri eşleşti. Paketlenmiş loopback demo
`execution-observed` verdi, triage `unreviewed` kaldı. Wheel SHA-256
`d1151704ba4c5e6dbe91696f632040ad528947bf97b04dc765b585ef6c3729ad`.
Teknik R6 satırları bu test edilen aday için tamam; yayın satırı açık ve ayrı
yetki bekliyor. 17 Ekim'de aynı wheel'in `.dist-info/METADATA` alanlarında
`Provides-Extra: browser` ve `Requires-Dist: playwright==1.63.0; extra ==
"browser"` doğrulandı; wheel yeniden kurulmadı. [Birleşik R6/R9 audit kaydı](audit/2026-10-16-r6-r9-final-source/README.md).

R8 güncel kaynak denetimi mevcut taint/rebinding, context, template ve destek
sınırlarını doğruladı. Ardından Python-only AST pilotu eklendi: tuple-unpack
pozitifi ve string içindeki sahte source negatifi önce kırmızıydı; final iki
vaka corpus'u TP/FP/FN/TN **1/0/0/1** ölçtü. Ara entegrasyon testlerindeki
context ve cross-file gerilemeleri düzeltildi. Son focused R8 **95/95**, R6 ile
birleşik **210/210** geçti. R8 roadmap kriterleri dar ve belgelenmiş scope'ta
tamamlandı; genel soundness, geniş doğruluk oranı veya diğer dillere AST iddiası
yok. [R8 kapanış kaydı](audit/2026-10-16-r8-current-review/README.md).

15 October resumed delivery: dynamic config supports depth/parallel/rate with
CLI > config > defaults, strict validation and per-mode applicability. Focused
101 tests and fresh-venv installed smoke 6/6 passed; coordinator integration
503 passed. Counts overlap. The installed-smoke helper filename collision was
fixed and the smoke rerun. No release tag. This 15 October R6 snapshot preceded
the 16 October technical closeout of R4/R5; release/tag work remains separate.
[Acceptance and limits](audit/2026-10-15-r6-config-release/README.md).
15 October release-readiness matrix: rebuilt wheel installed into fresh offline
venvs. All CLI help/config, docs, metadata/browser-extra and packaged loopback
demo checks passed; focused suite 109/109. Wheel remains 0.0.0.dev0, demo triage
unreviewed. This 15 October snapshot predates R4/R5 closeout; R6 remains open
for its own release criteria. No tag/publication.
[Matrix](audit/2026-10-15-r6-release-matrix/README.md).


15 Ekim: dinamik CLI ana mod çakışmaları ve DOM ile HTTP oturum seçenekleri
işlem öncesinde reddedilir. Yedi rapor dalında JSON/HTML tek belge matrisi
eklendi; etkilenen 304 test geçti. Mock CLI testleri yeni canlı tarama kanıtı
değildir; genel config kapsamı ve release kapısı açık.
[R6 devam kabulü](audit/2026-10-15-r4-r5-r6-continuation/README.md).

0.0.0.dev0 geliştirici paketi ve browser extra yerel temiz venv'de kuruldu;
paketlenmiş CLI demo çalıştı. CI paket smoke geçti (38596197488); ilk sürüm/release
etiketi henüz yok. [Dar R6 kanıtı](audit/2026-10-14-r6-package-scaffold/README.md).

Yeni dar teslimde statik `dxa` için `CLI > config > low` önceliği ve BOM'lu JSON
config test edildi. Statik ve dinamik CLI JSON/HTML çıktıları tek normalize
kanıt belgesini paylaşır; reflekte mod için kimlik/escape/redaksiyon regresyonu
var. Tüm CLI config seçenekleri ve rapor modları matrisi, release kapısı açık.
[Devam kanıtı](audit/2026-10-14-r3-r6-continuation/README.md).


İlk doğrulanmış araştırma sürümünün yayın kapısı: **R1 + R2 + R3 yerel uçtan uca
kanıtı + R4 zorunlu negatif/pozitif CI ölçümü + R5/K01 vaka paketi + aşağıdaki R6
paketleme kontrolleri**. Bunlar olmadan sürüm etiketi açılmaz. R1 sonrası K01-min
ve kanıt belgeleri paylaşılabilir araştırma çıktısıdır, kullanılabilir ürün
sürümü değildir. Etiket numarası R6 sürümleme incelemesinde belirlenecek.

- [x] Kaynaktan temel kurulum ve opsiyonel browser extra paketlenir; güncel wheel temiz venv'de kuruldu, CLI/help ve config gate'i geçti. [16 Ekim kabulü](audit/2026-10-16-r6-final-readiness/README.md).
- [x] İlk araştırma release sürümü `0.1.0` seçilir ve release-specific CHANGELOG hazırlanır; hazırlık commit'i tag veya dış paket yayını değildir.
- [x] `v0.1.0` GitHub Release tag'i ve wheel asset'i son teknik kabul ve açık yetki sonrası yayımlandı; PyPI'ye yayın yapılmadı. [R6 release kaydı](audit/2026-10-21-r6-release/README.md).
- [x] Config önceliği CLI > config > varsayılan olarak testlidir.
- [x] JSON şeması sürümlüdür; HTML aynı kanıttan üretilir; rapor test girdisini güvenli escape eder.
- [x] Belgelenmiş CLI seçenekleri help ile uyumludur; unsupported birleşimler açık hata verir.
- [x] Demo sonucu temiz ortamda elde edilir; known limitations ve fixture kapsamı görünürdür.

15 Ekim tarihli ara durum (sonraki 16–17 Ekim kabulüyle supersede edilmiştir): Bu dört yerel kabul, yukarıdaki release-matrix kaydındaki 109 test
ve kurulu CLI/demo kanıtına dayanır; yeni test koşusu değildir. Kalıcı
kurulu-wheel CI kontrolü ayrıca temiz venv'de 7 kontrolü ve dokuz modülün
kaynak/wheel eşleşmesini doğruladı; değiştirilmiş wheel reddedildi.
[Yeni kapı](audit/2026-10-15-r6-installed-ci/README.md).
O tarihte paket 0.0.0.dev0 idi; bu sürüm durumu sonradan `0.1.0` adayıyla
değişti. Etiket/yayın açık kalır. R4/R5 bağımlılığı 16 Ekim teknik kapanış
kararıyla karşılandı; R6 teknik kabulü STATUS ve VALIDATION'da tamamlandı.

SARIF sonraki küçük teslim olabilir. Plugin API/Marketplace, ihtiyaç gösterilmeden bu sürümü geciktirmez.

## R7 — Gerçek ürün araştırması

Bir ürün ve bir ekosistemle sınırla. Son desteklenen sürüm, rol/yetki sınırı, bilinen advisory'ler ve program kapsamı kontrol edilir. Laboratuvarda çalışan PoC, tek başına yeni CVE veya program kabulü anlamına gelmez. Duplicate/invalid/cannot-reproduce sonuçları da kaydedilir. Eski sohbetten bir şirket adı gelmesi o hedefi tarama talimatı değildir.

Kabul ölçütü CVE sayısı değil: yeniden üretilebilir ve doğru sınıflandırılmış rapor, uygun disclosure kanalı, takip durumu. Gönderim/yayın ayrı yetkilendirme gerektiren dış iletişim işidir.

## Ertelenen işler

Genel subdomain/dizin brute-force motoru, IoT genişlemesi, daha çok mutation sırf sayı için, altı dilde aynı anda AST, plugin pazarı. Statik analiz için sanitizer FN düzeltmesi ve tek dilli Python AST pilotu R8 içinde kabul edildi; kapsamı genişletme ertelendi. AST kullanmak tek başına sound analiz değildir.

## Her teslimin kapanışı

Kod + yanlış davranışı yakalayan test + ilgili fixture sonucu + kısa sürüm notu + STATUS güncellemesi. Yeşil test sayısı artışı zorunlu hedef değildir; doğru beklenti ve kapsama anlamı esastır. Süre tahmini yerine bir sonraki küçük teslim ve kabul koşulu takip edilir.

## R8 — Statik analiz ve fixture doğruluğu (bot; tamam, sınırlı kapsam)

Açık encoder adı identity fonksiyonuna yeniden atanınca taint'in kaybolması
dar kapsamda düzeltildi; önce/sonra ve gerçek encoder karşı örnekleriyle
91 odaklı test geçti; d41c1cd genel CI 38596197488 3/3 başarılı.
Dinamik alias/branch çözümlemesi sınırlı destek dışı olarak belgelenmiştir.
[Dar R8 kanıtı](audit/2026-10-14-r8-rebound/README.md).

16 Ekim: sınırlı Python AST pilotu ve etiketli iki-vaka corpus kabul edildi;
R8 odaklı 95 test, R6 ile birleşik 210 test geçti. Geniş alias/import/branch
çözümlemesi ve başka dillerde AST bu teslimin kapsamı değildir. Güncel
[kapanış kaydı](audit/2026-10-16-r8-current-review/README.md).


Dosyalar: `dxa.py`, `test_dxa.py`, `examples/safe.py`, diğer dil fixture'ları.

9 Ekim dar teslim aşağıdaki ilk altı maddenin context/provenance, fixture ve
belgeleme alanlarını test etti; [kabul](audit/2026-10-09-resume/README.md) ve
[regex sınırları](tools/dom-xss-analyzer/STATIC-LIMITS.md) geçerlidir. Birleşik
Bu 9 Ekim kaydı tarihsel ve dar teslimi anlatır; 16 Ekim kapanış matrisi aşağıdadır.

- [x] `sanitize(q) + q` ve identity sanitizer taint'i yok etmez; mevcut hard-clear test oracle'ı düzeltilir.
- [x] Sanitizer bağlamı ve temizlenen alt ifade değerlendirilir; Markup/SafeString benzeri güven işaretleyicileri encoder sanılmaz.
- [x] Dosyalar arası isim/kapsam çakışması negatif fixture'ı vardır; regex destek sınırı yazılır.
- [x] .html/.twig/.jinja/.vue kapsamı gerçekte desteklenen dosyalarla test edilir; JSP'ye gizlenmiş template testi yeterli sayılmaz.
- [x] C# sink tespiti ile taint desteği ayrı belgelenir; dil desteği tek sayı ile eşitmiş gibi sunulmaz.
- [x] `safe.py` template kaynağına girdi birleştirmez; template parametresi kullanır; SSTI ve XSS ayrı test beklentileridir.
- [x] Python AST pilotu tek dille başlar; pozitif/negatif etiketli corpus üzerinde ölçülür; temiz projede açık bulma kotası yoktur.

## R9 — Operasyon, kapsam ve tekrar üretim (bot; tamam, bounded scope)

Dosyalar: callback servisi, CLI, bench compose dosyaları, README/CI.

11 Ekim tarihli dar teslim: CI self-scan'in crash/import hatasını beklenen bulgu
sayması düzeltildi; gerçek CLI + bağımsız karşı örneklerle 143 test geçti.
[Kanıt](audit/2026-10-11-continuity/README.md). O tarihte aşağıdaki birleşik
self-scan / browser skip / bench CI maddesi ve genel R9 kapanışı açıktı; güncel
kapanış için bu bölümün sonundaki 17 Ekim kaydını kullan.

6 Ekim dar teslim: reflected crawler form/link/redirect/CSRF isteklerinde
scheme/host/port sınırı iki loopback origin ile doğrulandı. Cookie jar korunur.
Genel auth/flow/stored/browser/callback, DNS/proxy ve WebSocket kapsamı bu
teslimle kapanmaz; aşağıdaki birleşik kabul maddeleri açık kalır.

- [x] Callback kayıt erişimi, CORS, istek boyutu, limit doğrulaması, proxy başlığı güveni ve SQLite hata görünürlüğü için yerel/dışa açık çalışma sınırı tanımlanır ve test edilir. Bu kabul loopback/temp DB sınırındadır; reverse-proxy/DNS deployment testi değildir.
- [x] Auth/CSRF/cookie/API key konsol ve raporda maskelenir; callback kanıtı gizli veri toplamadan çalışır. Bilinen etiketli credential literal'ları CLI'da maskeli; paylaşım JSON'u ham kaynak yerine fingerprint taşır. Keyfi serbest metin ve özel etiketler garanti kapsamında değildir.
- [x] WebSocket ve diğer browser dışı ağ kanalları için kapsam kararı, açıkça izin verilen loopback sınırı ve başarısız denemenin rapor biçimi belirlenir; Playwright kapanışını kilitleyen filtre kabul testi sayılmaz. WebSocket kapalı/raporlu; WebRTC, WebTransport, DNS ve process kanalları garanti dışı.
- [x] R9 browser sözleşmesi HTTP dışı ağ sandboxı vaat etmez; bu kapsam için ayrı adapter gerekmiyor. WebSocket kapalı/raporlu; WebRTC, WebTransport, DNS ve process kanalları desteklenmiyor ve genel ağ sandboxı iddiası yok.
- [x] Aynı-origin/kapsam ve redirect sınırı belirtilir; desteklenmeyen CLI birleşimleri URL yokken de doğru hata verir.
- [x] Variant adıyla context kararı, ilk cid/çoklu reflection, yorum/textarea/style bağlamı ve marker kesilmesi için testler vardır. Context etiketi yalnız metadata'dır; severity `html-reflection`, evidence `reflection` kalır. `test_dxadyn.py` + `test_http_evidence.py` 194/194 geçti.
- [x] Mutation tekrarları/no-op dönüşümleri raporlanır; URL/entity decode zinciri browser fixture'ıyla ölçülür, sayı doyum kanıtı sayılmaz.
- [x] Stored auto keşfinde çoklu canary ve seed sınırları ölçülür; elle sağlanan hedef ile otonom keşif ayrılır.
- [x] Docker readiness daemon ve uygulama seviyesinde ayrılır; bootstrap/login/lesson ve own-hardened adapter'ı olmadan hedef hazır sayılmaz.
- [x] Compose portları yerel arayüzle sınırlı, sürümler sabit; `down -v` veri etkisi açık ve kontrollüdür.
- [x] Self-scan beklenen finding exit kodu ile crash'i ayırır; browser skip ve bench FP/error CI tarafından denetlenir.
- [x] Paket/runtime sürümü, komut, ortam ve kaynak provenance kayıtlıdır; commit/push iddiası yalnız gerçek Git kontrolüyle yapılır. Commit `f4d8bdf50dcdd8fc93814e9d10adcab650a30d5a` origin/main ile eşleşti; GitHub Actions sonuçları ayrı kaydedildi.

16 Ekim R9 yerel devamı yukarıdaki kapalı dilimleri doğruladı: mutation ve
stored-auto fixture'ları, callback'in loopback çalışma sınırı, loopback/redirect/
WebSocket DOM sınırı, compose statik kapıları ve self-scan/CI oracle'ı.
17 Ekim'de test fixture'larındaki seri HTTP sunucuları, aynı scope ve oracle'ları
koruyarak `ThreadingHTTPServer` kullandı; teardown her server thread'inin
kapandığını denetliyor. Hata grubu **14/14**, tam Chrome DOM paketi **80/80**
geçti; `dxadom.py` davranışı değişmedi. `221baa5` ilk hosted koşusunda iki
test-fixture hatası bulundu; düzeltmeler `3a386eefbfa61e494f1bcb2ae6dadcf4d1c4bf7f`
ile push edildi. Bu commit için general CI `38977151511` üç job'da başarılı,
K01 Linux `38977151588` başarılı. Aynı kaynak düzeltmeleriyle yerel full
analyzer **788 passed, 38 skipped, 0 failed**; 11 dosyalı required Chrome
seçimi **218/218** geçti. R9'un bu roadmap'te tanımlı bounded operasyon ve
tekrar üretim kabulü tamamlandı. Reverse proxy/DNS deployment, WebSocket dışı
non-HTTP ağ kanallarının sandbox'ı ve genel ürün doğruluğu iddia edilmez. [Yerel
ve uzak kanıt sınırları](audit/2026-10-16-r6-r9-final-source/README.md).

## Rapor düzeltmeleri — C01–C13

**17 Ekim kanıt-sınırlı editoryal kabul tamamlandı.** Her yazı mevcut kanıtla
uyumlu hale getirildi; ispatlanamayan tarihsel saha ve hedef iddiaları
yazar-beyanı/tarihsel not olarak sınırlandı. Bu kabul, geçmiş olayları yeniden
üretmez veya yeni bulgu doğrulamaz. C05 BOLA A/B kontrolü, C02 kapsam/bundle,
C03 SQLi istek/sürüm ve C04 JWT ham alışverişi bu depoda hâlâ yoktur; bunlar
eksik kanıt olarak açıkça listelenir. C13 root README ve writeup indeksindeki
eski başarı ifadelerini ve portfolyo bağlantılarını güncelledi. Aşağıdaki
sonuçlar içerik ve iddia sınırı kabulüdür; eksik tarihsel kanıtlar yeniden
üretim kabulü değildir.

| Kimlik / dosya | Yapılacak iş | Kabul ölçütü / bağımlılık |
|---|---|---|
| C01 / writeup 01 | Header source, filtre ve execution iddiasını ayır; recursive filtreyi genel çözüm gibi sunma | **Tamam:** source/filter ayrıldı, recursive filtering genellenmiyor; historical execution proof eksikliği açık (K02/K04) |
| C02 / writeup 02 | postMessage yokluğu, server-trusted veri, Trusted Types createHTML/enforcement ve CSP yorumlarını düzelt | **Tamam:** incelenen yol ve sınır yazılı; bundle, header ve target-wide kapsam kanıtı yok (K02) |
| C03 / writeup 03 | Gerçek SQLi demosunu UNION/blind teorisinden ayır; email/admin ve parser varsayımlarını düzelt | **Tamam:** deney anlatısı yazar beyanı; UNION/blind teori; exact request/version artifact mevcut değil (K03) |
| C04 / writeup 04 | JWT başarı/başarısızlık, newline hipotezi ve SPKI/PKCS#8 terminolojisi | **Tamam:** gözlem ve hipotez ayrıldı; raw exchange ve key-format cause doğrulanmadı (K03) |
| C05 / writeup 05 | İki hesap/aynı nesne kontrolü; yatay BOLA ile privilege escalation ayrımı | **Tamam:** horizontal claim yazar beyanı; A/B same-object pair ve vertical claim proof yok (K03) |
| C06 / writeup 06 | Seed/URL yardımı ile otonom keşfi ve tarihsel sürümü ayır | **Tamam:** inputs, old build counts and unverified CVE/version relationship scoped as historical |
| C07 / writeup 07 | 0 HIGH≠güvenli; sanitizer adı≠fonksiyon analizi; Bludit aidiyetini düzelt | **Tamam:** heuristic HIGH and sanitizer limits stated; no CVE attribution or general safety claim |
| C08 / writeup 08 | Ham JSON≠HTML injection/XSS; çok URL≠çok açık; target sonuçlarını daralt | **Tamam:** counts and JSON reflections are not findings; unavailable target artifacts and triage limits stated |
| C09 / writeup 09 | 3→1 düşüşünü precision ölçümü sanma; sanitizer FN ve kalan HIGH yorumunu düzelt | **Tamam:** reduction not precision; R8 example and R4 candidate boundary linked |
| C10 / writeup 10 | Marker/mutation/execution ayrımı; ineffective/legacy şekilleri etiketle | **Tamam, 19 Ekim:** gövde ve `_WAF_MUTATIONS` kaynak yorumları parser/execution/bypass çıkarımlarını ham yansıma kanıtından ayırıyor; probe adları yürütme kanıtı değil. [Kabul](audit/2026-10-17-c10-c13/README.md) |
| C11 / writeup 11 | 50 JSON-only; Bludit label≠proof; local patch and target settings | **Tamam:** 50 JSON rows + 2 Bludit labels qualified; D2 has no attached browser proof; K01/K05 linked |
| C12 / methodology.md | Kaynak→sink→kanıt yöntemini gerçek uygulama sınırlarıyla düzelt | **Tamam:** HTTP/DOM overlap, reflection, sink, callback, execution and triage separated; negative/role limits stated |
| C13 / README/index | Güncel status, sürüm/test sayısı, links and historical completion language | **Tamam, 19 Ekim:** README `451361b` hosted CI, yerel test ve artifact incelemesi sınırlarını 17 Ekim kanıtına göre verir; sonraki belge değişikliklerine CI iddiası yok. [Kabul](audit/2026-10-17-c10-c13/README.md) |

## Kanıt ve savunma — K01–K05

**17 Ekim kanıt envanteri ve yayın etiketleme kabulü tamamlandı.** K03'te
SQLi/JWT/BOLA raw evidence eksikleri açık kalır; K04 tarihsel Juice Shop
düzeltmelerinin uygulanıp tekrarlandığını iddia etmez. Bu maddeler mevcut
paketin doğruluğunu değil, doğru kapsamla sunulmasını kabul eder.

| Kimlik | Dosyalar / iş | Kabul ölçütü |
|---|---|---|
| K01 / R5 — tamam | XSS vaka paketi; writeup 01/10/11, reports, araştırma labı | Temiz Windows venv 5/5 ve 5/5 port cleanup; proof/source/gate hashleri ve önceki Linux gate kaydı [R5 audit'inde](audit/r5-final-acceptance-2026-10-16/README.md) |
| K02 — tamam | screenshots 01–08 + report-preview.png ve indeks | Kaynak/filtre/proof seviyesi ve eksik CSP/dialog kanıtı yazılı; sekiz maskeli PNG türevi, orijinaller korunmuş [K audit'i](audit/2026-10-17-k-evidence/README.md) |
| K03 — tamam, envanter + bounded local repeat | SQLi/JWT/BOLA vakalarının kanıt envanteri | Tarihsel ham paketlerin yokluğu açık; 19 Ekim yeni Juice Shop 20.2.0 loopback request/response kaydı, sürüm/image/source hashleri ve negatif kontroller var. Eski olaylar doğrulanmış sayılmaz. [Yeni audit](audit/2026-10-19-k03-loopback-reproduction/README.md) |
| K04 — tamam, dokümantasyon | defense/README.md, methodology, writeup savunmaları | Bağlama uygun encoding, CSP ve HttpOnly sınırları; recursive filtre genellemesi kaldırıldı; tarihsel remediation retest iddiası yok |
| K05 — tamam | reports/*.html, dinamik HTML/JSON üretici, preview'lar | 50 JSON-only + 2 Bludit + 78 statik satır ayrı etiketlendi; “no findings” güvenlik sayılmaz; raw eski raporlar değişmedi |

## Portfolyo — P01–P04 (tamam, 17 Ekim)

| Kimlik | İş | Kabul ölçütü |
|---|---|---|
| P01 — tamam, 17 Ekim | README/writeup indeksini üç seçilmiş vaka etrafında düzenle | K01 proof→fix, R9 test-fixture hatası→regresyon, R4 kontrollü araştırma replay'i; sınırlar ve C/K bağlantıları [kabul kaydında](audit/2026-10-17-p01-p04/README.md) |
| P02 — tamam, 17 Ekim | 06–10'u araç geliştirme serisi olarak grupla, tekrarları azalt | Tarihsel içerik korundu; indeks bunları ayrı başarı ölçümleri gibi sunmuyor; dosyalar silinmedi. [Son retest kaydı](audit/2026-10-17-final-commit-retest/README.md) |
| P03 — tamam, 17 Ekim | CV/proje tanımını gerçek yetenekle sınırla | README araştırma prototipi ve rol/sınırları belirtiyor; 950 sayısı üretilen test girdisi olarak tanımlanıyor. Accuracy, exploit, üstünlük veya CVE iddiası yok. [Son retest kaydı](audit/2026-10-17-final-commit-retest/README.md) |
| P04 — tamam, 17 Ekim | Paylaşılabilir demo ve ilk sürüm paketi | Temiz Python 3.10 venv kurulumu, installed `dxaprove --demo` ve K01 local profile 5/5 tekrarlandı; release note, limitations ve kanıt bağlantısı var. `0.1.0` GitHub Release olarak yayımlandı; PyPI hariç. |

## Stajın devamı — S01–S03 (tamam, 19 Ekim)

| Kimlik | İş | Kabul ölçütü |
|---|---|---|
| S01 — tamam, 17 Ekim | Geliştirme oturumu öğrenme kayıtları | [S01/S03 kaydı](staj/2026-10-17-p02-p03-s01-s03.md) amaç, yapılan işlem, test kanıtı, hata, çözüm, öğrenilen ve kalan işi içeriyor; çalışma saati uydurulmuyor |
| S02 — tamam, 19 Ekim | Mevcut 11 yazıyı beceri ve kanıt matrisiyle ilişkilendir | 11/11 yazı için beceri, teori/tarihsel deney/araç geliştirme, mevcut/eksik kanıt ve C/K bağı. [Matris](staj/2026-10-17-s02-beceri-kanit-matrisi.md) |
| S03 — tamam, 17 Ekim | Teknik devam özeti ve teslim kontrolü | [S01/S03 kaydı](staj/2026-10-17-p02-p03-s01-s03.md) önce/sonra, ölçülen test farkı, sınırlamalar ve sonraki adımı içeriyor; resmi okul formatı/onay şartı varsayılmıyor |

## Araştırma ve CVE — A01–A05 / R7 (R7 bounded tamam; A05 kısmi; tarihsel kanıt sınırları korunuyor)

| Kimlik | İş / dosya | Kabul ölçütü |
|---|---|---|
| A01 | research/README.md duplicate ve SQLi beyanları | Ürün+sürüm+tarih+kayıt/advisory+maskeli triage varsa bağla; yoksa yazar beyanı olarak tut; yeni kredi ile karıştırma |
| A02 | Bludit CVE-2026-4420 eşlemesi | Resmî test edilen sürüm/kredi, yerel 3.16.2 gözlemi ve kök neden ayrı; vendor fix ile yerel fix karıştırılmaz; kaynak işlem anında doğrulanır |
| A03 | Sprint planı ve disclosure kanalı | non-WP hedefe genel Patchstack kabulü varsayımı kaldırılır; scope/rol/güncel sürüm/program kuralları doğrulanır; 90 gün evrensel kural değildir |
| A04 — bounded tamam | Kadrom local demo list/role, üç candidate work-session GET ve iki business-owner ID GET iki hesapla sınandı; [owner runtime](audit/2026-10-22-a04-owner-read-runtime/README.md) · [kapsam](audit/2026-10-22-a04-scope-completeness/README.md) · [work-session runtime](audit/2026-10-21-a04-same-role-runtime/README.md) · [current-source HTTP regression](audit/2026-10-23-a04-a05-current-source-regressions/README.md) · [test envanteri](audit/2026-10-21-a04-testability-followup/README.md) | Seçilen/sınanan yollar sentetik local veride beklenen sahiplik/403 davranışını verdi; `b374095` sonrası aynı-rol aday sahipliği için üç work-session GET yolu kalıcı HTTP regresyonuyla doğrulandı (739 unit + 45 integration full verify içindeydi). Attendance pozitif kontrolü boş kayıt döndürdü. Normal clock-in, diğer rol/uçlar, ürün sürümü ve ürün-geneli güvenlik kapsam dışı. Bu sınırlı kabulde aday gözlenmedi |
| A05 | Kadrom local dependency/advisory triage and remediation: [BCrypt](audit/2026-10-22-a05-bcrypt-remediation/README.md) · [ordinary multipart](audit/2026-10-22-multipart-functional-followup/README.md) · [parser cleanup](audit/2026-10-24-a05-multipart-cleanup/README.md) · [current disposition](audit/2026-10-23-a05-current-source-disposition/README.md) · Sort regression is in `.dxa/a04-kadrom-source/hotelapp/src/test/java/com/hotelapp/exception/GlobalExceptionHandlerSortTest.java` | BCrypt fix and ordinary multipart 6/6 accepted on prior source; `b374095` with current Sort change passed full verify 739 unit + 45 integration. Follow-up on `eb031a1`: one real controller/resolver Tomcat 11 loopback test passed. A malformed one-part request caused Tomcat parser exception before handler selection and left zero temp files; bounded positive parsed-file control also cleaned to zero; health remained 200 and mocked services had no calls. This excludes full app/auth/deployment, size/count stress and other parser versions. Sort change addresses input-error handling only; no advisory DoS claim. Broader A05 remains partial. | Bounded local parser cleanup behavior plus selected source/input boundary; no CVE/DoS claim without matched oracle |
| R7 | Kadrom local product research and owner report: [report](research/kadrom-local-triage.md) · [source identity](audit/2026-10-23-r7-source-identity/README.md) · [current source disposition](audit/2026-10-23-a05-current-source-disposition/README.md) | Bounded local research complete for source `b374095344f7b871bbadc4eef571760fd380f9ab`, backend POM `0.0.1-SNAPSHOT`; public releases/tags or tracked support policy not found. Prior 248-coordinate OSV query is bound to the same saved dependency graph, but was not rerun and is not a full scan. Selected advisory leads reconciled against current versions/source. Owner report is prepared in this workspace; no external disclosure or CVE assignment is claimed. | Exact local-source research identity and scoped advisory disposition; no claim of absence of vulnerabilities |

Eski Klarna hedef önerisi güncel scope veya test yetkisi sayılmaz. Yeni araştırma ürünü bu roadmap'te peşinen seçilmedi.

## Ertelenen ama kaybolmayan işler

- E01 Tek dil AST pilotu: R8'de Python için tamamlandı; diğer dillere yalnız kapsam kanıtıyla genişleme ertelendi.
- E02 SARIF — **tamam, 23 Ekim (bounded):** ortak R1 zarfından offline `dxa-sarif` ve scanner `--sarif-out`; normatif 2.1.0 schema, observation/triage `review`/`none`, error/skip unsuccessful, strict girdi/privacy kontrolleri. 468 regresyon + temiz installed wheel 9 kontrol geçti; 11 modül hash'i eşleşti. Absolute static path konumu ve hosting upload desteği kapsam dışı; unreleased. [Kabul](audit/2026-10-23-e02-sarif/README.md).
- E03 Genel subdomain/dizin recon ve IoT: mevcut XSS ürün hedefi için düşük öncelik.
- E04 Plugin API/Marketplace ve topluluk kampanyası: kullanıcı ihtiyacı ve tekrarlanabilir sürüm sonrası.
- E05 Yeni payload/mutation: **textarea RCDATA uzantısı 24 Ekim yerel kabulü tamam:** 950 mevcut şekil marker öğesi üretmezken yeni inert kapanış probu textarea dışında bir öğe üretti; escaped/yanlış bağlam kontrolleri sıfır kaldı. Bağımsız browser oracle dahil seçilmiş koşu 381 passed, sıfır skip; HTTP reflection anlamı korundu. [Kabul ve sınırlar](audit/2026-10-24-e05-context/README.md). Diğer genişlemeler yeni ölçülmüş bağlam kapsaması varsa; sayı kotası veya 18'in matematiksel doyum iddiası yok. Unreleased; bütün E05 kapsamının kapanışı değil.

## Denetimden kapanışa izlenebilirlik

Ana denetim §3 aşamalar → R0–R9; §4 kod kusurları → R1–R4/R8/R9;
§5 CVE → A01–A05; §6 yazılar → C01–C13 ve K01–K05;
§7 portfolyo → P01–P04; §8 kapanış sırası → bu ana öncelik sırası.
76 dosyanın tek tek görev eşlemesi DOSYA-KAPSAM.md içindedir; bulgusuz/destekleyici dosyalara gereksiz düzeltme zorlanmaz.

Kapanan her görev: değişen dosya + kabul testi/kanıt + tarih + CHANGELOG kaydı.
Uyarı etiketi eklemek, yalnız test sayısı artırmak veya bir helper yazmak tamamlanma değildir.
