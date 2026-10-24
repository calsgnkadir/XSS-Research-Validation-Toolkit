# K04 retest follow-up — faithful source unavailable

Date: 24 October 2026. Roadmap item: K04. This is a source/artifact
testability review. No HTTP request or browser test was run because the local
evidence does not include a target path that faithfully implements the
historical nested-tag/regex-reassembly claim.

## Question and historical evidence

The writeup says its author's 28 September local Juice Shop experiment showed
a `True-Client-IP` value reaching the Last Login IP field, but explicitly says
retained screenshots do not show a successful JavaScript canary
(`writeups/01-filtering-is-not-protection.md:3,54-57,69-73`). The shown
`dirty.replace(/<script.*?>.*?<\/script>/gi, '')` at lines 23-25 is introduced
as an illustrative single-pass filter. The claimed reassembly input and output
are illustrated at lines 35-50; the writeup now labels the exact target payload
and execution story as historical author-reported, not independently verified.
The archived screenshots were previously reviewed and show header propagation,
filtering, and blank output—not successful execution
(`audit/2026-09-28/DENETIM-RAPORU-TR.md`, HTML screenshot assessment; see also
`audit/2026-10-20-r7-k03-k04-followup/README.md`, K04 section).

## Local artifacts and current source path

Read-only Docker image inventory found one local Juice Shop image: version
20.2.0, image ID
`sha256:0cec496d878c6855a1c81694c9f91564082f418b84aece87538adb8850d2437e`,
repository digest
`bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`.
The ignored local `.dxa/k03-original-package.json` also identifies Juice Shop
20.2.0; its SHA-256 is
`e582b8e132fb6fa82e10f496e8ee55c8d9617f4ba19fc50ad87547bf8d281d87`, matching
the package hash recorded for that image. No earlier Juice Shop image tag or
historical source checkout was found in the local artifacts reviewed.

The pinned 20.2.0 source evidence from the preceding K04 inspection has these
hashes:

| Image file | SHA-256 |
|---|---|
| `build/routes/saveLoginIp.js` | `07a71cfcea57c56d1190770a29ef56c517ec7536afe8fd8c49f633d6ea3241` |
| `build/lib/insecurity.js` | `0f21e927a94a4cb9116f77b8bd7b883f5ba53813971bbfd8393f998e0fc63a0d` |

In the inspected `saveLoginIp.js` path, the `True-Client-IP` header reaches a
challenge check first when `httpHeaderXssChallenge` is enabled; that branch
compares against the challenge's exact active iframe answer. With the
challenge disabled, the route calls `security.sanitizeSecure`. In
`insecurity.js`, that helper uses `sanitize-html` recursively until output
stops changing. The legacy regex is a separate `sanitizeLegacy` helper and is
not called by this route. Therefore the current target does not supply the
writeup's claimed nested-tag deletion/reassembly oracle. Exercising the active
challenge branch would test intentional CTF behavior; substituting a generic
regex fixture would not retest the historical application path.

## Testability outcome

**K04 was not runtime-retested.** The Docker image inventory was read-only.
No image was pulled, container/network/volume was created or modified, no app
was started, and no HTTP or browser request was made. No active challenge value
was submitted. This is a source/artifact mismatch result, not a pass, fail, or
safe-by-test conclusion.

The previous K04 testability audit is
[`2026-10-24-k04-independent-retest`](../2026-10-24-k04-independent-retest/README.md).
It found the same mismatch from a temporary stopped source-copy container;
that container/network were removed. The current inventory check confirms the
historical target image is not locally available. These are separate source
reviews, not two independent reproductions of the claimed behavior.

To attempt a faithful retest later, the owner would need to provide or identify
the exact historical image digest/source commit and its route, sanitizer
dependency/version, and render path corresponding to the 28 September claim.
Retained request/response and browser evidence would help bind the historical
input to that source. Then a disposable internal-only local lab could use
synthetic input and separate stages: output transformation, inert parser
placement, and (only if needed) a harmless CID-matched browser canary. Reflection
or marker placement alone must not be upgraded to JavaScript execution or
vulnerability triage.

Evidence type: current-image/source-path inspection plus read-only Docker image
inventory; no retest result. No source, test, or existing audit file was changed.
