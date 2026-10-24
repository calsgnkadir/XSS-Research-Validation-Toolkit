# K03 independent local retest — 24 October 2026

## Scope and provenance

An independent QA + Security Lab specialist reran the K03 SQLi, unsigned JWT,
modified-signature and two-account basket controls against the already-present
local OWASP Juice Shop image. This is a new bounded reproduction; it does not
validate the date, target version or traffic of the historical writeups.

| Item | Observed value |
|---|---|
| Product/version | OWASP Juice Shop 20.2.0 |
| Image ID | `sha256:0cec496d878c6855a1c81694c9f91564082f418b84aece87538adb8850d2437e` |
| Repo digest | `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e` |
| Local tag | `bkimminich/juice-shop:latest` (the immutable image ID above was run; no pull) |
| Capture script SHA-256 | `b85503c50e6942d5a05d6d5d8c37f979bc9679af8fb9869367ce51669c03a047` |
| Image `package.json` SHA-256 | `e582b8e132fb6fa82e10f496e8ee55c8d9617f4ba19fc50ad87547bf8d281d87` |
| `build/routes/login.js` SHA-256 | `047045a8bbb4fd8a5af1f34e8339a37edb59d7dca9d5e5f6ec22044fd8b8c721` |
| `build/routes/basket.js` SHA-256 | `2ecc5259f8886d720d27899e69083e60cbc9482348e3c3ef662b706a3f266787` |
| `build/routes/currentUser.js` SHA-256 | `27efa0973dd94127a2938b34a2017edcce5923b2fde861f79dd3dda8a3e25e42` |
| `build/lib/insecurity.js` SHA-256 | `0f21e927a94a4cb9116f77b8bd7b883f5ba53813971bbfd8393f998e0fc63a0d` |

Only the new `dxa-k03-independent-20261024` Docker container and network were
created. The network was verified `Internal=true`; the container used the image
ID above with `--pull=never`, no published ports, no mounts and no restart
policy. Requests used the test script's `http://127.0.0.1:3000` origin from
inside the container. The network had no external egress. The old stopped
`juice-shop` container and `dxa-k03-loopback-20261019` network were not reused
or changed.

Reproduction steps:

```powershell
docker network create --internal dxa-k03-independent-20261024
docker run --pull=never --detach --name dxa-k03-independent-20261024 --network dxa-k03-independent-20261024 --restart no sha256:0cec496d878c6855a1c81694c9f91564082f418b84aece87538adb8850d2437e
docker cp audit/2026-10-19-k03-loopback-reproduction/capture_local.js dxa-k03-independent-20261024:/tmp/k03_capture.js
docker exec dxa-k03-independent-20261024 /nodejs/bin/node /tmp/k03_capture.js
```

The script generated new random `example.invalid` users. Its console output
contained only boolean/status summaries and the SHA-256 of the private capture.
The raw capture is preserved locally at the ignored path
`.dxa/k03_private_capture_20261024.json` (37,567 bytes; SHA-256
`f8dbd5bcdb318021dca0fce23ed40a25a053e6b36f36ab05b4de1784252ef2d0`). It is
not part of this audit and must not be committed or shared. The older private
capture was not overwritten.

## Observed results

The script completed successfully and recorded **17 HTTP requests**:

| Control | Observed result |
|---|---|
| Normal invalid-password login | HTTP 401 |
| SQLi-shaped login negative/positive | Normal login 401; the SQLi-shaped login returned HTTP 200 and a token whose `whoami` identity was the local admin account |
| Two synthetic accounts | Both registrations returned 201; both logins returned 200; each `whoami` matched its own account |
| Basket ownership BOLA pair | Account A read its own basket (200) and account B's seeded basket (200); response owner matched B and included the synthetic item. Anonymous read of B's basket returned 401 |
| Unsigned JWT (`alg:none`) | `whoami` mapped to the local admin identity; a read of A's synthetic basket returned 200 and owner matched A |
| Modified-signature control | `whoami` returned HTTP 200 with no user identity; this is not described as HTTP rejection |

These results reproduce the specific behaviors in this Juice Shop 20.2.0 image.
They do not establish historical writeup sessions, behavior across Juice Shop
versions, CVE attribution, remediation, or a new finding in the toolkit's
software.

## Cleanup and limits

Only the new container and network were stopped and removed. Verification
showed neither newly named resource remained; the pre-existing Juice Shop
container was still `exited` on the same image ID, and the prior K03 network
remained present and internal. No volumes were created. No public target or
external host was contacted. This retest did not run the analyzer, browser, or
the toolkit test suite, and did not exercise a fixed Juice Shop build.
