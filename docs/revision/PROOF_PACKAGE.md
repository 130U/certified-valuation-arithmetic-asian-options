# Payoff remainder revision proof package

## Status

PROVABLE AS STATED

Verification: Verified

This status applies to the propositions under the explicit premises below.
It does not certify newly computed numbers, the Heston coupled expectations,
or a convergence rate in h.

## Claim and premises

For the common Gaussian structure of manuscript (2.6), the scale c minimizing
the exact nonlinear width in (4.2) is the ratio of the two-model sums of
weighted AG and G² moments. Each raw moment is assumed finite, and
σ is positive almost surely. This extra raw-moment premise is distinct from
the manuscript condition Dν(c)<∞ alone.

For Heston with the same correlation parameter in the two laws, define
Hν=Eν[G² Iν^(-1/2)] and Eν+=Eν[(A-G)G Iν^(-1/2)]. Their sums satisfy
H>0 and E+≥0, and c*=1+E+/H. All these quantities refer to the actual
continuous and projected laws, with their own Iν.

For the direct remainder bound, fix c>0 and assume that both pricing laws
P and Q satisfy the full manuscript condition H_s(c). This includes
Eν(A+G)<∞ and Dν(c)=Eν[(A-cG)²/σν]<∞ for each law, as well as the
common conditional Gaussian structure. Assume a joint coupling of positive triples
(aν,cgν,σν) with the correct conditional marginal laws, and a finite
bound on E ΞK as defined in Proposition R.1 in remainder-revision.tex.
No cross-model independence, common σ, or Gaussian correlation assumption
is imposed on this coupling.

The H_s(c) assumptions are needed separately from E ΞK<∞. A diagonal
coupling can give ΞK=0 even for a heavy-tailed law with infinite remainder;
without marginal integrability the expression R_K,Q-R_K,P would be undefined.

The conclusions are (R.1)--(R.4) of the accompanying insertion fragment.
No claim of originality is made: the quadratic optimization and smooth
Lipschitz comparison use elementary tools. Their role is to make the
manuscript's error-width floor and a sufficient cancellation condition explicit.

## Verification Target and Bottleneck

The targets are the quadratic identity for exact nonlinear width, the
nonnegative Laplace integrand for the scale ratio, and an explicit global
gradient bound for the conditionally smoothed remainder.

The numerical bottleneck for scale optimization is a new outward evaluation
of the separately grouped moment profiles. Existing JSON files store the
combined square and cannot identify the two raw moments from that value alone.
The mathematical proof closes without assigning numerical values.

The numerical bottleneck for a cancellation certificate is a finite, validated
bound on the coupled expectation E ΞK. The marginal transform catalogs do not
contain cross-model distances of a, cg, and σ. The proposition treats that
quantity as an explicit additional premise and does not claim it was computed.

## Anchors and Implicit Machinery

The proofs are self-contained at graduate-calculus level. They use conditional
expectation, the arithmetic--geometric mean inequality for positive numbers,
Tonelli's theorem for nonnegative integrands, differentiation of a one-variable
normal integral, Taylor's integral remainder, and the fundamental theorem of
calculus on a line segment. Normal-integral curvature and its derivative are
displayed explicitly. No load-bearing external paper is invoked.

## Dependency Map

O1 -> exact width formula from manuscript (4.2) -> O2 quadratic minimum.
O3 AM--GM -> nonnegative Laplace integrands -> O4 Darboux/tail/profile bounds.
O5 sigma cancellation -> O6 certified midpoint regret.
O7 curvature formula -> O8 global curvature and sigma-derivative bounds ->
O9 gradient bound and coupling comparison -> O10 expectation and price units.
O11 checks the equal-model width floor.

## Proof

The nonlinear width from manuscript (4.2) is the upper endpoint minus the
lower endpoint. With exact dν=Dν(c), it equals

$$\gamma(K_1^{-1}+K_2^{-1})[D_P(c)+D_Q(c)].$$

