> **Historical / experimental reference — 2026-09-28 audit.** Capability and completion claims below are not a current guarantee. See [verified status](../STATUS.md) and [current acceptance criteria](../ROADMAP.md). A raw marker, scanner severity, callback or zero findings alone does not establish execution, a vulnerability or safety.

# Benchmark harness (Phase 0.5)

Compares `dxadyn` against optional external scanners (DalFox, XSStrike) on a
reproducible corpus. Every future roadmap phase lands with a delta against
this baseline — no more "feels faster / catches more" claims.

## Design

- **Zero third-party deps.** Runner and mock targets use stdlib only.
- **External scanners are opt-in.** If DalFox / XSStrike aren't on `PATH`,
  the corresponding rows say `skipped` and CI still passes.
- **Mock targets run in CI without docker.** A stdlib `http.server`
  exposes vulnerable + safe endpoints. Real OSS targets (Bludit, DVWA,
  Juice Shop, etc.) join via docker-compose as the corpus grows.
- **History is append-only** (`bench/history.jsonl`). Every run — local
  or CI — leaves a durable line so trends can be reconstructed later.
- **Scoring is symmetric.** True positives, false positives, and false
  negatives are all counted; a scanner that FPs on the safe target loses
  points, not gains them.

## Files

| File | Purpose |
|---|---|
| `targets.json` | Corpus definition (id, kind, url, expected findings, budget) |
| `mock_target.py` | Stdlib HTTP server with known-vulnerable + known-safe endpoints |
| `run.py` | Runner: spins targets, calls scanners, scores, writes report |
| `test_bench.py` | Pytest — mock endpoint semantics + score math + end-to-end |
| `results-YYYY-MM-DD.md` | Latest human-readable report (regenerated per run) |
| `history.jsonl` | Append-only totals per run (for trend graphs) |

## Usage

```bash
# dxadyn only, full mock corpus
python bench/run.py

# add external scanners if installed
python bench/run.py --with dalfox,xsstrike

# subset of targets
python bench/run.py --targets mock-reflected-easy,mock-stored-guestbook

# custom output path
python bench/run.py --out bench/results-2026-09-26.md
```

Exit code is non-zero only when `BENCH_STRICT=1` and dxadyn has any FN
on the mock corpus — that's the regression gate CI uses.

## Corpus (v0.5.0-mvp)

3 mock targets today; grows to 20 by end of Phase 1:

| id | kind | expect |
|---|---|---|
| `mock-reflected-easy` | mock | reflected=1 |
| `mock-reflected-escaped` | mock | (safe — nothing) |
| `mock-stored-guestbook` | mock | stored=1 |

Roadmapped docker targets (Phase 1 onwards): Bludit 3.16.2, DVWA, Juice
Shop, WebGoat, Prestashop, OpenCart, Cockpit CMS, Directus, Rundeck, plus
the three own-hardened controls (hotel-platform, wallet-api, mahrem).

## How results are scored

For every (target, scanner, vulnerability class) triple:

| expected | observed | outcome |
|---|---|---|
| N > 0 | 0 | 1 FN |
| N > 0 | K ≥ 1 | min(N, K) TP; excess K – N as FP |
| 0 | K ≥ 1 | K FP |

A skipped scanner (not on PATH) contributes zeros to every column. This
matters: a scanner absent from a run is not a scanner that scored zero.

## Extending

- **Add a mock target:** implement a handler in `mock_target.py`, list
  it in `targets.json` with expected counts.
- **Add a docker target:** flip `kind` to `"docker"` and include a
  `compose_file` path; the runner currently notes docker targets as
  non-runnable in-session (docker adapter lands in Phase 1).
- **Add a scanner:** write a `run_<name>(target, base_url, budget)`
  adapter in `run.py`, register it in `SCANNERS`, and add `--with <name>`.

## Honest limits

- Mock endpoints are proxies for real behavior, not replacements. Docker
  targets (real CVEs) are what will move the needle on external-scanner
  parity.
- The parsers for DalFox / XSStrike output are heuristics; they'll drift
  with those tools' version upgrades. Every parser change ships with a
  fixture-based test.
- One-run TP/FP counts are noisy on flaky targets. `history.jsonl`
  exists so we can look at trends, not single runs.
