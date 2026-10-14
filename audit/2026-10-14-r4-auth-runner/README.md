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
Fresh remote acceptance is pending push.

Prior standalone controls and blind/admin boundary regressions are in
[the historical delivery](../2026-10-14-r4-auth-blind-controls/README.md).
The separate-admin blind fixture and equal-condition comparator remain open.
Docker lifecycle files were untouched; live Docker was not repeated.
