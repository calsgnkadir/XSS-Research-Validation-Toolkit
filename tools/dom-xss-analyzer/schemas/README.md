# Vendored SARIF schema

`sarif-schema-2.1.0.json` is the unmodified OASIS SARIF 2.1.0 OS JSON Schema,
retrieved on 2026-10-23 from:

https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/schemas/sarif-schema-2.1.0.json

SHA-256: `AD6DB49878699B091F3EEB765B6E29E92A34BAD4DA88664D000C923B549C3A25`.
This digest covers the original download bytes, including CRLF line endings.
The repository's narrow `.gitattributes` entry disables text conversion for
this schema so Windows and Linux checkouts retain the same official bytes.
The LF-normalized copy has a different digest; it is not an accepted substitute
for the recorded download. The provenance test requires the exact digest;
export tests validate generated SARIF against this schema.

It is included for offline test-time validation only; the runtime exporter has
no `jsonschema` dependency. The source schema identifies itself as the SARIF
2.1.0 JSON Schema. Its upstream `$id` is
`https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json`;
the retrieval URL above is the OASIS published OS schema URL.
