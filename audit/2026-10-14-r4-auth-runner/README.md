# R4 auth/CSRF operational controls in the benchmark runner

The runner --auth-failure-controls option executes six disposable local
expected-failure cases through owned workers. Each has a 30-second deadline.
JSON and Markdown carry a separate operational_controls section with stage,
status, cleanup and source hash. A mismatch returns exit 2 regardless of
BENCH_STRICT. XSS rows and TP/FP/FN remain separate.

The local real-Chrome runner passed six of six controls and all six cleanup
checks. Its separate mock candidate score was TP=1 FP=0 FN=0. This is an
operational boundary control, not a detected auth/CSRF vulnerability or an
admin-account XSS proof. [Commands and hashes](acceptance.json).

Coordinator's combined affected regression: 215 passed, zero failures/errors/
skips. Engine also reported focused 82 and real-browser 28 passes; coordinator
checked the live JSON. Required hosted browser CI includes new regressions
and a real controls CLI step; JSON/Markdown outputs are uploaded.
Code commit bec59b48267ce61adbd485f617bb82bc2d22f4d6 was pushed.
[CI run 38593458769](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38593458769)
passed all three jobs. The downloaded archive digest matched GitHub metadata.
The exact-commit gate passed 169 JUnit tests with zero skips/errors, proof
corpus 14/14 TP=7 FP=0 FN=0 and canonical JSON/Markdown/demo checks.
The new auth-controls artifact passed 6/6 expected errors, 6/6 cleanup,
source hash and canonical Markdown checks. [Remote record and hashes](remote-acceptance.json).
Git main had advanced to the later K01 evidence commit by artifact inspection;
that commit descends from the tested code commit. Hosted CI did not run
the opt-in Bludit Docker acceptance.

Prior standalone controls and blind/admin boundary regressions are in
[the historical delivery](../2026-10-14-r4-auth-blind-controls/README.md).
The separate-admin blind fixture and equal-condition comparator remain open.
Docker lifecycle files were untouched; live Docker was not repeated.
