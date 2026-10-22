# R7/A05 effective local runtime preflight — 22 October 2026

## Result and scope

The authorized isolated Kadrom diagnostic context instantiated an observation
registry and Prometheus meter registry, registered the HTTP observation servlet
filter, and recorded exactly one ordinary health GET. Effective multipart byte
limits, disk threshold, servlet temporary directory, and Tomcat connector values
were read from live objects. This resolves the earlier unavailable-runtime checks
for this local diagnostic configuration. It does not establish advisory impact,
resource exhaustion, parser-error cleanup, production configuration, or a proxy/WAF
condition. **R7/A05 remains open.** No nonstandard method, upload, malformed input,
load test, login, browser or external application request was sent.

Coordinator assigned native `storage_docker_specialist`
`/root/a05_runtime_preflight`; the role TOML and AGENTS/ROADMAP/STATUS/workflow,
startup safety review and evidence contracts were read. Runtime configuration
loading of the TOML is not independently proven. Only this audit directory and
ignored `.dxa/a05-runtime-preflight/` were written by this specialist. Product
sources and existing databases were not edited. QA reviewed the diagnostic and
evidence independently in the sibling runtime-QA audit.

## Artifact identity and launch differences

Toolkit baseline: `2bf3b8e` (coordinator verified matching origin/main).
Selected source: `.dxa/a04-kadrom-source`, pinned
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`.

- Backend immutable image:
  `sha256:773ffd3a73373b974b80fab06897640a4c65bde044f9a246e22834853d2065a5`.
  This is exactly the image recorded in the prior A04 owner-read audit, not just
  a matching mutable tag. Its image labels identify that historical build project.
- `/app/app.jar` SHA-256:
  `e564ab781100246897733a9367cd64ef76251a6d77272d73243c0174154ff608`.
- Packaged library names identify Spring Boot 3.2.5, Spring MVC 6.1.6,
  Tomcat embed core 10.1.20, Micrometer core/Prometheus 1.12.5. Full filenames are
  in [runtime-identity.json](runtime-identity.json); no dependency was changed.
- Packaged base/dev/prod YAML hashes equal their pinned-source counterparts;
  see [config-hashes.json](config-hashes.json). This corroborates configuration
  correspondence, not a reproducible proof of every class's source-to-image origin.
  Full source/build attestation was not reconstructed; exact code equivalence to
  the Git commit is consequently limited by the prior image-build evidence.
- MySQL immutable image:
  `sha256:ee241324a55f4651d8601d3dcd4a294c5d6c363c46263f7e8d542bbc9c0deacc`
  (cached `mysql:8`, inspected configured version 8.4.11).

The original backend entrypoint is `java -XX:MaxRAMPercentage=75 -jar app.jar`.
The diagnostic used the same image/JAR/JRE and memory option with
`-Dloader.path=/diag -Dloader.main=EffectiveSnapshot -cp /app/app.jar
org.springframework.boot.loader.launch.PropertiesLauncher`.
An external class called `SpringApplication.run` on the packaged product's main
application class and duplicated its Europe/Istanbul timezone initialization.
It then read the resulting context objects and closed the context. This is a
diagnostic launch, not proof that the unmodified entrypoint or a production
deployment was inspected. No Actuator endpoint exposure/security override was added.

Effective profiles were `dev,demo`. The new-container environment supplied only
the local DB coordinates and randomly generated DB/JWT synthetic secrets,
`JPA_DDL_AUTO=validate`, `FLYWAY_ENABLED=true`, dummy Cloudinary/OAuth/mail values,
and a localhost app base URL. Credentials and raw environment are not published.
Schedulers/migrations/seeding remain the product's configured startup behavior;
startup operations and any scheduled writes could target only the new synthetic
database. Individual scheduler job execution was not established.
The Docker internal network blocked
ordinary external routing; no external service response is claimed.

## Observed live objects and one-request oracle

Exact executed diagnostic source: [EffectiveSnapshot.java](EffectiveSnapshot.java),
SHA-256 `69d0e37715ef76d6c51627f0322e8353025241f7e9c645549bfed16d7ccc3030`.
It was compiled using host `javac 21.0.11 --release 17` against library files and
the main class extracted from the inspected JAR; no Maven build/pull was performed.
The diagnostic was copied to the new container, not mounted over product code.
The exact allowlisted output is [snapshot.json](snapshot.json).

| Check | Observed |
|---|---|
| Observation registry | bean `observationRegistry`, `SimpleObservationRegistry` |
| Meter registry | bean `prometheusMeterRegistry`, `PrometheusMeterRegistry` |
| HTTP observation filter | servlet registration `webMvcObservationFilter`, class `ServerHttpObservationFilter`, URL mapping `/*` |
| Standalone filter bean query | empty list; this does not negate the actual servlet registration |
| Multipart resolver | bean `multipartResolver` |
| MultipartConfigElement maximum file/request | 20,971,520 / 26,214,400 bytes |
| MultipartConfigElement disk threshold/location | threshold 0 bytes; location empty string |
| JVM temporary directory | `/tmp` |
| Servlet context temporary directory | `/tmp/tomcat.8080.8487698591594884241/work/Tomcat/localhost/ROOT`; exists, readable, writable |
| Temp filesystem snapshot | usable 985,668,423,680 bytes, total 1,081,101,176,832 bytes; instantaneous metadata only |
| Connector | port 8080; `maxParameterCount=10000`; `maxPostSize=2097152`; `maxSavePostSize=4096`; parse body methods `POST` |
| Part-specific connector getters | `getMaxPartCount` and `getMaxPartHeaderSize` absent on this actual class |
| Protocol | `Http11NioProtocol`; `maxSwallowSize=2097152`; max request header size 8192; max header count 100; timeout 60000; max connections 8192; max threads 200 |

`MultipartProperties.isEnabled` was an unavailable method, and generic JSON
serialization of its DataSize objects exposed only `negative=false`. Those fields
are not numeric evidence; the byte values above come directly from
`MultipartConfigElement` primitive getters. A threshold of zero and an empty
configured location establish effective disk-use configuration, not that any
upload created a file or that parser-error cleanup succeeds/fails. No multipart
request was made. Absent part-specific getters do not imply all parser bounds
are absent: `maxParameterCount` is separately recorded.

The two container image configurations had **no Docker healthcheck**, and no
readiness HTTP probe or other helper sent requests. After context startup the
diagnostic took `http.server.requests` timer counts, sent exactly one ordinary
`GET /actuator/health` to its own loopback, discarded the body, waited 200 ms,
then read timers again. Before: no matching timers. After: one timer with
`method=GET`, `uri=/actuator/health`, `status=200`, `outcome=SUCCESS`,
`error=none`, `exception=none`, count **1**. Response status was 200.
This demonstrates that local HTTP instrumentation records a standard request;
it does not test handling/cardinality of arbitrary HTTP methods or reproduce DoS.

## Isolation, preservation, and lifecycle

Before creation, Docker inspect returned resource-not-found for each proposed
container/network/volume name; creation would abort if any name already existed.
Successful runtime project/resource prefix: `a05-kadrom-effective-20261022b`.
Its `_internal` network had `Internal=true`. Neither container had host port
bindings. Backend mounts were empty. MySQL mounted only the new
`a05-kadrom-effective-20261022b_mysql_data` at `/var/lib/mysql`.
The JAR and diagnostic were copied, not bound to existing data. No old volume was
mounted and no old stopped container was started. Startup migrations/seeding and
schedulers could mutate only this new synthetic database. Rollback was to stop
only these newly created containers and retain the volume; no deletion/down was used.

The initial prefix `a05-kadrom-effective-20261022` was also verified unused and
created fresh. JAR extraction then hit a Windows path-length failure before
either container was started. Those two containers remain **Created** (never
started); the newly created empty `_mysql_data` volume and internal network were
retained. Extraction was corrected to flatten library filenames and extract only
the needed product main class; a new `...20261022b` prefix avoided resource reuse.

The successful diagnostic emitted its complete snapshot and called context close.
The JVM remained alive afterward, so its new backend was explicitly stopped
(`docker stop --time 30`); Docker warned that `--time` is deprecated. Final backend
exit code was **143**, MySQL stopped with **0**; both `running=false` in
[final-state.json](final-state.json). Both A05 volumes remain present. No
resource deletion was performed. Final metadata checks showed all six previously
existing A04 containers still exited (owner-read 143/137, disposable 143/137,
original 137/137), and the original `a04-kadrom-20261021_mysql_data` still exists.
No query read the old database contents.

Other setup-only failures: the first Docker image-inspect template assumed optional
Config fields and failed; the corrected inspect succeeded. A local Python config
hash command was denied by the sandbox process launcher and succeeded on explicit
escalated retry. Neither is application behavior. Private startup logs, generated
credentials, copied JAR/libraries and Docker inventories remain ignored under
`.dxa/a05-runtime-preflight/`; only allowlisted metadata is published here.

No toolkit or product test suite was run. The live getter inspection and the one
standard GET are the new runtime evidence. Prior A04, BCrypt, Sort and other test
counts are not re-counted as this run. Source advisories/remaining uncertainty are
the linked prior Micrometer and multipart config audits; this preflight adds local
effective prerequisites and does not close R7/A05 or authorize target remediation.
