# Dosya–görev eşlemesi

Orijinal ZIP: 76/76 dosya. Güncel görev durumları ve kabul ölçütleri [ana roadmap](ROADMAP.md) içindedir. Bu tablo ikinci bir durum kaynağı değildir. “Koru” dosyanın kusursuz olduğunu değil, denetimde ayrı düzeltme gerektiren bulgu olmadığını belirtir.

| # | Dosya | Takip edilen görev |
|---:|---|---|
| 1 | [.github/workflows/ci.yml](.github/workflows/ci.yml) | R4, R9 |
| 2 | [.gitignore](.gitignore) | R4, R9 — benchmark artifact/history saklama |
| 3 | [LICENSE](LICENSE) | R6, P04 — koru; lisans düzenlemesi gerektiren bulgu yok |
| 4 | [README.md](README.md) | C13, P01, P03, R0 |
| 5 | [bench/README.md](bench/README.md) | R4, R9 |
| 6 | [bench/mock_target.py](bench/mock_target.py) | R4, R9 |
| 7 | [bench/run.py](bench/run.py) | R4, R9 |
| 8 | [bench/targets.json](bench/targets.json) | R4, R9 |
| 9 | [bench/targets/bludit/docker-compose.yml](bench/targets/bludit/docker-compose.yml) | R4, R9 |
| 10 | [bench/targets/dvwa/docker-compose.yml](bench/targets/dvwa/docker-compose.yml) | R4, R9 |
| 11 | [bench/targets/webgoat/docker-compose.yml](bench/targets/webgoat/docker-compose.yml) | R4, R9 |
| 12 | [bench/test_bench.py](bench/test_bench.py) | R4, R9 |
| 13 | [defense/README.md](defense/README.md) | K04 |
| 14 | [methodology.md](methodology.md) | C12, K04 |
| 15 | [reports/2026-09-26-v310-live/A-hotel-platform-25shape.html](reports/2026-09-26-v310-live/A-hotel-platform-25shape.html) | K05 — ham tarihsel çıktı korunur |
| 16 | [reports/2026-09-26-v310-live/B1-mahrem-static.html](reports/2026-09-26-v310-live/B1-mahrem-static.html) | K05 — ham tarihsel çıktı korunur |
| 17 | [reports/2026-09-26-v310-live/B2-mahrem-reflected.html](reports/2026-09-26-v310-live/B2-mahrem-reflected.html) | K05 — ham tarihsel çıktı korunur |
| 18 | [reports/2026-09-26-v310-live/C1-wallet-reflected.html](reports/2026-09-26-v310-live/C1-wallet-reflected.html) | K05 — ham tarihsel çıktı korunur |
| 19 | [reports/2026-09-26-v310-live/C2-wallet-stored-25shape.html](reports/2026-09-26-v310-live/C2-wallet-stored-25shape.html) | K05 — ham tarihsel çıktı korunur |
| 20 | [reports/2026-09-26-v310-live/D1-bludit-body-breakout-req.html](reports/2026-09-26-v310-live/D1-bludit-body-breakout-req.html) | K05 — ham tarihsel çıktı korunur |
| 21 | [reports/2026-09-26-v310-live/D2-bludit-title-breakout-EXECUTABLE.html](reports/2026-09-26-v310-live/D2-bludit-title-breakout-EXECUTABLE.html) | K05 — ham tarihsel çıktı korunur |
| 22 | [reports/2026-09-26-v310-live/README.md](reports/2026-09-26-v310-live/README.md) | K05, C11, C13 |
| 23 | [research/2026-09-27-cve-hunt-sprint/README.md](research/2026-09-27-cve-hunt-sprint/README.md) | A03, A04, A05, R4 |
| 24 | [research/README.md](research/README.md) | A01, A02, A03, A05 |
| 25 | [screenshots/01-scoreboard-solved-challenges.jpg](screenshots/01-scoreboard-solved-challenges.jpg) | K02 |
| 26 | [screenshots/02-profile-page-csp-fields.jpg](screenshots/02-profile-page-csp-fields.jpg) | K02 |
| 27 | [screenshots/03-burp-repeater-injection-testing.jpg](screenshots/03-burp-repeater-injection-testing.jpg) | K02 |
| 28 | [screenshots/04-burp-http-history.jpg](screenshots/04-burp-http-history.jpg) | K02 |
| 29 | [screenshots/05-last-login-ip-page.jpg](screenshots/05-last-login-ip-page.jpg) | K02 |
| 30 | [screenshots/06-header-xss-channel-verified.jpg](screenshots/06-header-xss-channel-verified.jpg) | K02 |
| 31 | [screenshots/07-header-xss-sanitizer-detected.jpg](screenshots/07-header-xss-sanitizer-detected.jpg) | K02 |
| 32 | [screenshots/08-header-xss-filter-mapping.jpg](screenshots/08-header-xss-filter-mapping.jpg) | K02 |
| 33 | [screenshots/README.md](screenshots/README.md) | K02, C13 |
| 34 | [tools/dom-xss-analyzer/README.md](tools/dom-xss-analyzer/README.md) | C13, R6, P04 |
| 35 | [tools/dom-xss-analyzer/ROADMAP.md](tools/dom-xss-analyzer/ROADMAP.md) | R0, C13 — ana roadmap yönlendirmesi |
| 36 | [tools/dom-xss-analyzer/conftest.py](tools/dom-xss-analyzer/conftest.py) | R4 — test altyapısı; mevcut dosya korunur |
| 37 | [tools/dom-xss-analyzer/dxa.py](tools/dom-xss-analyzer/dxa.py) | R8 |
| 38 | [tools/dom-xss-analyzer/dxa2dyn.py](tools/dom-xss-analyzer/dxa2dyn.py) | R8, R9 — heuristik eşleme sınırı |
| 39 | [tools/dom-xss-analyzer/dxa_callback.py](tools/dom-xss-analyzer/dxa_callback.py) | R1, R9 |
| 40 | [tools/dom-xss-analyzer/dxadom.py](tools/dom-xss-analyzer/dxadom.py) | R3, R9 |
| 41 | [tools/dom-xss-analyzer/dxadyn-report-preview.html](tools/dom-xss-analyzer/dxadyn-report-preview.html) | K05 — tarihsel çıktı korunur |
| 42 | [tools/dom-xss-analyzer/dxadyn.py](tools/dom-xss-analyzer/dxadyn.py) | R1, R2, R3, R9, K05 |
| 43 | [tools/dom-xss-analyzer/examples/flows/cookie-login.json](tools/dom-xss-analyzer/examples/flows/cookie-login.json) | R1, R2, C13 — gerçek hedef config değil, örnek şablon |
| 44 | [tools/dom-xss-analyzer/examples/flows/jwt-login.json](tools/dom-xss-analyzer/examples/flows/jwt-login.json) | R1, R2, C13 — gerçek hedef config değil, örnek şablon |
| 45 | [tools/dom-xss-analyzer/examples/flows/register-comment-verify.json](tools/dom-xss-analyzer/examples/flows/register-comment-verify.json) | R1, R2, C13 — gerçek hedef config değil, örnek şablon |
| 46 | [tools/dom-xss-analyzer/examples/safe.java](tools/dom-xss-analyzer/examples/safe.java) | R8, R4 |
| 47 | [tools/dom-xss-analyzer/examples/safe.js](tools/dom-xss-analyzer/examples/safe.js) | R8, R4 |
| 48 | [tools/dom-xss-analyzer/examples/safe.php](tools/dom-xss-analyzer/examples/safe.php) | R8, R4 |
| 49 | [tools/dom-xss-analyzer/examples/safe.py](tools/dom-xss-analyzer/examples/safe.py) | R8, R4 |
| 50 | [tools/dom-xss-analyzer/examples/vulnerable.cs](tools/dom-xss-analyzer/examples/vulnerable.cs) | R8, R4 |
| 51 | [tools/dom-xss-analyzer/examples/vulnerable.cshtml](tools/dom-xss-analyzer/examples/vulnerable.cshtml) | R8, R4 |
| 52 | [tools/dom-xss-analyzer/examples/vulnerable.java](tools/dom-xss-analyzer/examples/vulnerable.java) | R8, R4 |
| 53 | [tools/dom-xss-analyzer/examples/vulnerable.js](tools/dom-xss-analyzer/examples/vulnerable.js) | R8, R4 |
| 54 | [tools/dom-xss-analyzer/examples/vulnerable.php](tools/dom-xss-analyzer/examples/vulnerable.php) | R8, R4 |
| 55 | [tools/dom-xss-analyzer/examples/vulnerable.py](tools/dom-xss-analyzer/examples/vulnerable.py) | R8, R4 |
| 56 | [tools/dom-xss-analyzer/report-preview.png](tools/dom-xss-analyzer/report-preview.png) | K02, K05 — tarihsel görsel korunur |
| 57 | [tools/dom-xss-analyzer/test_blind_correlation.py](tools/dom-xss-analyzer/test_blind_correlation.py) | R1, K05 |
| 58 | [tools/dom-xss-analyzer/test_csrf.py](tools/dom-xss-analyzer/test_csrf.py) | R2 |
| 59 | [tools/dom-xss-analyzer/test_dxa.py](tools/dom-xss-analyzer/test_dxa.py) | R8 |
| 60 | [tools/dom-xss-analyzer/test_dxa2dyn.py](tools/dom-xss-analyzer/test_dxa2dyn.py) | R8, R9 |
| 61 | [tools/dom-xss-analyzer/test_dxa_callback.py](tools/dom-xss-analyzer/test_dxa_callback.py) | R1, R9 |
| 62 | [tools/dom-xss-analyzer/test_dxadom.py](tools/dom-xss-analyzer/test_dxadom.py) | R3, R4 |
| 63 | [tools/dom-xss-analyzer/test_dxadyn.py](tools/dom-xss-analyzer/test_dxadyn.py) | R1, R2, R9 |
| 64 | [tools/dom-xss-analyzer/test_flow.py](tools/dom-xss-analyzer/test_flow.py) | R1, R2 |
| 65 | [writeups/01-filtering-is-not-protection.md](writeups/01-filtering-is-not-protection.md) | C01, S02 |
| 66 | [writeups/02-dom-xss-assessment-react-spa.md](writeups/02-dom-xss-assessment-react-spa.md) | C02, S02 |
| 67 | [writeups/03-sql-injection.md](writeups/03-sql-injection.md) | C03, S02 |
| 68 | [writeups/04-jwt-forgery.md](writeups/04-jwt-forgery.md) | C04, S02 |
| 69 | [writeups/05-idor-bola.md](writeups/05-idor-bola.md) | C05, S02 |
| 70 | [writeups/06-building-an-xss-bot.md](writeups/06-building-an-xss-bot.md) | C06, S02 |
| 71 | [writeups/07-teaching-the-bot-to-log-in.md](writeups/07-teaching-the-bot-to-log-in.md) | C07, S02 |
| 72 | [writeups/08-what-does-not-shout-matters.md](writeups/08-what-does-not-shout-matters.md) | C08, S02 |
| 73 | [writeups/09-three-high-to-one-a-precision-journey.md](writeups/09-three-high-to-one-a-precision-journey.md) | C09, S02 |
| 74 | [writeups/10-one-shape-was-never-enough.md](writeups/10-one-shape-was-never-enough.md) | C10, S02 |
| 75 | [writeups/11-four-targets-one-afternoon.md](writeups/11-four-targets-one-afternoon.md) | C11, S02 |
| 76 | [writeups/README.md](writeups/README.md) | C13, P01, P02, S02 |

Yeni geliştirme belgeleri: ROADMAP/STATUS/CHANGELOG/VALIDATION/HISTORY-NOTES → R0/C13/P01/S01; yeni dialog regresyonu → R1; README-LEGACY ve ROADMAP-LEGACY → tarihsel arşiv, güncel tamamlanma kaynağı değil.
