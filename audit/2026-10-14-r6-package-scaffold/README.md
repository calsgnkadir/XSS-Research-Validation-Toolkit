# R6 installable CLI scaffold

The local project metadata builds a developer package at version
0.0.0.dev0. Core dependencies are empty. The browser extra pins Playwright
1.63.0; Chromium is installed separately. Three entrypoints expose the
existing dxa, dxadyn and dxaprove main functions.

A fresh Windows Python 3.10 venv installed the project and browser extra.
All three installed CLI help commands worked. The installed dxaprove module
loaded from site-packages and its disposable Chrome demo produced matching
browser execution. [Acceptance details](acceptance.json). Required CI now
installs the package and checks entrypoints. [Hosted CI run 38596197488](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/38596197488) passed all three jobs, including the package install/help step. [Step record](remote-ci.json). Hosted installed browser demo was not run; the local packaged Chrome demo is separate.

This establishes a local installation path, not a published or tagged
release. Config precedence, package docs completeness and full R6 release
gate remain open.
