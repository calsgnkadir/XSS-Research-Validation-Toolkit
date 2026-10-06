# R3 güncel browser kanıtı — 6 Ekim 2026

Bu klasör, R3 kod değişikliklerinden sonra gerçek Chrome ile üretilen güncel
tek komut demosudur. `dxaprove --demo` sonucu `execution-observed` döndü ve
JSON içindeki `source_sha256`, o anki `tools/dom-xss-analyzer/dxaprove.py`
dosyasının SHA-256 değeriyle eşleşir.

- [Demo JSON](demo/result.json)
- [Demo HTML](demo/result.html)
- Browser: Chrome 154.0.8037.98, Playwright 1.63.0
- Kapsam: loopback, tek origin, tek paylaşılan hesap, açık güvenlik açığı doğrulaması yok

R3 odaklı regresyon koşusu 21/21 geçti. Bu koşu direct-eval lexical scope,
SPA route budget ve allowlist edilmiş CSRF header aktarımını kapsar.
WebSocket/genel ağ sandboxı kabul kapsamı dışındadır; route-websocket denemesi
Playwright context kapanışında kilitlendiği için güvenilir test olarak tutulmadı.
