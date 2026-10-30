# Doğrulama kaydı — 2026-10-24

## 30 October — PyPI 0.2.1 documentation maintenance

### R8 receiver follow-up — later local source delivery

Windows / Python 3.10.11. Final independent regression baseline: 23 failed,
20 passed. Fixed selected five-file suite: 146 passed, no failure/error/skip.
Two owner-supplied source scopes were statically rescanned against unchanged
233/47 file hashes: 22->12 candidates (five append and five router false alarms)
and 129->129; no added candidate. One known vendor-directory skip remains.
No application, HTTP or browser ran. No PyPI runtime update or hosted CI claim.
[Source hashes, commands and limits](audit/2026-10-30-r8-receiver-fix/README.md).

### Later source-only owned-project comparison

Installed PyPI 0.2.1 dxa scanned two owner-authorized local source scopes;
reports remain ignored/private. No target application or HTTP/browser test ran.
Python 3.10.11 coordinator source-only synthetic scans produced 16 observations;
12 assertions verified baseline coverage/false-positive behavior, including
existing deficiencies. Installed dxa bytes match checkout SHA-256
`2561203de267961cc3e247aa3708b29bca82f903d6a0e4fdb1ccb68e9ec6b718`.
No scanner fix, pytest pass count or app-safety claim is made.
[Public method and limits](audit/2026-10-30-owned-source-baseline/README.md).

### Earlier packaging acceptance

Windows / Python 3.10.11, new ignored `.dxa/pypi-refresh-021` venv.
`python -m build --outdir .dxa/pypi-refresh-021-dist` succeeded;
`python -m twine check .dxa/pypi-refresh-021-dist/*` passed 2/2.
Local wheel install and production-PyPI reinstall passed. `dxa`, `dxadyn`,
`dxaprove`, `dxa-sarif --help` passed 4/4. All 11 wheel module bytes match
current source. Production PyPI JSON confirms 0.2.1, exact UTF-8 description,
and matching wheel/sdist SHA-256. No browser/toolkit suite was rerun.
K01 article cites dated existing evidence; CVE review is documentation analysis.
[Acceptance and hashes](audit/2026-10-30-pypi-portfolio/result.json).

## C01–C09 writeup reconciliation, A05 freeze, K04 artifact search — 24 October

Documentation-only changes aligned writeups 01–09 with their historical
evidence banners and the current K03/K04 records. C03 labels UNION and blind
material as theory; C05 distinguishes the historical basket-ID account from a
later two-synthetic-account horizontal BOLA replay, and states that vertical
escalation was not tested. C01/C02/C04/C06–C09 further scope execution,
negative observations, operator-supplied URL hints, raw JSON, sanitizer-name
heuristics, and HIGH/precision claims. Raw reports were not edited.

A05 is explicitly frozen as partial: its malformed multipart cleanup fixture
passed 1/1, but the separate current-source app runtime did not reach health or
auth because host-to-MySQL loopback connectivity failed. No new runtime request
or test was made for this documentation change; no app/auth/deployment result
is claimed.

K04 artifact-name/content search covered this workspace and reachable
`OneDrive\Desktop`, `Documents`, and `Downloads` project/artifact locations.
No matching historical route/source/image was located. Docker image listing
could not connect because the Docker engine named pipe was absent; this is not
evidence that no local image exists. No historical retest ran.

No toolkit tests were run. No raw reports, Docker resources, application data,
or external targets were changed or contacted.

## K03 independent local lab retest — 24 October

Windows local Docker, existing OWASP Juice Shop `20.2.0` immutable image ID
`sha256:0cec496d878c6855a1c81694c9f91564082f418b84aece87538adb8850d2437e`;
network internal-only, new unique container, no pull/published port/mount,
`http://127.0.0.1:3000` loopback target. A different QA/security agent ran the
capture script: 17 HTTP requests, process exit 0. SQLi-shaped login mapped to
admin identity; unsigned `alg:none` token mapped to admin; modified-signature
`whoami` returned HTTP 200 without identity; synthetic A read B's basket (200),
anonymous read returned 401. New container/network were stopped and removed;
old Juice Shop container/network remained unchanged. Raw private capture stays
in ignored `.dxa` and is not included here.

This is a new training-lab replay, not validation of historical writeup sessions,
a toolkit vulnerability, or a new CVE. Source hashes, sanitized results and
limits: [K03 audit](audit/2026-10-24-k03-independent-retest/README.md).

## K04 pinned-source testability review — 24 October

Juice Shop `20.2.0` source inspection: the challenge-enabled `saveLoginIp.js`
branch checks an exact active iframe value before the sanitizer; the normal
branch uses `sanitizeSecure` and recursive `sanitize-html`. The writeup's
nested-tag regex is a separate `sanitizeLegacy` helper not used by this route.
No faithful inert oracle was found, so no HTTP/browser retest ran. A temporary
unstarted container and internal network used only for source copying were
removed; no application process or request ran. The historical bypass and
fix/retest remain unverified. [K04 audit](audit/2026-10-24-k04-independent-retest/README.md).

## A05 authorized environment availability — read-only

Authorized Kadrom checkout `.dxa/a04-kadrom-source` is `eb031a1`. Docker
metadata inspection only: A05 app/DB containers are `Created` or `Exited`; no
running application built from the reviewed commit was identified. The local
JAR predates `eb031a1`. Development and production-shaped Compose files exist,
including Caddy, but no active app/proxy/WAF runtime was identified. No request,
authentication, container start/stop, volume inspection, source read of
credentials, or test was performed. Existing A04/A05 volumes were left intact.
This means source and embedded-fixture review are available, while deployment,
authenticated-runtime, effective proxy/WAF, production graph, and stress claims
have no current suitable environment. A future isolated local stack needs a
fresh synthetic database volume; it would not establish production behavior.
[Environment review](audit/2026-10-24-a05-authorized-environment/README.md).

## A05 current-source isolated runtime — inconclusive

Source `eb031a19f9f6b0715d8b302751542f631216cdd5`; 280 copied `src/main`
files and POM matched the authorized checkout. Offline Maven package completed
with exit 0 / `BUILD SUCCESS` and tests skipped in ignored `.dxa` staging. New
JAR SHA-256 `505df33126a2b7c65c9427da9b3679b95646d84db53ac5bf64ad02ff8b6353f7`;
existing source `target/` JAR remained unchanged.

Only a newly named MySQL 8.0 container/network/volume was created; the network
was internal, port binding was `127.0.0.1:13307`, image pull disabled. DB became
healthy, but host TCP to `127.0.0.1:13307` was false. The test-profile app
exited at Flyway connection before binding `127.0.0.1:18081`. No health,
registration, login, or 72/73-byte requests were sent. The app was not tested.
Only the new DB container was stopped; its new volume/network remain for
inspection. Existing A04/A05 containers/volumes and old JAR were untouched.
Outcome: **inconclusive environment connectivity**, not a pass/fail security
result. [Risk plan and evidence](audit/2026-10-24-a05-isolated-runtime/README.md).

## A05 current-source dependency reconciliation — source-only

Kadrom `main` `eb031a19f9f6b0715d8b302751542f631216cdd5`, fetched and equal to
`origin/main`. `hotelapp/pom.xml` SHA-256 is
`f757453d4066791a0b58409133dd9a3d22a6c932b4ad3a7caa3a51b8aa1678b2`, unchanged
from the recorded source review. Maven 3.9.16 ran the dependency tree offline;
no tests ran. The generated 16,881-byte tree SHA-256
`d8ebcd896e982834d6d9d42ea7b1d22b687931da1194b9a47dd751147e7bca5` matches the
saved tree behind the 23 October OSV query (248 coordinates, 248 response rows,
zero matched rows). The query was not repeated because its exact tree hash is
unchanged. This supports the selected dependency disposition for current source;
it does not prove a production graph or absence of vulnerabilities.

From `.dxa/a04-kadrom-source/hotelapp/`:

```powershell
<Maven 3.9.16 executable> -o -ntp -Dmaven.repo.local=<local Maven repository> -DoutputFile=target/a05-refresh-dependency-tree.txt -DoutputType=text dependency:tree
```

See the [A05 current-source reconciliation](audit/2026-10-24-a05-source-refresh/README.md)
for source-path diff scope and advisory-by-advisory disposition. The existing
[malformed multipart test](audit/2026-10-24-a05-multipart-cleanup/README.md)
is separate; it was not rerun during this source-only review.

## A05 multipart parser-error cleanup — bounded local retest

Kadrom checkout `eb031a19f9f6b0715d8b302751542f631216cdd5`, clean after a
fast-forward from `0ea07ed`. One local untracked test fixture was added under
`src/test`; no Kadrom application source/POM was modified. Windows 11, Java
17.0.18, Maven 3.9.16 offline, Spring 7.0.9, embedded Tomcat 11.0.27. The first
sandboxed compiler run failed while reading cached `spring-boot-jdbc` before
tests; the elevated retry compiled. Two initial fixture setup errors were
corrected before the final parser run. They did not reach the HTTP test and are
not counted as parser outcomes.

From the local `hotelapp/` directory:

```powershell
mvn -o -ntp -Dmaven.repo.local=<local Maven repository> -Dtest=MultipartParserCleanupTest test
```

Final result: **1 test, 0 failures, 0 errors, 0 skipped; BUILD SUCCESS**. A
well-formed one-part control parsed into exactly one 4-byte temp file before
required-part binding raised `MissingServletRequestPartException`; the file was
gone after the response. One truncated boundary then raised Spring
`MultipartException` with Tomcat `IOFileUploadException` and
`MalformedStreamException` causes before handler selection. The spool remained
empty at exception, after response, and after one health GET (200). Mock message
and storage services had zero interactions. The test tears down Tomcat and uses
a fresh JUnit temporary directory.

This verifies one bounded parser/cleanup path for the current embedded
Tomcat/Spring resolver. It is not a full app/auth/deployment or proxy test, a
stress/large-upload test, a general parser guarantee or a CVE/vulnerability
finding. See the [sanitized evidence and source](audit/2026-10-24-a05-multipart-cleanup/README.md).

## E05 textarea parser-context acceptance — 24 October 2026

Source base `532be7ac01e82fbe0612749ead6d3cb39f0be7e9` plus the scoped E05
changes. Windows / Python 3.10.11 / pytest 9.1.1; elevated coordinator execution
after specialist WindowsApps Python launch denial. Before production changes,
the new unit/transport file failed 6/6 (including three missing-registry-key
failures). The independent native Chromium oracle then returned **1 failed,
5 passed**, reproducing zero marker elements in the raw textarea positive.

After the change, with `DXA_REQUIRE_BROWSER=1`:

```powershell
py -3.10 -m pytest tools/dom-xss-analyzer/test_e05_context.py bench/test_e05_context_coverage.py tools/dom-xss-analyzer/test_dxadyn.py tools/dom-xss-analyzer/test_http_evidence.py tools/dom-xss-analyzer/test_json_transport.py tools/dom-xss-analyzer/test_blind_journal.py tools/dom-xss-analyzer/test_r1_contract.py tools/dom-xss-analyzer/test_sarif.py -q -p no:cacheprovider --tb=short --junitxml=.dxa/e05-acceptance.xml
```

**381 passed, zero failures/errors/skips**, 43.01s. This includes six independent
browser cases: all 950 legacy generated attempts remain marker-inert inside
textarea; the targeted new raw probe creates one marker outside textarea;
escaped/default/title/old textarea-opening controls produce none. Browser page
JavaScript was disabled. This measures parser placement, not execution or
vulnerability. HTTP evidence remains reflection. No full-suite run or new
hosted success is inferred. [Evidence, source hashes and limits](audit/2026-10-24-e05-context/README.md).

Current wheel built with `pip wheel --no-deps --no-build-isolation`, installed
with `--no-index --no-deps` into a new local venv. The installed CLI gate passed
**9 controls**, with all 11 source/wheel/installed module hashes matching.
Wheel SHA-256 `a7c3e89fd9257d6c4b3d1129822d5dd435c58279b812f3092ea65fc42d5a35d8`.
The published release asset was not replaced. Exact packaging commands and
sanitized gate output are in the E05 evidence package.

Delivery commit `77199075a271227bce7cb6386d571f34f0213b5d` was pushed; a
subsequent fetch verified local HEAD equals origin/main. For that exact SHA,
[CI 40083275086](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/40083275086)
completed all three jobs successfully. Hosted job logs show main suite
**887 passed / 62 skipped** (98.64s), required negatives **94 passed** (23.68s),
benchmark tests **522 passed** (16.26s), installed gate **9 controls passed**;
required authenticated-browser acceptance **224 passed** (104.62s), followed
by successful strict corpus, auth controls, demo and zero-skip evidence gate.
[K01 Linux 40083275084](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/40083275084)
also completed successfully. These are hosted metadata/log observations, not
local reruns or independent downloaded-artifact review. Skips are not passes.

## E02 hosted CI metadata follow-up — 24 October 2026

Source commit `532be7ac01e82fbe0612749ead6d3cb39f0be7e9`. The GitHub
`fetch_workflow_run_jobs` tool was used to recheck the latest-attempt jobs
for runs `39955815522`, `39955815291`, and `39954873774`.

For [CI 39955815522](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/39955815522),
the analyzer job `120421256070`, required authenticated-browser job
`120421256089`, and optional dxadom browser job `120421256218` all returned
`status=completed`, `conclusion=success`; each returned step also reported
success. The analyzer steps include the installed-wheel gate, main suite,
required negative controls, self-scan, benchmark tests and strict smoke run.
The required browser steps include R3 acceptance, R4 execution/auth controls,
proof demo, and the complete-evidence gate.

For [K01 Linux 39955815291](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/39955815291),
job `120421255038` and its returned steps were completed/success, including
the clean proof and independent artifact gate. The formerly pending required
browser job `120418093477` in fix-commit
[CI 39954873774](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/39954873774)
also returned completed/success, as did that run's other two jobs.

This was a read-only metadata check. No local test suite was rerun, no new test
counts were collected, and no hosted artifacts were downloaded or independently
reviewed. The prior recorded counts below remain tied to their original runs.
Initial combined Git fetch calls failed to write `.git/FETCH_HEAD`, including
an elevated retry; a later standalone elevated `git fetch origin` succeeded
and the local/upstream comparison was `0/0`. Separately, the coordinator checked GitHub's
`/repos/calsgnkadir/XSS-Research-Validation-Toolkit/branches/main` API and
observed the same full `532be7a` SHA as local HEAD. This establishes the
then-observed remote-main equality through the API as well.
[Reconciliation scope](audit/2026-10-24-status-reconciliation/README.md).

## E02 SARIF — 23 October 2026

Base `f0f42868fd05b1d7b5ba3a0228cf464b04fd5320` plus the E02 working tree.
Windows / Python 3.10.11 / pytest 9.1.1; coordinator-approved elevated Python
execution after sandbox WindowsApps access denial. Command:

