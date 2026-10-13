# R4 strict corpus provenance gate — local acceptance

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
Python 3.10.11, pytest 9.1.1. Focused artifact-gate suite: **90 passed**.
Combined scorer/corpus/artifact suite: **204 passed**, zero failures/errors/
skips. The exact commands and SHA-256 values are recorded in
[acceptance.json](acceptance.json). `git diff --check` passed.

## Acceptance still open

This is local acceptance only. Keep the remote artifact criterion open until
the updated GitHub workflow passes and the uploaded JSON/Markdown/JUnit
artifacts are downloaded and validated against this gate. Broad R4 corpus and
coverage, the full comparison methodology, R3 header harvesting, and general
R9 remain separate roadmap work.
