# SARIF 2.1.0 export — E02

The exporter converts a saved [common R1 evidence report](EVIDENCE-CONTRACT.md)
into a SARIF 2.1.0 JSON document. It works offline and does not start a scan.

```console
dxa SOURCE --json-out evidence.json
dxa-sarif evidence.json --output evidence.sarif
```

From an uninstalled source checkout, use
`python tools/dom-xss-analyzer/dxa_sarif_cli.py evidence.json --output evidence.sarif`.
The input must be the common `--json-out` envelope. Legacy `dxa --json` lists
and separate `dxa-browser-proof/1` records are unsupported inputs.

The static `dxa`, HTTP/DOM `dxadyn`, and static-guided `dxa2dyn.py` commands
also accept `--sarif-out FILE` alongside JSON/HTML exports. Their existing
scan behavior and exit conventions remain in effect. Output paths must be
distinct. The offline converter returns 0 for a valid conversion even if the
saved report contains errors or skips; inspect `executionSuccessful` for the
recorded analysis outcome. Invalid input or a read/write error returns 2.

## Evidence mapping

| R1 category | SARIF rule | SARIF level |
|---|---|---|
| `candidate` | `dxa.observation` | `none` |
| `reflection` | `dxa.observation` | `none` |
| `sink-observed` | `dxa.observation` | `none` |
| `resource-callback` | `dxa.observation` | `none` |

These are observation categories. The exporter assigns no vulnerability score,
security severity, CWE or execution confirmation. Evidence category and triage
remain in result properties. A SHA-256 hash of the finding identifier permits
correlation with the input report without exposing its raw value. It is not a
SARIF fingerprint: common finding identifiers do not promise identity across
runs. Raw identifiers, role labels and role verification fields are omitted.

All observations produce SARIF `kind=review` and `level=none`, while retaining
the original triage. The exporter does not create suppressions or convert
operator triage into a confirmed vulnerability or a safety verdict.

Relative static source/sink paths with a valid positive integer line become
URI-encoded file locations. A usable sink is the primary location; a different
usable source is related. A source alone becomes the primary location.
Absolute paths (including the absolute paths commonly emitted by static scans),
traversal paths, URLs and paths without a positive integer line are omitted.
Paths are not rewritten relative to an assumed repository root. HTTP(S)
observations remain result rows without invented source-code locations.

Operational events are invocation notifications, separate from result rows:
error → `error`, skip → `warning`, info → `note`. Any error or skip sets
`executionSuccessful=false`. A valid empty result list is not a safety verdict.

## Input and privacy boundary

The converter requires an integer `schema_version=1`, a nonempty mode, and
finding/event lists. Findings must satisfy the R1 dataclass contract; invalid
categories, triage and verified-role claims are rejected. Events must contain
the explicit R1 event identifier, stage, kind, reason and finite timestamp.
If supplied, `meta` must be an object and `skipped_submits` must agree with the
event list. Unsupported or malformed input fails rather than becoming an empty
successful report.

Output uses an allowlist. It omits snippets, payloads, raw observations,
producer metadata, attempt/canary identifiers, role labels, evidence links and
all observation URLs. Operational events use fixed messages; raw reasons,
stages, identifiers and URLs are omitted. Relative file paths can still contain
private information and should be reviewed before sharing. Identifier hashes
are for correlation, not a guarantee against identifying predictable inputs.

The pure `dxa_sarif.to_sarif(document)` function neither changes the input nor
adds random identifiers or timestamps. Equal input yields equal output.
SARIF export does not upload to any service. Schema acceptance does not by
itself establish a particular hosting service's code-scanning support.

The format follows the [OASIS SARIF 2.1.0 standard](https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html)
and [official JSON schema](https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/schemas/sarif-schema-2.1.0.json).
