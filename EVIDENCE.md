# Evidence and reproduction

The [`paper` release](https://github.com/130U/certified-valuation-arithmetic-asian-options/releases/tag/paper) identifies the online article and all calculations listed below. `REVISION-MANIFEST.json` inventories the public reading and verification files; `code/MANIFEST.json` verifies the original numerical package.

| Calculation | Inputs, results and execution records |
| --- | --- |
| Original certificates; step, scale and posterior-grid experiments | [Commands](code/revision/README.md), [exact ledger](code/revision/results/revision-summary.json), [archive inventory](code/revision/results/INDEX.md) |
| Second Heston parameter point | [Commands](code/revision/round2/README.md), [result](code/revision/round2/results/point-v004-result.json), [execution archive](code/revision/round2/results/evidence-point-v004.zip) |
| Deterministic coupled remainder | [Program](code/revision/round2_coupling_example.py), [result](code/revision/round2/results/coupling-v004-result.json), [proof and hash binding](docs/revision-round2/README.md) |
| Runner failure and timeout handling | [Controlled tests](code/revision/round2/test_runner_boundary.py), [test receipt](code/verification/runner-boundary.json), [successful five-task read-back](code/verification/runner-success.json) |
| Article | [English PDF](paper/paper.pdf), [read online](manuscript/report.md), [mathematical content check](manuscript/content-verification.json), [PDF build record](paper/build-record-en.json), [saved command-parser checks](code/verification/exported-command-check.json) |

The original numerical baseline is [5bc72cf](https://github.com/130U/certified-valuation-arithmetic-asian-options/tree/5bc72cf6036fdd73fea9c8bc6c85f85fd474b79a). Historical experiment data are frozen at [cf0d242](https://github.com/130U/certified-valuation-arithmetic-asian-options/tree/cf0d242f1590c7ca07ab8ca7afb57da5a583032b) and [1959f8f](https://github.com/130U/certified-valuation-arithmetic-asian-options/tree/1959f8f078e1fedd590000d6166cb20429ff31db). Their commits, numerical files and archive hashes are preserved. The publication entry above supplies the current manuscript and runner.

Saved-result checks verify byte identities and exact arithmetic ledgers. Fresh execution recomputes the finite interval calculations. Neither operation substitutes for an independent reading of the proofs.
