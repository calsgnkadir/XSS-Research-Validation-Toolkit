# R7 / A05 — Spring and Tomcat source impact triage

## Scope and evidence type

Read-only review of the user-selected Kadrom source checkout at
`.dxa/a04-kadrom-source`, pinned commit
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. This note covers only the
transitive advisory rows assigned for `tomcat-embed-core:10.1.20`, Spring Data
Commons `3.2.5`, Spring Security `6.2.4`, and Spring Framework `6.1.6`.

I compared the exact package/range entries and descriptions in the official
GitHub Advisory records linked below with the pinned Java source, YAML, and
POM. The effective versions and dependency paths are recorded in the
[effective tree](../2026-10-21-a05-effective-dependency-tree/README.md); the
version-range inventory is in the
[transitive range review](../2026-10-21-a05-transitive-range-review/README.md).
This is source/configuration analysis only. No Kadrom process, unit/integration
test, build, Docker container, HTTP/WebSocket endpoint, or external service was
run. No finding, exploitability, deployment behavior, or runtime guarantee is
claimed.

The roadmap mapping is **R7 / A05**: known-advisory applicability triage. The
advisory database's range hit is not itself a product vulnerability. Status
terms below mean: **plausible path** = source contains the feature and relevant
input/configuration, so bounded local validation is justified; **not found** =
the specific precondition was not found in the pinned source/config searched;
**unresolved** = source alone cannot establish a required deployment/runtime
fact or advisory-version record conflicts with its prose.

## Source map

The pinned POM supplies Spring MVC, WebSocket, Security and Data JPA at lines
`39`, `45`, `56`, and `68`; the runtime tree resolves the reviewed versions.
Selected application evidence:

| File and lines in pinned checkout | Observation |
|---|---|
| `hotelapp/src/main/java/com/hotelapp/controller/ApplicationController.java:46-51,89-100` | MVC endpoints accept Spring `Pageable`; default sort is `createdAt`. |
| `hotelapp/src/main/java/com/hotelapp/controller/MessageController.java:54-61,80-88` | Two MVC endpoints accept `Pageable` for conversations/messages. |
| `hotelapp/src/main/java/com/hotelapp/config/WebSocketConfig.java:31-63` | STOMP broker is enabled at `/ws`, with `/app`, `/topic`, and `/user` destinations. |
| `hotelapp/src/main/java/com/hotelapp/controller/ChatWsController.java:48-83` | A STOMP `@MessageMapping` handles a client message and broadcasts typing state. |
| `hotelapp/src/main/java/com/hotelapp/security/StompAuthorizationInterceptor.java:50-110` | CONNECT requires a valid bearer JWT; SUBSCRIBE destinations are allowlisted and typing subscriptions require conversation membership; SEND is limited to `/app/**`. |
| `hotelapp/src/main/java/com/hotelapp/config/SecurityConfig.java:103-140` | Servlet Spring Security response headers are explicitly configured: HSTS, frame options, Referrer Policy, CSP, and a custom Permissions Policy. |
| `hotelapp/src/main/java/com/hotelapp/controller/MessageController.java:30-50` | Authenticated attachment download emits `Content-Disposition` using `ContentDisposition.attachment().filename(name, UTF_8)`. |
| `hotelapp/src/main/java/com/hotelapp/service/MessageService.java:294-324` | A conversation member can upload an attachment; `MultipartFile.getOriginalFilename()` is stored verbatim as `attachmentName`. |
| `hotelapp/src/main/java/com/hotelapp/service/FileStorageService.java:31-46,52-75` | Attachment extension and size are validated (15 MB service limit); file bytes are stored as private raw objects through Cloudinary. |
| `hotelapp/src/main/resources/application.yml:81-85` and `application-prod.yml:81-85` | Servlet multipart is enabled with 20 MB/file and 25 MB/request limits. |
| `hotelapp/src/main/resources/application.yml:1-2` | App server port is configurable; no HTTP/2 or TLS connector setting appears here. |
| `hotelapp/src/main/resources/application-prod.yml:13-24,31-39` | Production comments/config say TLS terminates at a proxy, and configure native forwarded-header handling and thread limits. This does not describe or prove every deployment hop. |
| `hotelapp/src/main/java/com/hotelapp/config/AppConfig.java:74-75` | The configured password encoder is `BCryptPasswordEncoder`. |
| `hotelapp/src/main/java/com/hotelapp/service/AuthService.java:62-82,288-320` | Registration/change flows apply the project's password policy and use the encoder. |

