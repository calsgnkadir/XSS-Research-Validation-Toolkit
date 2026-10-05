# Roadmap hakkındaki agent yorumunun değerlendirmesi

5 Ekim 2026. Kullanıcının paylaştığı yorum tasarım önerisidir; bağımsız test,
ürün tamamlanma kanıtı veya çalışma talimatlarının üstünde bir yetki değildir.

Kabul edilen öneriler:

- R1 için resmî şema: dataclass sözleşmesi ve hata durumlarını reddeden testler eklendi.
- Son kanıt tarihi ve sonraki kabul kapısı: roadmap'e takip tablosu eklendi.
- R1 sonrası küçük K01: tam R5/R6'yı beklemeden tek yerel, tekrar üretilebilir vaka.
- C işlerini önceliklendirme: önce portfolyo için C01, araç doğruluğu için C11,
  yetkilendirme için C05. Diğer yazılar silinmeden daha sonraki sırada kalır.
- Sürüm kapısı: ilk doğrulanmış araştırma sürümünün zorunlu işleri açık listelenir.
- Okuyucu ve yetki: yeniden üretim hedefi Python/Git bilen bağımsız değerlendirici;
  dış hedef yetkisi ve dış mesaj/yayın yetkisi ayrı tutulur.

Düzeltilerek alınan noktalar:

- Yorum, K01'i R6 sonrasına yerleştiriyor; mevcut tabloda R5 zaten R6'dan önceydi.
  Asıl değişiklik küçük bir vaka paketini R1 sonrasına çekmek, bütün R5'i erken
  tamamlanmış saymak değil.
- Evidence seviyeleri doğrusal merdiven değildir. Sink-observed ve callback
  farklı gözlemlerdir; biri diğerinden genel olarak daha güçlü JS proof değildir.
- Dedup kuralı IDOR+XSS'in tek bulgu olduğu sonucunu vermez. Kök neden, rol ve
  güvenlik sınırı ayrıca incelenmelidir.
- "3–4 ay" veya toplam bitiş tarihi için kapasite/teknik veri yok. Küçük paketler
  için tahmini efor ayrı tutulur; geçmiş çalışma saati veya taahhüt değildir.

Patchstack beyanı tamamen boşluktan gelmiyor: [research/README Results](../../research/README.md#results)
bir WordPress eklentisinde kabul edilmiş duplicate beyanı içeriyor.
[Sprint planı](../../research/2026-09-27-cve-hunt-sprint/README.md) ise non-WordPress
hedef için kanal/kabul varsayımı içeriyor. Bunlar farklı iddia tipleridir:
ilki tarihsel yazar beyanı, ikincisi plan varsayımı. Depodaki bu metinler dış
triage kaydının yerine geçmez; kabul/ödül/yeni CVE bağımsız doğrulanmış sayılmaz.
"Kanıt yok" durumundan "uydurma" sonucu çıkarılmadı. Kanalın güncel kuralları
araştırma başladığında doğrulanacak; bu teslimde dış gönderim yapılmadı.
