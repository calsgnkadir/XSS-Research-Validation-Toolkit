# R7 Kadrom source and release identity — 23 October 2026

## Verified identity

The authorized target is the owner's local Kadrom source repository,
`https://github.com/calsgnkadir/hotel-platform`, not its public frontend preview
or a production service. Public REST metadata observed at
`2026-10-22T21:01:10.8990736Z` (23 October Europe/Istanbul) reported:

| Field | Observed value |
|---|---|
| Repository | `calsgnkadir/hotel-platform` |
| Default branch / archived | `main` / `false` |
| Current source commit | `1276892bd62eab8838ce5a03b877c545cf67da3f` |
| Public releases / tags | 0 / 0 (first page capacity 100, empty arrays) |
| Backend source coordinate | `com.hotelapp:hotel-student-platform:0.0.1-SNAPSHOT` |
| Frontend source package | `hotel-student-web:0.1.0`, `private: true` |

The Maven version comes from `hotelapp/pom.xml:16-19`; frontend metadata from
`hotel-web/package.json:2-4`. These are source package versions, not evidence
of publication to Maven Central/npm or a released supported binary.
Git fetch observed `01d5857` with two frontend copy changes from `4c9473a`,
then the coordinator pushed `1276892`, which adds only the bounded multipart
regression test. Backend source, POM and resolved dependency tree are unchanged.

Sources: [public metadata](https://api.github.com/repos/calsgnkadir/hotel-platform),
[main branch](https://api.github.com/repos/calsgnkadir/hotel-platform/branches/main),
[releases](https://api.github.com/repos/calsgnkadir/hotel-platform/releases),
[tags](https://api.github.com/repos/calsgnkadir/hotel-platform/tags), and the
[immutable POM](https://github.com/calsgnkadir/hotel-platform/blob/4c9473a68e5378778bb6fdef525b488edba74a21/hotelapp/pom.xml).
Web-tool cache misses and the first sandbox REST connection failure were not
counted as negative search results. The ordinary approved REST retry supplied
the metadata above; a subsequent Git fetch confirmed the source commit.

## Support and deployment boundary

No tracked SECURITY/SUPPORT policy or release changelog was found in the
reviewed tree. The repository therefore does not establish a supported
semantic-version release or a formal support lifetime. The precise research
identity is the dated `main` source commit above. An untagged source snapshot
must not be called a vendor-supported release merely because it is current.
This resolves the identity for the user's authorized local-source research;
a deployed build is outside that scope and is not needed to identify this
source snapshot.

`README.md:58-72` describes the public URL as frontend-only and says the
backend is not live. This is a checked-in description, not a fresh production
probe. `docker-compose.yml:27` and `deploy/prod/docker-compose.prod.yml:39`
build the backend from local source. `hotelapp/Dockerfile` builds a JAR and
copies it into an image; no published application image digest was established.
No public preview, production endpoint, database or existing Docker volume
was accessed for this identity review.

## Baseline change and validation provenance

The previous remediation was delivered as `c3ce102`. Fetch then found newer
commits including product behavior changes, Boot 4 Flyway starter support,
Istanbul test timezone alignment and acceptance concurrency locking. The
source is not equivalent to the previous tested tree. The multipart
specialist preserved its test outside the target, then the clean target was
fast-forwarded through `d96b835` to `4c9473a`; the same test was restored
afterward. The earlier **665/665** result and **246-coordinate OSV snapshot**
remain historical evidence for their recorded source.

The coordinator generated a default-scope Maven dependency tree at `d96b835`;
it contained 248 distinct JAR coordinates, including Boot 4/Flyway modules.
An OSV `v1/querybatch` request returned 248 response rows and zero matched
coordinate rows at `2026-10-23T06:56:43.1698927Z`–`2026-10-23T06:56:44.1002895Z`.
At current source `1276892`, the generated dependency-tree output has the same
SHA-256 as the queried tree
(`d8ebcd896e982834d66d9d42ea7b1d22b687931da1194b9a47dd751147e7bca5`); both
extracted coordinate sets contain 248 entries and are identical. The current
POM's timezone-only test plugin adjustment did not change resolved coordinates.
Query provenance, coordinate-set hash, current POM/tree hashes and normalized
coordinate list are in [osv-query.json](osv-query.json), SHA-256
`79363622d20ea0afaE0278bac6c34a17139e224e8b0366d556b1766430dca6ed`.
This includes Maven's default test scope and is not a production dependency
graph or proof that the application has no vulnerabilities.

GitHub CI run [39852706081](https://github.com/calsgnkadir/hotel-platform/actions/runs/39852706081)
reported backend failure on `d96b835`; its public logs returned 403. Later
upstream added Europe/Istanbul timezone settings for UTC-midnight test
flakiness, and CI run [39861668186](https://github.com/calsgnkadir/hotel-platform/actions/runs/39861668186)
on `4c9473a` reported backend, frontend and E2E jobs successful. This sequence
is consistent with that timezone change addressing the earlier failure, but
the exact failing tests are unconfirmed because the `d96b835` log was
inaccessible. The coordinator's independent local `mvn verify` on `4c9473a`
with the multipart test is recorded in [VALIDATION](../../VALIDATION.md).
The later upstream commit `01d5857` changed two frontend copy strings; CI run
[39915595907](https://github.com/calsgnkadir/hotel-platform/actions/runs/39915595907)
also succeeded on that commit. The coordinator pushed the test as `1276892`;
CI run [39919982298](https://github.com/calsgnkadir/hotel-platform/actions/runs/39919982298)
completed successfully for the test commit. Local Maven `verify` on the
identical working tree with the multipart test is recorded in
[VALIDATION](../../VALIDATION.md).
Neither CI nor a local test establishes deployment.

## R7 disposition

The source identity and bounded advisory-search subtasks are complete with the
absence of a published supported release recorded. The appropriate current
recipient is the product owner in this authorized workspace, who requested
remediation; the [owner report](../../research/kadrom-local-triage.md) is the
internal handoff. R7's bounded local research disposition is complete: the
existing BCrypt issue was matched to its vendor advisory, remediated and
retested on the recorded source; the current graph query found no additional
known OSV matches. No new CVE is claimed. External disclosure, CVE assignment
and program acceptance are not inferred or performed. A05's malformed-parser
cleanup question remains separately open; normal multipart functionality
cannot close that question.
