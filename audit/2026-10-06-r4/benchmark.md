# Benchmark run — 2026-10-06T09:39:33.629212+00:00

- corpus: `0.7.0-cve-hunt`
- scanners: dxadyn
- measurement: legacy-candidate-counts; not confirmed XSS accuracy
- dxadyn coverage: selected=3, completed=3, skipped=0, error=0, timeout=0

## Totals

| scanner | TP | FP | FN | wall (s) |
|---|---:|---:|---:|---:|
| dxadyn | 2 | 0 | 0 | 1.15 |

## Per-target

### mock-reflected-easy
- expected: reflected=1 stored=0 dom=0
- **dxadyn**: reflected=1 stored=0 dom=0 — TP=1 FP=0 FN=0 (0.45s)

### mock-reflected-escaped
- expected: reflected=0 stored=0 dom=0
- **dxadyn**: reflected=0 stored=0 dom=0 — TP=0 FP=0 FN=0 (0.35s)

### mock-stored-guestbook
- expected: reflected=0 stored=1 dom=0
- **dxadyn**: reflected=0 stored=1 dom=0 — TP=1 FP=0 FN=0 (0.35s)

