# R7 / A05 — BCrypt 72-byte authentication-equivalence triage

**Date:** 2026-10-22
**Review type:** bounded source review plus review of one existing local synthetic registration/login reproduction
**Toolkit source:** `a20a281c898b430861b9f0539fee444efe0c5965` (`main`)
**Kadrom source:** pinned commit `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`
**Roadmap:** R7 / A05

## Conclusion

The pinned application has a **reproduced password-equivalence defect on its registration-to-login path**, and its resolved `spring-security-crypto:6.2.4` is in the affected range of CVE-2025-22228. One synthetic registration accepted a 73-byte ASCII password, and one login using the same first 72 bytes but a different final byte authenticated to the same newly registered principal. This is sufficient to classify the pinned configuration as exhibiting the advisory's behavior and to recommend remediation.

This does **not** establish that an attacker can take over a real account in practice: no victim password, password distribution, real account, external deployment, or end-to-end attack was tested. It is not a new CVE claim. The narrowly supported impact is that for affected passwords, the final bytes after BCrypt's effective 72-byte input boundary do not distinguish credentials; the accepted credential equivalence class is broader than the account owner may expect.

## Evidence and source path

### Reproduced behavior

The existing [bounded local check](../2026-10-22-a05-bcrypt-local-check/README.md) records one focused JUnit test under the pinned Kadrom `test` profile. It made one registration with a policy-valid 73-byte ASCII password, followed by one login using the same first 72 bytes and a different final ASCII byte. Registration returned HTTP 200; login returned HTTP 200 for the same principal; Surefire recorded 1 passed, 0 failed/errors/skipped. Inputs, password hash, tokens, cookies, response bodies, and the transient verification token were not retained.

This evidence is a local MockMvc/H2 reproduction using a synthetic account. It is not a second independent run in this triage. The test did not use Unicode, production settings, a real account, a browser, or an external service. The temporary test was removed; no Kadrom product source was changed. The successful Maven invocation required the platform escalation flow after an earlier cached-JAR read was denied; that earlier attempt did not execute the application request.

### Source-supported path

All paths below are relative to the read-only pinned Kadrom checkout `.dxa/a04-kadrom-source/hotelapp/`.

| Source | Relevant lines | What it establishes |
|---|---:|---|
| `pom.xml` | parent version 3.2.5 | Spring Boot dependency-management baseline. The resolved crypto artifact is recorded below from the dependency audits. |
| `config/AppConfig.java` | 53–58, 74–75 | The DAO authentication provider is configured with the application's `BCryptPasswordEncoder`. |
| `dto/RegisterRequest.java` | 31–37 | Registration password validation requires at least 8 Java `String` units and ASCII letter/digit composition; there is no maximum. |
| `validation/PasswordPolicy.java` | 13–27 | The shared policy is minimum length plus composition only; it contains no maximum or UTF-8 byte-length check. |
| `service/AuthService.java` | 62–82 | Registration applies the policy again, then passes the supplied password to `PasswordEncoder.encode`. |
| `controller/AuthController.java` | 64–70, 76–83 | The validated registration and login request bodies reach their respective service methods. |
| `dto/LoginRequest.java` | 8–13 | Login password is nonblank only; there is no length cap. |
| `service/AuthService.java` | 141–157 | Login passes the submitted password to Spring Security's `AuthenticationManager`. |
| `service/AuthService.java` | 291–302, 311–321 | Password change uses `matches` for the current password and encodes the new password; the request has no maximum. |
| `controller/PasswordResetController.java` | 68–78 | Password-reset confirmation caps the new value at 128 Java characters, not at 72 UTF-8 bytes. |

The dependency audit records resolved `org.springframework.security:spring-security-crypto:6.2.4` and its match to GHSA-mg83-c7gq-rv5c (`audit/2026-10-21-a05-transitive-advisories/README.md:167`; range cross-check `audit/2026-10-21-a05-transitive-range-review/README.md:47`). The actual effective Maven tree was captured in the preceding dependency-tree audit; this triage did not rerun Maven or alter the dependency graph.

### Advisory comparison

