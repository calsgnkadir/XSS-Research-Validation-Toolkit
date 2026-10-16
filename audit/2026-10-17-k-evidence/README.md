# K02–K05 evidence inventory — 17 October 2026

Scope: evidence inventory, screenshot sharing copies, defense guidance, and
report-label corrections. This is a document/artifact review; it does not rerun
Juice Shop, the historical scanner targets, or a vulnerability reproduction.
No raw screenshot or historical HTML report was modified.

## K02 — screenshots 01–08 and report preview

The [screenshot index](../../screenshots/README.md) records source/input,
visible filter or challenge state, and proof level per capture. The original
JPEGs are retained. [Publication-safe PNGs](../../screenshots/publication/README.md)
mask account email, cookies, token/password values and unneeded response/ETag
material with opaque black rectangles. As a result, the PNGs are context copies,
not independent proof of hidden response values.

| Original | SHA-256 | Shareable copy | SHA-256 |
|---|---|---|---|
| `01-scoreboard-solved-challenges.jpg` | `89210ca669c4bd1edc7227a37c41e90c277d13676b740ae1b3531d34269f54fb` | `01-scoreboard-solved-challenges.png` | `25fbf760d3090877c4566dff3b2a687d3e77ea2d3c4044293e5360ea4554411e` |
| `02-profile-page-csp-fields.jpg` | `68a610ccbafa0dec74c43a1bd62eb63085748beb0eb9561ac7ebcc0a3e955fc0` | `02-profile-page-csp-fields.png` | `a6cda2cdaf91871dce4cef933c8def8ce6ad1e8d708a808be70c46fb33984b64` |
| `03-burp-repeater-injection-testing.jpg` | `c71b46193aafede0e5f8e8f7c889bc1758ae0798d4cca69db8be9617c9b9ea6c` | `03-burp-repeater-injection-testing.png` | `573aaad963ba271aaa41ce3a3657afc88d48b23eb5eb9cc776f3db1d388a1383` |
| `04-burp-http-history.jpg` | `770b8ef0b6a278df3899ae2599847c0e034dc2f40194772b5b431933b543d79e` | `04-burp-http-history.png` | `324c0bffc257fe1772a78a59ade0ad809cdadccffc1371c7d441222709ed8301` |
| `05-last-login-ip-page.jpg` | `a461500a1acc15ef8aa1a7a59449d6d78ff7dad8fadf7492cf061168e4616a52` | `05-last-login-ip-page.png` | `1f465888796a8326b37c581dbe5bcff59c87e84a9bc1fdbc78682e4a1f6dd111` |
| `06-header-xss-channel-verified.jpg` | `e3a53dd580149df39656d13b9307c4f679c3ed0708a26194fcc83f9730ea8f98` | `06-header-xss-channel-verified.png` | `cd7ac8fd58eba1a13b21d0dc70e07056439fa904339d61c3b6f6b0bc3e0093c9` |
| `07-header-xss-sanitizer-detected.jpg` | `302522ba694e0887d2cc70cad302b5ccbbbf412409a19c7aee76fb5b64d76e05` | `07-header-xss-sanitizer-detected.png` | `a31b0afa290e6cf917ad1ec38044da51ee166dde2bff9ca7a4836a74e42a5a7c` |
| `08-header-xss-filter-mapping.jpg` | `3be9c04a2838bb10d75521e706bf56dd1647b85082dd83ea2847b0af85c80f6e` | `08-header-xss-filter-mapping.png` | `587344733a2948afa900f2b2c6591d4b51e404053973a8069b693ed5dcd79129` |

`tools/dom-xss-analyzer/report-preview.png` is an existing static-source
renderer screenshot: its summary shows nine findings and five high-confidence
rows; its footer says each HIGH requires manual confirmation. It is a UI example,
not product evidence or a new scan.

## K03 — SQLi, JWT, and BOLA evidence inventory

The historical writeups are author records, not raw reproduction packages.
The [report publication preview](../../reports/publication-preview.html) is
limited to archived XSS reports and does not add evidence for these three cases.

| Claim area | Existing source | Evidence present | Evidence absent / correct status |
|---|---|---|---|
| SQLi: Juice Shop Login Admin challenge | [Writeup 03](../../writeups/03-sql-injection.md), Login Admin banner in screenshot 01 | Author narrative says the local challenge was solved; the scoreboard capture gives broad challenge-UI corroboration. | No matching SQLi request/response, exact target/version, database output, or fixed/retest artifact in this K inventory. Treat the result as an author-reported historical exercise, not independently reproduced here. UNION and blind sections are explicitly explanatory, not Juice Shop findings. |
| JWT `alg:none` | [Writeup 04](../../writeups/04-jwt-forgery.md) | Author narrative says the local Unsigned JWT challenge was solved. | No matching JWT request/response, server verification trace, target/version record, or fix/retest artifact located in the scoped evidence files. The writeup's RS256→HS256 attempt is explicitly unsolved. A visible encoded token in the prose is not a request/response reproduction package. |
| BOLA / basket ID | [Writeup 05](../../writeups/05-idor-bola.md), View Basket banner in screenshot 01 | Author narrative reports reading baskets with changed IDs. | No paired account A/B request/response for the same object, account identity proof, authorization-denial retest, or raw HTTP artifacts located in the scoped evidence files. Horizontal BOLA is author-reported, not independently demonstrated by the scoreboard. No vertical escalation claim is supported. |

