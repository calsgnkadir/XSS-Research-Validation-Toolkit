# R7 / A05 — independent effective-runtime QA

**Date:** 2026-10-22. **Toolkit assignment baseline:** `2bf3b8e`, reported by
the coordinator as matching `origin/main`. Product review scope is the user's
Kadrom checkout at `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`.

## Ownership and method

The coordinator invoked `/root/a05_runtime_qa` with native
`agent_type=qa_security_lab_specialist`, exclusively owning this file. The
specialist read `.codex/agents/qa_security_lab_specialist.toml`; reading it does
not independently establish effective runtime loading of that TOML.
AGENTS, ROADMAP, STATUS, VALIDATION, workflow, initial architecture review,
the three evidence contracts and relevant A04/A05 audits were consulted.
Storage owns all Docker lifecycle operations and ignored runtime helpers.
QA does not send target requests or start/stop containers.

## Independent acceptance gates

These gates were derived before inspecting Storage's runtime output, from
the pinned application declarations and the Security specialist's
[advisory disposition](../2026-10-22-a05-advisory-disposition/README.md).

| Gate | Required observation | Failure / conclusion boundary |
|---|---|---|
| Lab isolation | New unique project, MySQL volume and internal network; actual backend/MySQL image IDs; no host port bindings; only new mounts/network | Compose declarations alone do not establish effective runtime isolation. Existing data must remain untouched. |
| Artifact identity | Actual running image ID, application JAR hash, packaged dependency versions; source/build provenance stated explicitly | A reused image tag or pinned checkout does not bind the running image to source. Matching selected JAR contents supports only that correspondence. |
| Micrometer configuration | Effective profiles/properties, observation and meter registry, actual servlet filter registration | Bean presence alone does not establish request instrumentation registration. |
| Micrometer recording | Same ordinary-route/method timer and exact tag set before/after exactly one ordinary GET, positive count delta after response completion | Missing/renamed timer, errors or timeout are inconclusive; no unusual method or resource impact follows. |
| Multipart values | Active resolver/config; max file/request bytes, threshold, resolved location, servlet/JVM temp directories | Source values must be compared to effective values; blank location is not proof of memory storage. |
| Tomcat connector | Actual version, body/parameter limits and explicit getter availability for part count | Unsupported getter is unavailable, never zero or a later-version default. Parameter count is not a demonstrated multipart part count. |
| Temp location | Fresh lab's resolved temp filesystem/capacity/access metadata | Empty directory or threshold zero does not exercise parser errors, temporary-file cleanup or exhaustion. |

Pinned source `hotelapp/src/main/resources/application.yml:81-85` declares
multipart enabled, max file size 20 MB and request size 25 MB. Expected binary
byte values are 20,971,520 and 26,214,400. The source does not specify threshold
or location. `hotelapp/Dockerfile:13` uses `-DskipTests`; image packaging is not
a test pass. No production override, WAF/proxy or adversarial method/upload
behavior can be established from the isolated local snapshot.

## A04 consistency check

`ROADMAP.md:903` marks selected A04 scope bounded complete. The
[owner-read runtime audit](../2026-10-22-a04-owner-read-runtime/README.md),
"Coordinator disposition", accepts only the selected two-account list and
same-role GET controls linked there. Its earlier broad "A04 and R7 remain
open" paragraph must be read with that later scoped disposition. Attendance's
positive fixture was empty; the roster workbook was not opened. These limits
remain compatible with bounded closure and do not establish product-wide
authorization safety. No new A04 run or wider scope is needed for this task.

## Runtime artifact and isolation review

QA reviewed the exact exported
[diagnostic](../2026-10-22-a05-runtime-preflight/EffectiveSnapshot.java),
[snapshot](../2026-10-22-a05-runtime-preflight/snapshot.json),
[identity](../2026-10-22-a05-runtime-preflight/runtime-identity.json) and
[final state](../2026-10-22-a05-runtime-preflight/final-state.json).
Independent SHA-256 reads matched the executed ignored diagnostic to the
exported copy and the identity's diagnostic hash:
`69d0e37715ef76d6c51627f0322e8353025241f7e9c645549bfed16d7ccc3030`.
The ignored/exported snapshot copies also match:
`3b73945557dacab3f14dfb83f9840462b6b854a596fda8b852b84cd18f621240`.

