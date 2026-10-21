# R7 / A05 — bounded local Spring RFD lead check

## Scope and source identity

This check was scheduled from the existing R7/A05 Spring Web advisory lead for
the user-owned Kadrom repository, pinned at source commit
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c` (2026-10-20). The toolkit's
`ROADMAP.md` identifies this as the remaining bounded local check for the
source-level Spring RFD candidate. Kadrom has no root `VALIDATION.md`; its
README says the backend CI runs Maven `verify`, but no project-specific local
test acceptance instructions were found that change this narrow check.

Only the existing `hotelapp/src/test/resources/application-test.yml` boundary
was considered: H2 in-memory (`jdbc:h2:mem:hotel_test`, Hibernate
`create-drop`), Flyway disabled, and Cloudinary disabled. No Docker engine,
container, volume, existing database, external service, browser, or hosted
target was started or contacted. No active script or executable content was
prepared. A temporary focused JUnit test was written under the Kadrom test
tree, then removed after the local runner preflight failed. Kadrom's git
working tree was clean both before and after the temporary-file window.

Relevant source at the pinned commit:

- `hotelapp/src/main/java/com/hotelapp/controller/MessageController.java:35-50`
  authorizes the attachment route, loads stored bytes, and builds an attachment
  `Content-Disposition` using `ContentDisposition.attachment().filename(name,
  UTF_8)`; it also sets `Cache-Control: no-store, private` and
  `X-Content-Type-Options: nosniff`.
- `hotelapp/src/main/java/com/hotelapp/service/MessageService.java:282-291`
  checks conversation membership and verifies that the message belongs to the
  requested conversation and has an attachment before returning it.
- `hotelapp/src/test/java/com/hotelapp/integration/PrivateAttachmentHttpTest.java:24-51`
  is the existing MockMvc pattern: H2 test profile, mocked `FileStorageService`,
  anonymous 401, nonmember 403, and member byte-return checks. Its test also
  asserts that the response does not redirect to storage.
- `hotelapp/src/test/resources/application-test.yml:1-17,60-64` configures H2
  in-memory `create-drop`, disables Flyway, and sets Cloudinary disabled.

Source hashes (SHA-256):

| Pinned source file | SHA-256 |
|---|---|
| `hotelapp/pom.xml` | `AF8E4AED12B15A646460987E2FD94BDA8F31C482537498599A3BB473B5CE8112` |
| `hotelapp/src/main/java/com/hotelapp/controller/MessageController.java` | `EA77EFD19302CDB2E1BB3EDBD3CCC85A2DE609763512E48F2B3F5C05A56D8D0B` |
| `hotelapp/src/main/java/com/hotelapp/service/MessageService.java` | `CD34B413E8923412094B58F1852842EFD5FB231DB87BE2182CA0448AAD04D50D` |
| existing `PrivateAttachmentHttpTest.java` | `F381F67CAEDF6D6AA97078154BB21D88F9B8B8CE223F08253C257FAC8BF8119F` |
| existing `application-test.yml` | `E9992524B6E40754D48AC1FCCF043F2558463F97AA847A5A15403939CFEF307E` |

## Attempt and actual result

The temporary test used two synthetic conversation members and a nonmember.
It was designed to check anonymous and nonmember denial, then request the
attachment as a member with the harmless Unicode filename
`résumé-候选人.txt` and inert UTF-8 marker bytes
`LOCAL-RFD-CHECK-ONLY: inert marker bytes`. It would print and assert the
resulting `Content-Disposition`, content type, and returned bytes. The first
attempt did not execute because the repository launcher could not find Maven.

Command, from `hotelapp/`:

```powershell
.\mvnw.cmd -o -Dtest=RfdLocalCheckTempTest test
```

The first command result was exit code **1** before Maven/test startup. The
repository file `mvnw.cmd` is a small launcher that runs `where mvn`; it
printed:

```text
Maven yuklu degil. Yuklemek icin:
  Windows: https://maven.apache.org/download.cgi

