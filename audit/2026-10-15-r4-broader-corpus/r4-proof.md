# Benchmark run — 2026-10-15T08:28:17.056212+00:00

- corpus: `loopback-proof/4`
- scanners: dxaprove
- measurement: correlated-browser-execution; not confirmed vulnerability accuracy
- dxaprove coverage: selected=17, completed=17, skipped=0, error=0, timeout=0, invalid=0, inconclusive=0
- dxaprove completed/selected coverage ratio: 17/17
- dxaprove accuracy denominator: completed rows only; incomplete rows are excluded and fail strict acceptance; selected=0 is n/a, not a safe or true-negative result

## Totals

| scanner | TP | FP | FN | wall (s) |
|---|---:|---:|---:|---:|
| dxaprove | 8 | 0 | 0 | 56.85 |

## Per-target

### proof-raw
- expected execution case IDs: ['proof-v4:raw:POST:/comments:comment:/comments:reader']
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/comments"]
- oracle: Raw HTML image onerror assigns the submitted canary.
- observation window: 400 ms
- **dxaprove**: execution TP=1 FP=0 FN=0; negative window completed=False (3.94s)

### proof-fixed
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/comments"]
- oracle: HTML encoding leaves the submitted image payload as text.
- observation window: 400 ms
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (3.48s)

### proof-json
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/comments"]
- oracle: An application/json response does not execute the submitted image markup.
- observation window: 400 ms
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (3.27s)

### proof-dialog
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/comments"]
- oracle: An ordinary application dialog never assigns the submitted canary.
- observation window: 400 ms
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (3.27s)

### proof-delayed
- expected execution case IDs: ['proof-v4:delayed:POST:/comments:comment:/comments:reader']
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/comments"]
- oracle: After 150 ms the submitted image enters innerHTML within the 400 ms window.
- observation window: 400 ms
- **dxaprove**: execution TP=1 FP=0 FN=0; negative window completed=False (2.34s)

### proof-eval
- expected execution case IDs: ['proof-v4:eval:POST:/comments:comment:/comments:reader']
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/comments"]
- oracle: Native direct eval reads a function-local binding before inserting the submitted image.
- observation window: 400 ms
- **dxaprove**: execution TP=1 FP=0 FN=0; negative window completed=False (2.19s)

### proof-title
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/comments"]
- oracle: The image payload remains inert title RCDATA without a closing title tag.
- observation window: 400 ms
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (2.91s)

### proof-textarea
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/comments"]
- oracle: The image payload remains inert textarea RCDATA without a closing textarea tag.
- observation window: 400 ms
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (2.62s)

### proof-resource-callback
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/comments"]
- oracle: Escaped payload plus a handler-free image requests its CID URL; HTTP callback is not execution.
- observation window: 400 ms
- matching resource callback count: 1 (not JavaScript proof)
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (2.72s)

### proof-sanitized-then-raw
- expected execution case IDs: ['proof-v4:sanitized-then-raw:POST:/comments:comment:/comments:reader']
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/comments"]
- oracle: The same input is rendered escaped and raw; only raw output executes the canary.
- observation window: 400 ms
- **dxaprove**: execution TP=1 FP=0 FN=0; negative window completed=False (2.62s)

### proof-identity-sanitizer
- expected execution case IDs: ['proof-v4:identity-sanitizer:POST:/comments:comment:/comments:reader']
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/comments"]
- oracle: A deliberately identity sanitizer leaves the submitted canary executable.
- observation window: 400 ms
- **dxaprove**: execution TP=1 FP=0 FN=0; negative window completed=False (2.42s)

### proof-editor-raw
- expected execution case IDs: ['proof-v4:editor-raw:POST:/notes:text:/review:editor']
- expected identity: {"method": "POST", "parameter": "text", "read_path": "/review", "role": "editor", "source_path": "/notes"}
- expected proof frame paths: ["/review"]
- oracle: The editor-role fixture renders the submitted note as raw HTML.
- observation window: 400 ms
- **dxaprove**: execution TP=1 FP=0 FN=0; negative window completed=False (2.34s)

### proof-editor-fixed
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "text", "read_path": "/review", "role": "editor", "source_path": "/notes"}
- expected proof frame paths: ["/review"]
- oracle: The editor-role fixture HTML-encodes the submitted note.
- observation window: 400 ms
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (3.77s)

### proof-iframe
- expected execution case IDs: ['proof-v4:iframe:POST:/comments:comment:/comments:reader']
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/frame"]
- oracle: The submitted canary executes in the fixture's explicitly expected same-origin /frame.
- observation window: 400 ms
- **dxaprove**: execution TP=1 FP=0 FN=0; negative window completed=False (5.14s)

### proof-comment
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/comments"]
- oracle: The submitted image remains inside an HTML comment without a comment terminator.
- observation window: 400 ms
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (5.36s)

### proof-template
- expected execution case IDs: []
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/comments"]
- oracle: The submitted image remains in inert template content outside the active document.
- observation window: 400 ms
- **dxaprove**: execution TP=0 FP=0 FN=0; negative window completed=True (4.48s)

### proof-template-activated
- expected execution case IDs: ['proof-v4:template-activated:POST:/comments:comment:/comments:reader']
- expected identity: {"method": "POST", "parameter": "comment", "read_path": "/comments", "role": "reader", "source_path": "/comments"}
- expected proof frame paths: ["/comments"]
- oracle: The application imports the submitted image from inert template content into the active document.
- observation window: 400 ms
- **dxaprove**: execution TP=1 FP=0 FN=0; negative window completed=False (3.98s)

