# Kadrom local security triage — owner review draft

**Date:** 22 October 2026. **Roadmap:** R7 / A04 / A05. **Status:** draft prepared for the product owner in this workspace; not sent to a maintainer, vulnerability database or disclosure service. A04 has bounded acceptance for the selected GET routes. The user separately authorized Kadrom source/dependency fixes. The BCrypt byte-boundary remediation and tests are recorded in [the remediation audit](../audit/2026-10-22-a05-bcrypt-remediation/README.md); target commit `6be6a07` was merged with upstream Vite commit `ba38bd3` and pushed as `c3ce102`. The target remains undeployed. Other A05/R7 questions remain open.

**Coordinator update — 22 October 2026:** The final local Kadrom source tree now
uses Boot 4.1.1 / Security 7.1.1, the Boot 4 Resilience4j integration and
additional dependency fixes. Its complete Maven test suite passed 665/665
after the test-only H2 2.3.232 pin. OSV querybatch checked the resulting 246
Maven coordinates and returned 246 rows with zero matches. This snapshot does
not establish an advisory-free product or deployed graph; official
product-identity queries remain inconclusive and multipart testing is reserved
for the user. See the [A05 dependency follow-up](../audit/2026-10-22-a05-dependency-refresh/README.md).

The strongest supported result is a reproduced password-equivalence defect in the pinned local application's registration/login flow, matching known Spring Security BCrypt advisory CVE-2025-22228. A synthetic 73-byte ASCII password was accepted at registration, and a different suffix sharing its first 72 bytes authenticated to the same synthetic account. Practical compromise of a real account was not demonstrated. Other dependency leads have the narrower dispositions below.

## Product, authorization and artifact identity

