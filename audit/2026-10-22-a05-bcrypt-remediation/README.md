# Kadrom BCrypt password remediation — 22 October 2026

## Scope and authorization

The product owner explicitly authorized Kadrom source/dependency fixes in this
conversation. Native specialist `/root/bcrypt_fix` owned the auth, dependency,
and compatibility changes in the user's local checkout. The source baseline is
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c` in
`.dxa/a04-kadrom-source` (`main`). The checkout was clean at assignment start.
The user-owned upstream was observed one commit ahead, with the single known
change in `hotel-web/vite.config.js`; the checkout was deliberately left at the
pinned evidence baseline. No target code was committed or pushed.

The prior pinned app reproduction and official advisory are recorded in the
[BCrypt triage](../2026-10-22-a05-bcrypt-triage/README.md) and
[local check](../2026-10-22-a05-bcrypt-local-check/README.md). The advisory
lists Spring Security 6.2.0–6.2.9 as affected and 6.2.10 as enterprise-only;
its other public fixed lines are 6.3.8 and 6.4.4. The selected currently
maintained path is the aligned Spring Boot 4.1.1 / Spring Security 7.1.1 family.
Official sources: [CVE-2025-22228 advisory](https://spring.io/security/cve-2025-22228/),
[Spring Boot 4.1 requirements](https://docs.spring.io/spring-boot/4.1/system-requirements.html),
[Spring Security 7.1 reference](https://docs.spring.io/spring-security/reference/7.1/).

## Implementation

- Upgraded the Maven parent to Spring Boot 4.1.1 and springdoc to 3.1.1. Added
  the Jackson 2 module required by existing application `ObjectMapper` use and
  Boot 4's MVC, JPA and metrics test modules.
- The resolved Spring Security config, OAuth client, JOSE, core, test, crypto
  and web modules were reported at 7.1.1. This is a managed aligned set, not a
  single-jar override.
- `PasswordPolicy` now defines a maximum of 72 UTF-8 bytes. Bean Validation
  enforces it on registration, login, password-change current/new values and
  reset confirmation. Service-level guards repeat the limit before hashing or
  authentication. Over-limit requests receive a deliberate client error
  (`400` at the login DTO boundary; service rule violations use the app's 4xx
  mapping). No password is truncated, normalized or transformed.
- The encoder upgrade rejects creating hashes from over-72-byte inputs. Spring
  Security retains long-input matching behavior for legacy hashes; therefore
  the application byte guard before every `matches` path is required. The
  guard rejects over-limit legacy credentials until the account uses password
  reset. No automatic hash migration or existing-account inventory was done.
- Boot 4 migration compile fixes use `PathPatternRequestMatcher` for the
  `/api/**` entry-point rule, the new `DaoAuthenticationProvider` constructor,
  and `UriComponentsBuilder.fromUriString` at two call sites. Test imports,
  `@MockitoBean` annotations and Tomcat 11 test fixtures were adapted to the
  Boot 4 managed test stack. All 91 test source files compiled in the focused
  verification run.

## Regression evidence

The specialist reported this focused command, run from `hotelapp/`:

```powershell
mvn -ntp -Dmaven.repo.local=C:\Users\user\.m2\repository -Dtest=InputPolicyTest,AuthServiceTest,AuthServiceLoginLimitTest,PasswordResetServiceTest,BcryptPasswordHttpTest,CheckInServiceTest test
```

Result: **51 tests passed; 0 failures, 0 errors, 0 skipped**. All 91 test source
files compiled. Coverage includes
exact 72-byte and over-limit 73-byte ASCII and UTF-8 values, two/four-byte
characters, encoder rejection for over-limit encoding, ordinary valid matching,
wrong-password rejection, registration/login/change/reset guards, and a
MockMvc login with a 73-byte password returning 400 before authentication. A
separate anonymous `/api/me` control returned 401. `git diff --check` passed.

`CheckInServiceTest` was included in the original combined selector: all 15
tests passed, including the owner-denial/no-roster-read regression. An earlier run on the old
3.2.5/6.2.4 dependency set passed 32 focused tests, but predates the final
assertions and is not counted as final verification. After that combined run,
the BCrypt follow-up specialist added a positive exact-72-byte multibyte
change-password regression in `AuthServiceTest`. The auth-only selector then
passed **37 tests, 0 failures/errors/skips**, compiling all 91 test sources.
The added test checks matching the existing password, encoding/saving the new
password, and refresh-token revocation. Its source SHA-256 is
`192b46948859ab81efa6c95b542d10a7b1d5f40edfc799af1b704860206d44e9`.
The earlier combined 51-test result remains valid for the earlier exact source
state, but was not rerun after this test-only addition. A SHA-256 manifest lists
all **41 modified or new target files** in the current tested source tree:
[source-hashes.json](source-hashes.json), SHA-256
`6654b61818574f6bcc40492796e07a3679070c59c6effe07ba346f9a34224cf7`.

## Coordinator final verification follow-up — 22 October 2026

The POM hash mismatch noticed in the first independent review was corrected;
the current manifest now matches all 41 target files. The final POM also
aligns Resilience4j to its Boot 4 module and includes the Boot 4 AspectJ
starter. A full in-memory-H2 Maven run passed **665 tests, 0 failures, 0 errors,
0 skipped** after test-only H2 was pinned to 2.3.232 to avoid the known H2
2.4.240 CHECK/enum regression. The full result and final 246-coordinate OSV
snapshot are recorded in [VALIDATION](../../VALIDATION.md) and the
[A05 dependency follow-up](../2026-10-22-a05-dependency-refresh/README.md).
Coordinator delivery update: target commit `6be6a07` was merged with the
upstream-only `ba38bd3` Vite change and pushed as `c3ce102`; local and fetched
`origin/main` matched that commit. The source tree covered by the 41-entry hash
manifest and 665/665 test run is unchanged by the Vite-only merge. It remains
undeployed; the existing-account reset rollout, CI and multipart follow-up are
still unverified.

## Limits and disposition

This remediation closes the reproduced overlong-input path in the committed
source state, but is not deployed. The final full local test suite
passed as recorded below; Docker runtime, production accounts, effective
production deployment tree and existing long-password account population were
not tested. Users with existing
over-limit passwords need an explicit reset/recovery path before rollout.
No data was migrated or deleted. The BCrypt remediation subtask is complete for
this local source state. The A05 umbrella remains partial for multipart,
effective-runtime and advisory/applicability follow-up; R7 separately remains
open for product-identity evidence and owner/disclosure disposition. The user
reserved multipart testing for their own later work; it was not executed here.
No external disclosure or communication occurred.
