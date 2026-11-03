# JSX bağlantı adaylarının ilgisiz prop yüzünden atlanması

3 Kasım 2026 · R8-M1 · yayımlanmamış kaynak değişikliği

**İncelenen commit:** `3e34515774b16a20c99aa6761f425f2bb36aebdf`.
**Önceki commit:** `220bbd2ead87f555fc09a45366558549dc2c536f`.

**Problem.** Statik XSS inceleme aracında `<a href={target}>` raporlanırken
aynı etikete `style={{color:'navy'}}` eklenmesi bağlantı adayını kaybettiriyordu.
Parser, href dışındaki süslü parantez derinliğini de tüm etiketi dışlama nedeni
sayıyordu. İzinli gerçek projede iki bağlantıda beklenen birer aday yerine
sıfır gözlendi; kaynak hashleri değişmedi. Üçüncü aynı biçim seçim aşamasında
bulundu. Gerçek URL değerleri korumalardan geçiyor; kaçırılmış XSS gösterilmedi.

**Deney.** Motor değişmeden önce 6 geliştirme, 10 ayrı değerlendirme ve
3 destek sınırı vakasının girdileri, beklentileri ve hashleri sabitlendi.
Değerlendirme ayrıntıları motor uzmanına uygulama hash'i sabitlenene kadar
aktarılmadı. Ortak dosya sistemi nedeniyle bu, süreç ayrımıdır; dışarıdan
kör değerlendirme değildir. Vakalar amaçlı seçildi, genel kaynakları temsil etmez.

**Değişiklik.** Parser dengeli, href dışındaki expression prop'larını içeriklerini
analiz etmeden atlıyor; düz href ifadesini ayrıca inceliyor. Eksik/bozuk etiket,
spread ve yinelenen href belirsizliğinde aday üretmiyor. Etiket boyutu 32 KiB,
parantez derinliği 32 ile sınırlı. İlk geliştirme kontrolünden sonra kaynak
incelemesinde yinelenen href koruması eklendi; ayrı değerlendirme bundan sonra
son motor hash'i üzerinde bir kez açıldı. Değerlendirme sonrası kod değişmedi.

| Gözlem | Önce | Sonra |
|---|---|---|
| Geliştirme: beklenen bağlantı adayları | 1/3 | 3/3 |
| Ayrı değerlendirme: beklenen bağlantı adayları | 0/6 | 6/6 |
| Ayrı değerlendirme: negatif kontroller | 4/4 korundu | 4/4 korundu |
| Destek dışı href ifadeleri | 3/3 dışlandı | 3/3 dışlandı |
| Gerçek kapsam A: inceleme adayları | 20 | 23 |
| Gerçek kapsam B: inceleme adayları | 129 | 129 |

**Sonuç ve sınırlar.** Gerçek kaynakta üç medium `jsx-href` adayı eklendi;
önceki adaylar ve diğer satır özellikleri korundu. İki kapsamın 233/47 kaynak
hash'i aynı kaldı; hata yok, B'deki bir vendor atlaması sürüyor. Artan aday
sayısı daha çok manuel inceleme de gerektirebilir; zaman veya emek kazancı
ölçülmedi. İç içe gerçek href ifadeleri, spread ve genel JSX/TSX çözümlemesi
desteklenmiyor. Bu üç sınırın dışlanması güvenlik sonucu değildir. Seçilmiş
15 dosyada tarihsel kabulde 607 regresyon ve yerel CI self-scan geçti; bunlar yazılımın
doğrulama kanıtıdır, kullanıcı başarısı ölçüsü değildir. Uygulama/HTTP/browser
testi bu statik vaka kabulünde yapılmadı; genel doğruluk, doğrulanmış XSS veya
CVE iddiası yok. Yeni sürüm kabulü ayrıca kaydedilir; 607 tüm pytest/browser
paketinin güncel tekrarlandığı anlamına gelmez.

**Katkı.** Engine uzmanı parser ve sınır kontrollerini, QA uzmanı
bağımsız vaka/oracle ve ölçüm aracını, security uzmanı gerçek kaynak seçimi ve
kapsam incelemesini hazırladı. Koordinatör kapsamı yönetti, kod/oracle'ları
inceledi, karşı örnekleri geri gönderdi ve bütünleşik doğrulamayı çalıştırdı.

**Tekrarlama.** Depo kökünde Python 3.10+ ve yerel Git geçmişiyle:

```powershell
py -3.10 audit/2026-11-03-release-acceptance/demo.py
py -3.10 audit/2026-11-03-r8-m1/run_validation.py
```

İlk komut iki sabit motoru Git'ten okuyup 19 vakayı karşılaştırır; checkout
yapmaz. İkinci komut mevcut kaynağın seçilmiş regresyonlarını çalıştırır.

[Kabul ve komutlar](../audit/2026-11-03-r8-m1/README.md) ·
[Ayrı değerlendirme](../audit/2026-11-03-r8-m1/final.json) ·
[Gerçek kaynak karşılaştırması](../audit/2026-11-03-r8-m1/owned-comparison.json) ·
[2–3 dakikalık demo](R8-M1-DEMO.md)
