# Benchmark run — 2026-10-13T17:40:48.698598+00:00

- corpus: `0.7.0-cve-hunt`
- scanners: dxadyn
- measurement: legacy-candidate-counts; not confirmed XSS accuracy
- dxadyn coverage: selected=1, completed=1, skipped=0, error=0, timeout=0, invalid=0, inconclusive=0

## Totals

| scanner | TP | FP | FN | wall (s) |
|---|---:|---:|---:|---:|
| dxadyn | 1 | 0 | 0 | 0.41 |

## Product controls (by-design; excluded from vulnerability scoring)

### bludit-3.16.2-admin-controls
- status: passed; cleanup: passed; triage: by-design
- case | expected execution | observed execution | matched
- raw-admin-content | true | true | true
- escaped-admin-content | false | false | true

## Per-target

### mock-reflected-easy
- expected: reflected=1 stored=0 dom=0
- **dxadyn**: reflected=1 stored=0 dom=0 — TP=1 FP=0 FN=0 (0.41s)
