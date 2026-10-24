> **Historical lab account — proof limit.** The text reports changing basket IDs while authenticated and receiving different `UserId` values, but the retained evidence does not include a masked A/B account-control pair or request/response set proving which object belonged to which user. The historical BOLA claim is therefore not independently verified here. Vertical privilege escalation was not demonstrated. See [C05](../ROADMAP.md) and the [audit](../audit/2026-09-28/DENETIM-RAPORU-TR.md).

> **Bounded local repetition — 19 October 2026.** On an isolated OWASP Juice Shop
> 20.2.0 image, two newly registered local accounts were identified separately.
> Account A read its own basket and account B's basket with the same A session;
> the latter response matched B's owner ID and included a product B had added.
> The same request without a session returned 401. The versioned request/
> response record and source hash are in the
> [K03 audit](../audit/2026-10-19-k03-loopback-reproduction/README.md). This
> is a new controlled repeat, not proof of the older basket IDs or session. A
> further pinned-image replay is documented in the
> [24 October K03 audit](../audit/2026-10-24-k03-independent-retest/README.md).

# IDOR / BOLA: the server checks *who you are*, not *what's yours*

> **TL;DR** — Most injection bugs are about a value being *parsed* in the wrong
> context. Access-control bugs are different: nothing is parsed, nothing executes.
> Authentication establishes identity; authorization decides whether that caller
> may access the requested object or action. If an object is fetched by an `id`
> without an applicable access check, a caller may reach data they are not
> allowed to read. That can be an **Insecure Direct Object Reference (IDOR)** or
> **Broken Object-Level Authorization (BOLA)**. The required policy depends on
> the resource and caller.

This is a general access-control model; it does not establish the behavior of
every ID-keyed route. Every other writeup in this repo turns on a value being interpreted as code —
markup in HTML, input in SQL, a claim in a JWT. This one has no payload at all.
The request can be well-formed and authenticated while still asking for an object
the caller is not entitled to. It's the
last step of the repo's [`methodology.md`](../methodology.md) — **AUTHZ: was the
privilege used even required?** — and on modern targets it lands far more often
because client-side hardening (auto-escaping, CSP, Trusted Types) does nothing
for it: authorization is enforced by application and server-side policy.

## The one idea: authentication ≠ authorization

Two different questions, and apps routinely answer only the first:

- **Authentication** — *who are you?* Proven by a session token / login. The server
  checks this well.
- **Authorization** — *are you allowed to touch **this** object?* Proven by an
  ownership/role check on the specific resource. This is the one that gets skipped.

A valid token means the request is *from a real user*. It says **nothing** about
whether *this* user owns *that* record. When the code treats "logged in" as
"allowed," every object becomes reachable by anyone with an account.

## The finding: Juice Shop's basket (`/rest/basket/{id}`)

The historical assessment describes this as **Finding #7**, exercised in Burp
by editing the ID. The transcript below is a narrative summary, not a retained
raw request/response pair:

```
1. Sent my own request  GET /rest/basket/1   → Repeater
2. Changed the id:       GET /rest/basket/2
                         GET /rest/basket/3
                         GET /rest/basket/4
3. Each returned 200 OK — a different UserId each time.
```

The historical report said a token returned basket records with different
`UserId` values and that the *View Basket* challenge completed. Those older
requests do not identify each object's owner or preserve an A/B control pair,
so that historical claim remains unverified. Separately, the bounded local
replay linked above used two synthetic accounts: account A read its own basket
and B's known basket with the same A session; the foreign response matched B's
owner ID and seeded product, while a no-session control returned 401. This
supports horizontal cross-account access for that pinned lab route and run. It
does not establish vertical privilege escalation or behavior on other routes.

## Why this ships so easily

- **The id is right there in the URL.** Building `GET /rest/basket/:id` and returning
  `Basket.findByPk(id)` reads as obviously correct — the ownership clause is a line
  you have to *remember to add*, and its absence looks like nothing.
- **"Authenticated" feels like "safe."** The route is behind a login wall, so it
  *feels* protected. The wall proves identity, not entitlement.
- **It's invisible to the client stack.** No amount of React escaping, CSP, or
  Trusted Types matters — the bug is in a check the server never ran.
- **Every id-keyed endpoint repeats the pattern.** Baskets, orders, messages,
  invoices, profiles — the same missing clause tends to be missing everywhere the
  same team wrote the same shape of handler.

## Two directions the same bug points

- **Horizontal BOLA**: a peer user accesses another user's object at the same
  privilege level. The bounded Juice Shop replay above tested this with two
  synthetic accounts and one basket route.
- **Vertical privilege escalation**: a lower-privilege user reaches an action
  or object reserved for a higher role. It requires a separate role-boundary
  test; it was not demonstrated in the cited basket replay.

Both are the same root cause (a missing authorization check); they differ only in
whether you move *sideways* to a peer's data or *up* to privileged data.

## Predictable ids make it worse — but obscurity is not the fix

Sequential ids (`1, 2, 3`) make the bug trivial to sweep: you just count. A common
half-fix is to swap them for UUIDs so they can't be guessed. That raises the effort
but is **security by obscurity** — the ids still leak (in URLs, emails, referrers,
API responses, shared links), and once an attacker has one, the *same* missing check
still serves the object. An unguessable id is a lock you left open with a longer key
number painted on it. The real fix doesn't care whether the id is guessable.

## The fix: check ownership on every object, every request

**Enforce per-object authorization at the point of access** — after you know *who*
the caller is, verify the requested object is *theirs* before returning it:

```js
// vulnerable: id from the URL, no ownership check
const basket = await Basket.findByPk(req.params.id);
return res.json(basket);

// fixed: the object must belong to the authenticated user
const basket = await Basket.findByPk(req.params.id);
if (!basket || basket.UserId !== req.user.id) return res.sendStatus(403);
return res.json(basket);
```

Supporting practices:

- **Scope the query to the user, don't filter after.** Prefer
  `Basket.findOne({ where: { id, UserId: req.user.id } })` so a foreign object is
  *never even loaded*, closing timing/error-leak side channels.
- **Centralise it.** A per-resource authorization layer (policy/middleware) applied
  to every id-keyed route, so a new endpoint is authorized by default rather than by
  a line someone must remember.
- **Deny by default.** New routes should require an explicit ownership/role rule to
  return data, not inherit "authenticated is enough."
- **Don't rely on unguessable ids** as the control — treat that only as defence in
  depth on top of a real check.
- **Test it directly.** Two accounts, swap the id, expect `403`/`404` — the exact
  Repeater step that *found* this bug is also the regression test that proves it
  fixed.

## Takeaway

The historical report and the later bounded lab replay are different evidence
items. The latter demonstrates one horizontal access-control failure in one
local route with synthetic accounts; it does not show vertical escalation or
prove a general pattern across the application. For each protected object,
verify the specific ownership and role policy with separate accounts and
positive/negative controls.

---

*Historical author report: OWASP Juice Shop via Docker, `/rest/basket/{id}` and
the *View Basket* challenge. The retained repository lacks the A/B ownership
control pair needed to independently verify the claimed cross-user access; no
current retest or vertical privilege-escalation result is claimed. Apply the
authorization check to each object access and test it with separate accounts.*
