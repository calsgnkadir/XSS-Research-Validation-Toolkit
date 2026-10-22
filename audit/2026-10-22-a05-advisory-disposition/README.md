# R7 / A05 — advisory discrepancies and runtime acceptance oracles

**Date:** 2026-10-22. **Toolkit assignment base:** `2bf3b8e` (coordinator
verified local/remote match). **Product:** user-owned Kadrom checkout
`.dxa/a04-kadrom-source`, commit
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`; product HEAD was independently
read and matched. This is public-record/source analysis, not an application
test or a new dependency scan.

## Ownership and evidence

The coordinator invoked `/root/a05_advisory_disposition` with native
`agent_type=xss_security_researcher`, exclusively owning this new file.
The role TOML was read; this does not independently prove runtime loading of
the TOML. AGENTS, ROADMAP, STATUS, VALIDATION, workflow, initial architecture
audit, relevant A05 audits, and evidence contracts were consulted. Shared
files and product sources were preserved. No Docker lifecycle operation,
application start, application request, upload, unusual method, certificate,
build/test, contact or disclosure was performed by this specialist.

Expected: a current primary clarification might resolve the two old-version
range disagreements. Observed: both global GHSA pages and Spring vendor pages
were retrievable, but their version statements still disagree for the pinned
branches. No explicit authoritative branch clarification was obtained.

## Current primary records and exact relevant predicates

All links below were retrieved with the web tool on 2026-10-22. Retrieved
page content was available; the tool did not expose origin HTTP status or
response headers, so no fresh origin HTTP 200 claim is made.

| Record | Current statements relevant to pinned version | Bounded disposition |
|---|---|---|
| [GHSA-mgvc-8q2h-5pgc](https://github.com/advisories/GHSA-mgvc-8q2h-5pgc), CVE-2026-22733 | Maven package `org.springframework.boot:spring-boot-starter-actuator`; structured affected interval `>=3.0.0, <=3.3.13` contains 3.2.5. Its narrative enumerates 3.3.0–3.3.17 but omits 3.2.x. | Database version match persists; this record internally gives different branch coverage. |
| [Spring CVE-2026-22733](https://spring.io/security/cve-2026-22733/) | Enumerates Boot 4.0.0–4.0.3, 3.5.0–3.5.11, 3.4.0–3.4.14, 3.3.0–3.3.17 and <=2.7.31; no 3.2.x line. Requires a web app with Actuator, Security and an authenticated application handler beneath a Cloud Foundry Actuator subpath. | Omission does not establish that 3.2.5 is unaffected. A branch-specific disposition remains unresolved. |
| [GHSA-293q-567p-wmwq](https://github.com/advisories/GHSA-293q-567p-wmwq), CVE-2026-47838 | Maven package `org.springframework.security:spring-security-web`; structured affected interval `>=6.0.0, <=6.3.10` contains 6.2.4. Its narrative lists enterprise 6.3.0–6.3.17 and later 6.x lines, plus 5.x, and omits 6.2.x. | Database version match persists; narrative omission does not decide applicability. |
| [Spring CVE-2026-47838](https://spring.io/security/cve-2026-47838/) | Enumerates 6.5.0–6.5.10, 6.4.0–6.4.17, 6.3.0–6.3.17, 5.8.0–5.8.26 and <=5.7.24. Describes `SubjectDnX509PrincipalExtractor` CN extraction behind pre-authentication, with upstream trust assumptions. | No affirmative 6.2.x disposition. Version disagreement remains unresolved. |

The related [Spring CVE-2026-22747](https://spring.io/security/cve-2026-22747/)
page was also retrieved. It scopes its fix to 7.0.0–7.0.4 and the other
extractor (`SubjectX500PrincipalExtractor`); it does not settle 6.2.4 for
CVE-2026-47838. The repository-specific advisory URL linked through the global
record, [GHSA-2jrg-rf5x-568g](https://github.com/spring-projects/spring-security/security/advisories/GHSA-2jrg-rf5x-568g),
returned a web-tool cache-miss failure; no content was obtained there.

These are dependencies of Kadrom, not advisory identifiers assigned to
Kadrom. No product vulnerability is attributed from the coordinate match.
No maintainer was contacted. Do not replace the disagreement with an assumed
unsupported-branch policy or a source-similarity inference.

## Source conditions already checked

The [prior Actuator source triage](../2026-10-21-r7-actuator-source-triage/README.md)
records the resolved three-artifact Actuator 3.2.5 subtree and a source search
with no protected handler under `/cloudfoundryapplication`. The [remaining
paths review](../2026-10-22-a05-remaining-paths/README.md) records no X.509
pre-authentication setup in the pinned product. These prior source-search
results are retained, not rerun as a full inventory here.

A narrow current read confirmed `SecurityConfig.java:104` declares the filter
chain, `:163-175` permits health/info and restricts other Actuator paths to
ADMIN, `:179` requires authentication otherwise, `:198-199` installs JWT/rate
filters and `:204` configures OAuth2 login. Paths are relative to
`.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/config/`.
This is source evidence, not a runtime handler or certificate-flow test.

## Minimal runtime acceptance oracles for the coordinator

These are proposed acceptance criteria. This specialist did not run them.
Storage owns the separate Docker/runtime work; its actual snapshot and any
ordinary GET outcome must be linked from its own audit before acceptance.

### Micrometer: distinguish configuration, recording and impact

The current [Spring Micrometer advisory](https://spring.io/security/cve-2026-40984/)
includes 1.12.5 in its 1.10.0–1.13.18 affected interval and requires configured
HTTP server instrumentation with metrics recorded through it. Its history
explicitly says unsupported 1.10.x–1.12.x were added on 2026-09-07. This
explicit clarification applies to Micrometer; it cannot be projected onto
the two unrelated discrepancies above.

The [Boot 3.2.5 MVC metrics documentation](https://docs.spring.io/spring-boot/docs/3.2.5/reference/html/actuator.html#actuator.metrics.supported.spring-mvc)
identifies default Spring MVC request instrumentation and the default meter
name `http.server.requests`, with a configurable observation name. Therefore:

1. **Configuration oracle:** record source/image identity, local active
   profiles and narrowly selected effective observation properties; identify
   the `ObservationRegistry`, relevant meter registry and servlet observation
   filter plus its actual registration. A bean of the right type alone does
   not establish registration or recording. Avoid exporting full environment,
   bean properties, credentials, or Actuator config dumps.
2. **Recording oracle:** after the configuration oracle, read the relevant
   timer count for a fixed ordinary local GET route, issue one ordinary GET,
   and read that same timer/tag set again after response completion. Require
   a positive count delta tied to that route/method and no concurrent probe
   traffic. Readback should be in-process or otherwise avoid counting the
   metrics-reader request as the target. A missing/renamed meter or timeout
   is inconclusive until explained; it is not a security success.
3. **Conclusion boundary:** a registered filter plus this delta supports
   effective local HTTP metric recording. It does not establish that an
   unusual HTTP method can create unbounded tags, cause DoS, traverse the
   deployed proxy, or affect production. No unusual method or impact test
   is part of this oracle.

### Multipart/Tomcat: distinguish values from parser behavior

`hotelapp/src/main/resources/application.yml:82-85` currently confirms source
multipart enabled and 20 MB / 25 MB file/request limits. Expected runtime
values should be compared against these declarations, not assumed from them.
The [prior multipart review](../2026-10-22-a05-multipart-config-review/README.md)
contains full affected-coordinate and source-path evidence.

Minimum effective snapshot: active servlet multipart resolver/config element,
max file/request bytes, file-size threshold, resolved multipart location and
servlet temp directory, JVM `java.io.tmpdir`, actual embedded Tomcat version,
connector parameter/body limits and whether a part-count property/API exists.
Resolve blank multipart location against the servlet temp directory. Record
filesystem type/capacity/permissions only for the fresh lab's temp location;
do not read user file contents. An absent getter must be reported as
unsupported/unavailable, never converted to zero or to a later version's
default. Byte limits and parameter limits do not prove a multipart part-count
limit.

The current [Apache Tomcat security page](https://tomcat.apache.org/security-10.html)
places 10.1.20 within the affected intervals for CVE-2025-48988
(10.1.0-M1–10.1.41), CVE-2025-52520 (10.1.0-M1–10.1.42) and
CVE-2025-61795 (10.1.0-M1–10.1.44). These involve part-related resource use,
an unusual upload-limit configuration, and delayed temporary-part cleanup
after errors, respectively. A configuration snapshot, zero threshold, or
empty temp directory does not reproduce parser-error cleanup, prove a leak,
establish an integer-overflow condition or establish availability impact.
The fresh internal local lab also cannot establish production WAF/proxy
multipart parsing; that intermediary prerequisite remains deployment-specific.

## Bounded current product-identity record lookup

One bounded web-tool attempt used the public repository identity
`calsgnkadir/hotel-platform`, product name `Kadrom`, and source artifact
`com.hotelapp:hotel-student-platform:0.0.1-SNAPSHOT` from the [prior identity
record](../2026-10-21-a05-public-records-followup/README.md). These official
API URLs all returned tool-level inaccessible responses, without an origin
status or evaluable JSON/schema/count:

- [NVD keyword Kadrom](https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=Kadrom).
- [NVD repository identity](https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=calsgnkadir%2Fhotel-platform).
- [NVD artifact name](https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=hotel-student-platform).
- [GitHub exact Maven coordinate](https://api.github.com/advisories?ecosystem=maven&affects=com.hotelapp%3Ahotel-student-platform%400.0.1-SNAPSHOT).
- [GitHub repository advisories](https://api.github.com/repos/calsgnkadir/hotel-platform/security-advisories).

A preliminary GitHub global API URL using `keyword=Kadrom` was inaccessible
as well; this review did not validate that parameter as an API search filter
and gives it no query-result weight. No endpoint was repeatedly retried.
**Known-record lookup remains partial/inconclusive**; no zero-result or
absence-of-advisory claim follows. Earlier successful GitHub filtered results
are historical observations, not fresh results in this assignment.

## Disposition

**R7/A05 remains open.** Current official version data preserves two explicit
disagreements, with advisory-specific product routes absent from the prior
bounded source review. Next smallest useful authorized action is the separate
fresh local effective snapshot and ordinary-GET recording oracle described
above. No application tests were run here; no reflection, callback or browser
execution occurred, and no vulnerability impact, remediation or CVE novelty
was verified. Application code/dependencies and Git staging/commits/pushes
were outside this specialist's write scope.
