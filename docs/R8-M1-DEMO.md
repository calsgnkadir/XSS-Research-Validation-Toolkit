# R8-M1 — 2–3 dakikalık teknik demo

Bu akış terminalde canlı sunum içindir; kayıt edilmiş video değildir.
Yalnız sentetik JSX/TSX metni statik taranır. Git geçmişi ve Python 3.10+
gerekir; ek paket gerekmez. Önce `220bbd2ead87f555fc09a45366558549dc2c536f`,
sonra `3e34515774b16a20c99aa6761f425f2bb36aebdf` motoru kullanılır.
Script Git checkout yapmaz; iki `dxa.py` SHA-256 değerini tarihsel kanıtla
karşılaştırır, dondurulmuş manifest'i mevcut ölçüm aracıyla doğrular.

Depo kökünde önceden prova edin:

```powershell
py -3.10 audit/2026-11-03-release-acceptance/demo.py
```

**0:00–0:30 — problemi göster.** Bu iki biçimi ekranda gösterin:

```jsx
const view = <a href={target}>go</a>;
const view = <a href={target} style={{color:'navy'}}>go</a>;
```

“Href aynı. İlgisiz style nesnesi eski parser'da bağlantının tamamını eliyordu.
İki biçimde de bir inceleme adayı bekliyoruz. Ölçtüğümüz şey adayın raporda
kalması; bu kaynakları uygulama olarak çalıştırmıyoruz.”

**0:30–1:15 — komutu çalıştır ve minimal tabloyu oku.** Yukarıdaki komutu
çalıştırın. `dev-flat` 1→1, `dev-style-after` 0→1 olmalı. Sabit URL ve custom
component kontrolleri 0→0 kalmalı. Hata veya nonzero çıkışı başarı diye
sunmayın. Beklenen sayılar veya son aday özellikleri farklıysa script hata verir.

“Kök neden href dışındaki parantez derinliğinin etiketi elemesiydi. Düzeltme
dengeli diğer prop'ları geçip href'i ayrı inceliyor. Destek dar ve sınırlı.”

**1:15–2:00 — ayrı değerlendirmeyi göster.** Terminaldeki split tablosunu okuyun:
geliştirme TP/FP/FN/TN 1/0/2/3→3/0/0/3; ayrı değerlendirme
0/0/6/4→6/0/0/4; üç sınır kontrolü 0/0/0/3 kalıyor.

“19 vaka motor değişmeden sabitlendi. Altı eksik değerlendirme adayı geri geldi;
dört negatif kontrol korundu. Bu demo aynı dondurulmuş vakaların tekrarıdır,
yeni görülmemiş değerlendirme değildir. Ortak dosya sistemi dış körlük sağlamaz.”

**2:00–2:40 — gerçek etkiyi ve sınırları bağla.**
[Tek sayfalık özetteki tabloyu](R8-M1-CASE-STUDY.md) gösterin.

“Tarihsel gerçek kaynak karşılaştırmasında A'da 20→23, B'de 129→129 aday
gözlendi; kaynak hashleri ve önceki satırlar korundu. Üç ek medium aday
incelemeye açıldı. Gerçek URL'lerde korumalar vardı; açıklık kanıtlamadık.
Bir vendor atlaması sürüyor. İç içe href, spread ve genel JSX analizi destek
dışında; genel doğruluk veya zaman kazancı ölçmedik.”

Seçilmiş regresyonların ayrıntılı tekrarı sunum dışında çalıştırılır:

```powershell
py -3.10 audit/2026-11-03-r8-m1/run_validation.py
```

Bu komut mevcut kaynağı test eder; tarihsel 607 sonucunu güncel tüm-suite
kabulüne dönüştürmez. Demo PyPI 0.2.2'yi değiştirmez ve browser kanıtı sağlamaz.

Önceki CV taslağı (sunum süresine dahil değildir): “XSS analiz aracında JSX
bağlantı adaylarının ilgisiz prop nesneleri nedeniyle atlanmasını gideren
çalışmayı koordine ettim; ayrı değerlendirmede 6 eksik inceleme adayının geri
kazanılmasını ve gerçek kaynakta üç ek bağlantı adayını önce/sonra
karşılaştırmasıyla doğruladım.”
