# R7 / A05 — effective Kadrom runtime dependency tree

## Scope and source identity

Read-only dependency resolution for the selected, user-owned Kadrom source. The
checkout is `.dxa/a04-kadrom-source` at commit
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`; its `hotelapp/pom.xml` SHA-256 is
`AF8E4AED12B15A646460987E2FD94BDA8F31C482537498599A3BB473B5CE8112`. The POM
declares `org.springframework.boot:spring-boot-starter-parent:3.2.5`
(`relativePath` is empty), project `com.hotelapp:hotel-student-platform:0.0.1-SNAPSHOT`,
and Java 17. Maven resolved the parent and its dependency management from the
existing local cache in offline mode.

No source file, POM, lock file, test, application, container, or product endpoint
was changed or run. The subcheckout stayed at the pinned commit and its POM had
no diff after resolution. No dependency or advisory conclusion is made here.

## Command and execution result

The repository's `mvnw.cmd` is a thin wrapper that calls an installed `mvn`; it
does not bootstrap Maven. `mvn` was not on PATH, so the already-cached Maven
3.9.16 executable was invoked directly. The successful command was:

```powershell
& "$env:USERPROFILE\.m2\wrapper\dists\apache-maven-3.9.16\56ba1f9f\bin\mvn.cmd" `
  -o "-Dmaven.repo.local=C:/Users/user/.m2/repository" `
  -f .dxa/a04-kadrom-source/hotelapp/pom.xml `
  org.apache.maven.plugins:maven-dependency-plugin:3.10.0:tree `
  "-Dscope=runtime" -Dverbose
```

Environment: Windows 11 x64, Apache Maven 3.9.16, Maven JVM Eclipse Temurin
Java 17.0.18, Maven dependency plugin 3.10.0. Maven used offline mode and the
existing local repository; it completed **BUILD SUCCESS** in about 6.6 seconds.
The default `runtime` scope includes compile and runtime dependencies and their
transitives, and verbose output records version mediation and duplicate
omissions. This is dependency resolution only: no compile, package, test,
integration test, or endpoint request occurred.

There were unsuccessful setup invocations before the successful one: the first
cache path omitted Maven Wrapper's hash subdirectory; the next used Maven's
unwritable default `C:\.m2\repository`; two corrected invocations exposed
Windows argument parsing issues. The successful invocation explicitly selected
the existing `C:/Users/user/.m2/repository` and completed offline. Those setup
errors do not make the final dependency-tree invocation partial. No downloads
were attempted by the successful invocation.

## Effective direct runtime roots

Versions below are the resolved versions from the successful tree. An explicit
POM version is marked `explicit`; otherwise the version is managed by the
Spring Boot 3.2.5 parent/BOM. Direct POM locations are included for traceability.

| POM line(s) | Coordinate | Effective version | Declared scope / note |
|---|---|---:|---|
| 29–33 | `org.apache.poi:poi-ooxml` | 5.3.0 | compile; explicit |
| 36–40 | `org.springframework.boot:spring-boot-starter-web` | 3.2.5 | compile; parent managed |
| 42–46 | `org.springframework.boot:spring-boot-starter-websocket` | 3.2.5 | compile; parent managed |
| 53–57 | `org.springframework.boot:spring-boot-starter-security` | 3.2.5 | compile; parent managed |
| 59–63 | `org.springframework.boot:spring-boot-starter-oauth2-client` | 3.2.5 | compile; parent managed |
| 65–69 | `org.springframework.boot:spring-boot-starter-data-jpa` | 3.2.5 | compile; parent managed |
| 71–75 | `org.springframework.boot:spring-boot-starter-validation` | 3.2.5 | compile; parent managed |
| 77–82 | `com.mysql:mysql-connector-j` | 8.3.0 | runtime; parent managed |
| 86–90 | `org.flywaydb:flyway-core` | 9.22.3 | compile; parent managed |
| 91–94 | `org.flywaydb:flyway-mysql` | 9.22.3 | compile; parent managed |
| 96–101 | `io.jsonwebtoken:jjwt-api` | 0.12.5 | compile; explicit property `jjwt.version` |
| 102–107 | `io.jsonwebtoken:jjwt-impl` | 0.12.5 | runtime; explicit property `jjwt.version` |
| 108–113 | `io.jsonwebtoken:jjwt-jackson` | 0.12.5 | runtime; explicit property `jjwt.version` |
| 115–120 | `com.bucket4j:bucket4j-core` | 8.10.1 | compile; explicit |
| 123–128 | `io.github.resilience4j:resilience4j-spring-boot3` | 2.2.0 | compile; explicit |
| 129–132 | `org.springframework.boot:spring-boot-starter-actuator` | 3.2.5 | compile; parent managed |
| 134–138 | `io.micrometer:micrometer-registry-prometheus` | 1.12.5 | compile; parent managed |
| 140–145 | `com.cloudinary:cloudinary-http44` | 1.36.0 | compile; explicit |
| 147–152 | `org.springdoc:springdoc-openapi-starter-webmvc-ui` | 2.5.0 | compile; explicit |
| 154–159 | `org.projectlombok:lombok` | 1.18.32 | compile, optional; parent managed |
| 191–195 | `com.iyzipay:iyzipay-java` | 2.0.129 | compile; explicit |

The Lombok row reflects Maven's resolved project dependency graph. The POM also
marks it optional and configures the Spring Boot Maven plugin to exclude Lombok
from repackaged output (POM lines 200–214); no package was built here, so the
packaged artifact was not checked.

## Resolved paths and mediation examples

The following edges are copied from the successful verbose tree; scopes shown
are the effective tree scopes. They demonstrate why an explicit-version-only
inventory misses dependencies and parent-managed versions:

| Dependency path | Effective coordinates / scopes |
|---|---|
| `poi-ooxml` → `poi` → `commons-codec` | `org.apache.poi:poi-ooxml:5.3.0:compile` → `org.apache.poi:poi:5.3.0:compile` → `commons-codec:commons-codec:1.16.1:compile` (managed down from 1.17.0) |
| `poi-ooxml` → `poi` → Log4j API | `org.apache.poi:poi:5.3.0:compile` → `org.apache.logging.log4j:log4j-api:2.21.1:compile` (managed down from 2.23.1) |
| `poi-ooxml` → `poi-ooxml-lite` → XMLBeans | `org.apache.poi:poi-ooxml-lite:5.3.0:compile` → `org.apache.xmlbeans:xmlbeans:5.2.1:compile` |
| web starter → Tomcat | `org.springframework.boot:spring-boot-starter-web:3.2.5:compile` → `org.springframework.boot:spring-boot-starter-tomcat:3.2.5:compile` → `org.apache.tomcat.embed:tomcat-embed-core:10.1.20:compile` |
| web starter → Spring MVC | `org.springframework.boot:spring-boot-starter-web:3.2.5:compile` → `org.springframework:spring-webmvc:6.1.6:compile` |
| JPA starter → Hibernate | `org.springframework.boot:spring-boot-starter-data-jpa:3.2.5:compile` → `org.hibernate.orm:hibernate-core:6.4.4.Final:compile` |
| OAuth client → JOSE | `org.springframework.boot:spring-boot-starter-oauth2-client:3.2.5:compile` → `org.springframework.security:spring-security-oauth2-jose:6.2.4:compile` → `com.nimbusds:nimbus-jose-jwt:9.24.4:compile` |
| Flyway MySQL → Flyway core | `org.flywaydb:flyway-mysql:9.22.3:compile` → `org.flywaydb:flyway-core:9.22.3:compile` |
| Cloudinary client → Apache HttpClient | `com.cloudinary:cloudinary-http44:1.36.0:compile` → `org.apache.httpcomponents:httpclient:4.4:compile` → `org.apache.httpcomponents:httpcore:4.4.16:compile` |
| Springdoc UI → Swagger UI | `org.springdoc:springdoc-openapi-starter-webmvc-ui:2.5.0:compile` → `org.webjars:swagger-ui:5.13.0:compile` |
| Resilience4j starter → circuit breaker | `io.github.resilience4j:resilience4j-spring-boot3:2.2.0:compile` → `io.github.resilience4j:resilience4j-spring6:2.2.0:compile` → `io.github.resilience4j:resilience4j-circuitbreaker:2.2.0:compile` |

The verbose tree also reports Maven's nearest/managed-version decisions, such
as Springdoc's requested Jackson 2.16.2 nodes resolving to 2.15.4 and duplicate
nodes omitted after mediation. The successful command is the reproducible full
runtime tree; this audit keeps selected paths and all direct roots rather than
copying the lengthy complete console tree.

### Filtered Actuator subtree follow-up

At the request of the coordinator, the same pinned POM/source and local
repository were queried again with this bounded offline filter:

```powershell
& "$env:USERPROFILE\.m2\wrapper\dists\apache-maven-3.9.16\56ba1f9f\bin\mvn.cmd" `
  -o "-Dmaven.repo.local=C:/Users/user/.m2/repository" `
  -f .dxa/a04-kadrom-source/hotelapp/pom.xml `
  org.apache.maven.plugins:maven-dependency-plugin:3.10.0:tree `
  "-Dscope=runtime" "-Dincludes=org.springframework.boot:spring-boot-actuator*" -Dverbose
