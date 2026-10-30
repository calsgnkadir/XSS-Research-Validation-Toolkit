# PyPI description refresh and portfolio — 30 October 2026

Roadmap: R6, K01/R5, A01–A03. Base checkout `dc04da3`; main matched
origin/main after fetch and the starting working tree was clean.

Three native roles completed disjoint work: report_frontend_specialist wrote
`docs/K01-CASE-STUDY.md`; xss_security_researcher wrote the historical CVE
review; scanner_engine_specialist prepared pyproject version/readme and the
dedicated PyPI description. Coordinator reviewed evidence and commands,
added package URLs, integrated documents and performed release validation.
Workers were closed; no active background work remains. Native invocation was
observed; TOML-loader behavior is not separately established.

## Published package

Published [0.2.1](https://pypi.org/project/dxa-research-toolkit/0.2.1/) as a
documentation/metadata maintenance release. Existing 0.2.0 files remain intact.
The separate `docs/PYPI-README.md` uses absolute GitHub links and current
installed-package commands. No runtime module was edited.

New Python 3.10.11 venv on Windows: build succeeded, twine check passed 2/2,
wheel install succeeded, production-PyPI reinstall succeeded, four CLI help
commands exited 0. Production JSON description matches source UTF-8 text and
both published artifact SHA-256 values match local files. All 11 wheel module
files equal current source bytes. [Machine record](result.json).

Commands (interpreter: `.dxa/pypi-refresh-021/Scripts/python.exe`):

```text
-m build --outdir .dxa/pypi-refresh-021-dist
-m twine check .dxa/pypi-refresh-021-dist/*
-m pip install --no-deps .dxa/pypi-refresh-021-dist/dxa_research_toolkit-0.2.1-py3-none-any.whl
-m twine upload --non-interactive --disable-progress-bar .dxa/pypi-refresh-021-dist/*
-m pip install --force-reinstall --no-deps --index-url https://pypi.org/simple dxa-research-toolkit==0.2.1
```

Old venv launchers were unusable from missing interpreter paths; the new
environment required execution outside the filesystem sandbox. Initial
PowerShell JSON comparison misdecoded UTF-8; Python requests comparison passed.
No credentials or private captures were printed or included.

## Content and limits

[K01 article](../../docs/K01-CASE-STUDY.md) presents retained lab proof/fix/retest;
no new browser test is claimed. [CVE review](../../docs/CVE-RESEARCH-REVIEW-TR.md)
finds missing verification for historical WordPress duplicate/SQLi claims;
Bludit CVE credit belongs to a different researcher. Known BCrypt reproduction
is separate from discovery credit. Primary advisories and safe CV wording are
linked in the review. No external target test, disclosure or message occurred.
A05 remains frozen/partial and K04 still requires its historical artifact.

No toolkit test suite or browser suite was rerun. Hosted CI is separate from
these local packaging checks. Git delivery is recorded in current STATUS.
