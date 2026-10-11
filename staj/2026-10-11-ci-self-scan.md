# 11 Ekim — CI başarısının anlamını doğrulama

Amaç: yeni sohbetin ilerlemeyi Git ve kanıt dosyalarından bulmasını sağlamak;
CI'ın analiz aracı hatasını beklenen bulgu sanmasını düzeltmek.

Eski shell zinciri RuntimeError ve eksik modül hatasında exit 0 dönüyordu.
Çıkış kodu tek başına yeterli değildi: normal bulgu da traceback de 1 olabilir.
Çözüm gerçek taramadan taze JSON raporu, bulgu eşleşmesi ve hata/skip olaylarını
birlikte denetlemek oldu. Statik aday yine execution kanıtı değildir.

Engine uygulamayı, QA bağımsız subprocess karşı örneklerini yazdı. Koordinatör
input skip ve yanlış context/kanıt tutarlılığı kontrollerini genişletmesini
istedi, sonra birleşik paketi çalıştırdı: **143 passed**, hata/skip yok;
gerçek self-scan başarılı. Browser/Docker veya dış hedef kullanılmadı.
[Komut, kaynak hash'leri ve sınırlar](../audit/2026-10-11-continuity/README.md).

Öğrenilen: eski bir test sayısının kaynak hash'iyle eşleşmesi yeni test koşusu
değildir; uzak workflow başarısı da artifact içeriğinin bağımsız incelemesi
değildir. STATUS tek devam noktası, audit tarihsel kanıt olarak ayrıldı.
