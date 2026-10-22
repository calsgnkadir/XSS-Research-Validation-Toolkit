# Three-specialist R7/A05 continuation — 22 October 2026

## Current authorization and baseline

The user explicitly requested three specialists working together. This updates
the preceding project limit of two concurrent specialists. The coordinator
remains responsible for shared progress documents, integration and Git delivery.
Toolkit baseline `6167fa8361fd9f02b1a9e859152117639c855540` matched origin/main
after fetch; its initial working tree was clean. Product source remains the
read-only selected Kadrom checkout at `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`.

The coordinator updated the concurrency wording in local AGENTS.md,
docs/AGENT-WORKFLOW.md and all five existing role TOMLs from two to three.
Those paths are explicitly excluded by the existing root .gitignore (lines
16–18); they remain local and the ignore rules were preserved. Only concurrency
wording changed; model/sandbox settings did not. Reading/changing a TOML is
not independent proof that the runtime loaded it. Actual role-selector calls
and tool results below are distinct evidence.

## Exclusive assignments

| Actual specialist call | Ownership | Work and acceptance gate |
|---|---|---|
| `storage_docker_specialist`, `/root/a05_multipart_bounded` | `audit/2026-10-22-a05-multipart-bounded/`, ignored `.dxa/a05-multipart-bounded/`; exclusive Docker lifecycle | Prepare one tiny wellformed control plus one tiny malformed multipart request in a fresh internal/no-host-port lab. Coordinator/QA review must precede target requests. No existing volume or stopped container may be used. |
| `qa_security_lab_specialist`, `/root/a05_bcrypt_utf8` | `audit/2026-10-22-a05-bcrypt-utf8/`, ignored `.dxa/a05-bcrypt-utf8/` | Offline exact-library UTF-8 boundary assay with independent byte/control oracles. No application/account requests or Docker lifecycle. Additional pre-run multipart review is read-only. |
| `xss_security_researcher`, `/root/r7_kadrom_triage_report` | `research/kadrom-local-triage.md`, `audit/2026-10-22-r7-kadrom-report/README.md` | Produce concrete owner-review R7 triage report from accepted evidence, with remediation proposal, impact limits and disclosure status; no external submission. |

Three actual specialist calls were active concurrently. Their exclusive paths
do not overlap; shared ROADMAP/STATUS/VALIDATION/CHANGELOG remain coordinator-owned.
A04's accepted selected GET scope remains bounded complete; this continuation
does not add product-wide authorization coverage or reopen unrelated routes.

## Accepted and blocked outcomes

- [Unicode assay](../2026-10-22-a05-bcrypt-utf8/README.md): exact cached Crypto
  6.2.4 matched three different Unicode suffix values with equal first 72 UTF-8
  bytes. Whole lengths 73/74/75 UTF-8 bytes versus 72/72/73 UTF-16 units; packaged
  PasswordPolicy admitted both inputs. Exactly 9 BCrypt calls; the exactly-72-byte
  correct/wrong control passed. Coordinator independently checked source, JSON,
  helper/crypto hashes, manifest version and operation accounting. This is direct
  library/policy execution, not a new application endpoint reproduction.
- [R7 owner-review report](../../research/kadrom-local-triage.md): completed
  concrete candidate dispositions and BCrypt remediation/retest proposal, with
  earlier application evidence separated from the new library assay. It was not
  externally submitted. Target source/dependency modification remains separately
  authorized work; no fix or recovery/migration was performed.
- [Multipart task](../2026-10-22-a05-multipart-bounded/README.md): automatic
  possible-cybersecurity-risk flag stopped the specialist before runtime. Its
  bookkeeping-only follow-up also failed on that gate. No test was retried or
  delegated as a workaround. Coordinator read-only name filters found no planned
  new resources; draft artifacts were preserved locally. Two unexecuted QA
  oracle gaps remain documented. No cleanup or security result is inferred.

All agent turns have ended; there is no continuing background task. No Docker
lab or application request was started in this continuation. Old source/data/
containers/volumes were preserved. A04 remains bounded complete; A05/R7 remain
open. No toolkit/product test-suite or new CI result is claimed.
