# Reproducing the Heston point and deterministic coupling example

Run these commands from the repository root with unoptimized Windows x86-64
CPython 3.12 and `python-flint==0.8.0`. Install the locked requirement with
`python -m pip install -r code/requirements.txt`. Workers use one thread and a
256 MiB hard memory limit; their preflight requires at least 512 MiB of
available physical and commit memory. Use a fresh output directory for every
attempt. A stopped computation exits unsuccessfully and produces no final
certificate capsule.

The stochastic Heston point is
`(kappa, vbar, xi, rho, v0) = (3, 9/200, 23/100, -11/20, 1/25)`, with
`S0=100`, `r=1/100`, `h=1/768`, twelve fixings at `m/12`,
`c=1254433/1250000`, and the arithmetic Asian spread `(A-95)+-(A-110)+`.
Its certificate covers this point and the original positive-part Euler kernel.

```powershell
python -B -X utf8 code/revision/round2/asian_parameter_point.py prepare --directory code/runs/reviewer-point
python -B -X utf8 code/revision/round2/asian_parameter_point.py run --directory code/runs/reviewer-point
```

Preparation verifies the baseline package, records the exact analytical
preflight and freezes the parameter copies. Execution completes the weighted
remainder, linear pilot, full linear calculation and both independent
checks. Every v0-dependent transform, projection prefix, variance floor and
tail is recomputed. All mathematical guards remain. The conservative
`exp(.78)` moment envelope is valid since `.6+4v0=.76<.78`.

The output is `code/runs/reviewer-point/result-capsule.json`. The stored
[point result](results/point-v004-result.json) encloses bias Q minus P by
`[-0.011798506839755763560265, 0.011383739258625372365583]`, with width at most
`0.023182246098381135925847`. Its `six_component_exact_width_ledger` records
nonlinear payoff, projection, P and Q frequency tails, periodization, and
arithmetic/endpoint reconciliation, all in price units with exact rational
values. The [execution receipt](results/point-v004-receipt.json) and
[preflight](results/point-v004-preflight.json) bind the inputs and executed
sources. Independent constructions check all 386 weighted nodes, 1,923
frequency intervals and seven linear error allowances. They share Arb and the analytical
bounds; this verifies implementation consistency.

The coupled remainder example sets `xi=0`, retaining the other displayed
inputs. It is completed using finite closed Gaussian moments and validated
inequalities at 384 and 512 bits. It certifies the remainder comparison;
a positive-xi Heston coupling certificate remains incomplete. It does not
compute a full price or a signed Asian leading coefficient.

```powershell
python -B -X utf8 code/revision/round2_coupling_example.py --output code/runs/reviewer-coupling.json
python -B -X utf8 scripts/verify_fresh_examples.py --point code/runs/reviewer-point/result-capsule.json --coupling code/runs/reviewer-coupling.json
```

The [coupling result](results/coupling-v004-result.json) contains both
precision runs and the proved comparison with the separate-law remainder
width. The comparison command checks every frozen mathematical field and
array exactly, excluding only the declared hashes and execution metadata.

The current entry points execute directly from this checkout. The immutable
[point archive](results/evidence-point-v004.zip) preserves the executed
sources, all five outputs and logs, and the exact source/mathematical audit.
Stored source hashes refer to those archived bytes. Its
[archive receipt](results/archive-receipt.json) binds SHA256
`338964eadb54b51fc1b0ff027df61da870cb2f4ae304421e7f1788bd47310db3`.
Existing commit and archive identifiers remain available. Saved-result
readback requires only the Python standard library:

```powershell
python -B -X utf8 code/revision/round2/replay_point.py --archive code/revision/round2/results/evidence-point-v004.zip --receipt code/revision/round2/results/archive-receipt.json --directory code/runs/reviewer-readback --output code/runs/reviewer-readback-receipt.json
```

This checks archive hashes, the exact source audit, all stored node/frequency
comparisons and rational width reconciliation. It does not rerun pricing
kernels. The recorded [readback receipt](results/evidence-readback.json) and
current [runner success receipt](../../verification/runner-success.json)
distinguish these checks from fresh numerical recomputation.

The actual subprocess boundary tests exercise ten success/failure cases and
validate all five completed output structures:

```powershell
python -B -X utf8 code/revision/round2/test_runner_boundary.py --directory code/runs/reviewer-boundary --reference code/runs/reviewer-point
```

The [boundary receipt](../../verification/runner-boundary.json) records the
local test results. Windows CI runs the same CLI after the full point
calculation, including timeouts after output, nonzero exits, existing or
incomplete outputs, and finalizer failures.
