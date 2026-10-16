# R8 current-source review — 2026-10-16

## Scope and result

At base commit `84839a47c2f64e50ecf9a9bd737fd6e1fe31d712`, the native
`xss_security_researcher` reviewed the remaining R8 static-analyzer criteria
and current source/tests. That review found no gap in the existing criteria;
the specifically planned one-language AST pilot was still outstanding. The
specialist then implemented that bounded pilot and its corpus, with exclusive
ownership of `dxa.py` and `test_r8_ast_pilot.py`.

```powershell
py -3.10 -m pytest tools/dom-xss-analyzer/test_r8_sanitizer.py tools/dom-xss-analyzer/test_static_context.py -q -p no:cacheprovider --tb=short
```

The initial R8 review subset passed **41 tests**. After adding the AST pilot,
the coordinator independently ran the expanded focused package on Windows /
Python 3.10.11:

```powershell
py -3.10 -m pytest tools/dom-xss-analyzer/test_r8_ast_pilot.py tools/dom-xss-analyzer/test_r8_sanitizer.py tools/dom-xss-analyzer/test_static_context.py tools/dom-xss-analyzer/test_dxa.py -q -p no:cacheprovider --tb=short
```

Result: **95 passed**, zero failures/errors/skips. The integrated R6/R8 set
including R6 config and installed-wheel metadata tests passed **210/210**. No
external target was tested.

After the AST pilot was included, the `0.1.0` wheel was rebuilt and installed
offline into a fresh temporary venv; the installed-wheel checker passed **7/7**
and all nine module hashes matched source, wheel and installation. Wheel
SHA-256: `bde6f6cdba1190f2bee30e5b02499f7a4717a943a503e1686e1f73680535aba9`.
No hosted CI has run on the AST-pilot follow-up commit yet.

## Current evidence

- `dxa.py:438-478` retains residual taint and tracks encoder-name rebinding;
  `:543-580` models the supported Python function scope; `:644-687` keeps raw
  and context-specific HTML mitigation separate.
- `test_r8_sanitizer.py` covers mixed sanitized/raw expressions, identity
  wrappers, trusted-markup markers, assignment order and unrelated scopes.
- `test_static_context.py` covers context behavior, cross-file/name isolation,
  supported template suffixes, C# sink-only behavior and template parameters.
- `examples/safe.py:17-22` passes input as a template parameter instead of
  concatenating it into template source. `STATIC-LIMITS.md` documents the
  scanner's regex-based limits.
- `dxa.py:708-860` contains the Python-only AST pilot; `:884-887` limits its
  integration to Python files. Other languages keep their prior analysis path.

These checks support only bounded static-candidate behavior; they do not prove
browser execution, general analyzer soundness, or a vulnerability.

## Bounded R8 AST pilot

Before the fix, the labeled cases failed: tuple-unpack source flow was missed
and source-like text inside a string literal was marked HIGH. The two-case
baseline corpus measured TP/FP/FN/TN = **0/1/1/0**. An intermediate integration
run also exposed context and cross-file regressions; those were corrected.
The final corpus oracle measured TP/FP/FN/TN = **1/0/0/1**, and the affected
95-test package passed. This tiny regression corpus is a pilot, not an accuracy
estimate.

Dynamic alias/import resolution, interprocedural flow, classes/closures,
path-sensitive branch effects and configurable sanitizers remain documented
limits. They are outside this bounded roadmap acceptance. The corresponding
R8 checklist is now complete; broader analysis is future work. See [ROADMAP R8](../../ROADMAP.md).