The user selected their Kadrom repository, `calsgnkadir/hotel-platform`, for local research. The reviewed product checkout is `.dxa/a04-kadrom-source` at `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. Maven identity is `com.hotelapp:hotel-student-platform:0.0.1-SNAPSHOT` (`hotelapp/pom.xml:15-18`), Spring Boot parent 3.2.5 (`:8-12`), Java target 17 (`:23`). The snapshot coordinate is not a supported product release. The prior identity review found upstream `ba38bd3a5fde6ea57089ab04eb38f58829110096` differed only by frontend configuration; this report does not claim to test a latest supported product release. See [identity review](../audit/2026-10-21-r7-r6-decision/README.md).

Report assignment baseline is toolkit commit `6167fa8361fd9f02b1a9e859152117639c855540`. Auth results below were recorded earlier in an H2 in-memory MockMvc test profile, using synthetic accounts. Docker diagnostic results used the cached backend image `sha256:773ffd3a73373b974b80fab06897640a4c65bde044f9a246e22834853d2065a5` and application JAR SHA-256 `e564ab781100246897733a9367cd64ef76251a6d77272d73243c0174154ff608`. Packaged library versions include Boot 3.2.5, Security Crypto 6.2.4, MVC 6.1.6, Tomcat 10.1.20 and Micrometer 1.12.5. [Runtime identity](../audit/2026-10-22-a05-runtime-preflight/runtime-identity.json) records exact filenames and selected metadata.

The effective runtime and method checks used an external diagnostic launcher invoking the packaged main application, profiles `dev,demo`, fresh synthetic MySQL volumes, internal Docker networks and no host ports. Packaged base/dev/prod YAML hashes matched pinned source. Full class-by-class source/build equivalence, the original entrypoint and production overrides were not independently reproduced. Previous containers were stopped and volumes retained as documented in the [preflight](../audit/2026-10-22-a05-runtime-preflight/README.md) and [method check](../audit/2026-10-22-a05-micrometer-method-check/README.md). This report starts no runtime and sends no application request.

## Candidate dispositions

| Item | Evidence and observed behavior | Supported disposition / remaining limit |
|---|---|---|
| A04 authorization reads | Own application lists 200; cross-role 403; anonymous 401. Two synthetic candidates compared three work-session GETs with a positive session fixture. Two synthetic owners compared attendance/roster: owner1 200, owner2 403. | Selected GET scope bounded accepted; no candidate observed there. Attendance positive control had no attendance rows. Normal clock-in, mutations, other controllers and product-wide security remain outside acceptance. [Scope](../audit/2026-10-22-a04-scope-completeness/README.md), [owner runtime](../audit/2026-10-22-a04-owner-read-runtime/README.md), [work-session runtime](../audit/2026-10-21-a04-same-role-runtime/README.md). |
| BCrypt / CVE-2025-22228 | Pinned Crypto 6.2.4; local registration of a 73-byte ASCII password 200, different-suffix login 200 for the same new principal. Separate direct packaged-library assay: three Unicode suffix pairs matched and packaged PasswordPolicy accepted them. | Actionable reproduced ASCII application-path defect matching a known dependency advisory, plus Unicode library/policy evidence. The Unicode assay made no endpoint request. Real-account compromise, Unicode application flows and recovery effects remain unverified. Detailed finding below. |
| Spring Data Sort | Authenticated candidate list exposes Pageable (`ApplicationController.java:45-51`). One 231-character malformed property returned 500 with UnknownPathException; no StackOverflow observed; following health 200. | Input error observed; advisory DoS not reproduced. A passing bounded harness is not successful/safe product handling. [Sort evidence](../audit/2026-10-22-a05-sort-local-check/README.md). |
| Micrometer | Registered ServerHttpObservationFilter on `/*`, actual ordinary health metric recording. One bodyless A05CHECK request returned 400; timer method UNKNOWN/count 1; health before/after 200, GET count 1→2. | No raw custom-method tag or DoS reproduced for this single request. Production instrumentation, other paths and general advisory applicability remain open. [Preflight](../audit/2026-10-22-a05-runtime-preflight/README.md), [single-method evidence](../audit/2026-10-22-a05-micrometer-method-check/README.md). |
| Multipart / Tomcat | Effective max file/request 20,971,520/26,214,400 bytes (20/25 MiB); threshold 0; blank configured location; writable servlet temp directory; maxParameterCount=10000, maxPostSize=2097152. Part-specific getter APIs absent. | Configuration evidence; absent getters do not establish absent parser limits. Parser-error cleanup, resource impact and deployed proxy/WAF conditions unverified. No upload was part of the accepted diagnostic snapshots. [Config review](../audit/2026-10-22-a05-multipart-config-review/README.md), [effective snapshot](../audit/2026-10-22-a05-runtime-preflight/snapshot.json). |
| Spring RFD | Inert attachment H2 test: anonymous 401, stranger 403, member 200; UTF-8 filename encoded in Content-Disposition. | Header/authorization behavior only; no browser interpretation, download execution or RFD exploitation demonstrated. [RFD evidence](../audit/2026-10-21-a05-rfd-local-check/README.md). |
| Nimbus | Pinned OAuth2 scope/config and cached-bytecode inspection did not support a path to the affected recursive JSON parser. | Source-supported applicability path absent in the inspected configuration; not a runtime negative or universal rejection. Deployment overrides/source JAR limitations remain. [Nimbus review](../audit/2026-10-21-a05-nimbus-path-review/README.md). |
| Actuator / CVE-2026-22733 | GHSA structured interval includes 3.2.5; Spring affected-version list omits 3.2.x. Prior source review found no protected application handler under the advisory-specific Cloud Foundry subpath. | Explicit version-range conflict unresolved; omission is not proof of unaffected status. [Disposition and primary links](../audit/2026-10-22-a05-advisory-disposition/README.md). |
| X.509 / CVE-2026-47838 | GHSA structured interval includes 6.2.4; narrative/vendor list omit 6.2.x. Prior bounded source review found no X.509 pre-authentication setup. | Explicit range conflict unresolved; no applicable product path demonstrated. No certificate-flow test. [Disposition](../audit/2026-10-22-a05-advisory-disposition/README.md). |

Dependency screening queried 21 direct and 127 transitive coordinates; source triage covered 92 distinct advisory keys and range checks covered 93 coordinate/advisory associations. These are dependency-screening coverage figures, not product vulnerabilities. POI's affected parser lacked a source-supported user-OOXML input path; see [POI triage](../audit/2026-10-21-r7-poi-source-triage/README.md). Existing screening and constraints are retained rather than recounted as a new scan.

## BCrypt finding for owner review

**Finding:** accepted long passwords lose suffix distinction during local authentication. **Affected tested configuration:** Kadrom pinned source and resolved `org.springframework.security:spring-security-crypto:6.2.4`. **Triage:** remediation recommended for the demonstrated local defect; practical exploitability and production status unverified. No application-specific CVE or CVSS score is assigned here.

### Preconditions and source evidence

The source configures BCrypt for the DAO authentication provider. A registration can supply a policy-valid value beyond 72 UTF-8 bytes because registration validation has a minimum/composition policy but no maximum. The observed run used a synthetic enabled, verified account in the local H2 profile. An attacker against a real account would still need a suitable candidate sharing the first 72 effective bytes; neither that knowledge nor realistic guessing/entropy/rate-limit conditions were established.

Paths in this table are relative to `.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/`; they were rechecked read-only for this report.

| Source | Role in the tested or related path |
|---|---|
| `config/AppConfig.java:54-57,74-75` | DAO provider uses the configured BCryptPasswordEncoder. |
| `dto/RegisterRequest.java:35-37`; `validation/PasswordPolicy.java:23-25` | Registration minimum/composition checks, with no maximum/UTF-8 byte check. |
| `service/AuthService.java:62-82` | Service repeats policy then encodes supplied registration password. |
| `controller/AuthController.java:64-83`; `dto/LoginRequest.java:12-14`; `service/AuthService.java:148-149` | Registration/login request path; login password has nonblank validation and reaches AuthenticationManager. |
| `service/AuthService.java:291-302,311-322` | Current-password matches and new-password encode also have no maximum; additional source lead, not an application runtime reproduction. |
| `controller/PasswordResetController.java:68-77` | Reset's 128-Java-character maximum is not a 72-UTF-8-byte boundary; additional source lead, not separately reproduced. |

### Expected, observed and reproduction record

Expected: either the application rejects an over-limit password deliberately before encoding/authentication, or every accepted credential byte distinguishes the stored password. A different accepted password must not authenticate merely because its effective BCrypt prefix is identical.

Observed in the prior [registration follow-up](../audit/2026-10-22-a05-bcrypt-local-check/README.md): one policy-valid 73-byte ASCII registration returned 200. Following the synthetic email-verification setup, one login with a different final byte and the same first 72 bytes returned 200 for that registered principal. The successful focused temporary test recorded one pass, no failures/errors/skips. An earlier distinct test created the hash directly from 72 bytes and accepted a 73-byte login; that earlier check alone did not prove registration acceptance. Neither run is repeated by preparing this report.

The check used Windows, Java 17.0.18, Maven 3.9.16 offline, Boot 3.2.5 and H2 in-memory `test` configuration. Flyway and external storage/mail delivery were disabled or prevented by the test preflight; queued messages remained in H2. Exact command, runner failures, synthetic verification step, cleanup and limited result retention are in the linked local-check audit. No credentials, hash, cookie, token or response body is included here. Temporary test source was removed after the run, so the audit is the retained reproduction procedure/result; no permanent product regression or independent rerun is claimed. See also the [prior detailed triage](../audit/2026-10-22-a05-bcrypt-triage/README.md).

### Separate Unicode library and policy assay

The completed [offline Unicode assay](../audit/2026-10-22-a05-bcrypt-utf8/README.md) directly executed Crypto 6.2.4 and PasswordPolicy extracted from the exact cached application JAR identified above. Its retained [Java helper](../audit/2026-10-22-a05-bcrypt-utf8/Utf8Boundary.java) and [allowlisted JSON](../audit/2026-10-22-a05-bcrypt-utf8/snapshot.json) record three valid Unicode input pairs:

| Final code-point width | UTF-8 bytes per whole value | Java UTF-16 units per whole value | First 72 bytes equal / full inputs differ | Different suffix matched / packaged policy allowed both |
|---|---:|---:|---|---|
| 2 bytes | 73 | 72 | true / true | true / true |
| 3 bytes | 74 | 72 | true / true | true / true |
| 4 bytes | 75 | 73 | true / true | true / true |

Each pair shared 71 ASCII bytes and the first encoded byte of the final code point. The complete submitted values were valid; their shared 72-byte prefix ended inside that final code point. An exactly-72-byte control (71 UTF-16 units) matched its correct value and rejected a first-byte substitution. The successful assay performed exactly nine BCrypt calls: four encodes and five matches. Independent input/control assertions passed; suffix-match results were recorded independently of those assertions. Helper SHA-256 is `9ac1efa55f5b642aaaf959c0cb5a4c27e1f15c3d5e5e4cf7a8c2380a488410ca`; JSON SHA-256 is `c2b63515a1fe3b8b9bba90d499a46351ed0ccb992c045897f82b1080a6eddc3d`.

This demonstrates Unicode boundary behavior in the packaged library and admission by its packaged shared policy. The source DTO password constraints also admit these shapes; it does not follow that their other DTO/state requirements or registration/login/change/reset endpoints ran. No application context, account, endpoint or network request was used. The earlier real registration/login evidence remains the separate ASCII-only reproduction. A 72-Java-unit cap would still admit the first two tested shapes; byte-aware policy and deliberate recovery planning remain necessary. Controls were limited to one exactly-72-byte pair; no new below-72-byte case, per-Unicode-pair original/wrong-first-byte controls or replayed random seed was included. Normalization, invalid surrogates and general Unicode behavior were not tested.

### Advisory mapping and impact limits

The [Spring advisory](https://spring.io/security/cve-2025-22228/) lists 6.2.0–6.2.9 as affected and 6.2.10 as the corresponding enterprise fix; 6.2.4 is inside that interval. Its prose describes long-input prefix equivalence. The [official fix commit](https://github.com/spring-projects/spring-security/commit/46f0dc6dfc8402cd556c598fdf2d31f9d46cdbf3) enforces 72 **bytes** and throws IllegalArgumentException above that bound. Advisory prose says characters; these measures coincide for the tested ASCII case. Both primary pages were retrieved again on 22 October 2026 for this draft.

The demonstrated consequence is a wider accepted credential equivalence class than the full submitted password suggests. Suffix bytes beyond the effective limit did not distinguish the tested credentials. This is actionable application behavior matching a known dependency issue. It does not show a real victim password, real-user harm, account takeover, a bypass requiring no password knowledge, or browser execution. Change/reset paths, Unicode normalization/boundary behavior in application flows, production overrides and recovery consequences are unverified.

### Minimum remediation and retest proposal

This was the review proposal. The implementation and final full-suite result
are recorded in the [remediation audit](../audit/2026-10-22-a05-bcrypt-remediation/README.md).
The fix is committed and pushed but remains undeployed. An explicit
existing-account recovery rollout plan and broader A05/R7 disposition remain
outstanding.

1. Select a supported, compatible Boot/Security dependency set containing the vendor fix; confirm module alignment with the effective runtime tree. The advisory's 6.2.10 entry is enterprise-only, so this report does not prescribe that artifact or infer current support eligibility.
2. Decide and document a consistent UTF-8 byte policy for registration, login, current/new password changes and reset confirmation. Deliberately reject unsupported lengths with a client error before library exceptions can become 500 responses. Application validation does not itself prove the vulnerable dependency was patched.
3. Plan recovery for existing over-limit-password accounts before rollout. Preserve existing hashes/data; do not silently truncate or rewrite credentials. Evaluate a controlled reset/recovery path and any encoding migration separately with the owner.
4. Retain focused regressions in an authorized disposable profile: valid 72-byte ASCII and multibyte values; the next byte rejected; different suffix cannot authenticate; known valid short password still works; change/reset boundaries; no 500 responses and expected session semantics. Verify resolved runtime versions and tested source hashes, then run the relevant auth suite. An isolated library test cannot establish application validation or endpoint behavior.

## Record search, communication and follow-up status

Product-identity known-record searches remain **partial/inconclusive**. A later coordinator follow-up received HTTP 200 for the public GitHub repository metadata and exact Maven-coordinate GitHub GHSA and OSV queries; both advisory sources returned zero rows for `com.hotelapp:hotel-student-platform:0.0.1-SNAPSHOT`. Public issues/releases/tags were empty, while the repository security-advisories endpoint returned 404. These lookups do not identify a supported product release or deployed dependency graph, and the 404 does not establish private-advisory absence. No absence of Kadrom advisories is inferred. Dependency advisories are known records for upstream components, not identifiers assigned to Kadrom. The two Actuator/X.509 range conflicts remain explicitly unresolved. Query details and timestamps are in the [R7 lookup audit](../audit/2026-10-22-r7-authorization-followup/README.md).

The intended review recipient is the user/product owner in the current authorized workspace. Review status is **prepared for coordinator/owner disposition**; no contact or transmission occurred. The user's new authorization covers local Kadrom remediation work, not external disclosure or messaging. A private maintainer/program disclosure endpoint and its current policy have not been verified. No external channel is selected or used based merely on a repository URL. If the owner later requests external submission, verify the product's private reporting route and permission before preparing the destination-specific message. No bounty eligibility, duplicate acceptance, maintainer acknowledgement or public disclosure status is claimed.

The parallel [multipart task record](../audit/2026-10-22-a05-multipart-bounded/README.md) and helper are preparation only. The specialist was stopped by an automatic possible-cybersecurity-risk flag before runtime execution; the blocked action was not rerun. The user has reserved multipart testing for their own follow-up after this conversation. No request, cleanup result, successful security control or negative advisory result is inferred from that block. The BCrypt local implementation and focused retest are recorded separately; external submission remains outside this authorization.

The evidence types here are pinned source, dependency metadata, recorded local authentication/HTTP observations, and official advisory/fix text. Reflection, resource callbacks, sink observation and browser execution were not produced by this report or by the BCrypt check. In the toolkit contracts, reflection/callback are not execution; CID-matched browser execution would still require separate vulnerability triage. The HTTP 500 and unresolved checks above are not safe results. The local BCrypt remediation advances this one A05 lead; it does not close A05/R7, establish rollout or production state, resolve remaining dependency/identity questions, or authorize external submission.
