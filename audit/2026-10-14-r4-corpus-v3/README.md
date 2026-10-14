# R4 loopback corpus v3 — local and remote acceptance

Base commit: 61dde5c31c8c5624aead0cd399708d563b6f8e71.
Active checkout: C:/xss/xss-github.

## Change and evidence

The corpus adds five cases to the previous nine: escaped-and-raw output,
an identity sanitizer feeding a DOM sink, editor-role raw and encoded notes,
and an explicitly allowed same-origin iframe. The alternate identity is
POST /notes, field text, read /review, role editor. Frame evidence is matched
against each target's explicit allowlist; only the iframe case allows /frame.

The adapter previously hardcoded reader and /comments. It now validates the
defined source, parameter, read sink, role and frame before crediting the
stable v3 case ID. Malformed identities fail closed; absent legacy demo
metadata retains the original reader/comments defaults. The gate compares
artifact metadata with the local corpus, checks all 14 independent labels,
and rejects nested proof mismatches even when JSON and Markdown agree.

The completed/selected ratio and accuracy denominator are explicit in
Markdown. Incomplete/error/timeout/skip outcomes are not evaluated and fail
strict acceptance. [Comparison protocol](../../bench/COMPARISON-PROTOCOL.md)
defines equivalent scopes, auth, budgets, coverage and human triage; no
competitor comparison has been run or claimed.

## Validation

The coordinator ran all benchmark tests plus affected R3 browser and cleanup
tests with browser required: **527 passed, zero failures/errors/skips**.
The real strict Chrome runner CLI completed **14/14, TP=7, FP=0, FN=0**,
with zero incomplete outcomes. JSON and canonical Markdown match.
Commands, environment and source/output hashes are in
[acceptance.json](acceptance.json); [JSON](local-proof.json) and
[Markdown](local-proof.md) preserve the local execution evidence.

During integration an old nine-case expectation failed five incomplete-status
regressions; it was corrected to the independently defined 14-case corpus.
The sanitizer fixture was completed as an actual identity-function-to-DOM
path, and the completed-negative oracle was adapted to the separate editor
identity. The final 527-test run includes these corrections.

## Ownership and Docker decision

Native Engine (r4_strict_corpus) implemented corpus/fixture/adapter changes.
Native QA (r4_qa_audit) wrote independent identity/frame/coverage tests.
Both stopped at a usage limit before final acceptance. The coordinator
reviewed and finished their work, integrated the gate/workflow, wrote the
protocol and ran final verification; no completed final specialist review
is claimed. At most two specialists worked concurrently.

Bludit adapter/Compose files and the DockerTarget, product-control validation,
runner and failure functions are unchanged by source/AST comparison.
Their benchmark regressions are included in the 527-test run. No Docker
restart or live Bludit rerun was needed or performed; historical live Docker
acceptance remains separate. Product controls remain outside XSS scores.

## Limits and remote acceptance

This is a bounded correlated-execution corpus, not vulnerability accuracy.
The editor fixtures use one account in a distinct role; they do not test a
cross-account authorization boundary. Dynamic sanitizer fixtures do not
prove static taint analysis. Only the named same-origin iframe is covered.
Blind/admin correlation, auth/CSRF failure corpus, broader identity/taint
coverage and an actual controlled competitor comparison remain open.

Code commit 43314032bbe26f4809dac6f565a6e751fba2ad70 was pushed and remote
main matched. [CI run 38550538424](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38550538424)
passed all three jobs. The downloaded archive digest matched GitHub metadata.
The exact-commit gate passed: JUnit 134 tests, zero skips/errors; corpus
14/14, TP=7 FP=0 FN=0; exact JSON/Markdown and source/corpus provenance;
demo execution observed. The report records Python 3.12.15/Linux.
[Remote acceptance and member hashes](remote-acceptance.json).

The Windows working runner/fixture bytes use CRLF while committed and hosted
sources use LF. The first local artifact check correctly rejected those
different byte hashes. Verification then used a minimal temporary source tree
containing exact Git blob bytes from the tested commit; no gate check was
relaxed. Local acceptance hashes retain the locally tested Windows bytes.
Hosted CI did not run Bludit Docker acceptance.
