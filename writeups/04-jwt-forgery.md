> **Historical lab account — evidence limit.** The `alg:none` challenge success and the unsuccessful key-confusion attempt are author-reported historical results. Retained evidence does not include the exact masked token exchange, target build, or verifier configuration needed to independently reproduce either outcome. The HS256 failure's cause is unknown; newline/key encoding below is a hypothesis, not an observed diagnosis. See the [audit](../audit/2026-09-28/DENETIM-RAPORU-TR.md) and [roadmap](../ROADMAP.md).

# Forging JWTs: when the token decides how it's checked

> **TL;DR** — A JSON Web Token carries its own claims (*who you are*) **and a
> header that says how the signature should be verified*. If the server trusts
> that header, the attacker controls the verification. Say `alg: none` and the
> server checks nothing; say `alg: HS256` and sign with the server's *public* key
> and the server validates your forgery with its own key. Both bugs have one root:
> the **token** is allowed to choose how the **server** authenticates it. The fix
> is to take that choice away from the token.

Every other writeup in this repo is about a value being interpreted in a context
the developer didn't expect — markup in HTML, input in SQL. JWT forgery is the
same failure at the **authentication** layer: a field the attacker controls (the
`alg` header) is used to make a security decision (how to verify the signature).
Control the decision, and you mint tokens for any user.

## The one idea: the signature is the only thing that binds the claims

A JWT is three base64url parts:

```
base64url(header) . base64url(payload) . signature
       {"alg":"RS256","typ":"JWT"}  .  {"data":{"email":"you@x"}}  .  <sig>
```

The header and payload are **not encrypted** — anyone can read and edit them. The
only thing stopping you from changing `email` to someone else's is the
**signature**, which binds `header.payload` with a key the server holds. So every
JWT attack is really one question: *can I produce a signature the server will
accept without knowing its secret?* Two classic yeses follow.

## Mechanism example 1 — `alg: none`

The header names the algorithm. The JWT spec even defines `none` — "unsecured,
no signature." If the server honors whatever the header says, you set
`alg: none`, drop the signature entirely (empty third part, but keep the trailing
dot), and edit the payload freely:

```
header   = {"typ":"JWT","alg":"none"}
payload  = {"data":{"email":"jwtn3d@juice-sh.op"}}
token    = base64url(header) . base64url(payload) .        ← empty signature
```

The historical account says an `alg:none` token was submitted for OWASP Juice
Shop's *Unsigned JWT* challenge and the challenge completed. The retained
repository does not verify that exchange. The token below is a historical
example from the writeup, not a current reproduction:

```
eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJkYXRhIjp7ImVtYWlsIjoiand0bjNkQGp1aWNlLXNoLm9wIn19.
```

The historical writeup says Burp Decoder/JWT Editor/Repeater were used and that
the challenge completed. The exact exchange and verifier response are not retained,
so the stated mechanism is not independently confirmed for the target.

> **Field note.** Encoding this by hand is fiddly only because of base64url:
> after a standard base64 encode, strip `=` padding and swap `+`→`-`, `/`→`_`. The
> header and payload are plain JSON; the third part is genuinely empty.

## Attack 2 — RS256 → HS256 key confusion: sign with the *public* key

`RS256` is **asymmetric**: a **private** key signs, a **public** key verifies. The
public key is, by design, public — you can often just download it. `HS256` is
**symmetric**: the **same** secret both signs and verifies (HMAC).

The bug appears when the verification code trusts the header's `alg` and feeds the
same key material to whichever algorithm the token names — roughly
`verify(token, publicKey)` with no algorithm pinned. Then:

1. Change the header from `RS256` to `HS256`.
2. Sign the token with **HMAC-SHA256, using the RSA *public* key as the HMAC
   secret** — which you have, because it's public.
3. The server sees `HS256`, runs HMAC with *its* key (the public key), and gets
   the **same** result you did. The signature "verifies." Forgery accepted.

It works because HMAC is symmetric: the public key, meant only for RSA
*verification*, becomes a shared secret the moment the server will HMAC with it.
Juice Shop's *Forged Signed JWT* challenge serves the public key right at
`/encryptionkeys/jwt.pub`; the intended path is to forge `email:
rsa_lord@juice-sh.op`, switch the header to `HS256`, and HMAC-sign with that key.

> **Historical field note — unsuccessful; cause unverified.** The author reported
> that the key-confusion attempt did not complete the challenge. Key-byte or
> representation differences are possible causes to investigate, but this attempt
> retained no diagnostic evidence to establish the cause. A well-formed token or
> HTTP 200 alone does not show signature verification succeeded. This remains an
> unsuccessful, unexplained attempt.

## The common root cause

Both attacks come from the same mistake: **the server let the token dictate how it
would be verified.** `alg: none` says "don't verify"; `alg: HS256` on an
RS256 system says "verify with the wrong algorithm and my public key." In each
case a claim (`alg`) that the attacker fully controls drives a security decision.
It's the auth-layer cousin of "client-side validation is not security" (Finding #4
in this repo): never let attacker-controlled input decide a control.

## The fix: the server decides, not the token

1. **Pin the accepted algorithm and key type server-side.** Use the library's
   explicit algorithm allowlist and reject unsecured tokens unless a narrowly
   designed protocol explicitly requires them. Reject incompatible key/algorithm
   combinations. Do not let the token header select arbitrary verification
   behavior.
2. **Never verify an HS256 token with an RSA public key.** Keep symmetric and
   asymmetric keys and code paths separate so a public key can never be used as an
   HMAC secret.
3. **Verify the signature *and* the claims** — check `exp`/`nbf`, the issuer, and
   the audience; a valid signature on an expired or wrong-audience token is still
   invalid.
4. **Strong secrets for HS256** (long, random) so brute-forcing the secret is not
   an alternative path.
5. **Reduce token theft exposure.** `HttpOnly` cookies prevent JavaScript from
   reading that cookie, unlike `localStorage`; they do not stop injected script
   from issuing authenticated actions through the page. Choose storage and CSRF
   defenses for the application's threat model.

## Takeaway

A JWT's claims are only as trustworthy as the check on its signature — and if the
token gets to choose that check, there is no check. `alg: none` removes it; key
confusion redirects it to a key you already hold. Both vanish the moment the server
**pins the algorithm and keys itself** instead of obeying the header. Don't let the
thing being verified decide how it's verified.

---

*Historical author report, on a stated local OWASP Juice Shop target: the *Unsigned JWT*
(`alg:none`) challenge was described as solved; retained evidence does not
independently verify the token exchange. The RS256→HS256 *Forged Signed JWT*
challenge was reported as attempted but unsolved; its cause was not established.
These are not current reproductions. The mechanism is explanatory: pin verification
policy independently of attacker-controlled token headers.*
