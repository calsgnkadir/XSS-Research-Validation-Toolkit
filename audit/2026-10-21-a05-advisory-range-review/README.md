# R7 / A05 — review of two deps.dev advisory keys

## Scope and method

Read-only review of the two advisory keys returned by the prior deps.dev
lookup: `GHSA-gmg8-593g-7mv3` for
`org.apache.poi:poi-ooxml:5.3.0`, and `GHSA-mgvc-8q2h-5pgc` for
`org.springframework.boot:spring-boot-starter-actuator:3.2.5`. The pinned
Kadrom dependency graph and its source/version identity are recorded in the
[effective dependency-tree audit](../2026-10-21-a05-effective-dependency-tree/README.md).

Official GitHub Advisory Database records, their raw reviewed JSON, and vendor
advisories were checked on **2026-10-21 20:19 UTC**. Apache POI's official
security guidance was also checked. This is advisory-range and dependency-path
analysis only: no application endpoint, code path, runtime, test, or disclosure
was exercised. It does not determine exploitability in Kadrom.

## Results

| Returned key and resolved artifact | Identity, alias, and source range | Dependency-path interpretation | Bounded applicability |
|---|---|---|---|
| `GHSA-gmg8-593g-7mv3` — `org.apache.poi:poi-ooxml:5.3.0` | The GitHub-reviewed record identifies the exact Maven package `org.apache.poi:poi-ooxml`, alias `CVE-2025-31672`, and affected range before 5.4.0; 5.4.0 is the fixed version. The issue is improper input validation while parsing OOXML (XLSX/DOCX/PPTX): archives with duplicate ZIP entry names may be interpreted differently by consumers. Apache's changelog notes the release history, and its security guidance advises caution with untrusted documents. | This is an exact direct runtime root in the pinned POM (dependency-tree audit, table of direct roots; POM lines 29–33), not a transitive-artifact substitution. The resolved graph also has POI's `poi` and `poi-ooxml-lite` children, but the GHSA key names the direct `poi-ooxml` artifact itself. | **Version-range match:** 5.3.0 is below 5.4.0. **Product impact unassessed:** the advisory concerns parsing OOXML with this library; this review did not establish whether/how Kadrom processes attacker-controlled OOXML, or any resulting impact. This is a known dependency advisory match, not a newly found vulnerability. |
| `GHSA-mgvc-8q2h-5pgc` — `org.springframework.boot:spring-boot-starter-actuator:3.2.5` | The GitHub-reviewed record aliases `CVE-2026-22733` and names `org.springframework.boot:spring-boot-starter-actuator`. Its ecosystem range includes versions from 3.0.0 through 3.3.13 (last affected), which numerically includes 3.2.5; it lists 3.5.12 and 4.0.4 as fixed for the newer maintained lines. Spring's vendor page describes an authentication bypass when a protected application endpoint is declared beneath the Cloud Foundry Actuator endpoint path, and lists affected supported lines 4.0.0–4.0.3, 3.5.0–3.5.11, 3.4.0–3.4.14, 3.3.0–3.3.17, and 2.7.31 and earlier; it lists corresponding fixes including 3.3.18 and 2.7.32 as enterprise-support-only. | The starter is itself a direct compile/runtime root (dependency-tree audit, direct-root table; POM lines 129–132), so the deps.dev key is not simply a different transitive artifact. The audit also shows `spring-boot-starter-web` and `spring-boot-starter-security` as direct roots, consistent with two framework prerequisites named by Spring. The affected behavior is Spring Boot endpoint routing/security interaction; the starter coordinate serves as the package key and does not by itself prove that Kadrom has the vulnerable endpoint mapping. | **Database range match:** GitHub's package range places 3.2.5 within its 3.0.0–3.3.13 range. **Vendor-version discrepancy:** Spring's page does not enumerate 3.2.x among the affected product lines or its listed fixes. Resolve this branch-specific discrepancy with authoritative maintainer/version support information before making a definitive product-version applicability claim. The documented route precondition also has not been checked against application source. No authentication bypass was reproduced or confirmed. |

## Source comparison and limits

- The GitHub record for [GHSA-gmg8-593g-7mv3](https://github.com/advisories/GHSA-gmg8-593g-7mv3)
  and its [reviewed JSON](https://raw.githubusercontent.com/github/advisory-database/main/advisories/github-reviewed/2025/04/GHSA-gmg8-593g-7mv3/GHSA-gmg8-593g-7mv3.json)
  identify CVE-2025-31672 and the `< 5.4.0` Maven range. Apache's [security guidance](https://poi.apache.org/security.html)
  recommends avoiding untrusted input parsing where possible and applying containment; it does not assert that every application using POI is exploitable.
- The GitHub record for [GHSA-mgvc-8q2h-5pgc](https://github.com/advisories/GHSA-mgvc-8q2h-5pgc)
  and its [reviewed JSON](https://raw.githubusercontent.com/github/advisory-database/main/advisories/github-reviewed/2026/03/GHSA-mgvc-8q2h-5pgc/GHSA-mgvc-8q2h-5pgc.json)
  identify CVE-2026-22733. Spring's [vendor advisory](https://spring.io/security/cve-2026-22733/)
  gives the concrete application preconditions and maintained-line versions. The GitHub JSON's broad 3.0.0–3.3.13 range and the vendor page's omission of 3.2.x are both recorded rather than silently reconciled.
- Apache POI's [changelog](https://poi.apache.org/changes.html) and
  [security guidance](https://poi.apache.org/security.html) were checked as vendor context. The advisory does not show a CVSS-based proof of impact in this selected application.
- `spring-boot-starter-actuator:3.2.5` was directly declared and resolved at that version. The advisory is keyed to the starter package, but the vulnerable behavior described by Spring requires a web app, Actuator and Spring Security on the classpath, plus an application endpoint requiring authentication under a Cloud Foundry Actuator subpath (for example `/cloudfoundryapplication/admin`). The dependency audit shows web, actuator, and security roots, but this review did not inspect route configuration or test the condition.

**Disposition:** one clear affected-version-range match for POI 5.3.0; one GitHub ecosystem-range match for the Actuator starter with an unresolved difference between the GitHub range and Spring's listed release lines. Neither result establishes application exploitability. A05 is a known-advisory triage result, not a disclosure or CVE claim. No tests were run and no files outside this assigned audit note were changed.
