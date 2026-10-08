# Online article

[Read the article](report.md) on GitHub. It contains ten main sections, nine appendices, fourteen tables, thirteen references and 95 numbered equations.

`content-verification.json` records the ordered mathematical-content checksum and the article checksum. Run the reading and evidence checks from the repository root:

```sh
python scripts/check_report.py
python scripts/verify_revision.py
```

The public repository contains the reading copy, numerical code and supporting evidence. The author's typesetting files are retained locally.
