# A04 isolated-test inventory — 21 October 2026

## Scope and source identity

This is a read-only testability follow-up for R7/A04. The Kadrom source checkout
at `.dxa/a04-kadrom-source` is pinned to
`ae4aebbf8963f550f6bb7c3465fb1270d677af1c`; its worktree was clean at inspection.
Only the existing synthetic-account ownership question was considered. No
product source, test, configuration, account, database, or container was
changed. Docker was not queried or started. No product HTTP request was sent.

## Test inventory

The relevant application-list route checked in the earlier bounded run is not
an ID-addressed object read. The source does expose three same-role candidate
GET routes in `hotelapp/src/main/java/com/hotelapp/controller/WorkSessionController.java`:

- `GET /{applicationId}/active` at line 56;
- `GET /active-batch` at line 70;
- `GET /{applicationId}` at line 86.

The controller has a candidate-role guard at line 30 and passes the authenticated
principal ID to `getActiveSession` / `listForApplication` (lines 60, 79, 90).
`WorkSessionService.java:135-149` contains the account comparison: active
session results are filtered by the associated application's candidate ID, and
history results are likewise filtered before DTO mapping. This is source
behavior, not runtime HTTP evidence.

The existing tests do not provide a narrowly targeted same-role GET ownership
oracle:

| Test | Isolation | Relevance to A04 |
|---|---|---|
| `service/WorkSessionShiftTest.java:24-28` | JUnit + Mockito mocks; no Spring context, database, Docker, or HTTP client | Tests clock-in/shift behavior, not `getActiveSession`, `listForApplication`, controller authorization, or cross-account GET visibility. |
| `service/NightShiftAndNoShowEntryTest.java:32-60` | JUnit + Mockito mocks; service objects are constructed directly | Tests check-in/clock-in and roster behavior, not the candidate GET ownership routes. |
| `integration/ApplicationFlowIT.java:35-37` | Full Spring context and MockMvc under the `test` profile; test YAML configures H2 in-memory with `create-drop` and disables Flyway (`src/test/resources/application-test.yml:1-17`) | Exercises registration, application creation, and a cross-role POST denial; it does not exercise same-role work-session GET ownership. It is broader than a minimal ownership unit test. |

The service's existing Mockito tests are isolated, but their assertions do not
cover the relevant read methods. Running them would not answer A04, so no test
was run. The broader HTTP integration test is not an equivalent substitute for
the requested two-account same-role comparison. Test configuration alone also
does not establish that a particular test has no external side effects; no
integration suite was started.

## Result and limits

No existing test was both directly relevant to the same-role ownership GETs and
clearly bounded enough to run as a substitute for the blocked lab check. No test
was added or modified. There is no test pass, failure, timeout, or skip to report.
This source/test inventory does not establish runtime behavior or prove safety.
Mocks and in-memory tests cannot replace same-role runtime HTTP proof using the
two existing synthetic accounts and existing application IDs.

A04 and R7 remain open. The next runtime step remains the previously documented
safe lab check after the Docker engine's existing project/network/port/volume
state can be verified; preserve the existing volume and send only bounded GET
requests. See the prior [runtime follow-up](../2026-10-21-a04-runtime-followup/README.md)
and [same-role source review](../2026-10-21-a04-same-role-followup/README.md).
