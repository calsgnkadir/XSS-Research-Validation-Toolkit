# 8 Ekim 2026 — onaylı roadmap geliştirmesi

Başlangıç HEAD: e17df59; çalışma ağacı temiz. Mevcut depo kullanılıyor.
Kullanıcı geliştirme yetkisini genişletti; commit/push/yayın/veri silme yasak.
Beş TOML workspace-write ve kod/test geliştirme talimatıyla güncellendi.
Kalıcı yapılandırma, native çağrı ve gerçek araç başarısı ayrı kaydedilir.

## Görev sırası ve özel dosya sahipliği

En fazla iki uzman çalışır. Bu liste ROADMAP'in yerine geçmez.

| Sıra | Rol / roadmap | Dosyalar | Kabul / durum |
|---|---|---|---|
| 1 | Engine / R4 | bench/run.py; yeni bench/proof_worker.py, bench/process_control.py; bench/test_runner_isolation.py | Sert süre sınırı, süreç temizliği, malformed dönüş izolasyonu; atanacak |
| 1 | Security / R8 | dxa.py, test_dxa.py, yeni test_static_context.py, examples/safe.py; STATIC-LIMITS.md | identity ve mixed sanitizer taint korunur, dosya kapsamı ayrılır, template uzantıları ve güvenli fixture; atanacak |
| 2 | Storage / R9 | dxa_callback.py, callback testleri, bench/targets Compose ve özel operasyon testi | Erişim/body/limit/CORS/SQLite hata sınırları; yerel portlar, veri koruma; sırada |
| 2 | Report / R6,K05,R9 | dxa_evidence.py, yeni test_report_safety.py | Aynı JSON/HTML kanıtı, güvenli çıktı ve mahremiyet karşı örnekleri; sırada |
| 3 | QA / R4,R5,R9 | Bağımsız yeni entegrasyon testleri, fixture/CI; özel sahiplik atamada kesinleşir | Gerçek subprocess/timeout oracle, clean lab, CI hata ayrımı; sırada |

Koordinatör: yapılandırma, AGENTS/workflow, ortak belgeler, tüm diff incelemesi,
test kanıtları ve entegrasyon. Başarı henüz ilan edilmedi; eski 681 sonucu yeni
koşu değildir. Sonraki işler teslimlere ve mevcut roadmap bağımlılıklarına göre
atanacak. Uzak CI bu oturumda doğrulanmış değildir.

## Gerçek çağrı ve ilk bulgular

- `scanner_engine_specialist` → `/root/r4_runner_implementation`, native çağrı
  başarılı; uygulama dosyası yazma başarılı, test başlatımı WindowsApps Python
  erişim engeliyle durdu. Testler koordinatörün izinli runtime'ında koşulacak.
- `xss_security_researcher` → `/root/r8_static_implementation`, native çağrı
  başarılı; yeni test dosyası yazma başarılı. Koordinatörün izinli gerçek red
  koşusu: **13 failed, 3 passed**. `r8-before-summary.json`; ham XML ignored
  `.dxa/2026-10-08-development/r8-before.xml` içinde. Uygulama devam ediyor.
- `docker info` salt okuma kontrolü sandbox dışında da başarısız: Docker Desktop
  Linux daemon pipe bulunamadı. Container başlatılmadı. R4 gerçek ürün/lab kabulü
  için daemon ve uygulama bootstrap kanıtı engeli var; Compose dosyasının bulunması
  çalışan hedef demek değildir.
- Ayar biçimi [resmî OpenAI kaynağı](https://learn.chatgpt.com/docs/agent-configuration/subagents)
  ile karşılaştırıldı. Desteklenen `sandbox_mode` gerçek süreç yetkisi iddiası
  yerine geçmez. Model veya global yetki değiştirilmedi.
