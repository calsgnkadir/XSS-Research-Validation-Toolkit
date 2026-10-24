# K04 historical artifact search and retestability result

Date: 24 October 2026. Roadmap: K04. This task searched repository history
and already-present local/ignored artifacts for the target used by the
28 September writeup. No target request, Docker operation, or browser test was
performed. The only locally retained Juice Shop artifact identifies version
20.2.0, whose source path was already shown not to match the historical claim.

## Claim to reproduce

`writeups/01-filtering-is-not-protection.md` describes a `True-Client-IP` value
reaching the Last Login IP field and illustrates a single-pass regex deleting
`<script>` markup before nested markup is parsed. The writeup's own closing
note says the retained evidence supports header-to-field propagation and
filter observations, but not successful JavaScript execution. The 28 September
review records the same limitation: archived browser evidence did not show a
successful JavaScript canary. This historical claim remains author-reported;
the illustrative regex snippet alone does not identify or prove the target's
implementation.

## Local artifact and Git-history search

- Toolkit HEAD at search: `4abb868829555a28bd22f08d12c144b2999e7347`, branch
  `main`. Local references include `main`, `origin/main`, historical feature
  branches, and tag `v0.1.0`; no historical Juice Shop source checkout or image
  archive was present in the refs reviewed.
- Git history search for `True-Client-IP`, `Last Login IP`, `saveLoginIp`,
  `sanitizeLegacy`, and the illustrative `dirty.replace` expression found the
  writeup and later documentation/evidence-boundary edits. It did not find a
  Juice Shop route implementation or the 28 September target source commit.
  The writeup was first added in `0006178`; the 28 September audit records are
  review/report/check files, not application source or a runnable target image.
- A filename-only search of `.dxa` for Juice Shop/K04/date/source-image clues
  found no historical image, source archive, or target checkout. It did find
  `.dxa/k03-original-package.json`, which identifies `juice-shop` `20.2.0`;
  its SHA-256 is
  `e582b8e132fb6fa82e10f496e8ee55c8d9617f4ba19fc50ad87547bf8d281d87`.
  This is package metadata, not the missing historical target.
- The separate preceding K04 audit records the only local image as Juice Shop
  20.2.0, ID `sha256:0cec496d878c6855a1c81694c9f91564082f418b84aece87538adb8850d2437e`,
  digest `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`.
  Its `saveLoginIp.js` reads the header but checks the intentional active
  challenge value before the normal sanitizer path. With the challenge
  disabled, the route uses recursive `sanitize-html`; the legacy regex helper
  is separate and not called by this route. Source hashes and details are in
  [the prior K04 pinned-source review](../2026-10-24-k04-retest-followup/README.md).

The K04 and A05 workspaces are distinct; no A05 Docker/runtime work was
interfered with. This search did not inspect or modify existing containers,
networks, volumes, or private raw captures.

## Retest decision

**No faithful K04 retest was possible, so no runtime test was started.** The
historical image/source and matching route, sanitizer version, and render path
are absent from the local artifacts reviewed. The current 20.2.0 path would
either exercise an intentional CTF challenge or a different `sanitize-html`
implementation. A generic regex fixture would only demonstrate the illustrative
algorithm, not reproduce the historical application. No external artifact was
downloaded, and no Docker, HTTP, or browser call was made.

To reopen K04, locate or provide the exact historical image digest or source
commit plus the route, sanitizer dependency/version, and render path matching
the writeup. Retained input/output details that bind the header to the claimed
rendered page would also help. If that artifact becomes available, first
reconcile its source identity, then use a new internal-only disposable lab and
synthetic data. Keep output transformation, inert parser placement, browser
JavaScript execution, and vulnerability triage as separate evidence stages.

**Evidence type:** local filename/Git-history search and prior pinned-source
audit reconciliation. No retest result, pass/fail, execution evidence, or
security conclusion is claimed. No source, private capture, or existing lab
resource was changed.
