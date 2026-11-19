# Executed numerical evidence

`executions.zip` is the single archive for the paper's saved finite calculations. `receipt.json` identifies the archive and its internal `inventory.json`. Every retained file has a byte length and SHA-256 digest. Each execution keeps its actual numerical sources, outputs, resource records, and logs. The h = 1/192 failed analytical guard is retained because it is part of the reported step table.

`execution/` contains the principal run, step-grid runs, posterior meshes, weighted moments, and the v0 = 1/25 run. `sources/` stores support programs by content hash; these bytes are the programs identified by saved receipts. Active drivers live in `../experiments/`. A saved execution's source hash does not identify a later active driver merely because both produce the same mathematical payload.

Run `python code/verification/read_evidence.py --directory code/runs/evidence-readback --output code/runs/evidence-check.json` from the repository root, using a fresh extraction directory. This checks byte identities and exact arithmetic without rerunning the pricing kernels.
