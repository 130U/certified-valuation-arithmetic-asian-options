# Grid and error-budget experiments

These scripts calculate mesh and error-budget comparisons while keeping
the original files in `code/core/` unchanged. The checked-in results describe
completed executions; a stopped execution is never represented as a certificate.
Read `../SCOPE.md`, `../ENVIRONMENT.md`, `../configuration.json`, and `../WORKING_GUIDE.md`
first. Original mathematical payloads must match every reference exactly.

## Environment and the original executable certificate

Use unoptimized Windows x86-64 CPython 3.12 and `python-flint==0.8.0`:

```powershell
python -m pip install -r code/requirements.txt
python -B -X utf8 code/run.py environment
python -B -X utf8 code/run.py run --module asian posterior --independent
```

Save the printed completed run directory as `BASE_RUN` below. This original
execution runs ten jobs, preserving copied source, exact rational endpoints,
all node/frequency/cell arrays, logs, controller contracts and an exact-payload
comparison receipt. `code/run.py check --run BASE_RUN` verifies them again.
The `base-run-receipt.json` in `results/` records the recorded ten-job
execution. `BASE_RUN` is the directory produced on the reviewer's own machine;
the checked-in receipt is evidence, rather than a directory guaranteed to exist
on that machine.

No global Python change, compiler, NumPy or market-data service is needed for the
interval calculations. Optional path and Gaussian-score diagnostics use
`numpy==2.3.5` and report statistical uncertainty, not strict enclosures.

## Complete Asian step comparison

```powershell
python -B -X utf8 code/revision/asian_step_grid.py --steps 192 --output code/revision/runs/asian-192-failed
python -B -X utf8 code/revision/asian_step_grid.py --steps 384 --output code/revision/runs/asian-384-enclosure
python -B -X utf8 code/revision/asian_step_grid.py --steps 1536 --output code/revision/runs/asian-1536-enclosure
```

The script creates immutable parameter copies and a patch journal. It changes
`h`, all dependent month/year step counts and reverse indices, expected workload
counters, and the author's source-identity pin used by the independent checker.
The same 641 Fourier frequencies and 91 weighted profiles are retained. The
continuous branch guards, Euler coefficient guards, integral tails,
periodization, projection correction and interval arithmetic error allowances remain in
force. The original tolerances `remainder radius < .011` and `absolute bias <
.025` are recorded as result flags in these experiment copies, so that a valid
wider enclosure can be reported. They are numerical acceptance targets, not
premises of the enclosure proof. No analytical precondition is removed.

The fixed-lambda projection proof fails at `h=1/192`: its minimum beta is exactly
`184040303/23040000`, approximately `7.987860373263889`, whereas the recurrence
uses the premise `beta > 8`. The stopped run therefore has no price enclosure.
The initial `h=1/384` attempt also stopped at the old `.011` radius acceptance
target; the subsequent experiment preserves that failed target as a boolean and
computes a wider complete enclosure. The initial `h=1/1536` attempt exceeded its
original 55-second weighted-worker budget under concurrent CPU load. A new
bounded resource contract scales wall budgets by `ceil(N/768)`; all mathematical
guards, one thread per worker and the Windows 256 MiB memory limit are retained.
Old attempts and their logs are preserved in the local execution archive.

For each successful grid, all five original jobs finish, including both
independent constructions. The independent weighted calculation uses a
hyperbolic Riccati matrix, an ordered-pair catalogue, a separately indexed
reverse Euler grid, exact rational Darboux sums and 384-bit arithmetic. The
independent linear calculation uses complex Euler recursion and exponential
matrix blocks, checking every frequency, source binding and error allowance. Sharing Arb
and the analytical proof does not exclude a common proof error.

The retained obligations include
`12 eta_(5/2) - 144 alpha - (15/8) h^2 > 0`, the negative continuous variance
barrier coefficient, the uniform growth bound below `.6`, the projection
`beta > 8` condition, positivity of its recurrence, negative first-month
Laplace coefficients, `Re(B) <= 1`, the appropriate `|B|` bound, and every
complex-logarithm branch guard. The bound `M2=exp(.78)` is the original
load-profile moment bound; it is not inferred from a floating-point scan. These
finite-grid computations do not extend the deterministic Talay--Tubaro theorem
to `xi=.23` or to its excluded step sizes.

## Common c and positive weighted moments

```powershell
python -B -X utf8 code/revision/weighted_grid.py --steps 768 --output code/revision/runs/weighted-768-author.json
python -B -X utf8 code/revision/weighted_grid.py --steps 768 --independent --output code/revision/runs/weighted-768-independent.json
```

Repeat at steps `384` and `1536` for the other successful grids. Each run
compares `c=1`, the retained exact `c=1254433/1250000`, and the midpoint of the
computed optimizer enclosure rounded to a rational lattice of spacing `1e-7`.
The output records that selected rational
value; `--c RATIONAL` can add a previously frozen candidate when comparing two
constructions.

