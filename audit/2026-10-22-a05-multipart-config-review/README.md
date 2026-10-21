# R7 / A05 — multipart and Tomcat configuration preflight

**Date:** 2026-10-22
**Review type:** bounded read-only source/configuration analysis
**Toolkit source:** `a20a281c898b430861b9f0539fee444efe0c5965` (`main`; local `origin/main` matched at assignment)
**Product source:** user-owned Kadrom checkout `.dxa/a04-kadrom-source`, pinned at `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`
**Roadmap:** R7 / A05

## Scope and method

Reviewed the pinned POM and Maven dependency-tree audit, base and production Spring configuration, upload controller/service/storage paths, and checked-in local/production deployment manifests. Compared the version and required conditions against the official Spring and Apache Tomcat advisories linked below. This is source/configuration evidence only. No Kadrom build, test, application start, request, Docker action, provider call, or source/dependency edit was performed. Existing shared-worktree edits were left untouched; this task created only this audit file.

The assigned QA specialist role was selected by the coordinator's agent invocation. This review does not independently prove that the role TOML was loaded by the runtime.

## Dependency and source evidence

The pinned POM sets Spring Boot parent 3.2.5 (`hotelapp/pom.xml:9-14`). The existing offline Maven dependency-tree audit resolves the servlet stack to `spring-webmvc:6.1.6` and `tomcat-embed-core:10.1.20` (`audit/2026-10-21-a05-effective-dependency-tree/README.md`, “Resolved paths and mediation examples”). These versions are within the official affected ranges for the advisories considered here. A range match is not proof that the advisory's deployment-specific or parser-specific conditions hold.

Relevant pinned source:

| File and lines | Evidence |
|---|---|
| `hotelapp/src/main/resources/application.yml:81-85` | Servlet multipart is enabled; configured maximum file size is 20 MB and maximum request size is 25 MB. |
| `hotelapp/src/main/resources/application-prod.yml:81-85` | Production profile repeats the same enabled/20 MB/25 MB values. |
| `hotelapp/src/main/java/com/hotelapp/controller/MessageController.java:104-115` | Authenticated `POST /conversations/{conversationId}/attachment` consumes `multipart/form-data`, binds a required `file` part and optional `caption`, then calls the service. |
| `hotelapp/src/main/java/com/hotelapp/service/MessageService.java:294-305` | The service checks conversation membership/block state and then sends the parsed file to storage. |
| `hotelapp/src/main/java/com/hotelapp/service/FileStorageService.java:45-46,52-55,252-275` | Service-level 15 MB attachment and 10 MB image limits, extension checks, and magic-byte checks. These run after servlet multipart parsing has produced a `MultipartFile`; they do not cap parser work before that point. |
| `docker-compose.yml:26-46` | The checked-in local stack sets `SPRING_PROFILES_ACTIVE=dev,demo`; no multipart override is shown in the inspected backend environment block. |
| `deploy/prod/docker-compose.prod.yml:45-65` and `deploy/fly/backend.fly.toml:19-49` | Checked-in production examples select `prod` and list deployment variables; no multipart override is present in the inspected sections. |

SHA-256 values for the reviewed product files (paths relative to `.dxa/a04-kadrom-source`):

| File | SHA-256 |
|---|---|
| `hotelapp/pom.xml` | `AF8E4AED12B15A646460987E2FD94BDA8F31C482537498599A3BB473B5CE8112` |
| `hotelapp/src/main/resources/application.yml` | `2AC8088C1BD346174B851D2EDD046A6303B8BF0A77035EC6A272B247840E1D76` |
| `hotelapp/src/main/resources/application-prod.yml` | `CEAA25212A67FABB4CAEC3EA8D67D73E2B32BC854F43A312E361669DF2A07799` |
| `hotelapp/src/main/java/com/hotelapp/controller/MessageController.java` | `EA77EFD19302CDB2E1BB3EDBD3CCC85A2DE609763512E48F2B3F5C05A56D8D0B` |
| `hotelapp/src/main/java/com/hotelapp/service/MessageService.java` | `CD34B413E8923412094B58F1852842EFD5FB231DB87BE2182CA0448AAD04D50D` |
| `hotelapp/src/main/java/com/hotelapp/service/FileStorageService.java` | `552BA7E92E883FD9B04EBA0A87AB647523D326F016C21D2F6637FE1773775310` |

## Advisory-specific preconditions

### Tomcat multipart part-count resource use — CVE-2025-48988 / GHSA-h3gc-qfqq-6h8f

Apache describes excessive memory use from a specially crafted multipart request with a large number of parts. Its fixed release introduced connector `maxPartCount`, with a default of 10 parts. Kadrom uses multipart and the resolved Tomcat 10.1.20 is in the affected range. The configured 20 MB per-file and 25 MB per-request byte limits do **not** establish a part-count limit. No `maxPartCount` / part-count connector setting appears in the checked application YAML or checked-in deployment snippets. Because the pinned Tomcat predates the fix that added this control, a later connector default cannot be projected onto 10.1.20. The exact effective request-parameter/part count and resource behavior remain unknown without the deployed connector/runtime configuration.

**Disposition:** version and multipart feature path confirmed; part-count bound and practical resource impact unresolved. This is not a reproduced DoS or confirmed product vulnerability.

