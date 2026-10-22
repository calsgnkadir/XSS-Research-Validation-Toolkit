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

`CheckInServiceTest` was included in the final selector: all 15 tests passed,
including the owner-denial/no-roster-read regression. An earlier run on the old
3.2.5/6.2.4 dependency set passed 32 focused tests, but predates the final
assertions and is not counted as final verification. No source files changed
during the final combined run. A SHA-256 manifest lists all **41 modified or
new target files** in that tested working tree:
[source-hashes.json](source-hashes.json), SHA-256
`47a6fcb05eb036ba53b66e38a140dbf431d7b6771ec86014f0ed1bd8e03a0b88`.

## Limits and disposition

This remediation closes the reproduced overlong-input path in this local
source state, but is not deployed or committed. The full 91-test suite, Docker
runtime, production accounts, effective production deployment tree and existing
long-password account population were not tested. Users with existing
over-limit passwords need an explicit reset/recovery path before rollout.
No data was migrated or deleted. A05/R7 remain open for other dependency leads,
product-identity advisory uncertainty and broader acceptance. The user reserved
multipart testing for their own later work; it was not executed here. No external
disclosure or communication occurred.
