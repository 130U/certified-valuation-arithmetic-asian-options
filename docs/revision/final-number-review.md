# Asian coefficient and posterior: numerical checks

Checked 7 October 2026: the coefficient and posterior formulas in [the manuscript](../../manuscript/report.md), [the Gaussian diagnostic](../../code/revision/asian_beta_diagnostic.py), [the coefficient-bound program](../../code/revision/asian_beta_bounds.py), the saved [diagnostic](../../code/revision/results/asian-beta-diagnostic.json), [coefficient bounds](../../code/revision/results/asian-beta-score-bounds.json), [posterior summary](../../code/revision/results/posterior-grid-summary.json), and both refined-grid completion receipts. This note checks source, formulas and retained numerical outputs; it does not rerun pricing. Its scope is the coefficient and posterior calculations. Completed Heston step experiments are documented separately in [the execution records](../../code/revision/results/INDEX.md).

## Verdict

No substantive algebra error, numerical mismatch, or diagnostic-versus-certificate scope error was found in the checked coefficient and posterior results.

## Analytic Asian coefficient bound

Equation (6.12) is correct. The call-spread payoff is in `[0,15]`; its centered value has absolute value at most `15/2`. The common Gaussian score has mean zero and second moment `sum_j d_j^2 J(s_j)`. Thus Cauchy–Schwarz gives

```math
|beta_Asian| <= (15 exp(-rT)/2) sqrt(sum_j d_j^2 J(s_j)).
```

`asian_beta_bounds.py` uses exactly this expression. The displayed four symmetric beta intervals contain the 384- and 512-bit saved interval endpoints. Each displayed analytical remainder upper bound at `h=1/768` is rounded upward from the saved rational enclosure. The pointwise replacement of `u_*` by each coordinate's `min(s_j,s_h,j)` is valid on the segment joining the two variance vectors; `J` and `H_2` are decreasing on positive arguments.

| Initial variance | Saved positive beta endpoint, abridged | Displayed positive endpoint | Saved remainder upper endpoint, abridged | Displayed upper bound |
| --- | --- | --- | --- | --- |
| .03 | 3.44149135754755 | 3.441491358 | .000121667772167664 | .000121667773 |
| .04 | .928189504541648 | .928189505 | .0000366468834719126 | .000036646884 |
| .05 | .785853081399917 | .785853082 | .0000345323684827406 | .000034532369 |
| .06 | 2.05727082136325 | 2.057270822 | .0000996845849822003 | .000099684585 |

These are genuine analytic enclosures of the coefficient; they are broad and all include zero. The manuscript explicitly says that they are not executed integration of the signed twelve-dimensional coefficient and do not certify nonvanishing. Cross precision and algebraic re-expression are not independent proof derivations.

## Gaussian Monte Carlo and residual formulas

The continuous increment law in the code is `Y_j=m_j+sqrt(s_j) Z_j`, with `m_j=r/12-s_j/2`, and the discrete law replaces `s_j` by the aligned Euler `s_h,j`. The density-score formula is

```math
S_d(Z)=sum_j d_j[(Z_j^2-1)/(2s_j)-Z_j/(2sqrt(s_j))].
```

Its negative linear-normal term correctly includes the derivative of the variance-dependent Gaussian mean. The code's density ratio is the product of `p_s_h(Y_j)/p_s(Y_j)`; its log is

```math
log L_h=sum_j[-(1/2)log(s_h,j/s_j)
                  -(Y_j-m_h,j)^2/(2s_h,j)+Z_j^2/2].
```

With `C=exp(-r)(psi(A)-7.5)`, `E C S_d` is the coefficient and

```math
E[C(exp(log L_h)-1-h S_d)]/h^2=(e_h-h beta_Asian)/h^2.
```

Centering is valid because both `E(L_h-1)` and `E S_d` are zero under the continuous Gaussian law. The signs, discount, and `N^2` scaling in the code are correct for `h=1/N`. The cumulative Euler variance and first variance coefficient agree with (6.2) and (6.4).

The run has `2,097,152=64*32,768` vectors **per point**, hence four sets of that size. The same vectors at a given point are reused for its four residuals. Their estimates are correlated across step sizes. The code uses the unbiased sample variance divided by the sample size for each estimated standard error, which is correct for the individual sample means. No claim of independent residual estimates across step sizes should be introduced.

All four beta estimates and standard errors and all sixteen residual estimates match their displayed six-decimal values. The saved diagnostic hash equals the current code hash:

`166968fec8609f08113d6191a527957500b908861064a29427d6eff73a84fa21`.

The record reports `STATISTICAL_DIAGNOSTIC`, binary64 evaluation, normal-approximation intervals, and the absence of a deterministic signed-coefficient or continuous-price enclosure. The manuscript retains those boundaries. Stable residual scales are correctly described as consistent with the analytical second-order result, rather than proving an order or nonzero coefficient.

Numerical interpretation:

1. The code evaluates `exp(x)-1` with `np.expm1` to reduce cancellation. The subsequent score subtraction still performs cancellation.
2. For `h=1/768`, the residual standard errors are approximately `.003733`, `.001000`, `.000863`, and `.002319`, respectively. The exact saved diagnostic values are in the linked JSON record.

## Posterior refinement table and uncertainty brackets

The 8192- and 16384-cell receipts both report `COMPLETE`. Each records a principal run, compatibility run, and 384-bit checker with zero return codes. The six shift upper bounds in the manuscript are upward roundings of the saved exact rational outputs; all coupling step counts match:

| Cells | Quotes | Saved shift upper value, abridged | Displayed upper value | Coupling steps |
| --- | --- | --- | --- | --- |
| 4096 | 1 | .008018821657241945 | .008018821658 | 2 |
| 4096 | 9 | .012716404216982817 | .012716404217 | 5 |
| 8192 | 1 | .006452960803994987 | .006452960804 | 2 |
| 8192 | 9 | .010367612937112381 | .010367612938 | 7 |
| 16384 | 1 | .006061495590683248 | .006061495591 | 3 |
| 16384 | 9 | .009584682510488902 | .009584682511 | 12 |

The reductions at 16384 cells are `24.4091482542%` and `24.6274155261%`, consistent with the displayed `24.4%` and `24.6%`. The 4096-cell mesh shares `39.0546372068%` and `61.5685388152%` support the text's approximate `39%` and `62%`.

The six printed initial-variance quantile brackets for the continuous-model posterior at 4096 cells contain their exact saved endpoints. They are explicitly described as **parameter marginal** brackets. The text does not present them as absolute Asian target-price quantiles or infer the target uncertainty scale. The statements that finer cells do not simply halve the final bound, and that a larger nine-quote enclosure does not prove a larger true bias, remain correct.

## Scope boundaries

The posterior refinement retains the restricted prior with `xi in [10^-7,10^-6]`; it is not extrapolated to the main `xi=.23` point. The four beta points remain on `xi=0`. Analytic enclosures and statistical diagnostics are distinct. Neither a signed coefficient integration nor absolute target-price quantiles are supplied by these calculations. The numerical JSON and exact completion receipts are listed in [the evidence index](../../code/revision/results/INDEX.md); the root manifest records their published file hashes.
