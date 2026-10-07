# Executed deterministic-variance example of the coupled remainder bound

## Status

PROVABLE AS STATED

Verification: Verified

The statement is confined to xi=0, kappa=3, vbar=9/200, v0=1/25,
h=1/768, twelve monthly fixings, S0=100, r=1/100, c=1254433/1250000,
and strikes 95 and 110. It is a certificate for the nonlinear remainder
contribution, not a full-price enclosure or a signed Asian leading coefficient.

## Claim and premises

Let P be the continuous deterministic-variance law and Q the original
positive-part variance Euler law on this deterministic face. Its variance
updates stay strictly positive, because 0<1-3h<1 and v0,vbar>0. Thus the
projection is inactive and the cumulative variances are exactly

$$I_P(t)=\bar v t+\frac{v_0-\bar v}{\kappa}(1-e^{-\kappa t}),\qquad
I_Q(t)=\bar v t+\frac{v_0-\bar v}{\kappa}[1-(1-\kappa h)^{t/h}].$$

At fixing t_i=i/12 set sν,j=Iν(t_j)-Iν(t_{j-1})>0. Couple the two log-price
vectors using the same twelve independent standard normals Z1,...,Z12:

$$S_{\nu,i}=100\exp\left(rt_i-I_\nu(t_i)/2+
                       \sum_{j=1}^i\sqrt{s_{\nu,j}}Z_j\right).$$

On xi=0 the stock driver ρW+√(1-ρ²)B is itself a standard Brownian motion,
and the variance is deterministic. The marginal price laws therefore do not
depend on ρ. We use this combined driver for conditioning, rather than
conditioning separately on W as in the stochastic-Heston construction.
Its full first-month increment variance is sν,1.

After conditioning on Z2,...,Z12, Uν=σν Z1 with σν=√sν,1 is centered normal
and every fixing price has the common factor exp(Uν). Write

$$m_{\nu,i}=rt_i-I_\nu(t_i)/2,\quad
\ell_{\nu,i,j}=\sqrt{s_{\nu,j}}\mathbf1_{j\le i}\quad(2\le j\le12),$$
$$a_{\nu,i}=100e^{m_{\nu,i}+\ell_{\nu,i}\cdot Z},\qquad
a_\nu=\frac1{12}\sum_i a_{\nu,i},\qquad
g_\nu=100e^{\bar m_\nu+\bar\ell_\nu\cdot Z},\quad b_\nu=cg_\nu,$$

where Z=(Z2,...,Z12) and bars denote arithmetic means over fixing index i.
The full cumulative drift includes the first interval; removing its -sν,1/2
would be incompatible with the centered Uν required by H_s(c).

Define qν=E(aν-bν)², D_A=E(aQ-aP)², D_b=E(bQ-bP)², Z2=qP+qQ,
σ-=min(σP,σQ), σ+=max(σP,σQ), and Δσ=|σQ-σP|. For K>0 put

$$M_K=\frac{e^{2\sigma_+^2}}{K\sigma_-\sqrt{2\pi}},\qquad
N_K=\frac{e^{2\sigma_+^2}(1+4/e+8\sigma_+^2)}{K\sigma_-^2\sqrt{2\pi}},$$
$$B_K=M_K\sqrt{Z2}(\sqrt{D_A}+\sqrt{D_b})+
                         \frac12N_K Z2\Delta\sigma.$$

The claims are E ΞK≤BK and |R_K,Q-R_K,P|≤BK, with ΞK as defined in
Appendix I / Proposition R.1. The finite closed-moment execution additionally
proves strict narrowing of the discounted call-spread nonlinear interval.

## Verification Target and Bottleneck

All moments in the bound must be evaluated for the coupled conditional
variables, including mixed P/Q moments. Marginal square moments alone do not
close the displacement terms. The present example closes them through finite
Gaussian exponential identities; it introduces neither numerical integration
of an unbounded domain nor statistical estimation.

## Implicit Machinery

The proof is self-contained at calculus/probability level. It uses independent
Gaussian integration by completing the square, finite linear combinations,
Taylor's integral remainder for the smoothed payoff, the fundamental theorem
of calculus, and Cauchy--Schwarz. The global smoothing derivatives are proved
explicitly below. No external paper is load bearing and no originality claim
is made.

## Dependency Map

