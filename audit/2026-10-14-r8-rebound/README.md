# R8 explicit encoder rebinding counterexample

Static HTML candidate analysis previously removed recognized encoder calls
solely by spelling. An explicit local assignment of that name to an identity
function could therefore hide a raw source. The fix tracks explicit
rebindings in source order within the supported scope. Tests cover mixed
sanitized/raw expressions, identity wrappers, Markup/SafeString, rebinding
before and after sink use, unrelated function scope and a genuine encoder
negative control. [Focused acceptance](acceptance.json): 91 passed.

The scanner still uses regex approximations. Dynamic alias/import, branch
effects and sanitizer configuration are outside this narrow acceptance.
HIGH is a static candidate, not browser execution or a CVE. [Hosted CI run 38596197488](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38596197488) passed all three jobs, including the analyzer test suite. The local 91-test count is separate from the hosted full suite.
