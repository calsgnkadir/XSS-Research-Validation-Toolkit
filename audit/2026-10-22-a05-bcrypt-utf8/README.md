# R7/A05 — bounded offline UTF-8 BCrypt boundary assay

Date: 2026-10-22. Toolkit baseline: `6167fa8361fd9f02b1a9e859152117639c855540`.
Pinned Kadrom source: `ae4aebbf8963f550f6bb7c3465fb1270d677af1c`.
Evidence type: new direct-library execution plus read-only source tracing.

## Result and limits

The exact cached packaged `spring-security-crypto:6.2.4` matched all three
different Unicode suffix inputs against hashes of their paired original values.
Each pair had identical first 72 UTF-8 bytes and different complete inputs.
Two pairs contained only **72 Java UTF-16 units**, while occupying 73 and 74
UTF-8 bytes. The third contained 73 UTF-16 units and 75 UTF-8 bytes. Thus a
72-unit Java character cap would still admit the first two tested shapes.

| Case | UTF-16 units per value | UTF-8 bytes per value | Same first 72 bytes | Different suffix matches |
|---|---:|---:|---|---|
| Two-byte final code point | 72 | 73 | true | true |
| Three-byte final code point | 72 | 74 | true | true |
| Four-byte final code point | 73 | 75 | true | true |

A separate exactly-72-byte positive control occupied 71 UTF-16 units: the
known value matched, and a first-byte substitution did not match. All independent
input/control assertions passed. There were exactly **9 BCrypt operations**:
four encodes and five matches. No exception, timeout or skipped case occurred in
the successful execution. These are assay cases, not a JUnit or toolkit suite.

This extends the earlier [ASCII registration/login reproduction](../2026-10-22-a05-bcrypt-local-check/README.md)
with Unicode **library behavior**. No new registration, login, password change,
reset, account or application request ran. Source-supported admission of these
specific shapes does not prove they traversed any application endpoint in this
run. No real-account effect, account takeover, production equivalence or new
CVE is established. The [existing triage](../2026-10-22-a05-bcrypt-triage/README.md)
remains the record for advisory comparison; this task made no new advisory lookup.
R7/A05 remains open, including separately authorized remediation and retest.

## Independent oracle and executed helper

The exact executed source is [Utf8Boundary.java](Utf8Boundary.java). It generates
random synthetic ASCII prefixes with an ASCII letter and digit. A shared
71-byte prefix is followed by one of three valid code-point pairs, with encoded
widths 2, 3 and 4 bytes. In each pair the final code points differ but share their
first UTF-8 byte. The boundary therefore ends **inside** the final code point;
the whole submitted strings are valid Java/UTF-8 values, but their shared
72-byte prefix alone is not a complete UTF-8 string. No truncation or repair of
the submitted strings is done by the helper.

Before calling BCrypt, independent assertions check code-point widths, both
byte lengths, both UTF-16 lengths, full inequality, first-72-byte equality and
the packaged `PasswordPolicy.violationKey` result. The at-limit control
asserts true/false matching independently. Observed suffix matching is recorded
without asserting the suspected outcome, so contrary library behavior would
still be reported. The packaged policy accepted both inputs in every pair.
Input strings, encoded password hashes and random prefixes are never emitted.

Exact allowlisted output: [snapshot.json](snapshot.json), SHA-256
`c2b63515a1fe3b8b9bba90d499a46351ed0ccb992c045897f82b1080a6eddc3d`.
Executed Java helper SHA-256:
`9ac1efa55f5b642aaaf959c0cb5a4c27e1f15c3d5e5e4cf7a8c2380a488410ca`.
Package-local `.gitattributes` preserves those artifact bytes across Git newline
settings. The snapshot contains counts, booleans and artifact identity only.

## Cached artifact identity and execution

The existing `.dxa/a05-runtime-preflight/app.jar` was read, with its required
SHA-256 checked before extraction:
`e564ab781100246897733a9367cd64ef76251a6d77272d73243c0174154ff608`.
Only these three entries were extracted into the new ignored
`.dxa/a05-bcrypt-utf8/cached/` directory:

| Packaged entry | SHA-256 |
|---|---|
| `BOOT-INF/lib/spring-security-crypto-6.2.4.jar` | `5a36c1f29d11f0b9ce4b7c54886bd909499eadb0b19be507b6b3992830af23b6` |
| `BOOT-INF/lib/spring-jcl-6.1.6.jar` | `bfbd972fbd94dfb40cc2b19de21b769e8157497cf55555523a0e01b468b8e9b8` |
| `BOOT-INF/classes/com/hotelapp/validation/PasswordPolicy.class` | `88045e52ceb4a2f3e2b4b0c8a726f84327745703d3d5feea9cc32893423e5d4c` |

Host Windows Oracle Java/javac `21.0.11` compiled the helper with `--release 17`.
After extraction, the compile/run commands were the following (paths shown
relative to toolkit root; the wrapper passed absolute equivalents):

```powershell
javac --release 17 -cp '.dxa/a05-bcrypt-utf8/cached;.dxa/a05-bcrypt-utf8/cached/*' -d .dxa/a05-bcrypt-utf8/classes audit/2026-10-22-a05-bcrypt-utf8/Utf8Boundary.java
java -cp '.dxa/a05-bcrypt-utf8/classes;.dxa/a05-bcrypt-utf8/cached;.dxa/a05-bcrypt-utf8/cached/*' Utf8Boundary
```

