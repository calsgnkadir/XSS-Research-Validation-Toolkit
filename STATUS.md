# Güncel devam noktası — 14 Ekim 2026

Son auth/blind dar teslim birleşik regresyonu: **193 passed**, sıfır hata/skip.

Ana hedef ve kabul ölçütleri [ROADMAP](ROADMAP.md), test kanıtları
[VALIDATION](VALIDATION.md), çalışma düzeni [AGENT-WORKFLOW](docs/AGENT-WORKFLOW.md).

## Devam eden teslim — auth/CSRF ana runner entegrasyonu

Engine ana runner kod/testini tamamladı. Koordinatör 215 birleşik regresyonu
ve gerçek Chrome runner CLI 6/6 kontrolünü doğruladı; altı cleanup geçti,
aday XSS skorları ayrı kaldı. [Yerel kabul](audit/2026-10-14-r4-auth-runner/README.md).
Zorunlu browser CI yeni testleri ve gerçek kontrol adımını çalıştıracak;
uzak sonuç henüz bekliyor. R5/K01 temiz ortam tekrarı QA uzmanında sürüyor.
Blind/admin ve kontrollü araç kıyası sırada.

## Son çalışma — auth/CSRF ve blind/admin sınır kontrolleri

Engine auth fixture'ını yazdı; iki uzman da kullanım limitinde durdu.
Koordinatör devraldı: altı gerçek browser hata kontrolü ve yedi blind/admin
adapter regresyonu **13/13** geçti. Ayrı süre sınırlı CLI **6/6** geçti.
[Kanıt ve sınırlar](audit/2026-10-14-r4-auth-blind-controls/README.md).
Yeni modüller required browser CI test listesine eklendi; uzak kabul bekliyor.
Bu altı hata kontrolü XSS skorlarına girmez. Ana runner entegrasyonu yukarıda;
ayrı admin hesabıyla blind fixture ve eşit koşullu araç karşılaştırması açık. DalFox/XSStrike/ZAP/Go mevcut PATH'te bulunamadı.

## Aktif teslim — R4 corpus v3 yerel ve uzak kabulü

Başlangıç 61dde5c. Corpus 9→14 genişledi: escaped/raw birlikte, no-op
sanitizer→DOM, editor notes raw/fixed ve aynı-origin iframe. Adapter artık
source/parameter/read/role ve açık frame allowlist'ini doğruluyor.
Koordinatör kabulü: **527 test geçti**, sıfır hata/skip; strict Chrome CLI
**14/14, TP=7 FP=0 FN=0**. [Kanıt](audit/2026-10-14-r4-corpus-v3/README.md).
CI gate yeni kimlik ve 14 vaka sözleşmesine bağlandı. Kapsam paydası raporda
açık; [karşılaştırma protokolü](bench/COMPARISON-PROTOCOL.md) yazıldı.
Engine ve QA kod/test katkısından sonra kullanım limitinde durdu; koordinatör
eksikleri tamamlayıp doğruladı. Bu teslimdeki uzmanlar durdu; yeni görevler yukarıda.
Docker kodu değişmedi ve ürün regresyonları geçti; canlı Docker tekrar edilmedi.
Kod teslimi 4331403 push edildi; uzak main eşleşti. CI 38550538424 üç job
başarılı; indirilen artifact commit kaynaklarıyla gate'ten geçti:
JUnit 134, sıfır skip/error; corpus 14/14, TP=7 FP=0 FN=0.
[Uzak kanıt](audit/2026-10-14-r4-corpus-v3/remote-acceptance.json).
Sıradaki uygulanabilir R4 işi auth/CSRF hata corpus kapsamıdır.
Genel R4, auth/CSRF ve blind/admin kapsamı ile kontrollü rakip kıyası açık.

## Son doğrulanan teslim — R4 strict corpus artifact gate ve QA follow-up