The official [Spring advisory for CVE-2025-22228](https://spring.io/security/cve-2025-22228/) lists Spring Security 6.2.0–6.2.9 as affected and identifies 6.2.10 as the corresponding fix (enterprise-support-only in the advisory's published table); it says `BCryptPasswordEncoder.matches` can return true for values longer than 72 characters when the first 72 characters agree. The [GitHub Advisory](https://github.com/advisories/GHSA-mg83-c7gq-rv5c) provides the same affected range and description. Thus the resolved 6.2.4 falls in the published affected range, and the observed ASCII case matches the described behavior.

The linked Spring Security [fix commit](https://github.com/spring-projects/spring-security/commit/46f0dc6dfc8402cd556c598fdf2d31f9d46cdbf3) checks whether BCrypt input exceeds **72 bytes** and throws `IllegalArgumentException`; its regression test covers a 73-character ASCII case. This makes the byte boundary operationally important. The advisory prose uses “characters,” while the fix enforces bytes; they coincide in this test because the password was ASCII.

## Password policy, UX, and Unicode limits

The current registration policy accepts the tested 73-byte ASCII password because it has no maximum. New-user UX therefore lets a user choose a value whose suffix is not an independent BCrypt credential component. Login and password-change current-password schemas likewise have no maximum. Reset's maximum of 128 is above the BCrypt boundary and is a Java character-count limit, so it does not by itself enforce the BCrypt input limit.

The observed test used only ASCII. Java `String.length()` counts UTF-16 code units, while BCrypt's underlying boundary in the official fix is 72 encoded bytes. A Unicode string can occupy a different number of UTF-8 bytes than its Java character count; the application source's letter/digit regex also permits additional Unicode characters once its ASCII letter and digit lookaheads are met. No Unicode input, normalization behavior, invalid encoding, or boundary ending inside a multi-byte character was tested. Do not generalize the 72 ASCII character observation into a full Unicode policy result.

## Threat and impact assessment

- **Confirmed:** a newly registered synthetic account accepted a tested 73-byte ASCII value and authenticated with one different suffix sharing the first 72 bytes.
- **Security consequence supported by the behavior:** for passwords beyond BCrypt's effective input boundary, suffix bytes do not uniquely distinguish the credential. A user who expects the whole password to matter receives less effective password input than the UI accepts.
- **Threat condition:** an attacker would still need to obtain or guess the first 72 effective bytes of a victim's password, or otherwise reach an authentication flow with a suitable candidate. This review did not establish that condition, estimate password entropy, test rate-limit resistance, or demonstrate account takeover.
- **Other paths:** change-password current-password validation uses `matches` and has no maximum at the DTO; this is a source-supported additional exposure path, not separately reproduced. Password reset accepts at most 128 Java characters but still exceeds 72 for some inputs; not separately tested.
- **Classification:** confirmed vulnerable dependency behavior is reachable through the tested application flow; actionable application security defect / A05 candidate. Practical exploitability and real-user impact remain unverified. Do not label it “only a dependency alert,” but also do not claim a demonstrated real account compromise or a new CVE.

## Smallest safe remediation and retest plan

No Kadrom source or dependency was changed in this task. For an authorized remediation task, the smallest safe plan is:

1. **Select a supported fixed dependency set.** Prefer updating the Spring Boot dependency-management baseline to a currently supported release that manages a patched Spring Security line. Avoid overriding only `spring-security-crypto` without checking Spring Security module alignment and Boot compatibility. The advisory lists 6.2.10 as the 6.2 fix but marks it enterprise-support-only; confirm an eligible supported patched line for the product before choosing versions. Do not report a package bump as a behavior fix until the effective dependency tree proves the runtime version.
2. **Make the application's byte policy explicit at every password boundary.** Reject passwords whose UTF-8 encoded form exceeds the chosen BCrypt limit before registration/change/reset encoding, and prevent over-limit login/current-password values from reaching BCrypt. Count bytes, not Java characters. Keep validation at both DTO and service boundaries where the service currently repeats password policy. Use a neutral, documented validation error and ensure the rejected path does not return a server error.
3. **Handle existing long-password accounts deliberately.** A newly enforced limit can strand accounts whose registered passwords were longer than 72 UTF-8 bytes, especially when a boundary falls within a multi-byte character. Define an account recovery/password-reset path before rollout; do not silently truncate submitted passwords or silently transform existing hashes. No account migration is proposed by this source-only review.
4. **Retain focused local regressions.** In the authorized disposable H2 profile, test registration accepts the maximum allowed byte sequence and rejects the next byte; exercise ASCII and multi-byte UTF-8 boundaries. Test login with an over-limit suffix variant and assert it cannot authenticate as the same account (or is rejected by validation with a deliberate client error), with no 500. Cover change-password current/new values and reset confirmation. Recheck a known valid ≤72-byte password and verify session/token behavior remains as expected. Then run the relevant Kadrom auth suite and inspect the resolved runtime tree; report exact commands, environment, and tested source/dependency hashes.

The library upgrade is the root-cause dependency fix recommended by Spring. An application byte limit is defense in depth and UX consistency; it should not be presented as proof that the vulnerable library was patched. Conversely, applying the library update without handling password boundaries may cause over-limit values to fail or surface an error, so validate all relevant flows.

## Limits and roadmap disposition

- Evidence types: pinned source review; one previously recorded focused synthetic H2 registration/login reproduction; official advisory/fix-source review.
- No new application runtime, test, endpoint, Docker container, external target, disclosure, or communication was used for this triage.
- Reflection, callbacks, and browser/JavaScript execution are not applicable to this auth behavior and were not performed. The registration/login status and same-principal comparison are application-authentication evidence, not browser execution or a general vulnerability verdict.
- Native custom-role loader invocation was not verified in this session; this was a temporary delegated specialist task. The role TOML was read, but its presence is not evidence that the runtime loaded it.
- **R7/A05:** bounded lead advanced from plausible source path to reproduced advisory-matching behavior in the pinned local app. Product remediation/rollout, Unicode boundaries, real-account impact, dependency-upgrade validation, and broader R7 triage remain open.
- No R7/A05 closure, external report, CVE attribution to the application, or claim of real account compromise follows from this audit.
