# R4 / R5 / R6 resumed delivery - 15 October 2026

Base commit: `2abcd51`. The current checkout is the existing non-OneDrive
repository. Fetch confirmed HEAD and upstream matched (0 ahead/0 behind).
Uncommitted corpus/config changes and the independent-repeat form from the
interrupted session were preserved and reviewed, not replaced.

## Ownership and validation

Native Scanner Engine `/root/r4_resume` owns R4 corpus v4 and its regression
and live browser validation. Native Report `/root/r6_resume` owns dynamic CLI
config, tests, installed wheel smoke and README. The coordinator owns R5 human
handoff review, combined integration, progress records and Git delivery.
Only two specialists run concurrently. Ordinary sandbox process startup failed;
explicit escalated commands worked. No claim is made that TOML settings alone
granted runtime access. All experiments are authorized disposable loopback labs.

## R5 independent human handoff

The coordinator reviewed `cases/k01-stored-comment/INDEPENDENT-REPEAT.md`
against README and `check_repro.py`: five controls, twelve proof members plus
acceptance, commit/runtime/source hashes and live cleanup are distinguished.
The form explicitly remains unfilled; no independent human execution evidence
was supplied for this delivery. Automated regression, AI agent execution and
previous CI cannot close this criterion. No new human or live K01 result is
claimed. A real participant must execute the documented fresh checkout/venv
procedure and submit the form with that run's evidence for coordinator review.
No external message was sent.

## Acceptance

Coordinator integration passed **503 tests**, zero failures/errors/skips,
Python 3.10.11 on Windows. Exact command and source hashes: [acceptance.json](acceptance.json).
JUnit share copy removes only hostname. Specialist results are recorded in
the separate R4 and R6 audit packages; counts overlap and are not added.
Remote CI remains pending until push. R4 broad admin
coverage/comparison, R5 second-human acceptance and the R6 release gate remain
open. No release tag or vulnerability claim is created.

Specialists completed: [R4](../2026-10-15-r4-broader-corpus/README.md), 254 tests
and strict 17/17 (TP8 FP0 FN0); [R6](../2026-10-15-r6-config-release/README.md),
101 focused tests and 6/6 installed checks. Coordinator reviewed all code and
independent test oracles. The installed-smoke helper initially overwrote its
config with a same-named report; distinct filenames fixed the test helper and
the new successful run is recorded. Runtime product sources remained stable.
R5 has no human acceptance evidence; the handoff is the only R5 document change.

## Remote acceptance

Code `0261baaa8a21ff2d16308bf9a1a4ccd003ceccb8` was pushed and remote main
matched. General [CI 38706882024](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38706882024)
completed all three jobs successfully. Downloaded artifact digest matched
GitHub metadata. The exact committed gate accepted 179 JUnit tests, zero
failure/error/skip, corpus v4 17/17 TP8 FP0 FN0 and demo execution. Separate
auth controls passed 6/6 with cleanup. Canonical JSON/Markdown and Git-blob
source hashes matched. [R4 artifact record](remote-r4-acceptance.json).

[K01 Linux 38706882018](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38706882018)
also succeeded. Downloaded artifact: 22 JUnit tests, five passing proof
controls, five distinct closed ports recorded by CI, ci profile and gate/source/
proof-member hashes matched. [K01 artifact record](remote-r5-acceptance.json).
Downloaded artifacts do not re-observe historical sockets or establish a
second human. Docker acceptance was not rerun. Earlier pending statements
in local acceptance records describe their pre-push snapshot.

The canonical generated corpus Markdown includes a final blank line. Staged
whitespace checking with `core.whitespace=-blank-at-eof` passed; the canonical
renderer output was preserved for JSON/Markdown equality. Share copies omit
local JUnit hostname and browser path as recorded in their audit metadata.