Finite raw weighted moments allow each square to be expanded in expectation.
Writing a=Σ E[A²/σ], b=Σ E[AG/σ], d=Σ E[G²/σ], their sum is
J(c)=a-2bc+dc². Strict positivity of G and σ makes d>0, and b>0.
Completing the square gives J(c)=a-b²/d+d(c-b/d)². The minimizer on
c>0 is therefore b/d, and positive discount/strike factors do not change it.

AM--GM gives A≥G on every path, so each moment Eν+ is nonnegative. In the
Heston common-factor construction σν=√(1-ρ²)√Iν. The common correlation
factor cancels in b/d, while AG=G²+(A-G)G yields c*=1+E+/H. Each Laplace
integrand E[(A-G)G exp(-x²I)] is nonnegative. For x≥0 it is nonincreasing
because I>0. Tonelli gives the inverse-square-root integral representation.
Since (A-G)G≤AG, its continuous tail is bounded by the positive AG tail.
The normalized stock-load-2 profile bound C exp(-ζx) in manuscript (A.7)
gives the integrated tail 10000 C exp(-ζX)/ζ for AG and for G² at S0=100.
The sum of absolute coefficients of AG-G² is 20000, so its Q nodal
projection error is bounded by 20000 δQ using the per-profile error.
Its Q tail follows the same I_Q≥hv0 argument as (A.6). These statements
are bounds for the true grouped integrands after projection error is included.

If E+∈[e-,e+] and H∈[d-,d+], with d->0, positivity gives the ratio
interval c*∈[1+e-/d+,1+e+/d-]. A midpoint differs from c* by at most
half the interval width. For J in units weighted by σ^(-1), the coefficient
of c² is H/√(1-ρ²)≤d+/√(1-ρ²). Substitution in the completed square
gives (R.3), including the correlation factor. Optimizing the exact nonlinear
quantity does not optimize fees depending on c; a new selected c must be
substituted in the full calculation before a new price interval is stated.

For the direct comparison, the normal smoothing function is

$$F_K(x;s)=x e^{s²/2}\Phi(\log(x/K)/s+s)-K\Phi(\log(x/K)/s).$$

For positive x,s, differentiation yields
H_K=K exp[-(log(x/K))²/(2s²)]/(s x² √(2π)) and
∂sH_K=H_K[(log(x/K)/s)²-1]/s. Completing the square in log(x/K)/s
gives the representation in the TeX fragment. With w=log(x/K)/s+2s,
|(w-2s)²-1|≤2w²+8s²+1. Since max_w w² exp(-w²/2)=2/e,
the global derivative bound is

$$|\partial_s H_K(x,s)|\le
\frac{e^{2s²}}{K s²\sqrt{2\pi}}(1+4/e+8s²).$$

Along a positive line segment joining a coupled pair, s lies in [s-,s+].
Replacing the numerators by their values at s+ and the denominators by s-
gives the displayed M_K,N_K. This bounds curvature uniformly in x>0
without a lower bound on x.

For r_K(a,b,s)=F_K(a;s)-F_K(b;s)-(a-b)F'_K(b;s), differentiation gives
∂a r=F'(a)-F'(b) and ∂b r=-(a-b)H_K(b,s). Taylor's integral remainder
and differentiation on the compact positive line segment give
∂s r=(a-b)²∫_0^1(1-t)∂sH_K(b+t(a-b),s)dt. Differentiation under this
integral is justified for each outcome by continuity on its compact set of
positive x,s. There is no differentiation under the outer expectation.
The curvature bound gives |∂a r|,|∂b r|≤M_K |a-b| and
|∂s r|≤N_K |a-b|²/2.