14 Ekim: CI artifact gate JSON raporu ve JUnit'i doğruluyordu ama corpus
Markdown'ını karşılaştırmıyor, çalışma ortamı/komutu/kaynak hashlerini güncel
checkout'a bağlamıyordu. `check_ci_acceptance.py` artık zorunlu Markdown'ı
canonical JSON renderer ile tam eşleştiriyor ve runner/scanner/fixture/corpus
hashlerini doğruluyor; workflow bu Markdown'ı kapıya veriyor. İlk sürüm 90
focused/204 birleşik test geçti; `7f67d53` için uzak CI 3/3 başarılı ve artifact
gate'ten geçti. Bağımsız QA, makul fakat yanlış runtime beyanlarının da geçebildiği
dar bir boşluk buldu; gate bunu Python 3.12/Linux koşuluyla kapatıyor. Güncel
follow-up **94 focused / 208 birleşik test** geçti. [Kanıt ve sınırlar](audit/2026-10-14-r4-provenance-gate/README.md).
JSON/Markdown birlikte değiştirilmiş dört regresyon eski gate açığını
yeniden üretti; son birleşik JUnit 208/208 geçti. QA ve Engine incelemesi
tamamlandı. Runtime follow-up `3ca474a` push edildi ve uzak main eşleşti.
[38530419858](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38530419858)
CI 3/3 başarılı; indirilen artifact güncel gate ile geçti: JUnit 94, sıfır
skip/error; corpus 9/9, TP=3 FP=0 FN=0; Python 3.12.15/Linux ve kaynak
hashleri eşleşti. [Uzak kabul](audit/2026-10-14-r4-provenance-gate/runtime-remote-acceptance.json).
Bu teslimden sonraki kimlik/corpus ve kapsam paydası işi yukarıdaki v3 tesliminde
ilerletildi; kontrollü araç karşılaştırması henüz yapılmadı.
Bu runtime teslimindeki QA/Engine görevleri tamamlandı; yeni corpus görevleri yukarıda.

## Önceki teslim — R4 runner ve canlı Bludit kabulü

13 Ekim 2026: sabit Apache reverse proxy iki ağlı, yeni ve geçici bir Compose
projesinde çalıştı. Bludit yalnız internal ağda kaldı; proxy 127.0.0.1 üzerinde
geçici port yayımladı. Temiz kurulum, ayrı login, ham ve escaped public browser
kontrolleri geçti. Eksik browser ve enjekte edilmiş kanıt uyuşmazlığı hata verdi;
üç UUID projesi de temizlendi. Önceden var olan 15 container, 27 volume ve 9
network kimlikleri birebir korundu. Runner'a opt-in entegrasyon eklendi; gerçek
CLI koşusunda Bludit kontrolleri ayrı `product_controls` alanında kaldı ve
scanner skorlarına karışmadı. Benchmark regression paketi **434 passed, sıfır
failure/error/skip**.
[Runner kanıtı](audit/2026-10-13-r4-runner-live/README.md) ve
[lifecycle kanıtı](audit/2026-10-12-r4-ingress-live/README.md). Bu dar teslimler
genel R4/R9, corpus gate veya açıklık triage'ını kapatmaz.
Storage ingress/Compose kodunu, QA bağımsız testleri, koordinatör entegrasyon
ve canlı kabulü üstlendi. Aktif agent/arka plan işi yok. Runner commit’i
`afcb7c1` remote main ile eşleşti; aynı commit için [38444394044](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38444394044)
ve [38444393733](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38444393733)
CI koşuları 3/3 job success. Hosted CI yerel Bludit Docker kabulini çalıştırmadı;
workflow metadata'sı [burada](audit/2026-10-13-r4-runner-live/remote-delivery.json).

## Önceki R4 engeli (12 Ekim)

Eski tek-container internal ağda Docker host portu oluşmadığı için kurulumdan
önce duruldu. [Tarihsel kanıt](audit/2026-10-12-r4-product-adapter/README.md).
13 Ekim'deki iki-container ingress bu engeli yerel kabul kapsamında çözdü.

## Aktif çalışma yeri

Aktif depo **C:\xss\xss-github**. Kullanıcı bu yeni hedefi açıkça seçti.
1076 erişilebilir dosya SHA-256 eşleşmesi, HEAD/çalışma ağacı eşitliği ve yeni
konumda **95 passed** doğrulandı. Eski OneDrive kökü işlem kilidi nedeniyle
silinmedi; erişilemeyen .pytest_cache yalnız eski kopyada korundu. Eski kopyada
geliştirme sürdürülmez; sonraki Codex oturumu yeni kökten açılmalıdır.
[Taşıma kontrolü ve sınır](audit/2026-10-12-relocation/README.md).

