# Article

[English PDF](../paper/paper.pdf) · [Read online](report.md) · [Revision](../docs/REVISION-2026-10-26.md).

The current article contains ten main sections, nine appendices, fourteen tables, thirteen references and 97 numbered equations. Its 179 display and 521 inline formulas are generated from the same author-side source as the PDF.

`content-verification.json` records the revised formula sequence and article hash. `numbered-equation-baseline.json` preserves the preceding numbered formulas: 94 remain identical, the introductory equation (1.1) is replaced, and (2.9)–(2.10) are added. The original numerical code and evidence identities remain unchanged.

Run from the repository root:

```sh
python scripts/check_report.py
python scripts/verify_revision.py
```

The [PDF build record](../paper/build-record-en.json) binds the PDF, article and locally retained typesetting source. These checks verify document identity, preserved formulas and recorded numerical evidence; they do not independently certify the proofs.