```powershell
py -3.10 audit/2026-10-23-e02-sarif/run_validation.py
```

Nine selected test files: **468 passed, 0 failures/errors/skips** (55.11s pytest).
Includes 116 SARIF schema/semantic/CLI cases and existing static, shared R1,
HTTP, R2, config and packaging regressions. A prior focused run had 115 passed
and one test-helper KeyError; QA fixed it before this successful combined run.
No full browser suite was run. The runner then built a wheel without build
isolation, installed without dependencies into a fresh temporary venv, and
ran `bench/check_installed_cli.py` outside the source tree: **9 controls passed**,
all 11 packaged module hashes matched source and wheel. Synthetic saved-input
SARIF conversion and existing loopback fixture only; no external scan.

[Result and source hashes](audit/2026-10-23-e02-sarif/result.json),
[scope and oracle review](audit/2026-10-23-e02-sarif/README.md).
Wheel SHA-256 `adf7543c9bb7170924ed9c9bf8226622168dd789ab56b259b1e2c8fde99e729e`.
The local test wheel is not a replacement for the published release artifact.
Hosted CI is tracked separately; no hosted success is inferred from local tests.

Delivery commit `119d7acd837072b1b5f95549780f78e36682dd0b` was pushed and
verified equal to `origin/main` after fetch. Its
[K01 Linux run 39952400880](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/39952400880)
completed successfully. General CI run `39952400914` passed required proof and
optional browser jobs but failed the main analyzer job: **880 passed, 62
skipped, 1 failed**. The sole failure was the vendored schema byte digest:
Windows working bytes were original CRLF (`ad6db4...`), while Git normalized
the stored blob to LF (`2b19d2358baef0251d7d24e208d05ffabf1b2a3ab5e1b3a816066fc57fd4a7e8`).
The installed Linux gate had already passed 9 controls before that failure.
A narrow `.gitattributes -text` rule preserves the original schema bytes for
the follow-up. No downloaded-artifact review is claimed.

Follow-up: original schema bytes re-staged with `i/crlf w/crlf attr/-text`;
raw working file and staged blob Git object IDs both
`534d35da2b8450502d9256a6c699dfe40f5b1ed5`. Focused unchanged SARIF suite
rerun with `py -3.10 -m pytest tools/dom-xss-analyzer/test_sarif.py -q -p no:cacheprovider --tb=short`:
**116 passed**, zero failures/errors/skips, 27.46s. Existing runtime source
and the original strict schema digest are unchanged. Hosted follow-up pending.

Fix commit `9769a20002c81270b17d1ec192a9b2fa4e33bfc2` was pushed and verified
equal to origin/main after fetch. Follow-up general CI run `39954873774` main
job succeeded: **881 passed / 62 skipped** (97.52s), required negative controls
**94 passed**, benchmark tests **522 passed**, installed wheel **9 controls
passed**. Self-scan and strict benchmark smoke steps also succeeded. K01 Linux
run `39954873803` and optional browser job succeeded; required authenticated
browser job was still running at that 23 October check. Its later success is
recorded in the 24 October metadata follow-up above. Skips are not passing tests.

## Kadrom current source `b374095` plus A04/A05 regressions — 23 October 2026

The local Kadrom checkout was at `b374095344f7b871bbadc4eef571760fd380f9ab`
with three scoped working-tree changes: invalid Sort error handling, its three
MockMvc controls, and a synthetic same-role candidate ownership HTTP regression
for the three work-session read routes. Changed handler SHA-256 is
`4BC51C81D0DE86F623A881449A50B9DF81326D684D48B399266C612B6E179710`;
the Sort and A04 test hashes are
`7F0F9BC0DB8E126C280A8BABB8E9EA36855AB1D613785E222585D2941B870443` and
`49C32834F444FA7635B00187286A49B314D6A49AB42BC1A0183275FA61B6405D`.

Command from `.dxa/a04-kadrom-source/hotelapp/`:

```powershell
& 'C:\Users\user\.m2\wrapper\dists\apache-maven-3.9.16\56ba1f9f\bin\mvn.cmd' -o -ntp '-Dmaven.repo.local=C:\Users\user\.m2\repository' verify
```

Windows, Java 17.0.18, Maven 3.9.16 offline, in-memory H2 `test` profile.
Result: **739 unit + 45 integration tests, 0 failures, 0 errors, 0 skipped;
BUILD SUCCESS**. The three Sort controls passed 3/3 and the A04 ownership HTTP
regression passed 1/1. This verifies the reviewed source checkout and local
changes, not a pushed source commit. Malformed multipart parser-error cleanup
was not tested; the user's reserved test remains separate. Full log:
`.dxa/a04-kadrom-source/hotelapp/target/2026-10-23-b374-a04-a05-verify.log`.