### Tomcat multipart size-limit overflow — CVE-2025-52520 / GHSA-wr62-c79q-cv37

Apache limits this advisory to “some unlikely configurations” in multipart upload where an integer overflow can bypass size limits. Kadrom's source sets byte ceilings, but the advisory's exact configuration condition is not described in enough detail in the checked source to determine applicability. No relevant Tomcat connector customization is present in the inspected YAML/deployment snippets. Source-visible application byte limits do not rule out or establish the affected Tomcat configuration, and the service-level limits run after parsing.

**Disposition:** affected dependency and multipart path confirmed; advisory-specific configuration condition unresolved. No limit bypass or malformed body was attempted.

### Tomcat temporary-part cleanup after parse errors — CVE-2025-61795 / GHSA-hgrr-935x-pq79

Apache describes disk-backed temporary multipart parts that, after an error during processing (including a limit error), may remain until garbage collection removes them; impact depends on JVM settings, memory use, application load, and temporary-file growth relative to cleanup. The pinned Tomcat 10.1.20 is in the affected range and the app accepts multipart requests. The checked YAML does not declare `file-size-threshold`, a multipart temp `location`, or an application-specific Tomcat part-storage setting. Thus the effective memory/disk threshold, temp directory/capacity, cleanup timing, JVM behavior, and actual deployment load are not established. A file rejected by `FileStorageService` is rejected only after parsing, but that fact alone does not exercise Tomcat's parser-error cleanup path.

**Disposition:** version and feature path confirmed; disk-backed temp use and cleanup/availability preconditions unresolved. No parser error or repeated upload was generated.

### Spring MVC multipart request smuggling — CVE-2026-41853 / GHSA-cjpg-rgq5-fr37

The official Spring vendor advisory requires all of: Spring MVC or WebFlux, accepted multipart requests, and a protecting WAF/proxy that parses multipart bodies and checks their contents. Pinned `spring-webmvc:6.1.6` falls in the vendor's 6.1.0–6.1.27 affected line, and `MessageController.java:104-115` accepts multipart. The remaining WAF/proxy precondition is not provable from the checked application source. Production comments and checked-in deployment examples indicate proxy-based hosting, but do not establish that any deployed proxy parses multipart or applies content checks. The reviewed repository does not include the effective external proxy/WAF policy for every deployment.

**Disposition:** framework and multipart conditions confirmed; the necessary intermediary condition is unknown. Without evidence of that intermediary behavior, no request-smuggling behavior can be inferred. No crafted multipart request was sent.

## Limits and smallest useful follow-up

The two configured byte limits are source facts, not verified effective runtime values. Environment/system-property overrides, container connector customizers, proxy body handling, JVM options, temp filesystem, and actual deployment configuration may differ. The checked-in deployment examples are not proof of deployed settings. No `file-size-threshold` or `location` is set in the two YAML files, so this review does not assert whether upload parts are held in memory or written to disk under the effective Boot/Tomcat runtime.

A single **read-only effective-configuration inspection** in an isolated local instance is justified if A05 needs to narrow these conditions: capture resolved Spring multipart properties, Tomcat connector part-related settings, JVM temp directory and relevant proxy/WAF facts without sending a request or exposing secrets. That inspection alone would not establish parser error cleanup behavior or Spring request-smuggling impact. A valid small upload is not useful for those advisory-specific conditions; a malformed/boundary request, size bypass, repeated upload, or exhaustion attempt is not recommended on the current evidence. For the Spring advisory, first establish whether the specific deployed intermediary parses multipart and performs content-based checks; if none does, the vendor's stated prerequisite is absent for that deployment.

## Roadmap disposition

This contributes only source/configuration triage to **R7 / A05**. It narrows the conclusion to an affected-version multipart path with three Tomcat conditions unresolved and the Spring WAF/proxy condition unverified. No runtime test result, vulnerability confirmation, exploitation, remediation, or disclosure is claimed. A05 and R7 remain open; any Kadrom code change requires separate target-change authorization under the roadmap.

## Official primary advisory sources

- [Apache Tomcat CVE-2025-48988](https://tomcat.apache.org/security-10.html) (Tomcat 10 security page; multipart part-count description and fix).
- [GitHub Advisory GHSA-h3gc-qfqq-6h8f](https://github.com/advisories/GHSA-h3gc-qfqq-6h8f).
- [Apache Tomcat CVE-2025-52520](https://tomcat.apache.org/security-10.html) (Tomcat 10 security page; multipart size-limit overflow and affected range).
- [GitHub Advisory GHSA-wr62-c79q-cv37](https://github.com/advisories/GHSA-wr62-c79q-cv37).
- [Apache Tomcat CVE-2025-61795](https://tomcat.apache.org/security-10.html) (Tomcat 10 security page; delayed multipart temporary-file cleanup).
- [GitHub Advisory GHSA-hgrr-935x-pq79](https://github.com/advisories/GHSA-hgrr-935x-pq79).
- [Spring vendor CVE-2026-41853](https://spring.io/security/cve-2026-41853/) (explicit three-condition prerequisite).
- [GitHub Advisory GHSA-cjpg-rgq5-fr37](https://github.com/advisories/GHSA-cjpg-rgq5-fr37).
