> **Historical / experimental reference — evidence review updated 2026-10-20.** Outcomes below are author-reported unless their supporting artifacts are present. They do not establish current program scope, CVE credit, or general scanner capability. See [verified status](../STATUS.md) and [current acceptance criteria](../ROADMAP.md). A raw marker, scanner severity, callback or zero findings alone does not establish execution, a vulnerability or safety.

# Beyond the Lab — Independent Vulnerability Research

After building the foundation in this repository (OWASP Juice Shop, PortSwigger Academy), I applied
the same **source → sink** discipline to *real, third-party open-source software*: plugins published
in the WordPress.org directory.

> ⚠️ **Historical scope statement.** This describes the author's account of earlier work. The
> repository does not contain complete target/version, reproduction, submission, and triage packages
> needed to independently verify each outcome. It does not establish current permission, program
> scope, disclosure-channel eligibility, or a universal disclosure deadline. No new product research
> or external submission is recorded here.

---

## Why this matters

Automated scanners and pattern-matching tools (increasingly AI-assisted) have made *pattern-level*
bug hunting a crowded lane — the easy, greppable bugs get found and reported by many people at once.
The value has shifted to what tooling is **bad** at: reading code for **logic and access-control
flaws**, reasoning about **privilege context**, and — critically — **verifying** a hypothesis in a
real environment before believing it. This is the skill this research set out to build.

---

## Methodology

**1. Target discovery & batch triage.**
Custom Python tooling queries the WordPress.org plugin API, downloads plugins at pinned versions, and
statically triages their source for high-signal sinks (unescaped output, unprepared `$wpdb` queries,
sensitive AJAX/REST handlers). The triage improved over many iterations to cut false positives:

- **Guard-following** — resolve a handler's helper calls one level deep, so authorization checks
  hidden in a `check_permission()` helper are not mistaken for "missing."
- **"Nonce ≠ authorization"** — a CSRF nonce is *not* an access-control check; handlers with a nonce
  but no capability/ownership check are flagged, not cleared.
- **Active-class filtering** — verify a handler's class is actually instantiated; an `add_action()`
  inside a class that is never `new`'d is dead code, not an entry point.

**2. Patch-diffing / variant analysis.**
For a plugin that recently shipped a security fix, diff the vulnerable and patched versions to learn
*exactly* what the developer fixed — then hunt the **sibling code paths they did not fix**. Developers
routinely patch one instance of a bug class and miss its variants.

**3. Verification in a local lab.**
Every surviving candidate is reproduced in a Dockerized WordPress instance (multiple roles, real HTTP
requests from an attacker's perspective) **before** it is treated as real. This step repeatedly caught
static-analysis false positives — e.g. a handler that looked exploitable but whose class was never
loaded, and "missing authorization" that turned out to be an ownership check the grep missed.

**4. Coordinated disclosure.**
Confirmed issues are reported through Patchstack; unpatched details are never disclosed publicly.

---

## Historical author-reported outcomes (not independently verified)

The outcomes below reflect the author's account. The retained repository does not include the
matching product/version, source diff, independent reproduction, submission receipt, triage decision,
or CVE attribution needed to verify them.

- The author reports a WordPress-plugin access-control finding and says Patchstack marked the
  submission as a concurrent duplicate. The local PoC, submission receipt, and triage record are not
  present in this repository, so the outcome is not independently verified here.
- The author reports re-deriving a SQL-injection variant by patch-diffing and later associating it
  with a published CVE. The product/version, patch lineage, and CVE attribution are not present here;
  no CVE credit is claimed.
- The repository contains reusable **auditing tooling** and a documented workflow.

These accounts do not independently establish that the methodology produced externally validated
findings or establish general product-level detection capability.

For the Bludit comparison in this repository, CERT Polska's [CVE-2026-4420 advisory](https://cert.pl/en/posts/2026/04/CVE-2026-4420/)
credits Yassin Abdelrazek and confirms versions 3.17.2 and 3.18.0 as tested and vulnerable. The local
Bludit 3.16.2 behavior recorded elsewhere here is a separate observation; it does not establish that
the local path, root cause, or report matches CVE-2026-4420. The advisory says other versions were not
tested, so this distinction does not establish that 3.16.2 is safe.

---

## Disciplines learned (the part that transfers to any target)

- **Severity is contextual.** An admin-only SQL injection is not a meaningful vulnerability (an admin
  already has higher privilege); the same bug reachable by a Subscriber or unauthenticated user is.
- **A guard can be present but insufficient.** A nonce blocks CSRF, not authorization; an ownership
  check is not a capability check; a capability check on the wrong object is a bypass.
- **Static analysis lies without verification.** Dead code, helper-based guards, and framework
  escaping all fool a grep. Reproducing in a real environment is non-negotiable.
- **Read the program's scope before spending effort.** What counts as a valid, in-scope finding is a
  written rule, not a guess — and it changes.
- **Choose under-contested targets.** Heavily-audited components produce duplicates; the same effort
  on an under-watched target is far likelier to land.

---

*Independent, responsible security research · public open-source code · local verification · coordinated disclosure.*
