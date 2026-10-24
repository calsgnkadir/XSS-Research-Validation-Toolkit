# Writeup reconciliation, A05 freeze, and K04 artifact search — 24 October 2026

## Scope and disposition

This coordinator follow-up addressed the user's ordered documentation and
artifact-search tasks after pushing the existing docs-only commit `6170994`.
The initial push advanced `origin/main` from `4abb868` to `6170994`. The
writeup reconciliation was then committed as
`574ff7c707a8e28ceaf45b11605d0359c72ad06a`, pushed, and verified with
`git ls-remote origin refs/heads/main`, which returned that same SHA. No force
push was used. No CI run was requested or performed for this documentation-only
delivery.

The work changed writeup prose and project status records only. No raw historical
reports, application source, test fixture, Docker resource, or application data
was modified. No toolkit tests, target requests, or external communications
were performed.

## C01–C09 writeup body changes

| Roadmap | File(s) | Claim boundary added or corrected |
|---|---|---|
| C01 | `writeups/01-filtering-is-not-protection.md`, `writeups/README.md` | The nested-tag regex is now presented as a generic illustrative deletion mechanism. Retained screenshots support the header-to-field/filter observation, not the historical execution claim or recovered target filter implementation. K01 is explicitly separate evidence. |
| C02 | `writeups/02-dom-xss-assessment-react-spa.md` | The historical “no vulnerability” wording is replaced with “not independently substantiated”; the no-source-to-sink conclusion is attributed to the author and limited by the missing bundle. The reported `postMessage` observation is not described as independently confirmed. |
| C03 | `writeups/03-sql-injection.md` | Login bypass, `UNION`, and blind SQLi sections are labeled as theory/examples. The bounded local login-shape reproduction is linked separately and does not recover the older session or validate UNION/blind behavior. |
| C04 | `writeups/04-jwt-forgery.md` | JWT material is labeled mechanism, the two attack families are distinct examples, and only the separate pinned-image `alg:none` replay is identified as observed. The old HS256 failure cause remains unknown. |
| C05 | `writeups/05-idor-bola.md`, `writeups/README.md` | The old basket-ID account remains unverified. The later two-synthetic-account, same-session owner-A/owner-B basket check and anonymous 401 are described as bounded horizontal access-control evidence; vertical privilege escalation and other routes were not tested. |
| C06 | `writeups/06-building-an-xss-bot.md` | Operator-supplied `{CID}` URL seeds are distinguished from discovery. Candidate source/sink output and raw marker reflection are not described as proven execution or vulnerability. |
| C07 | `writeups/07-teaching-the-bot-to-log-in.md` | Post-submit checks are bounded link checks plus operator-supplied orphan hints. Historical 0-HIGH counts and sanitizer-name rules are not safety/function-analysis evidence. |
| C08 | `writeups/08-what-does-not-shout-matters.md` | Raw JSON is separated from HTML/XSS; repeated rows/counts from confirmed vulnerability counts; title/reflection labels from execution; sanitizer-like names from function-body/context analysis; and row changes from measured precision/recall. |
| C09 | `writeups/09-three-high-to-one-a-precision-journey.md` | The title now describes a historical row-count change. A sanitizer-name heuristic does not verify the helper, and the 3→1 result is not a precision measurement or validated TP/FP classification. |

## A05 — frozen partial

A05 remains **partial** and is frozen at the current environment boundary. The
malformed multipart cleanup fixture passed 1/1 on the embedded Tomcat 11/Spring
MVC fixture. A separate current-source application runtime attempt did not
reach health or authentication because host-to-MySQL loopback connectivity
failed. Therefore this record makes no current app, auth, deployment, proxy/WAF,
production dependency graph, stress, or broad CVE disposition claim. Earlier
evidence and data are preserved. Resume runtime work only if a suitable
authorized environment becomes available.

## K04 — artifact search and retestability

Read-only filename/content searches covered the active workspace and reachable
project/artifact locations under `OneDrive\Desktop`, `Documents`, and
`Downloads`, including the other local toolkit copies and the known 28 September
audit worktree. The search found old assessment documents and screenshot
references, but no matching historical source/image with the claimed route,
sanitizer version, and render path. No found artifact matched the pinned Juice
Shop 20.2.0 route reviewed in the prior K04 audits.

The Docker CLI could not list images because the Docker engine named pipe
`//./pipe/docker_engine` was absent. This is an unavailable inventory check,
not evidence that no local Docker image exists. The bounded conclusion is:
**no matching historical source/image was located in the searched paths, so a
faithful K04 retest cannot be performed from the available evidence.** The
historical bypass/execution claim remains unverified. No container was started,
stopped, pulled, or removed; no HTTP/browser request was made.

## Validation

Documentation and local artifact inventory only. No toolkit test suite was
run. `git diff --check` found no whitespace errors. The delivery SHA and remote
verification are recorded in the current handoff after commit.
