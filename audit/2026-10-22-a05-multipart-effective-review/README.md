# R7 / A05 — multipart effective-runtime configuration review

**Date:** 2026-10-22
**Review type:** bounded read-only runtime availability check; no effective runtime configuration retrieved
**Toolkit source:** `e34a4aad1cdd5e2e2054a616b888525bd8d8bb4c` (`main`)
**Product source:** `.dxa/a04-kadrom-source`, pinned at `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`
**Roadmap:** R7 / A05

## Scope, role, and method

The assigned scope was to inspect the pinned product source/deployment configuration and, only if an instance was already running, read its effective multipart/Tomcat settings, part-count behavior, temporary directory, and cleanup behavior. Building, testing, starting a service/container, sending HTTP, changing the product checkout/dependencies, and reading user-file contents were out of scope. No such actions were taken.

The coordinator assigned this read-only task through `collaboration.spawn_agent` with `agent_type=storage_docker_specialist` (`/root/multipart_effective`). The coordinator read the corresponding TOML role definition before assignment; runtime loading of that TOML was not independently verifiable. The available tool surface permitted workspace command execution and creation of the assigned toolkit audit file; it did not provide access to the Docker engine. No write was attempted in the Kadrom checkout.

Read-only checks:

| Check | Command/action | Result |
|---|---|---|
| Toolkit identity | `git rev-parse --show-toplevel`, `git branch --show-current`, `git remote -v`, `git status --short`, `git rev-parse HEAD` | Root is the toolkit checkout, branch `main`, HEAD is the assigned toolkit commit. Status showed no tracked/untracked entries; Git emitted only a user global-ignore access warning. No fetch was performed in this bounded assignment. |
| Product identity | `git -C .dxa/a04-kadrom-source rev-parse HEAD`; `git -C .dxa/a04-kadrom-source status --short` | HEAD matches pinned product commit; status showed no entries. Git emitted the same global-ignore warning. |
| Existing containers | `docker ps --format "{{.Names}} {{.Status}} {{.Ports}}"` | Could not contact Docker API: Docker config access was denied and `//./pipe/docker_engine` was absent. This is an environment/access failure, not evidence that no containers exist. No container was started or inspected. |
| Coordinator Docker check | Read-only `docker ps --all --format "{{.Names}} {{.Status}} {{.Ports}}"` with approved escalation | Docker reported that `npipe:////./pipe/dockerDesktopLinuxEngine` was absent and the daemon could not be reached. This confirms Docker runtime was unavailable to this check; it does not reveal the daemon's container inventory. |
| Local process/ports | Read-only `Get-Process` filter for `java`, `docker`, `podman`; `Get-NetTCPConnection` listener filter for ports 8080, 8081, and 3306 | No matching process or listener rows were returned. This narrow check does not exclude an app on other ports, under another process name, or in an inaccessible container. |
| Checked-in multipart/Tomcat configuration | `rg -n` over the pinned application YAML, Java sources and checked-in Compose/Fly deployment examples | Multipart endpoints and profile selections were found; no `file-size-threshold`, multipart temp `location`, `maxPartCount`/part-count setting, or Tomcat connector customizer was found in the searched paths. This is source evidence, not effective runtime evidence. |

**Runtime hash:** unavailable. No runtime/container metadata could be read. The product Git commit is the source identity, not a runtime image or deployment hash.

## Source facts and remaining uncertainty

The prior pinned source/configuration review remains the source evidence for the affected dependency versions and upload paths: [multipart/Tomcat configuration preflight](../2026-10-22-a05-multipart-config-review/README.md). In brief, it records Spring MVC 6.1.6 and Tomcat 10.1.20 from the pinned dependency tree; multipart enabled with 20 MB per-file and 25 MB per-request YAML values in `hotelapp/src/main/resources/application.yml:81-85` and `hotelapp/src/main/resources/application-prod.yml:81-85`; and multiple multipart controller routes, including `MessageController.java:104-115`. The preflight also records that service checks occur after multipart parsing.

This assignment did not independently recalculate the prior file hashes or re-read the dependency tree. The pinned commit remained the same. The currently available source search found no checked-in explicit part-count limit, temp directory/threshold, or Tomcat connector customization in the inspected paths. Other external environment variables, JVM arguments, packaged configuration, deployment overrides, proxy settings, or runtime extensions may change the effective behavior.

Expected versus observed:

| Property | Expected from the source-level preflight | Observed in this task |
|---|---|---|
| Spring multipart byte limits | Checked-in YAML says enabled, 20 MB file / 25 MB request | Effective values not read; environment and deployment overrides remain unknown. |
| Tomcat multipart part-count bound | No explicit bound was identified in checked-in configuration | Effective connector default/value not read. |
| Multipart temporary storage path/threshold | No explicit threshold/location was identified in checked-in YAML | JVM temp directory and actual memory/disk behavior not read. |
| Temporary-part cleanup after parse errors | Source preflight says this depends on parser error path, JVM/GC and load | No request was sent and no runtime/file-system observation was made; cleanup behavior is unverified. |
| Existing runtime availability | Inspection can continue only if an instance is already running and readable | Docker daemon unavailable; narrow local process/port check returned no matching row. No local runtime was discoverable through these checks, but container inventory and apps on other ports/processes remain unknown, so effective inspection stopped. |

No malformed or valid upload, size-boundary test, repeated request, parser-error trigger, or disk/resource observation was performed. No data loss or temporary-file leak was reproduced. Potential temporary-file accumulation and request resource consumption remain advisory-specific hypotheses from source/advisory analysis, not observed product behavior. No existing volume was inspected or modified.

## Roadmap disposition

This contributes a bounded runtime-availability result to **R7 / A05**. It does not narrow the effective part-count, temp-directory, or cleanup conditions because no existing application/container runtime was accessible. The earlier source/configuration triage remains unchanged: affected-version multipart paths exist, while the applicable Tomcat conditions and Spring intermediary condition remain unresolved. A05 and R7 remain open. No vulnerability, DoS, cleanup failure, remediation, or disclosure is claimed.

Smallest useful next step, if A05 continues: when Kadrom is already running in an explicitly authorized local environment, obtain a read-only effective-property/connector/JVM-temp snapshot and deployment image/source identity without sending a request. This will not by itself prove cleanup behavior after parser errors.
