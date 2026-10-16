# Local Docker lab operation (R4/R9)

These definitions are prerequisites, not evidence of XSS or safe negative controls.
Use only explicitly authorized labs. Review `docker compose config` before startup.
Standard configurations require an already installed, reviewed immutable image via
`DXA_BLUDIT_IMAGE`, `DXA_DVWA_IMAGE`, or `DXA_WEBGOAT_IMAGE`; use a full `sha256:`
image ID or repository digest. No automatic pull, restart or fixed container name.
Published ports bind to loopback only. Version tags alone do not prove provenance.

Before a data-affecting run, record existing containers and volumes read-only and
choose a fresh unique Compose project. Never attach existing project data. The
standard Bludit configuration uses a project-scoped volume: retain it after tests.
Do not use `down -v`, volume pruning, reset/install against an existing site, or
shared host mounts. Rollback means stopping only containers created by this run;
retain existing volumes and record any new volume names for the operator. A
failed setup is an error, never a clean negative benchmark result.

## Readiness boundary

Docker daemon availability only permits Compose preflight/startup. Compose
healthchecks and a reachable loopback URL are infrastructure/liveness signals;
they do not establish that an application is installed, logged in, configured,
or at the intended lesson. The generic benchmark runner reports that HTTP is
reachable while explicitly retaining “application setup and scan oracle not
verified”; this state is not product acceptance. A candidate scan may still
run, but must not be described as a completed application or lesson check.

The disposable Bludit ingress adapter is the only target-specific acceptance
path here: it verifies fresh bootstrap, login, admin-authored raw/escaped
controls and browser observations before it records a pass. DVWA and WebGoat
Compose definitions are infrastructure templates only; they have no
target-specific login/lesson acceptance adapter. The own-hardened targets named
in `bench/targets.json` have no Compose target adapter here. None of those
targets becomes product-ready from daemon health or HTTP reachability alone.

`bludit/local-inspected.yml` is a separate fresh disposable configuration with an
immutable local image and no volumes. On 9 October 2026 a network-disabled,
read-only inspection of this image found `BLUDIT_VERSION=3.16.2` in
`/var/www/html/bl-kernel/boot/init.php` (file SHA256
`8f4f87b049340ead81af2580e35ad84b54171fe73bbf80c05ab515b1cea26d00`).
No site database was present at `bl-content/databases/site.php`. This verifies
the embedded version string, not upstream authenticity or vulnerability status.
The image has no declared volumes. Other machines must obtain/review their own
image; this file deliberately cannot pull it. Its application network is
internal; the fixed ingress proxy publishes an ephemeral HTTP port on
127.0.0.1.

The standalone adapter below owns bootstrap, port discovery, explicit login and
controlled browser evidence for fresh UUID projects. It exports observations
before tearing down its disposable writable layers. The main benchmark runner
still does not consume this product adapter.

## Experimental standalone Bludit adapter (12 October)

`python bench/bludit_adapter.py --output <new-directory> --browser <chrome-path>`
implements a separate disposable lifecycle with pinned image, configuration and
ownership guards, installer/login, public raw/escaped controls and result
validation. It does not change the benchmark runner or its scorer. Its unit
suite runs without Docker or Playwright; its 12 October mock tests were not
live product acceptance.

**Historical 12 October blocker:** an internal-only application container had
no published host port at runtime. The adapter failed closed and cleaned up.
The 13 October ingress acceptance below resolves that local blocker.
[Earlier evidence](../../audit/2026-10-12-r4-product-adapter/README.md).

### 13 October Bludit ingress acceptance

`local-inspected.yml` now runs the pinned application only on an internal
network. A fixed Apache reverse proxy on the same pinned image joins that
network and an edge bridge; only the proxy publishes an ephemeral loopback port.
`bench/bludit_adapter.py` verifies topology, container commands, image,
ownership, network members and mapping before HTTP. Run on a machine with the
locally reviewed image and Chrome:

```powershell
py -3.10 bench/bludit_adapter.py --output .dxa/my-new-bludit-run --browser "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

The output directory must be new. Observations are written before removing the
UUID project's containers and networks without `down -v`. Raw/escaped controls
are administrator-authored and by design.
[Local acceptance and limits](../../audit/2026-10-12-r4-ingress-live/README.md).
The benchmark scorer still does not consume this standalone adapter.
