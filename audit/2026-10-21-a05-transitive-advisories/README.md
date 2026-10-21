# R7 / A05 — deps.dev transitive runtime advisory lookup

## Scope and source identity

Read-only known-record lookup against the pinned Kadrom source described in the
[effective dependency-tree audit](../2026-10-21-a05-effective-dependency-tree/README.md):
commit `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`, Maven project
`com.hotelapp:hotel-student-platform:0.0.1-SNAPSHOT`. No application, product
endpoint, test, or disclosure was involved.

The official stable deps.dev v3 `GetVersion` route returns version metadata and
advisory keys. Route details are in [API v3 GetVersion](https://docs.deps.dev/api/v3/#getversion)
and the [official API protocol](https://github.com/google/deps.dev/blob/main/api/v3/api.proto).
Each Maven coordinate was requested serially using
`GET https://api.deps.dev/v3/systems/MAVEN/packages/{URL-encoded-group:artifact}/versions/{version}`.

## Positive control gate

Before querying any transitive coordinate, a fresh request was made through
that exact route for the Maven control `org.apache.logging.log4j:log4j-core@2.14.1`.
The run proceeded only after the returned key matched and expected
`GHSA-3pxv-7cmr-fjr4` was present.

| UTC start | UTC end | Result | Returned key | Advisory count / control key |
|---|---|---|---|---|
| 2026-10-21T20:23:30.7923055Z | 2026-10-21T20:23:31.2457116Z | Passed | `MAVEN:org.apache.logging.log4j:log4j-core@2.14.1` | 7; expected `GHSA-3pxv-7cmr-fjr4` present |

## Runtime tree extraction and lookup result

The pinned POM's effective compile/runtime dependency tree was regenerated
offline with cached Maven 3.9.16 and dependency plugin 3.10.0. The dependency
tree invocation completed **BUILD SUCCESS**. Its text output contained 148
effective dependency nodes, including 21 direct roots (Lombok is marked
optional in the tree). After excluding all 21 direct roots already queried in
the previous direct-advisory audit, 127 unique transitive `group:artifact@version`
coordinates remained. Those 127 were queried once each in lexical order with a
500 ms pause between requests. There was no query cap.

| Measure | Result |
|---|---:|
| Transitive coordinates attempted | 127 |
| Successful exact `versionKey` matches | 127 |
| API errors | 0 |
| Returned-key mismatches / unresolved Maven nodes | 0 |
| Rows with one or more advisory keys | 18 |
| Rows with no returned advisory keys | 109 |
| Advisory-key associations across rows | 93 |
| Distinct advisory IDs across rows | 92 |

Every row below gives request-start UTC, requested coordinate/version, exact
returned version key, and the complete `advisoryKeys` list (or zero keys).
Successful responses had no error. Because the API returned exact keys for all
127 requests, no runtime coordinate from this effective Maven tree failed to
map through this endpoint.

| UTC start | Requested coordinate@version | Returned version key | Count | Advisory keys |
|---|---|---|---:|---|

| 2026-10-21T20:25:15.9907560Z | `ch.qos.logback:logback-classic@1.4.14` | `MAVEN:ch.qos.logback:logback-classic@1.4.14` | 0 | — |
| 2026-10-21T20:25:16.9218643Z | `ch.qos.logback:logback-core@1.4.14` | `MAVEN:ch.qos.logback:logback-core@1.4.14` | 6 | GHSA-25qh-j22f-pwp8, GHSA-6v67-2wr5-gvf4, GHSA-jhq6-gfmj-v8fx, GHSA-p47f-322f-whfh, GHSA-pr98-23f8-jwxv, GHSA-qqpg-mvqg-649v |
| 2026-10-21T20:25:17.5148433Z | `com.cloudinary:cloudinary-core@1.36.0` | `MAVEN:com.cloudinary:cloudinary-core@1.36.0` | 0 | — |
| 2026-10-21T20:25:18.1128377Z | `com.fasterxml.jackson.core:jackson-annotations@2.15.4` | `MAVEN:com.fasterxml.jackson.core:jackson-annotations@2.15.4` | 0 | — |
| 2026-10-21T20:25:18.6891079Z | `com.fasterxml.jackson.core:jackson-core@2.15.4` | `MAVEN:com.fasterxml.jackson.core:jackson-core@2.15.4` | 3 | GHSA-72hv-8253-57qq, GHSA-7hhh-6rmp-j9qf, GHSA-r7wm-3cxj-wff9 |
| 2026-10-21T20:25:19.2798796Z | `com.fasterxml.jackson.core:jackson-databind@2.15.4` | `MAVEN:com.fasterxml.jackson.core:jackson-databind@2.15.4` | 12 | GHSA-3pjw-73gf-8qr5, GHSA-5gvw-p9qm-jgwh, GHSA-5jmj-h7xm-6q6v, GHSA-cxp5-3px4-pw24, GHSA-gx83-3vf8-gh7j, GHSA-hgj6-7826-r7m5, GHSA-j3rv-43j4-c7qm, GHSA-q4xh-88c3-wmh7, GHSA-rmj7-2vxq-3g9f, GHSA-vvgp-rfg2-7rr6, GHSA-wjgm-6hv5-3cvf, GHSA-wv8q-qhhj-9h54 |
| 2026-10-21T20:25:19.8823725Z | `com.fasterxml.jackson.dataformat:jackson-dataformat-toml@2.15.4` | `MAVEN:com.fasterxml.jackson.dataformat:jackson-dataformat-toml@2.15.4` | 0 | — |
| 2026-10-21T20:25:20.4743082Z | `com.fasterxml.jackson.dataformat:jackson-dataformat-yaml@2.15.4` | `MAVEN:com.fasterxml.jackson.dataformat:jackson-dataformat-yaml@2.15.4` | 0 | — |
| 2026-10-21T20:25:21.0528162Z | `com.fasterxml.jackson.datatype:jackson-datatype-jdk8@2.15.4` | `MAVEN:com.fasterxml.jackson.datatype:jackson-datatype-jdk8@2.15.4` | 0 | — |
| 2026-10-21T20:25:21.6322405Z | `com.fasterxml.jackson.datatype:jackson-datatype-jsr310@2.15.4` | `MAVEN:com.fasterxml.jackson.datatype:jackson-datatype-jsr310@2.15.4` | 0 | — |
| 2026-10-21T20:25:22.2252135Z | `com.fasterxml.jackson.module:jackson-module-parameter-names@2.15.4` | `MAVEN:com.fasterxml.jackson.module:jackson-module-parameter-names@2.15.4` | 0 | — |
| 2026-10-21T20:25:22.8053640Z | `com.fasterxml:classmate@1.6.0` | `MAVEN:com.fasterxml:classmate@1.6.0` | 0 | — |
| 2026-10-21T20:25:23.4002217Z | `com.github.stephenc.jcip:jcip-annotations@1.0-1` | `MAVEN:com.github.stephenc.jcip:jcip-annotations@1.0-1` | 0 | — |
| 2026-10-21T20:25:23.9924425Z | `com.github.virtuald:curvesapi@1.08` | `MAVEN:com.github.virtuald:curvesapi@1.08` | 0 | — |
| 2026-10-21T20:25:24.5850322Z | `com.google.code.gson:gson@2.10.1` | `MAVEN:com.google.code.gson:gson@2.10.1` | 0 | — |
| 2026-10-21T20:25:25.2366036Z | `com.nimbusds:content-type@2.2` | `MAVEN:com.nimbusds:content-type@2.2` | 0 | — |
| 2026-10-21T20:25:25.8284281Z | `com.nimbusds:lang-tag@1.7` | `MAVEN:com.nimbusds:lang-tag@1.7` | 0 | — |
| 2026-10-21T20:25:26.4173869Z | `com.nimbusds:nimbus-jose-jwt@9.24.4` | `MAVEN:com.nimbusds:nimbus-jose-jwt@9.24.4` | 2 | GHSA-gvpg-vgmx-xg6w, GHSA-xwmg-2g98-w7v9 |
| 2026-10-21T20:25:27.0131233Z | `com.nimbusds:oauth2-oidc-sdk@9.43.3` | `MAVEN:com.nimbusds:oauth2-oidc-sdk@9.43.3` | 0 | — |
| 2026-10-21T20:25:27.6106758Z | `com.sun.istack:istack-commons-runtime@4.1.2` | `MAVEN:com.sun.istack:istack-commons-runtime@4.1.2` | 0 | — |
| 2026-10-21T20:25:28.2336906Z | `com.zaxxer:HikariCP@5.0.1` | `MAVEN:com.zaxxer:HikariCP@5.0.1` | 0 | — |
| 2026-10-21T20:25:28.8098221Z | `com.zaxxer:SparseBitSet@1.3` | `MAVEN:com.zaxxer:SparseBitSet@1.3` | 0 | — |
| 2026-10-21T20:25:29.3837672Z | `commons-codec:commons-codec@1.16.1` | `MAVEN:commons-codec:commons-codec@1.16.1` | 0 | — |
| 2026-10-21T20:25:29.9765906Z | `commons-io:commons-io@2.16.1` | `MAVEN:commons-io:commons-io@2.16.1` | 0 | — |
| 2026-10-21T20:25:30.5610273Z | `commons-logging:commons-logging@1.2` | `MAVEN:commons-logging:commons-logging@1.2` | 0 | — |
| 2026-10-21T20:25:31.1517921Z | `io.github.resilience4j:resilience4j-annotations@2.2.0` | `MAVEN:io.github.resilience4j:resilience4j-annotations@2.2.0` | 0 | — |
| 2026-10-21T20:25:31.7426852Z | `io.github.resilience4j:resilience4j-bulkhead@2.2.0` | `MAVEN:io.github.resilience4j:resilience4j-bulkhead@2.2.0` | 0 | — |
| 2026-10-21T20:25:32.3316491Z | `io.github.resilience4j:resilience4j-circuitbreaker@2.2.0` | `MAVEN:io.github.resilience4j:resilience4j-circuitbreaker@2.2.0` | 0 | — |
| 2026-10-21T20:25:32.9119715Z | `io.github.resilience4j:resilience4j-circularbuffer@2.2.0` | `MAVEN:io.github.resilience4j:resilience4j-circularbuffer@2.2.0` | 0 | — |
| 2026-10-21T20:25:33.5058546Z | `io.github.resilience4j:resilience4j-consumer@2.2.0` | `MAVEN:io.github.resilience4j:resilience4j-consumer@2.2.0` | 0 | — |
| 2026-10-21T20:25:34.0828391Z | `io.github.resilience4j:resilience4j-core@2.2.0` | `MAVEN:io.github.resilience4j:resilience4j-core@2.2.0` | 0 | — |
| 2026-10-21T20:25:34.6608767Z | `io.github.resilience4j:resilience4j-framework-common@2.2.0` | `MAVEN:io.github.resilience4j:resilience4j-framework-common@2.2.0` | 0 | — |
| 2026-10-21T20:25:35.2488566Z | `io.github.resilience4j:resilience4j-micrometer@2.2.0` | `MAVEN:io.github.resilience4j:resilience4j-micrometer@2.2.0` | 0 | — |
| 2026-10-21T20:25:35.8374039Z | `io.github.resilience4j:resilience4j-ratelimiter@2.2.0` | `MAVEN:io.github.resilience4j:resilience4j-ratelimiter@2.2.0` | 0 | — |
| 2026-10-21T20:25:36.4439828Z | `io.github.resilience4j:resilience4j-retry@2.2.0` | `MAVEN:io.github.resilience4j:resilience4j-retry@2.2.0` | 0 | — |
| 2026-10-21T20:25:37.0220721Z | `io.github.resilience4j:resilience4j-spring6@2.2.0` | `MAVEN:io.github.resilience4j:resilience4j-spring6@2.2.0` | 0 | — |
| 2026-10-21T20:25:37.6146874Z | `io.github.resilience4j:resilience4j-timelimiter@2.2.0` | `MAVEN:io.github.resilience4j:resilience4j-timelimiter@2.2.0` | 0 | — |
| 2026-10-21T20:25:38.1998768Z | `io.micrometer:micrometer-commons@1.12.5` | `MAVEN:io.micrometer:micrometer-commons@1.12.5` | 0 | — |
| 2026-10-21T20:25:38.7890256Z | `io.micrometer:micrometer-core@1.12.5` | `MAVEN:io.micrometer:micrometer-core@1.12.5` | 1 | GHSA-g3pr-3p32-fp23 |
| 2026-10-21T20:25:39.3839299Z | `io.micrometer:micrometer-jakarta9@1.12.5` | `MAVEN:io.micrometer:micrometer-jakarta9@1.12.5` | 0 | — |
| 2026-10-21T20:25:39.9740875Z | `io.micrometer:micrometer-observation@1.12.5` | `MAVEN:io.micrometer:micrometer-observation@1.12.5` | 0 | — |
| 2026-10-21T20:25:40.5487016Z | `io.prometheus:simpleclient@0.16.0` | `MAVEN:io.prometheus:simpleclient@0.16.0` | 0 | — |
| 2026-10-21T20:25:41.1439806Z | `io.prometheus:simpleclient_common@0.16.0` | `MAVEN:io.prometheus:simpleclient_common@0.16.0` | 0 | — |
| 2026-10-21T20:25:41.7351227Z | `io.prometheus:simpleclient_tracer_common@0.16.0` | `MAVEN:io.prometheus:simpleclient_tracer_common@0.16.0` | 0 | — |
| 2026-10-21T20:25:42.3133082Z | `io.prometheus:simpleclient_tracer_otel@0.16.0` | `MAVEN:io.prometheus:simpleclient_tracer_otel@0.16.0` | 0 | — |
| 2026-10-21T20:25:42.8904148Z | `io.prometheus:simpleclient_tracer_otel_agent@0.16.0` | `MAVEN:io.prometheus:simpleclient_tracer_otel_agent@0.16.0` | 0 | — |
| 2026-10-21T20:25:43.4689336Z | `io.smallrye:jandex@3.1.2` | `MAVEN:io.smallrye:jandex@3.1.2` | 0 | — |
| 2026-10-21T20:25:44.0328308Z | `io.swagger.core.v3:swagger-annotations-jakarta@2.2.21` | `MAVEN:io.swagger.core.v3:swagger-annotations-jakarta@2.2.21` | 0 | — |
| 2026-10-21T20:25:44.6237437Z | `io.swagger.core.v3:swagger-core-jakarta@2.2.21` | `MAVEN:io.swagger.core.v3:swagger-core-jakarta@2.2.21` | 0 | — |
| 2026-10-21T20:25:45.2141781Z | `io.swagger.core.v3:swagger-models-jakarta@2.2.21` | `MAVEN:io.swagger.core.v3:swagger-models-jakarta@2.2.21` | 0 | — |
| 2026-10-21T20:25:45.8027372Z | `jakarta.annotation:jakarta.annotation-api@2.1.1` | `MAVEN:jakarta.annotation:jakarta.annotation-api@2.1.1` | 0 | — |
| 2026-10-21T20:25:46.3774103Z | `jakarta.inject:jakarta.inject-api@2.0.1` | `MAVEN:jakarta.inject:jakarta.inject-api@2.0.1` | 0 | — |
| 2026-10-21T20:25:46.9699094Z | `jakarta.persistence:jakarta.persistence-api@3.1.0` | `MAVEN:jakarta.persistence:jakarta.persistence-api@3.1.0` | 0 | — |
| 2026-10-21T20:25:47.5497956Z | `jakarta.transaction:jakarta.transaction-api@2.0.1` | `MAVEN:jakarta.transaction:jakarta.transaction-api@2.0.1` | 0 | — |
| 2026-10-21T20:25:48.1388987Z | `jakarta.validation:jakarta.validation-api@3.0.2` | `MAVEN:jakarta.validation:jakarta.validation-api@3.0.2` | 0 | — |
| 2026-10-21T20:25:48.7162078Z | `javax.activation:javax.activation-api@1.2.0` | `MAVEN:javax.activation:javax.activation-api@1.2.0` | 0 | — |
| 2026-10-21T20:25:49.2927278Z | `javax.annotation:javax.annotation-api@1.3.2` | `MAVEN:javax.annotation:javax.annotation-api@1.3.2` | 0 | — |
| 2026-10-21T20:25:49.8788079Z | `javax.ejb:javax.ejb-api@3.2` | `MAVEN:javax.ejb:javax.ejb-api@3.2` | 0 | — |
| 2026-10-21T20:25:50.4697500Z | `javax.jms:javax.jms-api@2.0.1` | `MAVEN:javax.jms:javax.jms-api@2.0.1` | 0 | — |
| 2026-10-21T20:25:51.0481470Z | `javax.persistence:javax.persistence-api@2.2` | `MAVEN:javax.persistence:javax.persistence-api@2.2` | 0 | — |
| 2026-10-21T20:25:51.6380454Z | `javax.resource:javax.resource-api@1.7.1` | `MAVEN:javax.resource:javax.resource-api@1.7.1` | 0 | — |
| 2026-10-21T20:25:52.2310576Z | `javax.transaction:javax.transaction-api@1.2` | `MAVEN:javax.transaction:javax.transaction-api@1.2` | 0 | — |
| 2026-10-21T20:25:52.8386033Z | `javax.transaction:jta@1.1` | `MAVEN:javax.transaction:jta@1.1` | 0 | — |
| 2026-10-21T20:25:53.4477505Z | `javax.xml.bind:jaxb-api@2.3.1` | `MAVEN:javax.xml.bind:jaxb-api@2.3.1` | 0 | — |
| 2026-10-21T20:25:54.0404264Z | `net.bytebuddy:byte-buddy@1.14.13` | `MAVEN:net.bytebuddy:byte-buddy@1.14.13` | 0 | — |
| 2026-10-21T20:25:54.6281949Z | `org.antlr:antlr4-runtime@4.13.0` | `MAVEN:org.antlr:antlr4-runtime@4.13.0` | 0 | — |
| 2026-10-21T20:25:55.2217652Z | `org.apache.commons:commons-collections4@4.4` | `MAVEN:org.apache.commons:commons-collections4@4.4` | 0 | — |
| 2026-10-21T20:25:55.7922424Z | `org.apache.commons:commons-compress@1.26.2` | `MAVEN:org.apache.commons:commons-compress@1.26.2` | 0 | — |
| 2026-10-21T20:25:56.3868049Z | `org.apache.commons:commons-lang3@3.13.0` | `MAVEN:org.apache.commons:commons-lang3@3.13.0` | 1 | GHSA-j288-q9x7-2f5v |
| 2026-10-21T20:25:56.9603967Z | `org.apache.commons:commons-math3@3.6.1` | `MAVEN:org.apache.commons:commons-math3@3.6.1` | 0 | — |
| 2026-10-21T20:25:57.5372421Z | `org.apache.httpcomponents:httpclient@4.4` | `MAVEN:org.apache.httpcomponents:httpclient@4.4` | 1 | GHSA-7r82-7xv7-xcpj |
| 2026-10-21T20:25:58.1147406Z | `org.apache.httpcomponents:httpcore@4.4.16` | `MAVEN:org.apache.httpcomponents:httpcore@4.4.16` | 0 | — |
| 2026-10-21T20:25:58.6897355Z | `org.apache.httpcomponents:httpmime@4.4` | `MAVEN:org.apache.httpcomponents:httpmime@4.4` | 0 | — |
| 2026-10-21T20:25:59.2804257Z | `org.apache.logging.log4j:log4j-api@2.21.1` | `MAVEN:org.apache.logging.log4j:log4j-api@2.21.1` | 1 | GHSA-qv9r-c865-cp47 |
| 2026-10-21T20:25:59.8556502Z | `org.apache.logging.log4j:log4j-to-slf4j@2.21.1` | `MAVEN:org.apache.logging.log4j:log4j-to-slf4j@2.21.1` | 0 | — |
| 2026-10-21T20:26:00.4462562Z | `org.apache.poi:poi@5.3.0` | `MAVEN:org.apache.poi:poi@5.3.0` | 0 | — |
| 2026-10-21T20:26:01.0388315Z | `org.apache.poi:poi-ooxml-lite@5.3.0` | `MAVEN:org.apache.poi:poi-ooxml-lite@5.3.0` | 0 | — |
| 2026-10-21T20:26:01.6159373Z | `org.apache.tomcat.embed:tomcat-embed-core@10.1.20` | `MAVEN:org.apache.tomcat.embed:tomcat-embed-core@10.1.20` | 34 | GHSA-23hv-mwm6-g8jf, GHSA-25xr-qj8w-c4vf, GHSA-27hp-xhwr-wr2m, GHSA-3p2h-wqq4-wf4h, GHSA-42wg-hm62-jcwg, GHSA-563x-q5rq-57qp, GHSA-5j33-cvvr-w245, GHSA-5m62-pw8w-7w9f, GHSA-5mp6-jrq3-r938, GHSA-7jqf-v358-p8g7, GHSA-83qj-6fr2-vhqg, GHSA-9m3c-qcxr-9x87, GHSA-9m89-8frq-c98c, GHSA-9xv2-5v5q-p794, GHSA-ff77-26x5-69cr, GHSA-fpj8-gq4v-p354, GHSA-fv25-8xcx-gqjc, GHSA-gcx9-497g-6cp6, GHSA-gqp3-2cvr-x8m3, GHSA-gx5v-xp9w-j4cg, GHSA-h2fw-rfh5-95r3, GHSA-h3gc-qfqq-6h8f, GHSA-h3x4-894j-xpx5, GHSA-h6fc-48rj-7qqh, GHSA-hgrr-935x-pq79, GHSA-mgp5-rv84-w37q, GHSA-r29c-68gh-xp6x, GHSA-rv64-5gf8-9qq8, GHSA-vfww-5hm6-hx2j, GHSA-wc4r-xq3c-5cf3, GHSA-wm9w-rjj3-j356, GHSA-wmwf-9ccg-fff5, GHSA-wr62-c79q-cv37, GHSA-x4m4-345f-5h5g |
| 2026-10-21T20:26:02.2071186Z | `org.apache.tomcat.embed:tomcat-embed-el@10.1.20` | `MAVEN:org.apache.tomcat.embed:tomcat-embed-el@10.1.20` | 0 | — |
| 2026-10-21T20:26:02.8012222Z | `org.apache.tomcat.embed:tomcat-embed-websocket@10.1.20` | `MAVEN:org.apache.tomcat.embed:tomcat-embed-websocket@10.1.20` | 0 | — |
| 2026-10-21T20:26:03.3888283Z | `org.apache.xmlbeans:xmlbeans@5.2.1` | `MAVEN:org.apache.xmlbeans:xmlbeans@5.2.1` | 0 | — |
| 2026-10-21T20:26:03.9835648Z | `org.aspectj:aspectjweaver@1.9.22` | `MAVEN:org.aspectj:aspectjweaver@1.9.22` | 0 | — |
| 2026-10-21T20:26:04.5754874Z | `org.eclipse.angus:angus-activation@2.0.2` | `MAVEN:org.eclipse.angus:angus-activation@2.0.2` | 0 | — |
| 2026-10-21T20:26:05.1520731Z | `org.glassfish.jaxb:jaxb-core@4.0.5` | `MAVEN:org.glassfish.jaxb:jaxb-core@4.0.5` | 0 | — |
| 2026-10-21T20:26:05.7310219Z | `org.glassfish.jaxb:jaxb-runtime@4.0.5` | `MAVEN:org.glassfish.jaxb:jaxb-runtime@4.0.5` | 0 | — |
| 2026-10-21T20:26:06.3198151Z | `org.glassfish.jaxb:txw2@4.0.5` | `MAVEN:org.glassfish.jaxb:txw2@4.0.5` | 0 | — |
| 2026-10-21T20:26:06.9143475Z | `org.hdrhistogram:HdrHistogram@2.1.12` | `MAVEN:org.hdrhistogram:HdrHistogram@2.1.12` | 0 | — |
| 2026-10-21T20:26:07.5057813Z | `org.hibernate.common:hibernate-commons-annotations@6.0.6.Final` | `MAVEN:org.hibernate.common:hibernate-commons-annotations@6.0.6.Final` | 0 | — |
| 2026-10-21T20:26:08.0998587Z | `org.hibernate.orm:hibernate-core@6.4.4.Final` | `MAVEN:org.hibernate.orm:hibernate-core@6.4.4.Final` | 0 | — |
| 2026-10-21T20:26:08.6917981Z | `org.hibernate.validator:hibernate-validator@8.0.1.Final` | `MAVEN:org.hibernate.validator:hibernate-validator@8.0.1.Final` | 0 | — |
| 2026-10-21T20:26:09.2681379Z | `org.jboss.logging:jboss-logging@3.5.3.Final` | `MAVEN:org.jboss.logging:jboss-logging@3.5.3.Final` | 0 | — |
| 2026-10-21T20:26:09.8586003Z | `org.latencyutils:LatencyUtils@2.0.3` | `MAVEN:org.latencyutils:LatencyUtils@2.0.3` | 0 | — |
| 2026-10-21T20:26:10.4361433Z | `org.slf4j:jul-to-slf4j@2.0.13` | `MAVEN:org.slf4j:jul-to-slf4j@2.0.13` | 0 | — |
| 2026-10-21T20:26:11.0133313Z | `org.slf4j:slf4j-api@2.0.13` | `MAVEN:org.slf4j:slf4j-api@2.0.13` | 0 | — |
| 2026-10-21T20:26:11.6067527Z | `org.springdoc:springdoc-openapi-starter-common@2.5.0` | `MAVEN:org.springdoc:springdoc-openapi-starter-common@2.5.0` | 0 | — |
| 2026-10-21T20:26:12.1982269Z | `org.springdoc:springdoc-openapi-starter-webmvc-api@2.5.0` | `MAVEN:org.springdoc:springdoc-openapi-starter-webmvc-api@2.5.0` | 0 | — |
| 2026-10-21T20:26:12.7905942Z | `org.springframework.boot:spring-boot-actuator@3.2.5` | `MAVEN:org.springframework.boot:spring-boot-actuator@3.2.5` | 0 | — |
| 2026-10-21T20:26:13.3841410Z | `org.springframework.boot:spring-boot-actuator-autoconfigure@3.2.5` | `MAVEN:org.springframework.boot:spring-boot-actuator-autoconfigure@3.2.5` | 0 | — |
| 2026-10-21T20:26:13.9614403Z | `org.springframework.boot:spring-boot-starter@3.2.5` | `MAVEN:org.springframework.boot:spring-boot-starter@3.2.5` | 0 | — |
| 2026-10-21T20:26:14.5575514Z | `org.springframework.boot:spring-boot-starter-aop@3.2.5` | `MAVEN:org.springframework.boot:spring-boot-starter-aop@3.2.5` | 0 | — |
| 2026-10-21T20:26:15.1510671Z | `org.springframework.boot:spring-boot-starter-jdbc@3.2.5` | `MAVEN:org.springframework.boot:spring-boot-starter-jdbc@3.2.5` | 0 | — |
| 2026-10-21T20:26:15.7606497Z | `org.springframework.boot:spring-boot-starter-json@3.2.5` | `MAVEN:org.springframework.boot:spring-boot-starter-json@3.2.5` | 0 | — |
| 2026-10-21T20:26:16.3473725Z | `org.springframework.boot:spring-boot-starter-logging@3.2.5` | `MAVEN:org.springframework.boot:spring-boot-starter-logging@3.2.5` | 0 | — |
| 2026-10-21T20:26:16.9431524Z | `org.springframework.boot:spring-boot-starter-tomcat@3.2.5` | `MAVEN:org.springframework.boot:spring-boot-starter-tomcat@3.2.5` | 0 | — |
| 2026-10-21T20:26:17.5385957Z | `org.springframework.data:spring-data-commons@3.2.5` | `MAVEN:org.springframework.data:spring-data-commons@3.2.5` | 2 | GHSA-5m4m-73w9-8433, GHSA-5vpf-xvv7-c8vh |
| 2026-10-21T20:26:18.1283818Z | `org.springframework.data:spring-data-jpa@3.2.5` | `MAVEN:org.springframework.data:spring-data-jpa@3.2.5` | 0 | — |
| 2026-10-21T20:26:18.7247809Z | `org.springframework.security:spring-security-config@6.2.4` | `MAVEN:org.springframework.security:spring-security-config@6.2.4` | 0 | — |
| 2026-10-21T20:26:19.3128930Z | `org.springframework.security:spring-security-core@6.2.4` | `MAVEN:org.springframework.security:spring-security-core@6.2.4` | 1 | GHSA-q3v6-hm2v-pw99 |
| 2026-10-21T20:26:19.8926590Z | `org.springframework.security:spring-security-crypto@6.2.4` | `MAVEN:org.springframework.security:spring-security-crypto@6.2.4` | 1 | GHSA-mg83-c7gq-rv5c |
| 2026-10-21T20:26:20.4694517Z | `org.springframework.security:spring-security-oauth2-client@6.2.4` | `MAVEN:org.springframework.security:spring-security-oauth2-client@6.2.4` | 0 | — |
| 2026-10-21T20:26:21.0629121Z | `org.springframework.security:spring-security-oauth2-core@6.2.4` | `MAVEN:org.springframework.security:spring-security-oauth2-core@6.2.4` | 0 | — |
| 2026-10-21T20:26:21.6474274Z | `org.springframework.security:spring-security-oauth2-jose@6.2.4` | `MAVEN:org.springframework.security:spring-security-oauth2-jose@6.2.4` | 0 | — |
| 2026-10-21T20:26:22.2343531Z | `org.springframework.security:spring-security-web@6.2.4` | `MAVEN:org.springframework.security:spring-security-web@6.2.4` | 3 | GHSA-293q-567p-wmwq, GHSA-c4q5-6c82-3qpw, GHSA-mf92-479x-3373 |
| 2026-10-21T20:26:22.8276674Z | `org.springframework:spring-aop@6.1.6` | `MAVEN:org.springframework:spring-aop@6.1.6` | 0 | — |
| 2026-10-21T20:26:23.4224486Z | `org.springframework:spring-aspects@6.1.6` | `MAVEN:org.springframework:spring-aspects@6.1.6` | 0 | — |
| 2026-10-21T20:26:24.0163146Z | `org.springframework:spring-beans@6.1.6` | `MAVEN:org.springframework:spring-beans@6.1.6` | 0 | — |
| 2026-10-21T20:26:24.6102835Z | `org.springframework:spring-context@6.1.6` | `MAVEN:org.springframework:spring-context@6.1.6` | 2 | GHSA-4gc7-5j7h-4qph, GHSA-4wp7-92pw-q264 |
| 2026-10-21T20:26:25.1982816Z | `org.springframework:spring-expression@6.1.6` | `MAVEN:org.springframework:spring-expression@6.1.6` | 3 | GHSA-9f52-rjqv-25qv, GHSA-r5w3-xv2f-j59q, GHSA-wxpp-56q6-5pcg |
| 2026-10-21T20:26:25.7887392Z | `org.springframework:spring-jdbc@6.1.6` | `MAVEN:org.springframework:spring-jdbc@6.1.6` | 0 | — |
| 2026-10-21T20:26:26.3835631Z | `org.springframework:spring-messaging@6.1.6` | `MAVEN:org.springframework:spring-messaging@6.1.6` | 0 | — |
| 2026-10-21T20:26:26.9777478Z | `org.springframework:spring-orm@6.1.6` | `MAVEN:org.springframework:spring-orm@6.1.6` | 0 | — |
| 2026-10-21T20:26:27.5719117Z | `org.springframework:spring-tx@6.1.6` | `MAVEN:org.springframework:spring-tx@6.1.6` | 0 | — |
| 2026-10-21T20:26:28.1675056Z | `org.springframework:spring-web@6.1.6` | `MAVEN:org.springframework:spring-web@6.1.6` | 3 | GHSA-2rmj-mq67-h97g, GHSA-4gc7-5j7h-4qph, GHSA-6r3c-xf4w-jxjm |
| 2026-10-21T20:26:28.7594198Z | `org.springframework:spring-webmvc@6.1.6` | `MAVEN:org.springframework:spring-webmvc@6.1.6` | 15 | GHSA-3chg-m5w7-qfv5, GHSA-4773-3jfm-qmx3, GHSA-6hcq-hmm3-jj3c, GHSA-6p4f-wcwh-5vvm, GHSA-72pg-x5f8-j25j, GHSA-957g-f97v-vppc, GHSA-cjpg-rgq5-fr37, GHSA-cx7f-g6mp-7hqm, GHSA-g5vr-rgqm-vf78, GHSA-h3qp-gqrc-q736, GHSA-mq64-j8f9-9gcj, GHSA-pc63-qcmh-9cmg, GHSA-r936-gwx5-v52f, GHSA-wg35-8jpf-2xv3, GHSA-x23c-287f-qqv5 |
| 2026-10-21T20:26:29.3347184Z | `org.springframework:spring-websocket@6.1.6` | `MAVEN:org.springframework:spring-websocket@6.1.6` | 2 | GHSA-7fch-4f2f-jcgm, GHSA-q723-847q-5g8g |
| 2026-10-21T20:26:29.9254271Z | `org.webjars:swagger-ui@5.13.0` | `MAVEN:org.webjars:swagger-ui@5.13.0` | 0 | — |
| 2026-10-21T20:26:30.5163986Z | `org.yaml:snakeyaml@2.2` | `MAVEN:org.yaml:snakeyaml@2.2` | 0 | — |

## Interpretation and limits

- These are deps.dev index results for exact resolved package versions. A
  returned key is a known-record lead, not independent confirmation of an
  affected-version range, application reachability, exploitability, or a
  security finding. A zero-key response applies only to that returned row and
  this lookup time; it does not establish safety or absence from other sources.
- The transitive results include records for several Spring Framework,
  Spring Security, Tomcat, Jackson, and other components. Duplicate advisory
  IDs across components account for the difference between 93 associations and
  92 distinct IDs. Follow-up should compare authoritative advisory ranges with
  the exact Maven versions and dependency paths before making applicability
  statements.
- Maven tree scope is the pinned POM's effective compile/runtime graph resolved
  from the existing local cache. Test-scope dependencies, build-plugin graphs,
  unavailable repository metadata, and packaged-artifact contents were not
  examined. This was dependency/advisory metadata work only: no build, test,
  application, container, or product endpoint was run.
- No request failed or was rate-limited in this pass. A first local attempt to
  start the query script had a PowerShell parse error before any API request;
  the corrected invocation completed all 127 calls. The default sandboxed
  network had failed in the earlier direct lookup; the current control and
  transitive requests succeeded after network escalation.

**Bounded result:** the full Maven-resolved compile/runtime transitive set was
enumerated and queried: 127/127 exact key matches, no unmapped nodes, 18 rows
with advisory keys and 109 rows with zero keys. This is not a “no advisories”
or vulnerability-confirmation conclusion for Kadrom; the 18 returned rows need
affected-range and dependency-path review.
