# Independent review of the revision numerical extensions

Review date: 2026-10-07. This is a source and retained-output review. No expensive
pricing calculation was rerun for this review. The original baseline kernels
were used as the comparison, together with manuscript (A.1)--(A.8), (B.1)--(B.6),
(C.5)--(C.10), (6.4)--(6.8), and (F.2)--(F.6).

The actual extension filenames inspected are `weighted_grid.py`,
`posterior_grid.py`, and `asian_beta_bounds.py`. There is no
`asian_beta_score.py`. The subsequently added `asian_step_grid.py` was also
inspected for the full-price step experiments. `heston_path_diagnostics.py`
is outside the mathematical-certification review reported below.

No confirmed mathematical error was found in these extensions under their
stated scopes and guards. There is one real analytical exclusion at h=1/192,
one original acceptance threshold that must be distinguished from an analytical
premise, and an exact-midpoint versus rounded-candidate distinction.

## Weighted moments, scaling choice, and step changes

`weighted_grid.py` constructs the same 91 normalized total-stock-loading-2
profiles, grouped into A², AG, and G². Each positive group has total coefficient
10000. The ordered A² catalog, the twelve AG loadings, and the G² loading agree
with the original kernel. At every positive Laplace node, the continuous flow
and the actual discrete-kernel correction retain the original conventions.

The continuous construction in ordinary mode uses root/cross-ratio flow;
the 384-bit alternate mode uses a hyperbolic Riccati matrix. Discrete ordinary
mode uses month blocks; the alternate mode separately indexes the reversed
grid. The two modes share the analytical bounds and the Arb library, so their
agreement tests implementation and arithmetic, rather than independently
proving the analytical formulas.

The change of step count is correct: with N=T/h, the first fixing interval
contains N/12 steps, the subsequent eleven intervals are cached with the
corresponding reverse-grid index, and the projection-prefix sum contains N
terms. Both A and B updates use the previous B. Every discrete coefficient
remains checked against -512<B≤1.

For the weighted-moment projection correction, the minimum endpoint test is

β(N)=min_{s∈{12,12+512/N}}
{s(1-3253/(1000N))-(529/20000)s²-1/N²}.

The fee is still `(512/(12e))*exp(4r+d-12d)*h*prefix_sum`; no extra h is
introduced or removed. Exact rational evaluation gives:

| N | β(N) exact | Analytical requirement β>8 |
|---:|---|---|
| 192 | 184040303/23040000 | Fails |
| 384 | 745531727/92160000 | Passes |
| 768 | 3000866063/368640000 | Passes |
| 1536 | 12040940687/1474560000 | Passes |

Thus h=1/192 cannot use the retained e^(-8v/h) prefix argument. A guard stop at
that grid is a failure to certify by this particular bound; it is not evidence
that the price or the numerical scheme is inaccurate. This guard must remain
an analytical assertion.

The additional uniform-integrability checks use the correct h dependence.
For the enlarged real-loading range [-5/4,5/2] needed by the full transform
argument, the continuous variance generator coefficient is a convex quadratic
in p. Its endpoint values are -190761/20000 and -27417/2500, both negative.
The worst discrete condition

12η_(5/2)-144α-(15/8)h²>0

is positive for all four step counts. These facts, together with the retained
growth bound below .6 and 4v0=.18, justify retaining the moment constant
M2=exp(.78) at the otherwise admissible changed steps.

The grouping used for scale optimization is valid. A≥G pathwise gives
(A-G)G≥0, and the resulting Laplace integrand is nonincreasing. Evaluating
AG-G² at each node before Darboux summation retains cancellation. The true
Q nodal projection allowances are 10000δ for G² and 20000δ for AG-G².
The continuous tail of either positive raw moment is bounded by
10000 C exp(-ζX)/ζ, with X=128. The difference moment is bounded by the AG
tail because 0≤(A-G)G≤AG. Multiplication by 2/√π is retained in integration.

For Q, the same true nonnegative integrand at X=64 and I_Q≥hv0 give the tail
bound F_Q(64)/(128hv0), including the outward nodal projection fee. This
correctly changes with h. For the square, the continuous tail coefficient
2(1+c²) times the single-positive-moment tail agrees with
(A-cG)²≤2A²+2c²G². The square's Q point fee is
10000(1+c)²δ. The strike-dependent discount factor retains √(1-rho²) in
the denominator.

The reported scale bracket uses c*=1+E+/H with positive denominator bounds.
The executed candidate is the bracket midpoint rounded to a rational lattice
of spacing 10^-7. This is a valid predetermined c for recomputing the square,
but it is not the exact rational midpoint in formula (R.3). A regret statement
for this candidate must use

J(c_selected)-J(c*)≤d_upper*[(c_plus-c_minus)/2+5*10^-8]²,

where d_upper is in σ^-1 units, or replace 5*10^-8 with the exact distance
between the selected candidate and the midpoint. No rounding loss needs to
be charged to the price certificate if its square and linear terms are
recomputed at the selected rational c.

Retained 256/384-bit results for h=1/384 and h=1/768 were read and compared
without rerunning the calculation. At each grid all 772 stored positive/difference
group node pairs overlap: 2 groups times (257 P nodes + 129 Q nodes). The
scale-ratio intervals overlap, and the selected rational scales agree. These
are checks of the stored grouped-moment results, not a full-price certificate.

