# Reference numerical payloads

These files were copied from established results before executing this public package. Hash identities and timing fields were removed because source paths, documentation identities and execution durations change when a package is relocated. Mathematical fields were retained, including exact rational intervals, decimal enclosures, arrays, booleans, guard counts and fee components. A few descriptive strings were updated to identify the stable public layout.

`run.py` compares every remaining field exactly, without a tolerance. Its exclusions are keys ending in `sha256` and the six timing names `worker_seconds`, `elapsed_seconds`, `seconds`, `outer_seconds`, `envelope_worker_seconds`, and `full_linear_time_estimate`. The portability record contains the original and public source hashes. Source guards still bind generated results to the currently executed files.

The deterministic TT pointwise checks use v0 = 3/50. The common vector is nonzero when v0 differs from vbar; it vanishes at v0 = vbar. The report's uniform remainder claim and the source's pointwise coefficient check should not be conflated.