QA independently inspected only the two new `20261022b` containers, their
new network and new volume using Docker's read-only metadata commands. Actual
backend image is `sha256:773ffd3a73373b974b80fab06897640a4c65bde044f9a246e22834853d2065a5`;
MySQL is `sha256:ee241324a55f4651d8601d3dcd4a294c5d6c363c46263f7e8d542bbc9c0deacc`.
Both have empty host port bindings. Backend has no mounts; MySQL mounts only
`a05-kadrom-effective-20261022b_mysql_data` at `/var/lib/mysql`. Both are
attached only to `a05-kadrom-effective-20261022b_internal`, independently read
as `internal=true` with ID
`4f6d5445bd5e8736769612853127fabb8f0fd7aa587d61da492c49fc70ce4cae`.
The new local-driver volume remains present. Existing volumes were not opened
or queried by QA. Prior inventory preservation is Storage's separate record.

Read-only local JAR hashing independently confirms
`e564ab781100246897733a9367cd64ef76251a6d77272d73243c0174154ff608`.
Packaged `application.yml` and `application-prod.yml` match the pinned source
bytes, respectively SHA-256
`2ac8088c1bd346174b851d2edd046a6303b8bf0a77035ec6a272b247840e1d76` and
`ceaa25212a67fabb4caec3ea8d67d73e2b32bc854f43a312e361669df2a07799`.
Identity lists Micrometer 1.12.5, Tomcat 10.1.20, Spring MVC 6.1.6 and Boot
3.2.5 packaged libraries. This confirms selected artifact/config correspondence;
QA did not reconstruct the full source-to-image build or attest all classes.

The diagnostic replaces the image's normal JAR launcher with
`PropertiesLauncher`, loading `EffectiveSnapshot` from copied `/diag` classes.
It starts the product's application class through `SpringApplication.run`,
retaining the source main's timezone initialization, `dev,demo` profiles and
`-XX:MaxRAMPercentage=75`. It queries live beans, sends one loopback ordinary
GET and closes the context. This is a diagnostic application instance with a
modified launcher, not proof of an unchanged production entrypoint. No product
source or original app JAR was modified. The reviewed orchestration sets fresh
synthetic database/auth/provider configuration and performs MySQL readiness
via `mysqladmin ping`, with no HTTP readiness request. Stored runtime identity
records backend/MySQL healthcheck as null.

## Effective observations and acceptance

| Observation | Evidence and QA disposition |
|---|---|
| HTTP instrumentation registration | `snapshot.json:82` registers `webMvcObservationFilter` with class `ServerHttpObservationFilter` on `/*`. A standalone bean-name lookup is empty, so that lookup alone would have been misleading. Registry classes are `SimpleObservationRegistry` and `PrometheusMeterRegistry`. Configuration/registration gate supported for this context. |
| Ordinary request recording | `snapshot.json:140` has no matching HTTP timers before the request; `:141-156` records one GET `/actuator/health`, HTTP 200, then an exact timer/tag set `error=none, exception=none, method=GET, outcome=SUCCESS, status=200, uri=/actuator/health` with count 1. The reviewed helper contains one GET, no retry and no redirect following. This supports absent-to-count-one recording for that route; QA did not resend it. |
| Multipart primitive values | `snapshot.json:105-110` gives `MultipartConfigElement` max file 20,971,520 bytes, request 26,214,400 bytes, threshold 0 and location empty. These agree with source byte limits. A `multipartResolver` bean name is present; no upload was parsed. |
| Generic property-read limits | `snapshot.json:92` says `isEnabled=METHOD_ABSENT`; `DataSize` getter outputs contain only `negative=false`. They are not numeric size evidence. Actual primitive limits come from `MultipartConfigElement`, not these lossy generic representations. Resolver implementation class and effective observation-property names were not exported. Actual registration/recording independently establish the bounded metrics behavior. |
| Connector | `snapshot.json:121-138` gives parameter count 10,000, max POST 2,097,152, saved POST 4,096, parse methods POST, swallow size 2,097,152, header size 8,192 and header count 100. `getMaxPartCount` and `getMaxPartHeaderSize` are explicitly `METHOD_ABSENT`; no later-version part-count default is inferred. |
| Temp metadata | `snapshot.json:112-120` gives JVM `/tmp`, servlet temp `/tmp/tomcat.8080.8487698591594884241/work/Tomcat/localhost/ROOT`, present/readable/writable, usable 985,668,423,680 and total 1,081,101,176,832 bytes. Blank multipart location resolves to that servlet temp context. Filesystem type/mount quota were not exported; these capacity values are a point-in-time filesystem view, not a guaranteed dedicated upload budget. |