Along the line segment, a-b is the convex interpolation of its endpoint
values, hence its absolute value is bounded by
z=max(|aP-bP|,|aQ-bQ|). The fundamental theorem of calculus thus gives
|rQ-rP|≤M_K z(|Δa|+|Δb|)+N_K z²|Δσ|/2=ΞK for every coupled pair.
Conditionally smoothing each marginal shows R_K,ν=E rν. Each remainder
is integrable under the manuscript H_s condition. The premise E ΞK<∞
and the triangle inequality yield |R_K,Q-R_K,P|≤E ΞK≤B_K. Adding the
two strike bounds and discounting yields the price-unit interval. The exact
nonlinear residual also belongs to the interval from (4.2), so taking their
intersection retains a valid enclosure. Under the diagonal coupling every
distance is zero and ΞK=0. A statement that E ΞK→0 implies vanishing
remainder differences follows immediately; neither such an input bound nor
its Heston rate has been established in this package.

Finally, for identical P and Q with an exact zero linear difference,
(4.2) has width 2γ(K1^(-1)+K2^(-1))D_P(c). The width is zero precisely
when (A-cG)²/σ=0 almost surely, namely A=cG almost surely. A simple
example inside the common Gaussian structure makes this floor strict for
every c: take S1=exp(U), S2=exp(U+V) with independent nondegenerate
normal U,V. Then A/G=cosh(V/2) is nonconstant. All relevant moments are
finite and σ is a positive constant, so D_P(c)>0 for every fixed c.

## Obligation Ledger

- O1: CLOSED-LOCAL
  - closed at: Proof, first displayed width obtained by subtracting (4.2) endpoints.
- O2: CLOSED-LOCAL
  - closed at: Proof, quadratic expansion and completed-square identity with d>0.
- O3: CLOSED-LOCAL
  - closed at: Proof, AM--GM and monotone exponential kernel for nonnegative grouped moment.
- O4: CLOSED-LOCAL
  - closed at: Proof, nonnegative tail domination and exact absolute coefficient sums.
- O5: CLOSED-LOCAL
  - closed at: Proof, sigma=(1-rho²)^(1/2) I^(1/2) and AG decomposition.
- O6: CLOSED-LOCAL
  - closed at: Proof, positive ratio endpoints and the completed-square midpoint regret bound.
- O7: CLOSED-LOCAL
  - closed at: Proof, displayed closed normal smoothing formula and differentiated curvature.
- O8: CLOSED-LOCAL
  - closed at: Proof, completed-square inequality and maximum w² exp(-w²/2)=2/e.
- O9: CLOSED-LOCAL
  - closed at: Proof, exact remainder partial derivatives, compact line-segment differentiation, and fundamental theorem of calculus.
- O10: CLOSED-LOCAL
  - closed at: Proof, conditional marginal identity, finite E Xi premise, triangle inequality and discount factor.
- O11: CLOSED-LOCAL
  - closed at: Proof, equal-model width calculation and the two-fixing Gaussian counterexample.

## Verification Checks

Localization-before-expansion: every conditional line segment is compact and
strictly positive before differentiation. No global localization event is used.

Wrong norm or mode: the conclusion is an absolute difference of expectations,
then a deterministic enclosure in price units. It is not a statistical interval.

Good-event bookkeeping: no uncharged exceptional event is used. The finite
expectation E ΞK is an explicit premise, not inferred from marginal Dν.

Rate leakage: no positive-xi Heston rate or h-convergence is asserted.

Quantifier inflation: all global bounds are for x>0 and σ>0. The two-law
comparison requires an explicit coupling and finite E ΞK.

Citation identity and imported-result applicability: no external paper is
load bearing; the original manuscript formulas used are reproduced here.

Negligibility closure: the package claims a sufficient cancellation bound.
It does not claim the numerical ΞK expectation has been evaluated or vanishes.

Boundary or singularity: the factor σ_min^(-2) is shown explicitly. The
manuscript inverse-square-root moment alone does not control this singularity.
Full H_s(c) is imposed on each marginal before comparing expectations;
E ΞK<∞ alone does not replace this finite-remainder requirement.

Discount and units: J uses σ^(-1), while the experiment's H uses I^(-1/2).
The factor √(1-rho²) cancels in c* and appears in (R.3). All price bounds
include e^(-rT).
