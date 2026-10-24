> **Historical lab account — evidence limit.** This writeup mixes SQLi concepts, illustrative queries, and a historical author-reported Juice Shop challenge. The retained repository does not contain the matching masked request/response, database/version, or reproducible challenge record needed to independently verify the claimed login bypass. The `UNION` and blind sections are theory/examples, not results. See [C03 in the roadmap](../ROADMAP.md), the [audit](../audit/2026-09-28/DENETIM-RAPORU-TR.md), and [status](../STATUS.md).

> **New local repetition — 19 October 2026.** On an isolated OWASP Juice Shop
> 20.2.0 image, the same login shape returned 200 and a separate identity check
> matched the local admin account; a normal invalid login returned 401. The
> versioned request/response record and source hash are in the
> [K03 audit](../audit/2026-10-19-k03-loopback-reproduction/README.md). This is
> a new controlled reproduction; it does not identify the older session's
> version or recover its original HTTP exchange.

# SQL Injection: when your input becomes part of the query

> **TL;DR** — A SQL query is usually built by *gluing your input into a string*.
> Inside that string your input is **data** — until you send a `'`, which closes
> the quote early and drops everything after it into the **code** half of the
> query. That one boundary — data vs. code — is the whole bug: once you can write
> code where the app expected data, you rewrite the query's logic (bypass a login,
> dump another table). The only real fix is to never build the query by
> concatenation at all.

This section is **mechanism/theory**, not a Juice Shop experiment. The XSS writeups in this repo all turn on one idea: the browser parses a value in
a context where you didn't expect markup. SQL injection is the same shape one
layer down — the **database** parses a value in a context where the developer
expected only data. Same lesson, different parser.

## The one idea: the query is a string, and `'` is the border

An app authenticates a login like this — input concatenated straight into SQL:

```js
db.query("SELECT * FROM users WHERE username = '" + user + "' AND password = '" + pass + "'")
```

Type a normal username and your bytes sit **inside** the quotes, as data:

```sql
SELECT * FROM users WHERE username = 'alice' AND password = '...'
```

Now send `user = administrator'--`. The `'` **closes the string early**, and
everything you write after it is parsed as **SQL code**:

```sql
SELECT * FROM users WHERE username = 'administrator'-- ' AND password = '...'
```

In SQL dialects where the exact comment syntax is accepted in that position,
`--` comments out the trailing predicate. The illustrative query would then
omit its password check. This is a dialect/parser-dependent example, not proof
of the behavior of a specific application.

This maps directly onto the repo's [`methodology.md`](../methodology.md): the
**source** is any input that reaches a query (a form field, a `?query` param, an
API field, even a header), and the **sink** is the string-concatenated SQL. If a
source reaches that sink without being parameterised, you have SQLi.

## Three ways to use the border — examples, not this lab's results

**Theory example — login bypass:** comment out the check (the example above):

```
username:  administrator'--
password:  anything
```

**Theory example — retrieve hidden data:** make the `WHERE` always true. A product filter runs
`… WHERE category = 'Gifts' AND released = 1`; injecting into `category`:

```
Gifts' OR 1=1--
```
→ `… WHERE category = 'Gifts' OR 1=1-- AND released = 1`. `OR 1=1` is true for
every row and `--` kills the `released = 1` restriction, so **every** product —
including unreleased ones — is returned. (PortSwigger Academy's first two
SQL-injection labs are exactly these two shapes.)

**Theory example — `UNION`:** `UNION` appends a second `SELECT` and
stacks its rows onto the results. So a search that shows product names can be made
to show usernames and password hashes instead:

```sql
' UNION SELECT username, password FROM users--
```

`UNION` has two rules, and getting them right is the whole technique:

- **Same number of columns.** Both `SELECT`s must return equal column counts.
  Find the count by incrementing `ORDER BY 1--`, `ORDER BY 2--`, … until it
  errors (the last working number is the count), or by padding
  `UNION SELECT NULL--`, `UNION SELECT NULL,NULL--`, … until the page stops
  erroring.
