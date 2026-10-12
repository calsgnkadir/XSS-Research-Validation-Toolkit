# 12 Ekim — OneDrive dışına çalışma kökü geçişi

Kullanıcı yeni C:\xss\xss-github hedefini açıkça seçti. Hedef önceden yoktu;
başka depo üzerine yazılmadı. Kaynak .pytest_cache okuması erişim reddi verdi.
1076 erişilebilir dosyanın SHA-256 kaydı alındı; bütün Git-tracked dosyalar
bu kümede bulunuyor. Gizli .git, .codex ve yerel ignored .dxa verileri dahil.

Move-Item denemesi açık işlem kilidi nedeniyle başarısız oldu; kaynak
korunarak hedef kopyası oluşturuldu. 1076 hash eşleşti, HEAD ve git status
eşleşti. .git/index byte değişikliği git status cache refresh'i nedeniyle
karşılaştırma istisnası; semantik Git durumu ayrıca kontrol edildi.
Okunamayan .pytest_cache kopyalanmadı, kaynakta korundu. Kaynak silinmedi.
Bu, doğrulanmış yeni çalışma kopyasına geçiştir; eski konum temizliği tamamlanmadı.

Yeni kökte R4/R9 smoke **95 passed, 15.90 s**, sıfır failure/error/skip.
[JUnit](smoke.xml), [özet](acceptance.json). Yeni test sonucu önceki test
sayılarına eklenmez. Tam dosya manifesti yerel C:\xss\migration-verification.json
konumunda tutuldu; özel ignored dosya yollarını yayımlamamak için Git'e eklenmedi.

Aktif geliştirme bundan sonra yeni kökte yapılır. Eski OneDrive kopyası,
çalışan uygulama/oturum kilidi kalkmadan silinmez. Codex çalışma alanı yolu
bu araçlarla otomatik değişmedi; sonraki oturum yeni kökten açılmalıdır.
Yeni dashboard, dış tarama, volume/veri silme veya arka plan görevi yok.
