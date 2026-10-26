# Numerical results

| File | Meaning |
| --- | --- |
| `step-grid.json` | Full pointwise certificates, the h = 1/192 guard failure, and exact six-component widths |
| `posterior-grid.json` | Finite posterior meshes 4096, 8192, and 16384 |
| `point-v004-result.json` | Full v0 = 1/25 stochastic-Heston certificate |
| `point-v004-preflight.json`, `point-v004-receipt.json` | Analytical inputs and completed five-job execution identity |
| `coupling-v004-result.json` | Deterministic-variance coupled remainder bound |
| `asian-beta-score-bounds.json` | Analytic signed coefficient enclosures, all containing zero |
| `asian-beta-diagnostic.json`, `path-diagnostics.json` | Statistical diagnostics, without certified prices or signed coefficients |

The single `../evidence/executions.zip` archive supplies the complete source-bound arrays, logs, and execution records. Public result locators refer to its members. Readback checks saved evidence; it does not rerun pricing kernels or certify the proofs.