- **Compatible types.** The column you exfiltrate through must accept text. `NULL`
  fits any type, so you probe with `NULL`s first, then swap a `NULL` for a string
  to find which column renders on the page.

The historical author account says shape **#1, login bypass**, was solved as
Juice Shop Finding #6 using `' OR 1=1--` in the email field and that the
*Login Admin* challenge completed. The retained screenshots support some
challenge activity generally, but do not independently establish this exact
request, response, authenticated identity, or query behavior. Treat this as an
unverified historical report, not a currently reproduced finding. The
PortSwigger Academy exercises are also author-reported here without a retained
per-lab result. The `UNION` and blind sections below are mechanism/examples;
they were not run against Juice Shop.

## Theory example — when you can't see the output: blind SQLi

Often the query result never appears on the page — but the app still *behaves*
differently depending on whether your injected condition is true. You then leak
data one bit at a time:

- **Boolean-based:** `… AND (SELECT SUBSTRING(password,1,1) FROM users LIMIT 1)='a'`
  — the page renders normally only when the guess is right. Ask yes/no questions
  until you've reconstructed the value.
- **Time-based:** when even the page is identical, make a *true* condition sleep —
  `… AND IF(<condition>, SLEEP(5), 0)` — and read the answer off the response
  delay.

Slower, but the same border break: your input is running as code inside the query.

## Why "just escape the quotes" is not the fix

It is tempting to blocklist — strip `'`, ban the word `UNION`, escape quotes by
hand. This fails for the same reason a blocklist fails for XSS
([Writeup 01](01-filtering-is-not-protection.md)): you are trying to out-guess a
parser you don't control. Attackers route around it with encodings, comment
insertion (`UN/**/ION`), alternate quoting, or by injecting into a numeric context
that needs no quote at all (`id=1 OR 1=1`). Escaping is a patch over a design that
still hands the database a string it has to *parse* for structure.

## The fix: separate the code from the data

**Use parameterised queries (prepared statements).** You send the query *shape*
and the values on **separate channels**; the driver binds each value as a pure
literal that is **never parsed as SQL**:

```js
db.query("SELECT * FROM users WHERE username = ? AND password = ?", [user, pass])
```

Now `administrator'--` is looked up as a literal username `administrator'--` — a
user that doesn't exist — and login fails. The `'` can't close anything because
there is no surrounding string being parsed on the server side; the border between
code and data is enforced by the database API, not by your escaping. This
**structurally** removes the entire class.

Supporting controls:

- **ORM / query builders** that parameterise under the hood (Sequelize, Prisma,
  Hibernate) — use their bindings, never their raw-string escape hatches.
- **Least-privilege DB account** — the app's user shouldn't be able to read every
  table or run `DROP`; it caps the blast radius of any slip.
- **Allowlist the few parts you cannot bind.** Column names and `ORDER BY`
  direction can't be parameters — map them against a fixed allowlist, never
  interpolate raw input.
- **Don't lean on WAFs or escaping as the primary control** — they are
  defence-in-depth, not the fix.

## Takeaway

SQL injection is a **data-becomes-code** confusion: input is parsed as part of a
query. The examples here — login bypass, `OR 1=1`, `UNION`, and blind extraction
— show different possible query behaviors; only the login shape has a separate
bounded local reproduction linked above. Parameterised queries keep bound
values out of SQL syntax positions for query paths that use them. This guidance
does not claim every application query is parameterised or safe.

---

*Historical author-reported practice: OWASP Juice Shop's *Login Admin* challenge
and PortSwigger Academy labs. Their exact requests/results are not independently
verified from retained evidence. The `UNION` and blind sections are explanatory
examples, not claimed experiments. The method is source→query tracing applied to
the database layer.*
