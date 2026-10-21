# R7 / A05 — transitive advisory range review

## Scope and method

Read-only metadata review of the 92 distinct GitHub Advisory Database keys
returned for 127 transitive Maven artifacts in the pinned Kadrom compile/runtime
tree. The source identity and effective tree are recorded in the
[dependency-tree audit](../2026-10-21-a05-effective-dependency-tree/README.md);
the original exact-coordinate lookup and key inventory are in the
[deps.dev lookup audit](../2026-10-21-a05-transitive-advisories/README.md).
I opened each returned key at its corresponding official
`https://github.com/advisories/GHSA-…` record and compared the named Maven
package and affected-version range with the exact resolved coordinate/version.
GitHub's [global advisory REST documentation](https://docs.github.com/en/rest/security-advisories/global-advisories)
describes the advisory records' package/version range fields. Each linked
advisory page is also the primary source for its alias/CVE identifier, title,
affected range, and any stated conditions.

This is advisory metadata comparison only. No Kadrom source path was reviewed
in this task; no application, build, test, container, endpoint, or external
target was run or contacted. A range hit means only that the pinned library
version is named in the advisory's affected range for that artifact. It does
not establish that the application invokes the affected function, meets the
advisory's configuration/precondition, is exploitable, or has a product
vulnerability. A range miss is not a safety conclusion.

## Coordinate-to-range results

All keys listed below were individually opened and their affected artifact and
range compared with the exact version. `—` means no key in that row was
outside-range or unresolved in this bounded review. Advisory identifiers link
to the official GHSA record, where a CVE alias is shown when one is assigned.

