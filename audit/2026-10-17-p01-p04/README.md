# P01/P04 portfolio and demo acceptance — 2026-10-17

Baseline: `740e5bc3e9c37e72474ed571c30d799db0a6911f`, Windows, Python 3.10.11.
The final C/K reviews corrected historical claims to match the retained evidence
and documented evidence gaps. This record binds the portfolio selections and
reproducible demo; it does not claim target vulnerability validation.

## P01 — three selected evidence paths

The root README and writeup index present three distinct routes:

1. **Proof → fix → retest:** K01's local stored-comment case with a separate
   reader context, matching CID, four negative controls, and HTML text-context
   encoding. It is a training fixture, not a product or CVE claim.
2. **Measured tool-test failure → regression:** the R9 serial-HTTP fixture
   failures and threaded-server correction, followed by the full Chrome DOM
   suite. This measures fixture reliability, not scanner accuracy.
3. **Controlled research replay:** historical stored candidates replayed in
   fresh writer/reader-admin loopback fixtures with escaped controls. Two raw
   Dalfox candidates produced dialogs; other outcomes remain inconclusive. No
   scanner rerun or ranking is claimed.

Sources: [K01 case](../../cases/k01-stored-comment/README.md),
[R9 fixture audit](../2026-10-16-r6-r9-final-source/README.md),
[R4 replay audit](../r4-proof-experiment-2026-10-16/README.md), and the
[C/K claim and evidence inventory](../2026-10-17-k-evidence/README.md).

## P04 — clean install and local fixture runs

The [demo guide](../../docs/PORTFOLIO-DEMO.md) documents a clean Python 3.10
environment, the pinned browser extra, `dxaprove --demo`, K01 local profile,
expected evidence, limitations, and unique output paths.

The documented Windows clean-venv package command succeeded in
`.venv-p04-20261017`:

```powershell
py -3.10 -m venv .venv-p04-20261017
.venv-p04-20261017\Scripts\python.exe -m pip install --no-input '.[browser]'
.venv-p04-20261017\Scripts\python.exe -m playwright install chromium
```

The installed `.venv-p04-20261017\Scripts\dxaprove.exe --demo` command
returned exit 0 with `execution-observed`, triage `unreviewed`, checked HTTP
and browser sessions, and one matching loopback canary. Playwright was 1.63.0;
Chromium was 153.0.8010.12. The retained
[`dxaprove-installed-demo-result.json`](dxaprove-installed-demo-result.json)
SHA-256 is `DF066619B35E364D9B7E93CF9F8A94E699F83C9F62E2BCCE2A7D84F9794A02D9`.
This is the package's own fixture, not a vulnerability result.

From that environment the documented K01 command also passed **5/5 controls**
and verified **5/5 distinct fixture ports closed**:

```powershell
.venv-p04-20261017\Scripts\python.exe cases/k01-stored-comment/check_repro.py `
  --profile local --output .dxa/k01-p04-installed-demo-20261017
```

Environment: Windows, Python 3.10.11, Playwright 1.63.0, Chromium
153.0.8010.12. The copied
[`k01-installed-acceptance.json`](k01-installed-acceptance.json) SHA-256 is
`698BAF306A41DB68F7EA979D2319BBD219FFFAAFD780F972FE5EF619F3E5EBF9`;
[`k01-installed-result.json`](k01-installed-result.json) SHA-256 is
`66F75FA1A399824EF042684F63E9755D5C3520CD1A9DBE1BE62DA224A5D453E6`.
The gate's source/proof hashes bind this run; the complete earlier accepted
proof package is retained under
[`audit/r5-final-acceptance-2026-10-16`](../r5-final-acceptance-2026-10-16/README.md).

## Scope and closeout

The C review corrected C01–C12; C13's stale writeup-index claims were corrected
in the same delivery. The K review completed the screenshot inventory and
publication copies, SQLi/JWT/BOLA evidence inventory, defense guidance, and
report-label preview. Missing raw historical evidence and browser proof remain
explicit; no historical claim is promoted to a verified target finding.

These are local Windows fixture runs, not new hosted CI, an independent human
run, target assessment, or public package release. P01 and P04 are complete at
their stated scope. P02 and P03 remain open; the `0.1.0` candidate is not tagged
or published.
