# R7/A05 single Micrometer method-tag check — 22 October 2026

## Observed result

In a new isolated Kadrom diagnostic runtime, one bodyless HTTP/1.1 request with
the fixed valid method token `A05CHECK` to `/actuator/health` returned **400**.
The resulting HTTP-server timer used **`method=UNKNOWN`**, not the raw custom
method, with `error=exception=RequestRejectedException`, `uri=UNKNOWN`,
`status=400`, `outcome=CLIENT_ERROR`, and count **1**. One ordinary health GET
before and one after both returned **200**; the ordinary GET timer advanced
from 1 to 2. No raw `A05CHECK` method tag was observed in any captured timer.

This narrows Micrometer advisory applicability for this one request and local
configuration. It does not reproduce unbounded method-tag cardinality, resource
exhaustion, DoS, production behavior, or general handling of every custom method.
No loop, random method variants, retry, malformed body, upload, login, external
target, or load test was used. **R7/A05 remains open.**

## Assignment and safety gate

Following the accepted [effective-object preflight](../2026-10-22-a05-runtime-preflight/README.md),
the coordinator explicitly authorized this bounded next behavior check in the
user-owned local lab. Native `storage_docker_specialist`
`/root/a05_runtime_preflight` owned the lifecycle and this audit; native QA
`/root/a05_runtime_qa` reviewed the exact proposed helper before execution and
independently checked the result. The coordinator also inspected and approved
the exact sequence before execution. TOML runtime loading is not independently
proven by invocation alone. No Git operation was performed by the specialist.

Pre-request gates were a fresh unused resource prefix, cached immutable images,
internal Docker network, no host ports, new MySQL volume, no backend mounts,
no Docker healthcheck or HTTP readiness probe, same live observation filter and
registry checks, and health-before 200. The helper would stop before the custom
request if that health gate failed. It records the attempted stage and exception
class if a request fails; no failure path retries target traffic.

## Exact source, artifact and launch identity

Exact executed helper: [MethodSnapshot.java](MethodSnapshot.java), SHA-256
`b919641be52041775bbc1b7232532b4b5cb751248960aa3a681b3b1ae2086d7e`.
Host `javac 21.0.11 --release 17` compiled it against the inspected JAR libraries
and main class. No source/dependency change, Maven build or image pull occurred.

Backend immutable image:
`sha256:773ffd3a73373b974b80fab06897640a4c65bde044f9a246e22834853d2065a5`.
App JAR SHA-256:
`e564ab781100246897733a9367cd64ef76251a6d77272d73243c0174154ff608`.
These match the preflight and prior A04 cached image. Packaged Micrometer core
and Prometheus versions are 1.12.5; Spring Boot 3.2.5, Spring MVC 6.1.6, Tomcat
embed core 10.1.20. Full metadata: [runtime-identity.json](runtime-identity.json).

This used the **external diagnostic launcher**, not the original image's
`java -jar app.jar` entrypoint: `java -XX:MaxRAMPercentage=75
-Dloader.path=/diag -Dloader.main=MethodSnapshot -cp /app/app.jar
org.springframework.boot.loader.launch.PropertiesLauncher`.
It called SpringApplication on the packaged product main class and duplicated
the product's timezone initialization. No endpoint exposure/security override was
introduced. Profiles were `dev,demo`; effective SimpleObservationRegistry,
PrometheusMeterRegistry, and the registered `webMvcObservationFilter` class
`ServerHttpObservationFilter` mapped to `/*` were captured again.

The selected source remains pinned
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`; preflight compared packaged
base/dev/prod config hashes with that source and they matched. Full source-to-image
class equivalence is limited by historical build evidence, not independently
reproduced here. This is local diagnostic evidence, not deployed-production
configuration. The local DB/JWT secrets were generated for the new runtime;
only dummy provider/OAuth/mail configuration and localhost app base URL were used.
Environment values/raw startup logs/response bodies are excluded from this audit.

## Exact three-request oracle

The helper used one Java HTTP client with explicit HTTP/1.1, redirects disabled,
5-second connection timeout and 10-second per-request timeout. Responses used
`BodyHandlers.discarding()`. After each request a single 200-ms wait preceded
an in-process read of every current `http.server.requests` timer and its full
tag set. There were no other application HTTP clients or concurrent healthchecks.

| Stage | Status | GET /health success timer | UNKNOWN rejection timer |
|---|---:|---:|---:|
| One ordinary GET before custom | 200 | 1 | absent |
| One bodyless `A05CHECK` | 400 | 1 | 1 |
| One ordinary GET after custom | 200 | 2 | 1 |

The ordinary timer's full tag set was `error=none`, `exception=none`, `method=GET`,
`outcome=SUCCESS`, `status=200`, `uri=/actuator/health`. The rejection timer's
full tag set is recorded in the first paragraph and exact
[snapshot.json](snapshot.json). The custom response body was discarded; the
RequestRejectedException classification comes from the meter tags. No internal
exception stack or root-cause component beyond those observed tags is asserted.

The coordinator independently read Spring Framework v6.1.6's primary
[DefaultServerRequestObservationConvention source](https://raw.githubusercontent.com/spring-projects/spring-framework/v6.1.6/spring-web/src/main/java/org/springframework/http/server/observation/DefaultServerRequestObservationConvention.java):
lines 56 and 99–106 define known HTTP methods and map other methods to
`METHOD_UNKNOWN`. The observed UNKNOWN tag is consistent with that source path.
The exact active convention object was not introspected, so this is a
source-consistent explanation, not proof of that instance or of every runtime.

The request stage is `complete`, and the explicit status/count assertions above
are the acceptance evidence. Merely completing the helper or creating artifacts
would not establish the result. No toolkit/product test suite was run or claimed.

## Lifecycle and data preservation

New prefix: `a05-kadrom-method-20261022c`. All proposed resource names were
absent before creation. Network `a05-kadrom-method-20261022c_internal` was
inspected `Internal=true`. Backend and MySQL had no host-port bindings or Docker
healthchecks. Backend mounts were empty; MySQL mounted only new
`a05-kadrom-method-20261022c_mysql_data` at `/var/lib/mysql`.
The MySQL immutable image was the same cached
`sha256:ee241324a55f4651d8601d3dcd4a294c5d6c363c46263f7e8d542bbc9c0deacc`.
Startup operations and any scheduled writes could target only this new synthetic
database; individual scheduler job execution was not established.
Readiness used mysqladmin and container metadata; it did not issue extra HTTP.

After the snapshot was emitted the orchestration stopped only the new backend
and MySQL and retained the new volume. Backend exited **143**, MySQL **0**, both
`running=false` in [final-state.json](final-state.json); the new volume remained
present. The earlier preflight b and unused initial resources were not restarted
or mounted, and no existing A04 resource was started/mounted. No cleanup/delete/
`down -v` was used. The rollback plan was stopping these two new containers and
retaining their volume. Private generated configuration, copied JAR/libraries,
and startup logs remain only under ignored `.dxa/a05-micrometer-method-check/`.

The run succeeded without a request retry or setup failure. A later read-only
`rg` for explicit firewall customization returned no source matches (exit 1);
it is not a failed application request or proof of a default firewall's exact
effective configuration. No target code remediation was attempted or authorized
by this diagnostic result.
