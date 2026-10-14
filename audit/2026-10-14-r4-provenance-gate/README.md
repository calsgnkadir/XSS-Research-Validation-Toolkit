# R4 strict corpus provenance gate — acceptance and follow-up

## Gap and change

The required `r3-proof` job already ran the strict nine-case execution corpus,
produced JUnit, JSON and Markdown, and uploaded them. Its artifact gate checked
JUnit skips/errors, labelled case identities, nested canary proof, exact
positive/negative scores and completed/error/timeout/skip totals. It did not
read the Markdown artifact, compare it with JSON, or bind runtime/command/source
provenance to the current checkout.

The gate now requires `--corpus-markdown`. It validates the JSON report's
Python/platform/command metadata and SHA-256 values for the benchmark runner,
proof scanner, proof fixture and proof-corpus definition against the current
checkout. It compares the Markdown file byte-for-text with the runner's
canonical rendering of that JSON report. The required CI workflow supplies
`r4-proof.md` to the gate. Bludit remains opt-in local Docker acceptance and
is not part of hosted CI or vulnerability scoring.

## Local validation

Base commit: `7ce1927e9ac7c2f24e3bbeccd91c87e7d5a29d60`. Environment: Windows 10,
Python 3.10.11, pytest 9.1.1. After the QA runtime follow-up, focused
artifact-gate suite: **94 passed**. Combined scorer/corpus/artifact suite:
**208 passed**, zero failures/errors/skips. The exact commands and SHA-256
values are recorded in
[acceptance.json](acceptance.json). `git diff --check` passed.

## Remote acceptance and QA follow-up

Commit `7f67d53b8960788519e76d61dd0e4b4bf9b947ec` was pushed and the remote
`main` hash matched. GitHub Actions run
[38475480351](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38475480351)
completed successfully with all three jobs green. The uploaded
`r3-browser-proof` artifact was downloaded, its archive digest matched GitHub's
artifact metadata, and its JUnit/JSON/Markdown/demo files passed the strict gate
from this commit: 94 tests, zero skips/errors, corpus 9/9 (TP=3, FP=0, FN=0),
exact JSON/Markdown match, and observed demo execution. The report recorded
Python 3.12.15/Linux and all four source/corpus hashes matched the checkout.
Details and member hashes are in
[remote-acceptance.json](remote-acceptance.json).

An independent QA review then found the gate accepted any syntactically valid
Python/platform strings, even though the recorded artifact itself was correct.
The gate now requires Python 3.12 and Linux, with negative tests for plausible
but wrong runtime values. Locally this follow-up passed 94 focused and 208
combined tests. The runtime-hardening changes still need a fresh hosted CI run
and artifact inspection; the earlier remote result covers commit 7f67d53 only.
Broader R4 corpus and coverage, the full comparison methodology, R3 header
harvesting, and general R9 remain separate roadmap work. Hosted CI did not run
the opt-in local Bludit Docker acceptance.

## Resumed validation and independent review

On 14 October, the active checkout was verified as `C:/xss/xss-github`,
`main`, based on `7f67d53`; the pending runtime changes were preserved.
Native QA (`r4_qa_audit`) inspected code, evidence contracts and hashes.
Native Engine (`r4_strict_corpus`) mapped remaining R4 scope and corrected
the four runtime regressions: mutated JSON now has matching canonical
Markdown, so a Markdown mismatch cannot mask the missing runtime check.
The isolated old gate accepted all four wrong runtimes (four regression
failures); the current gate rejected all four (four passes). The coordinator
reviewed the change and reran the combined suite: **208 passed, zero
failures/errors/skips**, including 94 artifact-gate cases. Exact command,
source hashes and JUnit digest are in `acceptance.json`.

This validates declared Python series and OS family against CI expectations;
it is not cryptographic runtime attestation. Bludit/Docker was not rerun in
this follow-up. General corpus/coverage and comparison methodology remain
open; the next corpus increment needs distinct source/sink/role identities
and explicit incomplete-run coverage, with Bludit still in product controls.
