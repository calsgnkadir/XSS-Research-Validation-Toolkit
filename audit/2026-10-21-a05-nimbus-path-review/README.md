# R7 / A05 — Nimbus deep-nested JSON path review

## Scope and method

Read-only follow-up to the Nimbus item in
[`a05-other-source-review`](../2026-10-21-a05-other-source-review/README.md).
The inspected Kadrom checkout is the locally retained source snapshot at
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. Its `hotelapp/pom.xml` SHA-256 is
`AF8E4AED12B15A646460987E2FD94BDA8F31C482537498599A3BB473B5CE8112`.

I reviewed only that pinned source and artifacts already present in the local
Maven cache. No network access, dependency download, provider, endpoint, build,
test, application runtime, Docker, source change, or disclosure was used.

## Source path

- `hotelapp/src/main/resources/application.yml:91-101` configures the Google
  OAuth registration with the explicit scopes `profile, email` at line 100;
  `openid` is not configured in this pinned file.
- `hotelapp/src/main/java/com/hotelapp/config/SecurityConfig.java:203-206`
  enables OAuth2 login and installs the application's `oAuth2UserService` as
  the user service.
- `hotelapp/src/main/java/com/hotelapp/security/oauth/CustomOAuth2UserService.java:32`
  extends Spring Security's `DefaultOAuth2UserService`; lines 39-41 call
  `super.loadUser(request)` and then consume the returned attribute map.

Thus, for the pinned registration as written, the application is configured
for ordinary OAuth2 login/userinfo and does not request the `openid` scope that
selects the OIDC ID-token flow. The reviewed first-party source does not call
Nimbus JSON/JWT parsing APIs.

## Cached implementation evidence

No `*-sources.jar` was present for the cached Spring Security OAuth2 client,
OAuth2 JOSE, or Nimbus artifacts, so this is not a source-JAR trace. The
following binary artifacts were already cached and inspected with `jar` /
`javap`; their SHA-256 values identify the exact local inputs:

| Artifact | Local Maven-cache path | SHA-256 |
|---|---|---|
| `org.springframework.security:spring-security-oauth2-client:6.2.4` | `%USERPROFILE%\\.m2\\repository\\org\\springframework\\security\\spring-security-oauth2-client\\6.2.4\\spring-security-oauth2-client-6.2.4.jar` | `662E31EE3504B00342E16B6490F57E9005F74AE2B0CFA041323C06F9AC37DFD0` |
| `org.springframework.security:spring-security-oauth2-jose:6.2.4` | `%USERPROFILE%\\.m2\\repository\\org\\springframework\\security\\spring-security-oauth2-jose\\6.2.4\\spring-security-oauth2-jose-6.2.4.jar` | `B019731F03D26FDF22C91091C17106F273270FFD3BCE293C46FC1D4288046132` |
| `com.nimbusds:nimbus-jose-jwt:9.24.4` | `%USERPROFILE%\\.m2\\repository\\com\\nimbusds\\nimbus-jose-jwt\\9.24.4\\nimbus-jose-jwt-9.24.4.jar` | `8D589630722A4C56349248652477FDAA4E30DF9C732C4D6EAC2F271437246304` |

In the cached `DefaultOAuth2UserService.loadUser` bytecode, the userinfo
response is typed as `Map<String,Object>` and passed through
`RestOperations.exchange(RequestEntity, ParameterizedTypeReference)`; the
service constructs a `RestTemplate`. The cached
`OAuth2LoginAuthenticationProvider.authenticate` bytecode calls its configured
`OAuth2UserService.loadUser`. These observations support the configured
OAuth2 userinfo path, whose JSON mapping is handled by Spring's HTTP message
conversion path. They do not show that provider JSON reaches Nimbus's
deep-nested-JSON parser.

The cached `OidcAuthorizationCodeAuthenticationProvider` bytecode separately
shows that its OIDC path obtains an `id_token` from OAuth token-response
additional parameters and passes it to a `JwtDecoder`. That path is conditional
on OIDC login selection; the pinned registration explicitly lists only
`profile, email`. Merely having OAuth2 JOSE and Nimbus on the classpath does not
establish that this path runs. Runtime/deployment overrides were not inspected.

## Bounded disposition

The previous **plausible but unresolved** Nimbus path is narrowed for the
pinned source/configuration: no source-supported chain was found from the
configured provider's JSON userinfo response to Nimbus's affected recursive
JSON parser. The inspected built-in userinfo path consumes a Spring-converted
map; the OIDC/JWT decoder path is not selected by the checked scope list. This
is source plus cached-bytecode analysis, not a runtime reproduction.

Accordingly, no mock-provider validation is recommended on the current
evidence: the necessary Nimbus parser chain is not source-supported for this
configuration. Revisit only if the pinned configuration changes to request
`openid`, a Nimbus-backed user-info/JWT parser is introduced, or deployment
overrides are explicitly brought into the authorized local scope. The
currently reviewed path establishes neither a product vulnerability nor a
general safety conclusion, and it does not alter A05's other unresolved
advisory leads.

## Evidence classification and roadmap

- **R7 / A05:** read-only source/configuration and cached-bytecode analysis.
- **Reflection:** not evaluated here.
- **Callback:** none used or observed.
- **Browser/JavaScript execution:** none.
- **Vulnerability triage:** no reproduced failure and no product finding. The
  deps.dev advisory key remains a dependency lead; this review finds no
  applicable provider-JSON-to-Nimbus parser chain in the pinned configuration.
- No tests or product behavior were re-run.
