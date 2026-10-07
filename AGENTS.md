# Proje agent talimatları

## Başlangıç ve kaynaklar

- Bu deponun kökünü `git rev-parse --show-toplevel` ve çalışma ağacını `git status --short` ile doğrula. Güncel çalışma kopyası varken ZIP'ten ikinci proje üretme. Kullanıcı değişikliklerini koru.
- Her işe başlamadan kökteki `ROADMAP.md`, `STATUS.md` ve ilgili son `audit/` / `staj/` kaydını oku. Test iddiası için `VALIDATION.md` ve ilgili kanıt paketini karşılaştır; eski test sayılarını yeni koşu gibi sunma.
- `ROADMAP.md` tek ana iş planıdır. Silme, yeniden yazma veya specialist planıyla değiştirme. `tools/dom-xss-analyzer/ROADMAP-LEGACY.md` ve tarihsel raporlar güncel kabul kanıtı değildir.
- Specialist görevlendirmeden önce `docs/AGENT-WORKFLOW.md` oku. Mevcut mimari ve başlangıç analizi için `audit/2026-10-06-agent-review/README.md` oku; daha sonraki kodla değişmiş olabileceğini doğrula.
- Kanıt/rapor değişikliklerinde `tools/dom-xss-analyzer/EVIDENCE-CONTRACT.md`, `HTTP-EVIDENCE.md` ve `BROWSER-PROOF.md`; auth değişikliklerinde `SESSION-CONTRACT.md` ve `AUTH-LIMITS.md` okunur.

## Yetki ve mevcut aşama

- Kullanıcı 6 Ekim 2026'da sınırlı geliştirme onayı verdi: R9 yerel scope kontrolü, R3 eval karşı örneği ve R4 adapter/runner entegrasyonu bağımlılık sırasıyla uygulanabilir. Bu sınır dışındaki uygulama, CI, Docker veya veritabanı değişikliği için yeniden onay gerekir. Otomatik başlangıç/arka plan görevi kurulmaz.
- Testler yalnız kullanıcının kendi uygulamalarında ve açıkça izinli local/Docker/CTF laboratuvarlarında yapılır. Bir URL'nin belgede bulunması yetki değildir. Dış hedef, disclosure ve mesaj gönderimi için ayrıca açık yetki gerekir.
- Mevcut proje Python CLI/rapor araçlarıdır. Yeni dashboard, API, ORM, migration framework veya queue sırf bir uzman rolünün adında geçtiği için eklenmez.

## Koordinasyon ve kalite

- Bu sohbetin ana agent'ı koordinatördür. Specialist'ler roadmap görevine bağlı, sınırları belirli işler alır. Aktif araç gerçekten destekliyorsa gerçek sub-agent çağır; yalnız belge yazıp çalışan agent kuruldu deme.
- `.codex/agents/` tanımlarını koru. Kalıcı configuration varlığı, geçici sub-agent'ın talimat dosyasını okuması ve native custom-agent invocation ayrı kanıtlardır. Invocation doğrulanmadığında bunu açıkça belirt; ayrıntılı durum `docs/AGENT-WORKFLOW.md` içindedir.
- 7 Ekim 2026 oturumunda beş rol `agent_type` ile native çağrıldı; kayıt `audit/2026-10-07-r4-native/README.md` içindedir. Görevlendirmede native rol seçilir; başarısız çağrı sessizce generic çalışanla değiştirilmez. Dosya sahipliği ve gerçek runtime izinleri ayrıca kontrol edilir; yapılandırma değişikliği mevcut çalışana otomatik uygulanmış sayılmaz.
- Analiz varsayılanı salt okumadır. Geliştirme onayı sonrası koordinatör dosya sahipliğini belirler; iki agent aynı dosyayı eşzamanlı düzenlemez. Ortak şema, roadmap, birleştirme ve Git teslimi koordinatöre aittir.
- Bulgular dosya:satır, kanıt türü, beklenen/gözlenen davranış ve roadmap kimliği içerir. Kod incelemesi, yeniden üretilmiş hata ve doğrulanmamış şüphe ayrı belirtilir.
- Reflection, sink gözlemi, callback, browser execution ve güvenlik açığı triage'ı birbirine yükseltilmez. Test/payload sayısı ürün başarısı değildir.
- Onaylı düzeltmede önce kök neden, sonra anlamlı regresyon ve ilgili fixture kanıtı. Hata/timeout/skip başarı veya güvenli sonuç sayılmaz. Ham token, cookie, API key ve hassas request/body paylaşım belgelerine konmaz.
- Mevcut verileri koru; migration, Docker volume silme veya veri etkili refactor öncesinde risk ve geri dönüş planı çıkar. Gereksiz refactor yapma.
- Tamamlanma yalnız kabul kanıtıyla işaretlenir. Koddan bağımsız analiz tesliminde testler yeniden koşulmuş gibi yazılmaz.
