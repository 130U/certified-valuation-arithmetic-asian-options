# Reference numerical payloads

`run.py` compares each completed result with these exact mathematical payloads. Every rational interval, decimal enclosure, array, Boolean guard, count, and fee component is retained. The comparison excludes only keys ending in `sha256` and six timing fields: `worker_seconds`, `elapsed_seconds`, `seconds`, `outer_seconds`, `envelope_worker_seconds`, and `full_linear_time_estimate`.

Source and result bytes are checked separately against the execution receipt. `verification/numerical-reference.json` identifies the numerical inputs, kernels, and comparison records. Full saved executions are in `evidence/executions.zip`.

The deterministic TT pointwise check uses v0 = 3/50. The common vector is nonzero when v0 differs from vbar and vanishes at v0 = vbar. The paper's uniform remainder claim and this pointwise coefficient check have different scopes.
