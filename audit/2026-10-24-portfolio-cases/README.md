# Portfolio case pack — evidence-reviewed, 25 October 2026

This internal pack is ready to adapt for a CV or portfolio. The case briefs
summarize retained evidence; they do not add acceptance claims. No new tests,
target requests, or external publication were performed during this editorial
pass.

## Recommended order

1. **Primary — [K01 stored-XSS proof/fix/retest](k01-case.md).** A bounded
   execution proof and output-encoding fix in the repository's disposable local
   training fixture. It is not a third-party product finding or scanner score.
2. **Second — [E05 textarea parser context](e05-case.md).** A measured inert
   marker-placement result in a local Chromium oracle. JavaScript execution,
   confirmed vulnerability, and product impact were not established.
3. **Short supporting example — [BCrypt/CVE applicability](bcrypt-case.md).**
   One local synthetic-account reproduction of a known upstream Spring Security
   issue and its remediation. No CVE was assigned to the application; A05
   remains partial.

## CV wording

Use the concise English and Turkish bullets in
[PORTFOLIO-CV-DRAFT.md](../../docs/PORTFOLIO-CV-DRAFT.md). Tailor them to the
role and available space without removing the local-fixture and evidence limits.

## Public toolkit version

The current package is [`dxa-research-toolkit==0.2.0`](https://pypi.org/project/dxa-research-toolkit/0.2.0/),
with the `dxa-sarif` CLI and E05 context extension. Install it with:

```console
python -m pip install dxa-research-toolkit
```

The `v0.1.0` GitHub Release is historical and does not contain the 0.2.0
changes. Keep release-version claims separate from the case evidence.

## Sharing boundaries

- Keep K01 identified as the repository's disposable training fixture.
- Do not identify the private application in the BCrypt example unless its
  owner approves naming it. The linked reproduction/remediation records are
  internal evidence references; sanitize and review them before linking in a
  public portfolio.
- Do not attach raw request/response captures, tokens, cookies, account data,
  ignored `.dxa` files, or private deployment details.
- Keep test totals tied to their dated selectors. They do not establish broad
  product accuracy, exploit counts, severity rankings, or certification.
- This pack is not externally published; public use remains a separate choice.
