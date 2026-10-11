# 11 Ekim — dosyalardan devamlılık ve R9 self-scan

Başlangıç `main`, `5df257792d8e3d6f62f1ca7cb46eb4149f29c153`, temiz çalışma
ağacı. `git fetch origin` başarılı; HEAD...origin/main 0/0. Remote
`https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit.git`.
Fast-forward gerekmiyordu; kullanıcı değişikliği veya ayrışma yoktu.

## Belge denetimi

- `STATUS.md` eski benchmark/hard-timeout eksiklerini güncel iş gibi yineliyordu.
  9 Ekim paketindeki 43 kaynak hash'i eşleşti, JUnit 824/0 failure/0 error/0 skip
  destekliyor. Eski STATUS [ayrı kopyada](STATUS-before.md) korundu; tek güncel
  devam noktası kökte. Arşiv STATUS içindeki göreli bağlantılar özgün depo
  köküne göredir. Tarihsel audit/staj kayıtları değiştirilmedi.
- `AGENTS.md` ve workflow'daki 8/9 Ekim Git yasakları yeni kullanıcı yetkisiyle
  çelişiyordu. 11 Ekim doğrulanmış teslimlerde koordinatör commit/push yetkisi,
  fetch/fast-forward, kaynak okuma, sahiplik, mahremiyet ve uzak doğrulama açıklandı.
- Workflow'daki “diğer üç rol read-only” ifadesi 7 Ekim'e aitken güncel gibi
  duruyordu; 8 Ekim'de beş TOML workspace-write olduğu belirtildi. Beş kalıcı
  tanım değişmedi; SHA-256 değerleri kabul manifestinde.
- ROADMAP hedefleri, kabul kapsamı ve açık kutuları değiştirilmedi. R4 son
  kanıt bağlantısı 9 Ekim'e taşındı; R8 mevcut dar kabulü ve regex sınırı belirtildi.
  VALIDATION'ın eski “en son/güncel” başlıkları tarihsel olarak düzeltildi.
- Silme önerisi yok; kayıtlar ve kullanıcı verileri korundu. Yeni veritabanı,
  dış hedef taraması, Docker lifecycle veya arka plan otomasyonu çalıştırılmadı.

## R9 kök neden ve kabul

Başlangıç `.github/workflows/ci.yml:33` içindeki `command && exit 1 || echo`
zinciri her nonzero sonucu başarıya çeviriyordu. `dxa.py:814` JSON yolunda
error=2, finding=1, clean=0 üretir; Python traceback de exit 1 olabilir.
Bu nedenle yalnız exit 1 kontrolü yeterli değildir.

Yeni `bench/ci_self_scan.py:46` gerçek CLI'ı `--json --json-out` ile çalıştırır;
taze geçici rapor, exit 1, boş stderr, static v1/high candidate bulguları,
stdout/rapor source-sink eşleşmesi ve hata/eksik tarama olaylarını denetler.
Confidence filtresi skip'i kabul edilir, input okuma/keşif skip'i edilmez.
Statik adaylar XSS execution veya güvenlik açığı kanıtına yükseltilmez.
Workflow bu helper'ı ve bağımsız regresyonları zorunlu `test` job'ında çalıştırır.

Eski davranış gerçek Git Bash üzerinde RuntimeError ve ModuleNotFoundError
için gate exit 0, temiz child exit 0 için gate exit 1 olarak yeniden üretildi:
[kanıt](qa-legacy-gate-retry.json). İlk [deneme](qa-legacy-gate.json) PowerShell
quoting kusuru içerir; amaçlanan üç vakanın kanıtı sayılmaz. Dosya korunmuştur.

## Native roller ve inceleme

| Rol / görev | Özel sahiplik | Katkı |
|---|---|---|
| Engine `/root/ci_exit_gate` | ci.yml, bench/ci_self_scan.py | CLI sözleşmesi, helper ve CI bağlantısı |
| QA `/root/ci_gate_oracle` | bench/test_ci_self_scan.py | Bağımsız gerçek subprocess oracle'ları ve eski Bash karşı örneği |
| Koordinatör | Ortak belgeler, audit/staj, entegrasyon/Git | Kaynak ve oracle incelemesi, QA'ya ek karşı örnek geri bildirimi, birleşik kabul |

İki rol `agent_type` ile native çağrıldı; fork geçmişi verilmedi, dosyalardan
bağlam aktarıldı. En fazla iki uzman eşzamanlı çalıştı; aynı dosyada iki yazıcı
yoktu. Sandbox helper setup hatası gerçek araç sonucunda görüldü; okumalar ve
testler standart onaylı yükseltilmiş exec ile, yazmalar apply_patch ile başarılı.
TOML sandbox değeri gerçek runtime izin kanıtı sayılmadı. Uzmanlar Git yapmadı.
Her iki görev tamamlandı; arka planda sürdükleri iddia edilmez.

## Yeni yerel doğrulama

Koordinatör: **143 passed, 13.21 s**, exit 0; failure/error/skip yok. Gerçek
self-scan helper exit 0. Python 3.10.11, pytest 9.1.1, Windows; browser/Docker yok.
[Komutlar ve SHA-256](acceptance.json), [JUnit](acceptance.xml).

```powershell
py -3.10 audit/2026-10-11-continuity/run_validation.py
```

Script mevcut acceptance dosyalarının üzerine yazmayı reddeder. Başka tekrar
için JSON içindeki test/helper komutlarını yeni bir kanıt konumuyla çalıştır.
QA'nın [20 testlik son koşusu](qa-acceptance.xml) 143'e dahildir; önceki 15/16
testlik ara kayıtlar tarihsel ve örtüşür, sayılar toplanmaz. 9 Ekim 824 testi
bu oturumda yeniden koşulmadı; hash ve eski JUnit karşılaştırması yapıldı.
Yeni paylaşım JUnit'lerinde makine adı çıkarıldı; test sonuçları değişmedi.
21 teslim dosyasında secret/kişisel yerel yol kalıpları ve büyük çıktı taraması
eşleşme vermedi; içerikler ayrıca incelendi. Güncel devam/audit/staj/çalışma
düzeni bağlantıları ve `git diff --check` temiz. Bu tarama bütün olası sırları
tespit etme garantisi değil, bu teslimin paylaşım kontrolü kaydıdır.

## Uzak CI ve kalan kapsam

Başlangıç `5df2577` için [CI 37934071361](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/37934071361)
ve üç job başarılı. [Sınırlı API metadata'sı](remote-baseline.json) saklandı;
iki artifact mevcut ancak içerikleri indirilmedi. Genel workflow yeşilliği,
skip olmayan browser kabulü veya artifact içeriği için tek başına kanıt değildir.
Yeni teslimin uzak sonucu başlangıç CI'ından ayrı değerlendirilmelidir.

R4 gerçek ürün bootstrap/login/port-discovery, uzak artifact içerik kabulü;
R9 isteğe bağlı browser job/skip denetimi, rapor mahremiyeti ve genel ağ sınırı;
R5 temiz ortam tekrarı ve diğer roadmap işleri açık kalır. Yeni teslimin Git
durumu STATUS ve gerçek Git ref'lerinden okunmalıdır; audit aktif iş kuyruğu değildir.
