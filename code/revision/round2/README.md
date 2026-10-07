# A second complete stochastic-Heston point

This round executes one additional parameter point,

```
(kappa, vbar, xi, rho, v0) = (3, 9/200, 23/100, -11/20, 1/25).
```

The twelve annual fixings, arithmetic Asian call spread with strikes 95 and 110,
S0=100, r=1/100, h=1/768, scale c=1254433/1250000, continuous model and raw
positive-part Euler kernel are retained. Only initial variance changes from
.045 to .04. The resulting enclosure is pointwise; it does not certify a
parameter region.

Use the original Windows x86-64 unoptimized CPython 3.12 environment and
`python-flint==0.8.0`. From the repository root, fresh computation is:

```powershell
python -B -X utf8 code/revision/round2/asian_parameter_point.py prepare --directory code/revision/round2/runs/reviewer-point-v004
python -B -X utf8 code/revision/round2/asian_parameter_point.py run --directory code/revision/round2/runs/reviewer-point-v004
```

Preparation verifies the untouched baseline package, checks the runtime and
available memory, writes the exact mathematical preflight, and freezes four
parameter copies with a literal patch journal and source hashes. Execution runs
the weighted remainder, linear pilot, complete linear certificate, independent
weighted construction and independent linear construction. Every job must
finish before `result-capsule.json` is created. Completed runs are preserved;
use a new directory for another attempt.

The copied definitions of v0 are numerically changed to 1/25 in all four
implementations. This value enters each affine transform, each projection
prefix, the first-Euler-step variance floor, both weighted integral tails, the
first-month Laplace transform and both price-frequency tails. No old tail or
price value is substituted. The independent linear source pin binds the actual
final executed author copy.

The exact preflight verifies weighted projection beta greater than 8, linear
projection beta greater than 8, the positive discrete uniform-integrability
condition, negative continuous-generator coefficients at both loading-range
endpoints, and a growth upper bound below .6. The growth calculation is
independent of v0. Therefore the new point's price-profile moment envelope is
bounded by exp(.6+4*.04)=exp(.76), and the original exp(.78) constant remains
conservative. The first Euler integrated-variance floor is now h*v0=1/19200;
using the old h*.045 floor would be incorrect.

All analytical assertions, finite coefficient/catalogue checks, complex-log
branch guards, projection recurrences, tails, periodization and arithmetic fees
remain. The old `.011` remainder-radius and `.025` absolute-bias performance
targets are recorded as booleans, not treated as premises of the enclosure.
The declared finite worker wall budgets are 120 seconds for weighted jobs and
360 seconds for full linear jobs, with a 30-second pilot. One thread and the
Windows 256 MiB hard worker memory limit are retained. These budgets permit
desktop CPU-load variability and do not change the mathematical computation.

The result capsule records exact rational endpoints for bias Q minus P and
separate P and Q prices. Its six-component width ledger is reconstructed from
the executed results and reconciled by exact fractions. The original baseline
results, previous revision files and their evidence archive are not modified.

The completed five-job run took 97.47 seconds in the recorded environment. Its
outward price-difference enclosure is
[-0.011798506839755763560265, 0.011383739258625372365583], with width at most
0.023182246098381135925847. The continuous price enclosure is
[6.499318797594356329316702, 6.509948941255972621471292]; the raw Euler price
enclosure is [6.498150434416216857911027, 6.510702536852981701682285]. The two
old performance targets both pass at this point. Runtime measurements are
observations on one machine, not a performance guarantee.

`results/point-v004-result.json` is the curated result capsule. The
`six_component_exact_width_ledger` field contains nonlinear payoff,
projection, continuous frequency tail, discrete frequency tail, periodization,
and arithmetic/endpoint reconciliation contributions. Every component has an
exact rational value and outward decimal upper bound. The source fields and
proof references are recorded alongside the ledger. `results/point-v004-receipt.json`
contains every job, literal source change, hash and finite resource budget;
`results/point-v004-preflight.json` records the analytical obligations.

`results/evidence-point-v004.zip` contains all executed sources, results,
controller and worker logs, the untouched baseline source evidence, exact
ledger reader, entry point and the separately authored analytical/source
audit. Its `inventory.json` hashes every member. The archive receipt binds the
archive, inventory and result capsule. This archive is separate from the
previous revision's `code/revision/results/evidence.zip`.

Saved-result readback uses only the Python standard library; from the
repository root, use a fresh extraction directory:

```powershell
python -B -X utf8 code/revision/round2/replay_point.py --archive code/revision/round2/results/evidence-point-v004.zip --receipt code/revision/round2/results/archive-receipt.json --directory code/revision/round2/runs/reviewer-readback --output code/revision/round2/runs/reviewer-readback-receipt.json
```

This verifies all archive hashes, replays the exact source and rational
preflight audit, reconstructs the capsule, compares 386 weighted nodes and
1,923 frequency intervals, compares all seven linear fees, and reconciles the
six width components with exact fractions. It checks saved-result
consistency. Fresh numerical recomputation requires the two commands above
and the stated runtime. The recorded local readback is
`results/evidence-readback.json`.

The independent weighted construction uses the 384-bit hyperbolic matrix flow,
ordered-pair catalogue and separate reverse-grid indexing. The independent
linear construction uses complex Euler recursion and exponential matrix
blocks, checking all frequencies and fees. These computations share Arb and
the underlying bounds; they are implementation checks rather than independent
derivations of the theory.
