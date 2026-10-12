# R4 — pinned local Bludit product adapter (experimental; live acceptance blocked)

Baseline: d151a8a, clean main equal origin/main after fetch. Active repository
C:\xss\xss-github; OneDrive copy is not used for development.

User authorized this local/Docker task with two specialists and coordinator.
Engine /root/r4_product_adapter owns bench/bludit_adapter.py; QA
/root/r4_product_qa owns bench/test_bludit_adapter.py. Coordinator owns
integration, lab execution, Compose/docs/CI and acceptance evidence. Two native
agents resumed after an initial usage-limit interruption. No independent Git
operations by specialists.

## Data impact and rollback before lab startup

Only the existing inspected image sha256:7eb101cdb879f549d6e0088b13c07afa231292e9e15eeff741491abeafb3ebb8
is used. No pull/build, host mount, persistent volume, or existing application
instance. A fresh UUID Compose project publishes an ephemeral port on 127.0.0.1
and uses an internal network. Installer/login/content writes affect only its
new disposable container writable layer. Rollback stops/removes only resources
created by that project, without down -v, pruning, or any user volume deletion.
Observations are retained in memory and the sanitized report is written after
cleanup; durable export before teardown still needs live verification. Existing 15 containers and 27
volumes were inventoried privately before execution; public evidence will
record preservation checks rather than names/private configuration.

## Acceptance scope

Pinned image and fresh ownership checks; dynamic port validation against own
container inspection; fresh installer and explicit login; controlled raw HTML
and escaped-content browser canaries; structured errors and teardown.
Administrator HTML authoring is by design: execution observations are not a
vulnerability, role-boundary or CVE claim. This is a bounded product adapter,
not closure of every R4/R9 acceptance item. Existing loopback proof schema and
legacy candidate scoring remain separate.

Source inspection used a disposable read-only network-disabled container to
extract installer/login/content source into ignored .dxa/bludit-source. An
initial shell grep quoting error produced no valid source finding; subsequent
argv-based tar extraction succeeded. No actual app lab has been accepted yet.


## Actual results and coordinator review

Combined gate: **268 passed in 26.46 s**, zero failures/errors/skips. This
includes 83 independent adapter tests; counts are not additive. Exact command,
Python version, tested source hashes and unchanged-source check are in
[acceptance.json](acceptance.json), with [JUnit](acceptance.xml).
CI includes only the mocked adapter suite; the locally installed image is not
available to hosted runners. No live product acceptance is implied.

Coordinator reviewed the partial Engine implementation and independent QA
oracles. QA reproduced seven proof identity/status/privacy defects; coordinator
added identity validation, immutable expected-case copies, whitelisted report
fields and recomputed matches. Explicit process/browser timeout categories and
safe normalized Compose defaults are covered. Engine's native turn stopped at
an automated cybersecurity check; it was not retried or counted completed.
QA finished. No agents or background tasks remain active.

First CLI attempt encountered a file-encoding error before Docker; corrected.
First recorded run stopped in preflight on empty normalized IPAM; corrected to
accept only empty defaults. Three actual project startups then failed safely:
requested HostIp 127.0.0.1 / ephemeral port, but runtime `80/tcp: []`. The final
repeat waited three seconds before inspection and reproduced it. Each reported
cleanup passed. See the four individual JSON reports. Installer/login/browser
were never reached in these real runs; mock success is not product acceptance.

Private baseline comparison: **15/15 containers, 27/27 volumes**, exact identity
and name sets equal, not just counts. No existing data was attached or removed.
Compose configuration, host firewall and daemon settings were not weakened.
The result is an experimental fail-closed adapter, not a working product demo.

## Remaining work

Review an ingress design compatible with Docker Desktop while retaining app
network isolation, then rerun fresh installation, explicit login, raw/escaped
public browser observations and missing-browser cleanup. Do not bypass the
runtime port guard. Current adapter is separate from benchmark scoring and the
R1 evidence schema. General R4, role coverage and hard whole-lifecycle timeout
acceptance remain open. The raw administrator content control is by design.

[Docker networking documentation](https://docs.docker.com/desktop/features/networking/networking-how-tos/)
explains Desktop host access through published ports; the missing binding above
is a local observation, not a claim about every Docker version or platform.


An independent [report in Moby's upstream repository](https://github.com/moby/moby/discussions/53256)
describes missing published ports on internal-only networks in Engine 29.6.2.
It corroborates the symptom; it is not a maintainer-confirmed diagnosis of this
machine. A loopback-only ingress proxy on a separate edge network is a design
candidate to review, not implemented or accepted here. Attaching the application
itself to an unrestricted network would change the current isolation contract.


## Remote checkpoint

Implementation commit `db9602783068faa10373d15485da7b8f36eb7ed3` was pushed;
`git ls-remote` matched. CI [38302697303](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38302697303)
and all three jobs succeeded, including the new mocked benchmark adapter tests.
[Sanitized job/step metadata](remote-delivery.json). Artifact contents were not
downloaded for this run. CI did not run the local Bludit image. These delivery
notes are a subsequent documentation commit; they do not alter tested code.
