# C10/C13 editoryal takip kabulü — 17 Ekim 2026

Başlangıç kaynak commit'i: `451361b9f8faef3f328b13468d8d3f6a040c7d2c`.
Native `report_frontend_specialist`, görev `c10_c13_fix`, koordinatörün
atadığı README/C10 kapsamını düzenledi. Başlangıçta mevcut ROADMAP, STATUS,
VALIDATION ve `2026-10-17-delivery-review` incelemesi korundu. Ortak ilerleme
belgelerinin kabul kararı koordinatöre aittir.

## Kök neden ve değişiklik

- **C10:** Girişte geri çekilen execution iddiası tarihsel yazının gövdesinde
  ve sonucunda hâlâ güncel davranış gibi anlatılıyordu. Marker→execution ve
  varyant adı→parser escape çıkarımları yerinde geri çekildi. Eski
  `_apply_ct_gate` ve test snippet'leri açıkça obsolete/historical olarak
  etiketlendi; mevcut HTTP sınıflandırması `html-reflection`/`json-only`
  olarak açıklandı. Tarihsel kod örnekleri korunuyor, güncel sözleşme değil.
- **C10:** `split-cmt` için parser'ın özgün tag'i yeniden birleştirdiği
  iddiası düzeltildi. `script-breakout` ve `url-scheme` legacy/ineffective
  execution probe olarak etiketlendi: CID scheme'den önce, suffix yalnız
  comment; executable canary yok. Ayrı R3 href proof'un gerçek tıklama ve
  CID-matched canary sözleşmesine bağlandı.
- **C10:** 25 submit, 101 test, on ek test ve sıfır bağımlılık ifadeleri
  tarihsel snapshot/yazar beyanı olarak sınırlandı. 950 şekil çalışma/bypass
  sayısı değil. Güncel mutation registry'si daha geniş; no-op/duplicate
  ayrımı ayrı açıklandı. Sessizlik güvenli sonuç olarak sunulmuyor.
- **C13:** README eski “yalnız yerel sonuç” bilgisinden `451361b` kaynaklı
  yerel ve hosted CI sonuçlarına güncellendi. Genel CI run `38984494777`
  üç job, K01 run `38984494765` success; run linkleri eklendi. İndirilen
  R3/R4 checker kabulü ile K01 hash/JUnit/beş kontrol incelemesi ayrıldı.
  Tam K01 validate tekrarının yapılmadığı ve sonraki belge değişiklikleri
  için yeni CI sonucu bulunmadığı açık yazıldı.

## Kabul yöntemi ve sınır

Bu teslim belge/kaynak incelemesidir; yeni test, tarama veya browser deneyi
çalıştırılmadı. README'deki sayılar bu specialist'in yeni koşusu değildir;
koordinatörün [son teslim incelemesi](../2026-10-17-delivery-review/README.md)
ve ona bağlı kanıtlar kaynak alındı. Yeni uzaktan CI sorgusu yapılmadı.
`dxadyn.py` içindeki `_apply_ct_gate`, `make_canaries_for`, `_waf_mutations`
ve `_mutation_outcomes` kaynak olarak incelendi; runtime kodu değişmedi.
Kaynakta kalan tarihsel `split-cmt` parser yorumu güncel davranış kanıtı
sayılmadı; bu görevin dosya sahipliği runtime yorumlarını kapsamıyor.
Üç teslim dosyası için `git diff --check` geçti; Markdown yerel bağlantı
hedefleri dosya sistemi üzerinden kontrol edildi, eksik hedef bulunmadı.

Yeni vulnerability, WAF bypass veya tarihsel Bludit execution iddiası yok.
K01 yalnız kendi kontrollü fixture'ını doğrular. Git commit/push yapılmadı.

## Devam kabul incelemesi — 19 Ekim 2026

Native `report_frontend_specialist`, görev `c10_c13_acceptance`, önceki
README/C10 teslimini koruyarak yeniden kaynak/belge incelemesi yaptı.
Başlangıç HEAD `451361b`; önceki teslim çalışma ağacındaydı. Dosya sahipliği
README, writeup 10 ve bu kayıtla sınırlı kaldı; ortak ilerleme belgeleri
koordinatöre bırakıldı.

C10 gövdesindeki obsolete upgrade/test etiketleri, `split-cmt` düzeltmesi,
legacy script/URL şekilleri ve tarihsel test sayılarının sınırı doğrulandı.
Tarihsel kapsam maddelerindeki “still out of scope / not shipped” ifadeleri
geçmiş zamana alındı; güncel browser/callback işlevleriyle karışması önlendi.
`location.hash` → `innerHTML` örneğinde sink adından execution çıkarımı da
kaldırıldı. Bu bir kaynak/belge düzeltmesidir; browser deneyi değildir.

C13 README'deki `451361b`, iki hosted run bağlantısı, yerel 789/38,
218/218 ve 80/80 sayıları 17 Ekim denetimi ve VALIDATION ile eşleşiyor.
K01 hash/JUnit/kontrol incelemesi tam validate tekrarından ayrı anlatılıyor.
Bu tur yeni hosted CI sorgusu veya test/browser/tarama koşusu yapılmadı;
17 Ekim sonuçları 19 Ekim koşusu olarak sunulmadı. Runtime davranışı
değişmedi; C10 kapsam denetiminde kaynak yorumları da sınırlandı.

Üç teslim dosyasında 47 yerel Markdown bağlantı hedefi dosya sistemiyle
kontrol edildi: eksik hedef yok. Bu dosyalar için `git diff --check`
başarılı. Uzak bağlantıların canlılığı bu tur sorgulanmadı. Uzman kendi
commit/push işlemi yapmadı; ortak kabul koordinatörün incelemesine bırakıldı.

Koordinatör son kapsam kontrolünde `dxadyn.py` içindeki tarihsel
`_WAF_MUTATIONS` yorumlarının parser recovery ve WAF bypass iddialarını hâlâ
güncel kural gibi sunduğunu buldu; bu yorumlar kod davranışına dokunmadan
hipotez/ham string transform sınırına çekildi. C10 kaydı böylece writeup ve
ilgili kaynak yorumlarını kapsar. Bu yorum-only kaynak düzenlemesinde runtime
davranışı değişmedi; regresyon paketi çalıştırılmadı.
