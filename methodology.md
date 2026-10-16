# XSS assessment method: input, transformations, sinks and evidence

This method is for the project's own applications and explicitly authorized,
disposable local labs. A URL in a note or old report is not authorization.
Record the exact application/version, role, route, test window, tool version and
source revision. Do not use production data or place credentials, cookies or raw
request bodies in shareable evidence.

## Model the path, not just the string

For each input, trace:

1. **Source:** where the value originates (request parameter, stored field,
   header, browser location, message event, storage, or other input).
2. **Transformations:** decoding, validation, encoding, sanitization,
   concatenation, serialization, framework rendering, and any later rewriting.
3. **Sink:** the concrete parser or browser API that consumes it, including the
   output context (HTML text, attribute, URL, script, CSS, JSON, or DOM API).
4. **Reachability and controls:** which role, route, state, and interaction make
   the path reachable; what policy or sanitizer applies; and what negative
   control should remain inert.

Finding a source and a sink independently does not show a flow between them.
A static match or taint heuristic is a review candidate; inspect the exact path
and account for false positives and false negatives. A sanitizer's name, a
framework label, a CSP header, or the absence of a finding does not establish
that every path is safe.

## HTTP and browser observations can overlap

“Network” and “DOM” are not mutually exclusive categories. A reflected or
stored value may travel over HTTP and later be parsed into a DOM sink. A
client-side source such as `location.hash` may be read without that fragment
being present in the initial HTTP request, then be transformed or sent in a
later request. Record the whole path rather than classifying a bug from the
presence or absence of a network entry.

Use an inert, unique marker first to locate the input and inspect the response
and rendered DOM. Determine whether it is encoded, reflected in JSON/text, or
parsed as markup. A raw string in an HTTP response is only a reflection
observation. JSON-only and non-HTML reflections are not browser HTML execution;
they may still matter if a client later passes the value to an HTML sink, which
must be separately demonstrated.

For browser behavior, use a disposable authorized fixture and a harmless,
unique canary whose browser observation is bound to that exact submission.
Check the effective Content-Type, parser context, CSP and relevant browser
state. Include a known-negative control (for example, an encoded value or a
non-executable context) and a positive control where practical. A dialog,
console message, sink match, or arbitrary callback is not proof unless it is
causally linked to the submitted canary and expected source/sink/frame.

## Keep evidence levels distinct

The project's finding vocabulary is descriptive, not a monotonic severity
ladder:

| Record | What it supports | What it does not support by itself |
|---|---|---|
| `candidate` / static source-to-sink match | A code location merits review | Runtime reachability, reflection, execution, or a vulnerability |
| `reflection` | The submitted marker was observed in an HTTP response | HTML parsing, browser execution, impact, or exploitability |
| `sink-observed` | A browser/runtime sink observation was recorded | That the submitted canary executed or violated a security boundary |
| `resource-callback` | A request associated with a resource/canary was observed | JavaScript execution, a particular user's visit, or session/role identity |
| `execution-observed` in the separate R3 proof record | The configured browser observed the matching canary in the tested fixture and run | Vulnerability confirmation, authorization impact, general product correctness, or a CVE |
| vulnerability triage | A human assessed context, impact, authorization boundary and alternatives | A general result beyond the tested version, role, route and configuration |

`execution-observed` is not the same as the common Finding v1 `evidence_level`;
the R3 browser-proof record is separate. The current producers do not assert
`execution-confirmed` or a verified user role. Callback events remain separate
from browser JavaScript evidence. See the [evidence contract](tools/dom-xss-analyzer/EVIDENCE-CONTRACT.md),
[HTTP model](tools/dom-xss-analyzer/HTTP-EVIDENCE.md), and
[browser proof scope](tools/dom-xss-analyzer/BROWSER-PROOF.md).

## Test authorization and impact separately

An authenticated request proves only that the tested session was accepted. To
test object authorization, use two controlled accounts and the same known
object: record the owner's expected response, then the other account's actual
response, with a negative control. A same-role cross-account read is horizontal
access; access to an admin-only operation by a lower-privileged role is a
separate vertical test. Neither is established by a changed ID alone.

For a possible XSS, distinguish injection from impact and document who can
submit it, who can view it, the affected browser context, required interaction,
and reachable actions. “By-design”, self-XSS, rejected, and unreviewed are
triage outcomes, not substitutes for recording the observation. Do not claim a
CVE or affected version from similarity of payload shape.

## Report negative results with their limits

A negative result means only that the tested inputs, routes, roles, states,
browser, configuration and time window produced no observed result. Record
coverage boundaries and skipped/error cases. A zero-result scan does not prove
safety or source unreachability. A timeout, missing browser, failed login or
skipped route is incomplete evidence, not a negative finding.

For repeated scans, compare by stable case/attempt/source/sink evidence where
available; row counts alone are not a precision or accuracy metric. Report
tested, completed, skipped, errored and inconclusive cases separately. Preserve
historical reports as historical, and do not present old test counts or tool
labels as current acceptance.

## Reproduction and remediation record

For each accepted local finding, retain a minimal masked request/response or
fixture, exact application version and setup command, source-to-sink path,
expected and observed outcome, canary correlation, negative control, fix diff,
and retest result. Keep credentials, session tokens, personal data, and
unnecessary raw bodies out of the shareable copy. If any element is absent,
state the gap and keep the result at the evidence level actually supported.
