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

`bludit/local-inspected.yml` is a separate fresh disposable configuration with an
immutable local image and no volumes. On 9 October 2026 a network-disabled,
read-only inspection of this image found `BLUDIT_VERSION=3.16.2` in
`/var/www/html/bl-kernel/boot/init.php` (file SHA256
`8f4f87b049340ead81af2580e35ad84b54171fe73bbf80c05ab515b1cea26d00`).
No site database was present at `bl-content/databases/site.php`. This verifies
the embedded version string, not upstream authenticity or vulnerability status.
The image has no declared volumes. Other machines must obtain/review their own
image; this file deliberately cannot pull it. Its internal network blocks
ordinary container egress; the published HTTP port is ephemeral on 127.0.0.1.

Start only under a fresh project, discover its mapped port with Compose `port
bludit 80`, and complete installation in that fresh instance. Bootstrap/login,
fixture contents and expected evidence must be independently verified before
benchmark acceptance. Removing this disposable container loses its writable
layer: export required evidence first. Never substitute an existing user site.

The current benchmark runner requires a known published TCP port matching its
readiness URL before startup. It therefore cannot directly consume the ephemeral
port in `local-inspected.yml`; a reviewed bootstrap/port-discovery adapter remains
required. Compose configuration validation alone does not satisfy that acceptance.


## Experimental standalone Bludit adapter (12 October)

`python bench/bludit_adapter.py --output <new-directory> --browser <chrome-path>`
implements a separate disposable lifecycle with pinned image, configuration and
ownership guards, installer/login, public raw/escaped controls and result
validation. It does not change the benchmark runner or its scorer. Its unit
suite runs without Docker or Playwright; it is not live product acceptance.

**Live acceptance is currently blocked on this Docker Desktop environment.**
With the reviewed internal network, runtime inspection returned `80/tcp: []`
despite the requested ephemeral loopback binding. The adapter correctly errors
and tears down its own project. Rechecking after three seconds gave the same
result. Do not bypass the mapping guard or use an existing application instance.
The installer/login/browser stages have not yet been reached in the real lab.
A reviewed ingress design compatible with internal networking is the next step;
no host firewall, existing network or daemon configuration was changed.
See [evidence and remaining work](../../audit/2026-10-12-r4-product-adapter/README.md).
