# Independent mathematical review of Proposition R.1

Source reviewed: `theory/remainder-revision.tex`, 7 October 2026. Scope: Proposition R.1 and its proof, together with the definitions (2.6), (2.7), (3.1), and the call-spread combination (4.2) in the manuscript. This is a manual second-party algebra and assumptions audit, not formal verification.

## Verdict

**Verified in the repaired source under the stated `H_s(c)` and coupling-moment assumptions.** The pointwise derivative bounds, interpolation argument, and diagonal cancellation are correct. The first snapshot referred only to the structural representation (2.6); that representation alone does not make the two expectations `R_{K,P},R_{K,Q}` finite, and `E Xi_K < infinity` does not repair the omission. This issue was sent to the root agent, and a read-back of the modified source confirms that Proposition R.1 now explicitly assumes both laws satisfy `H_s(c)`, including (2.7), and the proof explicitly records finite marginal remainders. No further substantive gap was found in this local proof. The positivity of `K`, inherited from the call-strike notation, can also be stated at the proposition's opening for clarity.

## Statement repair, now closed

The repaired source uses the following assumption; optionally add `K>0` explicitly:

```tex
Fix \(K>0\) and \(c>0\). Suppose that both pricing laws satisfy
\(\mathsf H_s(c)\), and couple their conditional triples
\((a_P,b_P,\sigma_P)\), \((a_Q,b_Q,\sigma_Q)\), where
\(b_\nu=cg_\nu\) and each marginal is the corresponding conditional
triple in (2.6).
```

For the two-strike consequence, apply the proposition separately at `K_1` and `K_2`. No independence between the coupled triples is needed. All expectations defining `Xi_K` refer to the chosen coupling.

### Why integrability cannot be inferred from the new coupling condition

Take two identical laws and their diagonal coupling. Let `U~N(0,1)` be independent of a Pareto variable `X>=1` with `P(X>x)=1/x`. Use two conditional price factors `a_1=X^2`, `a_2=X^-2`, so `a=(X^2+X^-2)/2`, `g=1`, `sigma=1`, and choose `c=1`, hence `b=1`. This satisfies (2.6) and yields `Xi_K=0` under the diagonal coupling.

But, writing `F=F_K(.;1)`, as `a` tends to infinity,

```math
r_K(a,1,1)/a -> exp(1/2)-F'(1)
              =exp(1/2)[1-Phi(log(1/K)+1)]>0.
```

Since `E a=infinity`, both remainders have infinite expectation. Their numerical difference is undefined. This example is excluded by (2.7) and by the proposed explicit repair. Thus this is a statement-level missing-assumption issue, not a failure of the pointwise proof.

## Verified local steps

| Step | Check | Result |
| --- | --- | --- |
| Conditional identity | Given the conditional triple, `F_K(a;s)-F_K(b;s)` is the conditional difference of call payoffs; `(a-b)F'_K(b;s)` equals the conditional expectation of `(A-cG)1_{cG>K}`. | Correct. With the integrability repair, taking marginal expectations is legitimate. |
| Second derivative | `F'_K(x;s)=exp(s^2/2) Phi(log(x/K)/s+s)`. Differentiation gives `F''_K(x;s)=K exp[-log(x/K)^2/(2s^2)]/(s x^2 sqrt(2pi))`. | Correct; no missing `exp(s^2/2)` factor remains after simplification. |
| Square completion | `-2y-y^2/(2s^2)=2s^2-(y/s+2s)^2/2`, with `y=log(x/K)`. | Correct. |
| Volatility derivative | At fixed `x`, `partial_s H=(H/s)[y^2/s^2-1]`. | Correct. |
| Uniform derivative bound | For `w=y/s+2s`, `abs((w-2s)^2-1)<=2w^2+8s^2+1`, and `sup_w w^2 exp(-w^2/2)=2/e`. | The stated `N_K` follows correctly, including the `s_-^-2` denominator and `4/e` term. |
| Derivative in `a` | `partial_a r=F'(a;s)-F'(b;s)`, bounded by `M_K abs(a-b)`. | Correct. |
| Derivative in `b` | Differentiating both the reference call and tangent term gives `partial_b r=-(a-b)H_K(b,s)`. | Correct; the two `F'(b;s)` terms cancel. |
| Derivative in `s` | Taylor's integral remainder is `(a-b)^2 int_0^1(1-t)H_K(b+t(a-b),s)dt`; differentiation yields the formula in the proof. | Correct. Along a fixed coupled pair, positivity gives a compact local parameter segment, so differentiation is justified. |
| Linear interpolation | Positivity is retained; the residual `a-b` is an interpolation of the two endpoint residuals, so its absolute value is at most `z`; volatility stays in `[s_-,s_+]`. | Correct. |
| Pointwise coupling inequality | Integrating the directional derivative gives `M_K z(abs(delta a)+abs(delta b))+N_K z^2 abs(delta sigma)/2`. | Correct, including the factor `1/2`. |
| Marginal expectations | `abs(E r_Q-E r_P)<=E abs(r_Q-r_P)<=E Xi_K`. | Correct once the marginal remainders are integrable. |
| Call-spread consequence | The nonlinear contribution is `exp(-rT)[(R_K1,Q-R_K1,P)-(R_K2,Q-R_K2,P)]`. | Bound by `exp(-rT)(B_K1+B_K2)` is correct. |
| Diagonal cancellation | Under a diagonal coupling of the same conditional-triple law, all three differences vanish, hence `Xi_K=0` pointwise. | Correct. Equality of conditional-triple laws is what permits this particular coupling. |

## Suggested small clarification of interval combination

Give the nonlinear interval a name to avoid a reader intersecting with the already combined interval in (4.2):

```tex
\[
I_{\rm marg}=
\left[-\gamma\left(d_Q/K_2+d_P/K_1\right),
       \gamma\left(d_Q/K_1+d_P/K_2\right)\right].
\]
The price difference then belongs to
\([\ell,u]+(I_{\rm marg}\cap[-B,B])\),
where the plus sign denotes Minkowski addition of intervals.
```

This is a presentational clarification; the existing instruction to intersect before adding the linear interval is mathematically correct.

## Numerical and asymptotic boundary

The finiteness of the new coupled expectation is stronger information than the current marginal weighted remainder bound. In addition to small-volatility denominators, `Xi_K` includes `exp(2 s_+^2)` and products of conditional residuals and coupled differences. The source correctly does not infer finite Heston coupled moments, an executed certificate, or a convergence rate from the proposition. The conditional statement `E Xi_K -> 0` implying a vanishing remainder difference is valid. The preceding optimized-scale formulas (R.1)–(R.3) distinguish exact moments from computed fees correctly and do not supply those additional coupling moments.
