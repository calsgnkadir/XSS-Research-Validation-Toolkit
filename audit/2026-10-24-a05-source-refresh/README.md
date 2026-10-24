# A05 — current Kadrom source reconciliation

Date: 24 October 2026. Roadmap: A05 / R7. This is a coordinator-led,
read-only source and dependency reconciliation. It rebinds the selected
advisory dispositions to the current local source and the already completed
bounded multipart parser retest; it is not a new product test or a full audit.

## Source and dependency identity

The authorized Kadrom checkout is `.dxa/a04-kadrom-source`, branch `main`,
commit `eb031a19f9f6b0715d8b302751542f631216cdd5`. After `git fetch origin`,
`HEAD` matched `origin/main` (`0/0` ahead/behind). The checkout contains the
previously run local, untracked `MultipartParserCleanupTest.java`; its source
and sanitized result are preserved in the [A05 parser audit](../2026-10-24-a05-multipart-cleanup/README.md).
No Kadrom product source, POM, or existing data was changed for this review.

The current `hotelapp/pom.xml` SHA-256 is
`f757453d4066791a0b58409133dd9a3d22a6c932b4ad3a7caa3a51b8aa1678b2`, matching
the value recorded for `b374095`. Maven 3.9.16 regenerated the dependency tree
offline from the current `hotelapp/` directory using the existing local
repository. The result is 16,881 bytes and SHA-256
`d8ebcd896e982834d6d9d42ea7b1d22b687931da1194b9a47dd751147e7bca5`, exactly
matching the saved tree used by the 23 October disposition and OSV query. The
normalized set remains 248 Maven coordinates. The earlier OSV query returned
248 response rows and zero matched rows; because the exact queried tree hash is
unchanged, that result is bound to this source's dependency graph. It is still
not a production graph, a complete advisory inventory, or proof of no CVEs.

Command:

```powershell
mvn -o -ntp -Dmaven.repo.local=<local Maven repository> -DoutputFile=target/a05-refresh-dependency-tree.txt -DoutputType=text dependency:tree
```

The tree file remains in the ignored Kadrom `target/` directory. The Maven
launcher printed a transient access-denied line but completed with `BUILD
SUCCESS`; no tests ran as part of this tree generation.

## Source delta review

From the prior A05 review source `b374095` to `eb031a1`, the POM, controllers,
security/configuration classes, validation classes, resource profiles, and
file-storage implementation were unchanged. The intervening A04/A05 delivery
`0ea07ed` added the narrow malformed-Sort input-error handler in
`GlobalExceptionHandler`; that correction remains in current source. The later
upstream commits changed `User`, standby/application repositories, and GDPR,
SGK-reminder, and standby service code. A path-specific diff from `0ea07ed` to
`eb031a1` confirmed no further changes to the POM, application controllers,
auth/security configuration, password validation, resource profiles,
file-storage implementation, or exception handler.

Therefore the selected advisory versions and application preconditions in the
23 October A05 disposition still describe the current source snapshot. This
review does not claim the changed business-service code received a general
security audit.

## Current disposition

| Lead | Current source disposition |
|---|---|
| BCrypt / CVE-2025-22228 | Current Security is 7.1.1, outside the recorded affected line. The byte-length policy and the bounded prior registration/login remediation test remain in source history. No real account or deployment was tested. |
| Actuator / CVE-2026-22733 | Boot/Actuator 4.1.1 remains outside the recorded affected ranges. The earlier source review found no advisory-specific Cloud Foundry path; deployment overrides remain unchecked. |
| X.509 / CVE-2026-47838 | Security 7.1.1 remains outside the listed affected versions. No X.509 authentication path was found in the reviewed application source; proxy trust configuration remains outside scope. |
| Micrometer / CVE-2026-40984 | Micrometer 1.17.1 remains outside the listed affected ranges. Prior ordinary metric-path observations do not show the advisory's vulnerable version or DoS behavior. |
| Sort / CVE-2026-41711 | Spring Data Commons 4.1.1 remains outside the listed affected ranges. Current `GlobalExceptionHandler` retains the narrow invalid-sort-to-400 behavior from `0ea07ed`; this is error handling, not proof against every DoS condition. |
| Multipart / CVE-2025-48988, CVE-2025-52520, CVE-2025-61795 | Tomcat 11.0.27 remains outside the listed affected ranges. The exact current source has the bounded one-test parser/cleanup result: a 4-byte positive control temp file was removed; one truncated request failed before handler selection with an empty spool; health returned 200. This does not cover the full application/auth chain, proxy, stress, many-part inputs, or other parser builds. |
| RFD and Nimbus leads | The previous bounded source/config dispositions remain applicable because their relevant controllers, auth configuration, POM and resource profiles did not change in the upstream delta. No browser RFD or deployment override conclusion is added. |

The underlying selected advisory criteria, vendor range citations, and per-lead
limits remain in the [23 October disposition](../2026-10-23-a05-current-source-disposition/README.md).
The parser observation is in the [24 October test record](../2026-10-24-a05-multipart-cleanup/README.md).

## Conclusion and remaining boundary

The source and dependency reconciliation is complete for the selected A05
leads: they have been rebound to `eb031a1`, and the regenerated dependency
tree exactly matches the previously queried 248-coordinate graph. No newly
applicable CVE candidate was identified in this bounded review. The earlier
Spring Security BCrypt reproduction was a match to an existing upstream
CVE-2025-22228 and the remediation is recorded separately; it was not a new
Kadrom CVE assignment.

Umbrella A05 remains **partial** because no deployed artifact, production
dependency graph, proxy/WAF configuration, large/many-part stress case, or
all-parser-error-path review was performed. No CVE-free or product-wide safe
claim follows. The owner report remains internal; external contact, disclosure,
and CVE assignment were not performed.
