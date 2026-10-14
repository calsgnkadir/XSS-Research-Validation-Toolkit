# R5, R8 and R6 recheck — 14 October 2026

Starting HEAD `9c28601aed0cdc7fd5afc161a4dff72b577f20b6` on `main` matched
`origin/main` (0 ahead, 0 behind); the initial worktree was clean. The earlier
R5 Linux artifact, R8 static regression and R6 package install belong to code
commit `d41c1cd72164e28526e3a6900aa6ed0d20734a11`, not to this follow-up.

## R8 finding and correction

The earlier rebinding logic isolated ordinary Python function locals but also
discarded an explicit module-level encoder assignment made before the function.
The local fixture
`html.escape = lambda value: value; def render(): ... HTMLResponse(html.escape(q))`
therefore returned a MEDIUM candidate even though the recognized request source
flowed through the identity function. A new regression first failed with one
failure and 12 passes. The scope now carries only earlier, unindented encoder
rebindings into a Python function; unrelated module taint and sibling function
assignments remain excluded. The affected `test_r8_sanitizer.py`,
`test_static_context.py`, and `test_dxa.py` package passed **92/92** with
Python 3.10.11 on Windows:

```text
py -3.10 -m pytest tools/dom-xss-analyzer/test_r8_sanitizer.py tools/dom-xss-analyzer/test_static_context.py tools/dom-xss-analyzer/test_dxa.py -q -p no:cacheprovider --tb=short
```

Local byte SHA-256: `dxa.py`
`b70e163303d1f670a829d89e021058c1e9177a685abe7c5dff1a38cb6b637c7e`,
`test_r8_sanitizer.py`
`978e0365126abdc31db2847a79e9840bc4c358148b43ebb4a1d46cfe0da64f19`.
Git checkout line endings can yield a different Git blob digest.

This is a static source-to-sink candidate, not observed browser execution or
a product vulnerability. Runtime rebinding order, branches, aliases, nested
scopes and sanitizer configuration remain outside the regex model.

## R6 wheel review

With the previously prepared build venv, `pip wheel --no-deps
--no-build-isolation . --wheel-dir .dxa/r6-recheck` created a 94,775-byte
`dxa_research_toolkit-0.0.0.dev0-py3-none-any.whl` (SHA-256
`25da853433614bdb965b70a7ea51d3bb999cf8a6c5b2dc4a1d6695a075a21e4b`).
Its archive contained the nine declared Python modules and package metadata;
there were no audit, local database, or user files. A new ignored Python 3.10
venv installed that wheel with `pip install --no-deps`. From `.dxa/`, outside
the source directory, `dxa`, `dxadyn`, and `dxaprove --help` each exited 0,
and all three imported from the new venv's `site-packages`. An installed `dxa`
scan of the local `examples/safe.py` returned two MEDIUM static candidates
and exit 1 under its finding exit convention; it did execute. This follow-up
did not rerun the earlier packaged Chrome demo or create a release tag.

The system Python lacked `bdist_wheel` for `--no-build-isolation`, so the first
wheel command failed at build-tool setup. The same command with the existing
build venv succeeded; this was an environment prerequisite, not a package
source failure.

## R5 independent agent repeat

A separate QA agent created a new [K01 proof](../2026-10-14-r5-independent-agent-repeat/README.md)
on the owned 127.0.0.1 fixture. Its new output recorded 5/5 controls, one POST
per control, the same CID/payload, five distinct closed fixture ports, and
the expected vulnerable/fixed/JSON/JavaScript-disabled/dialog behavior. The
coordinator compared 12 proof-member and three source SHA-256 values with the
checkout; there were zero mismatches. No K01 source code changed. The agent
used the existing Python 3.10/Playwright 1.63.0 installation and Chrome on
the same Windows host. It was a distinct agent run, **not a second human or a
clean-machine acceptance**. The R5 roadmap checkbox remains open. The agent's
record includes exact steps for a human repeat on a separate Ubuntu machine.
The coordinator also ran the K01 fixture and gate tests: **13/13 passed**,
zero failures/errors/skips, with
`py -3.10 -m pytest cases/k01-stored-comment/test_fixture.py cases/k01-stored-comment/test_repro_gate.py -q -p no:cacheprovider --tb=short`.

This recheck did not contact external targets or rerun Docker. Previous hosted
CI results are historical until a new commit's workflows complete.
The canonical generated `proof/fix.diff` contains two blank context lines with
the required unified-diff prefix space. Plain `git diff --cached --check`
reports only those two lines; changing them would invalidate the exact fix-diff
gate and recorded SHA-256. The staged check with `core.whitespace=-blank-at-eol`
is used for this evidence bundle.
