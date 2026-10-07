# Benchmark run — 2026-10-07T19:35:56.757269+00:00

- corpus: `loopback-proof/2`
- scanners: dxaprove
- measurement: correlated-browser-execution; not confirmed vulnerability accuracy
- dxaprove coverage: selected=9, completed=9, skipped=0, error=0, timeout=0, invalid=0, inconclusive=0

## Totals

| scanner | TP | FP | FN | wall (s) |
|---|---:|---:|---:|---:|
| dxaprove | 3 | 0 | 0 | 16.32 |

## Per-target

### proof-raw
- expected execution case IDs: ['proof-v2:raw:POST:/comments:comment:/comments:reader']
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- oracle: Raw HTML image onerror assigns the submitted canary.
- observation window: 400 ms
- **dxaprove**: execution TP=1 FP=0 FN=0; negative window completed=False (1.8s)

### proof-fixed
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- oracle: HTML encoding leaves the submitted image payload as text.
- observation window: 400 ms
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (1.89s)

### proof-json
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- oracle: An application/json response does not execute the submitted image markup.
- observation window: 400 ms
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (1.94s)

### proof-dialog
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- oracle: An ordinary application dialog never assigns the submitted canary.
- observation window: 400 ms
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (1.81s)

### proof-delayed
- expected execution case IDs: ['proof-v2:delayed:POST:/comments:comment:/comments:reader']
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- oracle: After 150 ms the submitted image enters innerHTML within the 400 ms window.
- observation window: 400 ms
- **dxaprove**: execution TP=1 FP=0 FN=0; negative window completed=False (1.51s)

### proof-eval
- expected execution case IDs: ['proof-v2:eval:POST:/comments:comment:/comments:reader']
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- oracle: Native direct eval reads a function-local binding before inserting the submitted image.
- observation window: 400 ms
- **dxaprove**: execution TP=1 FP=0 FN=0; negative window completed=False (1.44s)

### proof-title
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- oracle: The image payload remains inert title RCDATA without a closing title tag.
- observation window: 400 ms
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (1.92s)

### proof-textarea
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- oracle: The image payload remains inert textarea RCDATA without a closing textarea tag.
- observation window: 400 ms
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (1.98s)

### proof-resource-callback
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- oracle: Escaped payload plus a handler-free image requests its CID URL; HTTP callback is not execution.
- observation window: 400 ms
- matching resource callback count: 1 (not JavaScript proof)
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (2.03s)
