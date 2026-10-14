# R5/K01 portable gated handoff — 15 October 2026

Base commit: `8dd50acb80ed41bb2e44d4f1ab9defa9f1deca09`.
This change makes the existing acceptance gate usable by a person on a local
Windows/macOS/Linux setup. It does not close the independent human repetition
criterion. No Docker, external target, fixture source or historical proof changed.

## Gap and implementation

Source inspection found that `check_repro.py` always required Linux/Python 3.12
and could not receive the installed browser option supported by `prove.py`.
The README's Windows handoff therefore called the proof producer without the
independent artifact/closed-port gate. The CLI now accepts `--profile local`
and `--browser`; its default `ci` profile still requires Linux/Python 3.12.
Both profiles compare the report's exact Python and OS values with the actual
executing runtime. The acceptance records the profile and gate source SHA-256.
Neither report nor console success output stores the browser path.

The gate now rejects optimized Python before running the assertion-based proof.
A real `python -O` subprocess regression confirms exit 2 with no proof directory.
Other negative regressions cover plausible wrong runtime declarations, default
CI rejection on unsupported runtime, timeout without acceptance, and preservation
of an existing proof directory. The original fixture function is restored even
when proof generation fails. README commands now use the gate and distinguish
local, hosted and second-person evidence.

## Local acceptance

Windows/Python 3.10.11, Playwright 1.63.0, installed Chrome. The targeted command:

```console
py -3.10 -m pytest cases/k01-stored-comment/test_fixture.py cases/k01-stored-comment/test_repro_gate.py -q -p no:cacheprovider --tb=short
```

Result: **22 passed**, zero failures/errors/skips. A purposeful new real local
CLI run used `check_repro.py --profile local --browser <installed-Chrome>
--output .dxa/r5-handoff-20261015-proof` and returned exit 0: **5/5 controls,
five distinct closed loopback ports**. Exact runtime binding and the existing
request/response/CID/source-hash gate passed. The new raw proof remains under
ignored `.dxa`; this audit stores its sanitized live acceptance, including the
12 artifact digests, in [acceptance.json](acceptance.json). This is a live result,
not a reuse of historical proof. Regression tests also intentionally use copies
of the prior proof as counterexample inputs.

No remote CI was run by this specialist; the coordinator handles integration.
No fresh venv or second human was used for this CLI acceptance. The existing
500 ms synchronous negative window and anonymous author/separate reader-context
limitations remain. Linux hosted proof is separate historical evidence, and
macOS local execution has not been tested. Independent second-person clean-machine
acceptance remains open under R5.
