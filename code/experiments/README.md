# Finite calculations

The drivers create isolated numerical jobs from `../core/`. Each saved result identifies the source actually executed. Parameter or mesh choices are explicit; no output replaces a failed analytical guard.

`asian_step_grid.py`, `weighted_grid.py`, and `posterior_grid.py` evaluate the stated finite grids. `asian_parameter_point.py` prepares and runs five checked jobs at v0 = 1/25. `coupling_example.py` computes a deterministic-variance Gaussian-moment bound. `asian_beta_bounds.py` encloses the analytic score bound. The NumPy programs `asian_beta_diagnostic.py` and `heston_path_diagnostics.py` are statistical diagnostics.

Commands and parameter domains are documented in [the computation guide](../../docs/COMPUTATION.md) and [SCOPE.md](../SCOPE.md).