The verified changes were committed and pushed as `0ea07ed77c9d2edfc8a3e4394d3ab3700ca69de0`.
After fetch, local HEAD and `origin/main` matched that full hash. GitHub Actions
run [39928860888](https://github.com/calsgnkadir/hotel-platform/actions/runs/39928860888)
completed successfully for the exact commit. This remote CI result is distinct
from the local Maven run above.

## Kadrom upstream source `b374095` remote CI — 23 October 2026

After the locally verified/test-committed source `1276892`, Kadrom `main`
advanced through four upstream commits to `b374095344f7b871bbadc4eef571760fd380f9ab`.
The backend changes include per-candidate locking for no-show updates and
per-record transactions for scheduled work. GitHub Actions run
[39925048373](https://github.com/calsgnkadir/hotel-platform/actions/runs/39925048373)
completed successfully for that exact source. No local Maven verification has
been run on `b374095` at the time that upstream CI was reviewed; the subsequent
local Maven verification for `b374095` plus regression changes is recorded
above. The earlier 770/770 result belongs to `1276892`. The resolved dependency
POM did not change in the upstream commits or the `0ea07ed` regression commit.

## Kadrom current main with multipart test commit — 23 October 2026

The target advanced while this work was in progress. Source HEAD at final
verification used source tree committed as `1276892bd62eab8838ce5a03b877c545cf67da3f`.
Its parent `01d5857a1cb6068f1feb731dd5baa3e7b46f849f` had two frontend copy
edits after `4c9473a`; backend tests and POM were unchanged. Upstream backend changes
include Istanbul test timezone setup and acceptance concurrency safeguards.
The focused multipart
test remained byte-identical at SHA-256
`eb2fa62d9bb6a542f35087d80cdc1378f39d437110f58bb7b450f4e7b4667d8f`.

Command from `hotelapp/`:

```powershell
& 'C:\Users\user\.m2\wrapper\dists\apache-maven-3.9.16\56ba1f9f\bin\mvn.cmd' -o -ntp '-Dmaven.repo.local=C:\Users\user\.m2\repository' verify
```

Windows, Java 17.0.18, Maven 3.9.16, in-memory H2 `test` profile. Result:
**725 unit + 45 integration tests, 0 failures, 0 errors, 0 skipped; BUILD
SUCCESS**, completed `2026-10-23T10:29:45+03:00` after 6 minutes 40 seconds.
It includes all six
`MultipartFunctionalControlsTest` methods. The ordinary small PNG request was
accepted by ephemeral Tomcat 11.0.27; external storage was mocked. Malformed
parser errors and temp-file cleanup remain untested. Run metadata and
test-source hash are in [current-source-verify.json](audit/2026-10-22-multipart-functional-followup/current-source-verify.json).

GitHub Actions run [39861668186](https://github.com/calsgnkadir/hotel-platform/actions/runs/39861668186)
for the backend-equivalent `4c9473a` completed with backend `mvn verify`,
frontend and E2E jobs all successful. Run
[39915595907](https://github.com/calsgnkadir/hotel-platform/actions/runs/39915595907)
completed successfully for the exact two-copy-change `01d5857` source, before
the multipart test commit. After pushing `1276892`, Actions run
[39919982298](https://github.com/calsgnkadir/hotel-platform/actions/runs/39919982298)
completed successfully on test commit `1276892`; backend, frontend and E2E
jobs all passed at `2026-10-23T07:55:59Z`. The earlier `d96b835`
backend failure has public log access 403;
the intervening timezone commit is consistent with resolving UTC-midnight test
flakiness, but the exact failing test is unconfirmed. This current remote run
is independent of the Windows local result. Neither is a deployment.

## Kadrom intermediate `d96b835` verification and multipart — 23 October 2026 (superseded)

Source HEAD: `.dxa/a04-kadrom-source` commit
`d96b8359a4121437d45c1ae1a4926f4647f7b00e` (fast-forward from `c3ce102`).
The upstream update adds the Boot 4 Flyway starter and subsequent product
changes; earlier 665/665 results do not describe this source. The current
uncommitted coordinator regression is
`hotelapp/src/test/java/com/hotelapp/service/MultipartFunctionalControlsTest.java`,
SHA-256 `eb2fa62d9bb6a542f35087d80cdc1378f39d437110f58bb7b450f4e7b4667d8f`.

Focused ordinary multipart command from `hotelapp/`:

```powershell
& 'C:\Users\user\.m2\wrapper\dists\apache-maven-3.9.16\56ba1f9f\bin\mvn.cmd' -o -ntp '-Dmaven.repo.local=C:\Users\user\.m2\repository' '-Dtest=MultipartFunctionalControlsTest' test
```

Result: **6 tests, 0 failures, 0 errors, 0 skipped; BUILD SUCCESS**. One valid
1x1 PNG request returned HTTP 200 through ephemeral loopback Tomcat 11.0.27 to
a diagnostic servlet; real storage-service paths and rejection controls used
mocked Cloudinary. No product auth/controller chain, production limits,
malformed input, parser cleanup, database, external provider or Docker was
tested. Details and structured result:
[multipart audit](audit/2026-10-22-multipart-functional-followup/README.md).

Afterward the coordinator ran local Maven `verify` on the same source plus the
same test file:

```powershell
& 'C:\Users\user\.m2\wrapper\dists\apache-maven-3.9.16\56ba1f9f\bin\mvn.cmd' -o -ntp '-Dmaven.repo.local=C:\Users\user\.m2\repository' verify
```

Result: **713 unit + 45 integration tests, 0 failures/errors/skips; BUILD
SUCCESS**, Windows, Java 17.0.18, Maven 3.9.16, test profile H2. GitHub CI run
39852706081 on this HEAD reported backend failure, frontend/E2E success; the
public log request returned 403. Local `verify` did not reproduce the remote
failure, whose cause remains unknown. The test output summary was captured at
`.dxa/a04-kadrom-source/hotelapp/target/r7-current-verify.log` (ignored local
build output, not shared). See [remote CI review](audit/2026-10-23-kadrom-current-ci-review/README.md).

## Kadrom final Boot 4 / BCrypt / A04 full suite — 2026-10-22

Pinned target baseline: `.dxa/a04-kadrom-source`, commit
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`, Windows, Java 17.0.18, Maven
3.9.16, in-memory H2 `test` profile. The final POM resolves Spring Boot
4.1.1/Security 7.1.1, Resilience4j Boot 4 module 2.4.0 with AspectJ starter,
H2 2.3.232 test-only, Jackson 2.21.8/3.1.8, Tomcat 11.0.27, POI 5.4.0 and
HttpClient 4.5.14. The POM and 40 other changed/new source files are listed in
the [source-hash manifest](audit/2026-10-22-a05-bcrypt-remediation/source-hashes.json).

Command, run from `hotelapp/`:

```powershell
& 'C:\Users\user\.m2\wrapper\dists\apache-maven-3.9.16\56ba1f9f\bin\mvn.cmd' -ntp '-Dmaven.repo.local=C:\Users\user\.m2\repository' test
```

Result: **665 tests, 0 failures, 0 errors, 0 skipped; BUILD SUCCESS**. Maven
compiled all 247 main source files and 91 test source files. Earlier in this
same review, the full suite ran with Boot-managed H2 2.4.240 and reported 665
tests with six errors, all from H2's known generated `CHECK`/enum connection
regression. The project now pins H2 2.3.232 only for test scope; rerunning the
full suite cleared all six errors. See upstream H2
[issue #4320](https://github.com/h2database/h2database/issues/4320) and
[issue #4302](https://github.com/h2database/h2database/issues/4302). This
workaround does not change the production database.

After adding the Boot 4-specific Resilience4j module and AspectJ starter, a
selected compatibility/auth/A04/POI/email run also passed **63/63**; the final
665-test run supersedes it for overall local suite status. `git diff --check`
passed in the target checkout.

The final Maven tree had 246 distinct JAR coordinates. OSV `v1/querybatch`
returned 246 response rows and 0 matched coordinates at
`2026-10-22T13:26:35Z`; this is a known-record snapshot, not evidence that no
vulnerability exists or that the graph matches a deployed release. Details and
the dependency disposition are in
[the A05 dependency audit](audit/2026-10-22-a05-dependency-refresh/README.md).

No full Docker/runtime/deployment test, CI result, production-account check or
multipart request is claimed. The user reserved multipart testing for a later
session. After this suite, target commit `6be6a07` was merged with the
upstream-only Vite change and pushed as `c3ce102`; the 41-file tested tree is
unchanged by that merge. It remains undeployed.

## Kadrom BCrypt follow-up — exact-72 change-password — 2026-10-22

Pinned Kadrom source baseline: `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`;
checkout `.dxa/a04-kadrom-source`, Windows, Java 17.0.18, Maven 3.9.16,
H2 test profile. A follow-up added a positive service regression for changing
from and to passwords each exactly 72 UTF-8 bytes, with multibyte characters.
It checks existing-password match, new hash save, and refresh-token revocation.

```powershell
mvn -ntp -Dmaven.repo.local=C:/Users/user/.m2/repository '-Dtest=InputPolicyTest,AuthServiceTest,AuthServiceLoginLimitTest,PasswordResetServiceTest,BcryptPasswordHttpTest' test
```

Result: **37 passed, 0 failures, 0 errors, 0 skipped**; all 91 test sources
compiled. `git diff --check` passed. The earlier 51-test combined run also
covered A04 and passed before this test-only addition; it was not rerun on the
new source hash. No Docker, multipart, full product suite, CI, commit, or target
push is claimed. Updated source-hash manifest and limits are in the linked
remediation audit. A04's doc-only acceptance cross-check did not rerun tests.

## Kadrom A05 BCrypt remediation ve A04 regresyon retesti — 2026-10-22

Ürün checkout'u `.dxa/a04-kadrom-source`, branch `main`, baseline source commit
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. Bu kayıttaki değişiklikler yerel
uncommitted çalışma ağacında test edildi; upstream target `main` bir commit daha
ileride ve yalnız `hotel-web/vite.config.js` farkı olduğu görülmüştü. O fark
birleştirilmedi. Güncel remediation ayrıntısı:
[audit/2026-10-22-a05-bcrypt-remediation](audit/2026-10-22-a05-bcrypt-remediation/README.md).

Host: Windows, Java 17, Maven 3.9.16, test DB: Spring `test` profili H2 in-memory.
Dependency baseline: Spring Boot `4.1.1`, springdoc `3.1.1`; resolved Spring
Security config/oauth2-client/oauth2-jose/core/test/crypto/web modules `7.1.1`.
Boot 4 test module/import and Tomcat 11 fixture compatibility edits are included.
Focused command:

```powershell
mvn -ntp -Dmaven.repo.local=C:\Users\user\.m2\repository -Dtest=InputPolicyTest,AuthServiceTest,AuthServiceLoginLimitTest,PasswordResetServiceTest,BcryptPasswordHttpTest,CheckInServiceTest test
```

Result reported by the specialist: **51 tests passed, 0 failures, 0 errors,
0 skipped**; all 91 test sources compiled. HTTP MockMvc confirmed a synthetic
73-byte login is rejected with `400` before auth; unit oracles cover ASCII,
2/4-byte UTF-8 boundaries, supported encoder max-length behavior and controls.
`git diff --check` passed. No full Kadrom suite, Docker, production account,
migration or CI run is claimed. A04's additional `CheckInServiceTest` was run
before the Boot 4 migration (15 passed) and again in the final combined
selector (15 passed).

The test confirms selected remediation code and boundary behavior only. It does
not prove deployment, existing-account inventory/recovery completion, or broad
R7/A05 closure. Multipart was not tested by coordinator or specialists.

## R7/A05 offline UTF-8 assay and blocked multipart task — 2026-10-22

Toolkit baseline `6167fa8361fd9f02b1a9e859152117639c855540`; product source
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c` remained read-only. Host Java/javac
21.0.11, compiled `--release 17`, cached packaged Crypto 6.2.4. Crypto JAR
SHA-256 `5a36c1f29d11f0b9ce4b7c54886bd909499eadb0b19be507b6b3992830af23b6`;
parent app JAR identity matches the preceding runtime audit.

New direct-library assay: exactly 9 BCrypt calls (4 encode, 5 matches). Three
different Unicode pairs had equal first72 UTF-8 bytes and lengths 73/74/75
bytes versus 72/72/73 UTF-16 units; all different-suffix matches returned true.
The extracted packaged PasswordPolicy admitted both inputs in each pair.
Exactly72-byte control: correct true, first-byte substitution false. Independent
shape/control assertions passed; no error/timeout/skip in the successful run.
No new application context/account/endpoint, Docker lifecycle or network request
ran. Per-pair original/negative controls, below72-byte samples and normalization
were not tested; these are not application suite results.

Exact Java SHA-256 `9ac1efa55f5b642aaaf959c0cb5a4c27e1f15c3d5e5e4cf7a8c2380a488410ca`;
allowlisted JSON SHA-256 `c2b63515a1fe3b8b9bba90d499a46351ed0ccb992c045897f82b1080a6eddc3d`.
Initial Python process launch was denied before execution; explicit escalated
retry completed the offline assay. Coordinator independently checked artifact
hashes, manifest6.2.4, source/JSON oracles and operation accounting without rerun.
Exact commands, source, hashes and control limits: [Unicode audit](audit/2026-10-22-a05-bcrypt-utf8/README.md).

Multipart helper compilation succeeded, but automated possible-cybersecurity-risk
flag stopped its specialist before application/runtime traffic. A bookkeeping-only
follow-up also hit the flag; no blocked test retry was made. Read-only proposed
resource name filters returned no containers/networks/volumes. No multipart test,
cleanup observation or passing outcome is claimed. [Blocked-state record](audit/2026-10-22-a05-multipart-bounded/README.md).
No full toolkit/product suite or fresh CI result was run/inspected in this
continuation. The R7 report is document production, not a new endpoint retest.

## R7/A05 local diagnostic controls — 2026-10-22

Toolkit baseline `2bf3b8e`; selected Kadrom source
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. Cached backend image
`sha256:773ffd3a73373b974b80fab06897640a4c65bde044f9a246e22834853d2065a5`,
app JAR SHA-256 `e564ab781100246897733a9367cd64ef76251a6d77272d73243c0174154ff608`.
Packaged Spring Boot 3.2.5/MVC 6.1.6/Tomcat 10.1.20/Micrometer 1.12.5.
Host javac 21.0.11 compiled exact published diagnostic sources with `--release 17`;
PropertiesLauncher invoked the packaged application through those helpers.
Base/dev/prod YAML bytes match pinned source; full build attestation/original
entrypoint/production equivalence was not reproduced.

- Preflight helper SHA-256
  `69d0e37715ef76d6c51627f0322e8353025241f7e9c645549bfed16d7ccc3030`:
  actual observation filter registration, one ordinary health GET 200 and timer
  absent→1; effective MultipartConfigElement limits 20971520/26214400 bytes,
  threshold 0, blank location, writable servlet temp dir. Dedicated part-count
  getters absent; generic DataSize JSON and missing isEnabled accessor are not
  numeric/disabled evidence. No upload or parser-error cleanup test.
- Method helper SHA-256
  `b919641be52041775bbc1b7232532b4b5cb751248960aa3a681b3b1ae2086d7e`:
  exactly GET health 200→bodyless A05CHECK 400→GET health 200. Rejection timer
  method=UNKNOWN/count1; GET timer 1→1→2. No raw A05CHECK method tag observed.
  This bounded path did not reproduce raw-method retention or DoS; no broad
  safety, production or entire-advisory conclusion follows.

Each successful run used a fresh internal network/new MySQL volume and no host
port publishing. Both backend/MySQL pairs stopped (143/0), volumes retained;
old data was not mounted. An initial Windows path-length setup error occurred
before either first-attempt container started; those unused resources remain.
QA independently checked hashes, actual Docker metadata and output oracles.
Package-local `.gitattributes` preserves Java/JSON bytes so recorded artifact
hashes survive Git checkout newline settings; coordinator checks index/raw
blob identity before commit.
No toolkit/Kadrom test suite or fresh CI result is claimed. Exact code, selected
commands, JSON evidence, launch differences and failure limits:
[preflight](audit/2026-10-22-a05-runtime-preflight/README.md),
[method check](audit/2026-10-22-a05-micrometer-method-check/README.md),
[QA](audit/2026-10-22-a05-runtime-qa/README.md).

## R6 güncel kaynak wheel kabulü — 2026-10-21

Test edilen toolkit commit'i `6928fd6ffd8557a311b06b2b22f33fd6a2ac0b71`,
Windows 10.0.26200 / Python 3.10.11, pytest 9.1.1. Yerel paket build'i:

```powershell
py -3.10 -m pip wheel --no-deps --no-build-isolation --wheel-dir <temp> .
```

Çıkış 0; `dxa-research-toolkit 0.1.0` wheel SHA-256
`ffab49944876bca0b5362dd22c5a220aec62a09fbe962a390fcb16064c80ad91`. Wheel
çevrimdışı yeni venv'e kuruldu ve `bench/check_installed_cli.py` installed-wheel
gate'i 7/7 geçti. `test_dxadyn.py`, `test_dxadyn_report_identity.py` ve
`test_dxadyn_config.py`: **271 passed, 0 failed/error/skip** (24.87 s). Dokuz
paket modülünün source/wheel/install hashleri eşleşti; güncellenmiş `dxadyn.py`
hash'i `6864971fbf0bd152bcbffef2a98c6fb783f8397447fabaa8f36c8876c31e509e`.
Bu odaklı yerel koşudur; tam analyzer suite yeniden koşulmadı. Ayrıntılı gate
çıktısı ve sınırlar [R6 revalidation audit'inde](audit/2026-10-21-r6-current-source/README.md).

Bu commit'in hosted genel CI [39615470595](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/39615470595)
ve K01 Linux [39615470859](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/39615470859)
işleri başarılı; bunlar yerel testlerden ayrı workflow sonuçlarıdır.

GitHub Release'e eklenecek son wheel, README'nin dağıtım kanalını açıklaması
sonrasında yeniden üretildi: SHA-256
`111a0f6c43c3d6710c9c30434fb402604cec9fa5ee69845a44b6d14023195399`, 104,949
byte. Yeni çevrimdışı venv kurulumunda installed-wheel gate tekrar **7/7**
geçti; final artifact JSON'u ve wheel rebuild ayrıntısı aynı R6 audit'indedir.
Bu paket yeniden üretiminde uygulama modülleri değişmedi; 271 odaklı testin
kaydı yukarıdaki aynı kaynak kodu içindir.

## R6 GitHub Release — 2026-10-21

Annotated tag `v0.1.0` targets commit
`d7d1bd666ae4fe5643bf0574658d8d8a0f4411a0`. The [GitHub Release](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/releases/tag/v0.1.0)
was published with one wheel asset. The public release API reported 104,949
bytes and SHA-256
`111a0f6c43c3d6710c9c30434fb402604cec9fa5ee69845a44b6d14023195399`, matching
the locally gated artifact. Hosted general CI
[39650964831](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/39650964831)
and K01 Linux
[39650964757](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/39650964757)
completed successfully for the tagged source commit. PyPI publication was
explicitly excluded. Full publication details are in the
[R6 release audit](audit/2026-10-21-r6-release/README.md).

## K03 local reproduction, 2026-10-19

Local-only lab: OWASP Juice Shop **20.2.0**, Docker image
`sha256:0cec496d878c6855a1c81694c9f91564082f418b84aece87538adb8850d2437e`.
The request run used a Docker `--internal` network, no mounted volumes and
synthetic disposable users. Its raw request/response file contains their
passwords and JWTs and stays under ignored `.dxa/`; SHA-256
`f8858b7340f7bf4443ab94a2baa7494c43be9c241ab9aee3c0f7083c1e7d274f`. The
shareable, secret-free summary and handler source hashes are in the
[K03 audit](audit/2026-10-19-k03-loopback-reproduction/README.md).

Observed: invalid login 401; the SQLi login shape 200 and current-user identity
matched the local admin. `alg:none` also returned admin identity; a modified
signature returned no identity. Two distinct accounts were independently
identified; A read A's basket and B's seeded basket using the same A session,
including the product B added. Anonymous access to B's basket returned 401.
This is new behavior on the specified image, not reproduction of the old
writeup session, CVE attribution, or a remediation retest. No local analyzer
suite ran for this lab/document pass. Push commits `c58c74b` and `2650ede`
triggered hosted workflows; both commits' four jobs passed, including analyzer,
required authenticated browser proof, K01 Linux and opt-in browser harness.
Job results and remote commit hashes are in [STATUS](STATUS.md).

## Son teslimlerin bağımsız incelemesi — 2026-10-17

Test edilen kaynak `451361b9f8faef3f328b13468d8d3f6a040c7d2c`, Windows /
Python 3.10.11. Yeni analyzer koşusu **789 passed, 38 skipped, 0 failed**;
38 skip'in tamamı otomatik Chromium keşfi olmayan DOM testleri. Açık Chrome
155.0.8059.82 ve required-browser ayarıyla yeni birleşik koşu **298 passed,
0 skipped, 0 failed**: tam DOM 80 ve gerekli R3/R4 seçimi 218. Bunlar aynı
testleri kısmen yeniden içerir; sayıları toplanmaz. Komutlar, JUnit ve skip
gerekçeleri [inceleme paketinde](audit/2026-10-17-delivery-review/README.md).
Aynı kaynakta CI workflow'undaki 10 dosyalı benchmark/kabul matrisi yeniden
**520 passed, 0 skipped, 0 failed** verdi (91.74 saniye); JUnit saklandı.
Ortam ayrıca sorgulandı: Python 3.10.11, Playwright 1.63.0, pytest 9.1.1.

Son HEAD'in genel CI `38984494777` üç job'ı ve K01 Linux `38984494765`
doğrudan sorgulandı: success. Bu tur indirilen R3/R4 artifact'i mevcut
checker'dan geçti: 218 sıfır-skip test, corpus 17/17, TP8/FP0/FN0 ve
JSON/Markdown provenance eşleşmesi. İndirilen K01 paketinde 22 sıfır-skip
JUnit testi, 12 proof hash'i, üç kaynak ve gate hash'i eşleşti; beş kontrol
sonucu uyumlu. Uzak port cleanup yalnız CI'nin kaydettiği sonuçtur.
Önceki bölümlerdeki 'artifact indirilmedi' ifadeleri o tarihli incelemenin
sınırıdır; bu yeni inceleme yalnız son HEAD'in belirtilen iki paketini kapsar.

## Final source commit retest and P02/P03 — 2026-10-17

The final code/evidence source commit `3ef8499bc56827614602540d962eb4ab0ea9bdca`
was retested locally on Windows/Python 3.10.11. The full analyzer suite passed
**789**, skipped **38**, failed **0**. The selected 10-file benchmark/CI
acceptance matrix passed **520/520**. `bench/ci_self_scan.py` succeeded; the
strict three-target mock smoke was TP=2/FP=0/FN=0; required 11-file R3/R4
Chrome acceptance passed **218/218**; strict proof suite TP=8/FP=0/FN=0;
auth controls TP=1; installed `dxaprove --demo` returned
`execution-observed`; K01 fixture/gate tests passed **22/22**; fresh K01 local
profile passed **5/5 controls** and closed **5/5 fixture ports**; full Chrome
`test_dxadom.py` passed **80/80**. Results are separate suite measurements and
must not be added together or interpreted as real-world scanner accuracy.

The local `bench/check_ci_acceptance.py` rejected the locally generated proof
artifacts because its provenance contract requires Linux/Python 3.12 while
this run was Windows/Python 3.10.11. This local artifact gate is therefore
not recorded as passed. Hosted general CI
[run 38982247229](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38982247229)
passed all three jobs and K01 Linux
[run 38982247201](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38982247201)
passed; artifacts were not downloaded or independently inspected.

P02/P03 changed only README and writeup index wording/grouping. `git diff
--check` and relative-link review passed; runtime behavior did not change.
The detailed matrix and scope are in the [retest audit](audit/2026-10-17-final-commit-retest/README.md).

## Portfolio/evidence closeout — 2026-10-17, local Windows

The C/K evidence review updated historical claims and report labels without
rerunning historical targets. The report renderer and its regression test
changed; the coordinator ran the full analyzer suite against the combined
working tree:

```powershell
py -3.10 -m pytest tools/dom-xss-analyzer -q -p no:cacheprovider --tb=short
```

Result: **789 passed, 38 skipped, 0 failed** in 186.48 seconds, Windows,
Python 3.10.11. For commit `362d4d610430ae4111cfdf662559efacb695edc2`, hosted
general CI [run 38981902539](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38981902539)
passed all three jobs, including analyzer tests and authenticated browser proof.
K01 Linux [run 38981902461](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38981902461)
also succeeded. These are workflow/job outcomes; artifacts were not downloaded
or independently inspected.

P04 was reproduced from a fresh `.venv-p04-20261017` environment. The package
and `.[browser]` extra installed, Playwright 1.63.0 installed Chromium
153.0.8010.12, and installed `dxaprove --demo` returned
`execution-observed` with triage `unreviewed` on its loopback fixture. The
installed demo result SHA-256 is
`DF066619B35E364D9B7E93CF9F8A94E699F83C9F62E2BCCE2A7D84F9794A02D9`.
The installed K01 local profile passed **5/5 controls** and closed **5/5
distinct fixture ports**. Its acceptance SHA-256 is
`698BAF306A41DB68F7EA979D2319BBD219FFFAAFD780F972FE5EF619F3E5EBF9`.
See the [P01/P04 audit](audit/2026-10-17-p01-p04/README.md) for the retained
JSON files and detailed scope.

## Latest R9 delivery — 2026-10-17, local Windows and hosted jobs

Commit `3a386eefbfa61e494f1bcb2ae6dadcf4d1c4bf7f` was pushed to `origin/main`
and the remote ref hash matched. General CI
[run 38977151511](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38977151511)
passed all three jobs; K01 Linux
[run 38977151588](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38977151588)
passed. These are workflow/job outcomes; no artifact was independently
downloaded in this follow-up.

The commit contains two test-fixture fixes: direct-eval browser proof serves
from a literal-loopback HTTP fixture, and the stored-auto report matrix mock
supplies the probe's full metadata contract. On Windows/Python 3.10.11, the
11-file required Chrome suite passed **218/218**, and the full analyzer suite
passed **788**, skipped **38**, failed **0** in 183.55 seconds. Quiet pytest
output did not include skip names/reasons.

## Prior `221baa5` CI run — 2026-10-17

Commit `221baa5621fc26a8eb581b4d88410b2e0a66e77b` general CI
`38974413648` completed with opt-in Playwright harness success, but
`dom-xss-analyzer tests` and required authenticated browser proof failed.
K01 Linux `38974413706` succeeded. Hosted job logs returned HTTP 403 and were
not independently retrieved; no exact hosted failure cause or artifact content
is claimed.

Two test-only fixes were made after that run. The direct-eval browser proof now
serves its synthetic page from a disposable literal-loopback HTTP server,
consistent with the browser scope; the `stored-auto` report matrix mock now
supplies the metadata returned by the real probe. With both fixes, the exact
11-file required Chrome acceptance suite passed **218/218**, zero failures,
errors or skips (Windows, Python 3.10.11, Chrome 155.0.8059.82,
Playwright 1.63.0). The full `tools/dom-xss-analyzer` suite then passed
**788**, skipped **38**, failed **0** in 183.55 seconds (Windows/Python 3.10.11).
The quiet full-suite output did not identify skip names/reasons. These two
test-only changes were absent from `221baa5`; they were later delivered and
validated by hosted CI `38977151511` above.

## R9 DOM fixture recheck — 2026-10-17, local Windows

Base checkout: `dcd019d93e852cf26f3d562b0fd5f35f2435e7d0`; Python 3.10.11,
Chrome 155.0.8059.82, Playwright 1.63.0. A/B tests reproduced serial fixture
server failures for prompt (5/5) and `document.write` (5/5); corresponding
threaded dialog fixture prompt trials passed 5/5. All local HTTP fixture
servers in `test_dxadom.py` now use `ThreadingHTTPServer`; teardown shuts down,
closes, joins, and asserts each server thread exited. Test oracle and browser
scope are unchanged. This is a test-fixture concurrency fix; `dxadom.py` did
not change.

The historical failure/scope selection passed **14/14** (66 deselected, 58.68
seconds). The full Chrome suite passed **80/80**, zero failures/skips, in 91.29
seconds:

```powershell
$env:DXA_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
$env:DXA_REQUIRE_BROWSER='1'
py -3.10 -m pytest tools/dom-xss-analyzer/test_dxadom.py -q -p no:cacheprovider --tb=short
```

Updated `test_dxadom.py` SHA-256:
`A53E3E6A1C8273336F9E1A82D3575A3C041B5613786B8C76CD407889398A3879`.
This local working-tree result is based on `dcd019d`; it is not yet committed
and has no hosted CI result. See the [R6/R9 audit](audit/2026-10-16-r6-r9-final-source/README.md).

## R4/R5 closeout recheck — 2026-10-16, local Windows

Source checkout: `f1fb6556b930d683b7b47fd0c6b04d6f8703053b`; Python 3.10.11.
The coordinator reran the final R4 replay/oracle tests after the R4 specialist
confirmed the replay sources and test files still match the 16 October audit:

```powershell
py -3.10 -m pytest bench/test_r4_compare_local.py bench/test_r4_cid_oracle.py -q -p no:cacheprovider --tb=short
```

Result: **57 passed**, zero failures/errors/skips, 20.79 seconds. The suite uses
the local replay fixtures; it is not a new scanner comparison or a general
accuracy measurement.

The R5 specialist checked the K01 source/gate hashes against the final
acceptance and reran its local fixture/gate regressions:

```powershell
py -3.10 -m pytest cases/k01-stored-comment/test_fixture.py cases/k01-stored-comment/test_repro_gate.py -q -p no:cacheprovider --tb=short
```

Result: **22 passed**, zero failures/errors/skips. This Windows test run does
not establish a second human run or replace the historical Linux artifact
provenance. No hosted CI was run for this documentation/recheck turn.

## R6 current-source CLI/package readiness — 2026-10-16 (initial 0.0.0.dev0 run)

The R6 specialist reproduced duplicate JSON keys being accepted by the static
CLI config loader, added a regression, and changed the loader to reject the
ambiguous config before source discovery. The coordinator reran the focused
suite on Python 3.10.11:

```powershell
py -3.10 -m pytest tools/dom-xss-analyzer/test_dxa_config.py tools/dom-xss-analyzer/test_r6_cli_modes.py tools/dom-xss-analyzer/test_dxadyn_config.py tools/dom-xss-analyzer/test_dxadyn_report_identity.py -q -p no:cacheprovider --tb=short
```

Result: **110 passed**, zero failures/errors/skips. A current working-tree wheel
was then installed offline into a fresh Windows venv; installed CLI gate passed
**7/7**, and all nine module hashes matched source, wheel and installed copies.
Wheel SHA-256: `0edea5d639183f2088739241ec9b985cb7a39f0b43e33cc73a1ec8494675a07f`.
This packaging script run is not pytest, browser proof or hosted CI. Its base
HEAD and source-snapshot limits, the initial `bdist_wheel` failure, and the
cached `wheel==0.48.0` install into system Python are recorded in the
[R6 readiness audit](audit/2026-10-16-r6-final-readiness/README.md). No release
tag or publication was made in this initial run; the later selected `0.1.0`
candidate and final wheel check are recorded below.

## R6 final 0.1.0 wheel and R9 local continuation — 2026-10-16

The final R9 working-tree sources were built into the selected `0.1.0` wheel,
installed offline into a fresh temporary Windows/Python 3.10.11 venv, and
checked from outside the repository. The installed-wheel gate passed **7/7**;
all nine packaged module hashes matched source, wheel, and installation. Wheel
SHA-256: `d1151704ba4c5e6dbe91696f632040ad528947bf97b04dc765b585ef6c3729ad`.
The packaged `dxaprove --demo` returned `execution-observed` on its built-in
single-origin loopback fixture; triage remains `unreviewed`, so this is not a
vulnerability confirmation. The wheel recheck used Playwright 1.63.0 and
Chrome 155.0.8059.82 from the preinstalled environment; no package download
occurred. Full hashes and limits:
[final-source audit](audit/2026-10-16-r6-r9-final-source/README.md).

R9 coordinator reruns on local Windows/Python 3.10.11:

```powershell
py -3.10 -m pytest tools/dom-xss-analyzer/test_dxadyn.py -q -p no:cacheprovider --tb=short
py -3.10 -m pytest tools/dom-xss-analyzer/test_dxa_callback.py tools/dom-xss-analyzer/test_callback_boundaries.py tools/dom-xss-analyzer/test_blind_journal.py -q -p no:cacheprovider --tb=short
py -3.10 -m pytest bench/test_target_compose_safety.py bench/test_ci_self_scan.py bench/test_ci_acceptance.py -q -p no:cacheprovider --tb=short
$env:DXA_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'; $env:DXA_REQUIRE_BROWSER='1'; py -3.10 -m pytest tools/dom-xss-analyzer/test_dxadom.py -q -p no:cacheprovider --tb=short
```

Results: dynamic **182 passed** after the context matrix change; the combined
`test_dxadyn.py` + `test_http_evidence.py` set passed **194/194**. The context
tests retain `html-reflection` / `reflection` evidence and do not claim execution.
The malformed `dxadyn --header` warning no longer echoes supplied values.
Credential-labeled literals in `dxa.py --json` and terminal source snippets are
masked at presentation time; common `--json-out` omits source and retains its
fingerprint. `test_dxa.py` + `test_dxa2dyn.py` passed **58/58**, including
parameter-hint compatibility. Arbitrary free text and custom credential field
names are outside the masking guarantee.
Callback/journal **103 passed** (the narrower
callback boundary suite independently passed **82**), CI/compose **133 passed**,
report privacy **23 passed**, and the five targeted DOM redirect/WebSocket plus
historical dialog/XHR regressions **5 passed**. Callback evidence uses loopback
and temporary/in-memory SQLite, not a production reverse proxy or external
network. The complete DOM suite did not produce a clean run: three earlier
attempts were **77/80**, **79/80**, and **78/80**. A further isolated full suite
passed **70/80** in 270.63 seconds: 10 failures included page-error/sink/dialog
observations and two `goto` 15-second timeouts; most corresponding fixture
servers reported `ConnectionAbortedError`. The two latest previously failing
tests (`test_dialog_prompt_captured`, `test_mixed_page_captures_both_runtime_and_static`)
passed together **2/2** focused. Keep the full-suite gate open while route and
session lifecycle are investigated. The first
dynamic full-suite attempt also had a jitter-bound failure under concurrent
test load; its isolated rerun passed before the context-matrix change. No hosted CI was run for this
dirty working-tree snapshot, and the earlier R6/R8 CI records do not apply to
these R9 edits. Full evidence and source hashes are linked above.

The tested source snapshot was delivered as commit
`f4d8bdf50dcdd8fc93814e9d10adcab650a30d5a`; `origin/main` was queried and
returned the exact same hash. Hosted GitHub Actions for that commit:

- [General CI run `38923418347`](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38923418347): opt-in `dxadom` Playwright harness **success**;
  `dom-xss-analyzer tests` **failure**; required authenticated browser proof
  **failure**.
- [K01 Linux run `38923418259`](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38923418259): **success**.

These are job-level results only. The failed job logs and uploaded artifacts
were not independently retrieved, so their specific failure causes and proof
contents remain unverified. This hosted CI result does not replace the local
test counts above.

## R6 0.1.0 release-candidate gate and R8 current review — 2026-10-16

The installed-wheel gate was strengthened after review found that it checked
module bytes and launchers but not wheel distribution identity/version or the
exact three console-script mappings. Synthetic-wheel regressions cover valid
metadata and rejection of wrong name, missing/wrong script targets and duplicate
dist-info metadata. The focused R6 metadata/config and R8 static suites ran on
Windows / Python 3.10.11:

```powershell
py -3.10 -m pytest bench/test_check_installed_cli.py tools/dom-xss-analyzer/test_r8_sanitizer.py tools/dom-xss-analyzer/test_static_context.py tools/dom-xss-analyzer/test_dxa_config.py tools/dom-xss-analyzer/test_r6_cli_modes.py tools/dom-xss-analyzer/test_dxadyn_config.py tools/dom-xss-analyzer/test_dxadyn_report_identity.py -q -p no:cacheprovider --tb=short
```

Result: **156 passed**, zero failures/errors/skips (R8 subset 41). The selected
`0.1.0` wheel was rebuilt, installed offline in a fresh temporary venv, and the
full installed CLI gate passed **7/7**; all nine module hashes matched source,
wheel and installation. Wheel SHA-256:
`bde6f6cdba1190f2bee30e5b02499f7a4717a943a503e1686e1f73680535aba9` (rebuilt
again after the R8 AST pilot; updated module hashes are in acceptance.json).
The JSON acceptance is [here](audit/2026-10-16-r6-final-readiness/acceptance.json).
This is local Windows evidence. Commit `401e6bf6848a95986ba26eccd51127600712a4b3`
was pushed and its remote hash verified. General CI
[38894634586](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38894634586)
and K01 Linux
[38894634507](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38894634507)
completed successfully. These are workflow/job results; artifact contents were
not independently downloaded. The wheel is not tagged or published.

R8 then implemented the planned Python-only AST pilot. The two-case corpus
first failed on a tuple-unpack positive and quoted-source negative; final
TP/FP/FN/TN was **1/0/0/1**. An intermediate integration run exposed context
and cross-file regressions, which were fixed before the final focused
**95/95** and combined R6/R8 **210/210** runs. This closes the bounded R8
roadmap criteria only; general soundness and broader accuracy are not claimed.
See [R8 review](audit/2026-10-16-r8-current-review/README.md).

R8 commit `ab91b092f5a02af24149c48869083898e223b238` was pushed and its remote
ref hash matched. General CI
[38898993545](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38898993545)
passed all three jobs; K01 Linux
[38898993396](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38898993396)
also passed. These are workflow results; artifact contents were not
independently downloaded. No release tag or package publication occurred.

## 16 October final R4/R5 technical closeout

After coordinator review, R4 replay summaries require a clean escaped control
for every matched candidate, block non-fixture HTTP requests and disable service
workers. WebSocket and other non-HTTP traffic is outside this replay's sandbox.
Chrome-required command:

```powershell
$env:DXA_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
py -3.10 -m pytest bench/test_r4_compare_local.py bench/test_r4_cid_oracle.py -q -p no:cacheprovider --tb=short
```

Result: **57 passed, zero failure/error/skip**. Updated live replay command
and source/output hashes are in
[the R4 experiment audit](audit/r4-proof-experiment-2026-10-16/README.md).
It read 8 historical scanner rows and replayed 6 exact stored candidates; two
Dalfox raw payloads produced dialogs in the raw fixture and none in the
escaped fixture. Other candidates remain inconclusive. This was not a fresh
scanner run or original-session browser observation. The replay HTTP guard is
not a general network sandbox; WebSocket and other non-HTTP channels remain in
R9 scope. A dedicated WebSocket negative-control attempt timed out and was not
accepted as a pass.

R5 fresh Windows venv run: **5/5 browser controls**, **5/5 distinct ports
closed**, zero hash mismatches across the 12 proof members, 3 case sources
and gate. Environment: Python 3.10.11, Playwright 1.63.0, Chrome 155.0.8059.82.
The prior downloaded Linux artifact gate is on a different commit; current
push workflow status is recorded separately.

Commit `01a89e38e78182c1c7e81f2b1df021b66b429154` push was verified by remote
ref hash. General CI `38887832797` completed successfully with all three jobs;
K01 workflow `38887832998` also succeeded. Artifact contents for this commit
were not downloaded. R4/R5 scope and boundaries are recorded in ROADMAP.

## 16 October R4/R5 closure review at `d9db15b`

Native Engine ran `py -3.10 -m pytest bench/test_r4_compare_local.py
bench/test_r4_cid_oracle.py -q -p no:cacheprovider --tb=short` on Windows with
installed Chrome: **48 passed, zero failed/error/skipped**. These are focused
fixture and oracle regressions, not a fresh scanner comparison. The prior
8/8 scanner manifest's stored strings were inspected; none satisfied the
exact-CID JavaScript proof contract. See
[R4 review](audit/r4-closure-2026-10-16/README.md).

Native QA recomputed 16 hashes in the existing R5 local proof acceptance
package; all matched current bytes. No new R5 browser run, pytest run or hosted
CI was performed in this review. The independent human repeat remains open.
See [R5 review](audit/r5-closure-2026-10-16/README.md). The prior results below
retain their original commit and scope. Git delivery is tracked separately.

## 16 October local R4/R5 resume in the OneDrive copy

Commit `157a4387a1c60fd4520c25cb5477ec266518835f` was pushed to
origin/main and the remote ref hash verified equal. GitHub Actions
[general CI 38806623338](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38806623338)
completed successfully: required authenticated browser proof, main analyzer
tests (including the R4 gate), and opt-in browser harness all passed.
[K01 Linux 38806623393](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38806623393)
also completed successfully. This is workflow/job status, not downloaded
artifact-content verification or an independent human repeat. The final code
SHA is the commit above; this status follow-up is documentation.

After Git metadata restoration, the R4 specialist found three further red
counterexamples (credential angle-value bypass and v3 Dalfox report alias);
the focused gate suite passed **132/132** after fixes. Coordinator reran the
eight-module Chrome-required command from the R4 audit against the final
source. First run: **371 passed, 1 failed**, a Windows loopback
`ConnectionAbortedError [WinError 10053]` in the fixture deadline test.
That isolated test passed **1/1**. Repeated full run: **372 passed, zero
failure/error/skip**, 51.68 seconds. The earlier 368 result below applies
to the previous source revision. Remote CI was checked afterward, as recorded
above.

R4 `review-acceptance.json` binds the final gate files to SHA-256 and base
`df967d5`; both audit packages now preserve proof bytes under scoped
`.gitattributes` rules. Final commit/push status is recorded in STATUS.

At test time the active copy had no `.git`; tested source bytes are bound by SHA-256
manifests in [R4 acceptance](audit/r4-local-acceptance-resume/acceptance.json)
and [R5 validation](audit/r5-local-closure-resume/validation.json). Previous
Git base was `df967d5`, but no commit identity is claimed for this delivery.

R4 command and runtime are in [R4 audit](audit/r4-local-acceptance-resume/README.md).
Windows Python 3.10 with installed Chrome and `DXA_REQUIRE_BROWSER=1`:
**368 passed, 0 failure/error/skip**. Four new counterexamples first failed
on the imported v3 gate, then passed after correction. Historical run-02
validation returned selected/completed **8/8**, hashes, sessions and request
traces verified. This is prior artifact validation, not a fresh scanner run
or candidate browser execution. The run-01 hash mismatch was preserved.

R5 command and runtime are in [R5 audit](audit/r5-local-closure-resume/README.md).
Windows Python 3.10.11, Playwright 1.63.0 and Chrome 155.0.8059.79:
live K01 gate **5/5** controls and **5/5** distinct fixture ports closed;
focused pytest **22 passed, 0 failure/error/skip**. No fresh venv was made.
The independent second-person repeat is open-deferred. The two suite counts
are reported separately. Neither is overall R4/R5 acceptance. No new remote
CI result exists for this local delivery.

## 16 October R4 separate scanner sessions and coordinator triage

On the local Windows/Python 3.10.11 worktree based on remote `1850836`, the
coordinator reran `bench/test_r4_cid_oracle.py`: **27 passed**, zero
failures/errors/skips. The integrated auth/fixture/comparator command
`py -3.10 -m pytest bench/test_r4_scanner_sessions.py bench/test_r4_comparison_fixture.py bench/test_r4_compare_local.py -q -p no:cacheprovider --tb=short`
also passed **30 tests**, zero failures/errors/skips.

The loopback candidate comparison selected/completed **8/8**, with zero
errors/timeouts/incomplete; all pre/post role checks and four cross-role
controls passed. The coordinator recomputed the run manifest and every
referenced log/report hash; all matched, and shared artifacts contained no
session-token pattern. Scanner payloads did not carry the oracle's exact-CID
JavaScript proof contract, so execution and TP/FP/FN remain inconclusive. The
general R4 comparison gate remains open.
[Run evidence](audit/2026-10-16-r4-separate-scanner-auth/README.md),
[coordinator triage](audit/2026-10-16-r4-review/README.md).

Final combined rerun including both suites:
`py -3.10 -m pytest bench/test_r4_cid_oracle.py bench/test_r4_scanner_sessions.py bench/test_r4_comparison_fixture.py bench/test_r4_compare_local.py -q -p no:cacheprovider --tb=short`
resulted in **57 passed**, zero failures/errors/skips. The 27- and 30-test
focused runs overlap and must not be added to the combined count.

These are local results against the worktree based on `1850836`; no hosted CI result
is claimed by this local-result statement.

Code commit `ca83bf2` was pushed to `origin/main`; remote CI run `38795736800`
completed successfully with all 3 jobs, including the required browser proof
job. K01 Linux run `38795736790` also succeeded but is not independent-human
R5 evidence. This records workflow status; no downloaded artifact-content
acceptance is claimed here.

## R6 installed wheel CI gate

Coordinator rebuilt a wheel and installed it offline into a fresh Python
3.10.11 Windows venv. Seven installed CLI/config checks passed outside source;
all nine module hashes matched source and wheel. A changed wheel was rejected
before producing success evidence. These are script checks, not new pytest
cases. No browser execution is claimed by this new check.
[Command and results](audit/2026-10-15-r6-installed-ci/README.md).
Commit `db1167a` hosted CI `38790053904` üç job başarıyla tamamlandı. Remote
wheel gate 7/7; required browser gate 186 test, 0 skip/error, corpus17/17
TP8 FP0 FN0. Artifact digest/logları kaydedildi; R6 ZIP içeriği ayrıca yerelde
açılıp yeniden çalıştırılmadı.

## R4 equal-budget candidate comparison follow-up

Final integrated local regression: **207 passed**, zero failure/error/skip;
independent checker subset **72 passed**. Run-02 artifact validation selected
8, completed 8, error/timeout/incomplete/skipped 0, equal client timeouts true,
candidate-only true, ranking false. Browser fixture cases are included in the
integrated run. Counts overlap; they are not added together.
[Live run and limits](audit/2026-10-15-r4-comparator-execution/README.md),
[independent artifact check](audit/r4-comparison-acceptance/README.md).

## 15 October R4 candidate comparison follow-up

Pinned Dalfox 3.2.4 and dxadyn were attempted on the bounded loopback stored
fixture: 8 selected = 4 completed, 0 errors, 4 timeouts. Dalfox generated 28
attempts per run (20 forwarded plus eight 429 rejections) and exceeded the
budget; all four runs timed out. Source review confirmed dxadyn exit 1 means
candidate findings, so its two raw runs were completed candidate scans, not
errors or execution proof. The final combined comparator/accounting/browser
tests passed 9/9; the CI gate unit module passed within the 119-test suite.
This is inconclusive, not an accuracy score or tool ranking. R4 competitor
acceptance remains open.
[Run record](audit/2026-10-15-r4-admin-comparison/candidate-comparison/README.md).
Fix commit `ddb0ecf` remote CI run 38748348608 passed all 3 jobs. Required browser
gate accepted 185 tests with zero skips/errors, corpus17/17 TP8/FP0/FN0, and the
R4 fixture/browser module. Artifact SHA256 was
`3e4ffc1698f564d3fc845d99d0c854c328dc17656f247f1854d8430120bdb79c`.
K01 workflow 38748348674 succeeded but is not a human R5 repeat.
[Remote record](audit/2026-10-15-r4-admin-comparison/candidate-comparison/remote-ci.json).

## 15 October R4 admin fixture and R6 readiness

R4 separate-account loopback fixture/browser oracle: specialist 3 passed and
coordinator rerun 3 passed, no failures/errors/skips. Comparator unavailable
locally, so no equal-budget run. R6 config/report/help suite: 109 passed, no
failure/error/skip. Fresh installed 0.0.0.dev0 wheel passed all three CLI help
checks, config behavior, package metadata/docs and loopback demo. Demo triage is
unreviewed. [Combined record](audit/2026-10-15-r4-r6-followup/README.md),
[R4](audit/2026-10-15-r4-admin-comparison/acceptance.json),
[R6](audit/2026-10-15-r6-release-matrix/acceptance-final.json).
Commit 7d78f77 general CI 38710720264 passed 3/3; downloaded artifact gate accepted 182 zero-skip/error tests, corpus17/17 TP8/FP0/FN0, auth6/6 and all 3 new admin fixture tests. R5 human repeat was deferred and remains open; no release tag.


## 15 October resumed corpus/config acceptance

Coordinator Windows/Python 3.10.11 integration: **503 passed**, zero
failure/error/skip. Native Engine required Chrome suite: **254 passed**;
separate strict corpus **17/17, TP8 FP0 FN0**, zero incomplete outcomes.
Native Report focused config/report/modes: **101 passed**; fresh wheel/venv
installed CLI smoke **6/6**. Installed dxadyn hash matches tested source.
Counts overlap, not summed. R5 human handoff was reviewed only; automated
K01 regression in integration is not a second-human reproduction.
[Commands, JUnit and source hashes](audit/2026-10-15-resumed-delivery/README.md),
[R4](audit/2026-10-15-r4-broader-corpus/acceptance.json),
[R6](audit/2026-10-15-r6-config-release/validation.json).
Code 0261baa remote CI 38706882024 all 3 jobs success; downloaded artifact
accepted 179 tests with zero skip/error, corpus17/17 TP8/FP0/FN0, auth6/6.
K01 Linux 38706882018 success: artifact22 tests/proof5/5; digest and source/member
hashes matched. Exact remote records are in the resumed-delivery audit.
No release tag, second-human acceptance or external target test.


## 15 Ekim R4/R5/R6 devam kabulü

Başlangıç `8dd50acb80ed41bb2e44d4f1ab9defa9f1deca09`, Windows/Python 3.10.11.
R4 uzman gate/scorer/identity paketi 233; R5 uzman fixture/gate paketi 22 geçti.
Koordinatör R4/R5 birleşik paket 231 ve R6 etkilenen paket 304 geçti;
paketler örtüşür, toplam benzersiz test sayısı olarak toplanmaz.
Tüm bu koşularda sıfır hata/atlama. R5 yeni gerçek yerel CLI 5/5 kontrol ve
beş ayrı kapalı fixture portu: ikinci insan/fresh venv kabulü değil.
R6 rapor matrisi mock CLI testi; Docker tekrarına ihtiyaç olmadı.
Komutlar, hashler ve kapsam: [devam kabulü](audit/2026-10-15-r4-r5-r6-continuation/README.md),
[R4](audit/2026-10-15-r4-acceptance/README.md), [R5](audit/2026-10-15-r5-handoff/README.md).
Kod 9b6b7c3: genel CI 38640435614 3/3 başarılı; indirilen artifact güncel
gate ile 169 test, corpus14/14 TP7/FP0/FN0, auth6/6 geçti. K01 Linux
38640435613 başarılı; artifact22 test/proof5/5, ci profili ve gate kaynak
hashi doğrulandı. Her iki ZIP digest'i GitHub metadata ile eşleşti.
Uzak kanıtlar devam kabulündeki remote-r4/remote-r5-acceptance.json dosyalarında.

## 14 Ekim R3 header ve R6 CLI/rapor yerel kabulü

Başlangıç HEAD `d91238bfbfeb9736068dc6197738f464b5708312`.
Windows/Python 3.10.11, kurulu Chrome. Koordinatörün gerçek browser
`test_dxadom.py` koşusu **75 passed, 0 skipped**; etkilenen statik/dinamik/
kanıt paketinin birleşik koşusu **293 passed**, sıfır failure/error/skip.
Güncel wheel yeni venv'e kaynak dizini dışından kuruldu; üç CLI help exit 0,
BOM'lu config high exit 0, CLI low override bir adayla exit 1 ve JSON/HTML
aynı bulgu kimliği. Tam komutlar, yerel kaynak SHA-256 ve wheel digest'i
[acceptance.json](audit/2026-10-14-r3-r6-continuation/acceptance.json) içinde.
`git diff --check` geçti. Kod a0cf348 push edildi; genel CI 38637484190
3/3 başarılı. Kurulu CLI/analyzer/required artifact gate/opsiyonel browser
adımları success. K01 Linux 38637484214 başarılı; artifact bu turda
indirilmedi. [Uzak step kaydı](audit/2026-10-14-r3-r6-continuation/remote-ci.json).

## 14 Ekim üç işin bağımsız yeniden denetimi

R8: `py -3.10 -m pytest tools/dom-xss-analyzer/test_r8_sanitizer.py
tools/dom-xss-analyzer/test_static_context.py tools/dom-xss-analyzer/test_dxa.py
-q -p no:cacheprovider --tb=short` — **92 passed**; ilk yeni karşı örnek
eski kodda 1 failure verdi. Python 3.10.11/Windows. R6: mevcut build venv'iyle
wheel oluşturuldu; yeni `.dxa/r6-recheck-venv` içine wheel kuruldu ve kaynak
dizini dışından `dxa`, `dxadyn`, `dxaprove --help` çıkışları 0 oldu. Wheel dokuz
beklenen modülü içeriyor. R5: ayrı agent yeni loopback proof 5/5 yaptı;
12 kanıt ve üç kaynak SHA-256 değeri checkout ile eşleşti. Aynı Windows hostu,
mevcut Python; ikinci insan kabulü sayılmaz.
K01 gate testleri ayrıca `py -3.10 -m pytest cases/k01-stored-comment/test_fixture.py
cases/k01-stored-comment/test_repro_gate.py -q -p no:cacheprovider --tb=short`
komutuyla **13 passed** verdi.
[Komut/ortam/sınır](audit/2026-10-14-three-work-recheck/README.md).
74cda81 için genel CI 38598901908 3/3 başarılı; kurulu CLI, analyzer test
paketi ve zorunlu R3/R4 artifact gate adımları geçti.
[Uzak CI kaydı](audit/2026-10-14-three-work-recheck/remote-ci.json).
K01 Linux 38598901721 başarılı; indirilen artifact digest eşleşti,
JUnit 13/0 failure/error/skip, proof 5/5 ve kaynak/çıktı hashleri eşleşti.
[Uzak K01 kabulü](audit/2026-10-14-three-work-recheck/remote-k01-acceptance.json).
Aşağıdaki d41c1cd koşuları önceki teslimin tarihsel kanıtıdır.

## 14 Ekim R5 Linux gate, R8 ve R6 yerel kabulü

- R5+R8 birleşik etkilenen paket: 104 passed, sıfır failure/error/skip.
  Yeni K01 gate Windows Chrome çıktısında 5/5 ve beş kapalı portu kabul etti.
  [R5 komut/hash](audit/2026-10-14-r5-linux-gate/acceptance.json).
  d41c1cd için Linux run 38596197622 ve indirilen artifact geçti:
  13 JUnit sıfır failure/error/skip, K01 5/5 ve beş kapanan port, arşiv
  digest ve kaynak hashleri eşleşti.
  [Uzak kanıt](audit/2026-10-14-r5-linux-gate/remote-acceptance.json).
  İkinci kişi kabulü açık.
- R8 odaklı statik paket: 91 passed, sıfır failure/error/skip.
  [R8 komut/hash](audit/2026-10-14-r8-rebound/acceptance.json).
  d41c1cd genel CI 38596197488 3/3 başarılı; analyzer test step geçti.
- R6 temiz venv core/browser extra kuruldu; üç entrypoint help ve paketlenmiş
  Chrome demo execution-observed geçti.
  [R6 komut/hash](audit/2026-10-14-r6-package-scaffold/acceptance.json).
  d41c1cd genel CI 38596197488 3/3 başarılı; paket install/help step geçti.
  [CI step kaydı](audit/2026-10-14-r6-package-scaffold/remote-ci.json).
  Release kabulü henüz alınmadı.

## 14 Ekim R5/K01 yeni venv tekrarı

Ayrı QA agentı Python 3.10.11 yeni venv, Playwright 1.63.0 ve kurulu Chrome
155.0.8059.79 ile disposable K01 proof CLI 5/5, exit 0 çalıştırdı.
Koordinatör 12 dosya hashini ve README diffini kontrol etti; fixture portları
5/5 kapalı. [Komut, ortam, hashler](audit/2026-10-14-r5-k01-clean-repeat/acceptance.json).
Bu bir pytest koşusu veya ikinci işletim sistemi kabulü değildir; genel R5 açık.

## 14 Ekim R4 auth kontrol runner entegrasyonu

Koordinatör birleşik etkilenen paket: 215 passed, sıfır failure/error/skip.
Gerçek Chrome runner CLI: altı kontrol ve altı cleanup geçti; ayrı mock
candidate skoru TP=1 FP=0 FN=0. [Komut, ortam, hash](audit/2026-10-14-r4-auth-runner/acceptance.json).
bec59b4 uzak CI 38593458769 3/3 başarılı; artifact digest eşleşti,
169 JUnit sıfır skip/error, proof 14/14 TP=7 FP=0 FN=0, auth controls
6/6 cleanup 6/6 ve canonical JSON/Markdown doğrulandı.
[Uzak kabul](audit/2026-10-14-r4-auth-runner/remote-acceptance.json). Bu sayılar önceki 193/527 koşularının yerine geçmez.

Son auth/blind dar teslim birleşik regresyonu: **193 passed**, sıfır hata/skip.

## 14 Ekim auth/CSRF hata kontrolleri

13 focused test geçti; ayrı sahipli/süre sınırlı CLI altı beklenen hata kontrolünü
6/6 kabul etti. Bunlar XSS TP/TN değildir. [Komut, ortam ve hashler](audit/2026-10-14-r4-auth-blind-controls/acceptance.json).
Yeni uzak CI kabulü bekliyor; önceki 527 sayısı bu yeni dosyaların testi değildir.

## 14 Ekim R4 corpus v3

- Base 61dde5c; Windows/Python 3.10.11, pytest 9.1.1, zorunlu Chrome.
- Bütün bench testleri + test_browser_proof.py + test_proof_cleanup.py:
  **527 passed**, sıfır failure/error/skip.
- BENCH_STRICT=1 gerçek CLI: **14/14, TP=7 FP=0 FN=0**, sıfır incomplete.
  JSON/canonical Markdown eşleşti; önceki 9-vaka sayıları tarihsel kaldı.
- Kaynak/çıktı hashleri, tam komut ve ortam
  [acceptance.json](audit/2026-10-14-r4-corpus-v3/acceptance.json) içinde.
- Docker kodu değişmedi; mevcut ürün kontrol regresyonları bu koşuya dahil.
  Canlı Docker/Bludit tekrar edilmedi. Kod 4331403 için uzak CI 38550538424
  3/3 başarılı; indirilen artifact gate 134 test, sıfır skip/error ve corpus
  14/14 TP=7 FP=0 FN=0 ile geçti. Commit kaynaklarının birebir LF byte
  kopyasıyla doğrulandı; yerel CRLF hashleri korunuyor.
  [Uzak kanıt](audit/2026-10-14-r4-corpus-v3/remote-acceptance.json).


## 14 Ekim R4 strict corpus artifact provenance gate

- Başlangıç commit'i `7ce1927e9ac7c2f24e3bbeccd91c87e7d5a29d60`.
  Windows 10 / Python 3.10.11 / pytest 9.1.1.
- İlk gate: **90/204 passed**. QA follow-up runtime karşı örnekleri eklendikten
  sonra güncel odaklı CI gate: **94 passed**; birleşik benchmark scorer, proof
  corpus ve artifact gate: **208 passed**, sıfır failure/error/skip.
- Gate artık `r4-proof.md`'yi zorunlu alıyor; Markdown çıktısını JSON raporun
  canonical render'ıyla birebir karşılaştırıyor. JSON'daki Python, platform,
  komut ve runner/scanner/fixture/corpus SHA-256 alanlarını geçerli kılıyor;
  source hashlerini checkout dosyalarıyla karşılaştırıyor. Yeni karşı örnekler
  eksik/malformed artifact, stale hash/komut ve JSON-Markdown score/identity
  uyuşmazlığını reddediyor.
- QA, Python/platform değerleri için makul ama CI dışı karşı örnekleri ekledi;
  gate artık Python 3.12/Linux'u zorunlu kılar. `7f67d53` için uzak run
  38475480351 üç job'da success ve indirilen artifact eski gate'ten geçti.
  Runtime sıkılaştırması `3ca474a` push edildi. Yeni run 38530419858 CI 3/3
  başarılı; indirilen artifact güncel gate ile geçti (JUnit 94 sıfır skip/error,
  corpus 9/9 TP=3 FP=0 FN=0, Python 3.12.15/Linux, kaynak hashleri eşleşti).
  [Yeni uzak kanıt](audit/2026-10-14-r4-provenance-gate/runtime-remote-acceptance.json).
- [Komutlar ve kaynak hashleri](audit/2026-10-14-r4-provenance-gate/acceptance.json),
  [yerel/uzak kanıt ve sınırlar](audit/2026-10-14-r4-provenance-gate/README.md).

- Devam koşusu (`7f67d53` + runtime/test diff): JSON ve Markdown birlikte
  değiştirilerek dört runtime regresyonu güçlendirildi. Eski gate bu dört
  yanlış beyanı kabul etti (4 regression failure), güncel gate reddetti (4 pass).
  Son birleşik JUnit: **208 passed**, sıfır failure/error/skip; 94 gate vakası
  bu toplamın içindedir. Kaynak ve JUnit hashleri acceptance.json içindedir.

## 13 Ekim R4 Bludit runner bağlantısı

- `py -3.10 -m pytest bench/test_bench.py bench/test_bludit_adapter.py
  bench/test_bludit_ingress.py bench/test_bludit_runner.py
  bench/test_ci_acceptance.py bench/test_ci_self_scan.py
  bench/test_docker_safety.py bench/test_proof_adapter.py
  bench/test_proof_corpus.py bench/test_runner_isolation.py -q
  -p no:cacheprovider --tb=short`: **434 passed**, sıfır failure/error/skip;
  Python 3.10.11 / Windows.
- Gerçek opt-in `bench/run.py --targets mock-reflected-easy --bludit-control`
  koşusu: mock target ayrı candidate TP=1/FP=0/FN=0 (XSS accuracy değildir);
  Bludit raw/escaped davranışları beklenenle eşleşti, status ve cleanup
  `passed`. Ürün kontrolleri `product_controls` altında kaldı; scanner totals
  değişmedi. [Sanitized sonuç](audit/2026-10-13-r4-runner-live/result.json),
  [tekrar/limitler](audit/2026-10-13-r4-runner-live/README.md).
- Son Docker sayıları 15 container, 27 volume, 9 network; önceki lifecycle
  kabulindeki değerlerle aynı. Adapter kendi geçici projesinin cleanup'ını
  doğruladı. Commit `afcb7c1` için iki uzak CI çalışması 3/3 job success;
  [metadata](audit/2026-10-13-r4-runner-live/remote-delivery.json). Hosted CI
  bu yerel Bludit Docker kabulini çalıştırmadı ve artifact içerikleri bu turda
  incelenmedi.

## 13 Ekim R4 ingress ve gerçek ürün kabulü

- Aktif depo `C:\xss\xss-github`, başlangıç commit'i `02e8805`. Python
  3.10.11 / Windows, yerel Docker Desktop ve pinned Bludit imajı.
- `py -3.10 audit/2026-10-12-r4-ingress-live/run_validation.py`:
  **335 passed, sıfır failure/error/skip**, JUnit, komut ve sabit kaynak
  hashleri [acceptance.json](audit/2026-10-12-r4-ingress-live/acceptance.json).
- Aynı script `--live --browser <yerel Chrome yolu>`: gerçek kurulum, ayrı
  login, iki public browser kontrolü PASS; eksik browser ve enjekte edilmiş
  proof uyuşmazlığı doğru error. Üç cleanup PASS. Eski 15 container, 27 volume,
  9 network kimlik/ad setleri birebir korundu.
  [Live acceptance](audit/2026-10-12-r4-ingress-live/live-acceptance.json).
- Bu yalnız yerel ürün lifecycle kabulüdür; bench scorer ve uzak CI bu imajı
  çalıştırmaz. `e62bf34` için [uzak CI 38404107337](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38404107337)
  üç job success; artifact içerikleri bu koşuda indirilmedi.
  Önceki 268 ve engelli
  denemeler tarihsel kanıttır, bu koşuya eklenmez.

## 12 Ekim R4 ürün adapter taslağı — canlı kabul engelli

- Kod checkpoint'i `db96027` uzak main hash'iyle eşleşti. CI 38302697303 ve
  üç job success; yeni mock adapter regresyonları CI'da geçti. Bu koşunun
  artifact içerikleri indirilmedi, Docker ürün lifecycle'ı CI'da çalışmadı.
  [Uzak metadata](audit/2026-10-12-r4-product-adapter/remote-delivery.json).

- Koordinatör birleşik koşusu **268 passed, 26.46 s**, sıfır failure/error/skip;
  83 bağımsız yeni test bu sayıya dahildir. Python 3.10.11 / Windows.
  Başlangıç `d151a8a` + uncommitted kaynak hash'leri koşu boyunca sabit.
- Gerçek Docker üç başlangıçta `80/tcp: []` nedeniyle port kapısında durdu;
  her seferinde cleanup passed. İlk preflight denemesi normalize boş IPAM
  alanı yüzünden başlangıçtan önce durdu; guard boş IPAM'a göre düzeltildi.
- Gerçek installer/login/browser aşamaları çalışmadı; browser hata/negatif
  davranışı burada yalnız bağımsız mock testleridir. Canlı kabul verilmedi.
- Mevcut 15 container / 27 volume listesi birebir korundu. Yeni ürün adapter'ı
  benchmark scorer'ına bağlanmadı; R4 geniş kapsamı ve CI ürün kabulü açık.
- [Komut/hash/koruma](audit/2026-10-12-r4-product-adapter/acceptance.json),
  [JUnit](audit/2026-10-12-r4-product-adapter/acceptance.xml).

## 12 Ekim son kontrol — R9 uzak CI ve yeni çalışma kökü

- R9 8873aaf push ve uzak hash eşleşmesi; CI 38267306222 ve üç job success.
  [Uzak metadata](audit/2026-10-12-r9-report-privacy/remote-delivery.json).
  Bu koşunun artifact içeriği indirilmedi; R4 indirilen artifact kabulü ayrıdır.
- Yeni C:\xss\xss-github: **95 passed, 15.90 s**, sıfır failure/error/skip;
  bench/test_ci_acceptance.py ve test_report_privacy.py tekrarlandı.
  Önceki 185/126 sayılarına eklenmez. 1076 erişilebilir dosya hash'i ve Git
  durumu kopyalama öncesi/sonrası eşleşti. Kaynak işlem kilidi ve erişilemeyen
  cache nedeniyle eski OneDrive kopyası silinmedi.
  [Kontrol kaydı](audit/2026-10-12-relocation/README.md).

## 12 Ekim devamı — uzak R4 kabulü ve R9 rapor mahremiyeti

- `c5d5451` push ve uzak main eşleşmesi doğrulandı. CI **38233880679 success**;
  yeni zorunlu artifact kapısı success. Mevcut GitHub credential yalnız bellekte
  kullanılarak artifact indirildi; token kaydedilmedi/gösterilmedi.
- Uzak Linux/Python 3.12.15: JUnit **94 passed, sıfır failure/error/skip**,
  corpus **9/9 TP=3 FP=0 FN=0**, demo execution-observed. İndirilen içerik
  yerelde yeni kapıdan exit 0 ile geçti; runner/scanner/fixture hash'leri uzak
  commit blob'larıyla eşleşti. [Kanıt](audit/2026-10-12-r4-ci-acceptance/remote/acceptance.json).
- R9 koordinatör kabulü: **126 passed, 37.09 s**, sıfır failure/error/skip;
  Python 3.10.11 / pytest 9.1.1 / Windows. Yeni privacy, R1, HTTP, DOM CLI ve
  blind/journal regresyonları. [Komut/hash](audit/2026-10-12-r9-report-privacy/acceptance.json).
- Aynı iki privacy regresyonu eski `c5d5451` exporter'ı bellekte yüklenince
  beklendiği gibi **2 failed** verdi; yeni pakette geçiyor. İlk yanlış dosya
  adıyla yapılan denemede test koşmadı; acceptance.xml bu başarısız girişimin
  kaydıdır, acceptance-final.xml 126 testlik gerçek kabuldür.
- Uzman limitinden sonra R9 test ve son inceleme koordinatörce tamamlandı;
  bağımsız R9 specialist QA finali yok. Genel R4/R9 kapatılmadı.

## 12 Ekim 2026 — R4/R9 zorunlu CI artifact kapısı (ilk yerel kabul)

- HEAD `471ce977aa843a7286cff8ac86aa993edaf548cf` + commit edilmemiş değişiklikler.
  Python 3.10.11 / pytest 9.1.1 / Windows / Playwright 1.63.0, Chrome 155.0.8059.39.
- Gerçek zorunlu browser paketi: **94 passed, 93.37 s**, failure/error/skip yok.
  Ayrı strict corpus **9/9 completed, TP=3 FP=0 FN=0**, tüm incomplete sayaçları
  sıfır; ayrı demo execution-observed. Yalnız loopback fixture kullanıldı.
- Koordinatör birleşik kapı/self-scan/bench/adapter regresyonları:
  **185 passed, 23.24 s**, failure/error/skip yok. QA'nın 72 testi bunun içindedir;
  ayrı tekrarlar toplanmaz. Yeni kapı gerçek 94-test JUnit/corpus/demo çıktısını geçti.
- [Komut ve kaynak hash'leri](audit/2026-10-12-r4-ci-acceptance/acceptance.json),
  [kapsam ve browser komutları](audit/2026-10-12-r4-ci-acceptance/README.md).
  Hash'ler birleşik koşu boyunca sabitti; daha önceki browser koşusunun öncesinde
  alınmış yeni hash iddiası yok. JUnit hostname alanları paylaşım için çıkarıldı.
- Uzak `471ce97` CI metadata'sı yeniden success; artifact indirmesi HTTP 401.
  İçerik/uzak skip kabulü yapılmadı. Yeni kapı uzak CI'da çalışmadı;
  commit/push yok. Genel R4/R9 ve ürün adapter'ı açık.

## 11 Ekim 2026 — R9 CI self-scan ve devamlılık

- Yeni koordinatör kabulü: **143 passed, 13.21 s**, exit 0; failure/error/skip
  yok. Python 3.10.11 / pytest 9.1.1 / Windows; browser ve Docker kullanılmadı.
  `bench/test_ci_self_scan.py`, `bench/test_bench.py`, `test_dxa.py` ve
  `test_static_context.py` birlikte çalıştı. Gerçek examples self-scan exit 0.
- Başlangıç commit'i `5df2577` + bu teslimin çalışma ağacı. Test edilen kaynak,
  fixture, CI ve beş agent tanımı SHA-256'ları koşu boyunca sabit:
  [komut/ortam/hash](audit/2026-10-11-continuity/acceptance.json),
  [JUnit](audit/2026-10-11-continuity/acceptance.xml),
  [tekrar üretim script'i](audit/2026-10-11-continuity/run_validation.py).
- QA'nın ayrı 20 testlik koşusu birleşik 143'e dahildir; sayılar toplanmaz.
  Eski Bash gate'in RuntimeError/ModuleNotFoundError'ı exit 0'a çevirdiği
  [yeniden üretildi](audit/2026-10-11-continuity/qa-legacy-gate-retry.json).
- Önceki 9 Ekim paketindeki 43 kaynak hash'i mevcut dosyalarla eşleşti;
  824 testlik eski JUnit incelendi. Yeni tam 824 test koşusu yapılmadı.
- Uzak **başlangıç commit'i** `5df2577` için
  [CI 37934071361](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/37934071361)
  ve üç job başarılı; iki artifact metadata'sı görüldü. İçerik/skip sayısı bu
  kontrolde doğrulanmadı. Bu sonuç yeni değişikliğin uzak CI sonucu değildir.
- [Denetim, görev sahipliği ve kapsam](audit/2026-10-11-continuity/README.md).
- Yeni kod commit'i `471ce977aa843a7286cff8ac86aa993edaf548cf` uzak main ile
  doğrulandı. [Yeni CI 38171311413](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38171311413)
  ve üç job **success**; self-scan/regresyon, zorunlu R3 ve strict R4 adımları
  başarılı. [Job/adım metadata'sı](audit/2026-10-11-continuity/remote-delivery.json).
  Artifact içeriği/skip sayısı ayrıca incelenmedi; indirme API'si HTTP 401 döndü.
  Bu kayıt yerel 143 sonucundan ayrıdır, uzak test toplamı iddia edilmez.

## 9 Ekim 2026 — 8–9 Ekim değişikliklerinin tam tekrarı

- Analyzer ve bench: **824 passed, 309.10 s**, exit 0; failure/error/skip yok.
- Ayrı K01 HTTP fixture: **2 passed, 1.20 s**, exit 0.
- Gerçek Chrome strict proof corpus: **9/9 completed, TP=3 FP=0 FN=0**, exit 0.
- Python 3.10.11, pytest 9.1.1, Playwright 1.63.0, Chrome 155.0.8059.39.
  Kaynak hash'leri koşu boyunca sabit; browser zorunlu, Docker lab kapalı.
- R4 süreç izolasyonu, R8 statik context ve R9 callback/Docker guard testleri
  dahil. Docker guard testleri gerçek kurulum/login kabulü değildir; uzak CI
  bu yerel sonuçla doğrulanmaz. Eski hedefli koşular bu sayılara eklenmez.
- [Komutlar, JUnit, kaynak hash'leri ve sınırlar](audit/2026-10-09-resume/README.md).

## 7 Ekim 2026 — R3/R4 baştan sona yeniden doğrulama

- Yeni ilk tam koşu: 679 passed, 213.46 s; sonradan eklenen cleanup regresyonları
  bu koşuda yoktu. Yeni cleanup karşı örneği: **2 failed**, 4.48 s, exit 1.
- Düzeltme sonrası yeni tam analyzer/bench paketi: **681 passed, 223.96 s**,
  exit 0; failure/error/skip sıfır. `test_dxadom` 73, browser proof 22,
  cleanup 2, scope 11, benchmark 43, adapter 49, corpus 21 dahil.
  [JUnit](audit/2026-10-07-r3-r4-revalidation/acceptance-final.xml),
  [bütün modül sayımları](audit/2026-10-07-r3-r4-revalidation/test-summary.json).
- Gerçek Chrome 155.0.8059.39, Playwright 1.63.0, Python 3.10.11 kullanıldı;
  audit bootstrap açık Windows Chrome yolunu test sürecinde dxadom'a verdi.
- Yeni ayrı strict CLI: **9/9, TP=3 FP=0 FN=0**, exit 0, wall 16.32 s.
  Eksik browser: 9 error/0 completed/exit 1. Gerçek lab exception: 2 selected,
  1 completed/1 error/exit 1; iki listener kapandı ve JSON/MD üretildi.
  R3 demo exit 0 ve JSON/HTML nesne eşitliği doğrulandı.
- R3 mevcut loopback kapsamı PASS; R4 7 Ekim yerel kapsamı PASS. Genel R4,
  hard timeout ve uzak Linux CI açık; sonuçlar örtüşür, sayılar toplanmaz.
  [Komutlar, kaynak incelemesi ve sınırlar](audit/2026-10-07-r3-r4-revalidation/README.md).

## 7 Ekim 2026 — R4 vaka istisnası izolasyonu

- Önceki kabul paketindeki 136 test ve 9/9 sonucu dosyalardan incelendi;
  runner/scanner/fixture hash'leri başlangıç kaynaklarıyla eşleşti.
- Yeni regresyonların düzeltme öncesi koşusu: **8 failed, 2 passed,
  39 deselected, 1.72 s**, exit 1. [JUnit](audit/2026-10-07-r4-case-isolation/before.xml).
- Yeni birleşik yerel kabul: **146 passed, 78.86 s**, exit 0, skip yok.
  [JUnit](audit/2026-10-07-r4-case-isolation/acceptance.xml).
- Yeni strict Chrome CLI: **9/9 completed, TP=3 FP=0 FN=0**, diğer durum
  sayaçları sıfır, exit 0, wall 17.23 s.
  [JSON](audit/2026-10-07-r4-case-isolation/corpus-results.json).
- İstisna enjeksiyonları aynı süreçte gerçek main/scorer/renderer akışını
  doğrular; hard timeout veya OS crash/kill testi değildir. Uzak CI yapılmadı.
  Koşular örtüşür; sayılar toplanmaz. [Komutlar ve sınırlar](audit/2026-10-07-r4-case-isolation/README.md).

## 7 Ekim 2026 — native R4 corpus/CI turu

- Değişiklik öncesi scope/R3/benchmark/adapter: **89 passed, 51.61 s**, skip yok.
- Frame canary okuma hatası karşı örneği düzeltmeden önce **1 failed,
  21 deselected**: error yerine inconclusive üretiliyordu.
- Son birleşik kabul: **136 passed, 80.88 s**, skip yok, exit 0.
  [JUnit](audit/2026-10-07-r4-native/acceptance.xml).
- Strict gerçek Chrome CLI: **9/9 completed, TP=3 FP=0 FN=0**, error/skip yok,
  exit 0. [JSON](audit/2026-10-07-r4-native/corpus-results.json).
- Bağımsız oracle, JS-kapalı gerçek callback ve malformed/incomplete kontrolleri
  dahil. Koşular örtüşür; sayılar toplanmaz. Uzak CI çalıştırılmadı.
- [Komutlar, roller ve sınırlar](audit/2026-10-07-r4-native/README.md).

Aşağıdaki kayıtlar önceki teslimlerin sonuçlarıdır.

## Push öncesi belge temizliği doğrulaması

Her dosya ayrı olarak bir kez `python -m pytest <dosya> -q -p no:cacheprovider
--tb=short` ile çalıştırıldı. Sayılar birleştirilmez. Yerel loglar
`.dxa/prepush/` altındadır; depoda yoktur, aynı komutla yeniden üretilebilir.

| Dosya | Sonuç |
|---|---|
| tools/dom-xss-analyzer/test_crawl_scope.py | 11 passed |
| tools/dom-xss-analyzer/test_dxadyn.py | 169 passed |
| tools/dom-xss-analyzer/test_r2_contract.py | 30 passed |
| tools/dom-xss-analyzer/test_auth_guards.py | 15 passed |
| tools/dom-xss-analyzer/test_browser_proof.py | 21 passed |
| tools/dom-xss-analyzer/test_dxadom.py | 37 passed, 36 skipped |
| tools/dom-xss-analyzer/test_r1_contract.py | 30 passed |
| tools/dom-xss-analyzer/test_dom_cli_evidence.py | 6 passed |
| bench/test_bench.py | 43 passed |
| bench/test_proof_adapter.py | 14 passed |

11 belgenin yerel bağlantı hedefleri kontrol edildi; eksik hedef yok.
`git diff --check` temiz. Testlerde standart Chrome yolları değiştirilmedi:
`test_browser_proof.py` DXA_BROWSER destekler; `test_r1_contract.py` içindeki
Chrome testi desteklemez. İkincisine aynı ortam değişkeninin eklenmesi öneridir,
bu teslimde uygulanmadı. Eski browser discovery skip'leri kapanmış sayılmaz.

## Sınırlı multi-agent geliştirme turu — tarihsel 6 Ekim koşusu

- Birleşik scope/HTTP/auth/browser/rapor/benchmark paketi: **339 passed,
  86.51 saniye**. Log/JUnit yerel çıktıdır, depoda yoktur;
  tarihsel yeniden üretim komutu yerel kopyadaki audit paketindedir; paket kamuya açık depodan çıkarılmıştır.
- Chrome proof-suite: dört seçilen/dört tamamlanan, TP=1 FP=0 FN=0,
  strict exit 0. JSON/Markdown yerel çıktıdır, depoda yoktur;
  tarihsel yeniden üretim komutu yerel kopyadaki audit paketindedir; paket kamuya açık depodan çıkarılmıştır.
- Eval global-scope testi yeterli değildi: fonksiyon-local karşı örnek önce
  başarısız oldu; hook kaldırılınca 21 browser testi geçti. Ortak JSON/HTML
  raporunda eval gözleminin desteklenmediği artık açıkça kayıtlıdır.
- Bu tur tam depo veya uzak CI koşusu değildir. Önceki 36 browser skip'in
  tamamının çözüldüğü iddia edilmez. Kapsam ve katkıların tarihsel kaydı yerel kopyada korunup kamuya açık depodan çıkarılmıştır.

## R3 ilk browser zinciri — tarihsel teslim

- Önceki tam paket **544 passed, 36 skipped, 1 warning**, 141.50 saniye.
  R3 değişikliklerinden sonra odaklı browser paketi **21/21 geçti**;
  route budget, header allowlist ve direct eval kontrolleri dahil.
- Loopback demo: HTTP/browser kullanıcı+rol kontrolü, stored submit 201, read
  200 ve eşleşen CID; Chrome 154.0.8037.98, Playwright 1.63.0.
- Negatifler: fixed/JSON/dialog/JS disabled, yanlış rol, cross-origin request,
  gecikme penceresi, eksik browser ve geçersiz scope. href, iframe, delayed,
  eval lexical-scope, cookie/bearer ve CSRF olumlu kontroller de var.
- [R3 test logu](audit/2026-10-06-r3-final/pytest.log),
  [JUnit](audit/2026-10-06-r3-final/pytest.xml),
  [demo JSON](audit/2026-10-06-r3-final/demo/result.json),
  [HTML](audit/2026-10-06-r3-final/demo/result.html),
  [kapsam/sınırlamalar](tools/dom-xss-analyzer/BROWSER-PROOF.md).
- WebSocket filtreleme denemesi takıldı ve kaldırıldı. Yeni browser komutu
  HTTP/redirect'i same-origin kısıtlar; WebSocket/ağ sandbox desteği yok.
  R3 kabul scope'u tamam; uzak Linux CI henüz çalıştırılıp doğrulanmadı.
- 36 eski dxadom browser testi mevcut binary keşfinde atlandı; R3 yeni testleri
  DXA_REQUIRE_BROWSER=1 ile skip edemez. Uyarı benchmark utcnow kullanımı.

## R2 HTTP kabul kapanışı — güncel teslim

- **526 passed, 36 skipped, 1 warning**, 112.13 saniye. 30 yeni R2 kabul
  testi: hedefe özel oturum sözleşmesi, rol kaydı, CLI hata duruşu, fractional
  rate, tek kullanımlık CSRF ve stored sırası, hata olayları ve desteklenmeyen birleşimler.
- 36 eski browser testi otomatik binary keşfi nedeniyle atlandı; geçmiş sayılmadı.
  Uyarı benchmark datetime.utcnow kullanımıdır. GitHub CI sonucu henüz doğrulanmadı.
- [Kapanış matrisi](audit/2026-10-06-r2/R2-KAPANIS.md),
  [log](audit/2026-10-06-r2/pytest.log), [JUnit](audit/2026-10-06-r2/pytest.xml).
- İlk tam koşudaki CSRF'siz guestbook konfigürasyon eksiği hedefe özel
  csrf_field ayarıyla düzeltildi. Paylaşılan HTTP oturumunda sıralama davranışı
  belgelenmiştir; eski paralel hız iddiası güncel kabul değildir.

## R2 auth guard — önceki teslim

- Tam paket **496 passed, 36 skipped, 1 warning**, 89.38 saniye.
  36 eski browser testi otomatik keşif nedeniyle atlandı; benchmark utcnow
  uyarısı devam ediyor. Geçmiş sayılan testlere atlamalar dahil değil.
- 15 yeni regresyon: 401/403/429/500, eksik/null/boş/geçersiz token,
  eski cookie, form hata yanıtı ve CLI durma + ortak hata raporu.
- Odaklı auth/flow koşusu **49 passed**. İlk tam koşuda eksik dashboard'lu
  eski stored fixture başarısızdı; fixture tamamlandıktan sonra yukarıdaki
  tam koşu geçti. Üretimdeki HTTP hata kontrolü gevşetilmedi.
- [Test logu](audit/2026-10-05-r2-auth/pytest.log),
  [JUnit](audit/2026-10-05-r2-auth/pytest.xml),
  [davranış ve sınırlar](tools/dom-xss-analyzer/AUTH-LIMITS.md),
  [staj kaydı](staj/2026-10-05-r2-auth.md).

R2 ilk auth guard kabulü tamam; hedefe özel oturum/rol doğrulaması,
fractional rate ve CSRF sıralaması açık.

## K01-min stored yorum vakası — önceki teslim

- Yerel browser deneyi: **5/5 kontrol geçti**, Chrome 154.0.8037.93, Playwright
  1.63.0, Python 3.12.14. Savunmasız HTML'de ayrı okuyucu context'inde canary;
  aynı payload için fix sonrası, JS kapalı, JSON-only ve normal dialog negatifleri.
- Bot R1 raporu reflection/candidate seviyesinde kalır; vaka execution sonucu
  ayrı kaydedilir. Bu çalışma genel R3 execution motorunu tamamlamaz.
- İki HTTP fixture regresyonuyla tam paket: **481 passed, 36 skipped, 1 warning**,
  80.33 saniye. Atlamalar eski browser otomatik keşfi, uyarı benchmark utcnow.
- [Vaka ve tekrar üretim](cases/k01-stored-comment/README.md),
  [browser sonuçları](cases/k01-stored-comment/evidence/2026-10-05-verified/result.json),
  [fix diff](cases/k01-stored-comment/evidence/2026-10-05-verified/fix.diff),
  [pytest logu](audit/2026-10-05-k01/pytest.log), [JUnit](audit/2026-10-05-k01/pytest.xml).
- İlk browser denemesi route callback imza hatasıyla başarısız oldu; helper
  düzeltildikten sonraki 5/5 kaydı yayımlandı. Önceki başarısız çıktı yerel audit
  alanında korundu, başarılı deney sayısına katılmadı.

K01-min tamam. Yeni venv kurulumu/bağımsız temiz ortam tekrarı henüz doğrulanmadı;
tam R5'in bu kabul maddesi açık kaldı. Haricî ürün, oturum rolü veya CVE kanıtı yok.

## R1 kabul kapsamı kapanışı — önceki teslim

- Tam paket: **479 passed, 36 skipped, 1 warning**, 87.53 saniye.
- Önceki teslimin üzerine 29 kabul/regresyon örneği: dokuz ayrıştırma sınırı,
  aynı gözlemi kaybetmeden gruplama, bilinmeyen sink/rol, geçersiz şema ve
  kazanılmamış proof/rol iddiaları, maskeleme, ayrı hata/skip olayları, DOM/journal/
  statik/bridge adaptörleri, flow/auth-flow girdi hatası.
- **Gerçek yerel Chrome kontrolü geçti:** normal alert + innerHTML sink; yalnız
  candidate/sink-observed; aynı bulgu kimliği JSON ve HTML'de. Chrome yolu testte
  açık verildi. [JSON](audit/2026-10-05-r1/chrome.json), [HTML](audit/2026-10-05-r1/chrome.html).
- Eski 36 browser testi otomatik binary keşfi nedeniyle atlandı; bunlar geçmiş
  sayılmadı. Uyarı benchmark'taki `datetime.utcnow()` deprecation uyarısıdır.
- Ara kontrol: 259 odaklı test geçti; ilk tam paket 476 geçti. Son üç kapanış
  kontrolünden sonra 479 sonucu alındı. Arada otomatik onay incelemesi kullanım
  limitine takıldığı için bir test komutu hiç çalışmadı; sonuç diye sayılmadı.
- [Tam log](audit/2026-10-05-r1/pytest-r1.log), [JUnit](audit/2026-10-05-r1/pytest-r1.xml),
  [kabul testleri](tools/dom-xss-analyzer/test_r1_contract.py),
  [kapanış matrisi](audit/2026-10-05-r1/R1-KAPANIS.md),
  [resmî sözleşme](tools/dom-xss-analyzer/EVIDENCE-CONTRACT.md).

Bu sonuç R1'in raporlama/kanıt kabul kapsamını kapatır. R2 auth/rate/CSRF,
R3 execution/rol doğrulaması ve R4 benchmark doğruluğu tamamlandı sayılmaz.

## R1 HTTP kanıt modeli — önceki teslim

- Tam paket: **450 passed, 36 skipped, 1 warning**, 76.29 saniye.
- 12 yeni regresyon: yedi Content-Type × beş HTTP yolunun ortak sınıflandırması;
  üç yanlış bağlamda raw marker; encoded flow; gerçek localhost JSON echo üzerinde
  ayrı CLI sürecinin console/JSON/HTML çıktısı ve ortak finding kimliği.
- İlk odaklı çalışmanın sandbox ortamı localhost ve geçici dosyaları engelledi;
  aynı paket gerekli izinlerle **215 passed** verdi. Son JSON/HTML ekleri yukarıdaki
  tam paketle doğrulandı. Test beklentileri execution iddiasını korumak yerine
  reflection semantiğine güncellendi; negatif kontroller ayrıca eklendi.
- 36 browser testi otomatik Chrome keşfi nedeniyle atlandı. Yeni browser proof
  doğrulaması yapılmadı. Tek uyarı benchmark'ın `datetime.utcnow()` kullanımıdır.
- [Log](audit/2026-10-05/pytest-http-evidence.log),
  [JUnit](audit/2026-10-05/pytest-http-evidence.xml),
  [regresyon kaynağı](tools/dom-xss-analyzer/test_http_evidence.py),
  [model ve sınırlar](tools/dom-xss-analyzer/HTTP-EVIDENCE.md).

Genel R1 kapanmadı: DOM/attempt şeması entegrasyonu, sink/rol dedup ve bütün
hata/atlama olaylarının ortak raporu açık. HTTP reflection açıklık kanıtı değildir.

## R1 kalıcı stored blind takip — önceki teslim

- Tam paket: **438 passed, 36 skipped, 1 warning**, 76.57 saniye.
- 18 yeni regresyon: stored/stored-auto yansımasız beş aile, gönderim hatası,
  canlı ve süreç kapandıktan sonra callback, eşzamanlı kalıcı yazma, tekrar
  kontrol, CID/zaman/endpoint/run ayrımı, yanlış yanıt, mahremiyet ve rapor escaping.
- İki CLI süreci + localhost HTTP fixture: tarama kapanır, callback daha sonra gelir,
  ayrı kontrol komutu aynı attempt kimliğine bağlar; hedef **yalnız bir POST** alır.
- JSON ve HTML kontrol raporu aynı attempt listesinden oluşturulur.
- Ara odaklı çalışma **220 passed**; son dört ek test ve canlı callback kalıcılığı
  yukarıdaki tam pakette doğrulandı.
- 36 browser testi mevcut otomatik Chrome keşfi sorunu nedeniyle atlandı.
  Bu teslim yeni browser execution doğrulaması yapmadı. Tek uyarı benchmark'taki
  `datetime.utcnow()` kullanımının deprecation uyarısıdır.
- [Test logu](audit/2026-09-29/pytest-blind-journal.log),
  [JUnit](audit/2026-09-29/pytest-blind-journal.xml),
  [test kaynağı](tools/dom-xss-analyzer/test_blind_journal.py),
  [tekrar üretim ve sınırlar](tools/dom-xss-analyzer/BLIND-JOURNAL.md).

Sınır: journal yalnız stored/stored-auto blind gönderim/callback kaydıdır;
bütün reflection/sink bulgularının ortak şeması değildir. Rol operatör etiketidir.
Callback JavaScript execution veya açıklık kanıtı değildir. Genel R1 açık kalır.

## R2 JSON gönderimi — önceki teslim

- Tam paket: **420 passed, 36 skipped, 1 warning**, 69.03 saniye.
- 36 browser testi otomatik Chrome keşfi nedeniyle atlandı; browser entegrasyonu tamamlandı sayılmıyor.
- Yeni yedi regresyon senaryosu: 950 payload'ın gerçek submit fonksiyonunda JSON round-trip'i; iç içe değer/anahtar ve kontrol karakterleri; üç geçersiz JSON durumu; anahtar çakışması; iki eşzamanlı JSON isteğinde ortak header izolasyonu.
- Eski quote testi elle escape algoritmasını kopyalamak yerine gerçek submit fonksiyonunun çıktısını kontrol ediyor.
- Odaklı JSON + dinamik test çalışması 176 geçti; son quote testi değişikliği yukarıdaki tam pakette doğrulandı.
- Kanıtlar: [test logu](audit/2026-09-28/pytest-json-transport.log), [JUnit](audit/2026-09-28/pytest-json-transport.xml).

Önceki 413 test sonucu callback teslimine aittir. JSON request kodlaması düzeltildi;
flow modundaki response/XSS sınıflandırması, auth ve CSRF açık kalır.

## Ana roadmap ve callback düzeltmesi — önceki teslim

- Callback/dinamik odaklı testler: **206 passed**.
- Tüm paket: **413 passed, 36 skipped, 1 warning**, 103.58 saniye. Atlanan 36 test Windows browser keşfi nedeniyle; cache yazma uyarısı var.
- 19 yeni callback regresyonu geçti; yanlış proof bekleyen önceki testler yeni gözlem semantiğine uyarlandı.
- JavaScript kapalı gerçek Chrome 154.0.8037.58: img isteği → 1 callback → 1 eşleşme → `severity=resource-callback`, `evidence_level=resource-callback`; JS proof iddiası yok.
- Canary id'si eksik/boş/farklı olduğunda eşleştirme reddedilir; HTTP yöntemi veya payload ailesi JS yürütme kanıtı sayılmaz.
- CLI help ve HTML resource-callback anlamını taşıyor; HTML'de istek metadata'sı escape ediliyor.

Kanıtlar: [tam test logu](audit/2026-09-28/pytest-master-roadmap.log), [JUnit](audit/2026-09-28/pytest-master-roadmap.xml),
[odaklı test logu](audit/2026-09-28/pytest-callback-focused.log), [Chrome sonucu](audit/2026-09-28/resource-callback-fix-browser.json),
[örnek rapor](audit/2026-09-28/resource-callback-report.html). Otomatik regresyonlar
`tools/dom-xss-analyzer/test_blind_correlation.py` içindedir.

Sınır: bu teslimde gerçek canary execution motoru veya yansımasız kalıcı blind takip yapılmadı. Callback gözlemi ile açıklık/etki ayrı tutuldu; ortak kanıt şeması henüz tamamlanmadı.

## İlk geliştirme teslimi

- Yeni CLI regresyon dosyası: **6 passed**.
- Geliştirme kopyasının tüm test paketi: **394 passed, 36 skipped, 1 warning**, 68.83 saniye.
- Atlanan 36 test browser keşfi nedeniyle atlandı; Windows Chrome yolunun otomatik bulunması hâlâ açık iş. Bunlar geçmiş baseline'da açık Chrome yolu ile çalıştırılmıştı; bu teslimde yeniden çalışmış gibi sayılmıyor.
- Mevcut Chrome ile ayrı gerçek tarayıcı kontrolü: yalnız 127.0.0.1 üzerinde normal alert sayfası açıldı. **OBSERVED-DIALOG**, exit 0; **PROVEN-EXECUTABLE yok**. Test sürecinde browser yolu açık verildi; kaynakta platform keşfi değiştirilmedi.
- Pytest cache yazma uyarısı test başarısızlığı değildir.

Tekrarlama: pytest kurulu ortamda depo kökünden `python -m pytest -q -ra`.
Dar regresyon: `python -m pytest tools/dom-xss-analyzer/test_dom_cli_evidence.py -q`.

Bu çalışma alanındaki ham kanıtlar:

- [Tam test logu](audit/2026-09-28/pytest-development.log)
- [JUnit sonucu](audit/2026-09-28/pytest-development.xml)
- [Gerçek tarayıcı sonucu](audit/2026-09-28/dom-dialog-fix-browser.json)
- Otomatik CLI regresyonları: `tools/dom-xss-analyzer/test_dom_cli_evidence.py`.

Bu bağlantılar depodaki tarihsel kanıtlara gider. Yerel kullanıcı dizinleri paylaşım
kopyalarında maskelendi; test sonuçları değiştirilmedi. Eski denetim scriptlerinin
tümü bu kanıt paketine dahil değildir; paket açıklaması `audit/2026-09-28/README.md` içindedir.

## İlk teslimin sınırı (tarihsel)

Yalnız bare-visit dialog çıktısındaki yanlış proof iddiası düzeltildi. Yeni execution doğrulama motoru eklenmedi. Blind korelasyon, breakout severity, auth, JSON ve benchmark kusurları açık; ROADMAP'te ayrı kabul koşulları var.

Orijinal ZIP ve denetim kaynak kopyası korunmuştur. İlk düzeltmeler `2703d1a`
ile Git geçmişine ve GitHub main dalına aktarıldı. Sürüm etiketi oluşturulmadı.

## PyPI 0.2.0 publication and production install gate — 24–25 October

Source release commit `8891219c3899f3208db9d19bff1990f96544dac5`, tag
`v0.2.0`. Rebuilt sdist and wheel with the isolated build environment; `twine
check dist/*` passed for both. TestPyPI accepted both artifacts. A clean Python
3.11 venv installed `dxa-research-toolkit==0.2.0` from TestPyPI; `dxa`,
`dxadyn`, `dxaprove`, and `dxa-sarif --help` all exited successfully (4/4).
This was package/install verification, not a source test run.

Production PyPI accepted the same wheel and sdist; the public JSON endpoint
then reported package `dxa-research-toolkit`, version `0.2.0`, and two files.
A separate clean Python 3.11 venv installed `dxa-research-toolkit==0.2.0`
from production PyPI. `dxa --help`, `dxadyn --help`, `dxaprove --help`, and
`dxa-sarif --help` all exited 0 (4/4). This is an install/entry-point check,
not a source test run. Artifact hashes and release details are in
`audit/2026-10-24-pypi-0.2.0/README.md`.
