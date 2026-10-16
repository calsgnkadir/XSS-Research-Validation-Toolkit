# Defense notes: controls tied to the failure boundary

These are general remediation patterns for the classes discussed in the
historical Juice Shop writeups. They are not claims that every control was
tested against the pictured application. The screenshots show limited UI or
request/response observations; see the [evidence inventory](../audit/2026-10-17-k-evidence/README.md)
for the artifacts that are absent.

## Cross-cutting XSS controls

- Render untrusted values as text by default. If rich HTML is a product
  requirement, use a maintained HTML parser/sanitizer with an explicit
  allowlist and test it against the actual output context.
- Encode for the destination context at the point of output. HTML text,
  attributes, JavaScript, CSS, and URL components have different rules.
- Treat Content Security Policy as defense in depth. A policy can reduce the
  impact of some script injection paths; it does not make unsafe rendering safe
  or prove that a particular input path is blocked.
- `HttpOnly` limits direct script access to a cookie value. It does not stop
  same-origin script from making authenticated requests, and it does not replace
  output encoding or authorization checks.
- Do not generalize from one sanitizer observation or recursive filtering
  example. Repeated deletion can change input structure; a parser-based policy
  with regression tests is preferable to a hand-maintained blocklist.

## Per-class guidance and evidence boundary

| Class | Recommended control | What this repository currently supports |
|---|---|---|
| DOM XSS | Keep framework escaping enabled; avoid trust-bypass APIs for untrusted data. If markup is required, sanitize with a maintained parser before the HTML sink. | The writeup describes a DOM path; the screenshots here do not show the source-to-sink path or a browser execution proof. |
| Stored XSS / header input | Treat request headers as untrusted. Validate expected format and encode at the rendering sink. | Screenshots 03 and 06 show a header value reflected in JSON. Screenshots 07–08 show two empty response values. They do not establish HTML execution, a complete filter, or an exhaustive bypass test. |
| Stored XSS / API input | Validate on the server and encode output in every consuming interface, including administrative views. | A recommendation only; no evidence package here establishes an admin-view execution or role boundary. |
| CSP-related behavior | Keep security policy configuration server-controlled; avoid reflecting user input into policy headers. Use CSP as an additional restriction and test response headers plus browser behavior. | Screenshot 02 shows profile form fields only. No CSP header or bypass result is captured in this image set. |
| SQL injection | Use parameterized queries or prepared statements; allowlist any query structure that cannot be bound and apply least privilege to the database identity. | The writeup records an author-reported local challenge result. The exact request/response and retest artifacts are absent from the current evidence set; UNION/blind sections are explanatory theory. |
| JWT validation | Pin accepted algorithms in server configuration; bind keys to the expected algorithm and validate issuer, audience, and time claims. | The writeup records an author-reported `alg:none` challenge result. No matching request/response artifact is present; the RS256-to-HS256 attempt is explicitly recorded as unsolved. |
| BOLA / IDOR | Authorize each object operation against the authenticated principal, preferably by scoping the data lookup to that principal. Test with two accounts and the same object identifier. | The writeup records an author-reported basket observation. A paired two-account request/response artifact is absent, so the cross-user authorization boundary is not independently demonstrated here. |
| Archive extraction | Canonicalize paths and enforce extraction containment; reject entries that escape the destination. Sanitize any subsequently rendered content separately. | General guidance only; no extraction test artifact is part of this K evidence set. |

## Review checklist for a fix

1. Identify the attacker-controlled source and the exact parser/rendering or
   authorization decision it reaches.
2. Apply the control at that boundary, not only at input validation.
3. Preserve a positive reproduction and a negative/fixed control with the same
   input where feasible.
4. Record product/version, role, request/response, environment, and proof type;
   mask credentials before creating a shareable copy.
5. Keep reflection, callback, browser execution, and vulnerability triage as
   separate conclusions.

This document gives remediation advice; it does not claim the historical target
was retested or fixed. Related roadmap work: C07, C08, C12, K02–K04, and P01.

## Technical references checked 17 October 2026

- [OWASP Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html) — context-specific output encoding, sanitization, CSP as defense in depth, and cookie attributes as impact limitation.
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) — prepared statements and parameterized queries.
- [OWASP JSON Web Token Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_Cheat_Sheet.html) — allowlisted algorithm/key binding.
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) — authentication is distinct from authorization and object-level checks need application context.