Searches across the pinned `src/main/java`, `src/main/resources`, and POM found
no `@ProjectedPayload`, user-controlled SpEL parser/evaluator, `@ModelAttribute`
controller, X.509 or Digest authentication configuration, Tomcat `Realm`,
`LockOutRealm`, CGI servlet, WebDAV servlet, AJP connector, RewriteValve,
JsonAccessLogValve, servlet `security-constraint`, Tomcat default-servlet
write setting, JSP/XSLT/script-template view configuration, `RouterFunction`,
or explicit static-resource handler/version-resource chain. No files were
found under a main-resource `static/` or `templates/` tree in the checked-out
source. Framework defaults, packaged resources not present in this checkout,
environment overrides, and deployment proxy configuration are not proven by
those source searches.

## Plausible source paths — local validation is justified

### Spring Data Commons Sort parsing — `GHSA-5vpf-xvv7-c8vh` / CVE-2026-41711

The advisory describes a StackOverflow DoS while parsing request `Sort`
parameters and its affected prose includes Spring Data Commons 3.2.0–3.2.15,
which includes 3.2.5. MVC controllers accept `Pageable` at
`ApplicationController.java:46-51,89-100` and `MessageController.java:54-61,80-88`;
Spring's MVC argument resolver therefore receives client `page`, `size`, and
`sort` query values on these routes. This makes the library feature and request
input path source-confirmed. The source does not show runtime request limits or
the actual exception behavior. **Disposition: plausible; not reproduced.**

Smallest useful next check, if the coordinator schedules it: in an isolated
local copy at the pinned commit, send a bounded malformed/deep Sort value only
to one of those own-app routes and record status, bounded completion time, and
whether the process remains responsive. Do not use a public deployment or a
load/volume test.

### Spring Security BCrypt password length — `GHSA-mg83-c7gq-rv5c` /
CVE-2025-22228

The advisory says `BCryptPasswordEncoder.matches` may accept passwords longer
than 72 characters when the first 72 match; its exact affected range includes
Spring Security 6.2.4. `AppConfig.java:74-75` selects `BCryptPasswordEncoder`,
and `AuthService.java:288-320` uses `matches` and encodes the changed password.
Registration also checks `PasswordPolicy` (`AuthService.java:62-82`), but the
read-only source pass did not establish a maximum-length check for every
password entry/match path. **Disposition: plausible; no authentication result
was reproduced.**

Smallest useful next check, if scheduled: in the disposable local account flow,
verify that a synthetic password over the BCrypt limit is rejected before
matching/encoding and cannot authenticate by sharing a 72-character prefix.
Use no existing or real account and do not run a password-guessing loop.

### Multipart parsing — Tomcat `GHSA-h3gc-qfqq-6h8f` / CVE-2025-48988,
`GHSA-wr62-c79q-cv37` / CVE-2025-52520, and Spring MVC
`GHSA-cjpg-rgq5-fr37` / CVE-2026-41853

Kadrom accepts multipart uploads in `MessageController.java:103-115` and other
upload controllers; it enables servlet multipart in both base and production
YAML (`application.yml:81-85`, `application-prod.yml:81-85`). The Spring MVC
advisory concerns multipart request parsing; the Tomcat records concern
multipart resource exhaustion/size-limit handling. The application sets file
and total request byte limits, and its storage service applies a 15 MB
attachment limit, but these source limits do not establish how many parts,
headers, parser allocations, or repeated requests are bounded in the effective
server. **Disposition: plausible feature path; exact runtime preconditions and
impact unresolved.**

Smallest useful next check, if scheduled: one disposable local request against
the own-app multipart endpoint with a small, non-destructive boundary case
within a strict request/time budget; inspect response and process health. Do not
test resource exhaustion or send repeated traffic.

### Download filename / reflected file download — Spring Web
`GHSA-6r3c-xf4w-jxjm` / CVE-2025-41234

The advisory's conditions are unusually specific. The official GHSA requires
all of: a `Content-Disposition` header prepared with
`ContentDisposition`; `filename(String, Charset)` (and a non-ASCII charset);
a filename derived from user input; that input not being sanitized; and an
attacker's ability to inject malicious content into the downloaded response.
The source comparison is:

