# Bounded BCrypt login check — 2026-10-22

## Scope and setup

This was one bounded local comparison for the R7/A05 lead in the user's
Kadrom application. The source checkout was pinned at
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. No external service, URL, Docker
container, or real account was used.

The existing `test` profile uses H2 in-memory with Hibernate `create-drop`
(`.dxa/a04-kadrom-source/hotelapp/src/test/resources/application-test.yml:1-17`),
disables Flyway (`:16-17`), rate limiting (`:29-30`), and Cloudinary (`:62-64`). The test made
one synthetic enabled and email-verified candidate account and exactly two
login requests through `POST /api/auth/login`
(`.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/controller/AuthController.java:74-85`):

1. A synthetic password consisting of 72 ASCII bytes, satisfying the app's
   minimum length and letter/digit composition policy.
2. The same 72 bytes followed by one different ASCII byte (73 bytes total).

The password, encoded hash, access token, refresh cookie, and response body
were not retained in this audit. Only HTTP status and whether the returned
principal matched the synthetic account were recorded.

## Result

Focused test result: **1 test passed, 0 failures, 0 errors, 0 skipped**.
The normal input returned HTTP 200 for the synthetic principal. The one
73-byte variant also returned HTTP 200 for that same principal. Thus the
longer input authenticated against the hash created from the first 72 bytes
in this local application path.

This reproduces the documented BCrypt boundary behavior for this pinned
application configuration. It is evidence of an authentication-input
equivalence condition in the tested path; it does not establish a practical
account compromise, CVE applicability, or a product vulnerability by itself.
No additional passwords, accounts, or authentication paths were tried. The
synthetic stored hash was created directly with the configured `PasswordEncoder`
in the temporary test; the 73-byte value was not submitted to the registration
endpoint. This check therefore makes no registration-acceptance claim.

