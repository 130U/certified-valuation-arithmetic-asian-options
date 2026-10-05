# Manuscript formats

- `report.md` is the complete GitHub-readable paper, including the abstract, ten main sections, seven appendices, and twelve linked references.
- `report.json` contains the same content as structured blocks for verification.
- `report-source.tex` is the public source used by `python scripts/build_report.py`. It contains the abstract, body, and bibliography, without a document-class preamble.
- `implementation-section.tex` supplies the public Appendix G interface description.
- `content-verification.json` records exact formula-preservation checks and artifact hashes.

The builder uses the Python standard library and preserves all 147 display-math occurrences, 373 inline-math occurrences, and 88 distinct equation tags. Display formulas use GitHub's fenced `math` blocks. Inline formulas use dollar-backtick delimiters to protect TeX characters from Markdown escaping. Inline whitespace is folded onto one line for headings and tables. The labeled implication in equation (1.1) uses an equivalent AMS arrow in Markdown; the original TeX remains in the source and structured formula data.

Run `python scripts/build_report.py` to regenerate the paper and `python scripts/check_report.py` to check formula coverage, source correspondence, equation numbers, links, and artifact identities.

## JSON schema

The top-level object contains `schema_version: 1`, `metadata`, `counts`, `blocks`, and `references`. The ordered `blocks` array is the rendering entry point. Every block also has a `markdown` fallback.

| Block type | Fields |
| --- | --- |
| `heading` | `id`, `level` (2 or 3), `number` (string or null), `appendix` (boolean), `inlines` |
| `paragraph` | `inlines` |
| `display_math` | `id`, `tex` (including any explicit tag), `tags` |
| `ordered_list` | `items`, each containing `inlines` |
| `table` | `rows`, each containing cells with `inlines`; `header_rows` |
| `reference` | `id`, `number`, `key`, `inlines`, `text`, `url` |

Inline nodes use `type: text` with `text`; `math` with `tex`; `code` with `text`; `strong` or `emphasis` with nested `inlines`; `link` with `url` and nested `inlines`; or `citation` with an array of reference `numbers`. Text nodes retain the spaces around adjacent mathematical and citation nodes. Render headings with their `number` prefix when non-null; alphabetic main numbers identify appendices. Block IDs are stable anchors.

Citation numbers refer to `references`, which is ordered from 1 through 12. Publication years inside the references identify the cited works. Source and output paths are repository-relative.
