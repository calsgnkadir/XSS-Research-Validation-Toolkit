# R2 kabul matrisi — 6 Ekim 2026

**R2 HTTP kabul kapsamı tamam. 526 passed, 36 skipped, 1 warning; 112.13 saniye.**
Atlamalar eski browser binary keşfi, uyarı benchmark utcnow kullanımıdır.

HTTP oturumu için kabul kapsamı aşağıdadır. Browser oturum aktarımı R3,
genel origin/redirect güvenliği R9 olarak kalır. Ana sözleşme:
[SESSION-CONTRACT.md](../../tools/dom-xss-analyzer/SESSION-CONTRACT.md).

| Kabul maddesi | Uygulama ve kanıt |
|---|---|
| JSON round-trip ve istek başına Content-Type | `test_json_transport.py`; önceki teslim korunur |
| 401/403, eksik token, eski cookie | `test_auth_guards.py`; 15 guard regresyonu |
| Hedefe özel oturum kontrolü, rol kaydı | `--auth-check`; `test_target_session_contract`, `test_auth_flow_then_target_identity_check`, `test_cli_failed_session_check_stops_scan`; raporda ayrı check durumu ve operatör rol etiketi |
| Fractional rate ve geçersiz rate | `test_fractional_rate_progresses_with_fake_clock`, bucket/CLI negatifleri; gerçek uzun uyku yok; CLI 0=sınırsız |
| CSRF refresh+submit, stored submit+read | Ortak yeniden girişli oturum kilidi; 8 paralel tek kullanımlık header denemesi, overwritten-canary stored/stored-auto testleri, flow CSRF ve eksik token negatifleri |
| Hata/timeout/limit ile bulgusuzluk ayrımı | 401/403/429/500 olayları, timeout error, CSRF ve auth-check hata raporları |
| Zorunlu regresyon | Ana pytest ve CI `Required R1 and R2 negative controls` adımı; continue-on-error yok |

Yerel tam koşunun [logu](pytest.log) ve [JUnit kaydı](pytest.xml) bu klasördedir.
Komut: `python -m pytest -q -ra -p no:cacheprovider --tb=short --junitxml=audit/2026-10-06-r2/pytest.xml`.
Python 3.12.14; Windows. Yerel kök ve makine adı paylaşım kopyasında maskelenir.
GitHub CI yapılandırması güncellendi; uzaktaki CI başarısı bu yerel sonuçtan çıkarılmaz.

Önceki tam koşu 523 passed/1 failed/36 skipped idi: CSRF'siz guestbook
adapter'ı varsayılan zorunlu token alanını kullanıyordu. Hedef tanımına açık
`csrf_field: ""` kondu; tüm hedeflerde CSRF kapatılmadı. Önceki hız testi de
paylaşılan oturumun yeni sıralama sözleşmesine uygun şekilde gerçek örtüşen
istek sayısını ölçen kontrole dönüştürüldü.

Sınırlar: `session_check=passed`, yalnız kullanıcı tarafından tanımlanmış
JSON sözleşmesinin o anda eşleşmesidir; genel yetki analizi değildir.
`role_verified` kanıtsız yükseltilmez. Kontrol isteğe bağlıdır; kullanılmazsa
not-requested görünür. Tek paylaşılan HTTP oturumu sıralıdır, paralel hız artışı
iddiası yoktur. Stored-auto sayfa sayısı canary başına toplamdır. R3/R4/R9
ve bağımsız temiz R5 tekrarı bu teslimle kapanmaz.