```

It completed **BUILD SUCCESS** (Maven 3.9.16, dependency plugin 3.10.0; about
6.1 seconds; offline; no tests/build/package/network). The complete matching
path in the output was:

```text
com.hotelapp:hotel-student-platform:0.0.1-SNAPSHOT
└─ org.springframework.boot:spring-boot-starter-actuator:3.2.5:compile
   └─ org.springframework.boot:spring-boot-actuator-autoconfigure:3.2.5:compile
      └─ org.springframework.boot:spring-boot-actuator:3.2.5:compile
```

Thus the runtime graph resolves the starter, auto-configuration artifact and
Actuator core all at 3.2.5, with the latter two transitively reached from the
direct starter. This is dependency-path evidence only; it is not an advisory
match/absence assessment.

## Exclusions and status

- `spring-boot-devtools`, `spring-boot-starter-test`, `spring-security-test`,
  and `com.h2database:h2` are POM `test` scope and were excluded by
  `-Dscope=runtime` (POM lines 164–188).
- Maven build plugins and their dependencies are not project runtime
  dependencies and are not in this tree.
- No advisory database was queried in this task. No CVE/GHSA/OSV record was
  matched or ruled out, and no vulnerability or safety conclusion follows.
- Tree completeness: **complete for the pinned POM's effective compile/runtime
  dependency graph resolvable from the existing Maven cache**; test scope,
  plugin graphs, unavailable repositories/versions not needed by this POM, and
  packaged-artifact contents are outside this run. Offline resolution and the
  successful Maven exit establish this bounded graph, not a general supply-chain
  assessment.

R7/A05 may now use this resolved direct-plus-transitive coordinate set for a
separate advisory lookup. Prior GitHub Advisory and OSV attempts remain
inconclusive and are not upgraded by this dependency-tree result. No tests were
run.
