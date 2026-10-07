# Standalone manuscript editorial pass

Owned edits: `repository/manuscript/report-source.tex`, main text and Appendix H introductory/closing prose only. Appendix G, the H.1 statement and proof, numerical scripts, and builders were not edited.

## Changes

- The abstract now gives the principal certificate and the two separate auxiliary domains in one compact narrative.
- Section 6.1 presents a common expansion formula and explicit remainder bounds. The signed twelve-dimensional Asian coefficient integral remains uncomputed; the score bounds are zero-containing analytic enclosures. The coarse Monte Carlo columns are explicitly outside the fixed `h0=1/768` numerical-constant range.
- Sections 8.2–8.7 retain the step intervals and error decomposition while moving operation counts, alternate constructions, timing, execution stops, and result paths out of the main narrative. The width explanation identifies the increase in the discrete tail contribution at the finest grid.
- The Feller table now explicitly states that all three price estimates have magnitude below one standard error. It supports a change in negative-proposal incidence, without resolving price-bias signs.
- The monetary application retains the interval transfer formula and direct valuation enclosure. The posterior application reports the mesh improvement without interpreting it relative to an uncomputed Asian-target uncertainty scale.
- Section 9 now collects the genuine mathematical limits without repeating the execution history or multiple diagnostic disclaimers.
- Main tables have numbered captions 1–10 in source order. A new parameter-sensitivity table inserted later will require corresponding renumbering.
- Main prose uses “error contributions” or “allowances” and “width plateau”. Exact machine-readable field names are unchanged.

`proposed-G-additions.tex` supplies the relocated details as TeX for the root agent to merge into Appendix G, avoiding duplication with the existing implementation section.

## Verification

Compared the manuscript after editing with `editorial-before-source.tex` using a standard-library text check:

- 78 main display-equation blocks: unchanged.
- 10 main table bodies: unchanged, including every displayed numerical entry.
- 11 Appendix H display-equation blocks: unchanged.
- Ten new main captions, numbered consecutively.
- No remaining “fees” in main prose.
- Main source whitespace-token count fell from 7,223 to 6,089 (the count includes TeX formulas and tables, and is not a prose-only word count).

No compilation or builder execution was performed by this subagent; the root agent owns final rendering and compilation checks.