O1 exact positive variance laws -> O2 correct centered common Gaussian factor.
O3 closed Gaussian moments -> O4 residual and cross-model displacement moments.
O5 Gaussian curvature derivative bound -> O6 coupled gradient inequality.
O7 maximum-square/Cauchy--Schwarz -> O8 E Xi bound and discounted interval.
O9 separate-law width identity -> O10 completed outward strict-width check.

## Proof

The positive continuous variance is a convex combination of v0 and vbar.
Its deterministic Euler update is the same convex combination after every
step, with multiplier (1-κh)^j. Integrating the continuous curve and summing
the current discrete variances give the displayed I_P and I_Q exactly.
All fixing increments are strictly positive. The shared-normal construction
therefore has the required marginal increment means and variances. It induces
each original stock law, and its separation of the first centered normal
gives the displayed conditional a and g variables.

For any real m,n and vectors u,v in R^11, Gaussian integration gives

$$E[100e^{m+u\cdot Z}\,100e^{n+v\cdot Z}]
  =10000\exp[m+n+\|u+v\|²/2].\tag{C1}$$

This follows by writing (u+v)·z-||z||²/2 as
||u+v||²/2-||z-u-v||²/2 and integrating the centered Gaussian density.
Every such moment is finite. The equivalent exponent
m+n+(||u||²+||v||²)/2+u·v is used for a separate arithmetic identity check.

Let Lνμ,ij denote (C1) for (mν,i,ℓν,i),(mμ,j,ℓμ,j). Let Lνgμ,i
replace the second entry by (bar mμ,bar ℓμ), and let Lgνgμ replace both
entries by the respective averages. Then

$$E a_\nu a_\mu=12^{-2}\sum_{i,j}L_{\nu\mu,ij},\quad
E a_\nu g_\mu=12^{-1}\sum_iL_{\nu g\mu,i},\quad
E g_\nu g_\mu=L_{g\nu g\mu}.$$

Finite expansion yields qν=E aν²-2c E aνgν+c²E gν²,
D_A=E aP²+E aQ²-2E aPaQ, and
D_b=c²(E gP²+E gQ²-2E gPgQ). This is the explicit coupled moment
calculation. The same Gaussian formulas prove finite E(A+G) and weighted
second moments, so each marginal satisfies full H_s(c), including its
finite-remainder requirements.

For F_K(x;s)=E(xe^{sZ1}-K)^+ the curvature is

$$H_K(x,s)=\frac{K}{sx²\sqrt{2\pi}}
e^{-[\log(x/K)]²/(2s²)},\qquad
\partial_sH_K=\frac{H_K}{s}\left([\log(x/K)/s]²-1\right).$$

Completing the square in y=log(x/K)/s gives
H_K=e^{2s²} exp[-(y+2s)²/2]/(Ks√(2π)). With w=y+2s,
|(w-2s)²-1|≤2w²+8s²+1 and
sup_w w² exp(-w²/2)=2/e. Hence H_K≤M_K and |∂sH_K|≤N_K
whenever σ-≤s≤σ+, uniformly in x>0.

For r_K(a,b,s)=F_K(a;s)-F_K(b;s)-(a-b)F'_K(b;s), its derivatives are
∂a r=F'(a)-F'(b), ∂b r=-(a-b)H_K(b,s), and

$$\partial_s r=(a-b)²\int_0^1(1-t)\partial_sH_K(b+t(a-b),s)\,dt.$$

These hold by differentiation on each compact positive conditional line
segment; there is no differentiation under the outer expectation. If
z=max(|aP-bP|,|aQ-bQ|), the fundamental theorem of calculus along the
positive three-coordinate segment gives

$$|r_{K,Q}-r_{K,P}|
\le M_Kz(|a_Q-a_P|+|b_Q-b_P|)+N_Kz²\Delta\sigma/2=\Xi_K.$$

The pointwise inequality z²≤(aP-bP)²+(aQ-bQ)² implies E z²≤Z2.
Both M_K,N_K and Δσ are deterministic constants in this example. Applying
Cauchy--Schwarz separately to the two displacement terms gives

$$E\Xi_K\le M_K\sqrt{Z2}(\sqrt{D_A}+\sqrt{D_b})+
N_K Z2\Delta\sigma/2=B_K.$$

