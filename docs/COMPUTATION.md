# From the proof to the finite calculations

This note explains how the quantities in the [paper](../manuscript/report.md) are evaluated and checked. The [mathematical structure](MATHEMATICAL-STRUCTURE.md) gives the argument in outline; [EVIDENCE.md](../EVIDENCE.md) identifies the programs, exact results and reproduction commands.

## Weighted moments and the geometric scale

The twelve-fixing square expands into arithmetic-square, arithmetic–geometric and geometric-square terms. Combining repeated loadings gives the 91 real profiles in Appendix A. Each of the three positive moment groups has total coefficient 10000 at $`S_0=100`$. The finite catalog is determined by this expansion.

For each law, the conditional standard deviation is $`\sigma_\nu=\sqrt{1-\rho^2}\sqrt{I_\nu}`$. Section 4.1 assumes finite raw weighted moments before expanding the square. With

```math
a=\sum_\nu E_\nu[A^2/\sigma_\nu],\qquad
b=\sum_\nu E_\nu[AG/\sigma_\nu],\qquad
d=\sum_\nu E_\nu[G^2/\sigma_\nu]\gt0,
```

the exact objective is $`J(c)=a-2bc+dc^2=J(b/d)+d(c-b/d)^2`$. The common correlation factor cancels from the optimizing ratio. Arithmetic–geometric mean gives the nonnegative representation

```math
c_*=1+\frac{\sum_\nu E_\nu[(A-G)G I_\nu^{-1/2}]}
                 {\sum_\nu E_\nu[G^2 I_\nu^{-1/2}]}.
```

Both Laplace integrands are nonnegative and nonincreasing in their nonnegative argument. The calculation subtracts the $`AG`$ and $`G^2`$ profiles at each node before integrating their difference. This retains cancellation while allowing Darboux bounds for the resulting positive integrand.

The nodal projection allowances are $`10000\delta_Q`$ for $`G^2`$, $`20000\delta_Q`$ for $`(A-G)G`$, and $`10000(1+c)^2\delta_Q`$ for the square. The continuous tail of a positive moment is bounded by $`10000C e^{-\zeta X}/\zeta`$. Since $`0\le(A-G)G\le AG`$, the same positive $`AG`$ tail controls the difference moment. The discrete tail uses $`I_Q\ge hv_0`$ and the outward nodal value at the cutoff. All inverse-square-root integrals retain their factor $`2/\sqrt\pi`$.

The scale bracket determines a rational candidate before the square and linear terms are evaluated. Rounding its midpoint to a lattice of spacing $`10^{-7}`$ adds at most $`5\cdot10^{-8}`$ to its distance from the exact midpoint. A bound on its exact-objective loss therefore uses

```math
J(c_{\mathrm{selected}})-J(c_*)
\le d_{\mathrm{upper}}
\left(\frac{c_+-c_-}{2}+5\cdot10^{-8}\right)^2,
```

where $`d_{\mathrm{upper}}`$ is in $`\sigma^{-1}`$ units. Directly evaluating the full price construction at the selected rational scale includes that scale exactly. Minimizing the exact quadratic and minimizing a computed enclosure with its quadrature allowances are distinct optimization problems.

## Changing the Euler step

For $`N=1/h`$ aligned with twelve monthly fixings, each fixing interval has $`N/12`$ steps. The discrete transforms, projection prefix and first-period variance bound use the same $`N`$. Both recursion coefficients at a step are computed from the preceding coefficients.

The weighted projection argument requires

```math
\beta(N)=\min_{s\in\{12,\,12+512/N\}}
\left\{s\left(1-\frac{3253}{1000N}\right)
-\frac{529}{20000}s^2-\frac1{N^2}\right\}\gt8.
```

| Steps $`N`$ | Exact $`\beta(N)`$ | Condition |
| ---: | ---: | --- |
| 192 | $`184040303/23040000`$ | Below 8 |
| 384 | $`745531727/92160000`$ | Above 8 |
| 768 | $`3000866063/368640000`$ | Above 8 |
| 1536 | $`12040940687/1474560000`$ | Above 8 |

This is an analytical requirement of the projection bound. Numerical acceptance targets and finite runtime allowances are recorded separately from analytical conditions. A complete price row requires the weighted and linear computations, both alternative-construction checks, and every projection, branch, moment and tail check to complete.

The six width contributions are combined as exact rational numbers. Their sum equals the exact difference of the final upper and lower endpoints. Displayed decimal components are rounded outward individually. At 1536 steps the discrete frequency-tail contribution increases by more than the payoff and projection contributions decrease. Its dependence on the floor $`i_0=hv_0`$ explains why changing the Euler step alone need not narrow the chosen finite inversion bound.

