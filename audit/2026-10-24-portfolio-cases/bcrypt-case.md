## Case 3 — Known BCrypt boundary behavior and CVE applicability

**Roadmap:** A05 / R7. **Scope:** one authorized local application
authentication path, in-memory H2 test profile, synthetic account only. The
observed baseline was Spring Boot 3.2.5 / Spring Security Crypto 6.2.4; no
production account, deployment, external service, or third-party target was
used. The application identity is intentionally omitted from this portfolio
brief.

**Question and result:** does an input longer than BCrypt's 72-byte boundary
authenticate as the same principal as the first 72 bytes? A focused test sent
one 72-byte password and the same value plus a different byte. Both login
requests returned HTTP 200 for the synthetic principal. A separate one-test
registration follow-up observed acceptance of a policy-valid 73-byte value and
successful login with a different suffix but the same first 72 bytes. These
are bounded local observations, not a practical account-takeover demonstration.

**CVE applicability:** Spring Security's already-assigned
[CVE-2025-22228](https://spring.io/security/cve-2025-22228/) covers the known
BCrypt long-input behavior and lists the tested 6.2.4 line in its affected
range. This is a reproduction of a known upstream library issue in one
application path; it is not a newly discovered application vulnerability. No
CVE was assigned to the application.

**Remediation and regression evidence:** the local remediation aligned the
application to Spring Boot 4.1.1 / Spring Security 7.1.1 and rejects passwords
over 72 UTF-8 bytes before hashing or authentication, without truncation. The
focused remediation selector reported 51 passed; a full Maven run later
reported 665 passed, with no failures, errors, or skips. A subsequent
test-only exact-72-byte multibyte password-change regression passed in a
separate auth-only selector (37 passed); the full suite was not rerun after
that addition. The current-source review found Spring Security 7.1.1 outside
the recorded affected range and no new candidate in the selected lead set.
Those historical test counts must not be represented as a fresh full-suite run
on current source or as deployed runtime proof.

**Evidence and limits:** [bounded local reproduction](../2026-10-22-a05-bcrypt-local-check/README.md),
[remediation and regression results](../2026-10-22-a05-bcrypt-remediation/README.md),
and [current-source reconciliation](../2026-10-24-a05-source-refresh/README.md).
These linked records are internal supporting evidence and should be sanitized
and reviewed before public linking.
The work does not establish a practical takeover, production impact, existing
account recovery behavior, or a fully secure application. A05 remains partial;
no deployed current-source environment was available in the latest readiness
review.
