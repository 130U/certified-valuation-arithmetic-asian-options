# Evidence and reproduction

The [paper](manuscript/report.md), [PDF](paper/paper.pdf), programs and numerical results form the 2026 publication. [PUBLICATION-MANIFEST.json](PUBLICATION-MANIFEST.json) inventories its files. The [mathematical structure](docs/MATHEMATICAL-STRUCTURE.md) and [computational details](docs/COMPUTATION.md) explain how the recorded quantities arise from the proof.

## Results and programs

| Calculation | Program | Result |
| --- | --- | --- |
| Principal Heston price certificate | [Numerical runner](code/run.py) and [core calculations](code/core/) | [Weighted moments](code/reference/asian-remainder-result.json), [linear term and price interval](code/reference/asian-linear-result.json) |
| Euler step comparison and exact width components | [Step calculation](code/experiments/asian_step_grid.py) | [Step and width ledger](code/results/step-grid.json) |
| Common geometric scale | [Grouped weighted moments](code/experiments/weighted_grid.py) | [Scale calculation in the paper](manuscript/report.md) and [execution evidence](code/evidence/executions.zip) |
| Second Heston point, $`v_0=.04`$ | [Parameter-point calculation](code/experiments/asian_parameter_point.py) | [Price result](code/results/point-v004-result.json), [inputs and analytical conditions](code/results/point-v004-preflight.json), [execution receipt](code/results/point-v004-receipt.json) |
| Deterministic coupled remainder | [Closed Gaussian moments](code/experiments/coupling_example.py) | [Coupled and separate-law widths](code/results/coupling-v004-result.json) |
| Gaussian weak coefficient bounds | [Analytic bounds](code/experiments/asian_beta_bounds.py) | [Coefficient and remainder enclosures](code/results/asian-beta-score-bounds.json) |
| Gaussian score illustration | [Sampling calculation](code/experiments/asian_beta_diagnostic.py) | [Estimates and standard errors](code/results/asian-beta-diagnostic.json) |
| Heston path illustration | [Coupled path calculation](code/experiments/heston_path_diagnostics.py) | [Sampling results](code/results/path-diagnostics.json) |
| Posterior quantile transfer | [Cell calculation](code/experiments/posterior_grid.py) | [CDF envelopes and displacement bounds](code/results/posterior-grid.json) |

The [execution archive](code/evidence/executions.zip) contains the source copies, exact outputs, worker traces and job records used by these calculations. Its [receipt](code/evidence/receipt.json) identifies the archive and member inventory. The [evidence read-back](code/results/evidence-readback.json) records the checks of these materials. Analytical guards, result-acceptance targets and resource stops have distinct entries in the evidence.

## Verify the publication

Run the following from the repository root with Python:

```sh
python scripts/check_report.py
python scripts/verify_publication.py
python code/run.py verify
python code/verification/read_evidence.py --directory evidence-check --output evidence-readback.json
```

Use a new directory name for each archive read-back. The [reader](code/verification/read_evidence.py) checks the complete archive and its exact result ledgers using the Python standard library. [Parameter-point checks](code/verification/check_parameter_point.py), [runner integrity tests](code/verification/test_run_integrity.py) and [parameter-runner boundary tests](code/verification/test_parameter_point_boundary.py) exercise the corresponding validation rules.

The [formula inventory](manuscript/equations.json), [article content record](manuscript/content-verification.json) and [PDF build record](paper/build-record-en.json) bind the reading formats to the publication. File identity, ledger reconciliation and fresh numerical calculation are separate verification steps.

## Recompute the main examples

The [execution environment](code/ENVIRONMENT.md) specifies Windows, CPython and python-flint, together with the finite worker resource limits. Run fresh calculations in that environment from the repository root:

```sh
python code/run.py run --module asian --independent
python code/run.py check --run code/runs/run-ID
```

Replace `code/runs/run-ID` with the directory reported by the run. The complete Asian calculation includes the principal weighted and linear modules and their alternative numerical constructions.

For the second initial-variance point, use a new output directory:

```sh
python code/experiments/asian_parameter_point.py prepare --directory parameter-point-run
python code/experiments/asian_parameter_point.py run --directory parameter-point-run
python code/experiments/asian_parameter_point.py capsule --directory parameter-point-run --output parameter-point-result.json
```

For the deterministic coupled-remainder example:

```sh
python code/experiments/coupling_example.py --output coupling.json
```

The score and path illustrations additionally use NumPy; their result files retain the sample sizes, seeds and estimated standard errors. The interval calculations use exact rational endpoints and Arb enclosures. The mathematical assumptions and interpretation of each result are stated alongside its theorem and numerical table in the paper.

[Paper](manuscript/report.md) · [English PDF](paper/paper.pdf) · [Computational details](docs/COMPUTATION.md)