## The second initial-variance point

The second stochastic-variance calculation uses

```math
(\kappa,\bar v,\xi,\rho,v_0)
=(3,9/200,23/100,-11/20,1/25).
```

The contract, scale, fixing dates and $`h=1/768`$ agree with the principal calculation. Riccati coefficients, loading barriers and projection-prefix recurrences depend on $`\kappa,\kappa\bar v,\xi,\rho`$ and the transform arguments, and retain their form when only $`v_0`$ changes. The following quantities use the specified $`v_0`$ in every evaluation:

| Quantity | Dependence |
| --- | --- |
| Continuous and discrete transforms | $`\exp(A+Bv_0)`$ |
| Projection occupation sum | $`\exp(-v_0u_j/h)`$ |
| Continuous weighted and frequency tails | Their $`v_0`$-dependent prefactors and decay exponents |
| Discrete weighted and frequency tails | The transform at the cutoff and the floor $`hv_0`$ |
| Prices and residuals | The resulting moments, linear terms and complete error allowances |

Here $`hv_0=1/19200`$. The independently evaluated rational conditions are

```math
\beta_W=3000866063/368640000\gt8,\qquad
\beta_L=8004253583/983040000\gt8,\qquad
\beta_{\mathrm{UI}}=8001336523/983040000\gt0.
```

For the enlarged stock-loading interval $`[-5/4,5/2]`$, the continuous generator coefficient is a convex quadratic with endpoint values $`-190761/20000`$ and $`-27417/2500`$. The growth estimate is below $`.6`$, and hence the moment bound is $`\exp(.6+4v_0)=\exp(.76)\le\exp(.78)`$. A finite rational Taylor lower bound for $`\exp(131/50)`$ also verifies the growth inequality without ball arithmetic. The completed execution checks all transform nodes and frequencies at this parameter point.

## Coupled moments on the deterministic-variance face

The coupling example uses $`\xi=0`$ and the exact integrated variances in Section 6. Positive initial and long-run variance, with $`0\lt1-\kappa h\lt1`$, keep the deterministic Euler variance positive. Its projection is inactive. The combined stock driver $`\rho W+\sqrt{1-\rho^2}B`$ is Brownian, so the deterministic-variance stock law is independent of $`\rho`$.

After removing the first centered monthly normal, the remaining conditional factors have the form $`100\exp(m+u\cdot Z)`$, with eleven independent standard normal coordinates. Their means retain the drift of the entire observation interval, including the first month. Every pair moment is evaluated through

```math
E\left[100e^{m+u\cdot Z}\,100e^{n+v\cdot Z}\right]
=10000\exp\left(m+n+\frac12\|u+v\|^2\right).
```

Write $`L_{\nu\mu,ij}`$ for the moment of the two fixing factors, $`L_{\nu g\mu,i}`$ when the second factor is geometric, and $`L_{g\nu g\mu}`$ when both are geometric. Then

```math
E[a_\nu a_\mu]=\frac1{144}\sum_{i,j}L_{\nu\mu,ij},\qquad
E[a_\nu g_\mu]=\frac1{12}\sum_iL_{\nu g\mu,i},\qquad
E[g_\nu g_\mu]=L_{g\nu g\mu}.
```

The residual and displacement squares follow by finite expansion:

```math
\begin{aligned}
q_\nu&=E[a_\nu^2]-2cE[a_\nu g_\nu]+c^2E[g_\nu^2],\\
D_a&=E[a_P^2]+E[a_Q^2]-2E[a_Pa_Q],\\
D_b&=c^2\left(E[g_P^2]+E[g_Q^2]-2E[g_Pg_Q]\right).
\end{aligned}
```

The cross-model moments use the same eleven-dimensional normal vector. The Cauchy–Schwarz bound in the coupled-remainder appendix then evaluates the coupled remainder from these moments and the two deterministic conditional variances. The calculation checks 459 pair identities at each of 384 and 512 bits:

```math
459=2(144+12+1)+(144+1).
```

It compares the squared-norm exponent with its variance-and-covariance expansion. Conservative upper endpoints for squared moments and variance displacement, a lower endpoint for the minimum conditional standard deviation, and an upper endpoint for the maximum standard deviation give the outward remainder bound. Strict narrowing is checked by comparing the upper endpoint of the coupled width with the lower endpoint of the separate-law width.

### Why the marginal assumptions remain necessary

