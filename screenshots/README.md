# Screenshot evidence index

These captures are historical screenshots from an OWASP Juice Shop instance
described by the project records as a local authorized lab. A screenshot proves
only what is visible in that capture; it does not by itself prove a vulnerability,
JavaScript execution, authorization boundary, or complete filter behavior.

The files at this directory level are preserved originals. Some show credential
or account fields. Use the [publication-safe copies](publication/README.md) for
sharing; their redactions are opaque and the originals have not been modified.

| Capture | Visible source / control | Observation supported by pixels | Evidence level and limit |
|---|---|---|---|
| [01 scoreboard](01-scoreboard-solved-challenges.jpg) ([shareable](publication/01-scoreboard-solved-challenges.png)) | Juice Shop challenge scoreboard | Some solved-challenge banners are visible, including Login Admin, Password Strength, and View Basket. | Challenge UI only. It does not preserve request/response, exact payload, SQL result, JWT token, or two-user authorization comparison. |
| [02 profile](02-profile-page-csp-fields.jpg) ([shareable](publication/02-profile-page-csp-fields.png)) | Profile form: username and image URL inputs | The input fields are present in the UI. | UI/source-location context only. No CSP response header, policy diff, browser execution, or bypass proof is visible. |
| [03 Repeater](03-burp-repeater-injection-testing.jpg) ([shareable](publication/03-burp-repeater-injection-testing.png)) | Burp Repeater request to the local Juice Shop | The request includes a `True-Client-IP` test value and the original response JSON shows a corresponding `lastLoginIp` value. | Header processing / reflection in a JSON response only. The shareable copy masks cookie/account data and response body; it cannot independently verify the displayed response value. This is not browser execution evidence. |
| [04 HTTP history](04-burp-http-history.jpg) ([shareable](publication/04-burp-http-history.png)) | Burp Proxy history | Local request paths and status codes are listed. | Traffic-navigation context only; no response body, proof level, or security impact established. |
| [05 last-login page](05-last-login-ip-page.jpg) ([shareable](publication/05-last-login-ip-page.png)) | Juice Shop Last Login IP page | The page location and an empty IP display are visible. | UI context only; no injected value or execution is shown. |
| [06 benign header](06-header-xss-channel-verified.jpg) ([shareable](publication/06-header-xss-channel-verified.png)) | `True-Client-IP: 1.2.3.4` request and JSON response | The original JSON response displays that benign value in `lastLoginIp`. | Header accepted and reflected into JSON. No HTML/browser execution shown. The shareable copy retains the request header and masks cookies/account response fields; it cannot independently verify the response value. |
| [07 iframe-shaped value](07-header-xss-sanitizer-detected.jpg) ([shareable](publication/07-header-xss-sanitizer-detected.png)) | Header request and JSON response | The original response field is empty for the displayed input. | One observed input/output pair only. It supports neither a complete sanitizer model nor a bypass. The shareable copy omits response body. |
| [08 image-shaped value](08-header-xss-filter-mapping.jpg) ([shareable](publication/08-header-xss-filter-mapping.png)) | Header request and JSON response | The original response field is empty for the displayed input. | One observed input/output pair only; not an exhaustive allowlist/filter map and not execution evidence. The shareable copy omits response body. |
| [Static report preview](../tools/dom-xss-analyzer/report-preview.png) | Synthetic source-analysis report example | The preview shows nine rows and a summary of five high-confidence rows; its footer calls for manual confirmation. | Renderer UI only. Static candidates do not establish runtime execution, vulnerability, or target impact. No account credentials are visible. |

The scoreboard/writeup narratives are author-recorded historical results. The
repository does not include a matching raw SQLi request/response, a JWT
`alg:none` request/response, or a two-account BOLA A/B pair. See the
[K03 evidence inventory](../audit/2026-10-17-k-evidence/README.md) for those
gaps and the supporting artifact links.
