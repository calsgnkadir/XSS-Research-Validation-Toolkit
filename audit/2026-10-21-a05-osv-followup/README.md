# R7 / A05 OSV public-record follow-up — 21 October 2026

## Scope

One read-only request was attempted against OSV's official query API for the
Maven package identity recorded in the prior A05 audit:

`pkg:maven/com.hotelapp/hotel-student-platform@0.0.1-SNAPSHOT`

Request: `POST https://api.osv.dev/v1/query`, JSON body
`{"package":{"purl":"pkg:maven/com.hotelapp/hotel-student-platform@0.0.1-SNAPSHOT"}}`.
The request was attempted at **2026-10-21 19:03:16 UTC** using PowerShell
`Invoke-WebRequest` with a 20-second timeout.

## Result

The client reported **“Unable to connect to the remote server”** before an
HTTP response was received. HTTP status: **not available**. No response JSON
was received or parsed; result count and advisory IDs are **not available**.
This is an endpoint/network access limitation, not an empty OSV result. No
retry or alternate query was made.

## Status and limits

This attempt adds no evidence about whether OSV contains an advisory for the
package. It does not resolve the earlier NVD 406 challenge or the incomplete
CVE.org search. A05's public-record status remains partial/inconclusive, no
known-record absence is asserted, and **R7 remains open**. No product endpoint
was contacted, and no login, scan, exploit, disclosure, or message occurred.

Reference: [OSV API documentation](https://google.github.io/osv.dev/api/).
