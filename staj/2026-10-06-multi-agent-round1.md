# Scope, gözlemci etkisi ve benchmark — 6 Ekim 2026

Yerel iki-origin testi crawler'ın kapsam dışı form/redirect/CSRF isteklerini
ortaya çıkardı. Discovery filtresi tek başına yeterli değildi; istek ve redirect
katmanına aynı origin sınırı taşındı, cookie jar korundu.

Eval'i sarmalamak direct eval'i indirect çağrıya çevirerek fonksiyon kapsamını
bozuyordu. Global değişkenle geçen test yeterli değildi. Fonksiyon-local karşı
örnek hatayı gösterdi; hook kaldırıldı ve destek sınırı JSON/HTML'de belirtildi.

R4'te execution ile reflection ölçümlerini ayırdık. Tamamlanan pozitif vakada
canary bulunamazsa FN sayılır; beklenen etikete bakıp testi ölçümden çıkarmak
başarı oranını yanıltır. Hata/eksik pencere ise güvenli negatif değildir.

Gerçek çalışan katkıları, test sonuçları ve kalan kapsam
[teslim kaydında](../audit/2026-10-06-multi-agent-round1/README.md).
Bu bir öğrenme kaydıdır; resmî staj defteri veya yeni CVE iddiası değildir.
