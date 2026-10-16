# R8 current-source review — 2026-10-16

## Scope and result

At base commit `84839a47c2f64e50ecf9a9bd737fd6e1fe31d712`, the native
`xss_security_researcher` reviewed the remaining R8 static-analyzer criteria
and current source/tests. No new reproducible defect was found, so this review
made no R8 code changes. The coordinator independently ran the focused R8
tests on Windows / Python 3.10.11 as part of a 156-test R6/R8 regression run.

```powershell
py -3.10 -m pytest tools/dom-xss-analyzer/test_r8_sanitizer.py tools/dom-xss-analyzer/test_static_context.py -q -p no:cacheprovider --tb=short
```

R8 subset: **41 passed**, zero failures/errors/skips. The combined command also
included R6 config and installed-wheel metadata tests and completed **156
passed**. No external target was tested.

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

These checks support only bounded static-candidate behavior; they do not prove
browser execution, general analyzer soundness, or a vulnerability.

## Remaining R8 work

The one-language AST pilot and labeled positive/negative corpus measurement
remain open. Dynamic alias/import resolution, branch effects and configurable
sanitizers remain documented limits. They are not silently counted as passed
or closed by the 41-test run. See [ROADMAP R8](../../ROADMAP.md#r8--statik-analiz-ve-fixture-doğruluğu-bot-açık).
