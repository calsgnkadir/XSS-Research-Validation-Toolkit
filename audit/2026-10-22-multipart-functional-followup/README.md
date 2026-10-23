# A05 ordinary multipart functional follow-up

Actual run date: 2026-10-23 (Europe/Istanbul). Directory date follows the
coordinator's original task allocation. Native storage specialist:
`/root/multipart_controls`.

## Scope and source identity

The current user explicitly requested multipart testing. The earlier malformed
parser helper was automatically blocked before runtime; it was not executed,
repackaged or retried here. This is a separately scoped ordinary functional
regression using one tiny valid PNG upload, mocked external storage, and ordinary
file-validation controls. No parser-error, resource exhaustion or cleanup
acceptance follows from these checks.

The coordinator fast-forwarded the clean Kadrom checkout to
`d96b8359a4121437d45c1ae1a4926f4647f7b00e`. The only added target source is
`hotelapp/src/test/java/com/hotelapp/service/MultipartFunctionalControlsTest.java`.
Its SHA-256 is
`eb2fa62d9bb6a542f35087d80cdc1378f39d437110f58bb7b450f4e7b4667d8f`.
The test was temporarily moved into this audit directory before fast-forward;
matching before/after hashes were checked, then the same file was restored. No
duplicate draft or source overwrite remains.
The pre-fast-forward and failed-compile version had hash
`44d525b36afd8f6673d3ef79549709f8417b9a0743de248310b3533999403446`;
before final execution the fixture was improved to generate its 1x1 PNG with
Java ImageIO rather than trusting a base64 literal. The final hash above includes
that fixture-only change.

## Controls

- One small standards-valid multipart HTTP POST to an ephemeral `127.0.0.1`
  Tomcat connector. A diagnostic servlet calls `getPart`, passes the parsed bytes
  to the real `FileStorageService`, and returns its reference. The oracle requires
  HTTP 200, exact PNG bytes at the mocked provider, and matching image/reference
  options. This is not the product controller, auth chain or full application.
- Positive avatar and private message-image service paths require exact bytes,
  generated reference consistency, and public-image/private-raw options.
- Empty file, unsupported extension and mismatched ordinary image extension
  must throw `BusinessRuleException` before any Cloudinary interaction.

The test has six methods. All Cloudinary/Uploader objects are mocks; no provider
connection, database, application startup, scheduler, Docker container or old
volume is used. The servlet uses deliberately small test limits (1 KiB file,
4 KiB request, threshold zero); these are not production configuration evidence.
JUnit owns a new temporary directory; Tomcat stop/destroy runs in `finally`.
No temp-file cleanup observation is asserted.

## Execution record

Command from Kadrom `hotelapp/`:

```powershell
& 'C:\Users\user\.m2\wrapper\dists\apache-maven-3.9.16\56ba1f9f\bin\mvn.cmd' -o -ntp '-Dmaven.repo.local=C:\Users\user\.m2\repository' '-Dtest=MultipartFunctionalControlsTest' test
```

The first attempt on the previous `c3ce102` checkout was interrupted before tests
when the coordinator found four upstream commits. The next attempt on `d96b835`
failed during main compilation at 2026-10-23 00:04:40 +03:00: Maven reported a
fatal compiler error naming cached `spring-boot-jdbc-4.1.1.jar`; the launcher also
printed access denied. No test ran in either attempt. The cache file exists and
metadata was readable; the abbreviated error alone does not establish whether
the failure was file permissions or another compiler read problem. The
coordinator was notified for a normal runtime-permission review, independently
of the earlier blocked malformed-parser proposal.

The coordinator subsequently ran the same focused command through the ordinary
runtime approval gate. It completed **BUILD SUCCESS** at
`2026-10-23T00:09:57+03:00`: **6 tests, 0 failures, 0 errors, 0 skipped**.
Maven compiled 94 test sources. The final test hash above was verified before
the testCompile output. Tomcat reported **11.0.27**; the single ordinary loopback
multipart request satisfied the HTTP 200 and exact-byte/provider-options
assertions. The normalized result is [result.json](result.json).
This successful run supersedes the compilation failure for functional acceptance;
the earlier attempts remain non-results, not additional passing tests.

## Acceptance boundary

A05 ordinary functional coverage passed the six focused controls. The prior
parser-error cleanup criterion remains unverified.
No product vulnerability/safety, deployed artifact, proxy/WAF, or complete A05/R7
closure is established. The previous effective runtime preflight describes the
older Boot 3/Tomcat 10 diagnostic and is not current Tomcat 11 runtime evidence.

Shared ROADMAP/STATUS/VALIDATION and target application/POM files were not edited
by this specialist. No commit, push, deployment or external disclosure occurred.

## Coordinator final-source verification — 23 October

The same source file hash was restored after the target advanced to
`01d5857a1cb6068f1feb731dd5baa3e7b46f849f`; its only changes from `4c9473a`
were two frontend copy edits. Full local Maven `verify` on that source plus
this test completed **725 unit + 45 integration tests**, zero
failures/errors/skips, `BUILD SUCCESS` at `2026-10-23T10:29:45+03:00`. It
includes these six multipart controls. Test commit `1276892` was pushed to
Kadrom `main`; its CI run `39919982298` completed successfully with backend,
frontend and E2E jobs passing.
Structured run metadata is in
[current-source-verify.json](current-source-verify.json). GitHub Actions run
[39915595907](https://github.com/calsgnkadir/hotel-platform/actions/runs/39915595907)
also passed on `01d5857`; that run preceded this test commit. See the
current-source entry in
[VALIDATION](../../VALIDATION.md). The upstream `d96b835` failure and later
`4c9473a` success are separately documented in the CI review; no deployment
was performed.
