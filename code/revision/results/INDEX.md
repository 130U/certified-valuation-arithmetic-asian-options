# Revision numerical evidence

`revision-summary.json` and `revision-budget.json` are byte-identical copies of
the final exact-rational ledger produced by `read_budget.py`. The summary is the
manuscript's entry point. It records all price-unit error components, formula
and source-field traces, input/output hashes, completed checks and failed grids.

| Artifact | Meaning |
|---|---|
| `base-run-receipt.json` | Actual completed original Asian/posterior ten-job execution; exact reference payload comparison passed. |
| `asian-192-failure-receipt.json` | No certificate: fixed-lambda projection beta is below its required 8. |
| `asian-384-receipt.json` | Complete finite-grid pointwise enclosure, with the old `.011` remainder-radius target recorded as failed. |
| `asian-1536-receipt.json` | Complete finite-grid pointwise enclosure under the declared scaled wall budget; one thread and 256 MiB worker limits retained. |
| `posterior-8192-receipt.json`, `posterior-16384-receipt.json` | Principal/compatibility mathematical equality and independent whole-cell/coupling audits passed. |
| `posterior-grid-summary.json` | Exact mesh displacement bounds, v0 marginal CDF envelopes and absolute v0 quantile brackets. These are not absolute Asian-price posterior quantiles. |
| `asian-beta-score-bounds.json` | Four rigorously enclosed score norms and analytical h-squared residual bounds; every signed beta interval contains zero. |
| `asian-beta-diagnostic.json` | Optional iid Gaussian statistical diagnostic of signed beta and scaled residuals; not a strict integral enclosure. |
| `path-diagnostics.json` | Optional paired-path sensitivity and fixing-count statistics; confidence intervals are not strict price enclosures. |
| `evidence.zip`, `evidence.receipt.json` | Complete compressed execution archive and its SHA-256, including exact executed sources, outputs, all successful/failed controllers, logs and source snapshots. |

The full archive preserves the original run, canonical coarse/fine grids,
posterior cells and all weighted moment nodes. Historical failed attempts are
retained alongside successful revisions; they must not be mistaken for final
enclosures. A replay verifies actual archived inputs, rather than trusting a
summary that points at a private filesystem path:

```powershell
Expand-Archive code/revision/results/evidence.zip -DestinationPath replay-evidence
python -B -X utf8 code/run.py check --run replay-evidence/execution/base-run
python -B -X utf8 code/revision/read_budget.py --execution-root replay-evidence/execution --base-run replay-evidence/execution/base-run --output replay-evidence/replayed-summary.json
```

Verify each member against `EVIDENCE-INVENTORY.json`; the archive receipt binds
the zip bytes. Replayed numerical rows match the frozen summary's values. Path
strings differ after extraction and are execution metadata. Fresh computation
uses the commands in `../README.md` and new output directories, preserving all
already completed receipts.

The c comparison is a nonlinear-width experiment; the retained c is already
near the optimizer. The broad beta enclosure, statistical beta estimate and
uncomputed signed integral remain separate. No stochastic-Heston joint
first-order expansion, original five-dimensional-prior posterior certificate,
uniform original-domain price certificate or signed nonzero Asian coefficient
is claimed by these artifacts.
