# Geliştirme kaydı — 5 Ekim 2026

Görevler: R1, K05/C13 rapor altyapısı ve S01. Teknik çalışma kaydıdır;
resmî staj onayı veya çalışma saati beyanı değildir.

Önceki teslimde stored blind denemelerin kalıcı kaydı tamamlanmıştı.
Bugünkü incelemede flow CLI'nin ham marker içeren JSON yanıtına EXECUTABLE
dediği, HTML sınıflandırmasının da varyant adındaki `-breakout` son ekini
bağlamdan çıkma kanıtı saydığı doğrulandı.

HTTP modları ortak bulgu üreticisine bağlandı. Ham marker ve tırnak gözlemi
execution iddiasından ayrıldı. JSON, markup, diğer yanıt türleri ve eksik
Content-Type farklı sınıflandırılıyor. JSON ve HTML aynı finding nesnelerini
kullanıyor; bulgu kimliği ve evidence seviyesi raporda gösteriliyor.

Eski testlerin bazıları yanlış execution beklentisini koruyordu. Beklentiler
gözlem semantiğine uyarlandı; ayrıca yanlış bağlamda kalan gerçek marker
örnekleri ve beş HTTP yolunu karşılaştıran 12 regresyon eklendi.
İlk çalışmada sandbox localhost/geçici dosya erişimini engelledi. Aynı odaklı
paket gerekli izinlerle tekrar çalıştırıldığında 215 test geçti. Son rapor
değişiklikleriyle tam paket: **450 geçti, 36 atlandı, 1 uyarı**.
[Kanıt](../VALIDATION.md), [model ve kullanım](../tools/dom-xss-analyzer/HTTP-EVIDENCE.md).

Öğrenilen: testin beklediği etiket de yanlış olabilir. Üretim davranışını
negatif kontrolle sınamak, “ham metin var” ile “JavaScript çalıştı” ayrımını
korur. Ortak üretici, modlar arasında sessiz sınıflandırma farkını azaltır.

Kalan: DOM/attempt modeli entegrasyonu, sink/rol dedup, rol doğrulaması,
auth/rate/CSRF hataları ve browser ile canary execution. Tam proof→fix→retest
portfolyo vakası veya yeni CVE bu teslimde oluşturulmadı.
