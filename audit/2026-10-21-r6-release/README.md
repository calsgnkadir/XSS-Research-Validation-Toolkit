# R6 v0.1.0 GitHub Release — 21 October 2026

## Publication

The user authorized publication of the v0.1.0 Git tag and GitHub Release, with
PyPI upload explicitly excluded. Annotated tag `v0.1.0` points to source commit
`d7d1bd666ae4fe5643bf0574658d8d8a0f4411a0`. The public GitHub Release is
[dxa-research-toolkit 0.1.0](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/releases/tag/v0.1.0),
published `2026-10-21T18:22:28Z`.

The release has one uploaded asset:

- `dxa_research_toolkit-0.1.0-py3-none-any.whl`
- Size: 104,949 bytes
- SHA-256: `111a0f6c43c3d6710c9c30434fb402604cec9fa5ee69845a44b6d14023195399`
- Download: [wheel asset](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/releases/download/v0.1.0/dxa_research_toolkit-0.1.0-py3-none-any.whl)

GitHub's public release API reports this filename, size, uploaded state, and
`sha256:111a0f6c43c3d6710c9c30434fb402604cec9fa5ee69845a44b6d14023195399`
digest. This matches the local artifact hash recorded during the final
release-wheel rebuild. No PyPI upload was made.

## Acceptance evidence

- The release wheel was rebuilt after README release-channel wording was
  updated, installed offline into a fresh Python 3.10 virtual environment, and
  passed the installed-wheel gate **7/7**. All nine packaged module hashes
  match current source, wheel, and installed copies. See the
  [gate evidence](../2026-10-21-r6-current-source/release-installed-wheel-gate.json)
  and [rebuild record](../2026-10-21-r6-current-source/README.md).
- The unchanged application modules passed focused `dxadyn` tests **271/271**
  before release-note-only documentation changes.
- Hosted [general CI run 39650964831](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/39650964831)
  and [K01 Linux run 39650964757](https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/actions/runs/39650964757)
  completed successfully for the tagged source commit.

This release is a research-support prototype. It does not claim general
scanner accuracy or a newly discovered vulnerability. No PyPI distribution
was published; the user explicitly excluded PyPI from this release.
