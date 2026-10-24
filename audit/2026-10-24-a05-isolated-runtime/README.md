# A05 isolated current-source runtime — risk plan and result

Date: 24 October 2026. Workstream: A05. Owner: `/root/a05_isolated_runtime`.
Target is only the user's authorized local Kadrom checkout at
`.dxa/a04-kadrom-source`, branch `main`, commit
`eb031a19f9f6b0715d8b302751542f631216cdd5`. This audit records a bounded,
test-only local runtime, not a production or proxy assessment.

## Risk and rollback plan — written before any new runtime resource

### What must be preserved

Do not start, stop, remove, inspect contents of, or connect to any pre-existing
container/network/volume. The read-only inventory before setup showed:

- A05 containers: `a05-kadrom-effective-20261022-backend` / `-mysql`
  (`Created`), `a05-kadrom-effective-20261022b-backend` / `-mysql`
  (`Exited`), and `a05-kadrom-method-20261022c-backend` / `-mysql`
  (`Exited`).
- A05 networks: `a05-kadrom-effective-20261022_internal`,
  `a05-kadrom-effective-20261022b_internal`, and
  `a05-kadrom-method-20261022c_internal`.
- A05 volumes: `a05-kadrom-effective-20261022_mysql_data`,
  `a05-kadrom-effective-20261022b_mysql_data`, and
  `a05-kadrom-method-20261022c_mysql_data`.
- A04 containers/networks/volumes: `a04-kadrom-owner-read-20261022-*`,
  `a04-kadrom-disposable-20261021-*`, and `a04-kadrom-20261021-*`, including
  `a04-kadrom-owner-read-20261022_mysql_data`,
  `a04-kadrom-disposable-20261021_mysql_data`, and
  `a04-kadrom-20261021_mysql_data`.
- Unrelated running `psikonot_app` and its network/data, all other listed
  containers and volumes, the old local JAR, source files, and the known
  untracked `MultipartParserCleanupTest.java`.

### New resource boundary

If preflight remains safe, create only a unique project named
`a05-eb031a1-20261024`, internal bridge network
`a05-eb031a1-20261024_internal`, and fresh MySQL volume
`a05-eb031a1-20261024_mysql_data`. Pin to the already-present local `mysql:8.0`
image; do not pull images. The MySQL port, if needed for the host-built app,
must bind only to `127.0.0.1:13307`; the application must bind only to
`127.0.0.1:18081`. Do not build or start the repository's default Compose
stack, which publishes ports without loopback binding and enables demo profile
behavior. Do not use the production Compose/Caddy stack or any old volume.

Build the current source JAR offline into the unique ignored directory
`.dxa/a05-isolated-runtime/build-src/target`, not into the pre-existing
`.dxa/a04-kadrom-source/hotelapp/target`. Run with only the explicit dev/test
profile, synthetic ephemeral secrets, no demo seeder, and one new
`example.invalid` account. Never read or print existing `.env` contents,
credentials, database data, tokens, cookies, or real personal data. Do not
invoke mail, SMS, OAuth, payment, cloud-storage, geo, or public-preview paths.

### Rollback and stop conditions

- Stop before resource creation if local MySQL/JDK/Maven dependencies are not
  available offline or if Compose resolves any host port beyond the two
  loopback bindings.
- Stop immediately if the stack tries to use an existing volume/network, an
  existing database/account appears, a migration requests access to existing
  data, or any outbound destination/configuration becomes necessary.
- Keep all created database rows synthetic. After bounded checks, stop the
  Java process and run only `docker compose ... stop` or `down` without `-v`
  for this exact project. Never run `down -v`, `volume rm/prune`, or broad
  cleanup. Verify only the new app/database processes are stopped; retain the
  fresh named DB volume for inspection/recovery and record its name, not its
  contents.
- If any result is inconclusive, report it as inconclusive; no timeout, boot
  failure, or skipped check is a safe result.

At plan-write time, no new runtime container, network, or volume had been
created. This plan precedes resource setup as required by the project data
preservation rule.

