# R5/K01 independent agent repeat — 14 October 2026

This is a new local reproduction by an agent separate from the agents that wrote
the K01 proof and earlier acceptance. It is **not a second human** and it ran on
the same Windows host. The open R5 criterion, “another person can reproduce from
a clean environment,” remains open. No external target was contacted.

## Starting state and command

- Repository: `C:\xss\xss-github`, branch `main`, HEAD
  `9c28601aed0cdc7fd5afc161a4dff72b577f20b6`.
- `git fetch origin` followed by `git rev-list --left-right --count HEAD...origin/main`
  returned `0 0`. The worktree was clean at the initial check. Another agent's
  `tools/dom-xss-analyzer/test_r8_sanitizer.py` edit appeared later; this run did
  not modify it.
- Windows, Python 3.10.11, installed Playwright 1.63.0, installed Chrome
  155.0.8059.79. Existing Python/Playwright was used; this particular run did
  **not** create a fresh venv. Earlier clean venv and Linux runs are separate
  historical evidence.
- Command from repository root:

  ```powershell
  py -3.10 audit/2026-10-14-r5-independent-agent-repeat/run_repeat.py
  ```

The new `proof/` directory did not exist before the command. Process exit 0
reported 5/5 controls and 5/5 distinct closed loopback ports. The independent
artifact gate checked exact submitted payload, rendered response, browser CID,
HTTP finding class, source hashes, fix diff, one POST per control, and port
closure. [Machine record](proof/acceptance.json) contains all 12 proof member
SHA-256 hashes and ports. The command did not reuse earlier acceptance output.

| Control | Expected CID | Observed CID | Result |
|---|---:|---:|---|
| Vulnerable HTML, JavaScript on | yes | yes | passed |
| Vulnerable HTML, JavaScript off | no | no | passed |
| Escaped HTML, same payload | no | no | passed |
| JSON-only response | no | no | passed |
| Ordinary application dialog | no | no | passed |

The fixture source at `cases/k01-stored-comment/prove.py:46-69` binds only
`127.0.0.1` and shuts the server down in `finally`. Submission, separate browser
reader context and CID observation are at `prove.py:105-155`; the case-specific
HTTP finding remains below `execution-confirmed` at `prove.py:156-165`.
`check_repro.py:37-140` contains the gate used in this run. The vulnerable and
fixed renderer hashes are in the machine record; `fix.diff` was matched to the
current renderer source. `git diff -- cases/k01-stored-comment` was empty.

No runtime error, timeout, or skip occurred in this run. A broad test suite and
remote CI were not run for this repeat. Browser negatives cover this synchronous
fixture and its 500 ms observation window. Anonymous author and separate reader
contexts are not two authenticated roles. This is a fixture result, not a real
product, general safety, or CVE claim.

## Independent human repeat

On a separate Ubuntu machine, a person can clone the recorded commit, install
Python 3.12, then use a new venv and output directory:

```sh
python3.12 -m venv .venv-k01-human
.venv-k01-human/bin/python -m pip install -r cases/k01-stored-comment/requirements-proof.txt
.venv-k01-human/bin/python -m playwright install chromium
.venv-k01-human/bin/python cases/k01-stored-comment/check_repro.py --output human-k01-proof
```

Record the commit, OS/Python/Playwright/browser versions, command exit code,
`result.json`, `fix.diff`, all ten request/response files, and whether all five
controls passed. Check that the same CID and payload occur in all controls,
the positive browser case matches the CID, the four negatives do not, and the
fixed HTML displays the original payload as text. `check_repro.py` captures
all five ports and checks closure during the run; an archived proof cannot
recheck historical sockets. Review evidence for private data before sharing. Report
errors, timeouts, and skipped controls separately from passes.

Roadmap: R5/K01. The general second-person acceptance remains open.
