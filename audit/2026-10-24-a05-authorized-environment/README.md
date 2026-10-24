# A05 authorized environment availability review

Date: 24 October 2026. Scope: read-only check whether a suitable authorized
environment is currently available for remaining A05 runtime/deployment work.
No service requests, authentication, container changes, volume reads, or tests
were performed.

## Authorization and source identity

The available authorized target is the user's local Kadrom checkout at
`.dxa/a04-kadrom-source`, branch `main`, HEAD
`eb031a19f9f6b0715d8b302751542f631216cdd5`. Its working tree contains one
untracked local test fixture, `hotelapp/src/test/java/com/hotelapp/controller/MultipartParserCleanupTest.java`;
this review did not change it. The repo instructions authorize local testing
on the user's own application and disposable local/Docker labs, while excluding
public preview/production targets absent separate authorization. The source
repo README says there is no live backend and the public URL is a static UI
preview (`.dxa/a04-kadrom-source/README.md:280-281`).

## Read-only environment inventory

Docker metadata was inspected read-only after the sandbox denied access to the
Docker API. The successful elevated query listed existing containers, images,
networks and volume names; it did not start, stop, create, delete, inspect
contents of, or connect to a service.

Current A05-named application containers are not running:

| Container group | Observed state |
|---|---|
| `a05-kadrom-effective-20261022` backend and MySQL | `Created` (never shown running) |
| `a05-kadrom-effective-20261022b` backend / MySQL | `Exited (143)` / `Exited (0)` |
| `a05-kadrom-method-20261022c` backend / MySQL | `Exited (143)` / `Exited (0)` |

The A05 Compose project networks and named MySQL volumes remain present. Their
contents were not read. Earlier [runtime-preflight evidence](../2026-10-22-a05-runtime-preflight/README.md)
also records stopped A05 diagnostics and retained volumes. No existing A05
resource was changed or started. There are local images carrying historical
Kadrom/A04/A05-related tags, but the inventory contains no current active
container whose source/build identity matches `eb031a1`.

Docker also listed a similarly named Compose project whose source path is
outside this authorized checkout; it was exited and its source/image identity
was not validated. It is excluded as a candidate environment.

The authorized source checkout contains development Compose configuration
with MySQL, backend and frontend (`.dxa/a04-kadrom-source/docker-compose.yml:8-27,74-97`)
and a production-shaped Compose definition with backend build and Caddy
(`.dxa/a04-kadrom-source/deploy/prod/docker-compose.prod.yml:19-39,112-144`).
These are configuration files, not evidence that those effective settings are
running. No active Kadrom Caddy/reverse-proxy or WAF configuration was
identified in the runtime inventory. The local `hotelapp/target` directory
contains `hotel-student-platform-0.0.1-SNAPSHOT.jar` (96,721,749 bytes,
last-written 23 October 2026 11:54). Current source commit `eb031a1` is dated
23 October 15:33 +03:00 and includes later service/entity changes, so the
existing JAR is earlier than the reviewed source and is not established as a
current-source deployment artifact.

No account or database contents were inspected. No `.env` file contents,
credentials, cookies, or personal data were read or printed. No external URL,
public preview, production host, or local HTTP service was contacted.

## What the available environment can support

**Available now:** source/path review, dependency-tree review, and
source-bound component/embedded-connector regression work. The current-source
bounded malformed multipart fixture already passed separately at
`eb031a1` (one test; the fixture uses the checked-in controller/handler and
embedded Tomcat/Spring resolver). These checks do not require or establish a
deployed application or proxy.

**Not currently available:** a running application built from `eb031a1`, a
production dependency/artifact identity, active authentication/session path,
effective reverse-proxy/WAF settings, or a deployment configuration against
which to make deployment-wide A05 claims. The current test account state is
unknown because databases were deliberately not queried.

A future isolated local product run could be built from the authorized current
source using synthetic accounts and a newly named disposable Compose project
with a fresh, separate database volume. That would test only that local
configuration; it would not validate production or a reverse proxy unless
those effective settings are separately supplied and explicitly authorized.
Existing A05/A04 MySQL volumes must remain untouched. This assignment did not
create that environment.

## Conclusion

There is **no currently running, current-source A05 runtime/deployment
environment**. The existing authorized checkout is sufficient for another
bounded source/fixture task; it is not sufficient evidence for the remaining
deployment, proxy/WAF, production-graph, authenticated-runtime, or stress
claims. The proper next boundary is either (a) keep A05 at the current
source/fixture scope, or (b) separately authorize and prepare a fresh,
synthetic, isolated local deployment. No production access or external target
authorization was inferred. No tests were rerun in this read-only review.