An ignored Python wrapper checked the app hash, extracted these entries, ran
those commands with 30-second subprocess timeouts, parsed the emitted JSON and
added artifact identity. Its first `py -3.10` launch failed with access denied;
no Java execution or BCrypt operation ran in that attempt. The same bounded
offline wrapper succeeded after explicit platform escalation. No downloads,
Maven builds, Docker operations, network requests or application context startup
occurred. No product or toolkit test suite or CI workflow was run or queried.

## Source admission trace

Paths below are relative to read-only
`.dxa/a04-kadrom-source/hotelapp/src/main/java/com/hotelapp/`. This checkout was
verified at the pinned commit with an empty `git status --short` after the
assay (Git also warned it could not read the global ignore file). It was not
edited. The packaged class execution and source inspection are distinct;
this task did not reproduce the original image build or establish complete
source/bytecode equivalence.

| Path and lines | Source-supported conclusion for the three tested shapes |
|---|---|
| `validation/PasswordPolicy.java:13-26` | Minimum 8 UTF-16 units plus ASCII letter/digit lookaheads; no maximum or byte count. The tested shapes satisfy these source rules, and the extracted packaged class independently returned no violation for both values of each pair. |
| `dto/RegisterRequest.java:34-37`; `controller/AuthController.java:63-67`; `service/AuthService.java:62-82` | Registration validates nonblank/minimum/composition, repeats shared policy in the service, then encodes. No password-byte cap in the traced checks excludes the tested shapes. Required non-password DTO fields were not exercised. |
| `dto/LoginRequest.java:13-14`; `controller/AuthController.java:77-83`; `service/AuthService.java:141-149` | Password requires nonblank; the supplied value reaches the authentication manager. The shapes satisfy that password constraint. No new login was executed. |
| `controller/AuthController.java:146-151`; `service/AuthService.java:291-322` | Current password is nonblank and checked with `matches`; new password has minimum/composition constraints and is encoded. Both tested values satisfy the relevant password DTO constraints. Other authorization/state conditions and this runtime flow were not tested. |
| `controller/PasswordResetController.java:53-56,68-77`; `service/PasswordResetService.java:117-136` | Reset confirmation applies min 8/max 128 UTF-16 units and composition, then the service repeats shared policy before token/state lookup and encoding. Each tested shape is below 128 units and satisfies password checks; token/state requirements and endpoint execution were not tested. |

No normalization, invalid-surrogate input, password storage migration or existing
long-password account recovery was tested. Do not infer a general Unicode or
normalization result beyond these three valid code-point pairs.

## Ownership and invocation

Coordinator assigned only this audit directory and ignored
`.dxa/a05-bcrypt-utf8/` to native `qa_security_lab_specialist` task
`/root/a05_bcrypt_utf8`. The role TOML and current AGENTS/ROADMAP/STATUS/workflow,
VALIDATION, evidence/auth contracts and relevant prior audits were read.
Successful native role selection is distinct from proof that runtime loaded
the TOML, which was not independently established here. Only assigned files
were written; no Git mutation or shared roadmap/status edit was made.

## Acceptance self-review and control limits

After execution, a read-only artifact review rechecked the unchanged Java,
snapshot and extracted crypto JAR hashes against the values above. Reading
`META-INF/MANIFEST.MF` from the extracted JAR independently of its filename
showed `Implementation-Title: spring-security-crypto` and
`Implementation-Version: 6.2.4` (`Created-By: 17.0.10 (Oracle Corporation)`).
The manifest describes artifact metadata; the assay itself ran on host Java
21.0.11 as stated above. No assay or application request was repeated.

Source/JSON correspondence checks: the helper performs one control encode and
two control matches, followed by exactly three loop iterations, each with one
encode and one match (4 + 5 = 9). The snapshot has three rows in the same width
order as the source code-point table. Each row's UTF-16 and UTF-8 counts agree
with the independently asserted source lengths. `differentSuffixMatches` is
the returned library boolean, while first-prefix equality and policy admission
are separate assertions. Snapshot identity records the exact unchanged Java
bytes. Registration/login/change/reset DTO acceptance remains **source analysis**;
only the extracted shared `PasswordPolicy` class was actually invoked.

Control limitations: the operation budget includes no separate same-input match
or different-first-byte negative match for each of the three over-limit pairs;
those checks were performed only for the separate exactly-72-byte control.
No below-72-byte sample, repeated random seed, normalization variant, unmatched
surrogate, or pair whose boundary ends between complete code points was included
in this new assay. Prefixes and salts are random and not retained; a repeat can
reproduce the asserted shapes, not these exact private strings/hashes. This
review is the producing specialist's self-review, not an independent second
specialist acceptance or a second execution. Coordinator acceptance remains
separate.

Read-only pre-run review of the separate multipart proposal identified two
unexecuted oracle gaps: require an empty post-control temp snapshot before any
malformed comparator, and require `handlerPresent=false` before describing the
malformed parser error as occurring before handler binding. The multipart task
was stopped by an automatic cyber-risk flag; this specialist did not run,
repair or retry its helper or requests. Those review comments are not multipart
runtime evidence and do not advance its acceptance.
