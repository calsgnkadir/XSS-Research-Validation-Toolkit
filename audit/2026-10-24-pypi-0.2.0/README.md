# PyPI 0.2.0 release record — 24–25 October 2026

## Source and release

- Source commit: `8891219c3899f3208db9d19bff1990f96544dac5`.
- Tag: `v0.2.0` (`6f567d99b776a45b23dea0d27a933163a3bd50c2`).
- GitHub Release: https://github.com/calsgnkadir/XSS-Research-Validation-Toolkit/releases/tag/v0.2.0
- Historical `v0.1.0` GitHub Release was left unchanged.
- Packaging scope only: version, README install instructions, changelog grouping, and ignoring local `dist/`; no source behavior changes.

## Build and TestPyPI proof

Built sdist and wheel using the isolated Python 3.11 packaging environment.
`twine check dist/*` passed for both files. TestPyPI accepted both artifacts.
A fresh Python 3.11 venv installed `dxa-research-toolkit==0.2.0` from
`https://test.pypi.org/simple/`; `dxa --help`, `dxadyn --help`,
`dxaprove --help`, and `dxa-sarif --help` all exited 0 (4/4).

- Wheel SHA-256: `CD5C83ECD9C904878D66C1623187CAAA03BC4CFF9229BEE949807CA4639912CD`
- sdist SHA-256: `47E313A2CBBC925FE67D8640A01DE5874F0647D3A2299FA51BB8DB7C9B77AF96`

## Production publication and install gate — 25 October

The same two artifacts were uploaded to production PyPI with
`twine upload --repository pypi dist/dxa_research_toolkit-0.2.0*`. Twine
reported success. The public PyPI JSON endpoint confirmed name
`dxa-research-toolkit`, version `0.2.0`, and two uploaded files; project page:
https://pypi.org/project/dxa-research-toolkit/0.2.0/.
The SHA-256 digests reported for both live files match the local artifact hashes
recorded above.

A new Python 3.11 venv installed `dxa-research-toolkit==0.2.0` from the
default production index. `dxa --help`, `dxadyn --help`, `dxaprove --help`,
and `dxa-sarif --help` each exited 0 (4/4). No toolkit source tests were run
as part of this packaging-only release.
