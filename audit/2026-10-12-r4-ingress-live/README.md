# R4 ingress and live product acceptance - accepted locally

Baseline 02e8805, clean main equal origin/main after fetch. Active root
C:\xss\xss-github. User requested fixing Docker ingress and completing live acceptance.

## Ownership and pre-run data/rollback plan

Native Storage /root/r4_ingress_resume owns bludit_ingress.py and local-inspected.yml.
Native QA /root/r4_ingress_qa_resume owns independent adapter/ingress tests.
Coordinator owns adapter integration, bootstrap, docs, live execution and Git.
No more than two specialists run concurrently; no specialist commits/pushes.

Keep Bludit attached solely to a fresh internal network with no host port.
A minimal fixed reverse proxy joins that network and a fresh edge bridge;
only its ephemeral port binds 127.0.0.1. Same previously inspected immutable
local image; no pull/build, existing app attachment, host data mount, persistent
volume, host firewall or Docker daemon changes. Proxy command must not start
Bludit/PHP or support forward proxying. Runtime labels, image, network membership,
mounts and port must match reviewed configuration before HTTP requests.

Application installation and controlled content affect only fresh disposable
writable layers. Rollback removes only this UUID project's two containers and
two networks, never down -v/prune or user volumes. Save sanitized observation
JSON before teardown and update cleanup status afterward. Private inventory of
all existing containers/volumes/networks was saved before work; compare exact
sets after runs. Never publish raw cookies/passwords or private inventory names.

Acceptance requires successful fresh install and explicit login, independent
public raw/escaped browser controls, missing-browser error, mismatch failure,
and cleanup on success and failure. Admin-authored HTML remains by-design,
not a vulnerability/CVE/role-boundary claim. General R4 closure is separate.

## 13 October 2026 local acceptance

The pinned local image runs Bludit solely on a fresh internal Docker network
without a published port. A second container uses only Apache proxy modules,
with a fixed `bludit:80` reverse destination and a loopback ephemeral port.
No PHP module, host mount, persistent volume or image pull was used. Strict
Compose/runtime guards check image, commands, labels, network membership and
port bindings before HTTP. Only Docker's observed default IPv4/IPv6 options
are accepted. Apache syntax and normalized Compose configuration passed.

The combined local regression gate was **335 passed, zero failure/error/skip**,
Python 3.10.11 / Windows. [JUnit](acceptance.xml) and [command, source hashes
and totals](acceptance.json) show sources unchanged throughout.

Three separate fresh UUID projects used installed Chrome 155.0.8059.40 and
pinned local Bludit with embedded version 3.16.2:

- `success`: installer, independent login and authenticated author form passed.
  The public raw administrator content executed its matching CID canary; escaped
  content did not. Both readbacks were HTTP 200. This is **by design**, with no
  vulnerability or privilege-boundary claim.
- `missing-browser`: after real installation and content seeding, the missing
  executable caused `browser/browser-unavailable` and an error result.
- `control-mismatch`: after real browser observation, the validation harness
  deliberately rewrote the positive observation to exercise the failure oracle.
  This is an **injected test**, not a real browser miss. It caused
  `acceptance/control-mismatch` and an error result.

Each run wrote `observations.json` before teardown and cleaned its own project.
Exact private pre/post identity sets of the 15 existing containers, 27 volumes
and 9 networks matched. [Live acceptance and preservation](live-acceptance.json),
[sanitized success](success.json), [missing browser](missing-browser.json) and
[injected mismatch](control-mismatch.json) contain no credentials, cookies,
private inventory or request bodies. Private data remains ignored under `.dxa/`.
Initial network-default, anonymous-login and Markdown-readback failures were
reproduced and fixed. A valid inline Bludit login form still requires separate
explicit login and an authenticated author form. The escaped text control uses
an HTML code block so Markdown preserves the literal underscore payload.

This closes the local standalone R4 product lifecycle/port discovery adapter
acceptance. Benchmark scorer integration, broader R4/R9, role boundaries and
upstream image provenance remain open. Hosted CI tests mocked adapter behavior;
it does not run the local image. Remote delivery is recorded separately.

## GitHub delivery

Implementation commit `e62bf3422456bad2b9f770d0ad4e8a20bc78c76f` was
pushed to `origin/main`; `git ls-remote` matched the local hash and the working
tree was clean. [Workflow 38404107337](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38404107337)
completed successfully, with all three jobs successful. The hosted runner tested
mocked ingress/adapter behavior and existing browser proof; it did not run the
pinned local Bludit Docker image. Artifact contents were not separately inspected
for this run. [Sanitized job metadata](remote-delivery.json).
