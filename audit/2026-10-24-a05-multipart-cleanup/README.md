# A05 — bounded malformed multipart cleanup check

Date: 24 October 2026. Toolkit base `b5464b0e20db5ded72346caa1cff79e23a56c87a`.
Kadrom source: `eb031a19f9f6b0715d8b302751542f631216cdd5` (`main`, after a
clean fast-forward from `0ea07ed`). No source or POM in the Kadrom checkout was
changed; the one local untracked regression fixture is preserved here and is
not committed to the Kadrom repository.

## Fixture and command

`MultipartParserCleanupTest.java` runs an embedded loopback Tomcat 11 connector,
the checked-in `MessageController` and `GlobalExceptionHandler`, Spring's real
`StandardServletMultipartResolver`, and mocked message/storage services. The
test uses a fresh JUnit temp directory, a single four-byte inert part under the
wrong field name, and the real attachment route. It makes two small POSTs and
one health GET. No Spring application/database, authentication chain, Docker,
external provider, or old volume is started or contacted.

Reproduce from Kadrom `hotelapp/` with Java 17 and the existing local Maven
installation/cache:

```powershell
mvn -o -ntp -Dmaven.repo.local=<local Maven repository> -Dtest=MultipartParserCleanupTest test
```

The Maven wrapper printed a transient access-denied line on each launch. The
first sandboxed compiler attempt failed reading cached `spring-boot-jdbc` before
the test ran. The elevated retry reached test compilation; two fixture attempts
then ended before requests, one lacking a mock service dependency and one using
the context bean factory before initialization. The final fixture fixed both
setup issues and reached the parser; those earlier results are not parser
observations.

## Observed result

The well-formed control returned 500 because `file` was intentionally absent;
before the generic handler, the selected handler was the real
`MessageController.sendAttachment` and Spring raised
`MissingServletRequestPartException`. At that moment, the temporary spool held
exactly one regular file totaling four bytes. After the response, it was empty.

The incomplete boundary request returned 500 with this cause chain:
`MultipartException` → `IOFileUploadException` → `MalformedStreamException`.
The observation ran before binding/handler selection (`handlerPresent=false`),
and the spool held zero regular files/bytes at the exception. It remained empty
after the response and a following health request returned 200. Message/storage
services had zero interactions; Tomcat was stopped in `finally`.

**Result:** this fixture passed its positive parser control, malformed-parser
oracle, no-handler condition and cleanup checks: **1 test, 0 failures, 0 errors,
0 skipped; BUILD SUCCESS**. Structured, allowlisted observations are in
[result.json](result.json). Maven's full startup/error logs are not retained.
The result records both the original Windows test-file SHA-256 and the
LF-normalized source SHA-256 so checkout line-ending conversion does not obscure
which fixture source was executed.

## Limits and other conditional work

This closes the bounded cleanup question for one tiny truncated request on the
current Tomcat 11/Spring MVC resolver fixture. It does not cover the fully
booted product/auth chain, deployed proxy/runtime settings, large/many-part
requests, all parser error paths, other Tomcat builds or prove a general absence
of resource exhaustion. No vulnerability or CVE conclusion follows. A05 remains
partial for its broader dependency/advisory/product disposition.

A04's recorded selected-route acceptance is complete for its documented list,
work-session and attendance/roster GET paths; it is not product-wide coverage.
K04's documentation review is complete and retains the explicit boundary that
historical Juice Shop fixes were not retested. Their acceptance records are
[A04/A05 current-source regressions](../2026-10-23-a04-a05-current-source-regressions/README.md),
[A04 scope](../2026-10-22-a04-scope-completeness/README.md), and
[K04 follow-up](../2026-10-20-r7-k03-k04-followup/README.md).
