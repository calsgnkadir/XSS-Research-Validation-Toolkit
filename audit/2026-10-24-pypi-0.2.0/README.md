# PyPI 0.2.0 release record — 24 October 2026

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

## Production status

Production `twine upload dist/*` returned HTTP 403. The public PyPI JSON
endpoint returned 404 for `dxa-research-toolkit` version `0.2.0` after that
attempt. No production package upload is confirmed; a valid production token
with project upload permission is required before retrying. Final clean PyPI
installation and production publication record remain pending.
