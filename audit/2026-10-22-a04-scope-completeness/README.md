# R7 / A04 Kadrom same-role scope completeness — 22 October 2026

## Assignment and limits

This is a read-only source/test inventory for the user-selected Kadrom local
product scope and two-account authorization-boundary objective. Kadrom is pinned
to `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`. The toolkit repository started
at `a20a281c898b430861b9f0539fee444efe0c5965`; its unrelated, pre-existing A05
and roadmap edits were preserved. Only this audit file was added. No product
service, endpoint, Docker command, or test was run; no product data was changed.

The assignment ran as temporary collaboration worker `/root/a04_scope_completeness`.
The current collaboration call did not select or load a native TOML custom-agent
role, so this is not recorded as a native specialist invocation. This follows
the distinction in [AGENT-WORKFLOW](../../docs/AGENT-WORKFLOW.md).

## Previously recorded runtime evidence

The existing [A04 runtime audit](../2026-10-21-a04-same-role-runtime/README.md)
records six GET checks against the three candidate work-session routes below,
using two synthetic candidate accounts and a positive session row associated
with candidate 1. Candidate 1 received its own record; candidate 2 received an
empty result/no content. All six route/account oracles matched in that isolated
local run. This audit did not repeat those requests and does not independently
verify that runtime result.

The earlier [list/role audit](../2026-10-21-a04-kadrom/README.md) records
candidate and business-owner application-list checks: each role received its
own list, cross-role requests returned 403, and unauthenticated requests
returned 401. That is useful role-gate and collection-scope evidence, but the
two accounts have different roles and the routes are not object-ID reads.

## Source review: what the checks cover

At the pinned source, `WorkSessionController.java:25-31` applies a
`CANDIDATE` class-level guard. Its three read routes are:

| Route | Controller evidence | Ownership behavior in service |
|---|---|---|
| `GET /api/candidate/work-sessions/{applicationId}/active` | `WorkSessionController.java:55-62` | `WorkSessionService.java:135-142` loads the open session for that application and returns it only if its application candidate ID equals the authenticated candidate ID. |
| `GET /api/candidate/work-sessions/active-batch?ids=...` | `WorkSessionController.java:69-82` | Calls the same `getActiveSession(candidateId, appId)` filter for each requested ID and omits null results. |
| `GET /api/candidate/work-sessions/{applicationId}` | `WorkSessionController.java:85-91` | `WorkSessionService.java:144-149` lists sessions for the application, then filters each by the authenticated candidate ID. |

Consequently, the recorded two-candidate checks do directly address same-role,
ID-selected ownership for these three work-session GET paths, including the
batch variant. They support only the tested route/data fixture behavior for
that pinned local run. They do not cover every candidate-owned object, other
roles, or the whole application.

The application-list checks cover a different control: the role-specific
collection routes at `ApplicationController.java:45-54,91-102`. Their source
queries are owner-scoped (`ApplicationRepository.java:192-224`, as recorded in
the prior A04 audit), but collection scoping and cross-role rejection do not
show what happens when another account with the *same* role supplies an object
ID.

## Other source-level ownership/participant GET paths

The source exposes these additional ID-addressed reads where same-role
cross-account comparison is meaningful. These are source leads for coverage,
not vulnerability indications.

| Read path | Source behavior and evidence | Existing A04 evidence coverage |
|---|---|---|
| `GET /api/business/listings/{listingId}/attendance` | `CheckInController.java:47-56` requires `BUSINESS_OWNER`; `CheckInService.java:215-218,287-294` resolves the listing and checks its business owner's ID against the authenticated owner. | Not exercised in either prior A04 runtime audit. The prior accounts were one candidate and one owner for role-list checks; the work-session run used two candidates. Existing service unit tests for attendance logic are not an HTTP or two-owner authorization comparison. |
| `GET /api/business/listings/{listingId}/roster` | `RosterController.java:33-43` requires `BUSINESS_OWNER`; `RosterService.java:67-75` checks the listing's business owner ID before producing the roster. | Not exercised in the A04 runtime audits. `RosterServiceTest` covers roster content logic, not an authenticated second-owner GET boundary. |
| `GET /api/messages/conversations/{conversationId}/messages` | `MessageController.java:80-89`; `MessageService.java:178-180,592-600` routes through `getConversationForUser`, which is participant-based. | Not a same-role owner check in the narrow sense, but relevant to the user's authorization-boundary goal. `MessageFlowIT.java:164-169` records a third candidate denied access to a conversation; the test gives a useful outsider control but is not the A04 local runtime run or a second same-role product comparison. |
| `GET /api/messages/conversations/{conversationId}/messages/{messageId}/attachment` | `MessageController.java:35-51`; `MessageService.java:284-291` first requires conversation participation and then matches the message to that conversation. | `PrivateAttachmentHttpTest.java:27-47` covers anonymous rejection, a stranger candidate's 403, and access by the two actual conversation members. This is existing integration-fixture evidence for its specific mocked-storage route, but not the A04 lab run and not an unrelated same-role owner comparison. |

