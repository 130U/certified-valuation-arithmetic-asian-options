# Deterministic coupled remainder: derivation and numerical checks

Checked 7 October 2026:

- [Executed program](../../code/revision/round2_coupling_example.py)
- [Result](../../code/revision/round2/results/coupling-v004-result.json)
- [Proof](coupling-v004-proof.md)
- Proposition I.1 in [the manuscript](../../manuscript/report.md), together with (6.2).

## Verdict

**PASS for the stated deterministic-variance point and nonlinear remainder contribution.** No algebraic or integrability gap was found in the checked derivation. The checks cover the derivation, executed source and saved moments; they are not formal verification or a separate implementation of a full-price interval certificate.

The scope is `xi=0`, `kappa=3`, `vbar=9/200`, `v0=1/25`, `h=1/768`, twelve monthly fixings, `S0=100`, `r=1/100`, `T=1`, scale `1254433/1250000`, and strikes 95/110. It neither alters the principal positive-`xi` certificate nor evaluates the signed Asian leading coefficient.

## Checked mathematical steps

| Step | Derivation check |
| --- | --- |
| Deterministic projected law | For `eta=1-kappa*h` in `(0,1)`, variance remains a positive convex combination of `v0` and `vbar`; projection is inactive. Summing the **current** Euler variances gives the exact cumulative variance in (6.2). |
| Centered common Gaussian factor | The code's means are `r*t_i-I_nu(t_i)/2`, including the entire first-month drift. The eleven-dimensional coefficient vectors exclude only the first normal. Thus `U_nu=sigma_nu*Z_1` is centered, and `S_nu,i=exp(U_nu)*a_nu,i` has the correct marginal price law. |
| Correlation convention | With deterministic variance, `rho*W+sqrt(1-rho^2)*B` is a one-dimensional stock Brownian motion. Conditioning on its first monthly increment gives `sigma_nu^2=s_nu,1`. There is no omitted `(1-rho^2)` factor; this is a different valid conditioning choice from the stochastic-variance construction. |
| Mixed Gaussian moments | Completing the square proves `E[100 exp(m+u.Z)*100 exp(n+v.Z)]=10000 exp(m+n+||u+v||^2/2)`. The code includes mixed P/Q moments for both arithmetic and geometric displacement squares, and uses the same common eleven-dimensional normal vector. |
| Moment expansion | The expansions of `q_nu`, `E(a_Q-a_P)^2`, and `E(cg_Q-cg_P)^2` have the correct signs and scale factors. All moments are finite. Fixed positive `sigma_nu` also gives the full marginal `H_s(c)` integrability conditions. |
| Maximum-square bound | With `z=max(abs(a_P-b_P),abs(a_Q-b_Q))`, `E z^2<=q_P+q_Q`; neither a pointwise maximum nor a mixed moment is falsely replaced by a marginal equality. |
| Cauchy--Schwarz | It is applied separately to `E[z*abs(delta a)]` and `E[z*abs(delta b)]`, giving `sqrt(q_P+q_Q)*(sqrt(D_a)+sqrt(D_b))`. The constants are deterministic at this point. |
| Curvature and sigma derivative | The constants agree with H.1: `M=e^(2*sigma_plus^2)/(sigma_minus*sqrt(2*pi))` and `N=e^(2*sigma_plus^2)*(1+4/e+8*sigma_plus^2)/(sigma_minus^2*sqrt(2*pi))`, before dividing by strike. The sigma term retains its factor `1/2`. |
| Outward use of inputs | The code uses an upper endpoint for each squared moment and sigma displacement, a lower endpoint for `sigma_minus`, and an upper endpoint for `sigma_plus`. Every dependence in these sufficient constants has the correct conservative direction. |
| Call-spread combination | Discounting `B_95+B_110` produces a symmetric nonlinear contribution interval; doubling its radius gives its width. This controls a certificate contribution rather than the full price difference. |
| Same-conditioning comparison | `D_nu=exp(2*sigma_nu^2)*q_nu/sigma_nu` correctly integrates the independent first normal. The separate-law endpoints are `-gamma*(D_Q/110+D_P/95)` and `gamma*(D_Q/95+D_P/110)` under the same laws, scale, and Gaussian factor. |

## Numerical and source checks

The executed source's SHA-256 matches the result record. Each precision runs 459 closed pair-moment identity checks; this count equals `2*(144+12+1)+(144+1)`.

An additional scalar recomputation used standard-library `Decimal` at 210 digits and prefix covariance formulas, without calling the source's vector pair functions. Both conditional residual moments, both cross-model displacement moments, and `sigma_P`/`sigma_Q` lie inside their recorded 512-bit Arb rational intervals. This is a numerical consistency check, not interval certification.

The recorded outward comparison is:

| Quantity | Valid outward statement |
| --- | --- |
| `E Xi_95` | `<= .000023887739528734380066` |
| `E Xi_110` | `<= .000020630320502088782784` |
| Coupled discounted nonlinear width | `<= .000088150195864703911227` |
| Separate-law nonlinear width | `[.015383637151510699801154, .015383637151510699801155]` |
| Coupled/separate certificate-width ratio | `<= .005730127082206135457571` |

The exact rational comparison `upper(coupled_width)<lower(separate_width)` passes for both precision runs. Consequently the example proves a smaller nonlinear certificate interval at this point, without claiming a smaller true bias of this magnitude.

The shortened value `<= .00008815019586` is not a valid outward upper bound. The proof uses the 24-place outward endpoint. Valid shorter upper bounds are `<= .000088150195865` or `<= .00008815019587`. The separate lower bound `>= .01538363715` is valid.

## Model definitions

The proof uses `S0=100`, `r=1/100`, `T=1`, and twelve common **independent** standard normals. It defines `Z=(Z_2,...,Z_12)` and bars as averages over the fixing index. These definitions fix the model and conditioning used in the calculation.

The 384/512-bit agreement and algebraically equivalent Gaussian expressions share the proof and Arb. The present sources correctly describe them as arithmetic consistency checks, and correctly keep positive-`xi`, full-price, and signed-coefficient claims outside the result.