| Exact transitive Maven coordinate/version | In-range advisory keys | Out of range | Unresolved |
|---|---|---|---|
| `ch.qos.logback:logback-core@1.4.14` | [GHSA-25qh-j22f-pwp8](https://github.com/advisories/GHSA-25qh-j22f-pwp8), [GHSA-6v67-2wr5-gvf4](https://github.com/advisories/GHSA-6v67-2wr5-gvf4), [GHSA-jhq6-gfmj-v8fx](https://github.com/advisories/GHSA-jhq6-gfmj-v8fx), [GHSA-p47f-322f-whfh](https://github.com/advisories/GHSA-p47f-322f-whfh), [GHSA-pr98-23f8-jwxv](https://github.com/advisories/GHSA-pr98-23f8-jwxv), [GHSA-qqpg-mvqg-649v](https://github.com/advisories/GHSA-qqpg-mvqg-649v) | — | — |
| `com.fasterxml.jackson.core:jackson-core@2.15.4` | [GHSA-72hv-8253-57qq](https://github.com/advisories/GHSA-72hv-8253-57qq), [GHSA-7hhh-6rmp-j9qf](https://github.com/advisories/GHSA-7hhh-6rmp-j9qf), [GHSA-r7wm-3cxj-wff9](https://github.com/advisories/GHSA-r7wm-3cxj-wff9) | — | — |
| `com.fasterxml.jackson.core:jackson-databind@2.15.4` | [GHSA-3pjw-73gf-8qr5](https://github.com/advisories/GHSA-3pjw-73gf-8qr5), [GHSA-5gvw-p9qm-jgwh](https://github.com/advisories/GHSA-5gvw-p9qm-jgwh), [GHSA-5jmj-h7xm-6q6v](https://github.com/advisories/GHSA-5jmj-h7xm-6q6v), [GHSA-cxp5-3px4-pw24](https://github.com/advisories/GHSA-cxp5-3px4-pw24), [GHSA-gx83-3vf8-gh7j](https://github.com/advisories/GHSA-gx83-3vf8-gh7j), [GHSA-hgj6-7826-r7m5](https://github.com/advisories/GHSA-hgj6-7826-r7m5), [GHSA-j3rv-43j4-c7qm](https://github.com/advisories/GHSA-j3rv-43j4-c7qm), [GHSA-q4xh-88c3-wmh7](https://github.com/advisories/GHSA-q4xh-88c3-wmh7), [GHSA-rmj7-2vxq-3g9f](https://github.com/advisories/GHSA-rmj7-2vxq-3g9f), [GHSA-vvgp-rfg2-7rr6](https://github.com/advisories/GHSA-vvgp-rfg2-7rr6), [GHSA-wjgm-6hv5-3cvf](https://github.com/advisories/GHSA-wjgm-6hv5-3cvf), [GHSA-wv8q-qhhj-9h54](https://github.com/advisories/GHSA-wv8q-qhhj-9h54) | — | — |
| `com.nimbusds:nimbus-jose-jwt@9.24.4` | [GHSA-gvpg-vgmx-xg6w](https://github.com/advisories/GHSA-gvpg-vgmx-xg6w), [GHSA-xwmg-2g98-w7v9](https://github.com/advisories/GHSA-xwmg-2g98-w7v9) | — | — |
| `io.micrometer:micrometer-core@1.12.5` | [GHSA-g3pr-3p32-fp23](https://github.com/advisories/GHSA-g3pr-3p32-fp23) | — | — |
| `org.apache.commons:commons-lang3@3.13.0` | [GHSA-j288-q9x7-2f5v](https://github.com/advisories/GHSA-j288-q9x7-2f5v) | — | — |
| `org.apache.httpcomponents:httpclient@4.4` | [GHSA-7r82-7xv7-xcpj](https://github.com/advisories/GHSA-7r82-7xv7-xcpj) | — | — |
| `org.apache.logging.log4j:log4j-api@2.21.1` | [GHSA-qv9r-c865-cp47](https://github.com/advisories/GHSA-qv9r-c865-cp47) | — | — |
| `org.apache.tomcat.embed:tomcat-embed-core@10.1.20` | [GHSA-23hv-mwm6-g8jf](https://github.com/advisories/GHSA-23hv-mwm6-g8jf), [GHSA-25xr-qj8w-c4vf](https://github.com/advisories/GHSA-25xr-qj8w-c4vf), [GHSA-27hp-xhwr-wr2m](https://github.com/advisories/GHSA-27hp-xhwr-wr2m), [GHSA-3p2h-wqq4-wf4h](https://github.com/advisories/GHSA-3p2h-wqq4-wf4h), [GHSA-42wg-hm62-jcwg](https://github.com/advisories/GHSA-42wg-hm62-jcwg), [GHSA-563x-q5rq-57qp](https://github.com/advisories/GHSA-563x-q5rq-57qp), [GHSA-5j33-cvvr-w245](https://github.com/advisories/GHSA-5j33-cvvr-w245), [GHSA-5m62-pw8w-7w9f](https://github.com/advisories/GHSA-5m62-pw8w-7w9f), [GHSA-5mp6-jrq3-r938](https://github.com/advisories/GHSA-5mp6-jrq3-r938), [GHSA-7jqf-v358-p8g7](https://github.com/advisories/GHSA-7jqf-v358-p8g7), [GHSA-83qj-6fr2-vhqg](https://github.com/advisories/GHSA-83qj-6fr2-vhqg), [GHSA-9m3c-qcxr-9x87](https://github.com/advisories/GHSA-9m3c-qcxr-9x87), [GHSA-9m89-8frq-c98c](https://github.com/advisories/GHSA-9m89-8frq-c98c), [GHSA-9xv2-5v5q-p794](https://github.com/advisories/GHSA-9xv2-5v5q-p794), [GHSA-ff77-26x5-69cr](https://github.com/advisories/GHSA-ff77-26x5-69cr), [GHSA-fpj8-gq4v-p354](https://github.com/advisories/GHSA-fpj8-gq4v-p354), [GHSA-fv25-8xcx-gqjc](https://github.com/advisories/GHSA-fv25-8xcx-gqjc), [GHSA-gcx9-497g-6cp6](https://github.com/advisories/GHSA-gcx9-497g-6cp6), [GHSA-gqp3-2cvr-x8m3](https://github.com/advisories/GHSA-gqp3-2cvr-x8m3), [GHSA-gx5v-xp9w-j4cg](https://github.com/advisories/GHSA-gx5v-xp9w-j4cg), [GHSA-h2fw-rfh5-95r3](https://github.com/advisories/GHSA-h2fw-rfh5-95r3), [GHSA-h3gc-qfqq-6h8f](https://github.com/advisories/GHSA-h3gc-qfqq-6h8f), [GHSA-h3x4-894j-xpx5](https://github.com/advisories/GHSA-h3x4-894j-xpx5), [GHSA-h6fc-48rj-7qqh](https://github.com/advisories/GHSA-h6fc-48rj-7qqh), [GHSA-hgrr-935x-pq79](https://github.com/advisories/GHSA-hgrr-935x-pq79), [GHSA-mgp5-rv84-w37q](https://github.com/advisories/GHSA-mgp5-rv84-w37q), [GHSA-r29c-68gh-xp6x](https://github.com/advisories/GHSA-r29c-68gh-xp6x), [GHSA-rv64-5gf8-9qq8](https://github.com/advisories/GHSA-rv64-5gf8-9qq8), [GHSA-vfww-5hm6-hx2j](https://github.com/advisories/GHSA-vfww-5hm6-hx2j), [GHSA-wc4r-xq3c-5cf3](https://github.com/advisories/GHSA-wc4r-xq3c-5cf3), [GHSA-wm9w-rjj3-j356](https://github.com/advisories/GHSA-wm9w-rjj3-j356), [GHSA-wmwf-9ccg-fff5](https://github.com/advisories/GHSA-wmwf-9ccg-fff5), [GHSA-wr62-c79q-cv37](https://github.com/advisories/GHSA-wr62-c79q-cv37), [GHSA-x4m4-345f-5h5g](https://github.com/advisories/GHSA-x4m4-345f-5h5g) | — | — |
| `org.springframework.data:spring-data-commons@3.2.5` | [GHSA-5m4m-73w9-8433](https://github.com/advisories/GHSA-5m4m-73w9-8433), [GHSA-5vpf-xvv7-c8vh](https://github.com/advisories/GHSA-5vpf-xvv7-c8vh) | — | — |
| `org.springframework.security:spring-security-core@6.2.4` | [GHSA-q3v6-hm2v-pw99](https://github.com/advisories/GHSA-q3v6-hm2v-pw99) | — | — |
| `org.springframework.security:spring-security-crypto@6.2.4` | [GHSA-mg83-c7gq-rv5c](https://github.com/advisories/GHSA-mg83-c7gq-rv5c) | — | — |
| `org.springframework.security:spring-security-web@6.2.4` | [GHSA-293q-567p-wmwq](https://github.com/advisories/GHSA-293q-567p-wmwq), [GHSA-c4q5-6c82-3qpw](https://github.com/advisories/GHSA-c4q5-6c82-3qpw), [GHSA-mf92-479x-3373](https://github.com/advisories/GHSA-mf92-479x-3373) | — | — |
| `org.springframework:spring-context@6.1.6` | [GHSA-4gc7-5j7h-4qph](https://github.com/advisories/GHSA-4gc7-5j7h-4qph), [GHSA-4wp7-92pw-q264](https://github.com/advisories/GHSA-4wp7-92pw-q264) | — | — |
| `org.springframework:spring-expression@6.1.6` | [GHSA-9f52-rjqv-25qv](https://github.com/advisories/GHSA-9f52-rjqv-25qv), [GHSA-r5w3-xv2f-j59q](https://github.com/advisories/GHSA-r5w3-xv2f-j59q), [GHSA-wxpp-56q6-5pcg](https://github.com/advisories/GHSA-wxpp-56q6-5pcg) | — | — |
| `org.springframework:spring-web@6.1.6` | [GHSA-2rmj-mq67-h97g](https://github.com/advisories/GHSA-2rmj-mq67-h97g), [GHSA-4gc7-5j7h-4qph](https://github.com/advisories/GHSA-4gc7-5j7h-4qph), [GHSA-6r3c-xf4w-jxjm](https://github.com/advisories/GHSA-6r3c-xf4w-jxjm) | — | — |
| `org.springframework:spring-webmvc@6.1.6` | [GHSA-3chg-m5w7-qfv5](https://github.com/advisories/GHSA-3chg-m5w7-qfv5), [GHSA-4773-3jfm-qmx3](https://github.com/advisories/GHSA-4773-3jfm-qmx3), [GHSA-6hcq-hmm3-jj3c](https://github.com/advisories/GHSA-6hcq-hmm3-jj3c), [GHSA-6p4f-wcwh-5vvm](https://github.com/advisories/GHSA-6p4f-wcwh-5vvm), [GHSA-72pg-x5f8-j25j](https://github.com/advisories/GHSA-72pg-x5f8-j25j), [GHSA-957g-f97v-vppc](https://github.com/advisories/GHSA-957g-f97v-vppc), [GHSA-cjpg-rgq5-fr37](https://github.com/advisories/GHSA-cjpg-rgq5-fr37), [GHSA-cx7f-g6mp-7hqm](https://github.com/advisories/GHSA-cx7f-g6mp-7hqm), [GHSA-g5vr-rgqm-vf78](https://github.com/advisories/GHSA-g5vr-rgqm-vf78), [GHSA-h3qp-gqrc-q736](https://github.com/advisories/GHSA-h3qp-gqrc-q736), [GHSA-mq64-j8f9-9gcj](https://github.com/advisories/GHSA-mq64-j8f9-9gcj), [GHSA-pc63-qcmh-9cmg](https://github.com/advisories/GHSA-pc63-qcmh-9cmg), [GHSA-r936-gwx5-v52f](https://github.com/advisories/GHSA-r936-gwx5-v52f), [GHSA-wg35-8jpf-2xv3](https://github.com/advisories/GHSA-wg35-8jpf-2xv3), [GHSA-x23c-287f-qqv5](https://github.com/advisories/GHSA-x23c-287f-qqv5) | — | — |
| `org.springframework:spring-websocket@6.1.6` | [GHSA-7fch-4f2f-jcgm](https://github.com/advisories/GHSA-7fch-4f2f-jcgm), [GHSA-q723-847q-5g8g](https://github.com/advisories/GHSA-q723-847q-5g8g) | — | — |

## Aliases and interpretation notes

The linked records exposed these CVE aliases (same order as the GHSA IDs in the
coordinate table above). GHSA-only records remain identified by GHSA without an
inferred CVE alias.

- `logback-core`: GHSA-25qh → CVE-2025-11226; GHSA-6v67 → CVE-2024-12801;
  GHSA-jhq6 → CVE-2026-10532; GHSA-p47f → CVE-2026-9828;
  GHSA-pr98 → CVE-2024-12798; GHSA-qqpg → CVE-2026-1225.
- `jackson-core`: GHSA-72hv → CVE-2026-18401; GHSA-7hhh → CVE-2026-89425;
  GHSA-r7wm → CVE-2026-68494. `jackson-databind`: GHSA-3pjw →
  CVE-2026-59888; GHSA-5gvw → CVE-2026-59889; GHSA-5jmj → CVE-2026-54515;
  GHSA-cxp5 → CVE-2026-91777; GHSA-gx83 → CVE-2026-83557; GHSA-hgj6 →
  CVE-2026-54514; GHSA-j3rv → CVE-2026-54512; GHSA-q4xh → CVE-2026-68497;
  GHSA-rmj7 → CVE-2026-54513; GHSA-vvgp → CVE-2026-77310; GHSA-wjgm →
  CVE-2026-19032; GHSA-wv8q → CVE-2026-91776.
- `nimbus-jose-jwt`: GHSA-gvpg → CVE-2023-52428; GHSA-xwmg → CVE-2025-53864.
  `micrometer-core`: GHSA-g3pr → CVE-2026-40984. `commons-lang3`: GHSA-j288 →
  CVE-2025-48924. `httpclient`: GHSA-7r82 → CVE-2020-13956. `log4j-api`:
  GHSA-qv9r → CVE-2026-49844.
- `tomcat-embed-core`: GHSA-23hv → CVE-2025-55668; GHSA-25xr →
  CVE-2025-53506; GHSA-27hp → CVE-2024-56337; GHSA-3p2h → CVE-2025-31650;
  GHSA-42wg → CVE-2025-49124; GHSA-563x → CVE-2026-24880; GHSA-5j33 →
  CVE-2024-50379; GHSA-5m62 → CVE-2026-43515; GHSA-5mp6 → CVE-2026-43513;
  GHSA-7jqf → CVE-2024-38286; GHSA-83qj → CVE-2025-24813; GHSA-9m3c →
  CVE-2026-25854; GHSA-9m89 → CVE-2026-43514; GHSA-9xv2 → CVE-2026-65905;
  GHSA-ff77 → CVE-2025-31651; GHSA-fpj8 → CVE-2025-66614; GHSA-fv25 →
  CVE-2026-42498; GHSA-gcx9 → CVE-2026-65182; GHSA-gqp3 → CVE-2025-48989;
  GHSA-gx5v → CVE-2026-41284; GHSA-h2fw → CVE-2025-46701; GHSA-h3gc →
  CVE-2025-48988; GHSA-h3x4 → CVE-2026-68525; GHSA-h6fc → CVE-2026-43512;
  GHSA-hgrr → CVE-2025-61795; GHSA-mgp5 → CVE-2026-24734; GHSA-r29c →
  CVE-2026-41293; GHSA-rv64 → CVE-2026-34483; GHSA-vfww → CVE-2025-55754;
  GHSA-wc4r → CVE-2025-49125; GHSA-wm9w → CVE-2024-34750; GHSA-wmwf →
  CVE-2025-55752; GHSA-wr62 → CVE-2025-52520; GHSA-x4m4 → CVE-2026-34487.
- `spring-data-commons`: GHSA-5m4m → CVE-2026-41721; GHSA-5vpf →
  CVE-2026-41711. `spring-security-core`: GHSA-q3v6 → CVE-2024-38827.
  `spring-security-crypto`: GHSA-mg83 → CVE-2025-22228. `spring-security-web`:
  GHSA-293q → CVE-2026-47838; GHSA-c4q5 → CVE-2024-38821; GHSA-mf92 →
  CVE-2026-22732.
- `spring-context`: GHSA-4gc7 → CVE-2024-38820; GHSA-4wp7 → CVE-2025-22233.
  `spring-expression`: GHSA-9f52 → CVE-2026-41852; GHSA-r5w3 →
  CVE-2026-41850; GHSA-wxpp → CVE-2026-41851. `spring-web`: GHSA-2rmj →
  CVE-2024-38809; GHSA-4gc7 → CVE-2024-38820; GHSA-6r3c → CVE-2025-41234.
- `spring-webmvc`: GHSA-3chg → CVE-2026-41845; GHSA-4773 → CVE-2026-22737;
  GHSA-6hcq → CVE-2026-22735; GHSA-6p4f → CVE-2026-22745; GHSA-72pg →
  CVE-2026-41843; GHSA-957g → CVE-2026-41846; GHSA-cjpg → CVE-2026-41853;
  GHSA-cx7f → CVE-2024-38816; GHSA-g5vr → CVE-2024-38819; GHSA-h3qp →
  CVE-2026-41844; GHSA-mq64 → CVE-2026-41841; GHSA-pc63 → CVE-2026-47884;
  GHSA-r936 → CVE-2025-41242; GHSA-wg35 → CVE-2026-22741; GHSA-x23c →
  CVE-2026-41842. `spring-websocket`: GHSA-7fch → CVE-2025-41254; GHSA-q723 →
  CVE-2026-41838.

Several records describe narrow configuration or code-path requirements. For
example, GHSA-25qh and GHSA-pr98 require an attacker to influence Logback
configuration/environment with existing privileges; GHSA-7fch requires STOMP
over WebSocket; GHSA-cx7f and GHSA-g5vr require functional static-resource
routes; and GHSA-6p4f states Windows plus filesystem-backed static resource
conditions. These are advisory-record preconditions only; this task did not
check whether Kadrom satisfies them. GHSA-42wg concerns the Tomcat Windows
installer despite the database's Maven coordinate; its version-range match
does not imply that embedding Tomcat in this application exposes the installer
behavior.

## Outcome and limits

The advisory-page comparison covers all 92 distinct keys / 93 coordinate-key
associations returned by the preceding deps.dev transitive query. For every
association, the official record named the same Maven artifact and its
published range included the exact pinned version; this review found 0
outside-range keys and 0 inaccessible/unresolved records. This outcome is
consistent with, but independently checked against, the deps.dev keys. It does
not mean 92 vulnerabilities exist in Kadrom. Applicability triage requires
source-path/configuration review for each advisory and, only where a credible
application condition remains, an authorized local reproduction. No new
product finding, exploit, remediation, or disclosure claim is made.