Source context: `.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/config/AppConfig.java:53-58,74-75`
configures `BCryptPasswordEncoder`;
`.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/dto/LoginRequest.java:8-13`
has nonblank validation without a maximum length;
`.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/service/AuthService.java:141-157`
passes the supplied value to the authentication manager. Registration's
`.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/validation/PasswordPolicy.java`
enforces a minimum and letter/digit composition (`:13-27`) but no maximum.
The official advisory describes the >72-character
`BCryptPasswordEncoder.matches` behavior and lists Spring Security Crypto
6.2.4 in its affected range: [GHSA-mg83-c7gq-rv5c](https://github.com/advisories/GHSA-mg83-c7gq-rv5c).
This focused check confirms the behavior observed here, not every advisory
precondition or downstream impact.

## Runner and artifact accounting

Environment observed in the successful run: Windows, Maven 3.9.16 offline,
Java 17.0.18, Spring Boot 3.2.5, active `test` profile, H2
`jdbc:h2:mem:hotel_test`. The only test command was:

```powershell
mvn.cmd -o -Dmaven.repo.local=C:/Users/user/.m2/repository `
  -f .dxa/a04-kadrom-source/hotelapp/pom.xml `
  -Dtest=BcryptBoundaryLocalCheckTempTest test
```

The first attempt stopped in test compilation because the temporary source
had a UTF-8 BOM. After removing the BOM, the un-escalated offline run stopped
in test compilation while reading the cached Spring Boot starter JAR under
`.m2` (`Access denied`). The same offline command was then run through the
platform escalation flow and completed successfully. These are test-source
and runner permission failures, not application behavior; neither produced a
test result.

The focused JUnit source was temporary and removed after the successful run.
The final report recorded `Tests run: 1, Failures: 0, Errors: 0, Skipped: 0`.
The Kadrom checkout was verified at the pinned commit with a clean working
tree, and the temporary source path was confirmed absent. Maven's ignored
`target/` build outputs were not added to the Kadrom tree. The toolkit
workspace contained other in-progress changes and was left untouched except
for this assigned audit file.

## Evidence limits and roadmap

- Evidence type: one local H2 MockMvc reproduction using a synthetic account.
- No Docker, external endpoint, network provider, browser, fuzzing, loop, or
  brute-force activity was used.
- No product fix or regression test was written; the temporary check is not a
  retained product test.
- No full Kadrom suite or toolkit suite was run. No CI result was queried.
- This was a temporary generic delegated invocation; native custom-role
  invocation was not independently verified.
- Roadmap mapping: R7/A05. The bounded lead is reproduced; roadmap closure
  still requires coordinator review of applicability, impact, disposition,
  and any separately authorized fix/test work.

## Registration endpoint follow-up — 2026-10-22

### Side-effect preflight

Before the follow-up, the pinned Kadrom checkout was again verified at
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. The existing `test` profile uses
only the H2 in-memory database for persistence (`.dxa/a04-kadrom-source/hotelapp/src/test/resources/application-test.yml:1-17`),
disables Flyway (`:16-17`) and Cloudinary (`:62-64`), and delays the outbox
relay for `31536000000` ms (one year; `:49-51`). Environment-variable presence
checks found no `SPRING_DATASOURCE_URL`, `SPRING_PROFILES_ACTIVE`,
`RESEND_API_KEY`, or `CLOUDINARY_URL`; values were not printed.

The registration code queues welcome and verification email messages through
`EmailService.queue` and `OutboxService.appendEmail`
(`.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/service/AuthService.java:106-120`,
`.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/service/EmailService.java:59-71`,
`.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/service/OutboxService.java:37-49`). The outbox relay's
initial delay comes from the one-year test-profile setting
(`.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/service/OutboxRelay.java:53-55`),
so queued messages remain in H2 during this brief test.
`.dxa/a04-kadrom-source/hotelapp/src/main/resources/application.yml:147-155`
maps an absent `RESEND_API_KEY` to an empty
Resend key, and `EmailService.send` treats a missing key as no-send dev mode
(`.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/service/EmailService.java:79-85`).
The profile has a test OAuth registration only;
the registration flow under test does not call that provider. This established
that the test would not contact an external mail/storage/provider service.

### One registration and one login

One temporary focused JUnit test used the existing H2 `test` profile. It sent
exactly one candidate registration to `POST /api/auth/register`
(`.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/controller/AuthController.java:62-70`),
with required terms and privacy-notice fields and a policy-valid 73-byte ASCII
password. The request satisfies the DTO's minimum-length and composition
annotations and supplies its required role and consent values
(`.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/dto/RegisterRequest.java:20-38,63-72`).
It then sent exactly one `POST /api/auth/login`
(`AuthController.java:74-85`) for that synthetic account using the same first
72 ASCII bytes and a different final ASCII byte. No other registration or
login request was made.

Observed: registration returned **200**; the subsequent login returned **200**
and the response principal matched the account ID returned at registration.
The focused run reports **1 test passed, 0 failures, 0 errors, 0 skipped**.
The actual registration path therefore accepted this 73-byte input, and the
different-suffix login authenticated as that newly registered account.

The temporary test source, input values, response bodies, access token,
refresh cookie, and generated email-verification token were not retained in
this audit; only statuses and the same-principal boolean are recorded. The
messages and verification token were transient H2 data. The temporary JUnit
source was removed after the run; the Kadrom checkout was confirmed clean at
the pinned commit and the test-source path was confirmed absent. Ignored Maven
`target/` output remains local and is not part of the Kadrom working tree.

The un-escalated offline Maven attempt failed during test compilation while
reading the cached Spring Boot starter JAR (`Access denied`); no application
request ran in that attempt. The same focused command completed under the
platform escalation flow using offline Maven 3.9.16, Java 17.0.18, Spring Boot
3.2.5, and H2 `jdbc:h2:mem:hotel_test`. Surefire records 1/0/0/0. This was a
temporary generic delegated invocation; native custom-role invocation was not
independently verified. No full product or toolkit suite and no CI workflow
were run.

### Interpretation

This strengthens the earlier direct-hash login check: it now separately
demonstrates that the configured registration endpoint accepted the tested
73-byte synthetic value and that one other value sharing its first 72 bytes
logged into the resulting account. It remains a bounded local observation,
not by itself a claim of CVE applicability, exploitable account compromise,
or a product vulnerability. R7/A05 disposition and any source fix remain for
coordinator review.
