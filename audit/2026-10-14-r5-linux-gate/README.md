# R5/K01 clean Linux workflow, pending hosted acceptance

A new required workflow installs Python 3.12, pinned Playwright 1.63.0 and
Chromium on Ubuntu. It runs K01's five disposable 127.0.0.1 controls,
independent gate tests and a live artifact gate. The gate checks five distinct
closed fixture ports, one POST per control, shared CID/payload, source hashes,
fix diff, response bodies and the separation of HTTP candidates from browser
execution. JUnit and proof/acceptance files are uploaded.

Coordinator's local combined R5/R8 regression: 104 passed, zero
failures/errors/skips. The gate also accepted a new Windows Chrome K01 run
with 5/5 controls and 5/5 closed ports. [Commands and hashes](acceptance.json).
Hosted Linux execution and artifact inspection are pending push. A CI runner
is a second environment, not an independent second person; general R5
acceptance remains open.