Registration plus the ordinary timer delta supports the Micrometer advisory's
local configuration/recording prerequisites in this diagnostic context. It does
not establish unusual-method acceptance, unbounded tags, resource impact or
production applicability. Multipart values narrow configuration uncertainty;
part-count behavior, overflow conditions, parse-error cleanup, actual disk
growth and WAF/proxy parsing remain untested. No malformed upload, unusual
method, load, parser-error or exhaustion test occurred.

## Errors, stop and remaining limits

The first Storage attempt failed before application startup on Windows path
length; its unused resources were preserved and the successful run used the
new `20261022b` names. QA did not reproduce that setup error. QA's first Python
hash command was blocked by runtime access denial; the identical read-only
command succeeded with escalation. Initial sandbox Docker reads failed on
config/engine access; escalated inspection succeeded. One selected Docker
format then failed because `Healthcheck` was absent; a revised format verified
the other selected fields successfully. These command errors are not product
security failures or passing tests.

Independent final Docker state agrees with Storage's exported final record:
backend exited 143, MySQL exited 0, neither OOM-killed, both stopped. Storage
reports explicitly stopping the backend after snapshot/context closure because
the process lingered. Therefore snapshot capture succeeded, while autonomous
process termination did not complete as intended. Stop outcome is not an
application oracle or test-suite result. QA performed no lifecycle operation.

**Disposition: bounded local configuration/recording evidence accepted with
the stated artifact, launcher and metadata limits. R7/A05 remains open.** No
toolkit or Kadrom test suite was run by QA; no new CI result was inspected or
claimed. Source remediation, deployed proxy conditions, advisory branch
disagreements and product-identity record lookup remain separate open work.

## Separately authorized single-method follow-up — pre-run review

After accepting the preflight, the coordinator separately authorized a fresh
`20261022c` isolated context with exactly one bodyless `A05CHECK` method token
to loopback `/actuator/health`, plus at most one ordinary health GET before and
one after. The preflight source/artifacts remain separate. QA's ownership
continues to be only this audit; Storage owns the separate
`a05-micrometer-method-check` helper/runtime/audit.

QA inspected proposed `MethodSnapshot.java` and orchestration before execution:
the helper fixes HTTP/1.1 and redirects NEVER, requires initial health 200
before the custom request, contains one send per stage and no request retry
loop, and records exact HTTP timer tags/counts in process after each response.
It persists an attempted-stage marker and exception class on request errors.
The orchestration uses the same image IDs with new project/network/volume,
no host ports, and no HTTP readiness probes. QA requested that summary output
handle absent custom/health-after fields on partial error without mislabeling
the result. A partial/error response must not authorize automatic repeat.

Acceptance requires distinguishing a raw `method=A05CHECK` timer from an
`UNKNOWN` tag or no observation, and treating ordinary health-after separately.
One raw method observation supports only one retained method value; it cannot
prove arbitrary or unbounded cardinality, resource exhaustion, production
proxy traversal or DoS. No upload/malformed body/load is authorized in this
follow-up.

## Single-method follow-up — actual QA disposition