## Setup and bounded test result

### Source and build identity

- Source checkout: `.dxa/a04-kadrom-source`, commit
  `eb031a19f9f6b0715d8b302751542f631216cdd5` (`eb031a1`).
- To preserve the checkout's existing Maven target, only `pom.xml` and
  `src/main` were copied to ignored `.dxa/a05-isolated-runtime/build-src`.
  The 280 copied source files matched the source manifest byte-for-byte.
- Offline Maven package completed with exit code 0 and `BUILD SUCCESS`, using
  tests skipped (`-Dmaven.test.skip=true`; no test source was compiled or run).
- Built JAR:
  `.dxa/a05-isolated-runtime/build-src/target/hotel-student-platform-0.0.1-SNAPSHOT.jar`,
  96,725,206 bytes, SHA-256
  `505df33126a2b7c65c9427da9b3679b95646d84db53ac5bf64ad02ff8b6353f7`.
  The pre-existing source checkout JAR remained unchanged (96,721,749 bytes,
  SHA-256 `c8b3d67d6ab2ee60df53dd44bbc03a1755471cd32231930f5cf06a949cbeecb6`).
  The copied JAR contains `AuthController`, `PasswordPolicy`, and
  `spring-security-crypto-7.1.1` classes/dependency.

### Isolated infrastructure and runtime attempts

- Compose preflight resolved exactly project `a05-eb031a1-20261024`, internal
  network `a05-eb031a1-20261024_internal`, fresh volume
  `a05-eb031a1-20261024_mysql_data`, local image `mysql:8.0` with pull disabled,
  and only the planned DB binding `127.0.0.1:13307 -> 3306`.
- The new DB container `a05-eb031a1-20261024-mysql-1` started and reported
  `running|healthy`. Docker inspection confirmed its exact loopback binding,
  fresh named volume, and internal network. A host TCP probe to
  `127.0.0.1:13307` returned false. No port or network policy was changed.
- App launch attempt 1 (PID 27024) exited before Java startup because
  PowerShell split the workspace path containing spaces; Java reported
  `Unable to access jarfile` with the path truncated at the first space. This
  is a launch argument failure, not an application test outcome.
- App launch attempt 2 (PID 27052) started the built JAR with exactly the `dev`
  profile, loopback address `127.0.0.1`, port `18081`, ephemeral JWT secret,
  and explicit blank `RESEND_API_KEY`, disabled SMS, blank OAuth and Cloudinary
  values. Spring Boot logged the active profile as `dev`, then exited during
  Flyway initialization with MySQL `Communications link failure` and
  `Connection refused` to the configured host DB endpoint. It never bound
  port 18081. This is an environment connectivity failure, not an A05 check.
- Source review of `EmailService.send()` confirms it returns before HTTP when
  the Resend API key is blank (`EmailService.java:86–93`); the outbox relay
  calls that method. The registration-triggered mail path was therefore
  configured not to contact Resend. No email, SMS, OAuth, or other external
  integration was invoked.
- No health request, registration, login, or 72/73-byte boundary request was
  sent. The two planned password-boundary checks are **pending**, not passed or
  failed.

### Cleanup and limits

- Stopped only the new container `a05-eb031a1-20261024-mysql-1`; Docker
  reported state `exited`. No `down`, `down -v`, volume removal, or prune ran.
- Verified the new volume `a05-eb031a1-20261024_mysql_data` remains present and
  the network `a05-eb031a1-20261024_internal` remains present with `Internal`
  true. The volume contents were not read.
- No command targeted a pre-existing A04/A05 or unrelated resource; source and
  old JAR identity were preserved. No application process or listener remains.
- Outcome: **inconclusive / blocked by host-to-loopback MySQL connectivity**.
  Do not interpret boot failure or the skipped checks as evidence of safe or
  vulnerable A05 behavior. A future run needs an approved host bridge / DB
  connectivity solution within the same isolation boundary; no such adjustment
  was attempted here.
