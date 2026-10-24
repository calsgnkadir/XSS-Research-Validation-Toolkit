# K04 independent retest — testability result

Date: 24 October 2026. Roadmap item: K04 documentation/defense evidence.

## Scope reviewed

The K04 documentation acceptance covers the defense discussion in
`writeups/01-filtering-is-not-protection.md`: context-aware output handling,
parser-based allowlist sanitization for rich HTML, and limits of CSP and cookie
flags. The specific historical claim is that deleting a `<script>` block from
a nested-tag input assembles an iframe. This is separate from the retained K01
stored-comment fixture and does not establish an XSS finding in the toolkit.

The writeup itself records the limitation: its 2026-09-28 Juice Shop screenshots
show header-to-field propagation and filtering observations, but do not show a
successful JavaScript canary (`writeups/01-filtering-is-not-protection.md:3,
:55, :71`). The K04 review corrected stale sanitizer and `textContent`
descriptions; it did not apply a fix to the historical target or retest one
(`audit/2026-10-20-r7-k03-k04-followup/README.md:88-99`). The 19 October
Juice Shop 20.2.0 K03 lab is a separate SQLi/JWT/BOLA reproduction and explicitly
does not validate the historical K04 session or its fix.

## Pinned-source review and retestability

The already-present image was verified without pulling it:

- Product: OWASP Juice Shop `20.2.0`
- Local image ID: `sha256:0cec496d878c6855a1c81694c9f91564082f418b84aece87538adb8850d2437e`
- Repo digest: `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- `build/routes/saveLoginIp.js` SHA-256:
  `07a71cfcea57c56d1190770a29ef56c517ec7536afe8fd8c49f633d6ea3241`
- `build/lib/insecurity.js` SHA-256:
  `0f21e927a94a4cb9116f77b8bd7b883f5ba53813971bbfd8393f998e0fc63a0d`

In `saveLoginIp.js`, the `True-Client-IP` header is read. When the
`httpHeaderXssChallenge` is enabled, the route checks for the exact active
`iframe src="javascript:alert(...)"` challenge answer before the sanitizer
branch. When the challenge is disabled, it calls `security.sanitizeSecure`.
In `insecurity.js`, `sanitizeSecure` calls `sanitize-html` and recursively
re-applies it until the output stops changing. The regex is the separate
`sanitizeLegacy` helper; this route does not call it.

That source does not match the writeup's specific mechanism—deleting a script
block with a regex to assemble a new iframe. Replaying the exact active
challenge value would exercise an intentional CTF challenge branch and violate
the inert parser-only oracle. Replacing it with a generic inert regex fixture
would not retest the historical Juice Shop path. The feedback route/path also
was not established from the inspected route files.

**No K04 HTTP/runtime or browser retest was run.** K03 finished its separate
lab first. For K04, a unique internal Docker network and a stopped, unstarted
container were created only to copy the pinned image's route source for offline
inspection; both exact resources were then removed. No app process, HTTP
request, browser, external request, image pull, or volume was used. The existing
stopped Juice Shop container and its network were left untouched. No historical
target fix or remediation was tested.

## K04 retestability and next step

A future retest needs the exact historical image/source or a retained,
reproducible filter/input/render path that actually uses the claimed deletion
rule. The present `20.2.0` `saveLoginIp` path is not that oracle. If suitable
source becomes available, use fresh synthetic content in a new internal-only
lab, test output transformation and parsed marker placement with JavaScript
disabled, and retain a separate negative control. An inert marker establishes
parser placement only; it does not establish execution or vulnerability impact.

The documentation recommendation remains supported as general defensive
guidance, but the historical Juice Shop bypass and fix/retest are not newly
validated. Evidence type here: pinned-image metadata and source-path inspection,
plus Docker-resource cleanup verification; no test result. The historical
execution remains author-reported and unsupported by retained independent
evidence.
