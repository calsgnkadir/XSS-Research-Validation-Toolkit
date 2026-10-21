# R7 / A05 — source triage of selected transitive advisory leads

## Scope and method

Read-only source/configuration review of the user-owned Kadrom snapshot at
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`, under the already selected local
research scope. This pass covers only the following resolved Maven artifacts:
`logback-core:1.4.14`, `jackson-core:2.15.4`, `jackson-databind:2.15.4`,
`nimbus-jose-jwt:9.24.4`, `micrometer-core:1.12.5`,
`commons-lang3:3.13.0`, `httpclient:4.4`, and `log4j-api:2.21.1`.
The exact advisory keys came from the positive-controlled deps.dev lookup in
the [transitive lookup audit](../2026-10-21-a05-transitive-advisories/README.md).
Dependency paths and pinned POM identity are in the
[effective-tree audit](../2026-10-21-a05-effective-dependency-tree/README.md).

GHSA descriptions/preconditions were compared against the public GitHub
Advisory Database and, where needed, the upstream maintainer's advisory pages.
The source examined is the pinned checkout's `hotelapp/src/main` and POM.
Evidence below is source/configuration analysis only. No build, test, endpoint,
container, product runtime, external target, or disclosure was used. No source
files in the Kadrom checkout were changed.

## Findings by resolved artifact

| Artifact / advisory keys | Advisory precondition(s) checked | Pinned-source evidence and bounded disposition |
|---|---|---|
| `ch.qos.logback:logback-core:1.4.14` — [GHSA-25qh-j22f-pwp8](https://github.com/advisories/GHSA-25qh-j22f-pwp8), [GHSA-6v67-2wr5-gvf4](https://github.com/advisories/GHSA-6v67-2wr5-gvf4), [GHSA-jhq6-gfmj-v8fx](https://github.com/advisories/GHSA-jhq6-gfmj-v8fx), [GHSA-p47f-322f-whfh](https://github.com/advisories/GHSA-p47f-322f-whfh), [GHSA-pr98-23f8-jwxv](https://github.com/advisories/GHSA-pr98-23f8-jwxv), [GHSA-qqpg-mvqg-649v](https://github.com/advisories/GHSA-qqpg-mvqg-649v) | The records describe conditional configuration-file processing / Janino expression issues (attacker can modify logback configuration or inject configuration-related environment before startup), XML DOCTYPE SSRF through modified Logback XML, and restricted Java object injection when serialized input is sent to `SimpleSocketServer` or `SimpleSSLSocketServer`. | `src/main/resources/logback-spring.xml:14,29-62` has `scan="false"`, fixed `ConsoleAppender` definitions for dev/test/prod, fixed patterns, and no Janino evaluator, socket server, or network appender. It contains no user-controlled configuration path. The source does not evidence that an attacker can write this packaged config or set process environment before application startup. **Absent in reviewed application configuration/source.** This does not prove deployment filesystem/environment protections. |
| `com.fasterxml.jackson.core:jackson-core:2.15.4` — [GHSA-72hv-8253-57qq](https://github.com/advisories/GHSA-72hv-8253-57qq), [GHSA-7hhh-6rmp-j9qf](https://github.com/advisories/GHSA-7hhh-6rmp-j9qf), [GHSA-r7wm-3cxj-wff9](https://github.com/advisories/GHSA-r7wm-3cxj-wff9) | The three keys concern parser-specific denial of service: asynchronous/non-blocking parser number-length constraint bypass (including its chunked-input variant), and excessive error-token accumulation in a specialized parser. | POM lines `36-40` use `spring-boot-starter-web` (Servlet MVC); the reviewed code contains no `JsonFactory`, non-blocking parser, `feedInput`, or custom `jackson-core` parser construction. Jackson databind is used in ordinary typed/object-mapper paths, e.g. `service/OutboxRelay.java:99,107` and `service/WebPushService.java:152`; those are not evidence of the advisory-specific async parser. **Absent in the identified parser configuration.** This was not runtime-confirmed, and a transitive framework implementation path was not traced from dependency source JARs. |
| `com.fasterxml.jackson.core:jackson-databind:2.15.4` — [GHSA-3pjw-73gf-8qr5](https://github.com/advisories/GHSA-3pjw-73gf-8qr5), [GHSA-5gvw-p9qm-jgwh](https://github.com/advisories/GHSA-5gvw-p9qm-jgwh), [GHSA-5jmj-h7xm-6q6v](https://github.com/advisories/GHSA-5jmj-h7xm-6q6v), [GHSA-cxp5-3px4-pw24](https://github.com/advisories/GHSA-cxp5-3px4-pw24), [GHSA-gx83-3vf8-gh7j](https://github.com/advisories/GHSA-gx83-3vf8-gh7j), [GHSA-hgj6-7826-r7m5](https://github.com/advisories/GHSA-hgj6-7826-r7m5), [GHSA-j3rv-43j4-c7qm](https://github.com/advisories/GHSA-j3rv-43j4-c7qm), [GHSA-q4xh-88c3-wmh7](https://github.com/advisories/GHSA-q4xh-88c3-wmh7), [GHSA-rmj7-2vxq-3g9f](https://github.com/advisories/GHSA-rmj7-2vxq-3g9f), [GHSA-vvgp-rfg2-7rr6](https://github.com/advisories/GHSA-vvgp-rfg2-7rr6), [GHSA-wjgm-6hv5-3cvf](https://github.com/advisories/GHSA-wjgm-6hv5-3cvf), [GHSA-wv8q-qhhj-9h54](https://github.com/advisories/GHSA-wv8q-qhhj-9h54) | The keys map to narrowly conditioned databind behaviors: record-property `@JsonIgnore` with a naming strategy; `@JsonView` / `@JsonUnwrapped`; case-insensitive property binding combined with per-property `@JsonIgnoreProperties`; `@JsonIdentityInfo` forward-reference collections/maps; permissive `PolymorphicTypeValidator` variants; deserialization into `InetAddress`/`InetSocketAddress`, `Path`, or XML Schema `Duration`/`XMLGregorianCalendar`; and retention of unknown polymorphic type IDs. | The broad first-party DTO/source scan found no `@JsonView`, `@JsonUnwrapped`, `@JsonIgnoreProperties`, `@JsonIdentityInfo`, `PolymorphicTypeValidator`, default typing, `InetAddress`, `InetSocketAddress`, `XMLGregorianCalendar`, or `java.nio.file.Path` request properties. `RegisterRequest` is a class (`dto/RegisterRequest.java:20`) and its sole `@JsonIgnore` use is on a class property (`:83`), not a record property; this does not satisfy GHSA-3pjw's record precondition. The application uses `java.time.Duration` internally (for example `service/ShiftWindow.java:6,27,58-63`), not the `javax.xml.datatype.Duration` or `XMLGregorianCalendar` deserialization shape in GHSA-q4xh. **Absent for the reviewed advisory-specific DTO/type/configuration preconditions.** The ordinary Spring MVC JSON body path exists, so this is not a claim that Jackson sees no untrusted input. **Version-range note:** the official [GHSA-5gvw-p9qm-jgwh advisory](https://github.com/advisories/GHSA-5gvw-p9qm-jgwh) includes `jackson-databind >=2.0.0-RC1,<2.18.9`; therefore 2.15.4 is an affected-version-range match. The separate advisory-specific source/configuration preconditions reviewed above were not found. |
| `com.nimbusds:nimbus-jose-jwt:9.24.4` — [GHSA-gvpg-vgmx-xg6w](https://github.com/advisories/GHSA-gvpg-vgmx-xg6w), [GHSA-xwmg-2g98-w7v9](https://github.com/advisories/GHSA-xwmg-2g98-w7v9) | GHSA-gvpg concerns a large attacker-controlled JWE `p2c` iteration count reaching Nimbus `PasswordBasedDecrypter` (PBKDF2). GHSA-xwmg concerns excessive recursion while parsing deeply nested JSON. | Nimbus is brought through `spring-boot-starter-oauth2-client` (POM `59-63`; dependency path in the effective-tree audit). OAuth2 login is configured in `config/SecurityConfig.java:203-206`; the custom service calls `DefaultOAuth2UserService.loadUser` at `security/oauth/CustomOAuth2UserService.java:39-41`. The reviewed first-party code has no direct Nimbus parser/decrypter call and no explicit JWE/password-based decryption. The OAuth provider is configured as Google in `resources/application.yml:92-101`. **GHSA-gvpg absent in first-party code. GHSA-xwmg unresolved:** the configured OAuth2 login delegates token/userinfo parsing to Spring Security, but this source-only pass did not establish which Nimbus parser path is reached or whether attacker-controlled deeply nested JSON reaches it. Do not infer an unauthenticated product DoS from the dependency key alone. |
| `io.micrometer:micrometer-core:1.12.5` — [GHSA-g3pr-3p32-fp23](https://github.com/advisories/GHSA-g3pr-3p32-fp23) | The corresponding vendor record is CVE-2026-40984, a DoS from crafted HTTP requests against Micrometer HTTP server instrumentation. The official [GHSA-g3pr-3p32-fp23 advisory](https://github.com/advisories/GHSA-g3pr-3p32-fp23) lists `micrometer-core >=1.10.0,<=1.13.15`, which includes 1.12.5. | Micrometer is present through the Prometheus registry (POM `134-138`); the product has actuator metrics exposure in `resources/application-prod.yml:114-120` and custom metrics in `metrics/AppMetrics.java:17,26,46-47`. These show metrics use, but this source-only pass did not inspect Spring Boot's resolved HTTP server observation auto-configuration or the dependency's instrumented request path. **Version range matches; application source applicability remains unresolved.** Next step: read-only review of the pinned Boot/Micrometer HTTP server path; if that confirms the affected handler is active, consider a bounded request/control validation only in the authorized disposable local lab. |
| `org.apache.commons:commons-lang3:3.13.0` — [GHSA-j288-q9x7-2f5v](https://github.com/advisories/GHSA-j288-q9x7-2f5v) | The advisory describes `ClassUtils.getClass(...)` throwing `StackOverflowError` for very long inputs; its Apache Commons Lang 3 affected range is versions before 3.18.0. | A source-wide `src/main` search found no `org.apache.commons.lang3` import or `ClassUtils.getClass` call. The similarly named call in `service/FileStorageService.java:11,261` is Spring `org.springframework.util.StringUtils.cleanPath`, a different library and operation. **Absent in reviewed first-party code.** The package is transitive; its full internal caller graph was not examined. |
| `org.apache.httpcomponents:httpclient:4.4` — [GHSA-7r82-7xv7-xcpj](https://github.com/advisories/GHSA-7r82-7xv7-xcpj) | The advisory concerns malformed authority parsing when a crafted `java.net.URI` is passed to Apache HttpClient, potentially selecting the wrong request host. | The resolved dependency path is `cloudinary-http44` → Apache HttpClient (effective-tree audit). No first-party Apache `HttpClient`/`HttpClients` API use was found. The push path validates a short allowlisted HTTPS URI in `service/PushEndpointPolicy.java:20-49`, then sends it with the JDK `java.net.http.HttpClient` in `service/WebPushService.java:11-12,48-49,107-120`; it is not passed to Apache HttpClient. Cloudinary's internal request construction was not inspected. **Absent in identified first-party request path; unresolved only for the transitive Cloudinary implementation.** |
| `org.apache.logging.log4j:log4j-api:2.21.1` — [GHSA-qv9r-c865-cp47](https://github.com/advisories/GHSA-qv9r-c865-cp47) | The advisory requires a Log4j JSON-layout path using `MapMessage.asJson()` (or equivalent JSON resolver) and a `MapMessage` containing attacker-controlled NaN/Infinity. | The artifact is pulled by POI as shown in the effective-tree audit; no first-party Log4j API/`MapMessage`/JSON-template-layout use was found. The application's JSON-looking console pattern is configured in Logback at `resources/logback-spring.xml:22-24,48-56`; this is a Logback `ConsoleAppender`, not Log4j `MapMessage` serialization. **Absent in reviewed application logging path.** |

## Disposition and limits

- **Plausible but unresolved source path:** Nimbus deep-nested-JSON advisory
  `GHSA-xwmg-2g98-w7v9`, because OAuth2 login is enabled and delegates parsing
  into Spring Security. The repository does not contain the resolved Spring
  Security/Nimbus implementation source needed to connect the provider response
  to this exact parser behavior. The narrow next check is a read-only review of
  the pinned Spring Security OIDC/OAuth2 implementation path; only if that
  confirms untrusted nested JSON reaches Nimbus would the smallest useful
  validation be a disposable local OAuth2 mock-provider test with a bounded
  nested-JSON control. Do not contact Google or another hosted provider.
- The source tree supports **no reproduced failure, product vulnerability, or
  general safety claim**. No application-level runtime validation was run.
- GHSA-5gvw's official range includes Jackson Databind 2.15.4, and
  GHSA-g3pr's official range includes Micrometer Core 1.12.5. Both are
  affected-version-range matches; source applicability is a separate question:
  the listed Jackson DTO/configuration preconditions were absent in the scan,
  while the Micrometer HTTP instrumentation path remains unresolved. The
  advisory keys alone establish neither exploitability nor a product finding.
- A05/R7 remains open pending the unresolved Nimbus implementation-path review
  and the remaining advisory triage in other dependency groups. No disclosure or
  external test is authorized or recorded here. No tests were run.

## Source references

- [Dependency tree](../2026-10-21-a05-effective-dependency-tree/README.md)
- [deps.dev transitive keys](../2026-10-21-a05-transitive-advisories/README.md)
- [GitHub Advisory Database](https://github.com/advisories)
- [GHSA-5gvw-p9qm-jgwh — Jackson Databind](https://github.com/advisories/GHSA-5gvw-p9qm-jgwh)
- [GHSA-g3pr-3p32-fp23 — Micrometer Core](https://github.com/advisories/GHSA-g3pr-3p32-fp23)
- [Spring CVE-2026-40984 vendor advisory](https://spring.io/security/cve-2026-40984)
- [Apache Commons Lang CVE-2025-48924 record](https://github.com/advisories/GHSA-j288-q9x7-2f5v)