- **Charset overload:** present. `MessageController.java:46-50` calls
  `ContentDisposition.attachment().filename(name, UTF_8)`.
- **User-controlled filename:** present. `MessageService.java:307-320` takes
  `MultipartFile.getOriginalFilename()` and stores it unchanged as
  `attachmentName`.
- **Sanitization:** no filename normalization/character filtering was found
  between that assignment and the header construction. Extension validation in
  `FileStorageService.java:31-46,52-75` does not sanitize the stored original
  name.
- **Attacker-controlled downloaded content:** a conversation member can upload
  file bytes (`MessageService.java:294-324`; `FileStorageService.java:52-75`),
  and the later download returns the stored attachment bytes
  (`MessageController.java:30-50`). The repository does not show a content
  transformation or active-content neutralization on this path. The precise
  browser/RFD behavior was not exercised.
- **Authorization/recipient flow:** upload requires an authenticated
  conversation member (`MessageService.java:295-299`); download is also
  authenticated and calls the conversation-membership-checked
  `getAttachmentForUser` (`MessageController.java:30-35`,
  `MessageService.java:282-291`). The likely flow therefore requires a member
  to upload and another authorized recipient to download; this is a meaningful
  condition and is not equivalent to an unauthenticated endpoint.

These source facts make this a specific lead, not a reproduced or confirmed
RFD. The advisory's own precondition list and limits are preserved in its
[official GHSA record](https://github.com/advisories/GHSA-6r3c-xf4w-jxjm). The
source includes:
`MessageController.java:46-50` builds the header through exactly that API with
UTF-8, while `MessageService.java:307-320` stores the multipart
`getOriginalFilename()` unchanged as `attachmentName`. The download returns the
stored private attachment bytes at `MessageController.java:30-50`; an uploaded
conversation attachment can therefore supply both a filename and content. The
download is gated to authenticated conversation users (`MessageController.java:30-35`
and `MessageService.java:282-291`). This limits the actor to a participant who
can upload an attachment and requires a recipient to download it; it does not
remove the source-level feature match. Existing sanitization of filename/content
was not established by this read-only review. **Disposition: plausible
application path; candidate only, not a confirmed RFD.**

Smallest useful next check, if scheduled: in a disposable local setup, use two
synthetic members of a test conversation, a harmless marker filename containing
non-ASCII characters, and inert response content; inspect the resulting
`Content-Disposition` and browser/download interpretation. Avoid active script
or shell content. Cloudinary integration would need a local test double or an
already-authorized isolated service; this review did not call it.

### Spring Security HTTP response headers — `GHSA-mf92-479x-3373` / CVE-2026-22732

The pinned application explicitly configures servlet response headers in
`SecurityConfig.java:114-140`, and does not rely solely on Spring Security's
default writer. That is a direct source feature match for this advisory. Its
human-readable GHSA description lists several Spring Security release lines
but omits 6.2.x, while the machine/range inventory returned this key for 6.2.4;
the exact 6.2.4 applicability is therefore **unresolved**. Even if in-range,
source cannot show whether the affected response/dispatch conditions occur.
**Disposition: source path plausible; version and runtime behavior unresolved.**

Smallest useful next check, if scheduled: verify the five configured headers
on a bounded local set of normal, denied, and error-dispatch responses, without
asserting that any missing header is a vulnerability absent the advisory's
exact precondition.

### STOMP/WebSocket — `GHSA-7fch-4f2f-jcgm` / CVE-2025-41254 and
`GHSA-q723-847q-5g8g` / CVE-2026-41838

Kadrom enables STOMP and defines an inbound message handler
(`WebSocketConfig.java:31-63`, `ChatWsController.java:48-83`). The first GHSA
specifically requires STOMP over WebSocket, so its technology precondition is
present. The second concerns predictable WebSocket session IDs combined with
inadequate authorization. Source shows a custom JWT CONNECT check and
destination/participant checks (`StompAuthorizationInterceptor.java:50-110`),
but that is not a runtime authorization proof and says nothing about session ID
entropy. **Disposition: feature match; security outcome unresolved.** A bounded
local two-account test of unauthorized STOMP SEND/SUBSCRIBE destinations and
session separation is the smallest relevant next check; it was not run.

## Not found in pinned source/configuration

All of the following are exact version-range leads from the range inventory,
but their named application preconditions or framework features were not found
in the searched pinned source. This is source evidence, not a guarantee about
runtime defaults or later deployment overrides.

| Component / advisory key(s) | Advisory condition or affected feature | Pinned-source disposition |
|---|---|---|
| Spring Data Commons `GHSA-5m4m-73w9-8433` / CVE-2026-41721 | Spring Data Web Support together with a controller using `@ProjectedPayload` and attacker request data. | Pageable support exists, but no `@ProjectedPayload` use was found. Required sink not found. |
| Spring Security Core `GHSA-q3v6-hm2v-pw99` / CVE-2024-38827 | Locale-sensitive case conversion in authorization comparisons; exact range is 6.2.0–6.2.7. | Range includes 6.2.4. Source search found role/path rules and no custom case-conversion authorization expression; actual framework behavior not tested. Mark **unresolved framework-default path**, rather than asserting absence. |
| Spring Security Web `GHSA-c4q5-6c82-3qpw` / CVE-2024-38821 | Static-resource authorization bypass is WebFlux-only and requires Spring Security non-`permitAll` static-resource rules. | The POM selects servlet MVC, not WebFlux; no reactive starter or WebFlux security chain was found. Required WebFlux path not found. |
| Spring Security Web `GHSA-293q-567p-wmwq` / CVE-2026-47838 | `SubjectDnX509PrincipalExtractor` malformed-certificate username extraction. The official page's structured Maven range is `>=6.0.0, <=6.3.10`, which includes 6.2.4; its prose's list of supported affected lines starts at 6.3.x and omits 6.2.x. | **Preserve the GHSA structured-range vs narrative/vendor-line discrepancy.** No X.509 authentication or `SubjectDnX509PrincipalExtractor` configuration was found. The implementation-specific feature is not present in source, but the exact 6.2.4 applicability remains unresolved. Do not upgrade this dependency metadata lead to a product vulnerability. |
| Spring Web `GHSA-2rmj-mq67-h97g` / CVE-2024-38809 | DoS when an application parses `If-Match` or `If-None-Match` ETags. | No explicit conditional-request parsing, ETag generation, or `checkNotModified` path was found in the application sources; controller endpoints are application API handlers (for example, `ApplicationController.java:46-51,89-100`). Whether framework defaults or deployment resource handlers parse these headers is unresolved. **Application-specific feature not found; framework/default path unresolved.** |
| Spring Context + Spring Web `GHSA-4gc7-5j7h-4qph` / CVE-2024-38820 and Spring Context `GHSA-4wp7-92pw-q264` / CVE-2025-22233 | Case-insensitive `DataBinder.disallowedFields` behavior and bypass. | No MVC `@ModelAttribute` binding or explicit `DataBinder`/`disallowedFields` configuration was found. JSON `@RequestBody` DTOs do exist, but are not the named binder path. Generic request parameter conversion remains framework behavior, so runtime absence is not proven. Mark **specific sink not found**. |
| Spring Expression `GHSA-9f52-rjqv-25qv` / CVE-2026-41852, `GHSA-r5w3-xv2f-j59q` / CVE-2026-41850, `GHSA-wxpp-56q6-5pcg` / CVE-2026-41851 | Arbitrary method invocation / CPU or cache DoS requires evaluation of attacker-supplied SpEL. | No application SpEL parser, evaluator, expression input, or expression-backed user setting was found. Method-security annotations contain fixed developer-authored expressions (for example `AdminController.java:37-39`); no user-controlled expression flow identified. |
| Spring MVC `GHSA-3chg-m5w7-qfv5` / CVE-2026-41845, `GHSA-957g-f97v-vppc` / CVE-2026-41846, and Spring MVC `GHSA-4773-3jfm-qmx3` / CVE-2026-22737, `GHSA-pc63-qcmh-9cmg` / CVE-2026-47884 | JavaScriptUtils/JSP form-tag XSS; script-template or XSLT view path traversal. | No JSP files, JSP form tags, JavaScriptUtils calls, script-template engine, XSLT view resolver, or attacker-controlled view name was found in the pinned main source. |
| Spring MVC `GHSA-6hcq-hmm3-jj3c` / CVE-2026-22735 | Server-Sent Event stream corruption. | No `SseEmitter`, `ServerSentEvent`, or event-stream controller output was found. |
| Spring MVC `GHSA-72pg-x5f8-j25j` / CVE-2026-41843, `GHSA-mq64-j8f9-9gcj` / CVE-2026-41841, `GHSA-wg35-8jpf-2xv3` / CVE-2026-22741, `GHSA-x23c-287f-qqv5` / CVE-2026-41842 | Versioned/static-resource traversal, cache disclosure/poisoning, or DoS. | No application static-resource handler, version-resource resolver/chain, or main-resource static asset tree was found. Spring Boot defaults and environment overrides are unresolved; no resource endpoint was tested. |
| Spring MVC `GHSA-6p4f-wcwh-5vvm` / CVE-2026-22745 | Static-resource DoS requires MVC plus filesystem-backed static resources on Windows. | MVC is present; no filesystem static-resource location was found in source. Deployment OS and external resource configuration are unknown. **Unresolved platform/resource condition**, not a source-confirmed path. |
| Spring MVC `GHSA-cx7f-g6mp-7hqm` / CVE-2024-38816, `GHSA-g5vr-rgqm-vf78` / CVE-2024-38819, and `GHSA-r936-gwx5-v52f` / CVE-2025-41242 | Functional route/static-resource path traversal patterns. | Controllers use annotation mappings under `/api`; no `RouterFunction` or functional static-resource route found. Required route style not found. |
| Spring MVC `GHSA-h3qp-gqrc-q736` / CVE-2026-41844 | Open-redirect behavior in Spring MVC/WebFlux. | App has OAuth and billing redirects, but their destinations are formed from configured `app.base-url` or fixed local paths (`OAuth2SuccessHandler.java:32-46`; `BillingService.java:140-179`), not an identified request-provided redirect URL. No affected redirect path found in the source reviewed. |

## Tomcat 10.1.20 — advisory-by-advisory feature grouping

The complete 34-key list below matches the exact `tomcat-embed-core:10.1.20`
row in the range review. Each key was checked against its linked GHSA title and
stated condition, then mapped to source/configuration evidence above. Multiple
keys are grouped only where they share the same specific Tomcat feature.

| GHSA / CVE | Source triage |
|---|---|
| `GHSA-27hp-xhwr-wr2m` / CVE-2024-56337; `GHSA-5j33-cvvr-w245` / CVE-2024-50379 | TOCTOU during JSP compilation requires case-insensitive file system and Tomcat DefaultServlet write enabled (non-default). No JSP/static file root or write-enabled DefaultServlet setting found; app files are uploaded through multipart to private Cloudinary storage. **Specific precondition not found.** |
| `GHSA-83qj-6fr2-vhqg` / CVE-2025-24813 | Partial PUT issue requires writable Tomcat DefaultServlet and its file-backed target. No such servlet write setting or filesystem resource path found. **Specific precondition not found.** |
| `GHSA-h2fw-rfh5-95r3` / CVE-2025-46701 | CGI security-constraint bypass requires the CGI servlet. No CGI servlet declaration or mapping found. **Specific precondition not found.** |
| `GHSA-42wg-hm62-jcwg` / CVE-2025-49124 | Vulnerability is in the Windows Tomcat installer invoking `icacls.exe`; this Java application's runtime POM/source is not the installer path. **Not applicable to the inspected product source path.** |
| `GHSA-5m62-pw8w-7w9f` / CVE-2026-43515; `GHSA-wc4r-xq3c-5cf3` / CVE-2025-49125; `GHSA-gcx9-497g-6cp6` / CVE-2026-65182 | Servlet security-constraint/resource mapping interactions (including multiple HTTP-method constraints, pre/post resources, or longer/shorter overlapping constraint paths). No `web.xml` constraints, servlet `security-constraint`, pre/post resource roots, or Tomcat context customization found. Spring Security's filter-chain matchers are present (`SecurityConfig.java:141-179`) but do not themselves establish the servlet constraint configuration required by these Tomcat conditions. **Specific precondition not found.** |
| `GHSA-5mp6-jrq3-r938` / CVE-2026-43513; `GHSA-h6fc-48rj-7qqh` / CVE-2026-43512; `GHSA-9xv2-5v5q-p794` / CVE-2026-65905; `GHSA-h3x4-894j-xpx5` / CVE-2026-68525 | Tomcat `LockOutRealm`, Digest authenticator, or FORM authentication behavior. No Tomcat Realm/Digest/FORM login configuration found. App authentication is Spring Security JWT/OAuth (`SecurityConfig.java:194-207`) rather than a configured container Realm. **Specific precondition not found.** |
| `GHSA-9m89-8frq-c98c` / CVE-2026-43514 | AJP connector secret comparison. No AJP connector declaration/custom connector factory found. **Specific precondition not found.** |
| `GHSA-ff77-26x5-69cr` / CVE-2025-31651; `GHSA-23hv-mwm6-g8jf` / CVE-2025-55668 | Rewrite rule/session fixation via RewriteValve. No RewriteValve or rewrite configuration found. **Specific precondition not found.** |
| `GHSA-fpj8-gq4v-p354` / CVE-2025-66614 | Client-certificate verification bypass. The app YAML configures an ordinary server port and production TLS termination at a proxy; no server-side client-certificate or TLS connector config found. **App-local condition not found; proxy/deployment behavior unresolved.** |
| `GHSA-7jqf-v358-p8g7` / CVE-2024-38286 | TLS handshake resource exhaustion. No TLS connector is configured in the app YAML; production comments place TLS at a reverse proxy. **Not found in app-local connector configuration; external TLS endpoint is outside this source review.** |
| `GHSA-25xr-qj8w-c4vf` / CVE-2025-53506; `GHSA-3p2h-wqq4-wf4h` / CVE-2025-31650; `GHSA-r29c-68gh-xp6x` / CVE-2026-41293; `GHSA-wm9w-rjj3-j356` / CVE-2024-34750 | HTTP/2 stream, malformed priority header, HTTP/2 request-header, or HTTP/2 excessive-header handling. No embedded HTTP/2/ALPN setting found in source. Production TLS is proxied, but source does not state the proxy's protocol negotiation or upstream protocol. **Unresolved deployment/proxy precondition; not runtime-tested.** |
| `GHSA-563x-q5rq-57qp` / CVE-2026-24880 | Invalid chunk-extension request smuggling; exploit relevance depends on request parsing and any intermediary's interpretation. Production has a proxy hop, but its parser behavior is not part of this checkout. **Unresolved deployment-dependent condition.** |
| `GHSA-h3gc-qfqq-6h8f` / CVE-2025-48988; `GHSA-wr62-c79q-cv37` / CVE-2025-52520; `GHSA-hgrr-935x-pq79` / CVE-2025-61795 | Multipart upload DoS / size-limit bypass / delayed cleanup of disk-backed temporary parts on multipart processing errors. Multipart is enabled and upload endpoints exist, while byte caps are configured (see multipart section). Temp-file storage/cleanup and effective disk limits are not established by source. **Plausible feature path; validate only with a bounded local check.** |
| `GHSA-fv25-8xcx-gqjc` / CVE-2026-42498 | WebSocket authentication-header exposure. WebSocket/STOMP and an `Authorization` STOMP CONNECT header are present (`WebSocketConfig.java:31-63`, `StompAuthorizationInterceptor.java:56-58,77-95`). Exact GHSA condition concerns Tomcat WebSocket authentication handling; whether Spring's STOMP native header reaches that affected path is **unresolved**. Do not infer token exposure from the header's existence. |
| `GHSA-gx5v-xp9w-j4cg` / CVE-2026-41284 | WebDAV LOCK/PROPFIND unbounded read. No WebDAV servlet/resource set or LOCK/PROPFIND handler found. **Specific precondition not found.** |
| `GHSA-rv64-5gf8-9qq8` / CVE-2026-34483 | `JsonAccessLogValve` output encoding. No Tomcat access-log valve configured; application logging is configured in `logback-spring.xml`. **Specific valve path not found.** |
| `GHSA-x4m4-345f-5h5g` / CVE-2026-34487 | Kubernetes cloud-membership clustering component may log a bearer token. No Tomcat clustering/cloud-membership component or Kubernetes bearer-token setting found in the pinned app source/config. **Specific component path not found.** |
| `GHSA-vfww-5hm6-hx2j` / CVE-2025-55754 | ANSI escape injection through Tomcat log messages, with the advisory's concrete attack involving a Windows console that supports ANSI. The app's logging config is application Logback; whether embedded Tomcat logs request-derived data to a Windows console in any deployment is unknown. **Deployment/log-sink dependent and unresolved.** |
| `GHSA-mgp5-rv84-w37q` / CVE-2026-24734 | OCSP revocation-response verification when using Tomcat Native/FFM and an OCSP responder. No TLS connector, Tomcat Native/FFM setup, or OCSP responder configuration found. **Specific precondition not found in app-local config; external TLS setup unresolved.** |
| `GHSA-ff77-26x5-69cr` / CVE-2025-31651; `GHSA-23hv-mwm6-g8jf` / CVE-2025-55668; `GHSA-wmwf-9ccg-fff5` / CVE-2025-55752 | Rewrite rule bypass/session fixation/path normalization issues. `GHSA-wmwf` specifically requires rewrite rules that map query parameters into a URL (and PUT for its file-write consequence). No RewriteValve or rewrite configuration found. **Specific precondition not found.** |
| `GHSA-9m3c-qcxr-9x87` / CVE-2026-25854 | Tomcat open redirect. The app has configured-base OAuth/billing redirects, but no Tomcat-generated redirect path sourced from attacker-controlled redirect input was identified (`OAuth2SuccessHandler.java:32-46`; `BillingService.java:140-179`). **Specific source path not found; framework behavior not tested.** |
| `GHSA-gqp3-2cvr-x8m3` / CVE-2025-48989 | Tomcat's “made you reset” resource-shutdown/stream-reset issue. This is generic embedded HTTP protocol handling; no custom connector/context/valve is configured. The exact runtime protocol/trigger behavior is unknown. **Unresolved generic embedded-server behavior; no application exploit path identified.** |

## Recommended next step and limits

The strongest source-specific leads for the coordinator to prioritize are:

1. Spring RFD: user-controlled attachment filename reaches a UTF-8
   `Content-Disposition` builder, with uploaded content later returned to a
   conversation member.
2. Spring Security BCrypt length: the exact encoder is used and GHSA's range
   includes 6.2.4; a source check should verify maximum length enforcement at
   all public password entry points before any local check is attempted.
3. Spring Data `Sort` parsing and multipart parser behavior: the corresponding
   request features are present, but no failure was reproduced.
4. STOMP authorization/session behavior and configured security headers: both
   relevant source features are present, with advisory/version/runtime details
   still unresolved.

If the coordinator continues runtime work, keep it to a disposable local
instance of this user-owned pinned source, synthetic accounts/data, and narrow
non-destructive assertions. No external product endpoint, release/disclosure,
or security report was contacted. No product tests were run in this task.

### Advisory source links

The key-level inventory and CVE aliases are preserved in the linked
[transitive range review](../2026-10-21-a05-transitive-range-review/README.md).
The source-specific leads above are the GitHub-reviewed records for
[CVE-2025-41234 / `GHSA-6r3c-xf4w-jxjm`](https://github.com/advisories/GHSA-6r3c-xf4w-jxjm),
[CVE-2025-22228 / `GHSA-mg83-c7gq-rv5c`](https://github.com/advisories/GHSA-mg83-c7gq-rv5c),
[CVE-2026-41711 / `GHSA-5vpf-xvv7-c8vh`](https://github.com/advisories/GHSA-5vpf-xvv7-c8vh),
[CVE-2026-41853 / `GHSA-cjpg-rgq5-fr37`](https://github.com/advisories/GHSA-cjpg-rgq5-fr37),
[CVE-2025-48988 / `GHSA-h3gc-qfqq-6h8f`](https://github.com/advisories/GHSA-h3gc-qfqq-6h8f),
[CVE-2025-52520 / `GHSA-wr62-c79q-cv37`](https://github.com/advisories/GHSA-wr62-c79q-cv37),
[CVE-2025-41254 / `GHSA-7fch-4f2f-jcgm`](https://github.com/advisories/GHSA-7fch-4f2f-jcgm),
[CVE-2026-41838 / `GHSA-q723-847q-5g8g`](https://github.com/advisories/GHSA-q723-847q-5g8g), and
[CVE-2026-22732 / `GHSA-mf92-479x-3373`](https://github.com/advisories/GHSA-mf92-479x-3373).