All needed square moments have already been proved finite. Conditional
expectation and the triangle inequality therefore yield
|R_K,Q-R_K,P|≤B_K for finite remainders. The discounted nonlinear component
of the spread bias belongs to [-R,R], where R=exp(-r)(B95+B110).

For comparison, the original separate-law approach uses
Dν=E[(A-cG)²/σν]. Conditional Gaussian integration gives
Dν=exp(2σν²)qν/σν. Its nonlinear lower and upper endpoints are
-γ(D_Q/110+D_P/95) and γ(D_Q/95+D_P/110), where
γ=exp(-r)/(2√(2π)). Its width is γ(1/95+1/110)(D_P+D_Q).
This uses exactly the same smoothing structure, laws and c as the coupled
comparison; the reference width is not taken from a different Heston
conditioning construction.

The executed script evaluates each exact moment using Arb enclosures.
It forms 459 moment pairs at each of 384 and 512 bits. The squared-norm and
variance/covariance expressions overlap for every pair. Because conservative
upper rational endpoints are subsequently fed into the coupling bound, its
bound itself depends slightly on precision; the two precision results agree
in upper value to better than 10^-90. This is an arithmetic consistency check,
not an independent proof of the analytical formulas.

The closed-moment run gives the outward results

| Quantity | Verified upper endpoint / interval |
|---|---|
| E Ξ95 | ≤ .000023887739528734380066 |
| E Ξ110 | ≤ .000020630320502088782784 |
| Direct discounted nonlinear width | ≤ .000088150195864703911227 |
| Separate-law nonlinear width | [.015383637151510699801154, .015383637151510699801155] |
| Direct/separate width ratio | ≤ .005730127082206135457571 |

The strict inequality is checked as `high(direct_width)<low(separate_width)`.
It thus proves actual narrowing of the nonlinear certificate at this point.
Exact rational endpoints, the executed source hash, runtime and the supporting
second moments are in `coupling-v004-result.json`. The result says nothing
about a positive-xi coupled certificate or full-price enclosure.

## Obligation Ledger

- O1: CLOSED-LOCAL
  - closed at: Proof, positive convex variance formulas and exact cumulative integral/sum.
- O2: CLOSED-LOCAL
  - closed at: Proof, complete cumulative deterministic drift and first centered normal separation.
- O3: CLOSED-LOCAL
  - closed at: Proof, Gaussian square completion proving finite pair moments (C1).
- O4: CLOSED-LOCAL
  - closed at: Proof, finite expansions for q, D_A and D_b including mixed P/Q pairs.
- O5: CLOSED-LOCAL
  - closed at: Proof, displayed curvature derivative and completed-square global constants.
- O6: CLOSED-LOCAL
  - closed at: Proof, positive compact-segment differentiation and gradient comparison.
- O7: CLOSED-LOCAL
  - closed at: Proof, pointwise maximum-square domination and Cauchy--Schwarz.
- O8: CLOSED-LOCAL
  - closed at: Proof, finite remainders and two-strike discount factor.
- O9: CLOSED-LOCAL
  - closed at: Proof, conditional second moment Dν=exp(2σν²)qν/σν and endpoint subtraction.
- O10: CLOSED-LOCAL
  - closed at: Proof, completed exact rational output and strict outward width comparison guard.

## Verification Checks

Localization before expansion: all conditional interpolation entries remain
positive; the proof differentiates on samplewise compact sets only.

Wrong norm or mode: E Ξ is enclosed by deterministic inequalities. No
sampling error or confidence interval is used.

Good-event bookkeeping: no exceptional event is excluded or unpaid.

Rate leakage: no stochastic-Heston rate is claimed. h is the specified 1/768.

Quantifier inflation: the result is one deterministic-variance point with
one coupled construction. It is not a full parameter-region result.

Citation identity: every load-bearing formula is derived here; Appendix I
only provides the notation and comparison target.

Negligibility closure: both coupled displacement terms are actually computed
from mixed moments. Marginal moments alone are not substituted for them.

Boundary and singularity: deterministic σ->0 is excluded by positive
increments. Every σ denominator is bounded outward by the lower endpoint.

Source and read-back: the output binds the executed script and helper hashes.
An independent reviewer may inspect formulas and re-read endpoints without
claiming that shared-Arb cross precision constitutes independent derivation.
