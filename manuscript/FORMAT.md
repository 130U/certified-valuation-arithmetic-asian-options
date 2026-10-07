# Manuscript source and PDF build

`report-source.tex` and `report-source-zh.tex` contain the editable English and Chinese manuscripts. `report.tex` supplies a standalone English LaTeX preamble. `report.md` is the GitHub reading copy; `report.json` and `content-verification.json` bind its mathematical content to the source.

The publication PDFs are built with **ReportLab and MathJax**, using A4 pages, Computer Modern Latin type, embedded Noto Serif SC Chinese type, numbered equations and a linked contents list. The formulas remain vector outlines; an invisible TeX text layer supports searching and copying their inputs.

From the repository root, with Python 3.12 and Node.js on PATH:

```sh
python -m pip install -r scripts/pdf/requirements.txt
python scripts/build_report.py
python scripts/pdf/build_pdf.py --language en
python scripts/pdf/build_pdf.py --language zh
python scripts/verify_pdf_build.py
```

The MathJax archive is included with its checksum. No network connection is used during rendering. Font files and licenses are in `assets/fonts/`. Pass `--node /path/to/node` if Node.js is not on PATH. Outputs are `paper/paper.pdf` and `paper/paper-zh.pdf`; detailed render logs go to `.build/pdf/`.

The current manuscript has ten main sections, nine appendices, fourteen tables, thirteen references and 95 numbered equations. Its two language sources preserve the same mathematical expressions and numerical inputs. The final PDF hashes, page counts, source hashes, dependencies, build commands and visual inspection are recorded in [build-record.json](../paper/build-record.json).

Native LaTeX compilation has not been verified: the built-in compiler reports “Unable to find standard directories for platform.” The delivered PDFs use the successful build route above.
