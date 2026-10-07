# Independent analytical and source review: the Heston point v0=.04

The reviewed point is (κ,vbar,ξ,ρ,v0)=(3,9/200,23/100,-11/20,1/25).
S0=100, r=.01, h=1/768, twelve fixing dates i/12, the exact old rational c,
and the arithmetic Asian call spread 95/110 are unchanged. This supplies a
second stochastic-variance point by changing initial variance only. It does
not test a different Feller index or certify a parameter box.

The original `SCOPE.md`, `ENVIRONMENT.md`, `configuration.json`, `AGENTS.md`
and four numerical cores were read. The review checks the analytical domain
before the five executions. Preparation alone is not a price certificate.

## Why the constants remain valid

The Riccati flow coefficients depend on κ, d=κvbar, α=ξ²/2, ρξ, the stock
loading, the killing rate, and time. They do not depend on initial variance.
The same applies to the real B barriers, profile counts, modulus caps, complex
branch guards, and the projection-prefix u recurrence. At the new point
v0>0, so continuous first-month integrated variance is positive almost surely;
the discrete lower floor is exactly hv0=1/19200. Finite loading and branch
checks must still finish during execution even though their analytic form is
unchanged.

The projection endpoint tests, recomputed independently as rational numbers,
are βW=3000866063/368640000>8 and βL=8004253583/983040000>8. The enlarged
uniform-integrability condition is βUI=8001336523/983040000>0. The continuous
generator coefficient is a convex quadratic in real stock loading p; its
endpoint values on [-5/4,5/2] are -190761/20000 and -27417/2500, both negative.
The growth rate 4d+(5/2)r+exp(-12d-1)/3 is below .6 and does not depend on v0.
This inequality was also verified using an exact rational Taylor lower bound
for exp(131/50), independently of Arb arithmetic.

All needed price-profile moments therefore have the bound
exp(.6 T+4v0)=exp(.76) at T=1. Retaining the old M2=exp(.78) is conservative
because .76<.78. This applies both to the squared-profile moment for Fourier
tails and to the negative-loading moments used for periodization. The price
mass bounds 1 and 100 exp(.01) remain valid by the same stock-moment argument
and one-step discrete martingale identity. No moment constant is justified
only because a coefficient assertion happened to pass.

## Quantities that must change with v0

The independent source diff confirms that all four numerical variables used
for initial variance are 1/25; the vbar parameter remains 9/200 through the
unchanged d=27/200. Changing theta metadata alone would not meet this check.
The following expressions are evaluated afresh and use those actual variables:

| Quantity | Required dependence at the new point |
|---|---|
| Every P/Q transform | exp(A+Bv0), including separate real/imaginary Q evaluation |
| Every projection occupation sum | exp(-v0 u_j/h), with the same recurrence and 768 levels |
| Continuous weighted tail | C with v0 C1, and ζ=(dt1+v0)/√α |
| Discrete weighted tail | True outward nodal F_Q(64)/(128hv0) |
| Discrete frequency tail | L_Q(U)=exp(A+Bv0), and i0=hv0 in its denominator |
| Continuous frequency tail | C_P with v0 C1, and γ=(dt1+v0)√((1-ρ²)/α)/2 |
| Final residual and prices | Newly computed W_P,W_Q, linear values, and all recomputed fees |

The same κ, d, α, ρ, r, c, strikes, damping, frequency spacing, and cutoff
justify retaining their parameter-independent constants. The periodization
allowance uses the deliberately conservative retained exp(.78) moments.

## Exact source review

All four execution copies were compared line by line with the untouched cores.
The only changes are actual initial variance, theta/scope metadata, the executed
author source hash pinned by the checker, numerical target flags, and declared
finite wall-time allowances. No integrand, transform, projection, quadrature,
tail, rounding fee, coefficient guard, branch guard, precision, catalog,
frequency count, month count, or memory limit is changed.

The old remainder-radius target .011 and absolute-price target .025 are
result-acceptance goals rather than premises of any enclosure formula. In
the isolated new copies they are recorded as booleans. This permits a valid
wider enclosure without falsely asserting that an old target was met. The
768-step workload, one thread, 256 MiB worker cap and unoptimized Python remain.
Weighted/linear wall budgets are explicitly 120/360 seconds. Source identity
is rebound only after the final author copy, including resource edits, is saved.

`audit-new-point.py` reproduces the exact allowed source transformation
independently and rejects any other change. Its receipt records original and
executed hashes, rational analytical checks, and the current execution status.
If the five jobs finish, the same audit additionally verifies completed result
hashes, 257 P-node checks, 129 Q-node containments, 1923 frequency-row checks,
6399744 Q layers, and 799968 continuous branch guards. It does not rerun pricing.

## Review conclusion

The analytical extension to this particular changed-v0 point and the prepared
sources pass independent review. A complete new price statement additionally
requires all five jobs and their independent checks to finish, followed by
read-back of their exact endpoints. The accompanying JSON receipt identifies
whether that result-level gate has been met; this document does not infer
completion from preparation.
