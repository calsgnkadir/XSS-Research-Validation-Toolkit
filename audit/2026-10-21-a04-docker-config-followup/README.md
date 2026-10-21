# A04 stopped-container and effective Compose review — 21 October 2026

## Scope

Read-only continuation for R7/A04, limited to the user's Kadrom local lab and
the two existing synthetic candidate accounts. Product source remains pinned
to `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. No services or containers were
started/stopped/created, no HTTP requests were sent, and no volume, account,
source, or application data was changed. No build, migration, seeding, test,
or Git operation was performed.

The sandbox initially denied access to the Docker named pipe. After the
read-only request was authorized, the filtered inspection completed. An
initial `docker inspect --format` attempt had a malformed Go-template quoting
error and exposed no inspect data; it was corrected once. The successful
inspection printed only container name/state/labels, port bindings, mount
metadata, and attached network names. It did not print environment variables,
entrypoint/command values, or full inspect JSON. The Compose JSON was handled in
memory and only the requested ports, network names/internal flag, volume
names/mount targets, and entrypoint/command-presence booleans were emitted.

## Results

The union of containers matching the Compose project label or the named
database volume contained two records:

| Container | State | Saved host port bindings | Mount | Configured network |
|---|---|---|---|---|
| `a04-kadrom-20261021-mysql-1` | `exited` | none (`{}`) | named volume `a04-kadrom-20261021_mysql_data` to `/var/lib/mysql`, read/write | `a04-kadrom-20261021_internal` |
| `a04-kadrom-20261021-backend-1` | `exited` | `127.0.0.1:18081` to container port `8080` | none | `a04-kadrom-20261021_internal` |

No frontend container matched either filter. The stopped containers' Compose
labels identify the expected project and the base Compose file plus the
toolkit override. The saved database mount confirms the named volume remains
attached to the stopped MySQL container; the volume was not modified. The
network object had previously been inspected as `Internal: true` with no
running attachments. Stopped containers cannot have active network attachments
or listening host ports; the table records their saved configuration only.

The effective `docker compose -f ...docker-compose.yml -f
...a04-kadrom-compose.override.yml config --format json` was evaluated. Its
filtered output showed:

- `backend`: host `127.0.0.1`, published port `18081`, target `8080`;
- `mysql`: no published ports; `mysql_data` mounted at `/var/lib/mysql`;
- `frontend`: no published ports;
- default network: named `a04-kadrom-20261021_internal`, `internal=true`;
- volume: named `a04-kadrom-20261021_mysql_data`.

The result is consistent with the intended local-only port/network boundary in
the effective configuration and the stopped backend/MySQL container records.
This does not establish a live listening service or runtime behavior.

## Gate and remaining checks

**Same-role HTTP check: not run.** The backend and MySQL containers are both
stopped. No requests were sent because the task forbids starting services and
there is no running application to receive them. The running-only network
attachment and live host-port state therefore remain absent. No frontend
container is present; whether it is needed for the direct backend API check is
not relevant to the required two-account GET proof.

The safety configuration is now supported by both effective Compose output
and saved container configuration, while current runtime availability is not.
To produce the requested same-role evidence, a separately authorized lab
startup and health check would still be required before any GET request; this
agent did not perform that step. A04 and R7 remain open. No vulnerability
candidate was observed because the work-session endpoints were not contacted;
the earlier `no-candidate-observed` result remains limited to its prior tested
list/role routes.
