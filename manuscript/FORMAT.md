# Article

[English PDF](../paper/paper.pdf) · [Read online](report.md). Both contain ten main sections, nine appendices, fourteen tables, thirteen references and 95 numbered equations.

`content-verification.json` records the ordered mathematical-content checksum and the article checksum. Run the reading and evidence checks from the repository root:

```sh
python scripts/check_report.py
python scripts/verify_revision.py
```

The public repository contains the English PDF, online article, numerical code and supporting evidence. The author's typesetting files are retained locally; the [PDF build record](../paper/build-record-en.json) binds the published PDF to its source and mathematical content.
