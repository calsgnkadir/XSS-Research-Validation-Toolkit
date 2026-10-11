# Proje agent talimatları

## Başlangıç ve kaynaklar

- Her yeni sohbette kökü `git rev-parse --show-toplevel`, branch'i `git branch --show-current`, remote'u `git remote -v` ve çalışma ağacını `git status --short` ile doğrula; `git fetch origin` sonrası yerel HEAD ile upstream'i karşılaştır. Yalnız temiz ve sadece geride olan dalı fast-forward güncelle. Yerel değişiklik veya ayrışmada üzerine yazma; reset/clean/force kullanma. Güncel çalışma kopyası varken ZIP'ten ikinci proje üretme.
- Her işe başlamadan kökteki `ROADMAP.md`, `STATUS.md` ve ilgili son `audit/` / `staj/` kaydını oku. Test iddiası için `VALIDATION.md` ve ilgili kanıt paketini karşılaştır; eski test sayılarını yeni koşu gibi sunma.
- `ROADMAP.md` tek ana iş planıdır. Silme, yeniden yazma veya specialist planıyla değiştirme. `tools/dom-xss-analyzer/ROADMAP-LEGACY.md` ve tarihsel raporlar güncel kabul kanıtı değildir.
- Devamlılık sohbet belleğine dayanmaz: ROADMAP hedef/kabul ölçütlerini, STATUS tek güncel devam noktasını (son doğrulanan iş, sahipler, engeller, sonraki adım), VALIDATION komut/ortam/sonuç ve test edilen commit veya kaynak hash'lerini tutar. Audit tarihsel kanıttır; eski yetki ve görev durumları güncel talimat değildir. Yeni uzmana bağlamı bu dosyalardan aktar.
- Specialist görevlendirmeden önce `docs/AGENT-WORKFLOW.md` oku. Mevcut mimari ve başlangıç analizi için `audit/2026-10-06-agent-review/README.md` oku; daha sonraki kodla değişmiş olabileceğini doğrula.
- Kanıt/rapor değişikliklerinde `tools/dom-xss-analyzer/EVIDENCE-CONTRACT.md`, `HTTP-EVIDENCE.md` ve `BROWSER-PROOF.md`; auth değişikliklerinde `SESSION-CONTRACT.md` ve `AUTH-LIMITS.md` okunur.

## Yetki ve mevcut aşama

- 11 Ekim 2026 güncel kullanıcı talimatı: uygulanabilir roadmap işlerini geliştir; her anlamlı, doğrulanmış teslimde koordinatör bu işe ait kod/test, gerekli kalıcı agent yapılandırmaları ve ilerleme belgelerini birlikte commit ve push edebilir. İlgisiz kullanıcı değişikliklerini stage etme, force push yapma. Uzak commit'i doğrulamadan GitHub'a kaydedildi deme; uzak CI ile yerel testi ayrı raporla. Token/parola/.env/kişisel veri/yerel DB/ham sohbet/cache/gereksiz büyük çıktı gönderme; paylaşılacak kanıtı kontrol et. Bu yetki eski Git yasaklarının yerini alır; dış hedef, veri silme ve arka plan otomasyonu yetkisi vermez.

- Kullanıcı 8 Ekim 2026'da güncel ROADMAP'in uygulanabilir açık maddeleri için geliştirme onayını genişletti. Beş native uzman kendi alanlarında uygulama kodu ve test yazar; madde başına yeniden onay istenmez. Mevcut veriler korunur. Uzmanlar bağımsız Git teslimi yapmaz; koordinatörün Git yetkisi yukarıdadır. Diğer dış yayın, veri silme ve otomatik başlangıç/arka plan görevi yetkili değildir.
- Testler yalnız kullanıcının kendi uygulamalarında ve açıkça izinli local/Docker/CTF laboratuvarlarında yapılır. Bir URL'nin belgede bulunması yetki değildir. Dış hedef, disclosure ve mesaj gönderimi için ayrıca açık yetki gerekir.
- Mevcut proje Python CLI/rapor araçlarıdır. Yeni dashboard, API, ORM, migration framework veya queue sırf bir uzman rolünün adında geçtiği için eklenmez.

## Koordinasyon ve kalite

- Bu sohbetin ana agent'ı koordinatördür. Specialist'ler roadmap görevine bağlı, sınırları belirli işler alır. Aktif araç gerçekten destekliyorsa gerçek sub-agent çağır; yalnız belge yazıp çalışan agent kuruldu deme.
- `.codex/agents/` tanımlarını koru. Kalıcı configuration varlığı, geçici sub-agent'ın talimat dosyasını okuması ve native custom-agent invocation ayrı kanıtlardır. Invocation doğrulanmadığında bunu açıkça belirt; ayrıntılı durum `docs/AGENT-WORKFLOW.md` içindedir.
- 7 Ekim 2026 oturumunda beş rol `agent_type` ile native çağrıldı; kayıt `audit/2026-10-07-r4-native/README.md` içindedir. Görevlendirmede native rol seçilir; başarısız çağrı sessizce generic çalışanla değiştirilmez. Dosya sahipliği ve gerçek runtime izinleri ayrıca kontrol edilir; yapılandırma değişikliği mevcut çalışana otomatik uygulanmış sayılmaz.
- Onaylı geliştirmede en fazla iki uzman aynı anda çalışır; diğer işler sırada bekler. Koordinatör her göreve dosya sahipliği ve kabul ölçütü atar; iki agent aynı dosyayı eşzamanlı düzenlemez. Uzmanlar yalnız son inceleme için kullanılmaz. Koordinatör bütün değişiklikleri ve test oracle'larını inceler, eksikleri uzmana döndürür, entegrasyonu doğrular. Ortak şema ve roadmap koordinatöre aittir. Her anlamlı teslimde STATUS güncellenir; yalnız sohbet sonu beklenmez.
- Engellenen görev gerekçesiyle kaydedilir ve bağımsız işlere devam edilir. Kesinti/limit yaklaşırken tamamlanan, devam eden ve sıradaki işler audit kaydına yazılır; duran çalışma arka planda sürüyormuş gibi sunulmaz.
- Bulgular dosya:satır, kanıt türü, beklenen/gözlenen davranış ve roadmap kimliği içerir. Kod incelemesi, yeniden üretilmiş hata ve doğrulanmamış şüphe ayrı belirtilir.
- Reflection, sink gözlemi, callback, browser execution ve güvenlik açığı triage'ı birbirine yükseltilmez. Test/payload sayısı ürün başarısı değildir.
- Onaylı düzeltmede önce kök neden, sonra anlamlı regresyon ve ilgili fixture kanıtı. Hata/timeout/skip başarı veya güvenli sonuç sayılmaz. Ham token, cookie, API key ve hassas request/body paylaşım belgelerine konmaz.
- Mevcut verileri koru; migration, Docker volume silme veya veri etkili refactor öncesinde risk ve geri dönüş planı çıkar. Gereksiz refactor yapma.
- Tamamlanma yalnız kabul kanıtıyla işaretlenir. Koddan bağımsız analiz tesliminde testler yeniden koşulmuş gibi yazılmaz.
