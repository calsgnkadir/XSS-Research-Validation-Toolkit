# R3/R4 bağımsız yeniden koşu ve cleanup regresyonu — 7 Ekim 2026

Önceki yeşil sonuçları yeni kabul yerine kullanmadık. Git geçmişindeki 6 Ekim
R3/R4 commitlerini ve 7 Ekim çalışma ağacını birlikte inceledik. Yeni ilk koşu
679 test geçirdi; kaynak incelemesinde cleanup hatasının browser kapanışını ve
paylaşılan oturum durumunun restorasyonunu atlayabildiği bulundu. İki yeni gerçek
Chrome testi önce başarısız oldu; nested finally düzeltmesinden sonra tam paket
681 passed, sıfır skip ile tamamlandı.

Vaka izolasyonunu yalnız monkeypatch unit testine bırakmadık: ayrı CLI sürecinde
gerçek lab'ın ilk producer çağrısını bozduk; ikinci vaka gerçek Chrome ile
tamamlandı. JSON/Markdown yazıldı, strict exit 1 verdi ve iki lab portu kapandı.
Normal dokuz vakalık corpus TP=3 FP=0 FN=0; R3 demo JSON/HTML nesneleri eşitti.

İki native uzman kaynak incelemesi yaptı; kullanım limiti ve son dosya okuma
engelleri açıkça kaydedildi. Testlerin tamamını koordinatör çalıştırdı. Hard
timeout ve uzak Linux CI yerel kabul sonucu değildir; genel R4 açık kalır.

[Komutlar, yeni kanıtlar, sahiplik ve sınırlar](../audit/2026-10-07-r3-r4-revalidation/README.md).
Çalışma saati, resmî staj formu veya CVE iddiası değildir.
