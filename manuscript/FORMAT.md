# Article

[English PDF](../paper/paper.pdf) · [Read online](report.md) · [Code and evidence](../EVIDENCE.md)

The 2026 paper is available as a PDF and a GitHub-readable article. Both are generated from the same author-side source. The online format uses display mathematics and inline formulas compatible with GitHub rendering, with stable equation numbers and reference anchors.

[equations.json](equations.json) inventories the numbered formulas. [content-verification.json](content-verification.json) records the formula sequence and article hash. The [PDF build record](../paper/build-record-en.json) binds the PDF, article and locally retained typesetting source; [PUBLICATION-MANIFEST.json](../PUBLICATION-MANIFEST.json) inventories the complete publication.

Run from the repository root:

```sh
python scripts/check_report.py
python scripts/verify_publication.py
```

These checks validate document identity, formula inventory and the recorded numerical evidence. The [computational details](../docs/COMPUTATION.md) explain the quantities evaluated by the programs, and [EVIDENCE.md](../EVIDENCE.md) supplies the result links and reproduction commands.