The scoreboard UI is not a substitute for request, response, identity, or
negative-control evidence. Missing artifacts mean “not present in this package,”
not “the historical event did not happen.”

## K04 — defense claims

[`defense/README.md`](../../defense/README.md) now gives context-appropriate
recommendations and separates advice from what the local evidence supports. It
removes the earlier blanket advice to recursively filter until stable and the
claim that HttpOnly turns an alert into account takeover. It states that CSP is
defense in depth and does not fix unsafe rendering; object authorization needs
an explicit two-account test. The screenshot and evidence inventory do not prove
that these remediations were applied to or retested against Juice Shop.

The parallel C-workstream has now completed the `methodology.md` and writeup
pass. Those files distinguish context-appropriate encoding, reflection, sink
observation, callback, execution proof and triage; they do not overstate
recursive filtering, HttpOnly, CSP, or historical remediation. K04 is complete
at this evidence-scoped documentation level; the historical Juice Shop
remediations were not applied or retested.

## K05 — report labels and counts

Historical raw reports remain unchanged under
[`reports/2026-09-26-v310-live/`](../../reports/2026-09-26-v310-live/). A
separate [publication preview](../../reports/publication-preview.html) records
row counts and qualifies legacy labels:

| Source report | Count verified from archived table rows | Safe summary label |
|---|---:|---|
| A hotel stored report | 25 rows; 25 `JSON-ONLY` | JSON-only reflections; no browser execution proof attached |
| C2 wallet stored report | 25 rows; 25 `JSON-ONLY` | JSON-only reflections; no browser execution proof attached |
| D1 Bludit body report | 1 row, `BREAKOUT-REQ`, context `title` | Reflection candidate; title context; breakout required |
| D2 Bludit title report | 1 row, legacy `EXECUTABLE`, context `title` | Reflection candidate; the label is a legacy context heuristic; no browser-proof artifact is attached to this report package |
| B1 static report | 78 rows; all medium confidence; report summary says 0 high-confidence | Static analyzer candidates; no runtime execution or product triage established |

B2 and C1 each have one table row including the header and therefore zero
observed finding rows; their page says “No unencoded reflections found.” That is
not a safety result. The [HTML report renderer](../../tools/dom-xss-analyzer/dxadyn.py)
footer now describes a reflection/observation report rather than a deterministic
XSS verifier. A focused regression asserts JSON-only/reflection labeling and
the non-execution caveat in `test_dxadyn.py`.

### Verification record

- Renderer tests: `py -3.10 -m pytest tools/dom-xss-analyzer/test_dxadyn.py -q -p no:cacheprovider --tb=short` — **183 passed, 0 failed, 0 skipped**, Windows local run, 22.02 seconds. An initial test assertion failed due to wording mismatch; the assertion was corrected to match the actual existing warning, then the full focused file passed.
- The renderer specialist did not run the full suite. The coordinator then ran
  `py -3.10 -m pytest tools/dom-xss-analyzer -q -p no:cacheprovider --tb=short`
  against the final combined local source: **789 passed, 38 skipped, 0 failed**
  in 186.48 seconds (Windows/Python 3.10.11). Hosted CI was not run for this
  delivery.
- SHA-256 for the modified renderer and regression test: `tools/dom-xss-analyzer/dxadyn.py` `48d8691ee38409e90aa91f24eb3ce09daebc84ecbcd9446f1b717b5f907ceffa`; `tools/dom-xss-analyzer/test_dxadyn.py` `249fb927714248deb30bd4dd84cda3fb7701a6d9f5696107e4a1fdb84a85778b`. The curated preview hash is `reports/publication-preview.html` `4b483553bd7c5e97dba26961da77ca63f969e04275e1fe8712cffe7591831c9b`.
- Raw screenshot hashes above identify the preserved JPEGs; publication PNG hashes identify the redacted derivatives. Historical report SHA-256: A `f3ba53aa02ec839f1ce7feee06e054a8a2349f7b078cf4dcc518531c61731fa1`; C2 `0b984a8d2ef0a09d228661def68a0a658ad3d284620edea66126944d3fb332af`; D1 `bb7d42c92f7749df779642eff0a47e7312da545c59123f593b92af1e5a041e65`; D2 `da0d72ae50e2bbb1d2f5242d8077cb5a9bc3ee1f8c9197fa41d9ce943f8569d0`; B1 `55ffddb57f3f0670af6fdb36dde32050a44accfb87b57785e6a76004c8b2b58b`.

## K02–K05 state

- **K02: evidence inventory and shareable copies complete** for the 8 listed captures and existing static report preview. The copies intentionally mask response content where account/token/hash data was visible.
- **K03: inventory complete; evidence gaps explicit.** Historical SQLi/JWT/BOLA outcomes remain author-reported because paired raw evidence is absent.
- **K04: documentation and evidence-boundary review complete** across the defense guide, methodology, and writeups; no historical remediation retest is claimed.
- **K05: report count/label preview and renderer wording regression complete** for these archived reports. This does not create browser proof for the Bludit rows or turn static candidates into confirmed findings.
