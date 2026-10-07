# Primary-source audit for the major revision

Audit date: 7 October 2026. This is a focused comparison, not a systematic novelty review. The manuscript snapshot read was `output/latex/Theodore-Ouyang-Certified-Asian-Valuation-2024.tex`; the repository snapshot read was `research/asian-major-revision-20261007/repository`.

## Verified bibliographic identity

Fusai, Gianluca and Kyriakou, Ioannis (2016), *General Optimized Lower and Upper Bounds for Discrete and Continuous Arithmetic Asian Options*, *Mathematics of Operations Research* 41(2), 531–559; DOI [10.1287/moor.2015.0739](https://doi.org/10.1287/moor.2015.0739). The manuscript's existing bibliography is consistent with the [university repository record](https://openaccess.city.ac.uk/id/eprint/13241/) and the cover of its [accepted manuscript](https://openaccess.city.ac.uk/id/eprint/13241/1/AsianBound_FK.pdf).

## Exact locators used for the comparison

These are **printed pages**, not physical PDF page numbers. The accepted PDF has a repository cover before printed page 1.

| Object | Printed locator | Physical PDF page, one based |
| --- | --- | --- |
| Heston model | Section 2.2, page 5 | 6 |
| Conditional bounds | Section 3 | Starts on 10 |
| Payoff error statement | Theorem 4, page 15, equations (51)–(54) | 16 |
| Conditional moment inversion | Equations (55)–(56), pages 15–16 | 16–17 |
| Numerical inversion setup | Section 5, pages 16–17 | 17–18 |
| Fixing-frequency experiment | Section 5.1, page 17, Table 5 on page 31 | 18, 32 |
| Proof assumption | Appendix A, page 22, before equation (67) | 23 |
| Heston benchmark scheme | Appendix B, page 22 | 23 |

The proof of Theorem 4 uses monotonicity of the conditional expectation near the optimizing threshold; the source says its experiments checked this numerically. Do not portray that bound as an unconditional universal comparator.

The TeX insert compares precisely specified mathematical outputs. Searches for `branch`, `truncat`, and `round` returned no matches in the PDF extraction, and the inspected error and implementation sections do not report the corresponding finite interval budget. This supports **“not reported in the reviewed source”**, never a general absence or originality claim. PDF screenshot access failed for two requested pages; the accepted PDF's searchable text supplies the locators above.

## Manuscript edits recommended from independent read

| Location in original TeX | Recommended change | Reason |
| --- | --- | --- |
| Abstract, lines 19–28 | Name the target as the arithmetic Asian call spread `(A-95)^+-(A-110)^+`; add `xi=0.23` to the principal numerical result. | The enclosure is for this bounded payoff and specified point. |
| Abstract, lines 28–29 | Explicitly state `xi=0` for the ten-payoff expansion and `xi in [10^-7,10^-6]` for the posterior quantile example, with the other prior restrictions. | The two auxiliary modules do not certify the principal stochastic-volatility region. |
| Introduction, existing third task paragraph, line 49 | State the three numerical domains in parallel and call the posterior example a small-volatility perturbation certificate. | Readers should know the distinct scopes before Section 7. |
| Common factor paragraph, line 323 | Replace “B outside the first interval” with conditioning on `sigma(W_s:0<=s<=T) vee sigma(B_t-B_t1:t1<=t<=T)` (completed sigma algebra as needed). | Later Brownian levels reveal the first-interval endpoint and destroy the intended conditional independence; later increments are independent. |
| Title date, line 12 | Use the actual revision date `7 October 2026`; preserve the original-draft date separately. | A single version date makes the revision identifiable. |
| Author note, line 762; README last paragraph | Reconcile the factual history `derivations completed in 2023` versus `research originating in 2024`; keep these as author-supplied historical statements, never silently infer one from the other. Add the actual consolidation/revision date. | These statements are not automatically contradictory, but have different meanings. |
| Author note, line 762 | Replace the future-release wording with an actual repository link and verified commit/archive ID; report current run validation separately from historical reference payloads. | Publication and present recomputation are different facts. |
| Appendix G, lines 1466 onwards | Link repository, frozen commit, environment, concrete commands, exact output names, source hashes, and reference-comparison logs. | The code is publicly present in the supplied repository snapshot; the paper must point to it. |
| Appendix G, precision/independence statement | State that both implementations use Arb, list their distinct formula/program paths, and explain that raising precision checks arithmetic stability while shared theory remains common. | “Independent” needs an explicit scope. |
| Main theorem, after (4.2) | Add the identity-law counterexample observation and the warning that this separate-law remainder does not prove shrinking width. | Fixed-step correctness and asymptotic tightness are separate. |
| Limitations / experiment section | Retain the absence of an executed Asian scalar coefficient until a validated enclosure exists. Mark Monte Carlo/Sobol diagnostics as statistical estimates and not strict certificates. | No new strict conclusion may come from unvalidated diagnostic experiments. |

## Suggested abstract scope sentence

> The numerical claims have three separate domains: the main call-spread certificate uses the single Heston point with `xi=0.23`; the ten-payoff first-order expansion assumes deterministic variance (`xi=0`); and the posterior example uses the restricted prior with `xi in [10^-7,10^-6]`, so it certifies a perturbation near deterministic variance rather than the principal Heston parameter region.

## Suggested Brownian conditioning replacement

```tex
Condition on the entire variance driver and on the later increments of the
independent stock driver, using
\[
\mathcal G=\sigma(W_s:0\le s\le T)
\vee\sigma(B_t-B_{t_1}:t_1\le t\le T).
\]
Thus the first-interval integral
\(U=\sqrt{1-\rho^2}\int_0^{t_1}\sqrt{V_s}\,dB_s\)
retains, conditional on \(\mathcal G\), variance
\((1-\rho^2)I_P\). For the discrete model, condition analogously on all
\(G_j\) and only the \(H_j\) with \(j\ge t_1/h\), retaining
\(U=\sqrt{1-\rho^2}\sum_{j<t_1/h}\sqrt{hV_j^h}\,H_j\).
```

This replacement uses only independent later increments; the original formulas (5.3)–(5.4) are retained.

## Implementation-independence statement checked against supplied sources

The inspected source files support a more precise statement than merely “a second 384-bit run.” In `code/core/asian-remainder-certificate.py`, the continuous Riccati flow uses roots and a cross-ratio. In `code/core/check-asian-remainder.py`, the checker uses a hyperbolic two-by-two flow, constructs the catalog from ordered pairs and combines duplicates, indexes the discrete reverse grid separately, and accumulates a product for the projection ledger instead of exponentiating a prefix sum. The checker imports the resource helper, but not the principal numerical functions.

In `code/core/check-asian-linear.py`, the documented and inspected checker uses an `acb` complex discrete recursion and exponential representations of continuous flow blocks, checks each frequency term against the principal result, and recomputes the error fees rather than calling principal fee functions. Both implementations use Arb and the same theoretical error inequalities. Higher precision and alternative formulas can expose implementation or arithmetic problems; they do not provide an independent proof of the common analytic inequalities.

Suggested TeX:

```tex
The checks are independent at the numerical implementation level: the
weighted-remainder check replaces the root/cross-ratio Riccati formula by
a hyperbolic two-by-two flow and reconstructs the catalog and discrete
indexing; the linear check uses complex discrete recursions and exponential
flow blocks, and recomputes the finite error fees. The checks use 384-bit
arithmetic rather than the principal implementation's 256-bit arithmetic.
Both implementations share Arb and the theoretical inequalities, so these
checks test implementation consistency and arithmetic stability; they are
not independent derivations of the mathematical bounds.
```
