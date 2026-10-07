# Final independent review of the completed Heston step table

Date: 7 October 2026. Reviewed: the completed step insert in `repository/manuscript/report-source.tex`; `repository/code/revision/results/revision-budget.json`; the original base rerun receipt; the 384- and 1536-step completion receipts and result files; the 192/384/1536 stopped-run worker traces; and the resource/acceptance patch rules in `code/revision/asian_step_grid.py`. Only lightweight exact-fraction read-back checks were run. No certificate computation was rerun.

## Verdict: PASS

No numerical discrepancy, incorrect stop classification, or incorrect explanation for the finest-grid widening was found.

## Interval, width, and six-component reconciliation

All three successful signed enclosures in the manuscript contain the exact saved endpoints. Every displayed total width is an upper bound on the exact endpoint difference. The three rows in the ledger report `COMPLETE_INDEPENDENTLY_CHECKED_ENCLOSURE` and are supported by the five completed Asian tasks, including both alternative numerical constructions.

Using Python standard-library `Fraction` on the saved rational strings verified, for each successful row:

```text
sum(exact six width components) == exact total interval width
exact bias upper endpoint - exact bias lower endpoint == exact total width
```

Both equalities passed at 384, 768, and 1536 steps. The six printed width components are upward roundings of the exact component values, including `2.65628E-7` for the 1536-step projection width. The printed `1E-12` arithmetic/endpoints entry is a coarse upper bound on the extremely small exact arithmetic width, not an empirically inferred fee. Exact reconciliation refers to the rational ledger; rounded displayed component columns need not sum to the rounded total exactly.

The nonlinear shares are `95.5210138473%`, `94.5148261585%`, and `92.8101684112%`, supporting the displayed `95.5%`, `94.5%`, and `92.8%`.

## Recorded time sums

The manuscript correctly sums only the five Asian task wall times, including the pilot, both principal calculations, and both checks. It does not include the posterior jobs from the ten-job base run.

| Steps | Sum of recorded five-task outer times | Manuscript |
| --- | --- | --- |
| 384 | 122.31327259994578 seconds | 122.3 seconds |
| 768 | 184.0238435997162 seconds | 184.0 seconds |
| 1536 | 431.6250236000633 seconds | 431.6 seconds |

The narrative correctly presents these as machine- and load-specific observations rather than portable runtime guarantees.

## Failed attempts and retained guards

- **192 steps:** the retained worker trace stops at `assert beta>8`. The exact recorded projection beta is `184040303/23040000<8`, so reporting no certificate is correct. The manuscript correctly avoids inferring anything about the actual price bias from this failed sufficient condition.
- **384 steps:** the retained initial worker trace stops at `assert high(radius)<F(11,1000)`. The successful experiment records this original `.011` acceptance target as false rather than removing an analytical enclosure premise. The mathematical projection, moment, branch, and tail conditions are retained. The final `.025` absolute-price-error target remains satisfied.
- **1536 steps:** the first retained worker trace stops at `assert time.perf_counter()-start<55`. The controller reports a stopped worker; this is a resource stop, not a failed analytic inequality. The later bounded contract scales time allowances by `ceil(N/768)=2`, retains one thread and 256 MiB per worker, and completes all five tasks. Describing this as a declared resource extension with failed-attempt preservation is correct.

## Why the finest enclosure becomes slightly wider

The ledger changes from 768 to 1536 steps are:

| Exact-width component change, shown approximately | Change |
| --- | --- |
| Nonlinear payoff remainder | -.00030695657520932206 |
| Linear projection | -.000008355196663813299 |
| Continuous frequency tail | 0 |
| Discrete frequency tail | +.0003825379268851291 |
| Periodization | 0 |
| Arithmetic reconciliation | Negligible positive change of order `10^-72` |

The discrete-tail increase exceeds the decreases in the nonlinear and projection contributions; the net total-width increase is approximately `.00006722615501199376`. Thus the manuscript's attribution to the looser discrete frequency-tail bound is directly supported by the exact budget. Equation (C.7) uses the deterministic first-step lower bound `i_0=h v_0` in the denominator together with the first-month Laplace upper bound; both explain why a fixed frequency cutoff/tail construction need not tighten with the Euler grid. This concerns the slack of the certified enclosure, not monotonicity of the true discretization bias.
