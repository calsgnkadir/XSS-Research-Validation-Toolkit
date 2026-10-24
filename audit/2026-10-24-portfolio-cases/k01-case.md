# Portfolio case 1 — stored XSS proof, fix, and retest

**Roadmap:** K01 / R5. **Role in portfolio:** primary technical case.

## Problem and scope

The repository's own disposable `k01-v1.0` training fixture models a comment
feature whose contract is to display user input as plain text. Its vulnerable
renderer inserts a stored comment into HTML without encoding. This is a local,
synthetic fixture, not a third-party or production application.

## Method and result

An anonymous writer submitted a CID canary in one comment POST. A separate,
clean reader browser context loaded the stored comment. In the vulnerable
renderer with JavaScript enabled, the browser reported the same random CID
from the payload's limited `window.__k01` marker. The test read the existing
browser global to confirm the match; it did not execute payload text through
`page.evaluate`.

The same input was checked against four negative controls: JavaScript disabled,
the fixed renderer, JSON-only response, and a normal application dialog. None
produced the canary. The renderer fix applies `html.escape(comment, quote=True)`
at the HTML text output point. The content remains visible as text and does not
create the payload's `img` element. The retained local repeat passed all five
controls in a new Python environment.

**Evidence type:** fixture-level browser execution proof, CID match, positive
and negative controls, exact fix diff, and retained clean local repeat. The
K01 acceptance record and repeat audit identify the code and browser versions.

## Limits

This demonstrates a stored-XSS proof/fix/retest workflow on a deliberately
vulnerable local training fixture. It is not a newly discovered product issue,
CVE, privileged-role attack, or general scanner-accuracy result. The fixture
has no real user accounts or production data. Its negative execution window is
500 ms and only bounds that synchronous fixture. HTML text encoding is not a
universal encoder for JavaScript, CSS, or URL contexts.

## CV wording

**English:** Built and validated a repeatable stored-XSS proof/fix/retest in a
disposable local fixture, using a CID-matched browser canary, separate writer
and reader contexts, negative controls, and HTML text-context output encoding.

**Türkçe:** Geçici yerel fixture üzerinde CID eşleşmeli browser canary'si,
ayrı yazar/okuyucu bağlamları, negatif kontroller ve HTML metin bağlamı çıktı
kodlaması kullanarak tekrar üretilebilir stored-XSS kanıtı, düzeltme ve retest
akışı oluşturdum.

## Evidence links

- [K01 fixture and case record](../../cases/k01-stored-comment/README.md)
- [Clean local repeat](../2026-10-14-r5-k01-clean-repeat/README.md)
- [Machine acceptance](../../audit/2026-10-14-r5-k01-clean-repeat/acceptance.json)
- [K01 fix diff](../../cases/k01-stored-comment/evidence/2026-10-05-verified/fix.diff)
