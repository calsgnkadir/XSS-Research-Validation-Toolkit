# JSX bağlantısının ilgisiz style nesnesi yüzünden atlanması

3 Kasım 2026 · R8-M1 · teknik vaka özeti

**Sürüm.** Önce `220bbd2ead87f555fc09a45366558549dc2c536f`, düzeltilmiş
motor `3e34515774b16a20c99aa6761f425f2bb36aebdf`. HTTP düzeltmesi dahil
incelenen kaynak: `ccdf661abae8a887c30e78e9cbf644133c7f686e`; JSX motoru aynı.

**Problem ve kök neden.** Statik analiz aracı `<a href={target}>` için aday
üretirken aynı etikete `style={{color:'navy'}}` eklenmesi adayı kaybettiriyordu.
Parser, href dışındaki iç içe parantezleri de bütün etiketi eleme nedeni
sayıyordu. İzinli gerçek kaynakta iki bağlantıda beklenen birer aday yerine
sıfır gözlendi; üçüncü örnek seçim sırasında bulundu. Gerçek URL'lerde korumalar
vardı; kaçırılmış XSS gösterilmedi.

**Düzeltme ve yöntem.** Dengeli diğer expression prop'ları geçilip düz href
ayrıca incelendi. Bozuk etiket, spread ve yinelenen href belirsizliği dışlanır;
etiket 32 KiB, parantez derinliği 32 ile sınırlıdır. Motor değişmeden 6 geliştirme,
10 ayrı değerlendirme ve 3 sınır vakası hashleriyle sabitlendi. Değerlendirme
ayrıntıları uygulama sabitlenene kadar motor uzmanına aktarılmadı; değerlendirme
sonrası kod değişmedi. Ortak dosya sistemi dış körlük sağlamaz; amaçlı seçilmiş
vakalar genel kaynakları temsil etmez.

| Ölçüm: inceleme adayı varlığı | Önce | Sonra |
|---|---|---|
| Geliştirmedeki pozitifler | 1/3 | 3/3 |
| Ayrı değerlendirmedeki pozitifler | 0/6 | 6/6 |
| Ayrı değerlendirmedeki negatifler | 4/4 korundu | 4/4 korundu |
| Destek dışı href kontrolleri | 3/3 dışlandı | 3/3 dışlandı |
| Gerçek kapsam A / B adayları | 20 / 129 | 23 / 129 |

**Sonuç ve sınırlar.** Gerçek kaynakta üç medium `jsx-href` adayı eklendi;
önceki satırlar ve 233/47 kaynak hash'i korundu. B'deki bir vendor atlaması
sürüyor. Bu gerçek-kaynak karşılaştırması tarihsel; yeni kabulde tekrarlanmadı.
İç içe href, spread ve genel JSX/TSX/URL güvenliği analizi destek dışıdır.
Aday sayısı açıklık veya zaman kazancı değildir; ek aday manuel incelemeyi artırabilir.

**Yeni kabul.** Seçilmiş JSX suite'i 607 passed; 19 vakalık tekrar ve self-scan
geçti. Genel araç/bench koşusu 2055 passed / 38 skipped; atlanan dxadom
vakalarının tamamı ayrı açık-Chrome 80/80 koşusunda geçti. Temiz kurulumda
11 modül hash'i, 9 CLI kontrolü ve 19 JSX vakası doğrulandı. Yerel browser
kanıtı ayrı sentetik laboratuvar kapsamındadır; bu JSX adaylarını XSS yapmaz.
Linux/uzak CI kabulü ve PyPI yayını yok; mevcut PyPI 0.2.2 değişmedi.

**Katkı.** Engine parser/sınırları, QA bağımsız oracle/ölçümü, security gerçek
kaynak seçimini hazırladı. Koordinatör kod/oracle incelemesi, karşı örnekler,
bütünleşik kabul ve teslimi yönetti.

**Tekrar ve demo.** Depo kökünde Python 3.10+ ve yerel Git geçmişiyle:

```powershell
py -3.10 audit/2026-11-03-release-acceptance/demo.py
py -3.10 audit/2026-11-03-r8-m1/run_validation.py
```

İlk komut iki sabit motoru checkout yapmadan 19 vakada karşılaştırır; ikinci
komut mevcut kaynağın seçilmiş regresyonlarını çalıştırır. Bu tekrar yeni
görülmemiş değerlendirme değildir.

[Tüm kabul komutları ve sınırlar](../audit/2026-11-03-release-acceptance/README.md) ·
[İlk değerlendirme](../audit/2026-11-03-r8-m1/final.json) ·
[Gerçek kaynak karşılaştırması](../audit/2026-11-03-r8-m1/owned-comparison.json) ·
[2:40 demo akışı](R8-M1-DEMO.md)