## Son doğrulanan teslimler ve yetki

- Kullanıcının son talimatı ana ajan incelemesi ardından commit/push ve
  OneDrive dışına taşıma; önceki Git yasağı kaldırıldı.
- R4 **c5d5451cc81dc94ce65aab330e3925a3a6150c04** push ve uzak hash eşleşmesi
  doğrulandı. CI **38233880679 success**, yeni artifact kapısı success.
  Mevcut GitHub oturumu yalnız bellekte kullanılarak artifact erişimi çözüldü.
  Uzak Linux JUnit **94 passed, sıfır hata/skip**, corpus **9/9 TP=3 FP=0 FN=0**,
  demo execution-observed. Runner/scanner/fixture hash'leri commit ile eşleşti.
  [Uzak içerik kabulü](audit/2026-10-12-r4-ci-acceptance/remote/acceptance.json).
- R9 **8873aaf1848a0ef67d4c48523d9a2bd78ff60d88** push ve uzak hash eşleşmesi
  doğrulandı. Ortak raporda bilinen API/CSRF alanları ve HTTP(S) evidence_links
  sırları maskelendi. Eski kodda iki regresyon başarısız; yeni kod **126 passed**,
  sıfır hata/skip. [Kanıt](audit/2026-10-12-r9-report-privacy/README.md).
  CI **38267306222 success**, üç job success; [metadata](audit/2026-10-12-r9-report-privacy/remote-delivery.json).
  Bu R9 koşusunun artifact içeriği ayrıca indirilmedi; önceki R4 içerik kabulü ayrıdır.
- İlk yerel R4 kabulü 94 browser ve ayrı 185 birleşik regresyon; R9 kabulü 126.
  Yeni konum smoke'u 95. Örtüşen test sayıları toplanmaz. 9 Ekim 824 ve
  11 Ekim 143 kayıtları tarihsel; bu turda tam 824 paketi yeniden koşulmadı.

## Gerçek görev sahipliği

| Sahip | Sorumluluk | Durum |
|---|---|---|
| Koordinatör | Entegrasyon, belgeler, Git, uzak artifact ve yeni konum | İnceleme ve doğrulama tamam |
| Engine /root/r4_ci_gate | ci.yml, check_ci_acceptance.py | Tamam |
| QA /root/r4_acceptance_qa | R4 bağımsız testler ve son inceleme | R4 tamam; ayrı R9 turu limitte kesildi |
| Report /root/r9_report_privacy | dxa_evidence.py, test_report_privacy.py | Kod/test yazıldı; limit sonrası koordinatör tamamladı |

Native roller çağrıldı, beş kalıcı TOML korundu. En fazla iki uzman eşzamanlı
çalıştı. R9 bağımsız specialist QA finali yok; koordinatör kod/oracle, eski-kod
karşı örneği ve 126-test kabulünü tamamladı. Çalışan arka plan görevi yok.

## Açık işler ve sıradaki adım

- R1/R2 ve R3 loopback kabulü tamam; genel ürün tamam değil.
- R4 bağımsız gerçek ürün lifecycle kabulü ve yerel opt-in runner entegrasyonu
  tamamlandı. Runtime follow-up 3ca474a için yerel 208 test, hosted CI 3/3
  ve indirilen artifact kabulü geçti. Genel corpus/coverage ve karşılaştırma
  metodolojisi açık.
- Zorunlu r3-proof continue-on-error kullanmaz; ayrı opt-in browser-tests kullanır.
  Yeni R4 uzak artifact kabulü genel R4/R9 kutularını kapatmaz.
- R8 regex/tek dil AST; R9 genel rapor/konsol mahremiyeti, ağ/WebSocket ve diğer
  birleşik kabul işleri açık. Dar exporter düzeltmesi genel sır tespit garantisi değildir.
- R5 bağımsız temiz ortam tekrarı, R6 paketleme ve C/K/P/S/A işleri ROADMAP'te.
- Eski kilitli OneDrive kopyası, onu kullanan işlem kapandıktan sonra ayrı
  doğrulamayla kaldırılabilir. Yeni geliştirme yalnız C:\xss\xss-github içinde.