The separate weighted-moment worker has a declared wall guard of 80 seconds
(principal) or 110 seconds (matrix construction), multiplied by `ceil(N/768)`
for the finer grid. A previous 1536-step attempt stopped at the original
unscaled guard without producing a result; its executed source snapshot and
failure record are preserved. Increasing the declared finite runtime budget
does not change the moments, arithmetic precision or analytical inequalities.

For the common rho, the common factor `sqrt(1-rho^2)` cancels from the optimizer:

```
d = sum_(P,Q) E[G^2 / sqrt(I1)]
e = sum_(P,Q) E[(A-G)G / sqrt(I1)]
c_star = 1 + e/d
```

AM--GM gives `(A-G)G >= 0`. Its Laplace transform, as well as the `G^2`
transform, is nonnegative and nonincreasing. Computing the combined `AG-G^2`
node before integration keeps the cancellation; subtracting two separately
enclosed moments would be looser. The positive moment groups each have weight
sum 10000. Their continuous tail is bounded by
`10000 C exp(-zeta X)/zeta`, and the `e` tail is no larger than the `AG` tail.
The Euler projection error allowances are `10000 delta` for `d`, `20000 delta` for `e`,
and `10000(1+c)^2 delta` for the square. Euler tails use each true nonnegative
Laplace function's upper endpoint at 64, divided by `128 h v0`. Every final
integral includes `2/sqrt(pi)`.

The 256-bit cross-ratio flow and 384-bit hyperbolic matrix flow provide different
continuous constructions; the latter uses a separately indexed reverse Euler
grid. The budget reader checks all moment-node overlaps. These are independent
numerical constructions within a single revision script, rather than an
independent derivation of the theorem. The retained `c=1.0035464` is already
near the optimizer; the optimizer enclosure does not assert an exact numerical
value or optimize the total certificate.

## Posterior grid and uncertainty-scale diagnostic

```powershell
python -B -X utf8 code/revision/posterior_grid.py run --cells 8192 --base-run BASE_RUN --output code/revision/runs/posterior-8192
python -B -X utf8 code/revision/posterior_grid.py run --cells 16384 --base-run BASE_RUN --output code/revision/runs/posterior-16384
python -B -X utf8 code/revision/posterior_grid.py summary --result BASE_RUN/work/core/posterior-4096-result.json --result code/revision/runs/posterior-8192/work/core/posterior-8192-result.json --result code/revision/runs/posterior-16384/work/core/posterior-16384-result.json --output code/revision/runs/posterior-grid-summary.json
```

Only finite grid selection and its independent check's mesh/index values change.
There is no change to likelihoods, priors, whole-cell weights, target Lipschitz
bound, perturbation error allowances or 256 MiB resource controls. Each mesh is independently
checked with erfc Black tails, exact 128-bit price-interval quadratic squares,
and advancing-pointer transport. Principal and compatibility implementations
must agree on every nonmetadata mathematical field. The summary reconstructs
exact CDF envelopes and 0.025, 0.5 and 0.975 quantile brackets from the executed
whole-cell integer weights. Those absolute brackets concern the v0 marginal;
Asian-price target quantiles have only a P/Q displacement enclosure. A larger
nine-quote enclosure does not prove a larger true numerical bias.

## Asian leading coefficient: completed bound and remaining integration

```powershell
python -B -X utf8 code/revision/asian_beta_bounds.py code/revision/runs/asian-beta-score-bounds.json
```

This computes the Gaussian density-score norm at `v0=.03,.04,.05,.06`, providing
a rigorous signed interval `[-B sqrt(Fisher)/2, B sqrt(Fisher)/2]`, with
`B=15 exp(-r)`. It also evaluates analytical bounds on `|e_h-h beta|` at 768
and 1536 aligned steps, using the finite Gaussian variance-remainder formulas
from the original deterministic module. Two precisions and algebraic
re-expressions check the finite computations. Every signed interval contains
zero: the twelve-dimensional signed coefficient integral and a nonzero Asian
coefficient certificate remain unevaluated. The optional Gaussian-score
diagnostic supplies Monte Carlo estimates and scaled residuals with statistical
uncertainty; it does not replace the strict bounds.

## Traceable price-unit ledger

```powershell
python -B -X utf8 code/revision/read_budget.py --execution-root code/revision/runs --base-run BASE_RUN --output code/revision/results/revision-budget.json
```

The reader requires completed receipts and exact source/result hashes. It
reconciles the final signed-bias width using exact fractions:

```
width = nonlinear_remainder_width + 2*linear_fee + finite_bias_arithmetic_width
linear_fee = projection + tail_P + tail_Q + 2*one_law_alias
```

The output binds every row to input hashes and names the source fields and
analytical construction. Curated `results/` retain these exact ledgers and
execution receipts. Full generated runs and virtual environments are excluded
from version control. `results/INDEX.md` identifies the completed and partial
results. A result's scope hash binds prose; it is not a machine-checked proof.