## Full-price step orchestration

`asian_step_grid.py` copies the four original Asian modules into separate
execution directories. Its step parameter, every month-loop count, every
reversed-grid boundary, and the expected Q layer count are consistent.
The number of continuous branch guards remains 799968 because the thirteen
profiles, 641 frequencies, and eight continuous subintervals per month have
not changed. The continuous subinterval length remains 1/96. The original
branch guards, Re B and modulus guards, projection tests, Gaussian prefix
positivity, and first-month Laplace-tail tests are retained.

The complete linear correction still includes projection, both frequency
tails, twice the one-law alias fee, and outward arithmetic. Its discrete tail
uses N/12 first-month steps and i0=hv0, so the scaling is correct. The original
linear frequency catalog and periodization spacing have not changed.

The original terminal test `remainder_radius < .011` is a reported numerical
target at h=1/768. It is not used to derive any interval endpoint, quadrature
tail, projection allowance, moment identification, or branch bound. In the
new h=1/384 copies, recording this test as
`original_remainder_radius_target_pass=false` permits a wider valid enclosure
to be reported. This change must be journaled and must not be described as
meeting the old numerical target. The updated orchestrator records that
specific acceptance-assertion change. None of the analytical guards may be
converted to a flag on the same rationale.

A full-price row is certified only after both original-style computations
and both independent checks complete, including every frequency and fee.
A time/resource/analytical guard stop does not produce a complete price
enclosure. Review of the orchestration alone cannot replace those results.

## Posterior meshes and coupling

`posterior_grid.py` changes only the admitted mesh selection, the separately
copied independent-checker cell count, and its author-output filename. The
price formulas, 192-bit principal arithmetic, whole-cell boxes, nuisance-slab
price radii, and target-transfer bounds retain the original h=1/768 prior
domain. No Heston parameter-domain expansion is implied.

Endpoint Black prices remain valid whole-cell bounds because the reference
variance loading is positive and put vega is positive. Expanding the endpoints
by the unchanged positive-xi price radii encloses the entire u cell and the
entire nuisance slab. Likelihood squares are evaluated through the original
sum of nonnegative quadratic terms, and both integer endpoint roundings are
outward on the 2^-96 lattice. The CDF construction retains the shared mass
in numerator and denominator rather than normalizing unrelated bounds.

The independent checker uses complementary-error-function Black tails,
128-bit integer price intervals for quadratic boxes, and advancing pointers
for inverse-CDF pairing. Changing M consistently changes its dx=.03/M,
its complete weight scan, and its coupling scan. The retained output counts
confirm the following completed checks:

| Mesh | Whole-cell weight containments (4M) | Author coupling cell checks (2M) | Independent status |
|---:|---:|---:|---|
| 8192 | 32768 | 16384 | INDEPENDENT_POSITIVE_XI_3D_POSTERIOR_AUDIT_PASS |
| 16384 | 65536 | 32768 | INDEPENDENT_POSITIVE_XI_3D_POSTERIOR_AUDIT_PASS |

Both execution receipts are COMPLETE and record exact principal/compatibility
agreement on all mathematical fields. The duplicate principal and compatibility
implementations are not claimed to be mathematically independent; the separate
384-bit checker is the implementation audit.

The summary's CDF bands and absolute quantile brackets concern the v0 marginal.
They do not provide absolute posterior quantiles of the Asian price. The Asian
output remains an all-level bound on P/Q quantile displacement. The script
states this distinction. The nine-quote bound remaining wider must not be
interpreted as proving a larger actual discretization bias.

## Asian first coefficient

`asian_beta_bounds.py` evaluates the exact deterministic increment variances,
their first variance perturbation coefficients, and the Fisher/score upper
bound. The coefficient enclosure is the symmetric interval [-Bscore,Bscore],
with

Bscore=(15 exp(-r)/2)*sqrt(Σ_j d_j² J(s_j)).

The factor 1/2 is justified by centering the bounded call-spread payoff and
the score's zero integral. Discounting is retained. The alternate expression
of d_j is algebraically identical to the first expression. The 384/512-bit
comparison checks numerical consistency rather than an independent proof.

For h=1/768 and h=1/1536, the script checks the actual aligned variance
increments against the analytical h² increment remainder. Its per-coordinate
lower variance is min(s_j,s_h,j), which bounds the entire interpolation
segment. Substitution into J and H2 therefore yields a valid pointwise
analytical bound for |e_h-hβ_Asian|. Setting h0=h for each individual bound
is admissible in the original expansion argument.

This computation does not integrate the signed twelve-dimensional score
expectation defining β_Asian. All enclosures contain zero. It does not
establish nonvanishing or experimentally verify the order of the observed
price residual. The script's no_claim fields explicitly preserve those
limitations. The review recommendation asking for a practically informative
signed coefficient computation remains only partly addressed by these
analytical enclosures.

## Conclusion and scope of this review

The checked extensions preserve the original analytical error allowances and correctly
scale the changed mesh or step count. The h=1/192 exclusion, the wider
h=1/384 acceptance result, the limited independence of shared-Arb checks,
and the unevaluated signed Asian leading coefficient must all remain visible
in the revised manuscript and response letter. New experiment results should
be frozen by their execution hashes after the running full-price checks finish.