Other ID-shaped reads found in the controller inventory are intentionally
public/resource reads or use their own relationship rules, so they are not
counted as missing owner-ID checks here: for example,
`JobListingController.java:146-160` reads a listing by ID, and
`BusinessController.java:43-66` reads public business details/media by ID.
`CandidateController.java:137-145` exposes a public candidate profile subject
to the service's application relationship. They may merit separate privacy or
policy review, but source inventory alone does not establish a security defect.

Two other ID-shaped GETs have explicit relationship semantics rather than
resource ownership: `PresenceController.java:37-46` accepts `/last-seen/{userId}`
but returns live/last-seen data only when `PresenceService.java:126-128` says
the viewer and target are conversation counterparts without a block; otherwise
the response is the intentionally indistinguishable offline/no-last-seen shape.
`FavoriteController.java:59-65` checks whether the authenticated business
owner favorited the supplied candidate ID, so the queried relation is the
caller's own favorite state, not the candidate's private record. These paths
are outside the listed owner-scoped attendance/roster comparison and were not
tested in the prior A04 runtime audits.

## Existing test/fixture inventory

- `WorkSessionShiftTest.java` is the work-session-named test class in the
  repository test tree; it covers shift/time logic. Source search found no
  existing controller/integration test for any of the three work-session GET
  routes. The six GET results above come from the separate A04 runtime audit,
  not from that test class or a newly run suite.
- `ApplicationFlowIT.java` covers application creation/flow and reads a public
  listing for fixture setup; it does not exercise the candidate/business
  application-list ownership boundary. `CandidateBlockFlowIT.java:76-80`
  reads the candidate's own application list as part of a block-flow fixture,
  but it is not a two-candidate list comparison. No matching business-list GET
  boundary assertion was found in the test tree.
- `RosterServiceTest.java` and `CheckInServiceTest.java` test service-level
  roster/attendance behavior. They do not invoke the corresponding controller
  with two business-owner principals.
- `MessageFlowIT.java` and `PrivateAttachmentHttpTest.java` contain the
  participant/outsider cases summarized above. Their fixtures show test
  coverage for those message-specific checks; they are not evidence that
  unrelated account-owned routes have been covered.

This was source/test inspection only. No suite was run, so no new test pass,
failure, timeout, or skip is claimed.

## Assessment and recommendation (R7/A04)

The existing A04 evidence is sufficient to describe two bounded results:

1. Role separation and own-list behavior for the candidate/business-owner
   application-list routes in the recorded local run.
2. Same-role candidate ownership behavior for the three work-session GET routes
   in the recorded disposable local run.

It is not product-wide coverage of the selected two-account authorization
objective. The clearest remaining same-role ID/ownership GET coverage gap in the
reviewed source is business-owner access to another owner's
`attendance`/`roster` for an ID-addressed listing. If A04 is intended to claim
broader owner-boundary coverage, the next smallest read-only local comparison
would use two synthetic business owners and an existing listing belonging to
owner 1, with owner 1 as positive control and owner 2 as the cross-owner
negative control for those two GET routes. Preserve the existing-volume safety
constraints from the A04 startup/runtime audits; no data or service was changed
for this source review.

Recommendation: keep A04/R7 open for bounded scope completeness, or explicitly
record A04 as a narrow acceptance limited to the application lists and the
three work-session GETs. Do not expand `no-candidate-observed` beyond the exact
routes and synthetic local data already tested. A05 known-record work and the
broader R7 research status are separate acceptance questions; this audit makes
no advisory/CVE claim.
