# R2 auth guard doğrulaması — 5 Ekim 2026

Kabul: auth akışında HTTP hata durdurma, geçersiz/eksik token reddi,
önceden mevcut cookie'nin tek başına başarı sayılmaması ve form login
başarısızlığında CLI exit 2 + ortak hata raporu.

`test_auth_guards.py` 15 yeni negatif/regresyon kontrolü içerir; mevcut
`test_flow.py` cookie/bearer pozitifleriyle odaklı koşu **49 passed**.
İlk tam koşu **495 passed, 1 failed, 36 skipped**: stored fixture başarılı
login sonrası olmayan dashboard'a yönleniyordu. Oturum kontrollü dashboard
eklendi; hata yanıtını reddeden üretim kontrolü korundu.

Son tam koşunun [logu](pytest.log) ve [JUnit kaydı](pytest.xml) bu klasördedir.
Komut: `python -m pytest -q -ra -p no:cacheprovider --tb=short --junitxml=audit/2026-10-05-r2-auth/pytest.xml`
Paylaşım kopyasında yerel kök `[workspace]`, hostname `[host]` ile maskelenir.
İlk tam koşunun ham çıktısı yerel xss-audit alanında korunur.

[Kapsam ve kalan işler](../../tools/dom-xss-analyzer/AUTH-LIMITS.md).
R2 tamamlanmadı; hedefe özel oturum/rol kontrolü, rate ve CSRF hâlâ açık.
