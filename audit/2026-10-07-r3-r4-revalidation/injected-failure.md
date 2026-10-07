# Benchmark run — 2026-10-07T19:36:05.381157+00:00

- corpus: `loopback-proof/2`
- scanners: dxaprove
- measurement: correlated-browser-execution; not confirmed vulnerability accuracy
- dxaprove coverage: selected=2, completed=1, skipped=0, error=1, timeout=0, invalid=0, inconclusive=0

## Totals

| scanner | TP | FP | FN | wall (s) |
|---|---:|---:|---:|---:|
| dxaprove | 0 | 0 | 0 | 2.76 |

## Per-target

### proof-raw
- expected execution case IDs: ['proof-v2:raw:POST:/comments:comment:/comments:reader']
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- oracle: Raw HTML image onerror assigns the submitted canary.
- observation window: 400 ms
- **dxaprove**: error (not evaluated)

### proof-fixed
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- oracle: HTML encoding leaves the submitted image payload as text.
- observation window: 400 ms
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (2.23s)
