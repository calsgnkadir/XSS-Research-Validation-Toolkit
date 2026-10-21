# Bounded Spring Data Sort check — 2026-10-22

**Roadmap:** R7 / A05
**Review type:** one bounded local H2/MockMvc request
**Toolkit source:** `a20a281c898b430861b9f0539fee444efe0c5965` on `main`
**Kadrom source:** user-owned local checkout, pinned at
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`
**Agent role:** QA + Security Lab Specialist instructions in
`.codex/agents/qa_security_lab_specialist.toml`; temporary generic delegated
agent. Native custom-role invocation was not independently verified.

## Scope and source preflight

The official [Spring advisory](https://spring.io/security/cve-2026-41711/)
describes a potential `StackOverflowException`/DoS when an exposed Spring Data
Commons endpoint parses crafted Sort input. It says exposure depends on the
consumer endpoint and includes untrusted `Sort`, `@ProjectedPayload`, and
`@QuerydslPredicate` paths. GitHub's [GHSA record](https://github.com/advisories/GHSA-5vpf-xvv7-c8vh)
lists Spring Data Commons 3.2.0–3.2.15 among affected prose ranges.

The pinned app uses Spring Boot 3.2.5, whose dependency management resolves the
reviewed Spring Data Commons 3.2.5 (the prior [effective-tree record](../2026-10-21-a05-effective-dependency-tree/README.md)
records the exact coordinate). `ApplicationController.java:45-51` exposes
`GET /api/candidate/applications` with a `Pageable` argument; its method requires
`CANDIDATE` at line 46. `SecurityConfig.java:176` also requires `ROLE_CANDIDATE`
for `/api/candidate/**`. This route is not anonymous: the request used one
synthetic candidate created in the test database.

The active `test` profile uses H2 in-memory and Hibernate `create-drop`, and
disables Flyway (`application-test.yml:1-17`); rate limiting, Cloudinary, and
Resend are disabled there (`:27-30,62-69`). The focused test did not start
Docker, contact an external endpoint/provider, use a real account, or alter
Kadrom source/dependency files.

## Bounded procedure and result

A temporary `@SpringBootTest`/MockMvc test registered one synthetic candidate,
then sent exactly one authenticated GET to the route above with `page=0`,
`size=1`, and one 231-character malformed property path made of 32 repeated
camel-case components. The request ran in a worker with a 2.5-second completion
timeout. A single `GET /actuator/health` followed, with a 2-second timeout.
No repeat, loop, load test, extra candidate, or alternative payload was used.
The synthetic email, credentials, JWT, and response body are not retained here.

Observed: the Sort request completed with **HTTP 500**. The application log
identified `InvalidDataAccessApiUsageException` wrapping Hibernate
`UnknownPathException` for the nonexistent property. It did **not** show
`StackOverflowError`/`StackOverflowException`. The follow-up health request
returned **HTTP 200**. This is a completed bounded request and liveness oracle;
it is not a reproduction of the advisory's stack-overflow/availability effect.
The malformed property causing an HTTP 500 is a separate input-handling
observation, not a confirmed vulnerability or CVE match. The request required a
valid authenticated candidate role, so this run does not establish anonymous
reachability or behavior from other endpoints.

## Runner accounting

Environment: Windows, Java 17.0.18, Maven 3.9.16 offline, Spring Boot 3.2.5,
active `test` profile, H2 `jdbc:h2:mem:hotel_test`. Final command (run from the
pinned `hotelapp` directory):

```powershell
$env:MAVEN_OPTS='-Duser.home=C:\Users\user'
& 'C:\Users\user\.m2\wrapper\dists\apache-maven-3.9.16\56ba1f9f\bin\mvn.cmd' `
  -o -Dtest=SortAdvisoryBoundedCheckTest test
```

The final Surefire result was **1 test, 0 failures, 0 errors, 0 skipped**
(`SortAdvisoryBoundedCheckTest`, elapsed 40.75 seconds including Spring startup).
The single test itself recorded HTTP 500 for the malformed Sort request and
HTTP 200 for health.

Earlier attempts did not produce test results: an un-escalated Maven launch
could not create the default `C:\.m2\repository`; an escalated retry with a
mis-parsed `-Dmaven.repo.local` argument stopped before test compilation; and
the first test compilation stopped on a temporary source UTF-8 BOM. The BOM was
removed and the final offline command above completed. These are runner/source
setup errors, not product behavior, and are not counted as skips or failed
runtime checks.

The temporary test source was removed after the run. Kadrom HEAD still matched
the pinned commit and `git status --short --untracked-files=all` was empty.
Ignored Maven `target/` outputs were left in place; no user data or existing
volume was deleted. No toolkit test suite, full Kadrom suite, or CI job was run.

## Evidence limits and disposition

- Evidence type: one local MockMvc request through the app's test-profile MVC,
  Spring Security, repository, and H2 path, followed by a separate health check.
- No StackOverflow or process-level availability failure was reproduced. HTTP
  500 from this one invalid property does not prove the advisory condition.
- A single bounded value cannot establish safe limits for longer input, other
  endpoints, deployment overrides, concurrent requests, or other Spring Data
  versions.
- No Kadrom fix, permanent regression test, advisory submission, or disclosure
  was performed. R7/A05 remains open pending coordinator review of the remaining
  advisory paths; this observation alone does not close A05 or R7.