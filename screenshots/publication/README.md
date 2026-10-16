# Publication-safe screenshot copies

These PNGs are redacted derivatives of the adjacent historical JPEG originals.
Opaque black blocks mask the visible account email, cookie values, token/password
fields, and response body material that is not required to show the limited
observation. The originals remain untouched. Redacted areas are intentionally
not recoverable from these copies.

| Original | Shareable copy | Redaction |
|---|---|---|
| `01-scoreboard-solved-challenges.jpg` | [PNG](01-scoreboard-solved-challenges.png) | No visible credential fields found; copy retained as-is. |
| `02-profile-page-csp-fields.jpg` | [PNG](02-profile-page-csp-fields.png) | Email/account field. |
| `03-burp-repeater-injection-testing.jpg` | [PNG](03-burp-repeater-injection-testing.png) | Cookie area, response body and validator/hash fields. The test header remains visible. |
| `04-burp-http-history.jpg` | [PNG](04-burp-http-history.png) | No visible credentials found; copy retained as-is. |
| `05-last-login-ip-page.jpg` | [PNG](05-last-login-ip-page.png) | No visible credentials found; copy retained as-is. |
| `06-header-xss-channel-verified.jpg` | [PNG](06-header-xss-channel-verified.png) | Cookie area, ETag/hash metadata, and JSON response body. The benign test header remains visible. |
| `07-header-xss-sanitizer-detected.jpg` | [PNG](07-header-xss-sanitizer-detected.png) | Cookie area, ETag/hash metadata, and JSON response body. The test header remains visible. |
| `08-header-xss-filter-mapping.jpg` | [PNG](08-header-xss-filter-mapping.png) | Cookie area, ETag/hash metadata, and JSON response body. The test header remains visible. |

These copies preserve UI/request context only. Redaction removes response values
that could expose credentials or account data, so the copies cannot independently
establish the original response result. The original screenshot and writeup remain
historical evidence; proof level and missing artifacts are recorded in the
[K evidence inventory](../../audit/2026-10-17-k-evidence/README.md).