Veya IntelliJ IDEA kullan - Maven'i otomatik yonetir.
```

`Get-Command mvn` and `where.exe mvn` found no Maven executable; no `MAVEN_HOME`
or `M2_HOME` was set. Java is present (runtime `21.0.11`), but this does not
replace Maven. No dependency download or installation was attempted.

### Cached Maven retry

The coordinator located a cached Maven 3.9.16 binary. The same temporary test
was recreated (temporary test SHA-256
`7CAA961906284A7D172F4533F2DD6FD2F2A976CDCFE41426C92A15A3B9D9A6E4`) and
the assigned offline command was run from the toolkit root:

```powershell
& 'C:\Users\user\.m2\wrapper\dists\apache-maven-3.9.16\56ba1f9f\bin\mvn.cmd' -o '-Dmaven.repo.local=C:/Users/user/.m2/repository' -f .dxa/a04-kadrom-source/hotelapp/pom.xml '-Dtest=RfdLocalCheckTempTest' test
```

The cached executable was present and Maven scanned the project, copied
resources, and started compiling 245 source files. On the first cached attempt,
the command exited **1** with `BUILD FAILURE` after 23.900 seconds, before
Surefire/test startup. The output included `Erişim engellendi.` and the
compiler error:

```text
Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.11.0:compile (default-compile) on project hotel-student-platform: Fatal error compiling: C:\Users\user\.m2\repository\org\springframework\boot\spring-boot-starter\3.2.5\spring-boot-starter-3.2.5.jar -> [Help 1]
```

This was an offline Maven compiler/build error associated with access to the
cached Spring Boot starter JAR; the output did not establish an application
compile defect. At that attempt, no test method ran. The temporary test source
was then rewritten as UTF-8 without BOM after a subsequent escalated run
reported `illegal character: '\ufeff'` at its first character. That run also
stopped before application tests. No install, download, network access, or
dependency-cache change was attempted.

### Final escalated offline run

After the BOM was removed, the coordinator ran the same focused test using the
cached Maven executable and offline repository. Surefire recorded **1 test,
0 failures, 0 errors, 0 skipped**; Maven reported `BUILD SUCCESS`. The Surefire
test elapsed time was 35.38 seconds (test method 0.685 seconds). The retained
local report is
`hotelapp/target/surefire-reports/TEST-com.hotelapp.integration.RfdLocalCheckTempTest.xml`;
its testcase is `inertUnicodeAttachmentHeaderBytesAndMembership`.

The actual observed response for the authorized synthetic conversation member
was:

```text
HTTP status: 200
Content-Disposition: attachment; filename="=?UTF-8?Q?r=C3=A9sum=C3=A9-=E5=80=99=E9=80=89=E4=BA=BA.txt?="; filename*=UTF-8''r%C3%A9sum%C3%A9-%E5%80%99%E4%BA%BA.txt
Content-Type: text/plain
Body UTF-8: LOCAL-RFD-CHECK-ONLY: inert marker bytes
```

The same test asserted **401** for anonymous access and **403** for the
synthetic nonmember; the mocked storage service had no interactions before the
authorized request. It then returned the inert marker bytes for the member.
Only the `BUSINESS_OWNER` member's authorized download was exercised in this
temporary test. No browser was launched and no active content was used.

The temporary test file
`hotelapp/src/test/java/com/hotelapp/integration/RfdLocalCheckTempTest.java`
was removed exactly after the successful focused run. A subsequent `git status
--porcelain=v1` in the pinned Kadrom checkout returned no entries, and
`Test-Path` confirmed that temporary test file was absent. The pre-existing
test and profile hashes above remained available for comparison. No permanent
Kadrom file was modified.

## Disposition and limits

The source-level lead remains plausible: user-supplied original attachment
filename is stored (`MessageService.java:307-320`) and later reaches a UTF-8
`Content-Disposition` builder (`MessageController.java:42-50`); the download
service checks conversation membership. The existing source does not establish
the effective Spring response header for the Unicode filename in this runtime,
nor does it establish browser interpretation or a reflected file download.

The bounded MockMvc test confirms that this pinned local application path
returns the stored inert bytes to a synthetic conversation member and emits the
recorded RFC-compatible encoded Unicode filename header; it also confirms the
tested anonymous/nonmember denial statuses. This validates response encoding
and the exercised authorization path only. It does **not** establish browser
interpretation, reflected file download behavior, malicious-content execution,
or RFD exploitability. The earlier missing-launcher, cached-JAR access, and
temporary-test BOM errors were runner/build failures, not application test
failures. No RFD, exploit, browser execution, or vulnerability is confirmed;
the source-only Spring GHSA candidate remains open under R7/A05 pending separate
evidence for the advisory's malicious-content/browser conditions.