QA reviewed the exported
[method helper](../2026-10-22-a05-micrometer-method-check/MethodSnapshot.java),
[snapshot](../2026-10-22-a05-micrometer-method-check/snapshot.json),
[identity](../2026-10-22-a05-micrometer-method-check/runtime-identity.json) and
[final state](../2026-10-22-a05-micrometer-method-check/final-state.json).
The pre-reviewed, executed and exported helper SHA-256 matches:
`b919641be52041775bbc1b7232532b4b5cb751248960aa3a681b3b1ae2086d7e`.
Ignored/exported snapshot hashes independently match:
`655587a7e3ff25f7e2da8f89908d524db0e929a2bc9aa2cd65f9447fa282dc9a`.
The independently hashed c-run extracted app JAR again equals
`e564ab781100246897733a9367cd64ef76251a6d77272d73243c0174154ff608`.
No full source-build attestation is added by that equality.

| Stage | Actual snapshot observation | QA interpretation |
|---|---|---|
| Before custom | `snapshot.json:141-156`: ordinary GET health 200; exact GET/SUCCESS/200/health timer count 1 | Initial positive health/recording control completed. |
| Single custom | `snapshot.json:159-185`: bodyless A05CHECK health 400; new timer has `method=UNKNOWN`, `uri=UNKNOWN`, `error=exception=RequestRejectedException`, `outcome=CLIENT_ERROR`, `status=400`, count 1; original GET timer remains 1 | Custom request was rejected and recorded with a normalized method label. No raw `A05CHECK` tag was observed in this snapshot. |
| After custom | `snapshot.json:188-214`: ordinary GET health 200; same GET timer count 2; UNKNOWN rejection timer still count 1 | Ordinary health succeeded after the single request; no second custom request is reflected in the reviewed sequence. |

`requestStage=complete` and absence of `requestErrorClass` agree with the three
completed bounded observations. The custom 400 is the observed rejection
outcome, not a transport/setup error or a passing vulnerability test. Missing
raw-method recording is not a general proof that all arbitrary methods or
routes are safe. The coordinator's separate primary-source check of Spring
6.1.6's [default request observation convention](https://raw.githubusercontent.com/spring-projects/spring-framework/v6.1.6/spring-web/src/main/java/org/springframework/http/server/observation/DefaultServerRequestObservationConvention.java)
reports standard-method enumeration and UNKNOWN fallback. That is consistent
with the observed label; the actual convention instance was not separately
introspected by this diagnostic.

QA independently read c-run Docker metadata with escalation: same backend/MySQL
image IDs, empty host port bindings, no backend mounts, only new c MySQL volume,
sole network `a05-kadrom-method-20261022c_internal`. Its independent network
read returned `internal=true`, ID
`89851f55ba8122795e9305a942cab035ab7cb1436a6ba55bc121024b326e94ca`;
the c local-driver volume remains present. Both containers were stopped with
backend exit 143 and MySQL exit 0, neither OOM-killed, matching final-state
artifact. An initial optional Healthcheck-format expression failed to parse;
revised selected-field inspection succeeded. QA performed no lifecycle or
target request operations.

**Accepted bounded result:** one custom method was rejected, its observed
metric label was UNKNOWN, and ordinary health was 200 before/after. The
specific raw-method retention candidate was not reproduced by this one-token,
one-route local control. No resource exhaustion, broad DoS resistance,
production behavior, complete advisory rejection, remediation or new CVE
conclusion follows. R7/A05 remains open with the preflight and advisory limits
above. QA did not run a test suite or inspect a new CI result in either phase.

## Coordinator Git artifact-byte check

Before commit, the coordinator detected that Git's newline conversion changed
the staged JSON snapshot blob relative to its captured bytes. Package-local
`.gitattributes` now marks Java and JSON artifacts `-text`; the two evidence
directories were restaged with those rules. The coordinator requires each raw
artifact's Git object ID to equal its staged blob ID before acceptance. This
preserves the reported SHA-256 hashes across checkouts; no runtime source,
snapshot value or request was changed by this storage correction.