The coupled-remainder appendix assumes finite marginal remainders separately from a finite coupled bound. The distinction can be seen even under a diagonal coupling. Let $`U\sim N(0,1)`$ be independent of $`X\ge1`$ with $`P(X\gt x)=1/x`$, and take conditional fixing factors $`a_1=X^2`$, $`a_2=X^{-2}`$. Then $`a=(X^2+X^{-2})/2`$, $`g=1`$, and $`\sigma=c=1`$. The coupled differences vanish, so $`\Xi_K=0`$. But, for the smoothed call $`F_K`$,

```math
\lim_{a\to\infty}\frac{F_K(a;1)-F_K(1;1)-(a-1)\partial_xF_K(1;1)}a
=e^{1/2}\left[1-\Phi(\log(1/K)+1)\right]\gt0.
```

Since $`Ea=\infty`$, the marginal remainder expectations are infinite. Their difference is undefined. The marginal integrability conditions in the paper exclude this example.

The positive width for identical laws in Section 4.1 also occurs in an elementary integrable model. Take $`S_1=e^U`$, $`S_2=e^{U+V}`$ with independent nondegenerate normal $`U,V`$. Then $`A/G=\cosh(V/2)`$ is nonconstant. All needed Gaussian exponential moments are finite, and $`E[(A-cG)^2/\sigma]\gt0`$ for every fixed $`c`$. The separate-law width is therefore positive although the actual difference between identical laws is zero. A diagonal coupling preserves that equality directly.

## Gaussian score calculations

On $`\xi=0`$, continuous fixing increments have the form $`Y_j=m_j+\sqrt{s_j}Z_j`$, where $`m_j=r/12-s_j/2`$. Let $`d_j`$ be their first variance perturbation coefficients. The density score is

```math
S_d(Z)=\sum_jd_j\left[\frac{Z_j^2-1}{2s_j}-\frac{Z_j}{2\sqrt{s_j}}\right].
```

The second term includes the derivative of the variance-dependent Gaussian mean. The score has mean zero and second moment $`\sum_jd_j^2J(s_j)`$. Centering the call-spread payoff at $`7.5`$ gives the analytic coefficient bound in Section 6:

```math
|\beta_{\mathrm{Asian}}|\le
\frac{15e^{-rT}}2\sqrt{\sum_jd_j^2J(s_j)}.
```

For the density-ratio diagnostic, replace $`s_j,m_j`$ by their Euler counterparts $`s_{h,j},m_{h,j}`$ and use

```math
\log L_h=\sum_j\left[-\frac12\log\frac{s_{h,j}}{s_j}
-\frac{(Y_j-m_{h,j})^2}{2s_{h,j}}+\frac{Z_j^2}2\right].
```

With $`C=e^{-rT}(\psi(A)-7.5)`$, the expectations $`E[CS_d]`$ and $`E[C(L_h-1-hS_d)]/h^2`$ give the coefficient and scaled second-order residual. The implementation uses `expm1` for $`L_h-1`$. Each initial-variance point uses 2,097,152 vectors, reused across its four step sizes; residual estimates across steps are consequently correlated. Estimated standard errors describe the individual sample means. The analytic symmetric coefficient intervals and finite-step remainder bounds are evaluated separately with outward arithmetic.

## Posterior cells and target transfer

The posterior calculation uses the restricted prior and synthetic quotes specified in Section 7 and Appendix F. Endpoint reference put prices, monotonicity in variance and the positive-$`\xi`$ perturbation radii give price intervals over each complete initial-variance cell and nuisance slab. Likelihood squares are bounded term by term, and integer endpoints are rounded outward on the $`2^{-96}`$ lattice. CDF bounds retain the common cell masses in numerator and denominator.

The 8192- and 16384-cell calculations check 32768 and 65536 whole-cell weight containments, respectively. Their inverse-CDF pairings support the target-price quantile displacement bounds in the paper. The stored absolute 2.5, 50 and 97.5 percent quantile brackets instead concern the initial-variance marginal. These two outputs answer different questions and retain their own units.

## Verification and evidence

The exact ledgers reconcile interval endpoints and their component allowances. Source and result hashes bind each calculation to its inputs and executed program. Complete execution requires all expected jobs and result files; an analytical exclusion, acceptance-target failure or resource stop retains its specific classification.

The alternative weighted-moment computation uses a hyperbolic matrix flow and separate reverse-grid indexing; the alternative linear computation uses complex recursions and exponential flow blocks. Both retain the same mathematical bounds and Arb arithmetic. Their agreement tests implementation consistency. Saved-result verification checks identities and rational ledgers, while a fresh execution recomputes the finite interval calculations. The proofs supply the mathematical assumptions connecting those calculations to the price statements.

[Paper](../manuscript/report.md) · [Mathematical structure](MATHEMATICAL-STRUCTURE.md) · [Evidence and reproduction](../EVIDENCE.md)
