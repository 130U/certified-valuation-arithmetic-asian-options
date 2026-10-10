# Certified Valuation of Arithmetic Asian Options

Deterministic error bounds in price units for a specified Heston arithmetic Asian call spread and its projected Euler implementation.

[Read the paper](manuscript/report.md) · [English PDF](paper/paper.pdf) · [Code and evidence](EVIDENCE.md)

Research by **Theodore Ouyang**.

Numerical valuation needs both a price and an account of its implementation error. This project derives a weighted payoff remainder from a Gaussian factor shared by the observation dates, then combines it with validated transforms for the original positive-part variance Euler scheme. The resulting certificate encloses the difference between the discrete and continuous model prices.

## A complete price certificate

For a one-year arithmetic Asian call spread with twelve monthly fixings, strikes 95 and 110, and $`h=1/768`$:

```math
p_h-p_c\in[-0.011024692273,\;0.010642371599],
\qquad |p_h-p_c|\lt0.011025.
```

Here $`p_h`$ is the projected-Euler price and $`p_c`$ the continuous Heston price. The parameter order is $`(\kappa,\bar v,\xi,\rho,v_0)`$, with $`(3,.045,.23,-.55,.045)`$, $`S_0=100`$ and $`r=.01`$. The continuous price is enclosed by $`[6.508371733,6.518868974]`$.

These are outward-rounded deterministic enclosures under the paper's analytical bounds and interval-arithmetic assumptions. They concern the stated payoff, parameters and numerical scheme.

## The mathematical contribution

The payoff argument controls the kink remainder through

```math
E\!\left[(A-cG)^2I_1^{-1/2}\right],
```

where $`A`$ and $`G`$ are arithmetic and geometric averages, and $`I_1`$ is first-period integrated variance. The full price budget also includes variance projection, transform inversion, infinite tails, complex-logarithm branches and outward rounding.

The paper builds on established Asian conditioning and Heston transform methods. [Section 1.1](manuscript/report.md#11-comparison-with-conditional-asian-bounds) identifies the comparison with Fusai–Kyriakou; [Sections 3–5](manuscript/report.md#3-the-core-argument-from-a-common-gaussian-factor-to-a-weighted-remainder) give the payoff argument and its application to the original discrete kernel.

| Completed result | Domain and reading path |
| --- | --- |
| Full signed Heston price-error certificates | Original point at $`h=1/384,1/768,1/1536`$; second point $`v_0=.04`$ at $`h=1/768`$. [Step and parameter results](manuscript/report.md#82-step-grid-certificates-and-the-width-plateau). |
| Direct coupled payoff remainder | A deterministic-variance example, $`\xi=0`$, reduces the nonlinear width to about **0.573%** of the separate-law width. [Proof and evidence](docs/revision-round2/README.md). |
| Common first-order expansion with explicit remainders | Nine puts and the Asian spread on the deterministic-variance family. [Section 6](manuscript/report.md#6-a-common-density-perturbation-and-weak-expansions-for-ten-payoffs). |
| Posterior quantile transfer | Restricted continuous prior with $`\xi\in[10^{-7},10^{-6}]`$ and synthetic quotes. [Section 7](manuscript/report.md#7-from-a-reference-family-to-stochastic-volatility-posterior-quantiles). |

Refining the Euler grid alone does not ensure a narrower certificate: payoff conversion dominates the reported widths, and the fixed discrete-tail bound can grow. The coupled improvement applies to the deterministic example's nonlinear component; the required coupled moments for stochastic-variance Heston remain uncomputed. [Mathematical scope](code/SCOPE.md) gives the exact domains.

## Reproduce the original Asian certificate

Use **Windows x86-64, unoptimized CPython 3.12** and the pinned dependency. These commands select the certified [paper release](https://github.com/130U/certified-valuation-arithmetic-asian-options/releases/tag/paper):

```powershell
git clone --branch paper --depth 1 https://github.com/130U/certified-valuation-arithmetic-asian-options.git
cd certified-valuation-arithmetic-asian-options
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r code/requirements.txt
.\.venv\Scripts\python.exe code/run.py verify
.\.venv\Scripts\python.exe code/run.py run --module asian --independent
```

The runner creates a fresh output directory and retains source identities, exact endpoints and execution records. The two numerical constructions share Arb arithmetic and the analytical bounds. Their agreement checks implementation consistency.

[Environment and resource limits](code/ENVIRONMENT.md) · [Other calculations](code/README.md) · [Second point and coupling](code/revision/round2/README.md)

Saved-result checks verify recorded identities and exact ledgers. Fresh execution recomputes finite interval calculations. The mathematical proofs require their own reading.

## Research timeline

Research began in the second half of 2023. The initial manuscript was written in the first half of 2024. The project was published on GitHub in 2026.

[theodore.oy2025@gmail.com](mailto:theodore.oy2025@gmail.com) · [10@alumni.duke.edu](mailto:10@alumni.duke.edu)

© Theodore Ouyang. All rights reserved.

