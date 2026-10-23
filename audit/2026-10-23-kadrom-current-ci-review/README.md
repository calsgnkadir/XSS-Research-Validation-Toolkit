# Kadrom current CI review — 23 October 2026

Native QA task `/root/r3_r6_acceptance`; coordinator-assigned read-only
follow-up. This concerns Kadrom, not the toolkit's accepted R3–R6 scope.
No target tests were run while the multipart specialist was using the target.
No code, shared planning documents, credentials, Git state or deployment was
changed. This audit is the only file created by this follow-up.

## Confirmed remote result

Public GitHub REST job/check-run responses bind
[CI run 39852706081](https://github.com/calsgnkadir/hotel-platform/actions/runs/39852706081)
to Kadrom HEAD `d96b8359a4121437d45c1ae1a4926f4647f7b00e`.

| Job | ID | Result |
|---|---|---|
| Backend (Spring Boot · mvn verify) | 120082807651 | Completed, failure |
| E2E (Playwright · actual MySQL + backend) | 120082807926 | Completed, success |
| Frontend (React · vitest + build) | 120082808093 | Completed, success |

Backend setup, checkout and JDK setup succeeded. The `Build & test` step
failed between `2026-10-22T20:53:32Z` and `20:55:02Z`. Current target
`.github/workflows/ci.yml:35`–`:36` runs `mvn -B -ntp verify` in `hotelapp`.
The public failure annotation states only **Process completed with exit code 1**.
This establishes build/verification failure, not its precise Maven phase,
test class, assertion, application cause or infrastructure cause.

The E2E job's backend jar build, backend start and Playwright steps succeeded.
Its conditional report/backend-log upload step was skipped. A skipped upload
does not make the job a failed test; conversely no downloaded E2E artifact
content was independently verified here. No individual E2E/frontend test
counts are asserted.

## Inspection limits and reproducible endpoints

The following public endpoints were read successfully:

- `/repos/calsgnkadir/hotel-platform/actions/runs/39852706081/jobs`
- `/repos/calsgnkadir/hotel-platform/actions/jobs/120082807651`
- `/repos/calsgnkadir/hotel-platform/check-runs/120082807651`
- `/repos/calsgnkadir/hotel-platform/check-runs/120082807651/annotations`

The check run has null summary/text and four annotations: the generic failure,
Node 20 deprecation warning, setup-java v4 deprecation warning and Ubuntu
runner image migration notice. The three notices/warnings do **not** establish
the failure's cause. Full public job-log download at
`/repos/calsgnkadir/hotel-platform/actions/jobs/120082807651/logs` returned
HTTP 403, `Must have admin rights to Repository`. No credential search or
authenticated retry was attempted. `gh` was unavailable in the escalated
shell; direct REST supplied the public metadata. The initial sandbox REST
network attempt failed; the explicitly escalated read-only requests succeeded.

Source inspection shows `d96b835` adds Boot 4's Flyway starter to the POM,
but no available log proves that change caused the CI failure. The previously
recorded 665-test local acceptance belongs to the earlier source associated
with `c3ce102`; it must not be presented as passing tests for `d96b835`.

## Next discriminating check

Once the concurrent multipart test finishes, the coordinator can run current
source `mvn verify` in the authorized local disposable test environment and
capture the actual failure summary. If it does not reproduce, authenticated
CI logs or a controlled rerun would be required to distinguish an environment
failure from a source defect. No speculative fix is proposed from public
metadata alone. Kadrom CI remains **failed, exact cause undetermined**.

## Coordinator local reproduction follow-up — 23 October

After the multipart specialist finished, the coordinator ran offline Maven
`verify` from `hotelapp/` at the same target HEAD `d96b835` with the added
`MultipartFunctionalControlsTest` source hash
`eb2fa62d9bb6a542f35087d80cdc1378f39d437110f58bb7b450f4e7b4667d8f`.
The captured summary reported **713 unit tests and 45 integration tests**, all
with zero failures, errors or skips; `BUILD SUCCESS`. This is a Windows/Java
17.0.18/Maven 3.9.16/H2 local reproduction, not the remote Ubuntu run.
Therefore the public CI failure did not reproduce locally, but its precise
cause remains unknown because the job log endpoint denied access. No cause is
assigned to the Flyway change or to the runner without that log.

## Later upstream CI and current-source verification — 23 October

Kadrom `main` then advanced to `4c9473a68e5378778bb6fdef525b488edba74a21`.
GitHub Actions run
[39861668186](https://github.com/calsgnkadir/hotel-platform/actions/runs/39861668186)
completed successfully for backend, frontend and E2E jobs. The Maven verify
was rerun locally at this source with the multipart test included: **725 unit
+ 45 integration tests, zero failures/errors/skips; BUILD SUCCESS**. The
upstream POM added `Europe/Istanbul` timezone settings for Surefire/Failsafe
between the two CI observations. That change is consistent with resolving the
earlier UTC-midnight test instability, but the `d96b835` failing test remains
unconfirmed because its public log was inaccessible. The `4c9473a` CI run did
not include the coordinator's uncommitted multipart test; the local run did.

GitHub Actions run
[39915595907](https://github.com/calsgnkadir/hotel-platform/actions/runs/39915595907)
subsequently completed successfully on `01d5857a1cb6068f1feb731dd5baa3e7b46f849f`
at `2026-10-23T07:23:11Z`; it also preceded the multipart test commit.

## Test commit CI — 23 October

After the coordinator pushed commit
`1276892bd62eab8838ce5a03b877c545cf67da3f`, GitHub Actions run
[39919982298](https://github.com/calsgnkadir/hotel-platform/actions/runs/39919982298)
started on that exact SHA. At `2026-10-23T07:55:59Z`, backend `mvn verify`
(job `120302595295`), frontend (job `120302595294`) and E2E
(job `120302595013`) had all completed successfully. This remote result is
separate from the local Windows Maven verification.
