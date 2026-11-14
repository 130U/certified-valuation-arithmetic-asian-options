# Studies

Four calculations for Sections 4 to 6 of the [paper](../manuscript/report.md). They stand beside the certified package in [`code/`](../code): the first is a proof in ball arithmetic under Black's model, the others are binary64 computations that say what the proved intervals of Section 5 contain.

| Program | What it computes | Result |
| --- | --- | --- |
| [`run_black.py`](run_black.py) | Table 1. For twelve market-style contracts under Black's model: the proxy-exercise value, both kink bounds and the price interval, in Arb at 256 bits from exact rational inputs. Adds a simulated cost and the classical first-order bound as binary64 diagnostics. | [`black-contracts.json`](results/black-contracts.json) |
| [`run_heston_contracts.py`](run_heston_contracts.py) | Table 2. The same contracts under Heston dynamics, by simulation with the first-period factor integrated in closed form. | [`heston-contracts.json`](results/heston-contracts.json) |
| [`run_gap_profile.py`](run_gap_profile.py) | Section 5.5 and Figures 1 and 3. The cost of the kink across strikes for the Heston contract of Section 5, its second-order term, the two bounds, and a numerical check of the two conservation laws. | [`gap-profile.json`](results/gap-profile.json) |
| [`run_euler_ladder.py`](run_euler_ladder.py) | Table 8 and Figure 4. The Euler bias of the proxy value at twelve step sizes by transform inversion, compared with the finite sums stored in the certified package, and a coupled simulation of the change in the cost of the kink. | [`euler-ladder.json`](results/euler-ladder.json) |

[`black.py`](black.py) holds the closed forms of Proposition 4.1 and Appendix I, written once for binary64 and for ball arithmetic. [`heston.py`](heston.py) holds the conditional simulation and the transform inversion.

## What is proved and what is estimated

The endpoints in `black-contracts.json` are outward-rounded enclosures: under Black's model with the stated inputs, each price lies in its `price_interval`. Everything under `binary64_diagnostics`, and every number in the other three files, is a floating-point computation or a Monte Carlo estimate with its standard error, seed and sample size. The inversion in `run_euler_ladder.py` reproduces the certified finite sums at 384, 768 and 1536 steps and at the second parameter point to within $`2\cdot10^{-13}`$, and the program stops if the difference exceeds $`10^{-11}`$.

## Run

```sh
python -m pip install -r studies/requirements.txt
python studies/run_black.py --check studies/results/black-contracts.json
python studies/run_euler_ladder.py --check studies/results/euler-ladder.json
```

The two checks recompute the enclosures and the deterministic ladder and compare them with the saved results. To regenerate a result, pass `--output` with a new file name in place of `--check`; the simulations take a few minutes each.

[Paper](../manuscript/report.md) · [Evidence and reproduction](../docs/EVIDENCE.md)
