# Certified Valuation of Arithmetic Asian Options

**A mathematical framework that turns Heston discretization error into a complete, auditable price certificate.**

Research by **Theodore Ouyang** · [Paper](manuscript/report.md) · [English PDF](paper/paper.pdf) · [Code and evidence](EVIDENCE.md)

This project derives a weighted payoff remainder, certifies the original positive-part variance Euler implementation, and combines the analytical and numerical contributions into one signed error enclosure. Its central result bounds the discrete-versus-continuous price error by **less than 0.011025 price units** for the specified one-year Heston Asian call spread. A separate deterministic-variance experiment reduces the nonlinear remainder width by **99.4%** through a direct coupling construction.

## Results

| Result | Quantified outcome | Evidence |
| --- | --- | --- |
| Complete Heston price-error certificate | $`p_h-p_c\in[-0.011024692273,\;0.010642371599]`$ at $`h=1/768`$ | [Theorem and numerical certificate](manuscript/report.md#4-the-main-theorem-and-the-complete-price-certificate) |
| Continuous-model price enclosure | $`p_c\in[6.508371733,\;6.518868974]`$ | [Paper](manuscript/report.md), [exact result ledger](code/revision/results/revision-summary.json) |
| Direct coupled remainder | Nonlinear width **0.01538363715 → 0.00008815020**, a **99.4% reduction** in the $`\xi=0`$ example | [Proof](docs/revision-round2/coupling-v004-proof.md), [exact intervals](code/revision/round2/results/coupling-v004-result.json) |
| Step and parameter study | Complete certificates at **three step sizes**; a second stochastic-Heston point at $`v_0=.04`$ | [Step study](manuscript/report.md#82-step-grid-certificates-and-the-width-plateau), [second-point result](code/revision/round2/results/point-v004-result.json) |
| Common weak expansion | First-order formula with explicit remainders for **nine puts and one Asian spread** on the deterministic-variance family | [Theorem and derivation](manuscript/report.md#6-a-common-density-perturbation-and-weak-expansions-for-ten-payoffs) |

The main certificate uses twelve monthly fixings, strikes 95 and 110, $`S_0=100`$, $`r=.01`$, and Heston parameters $`(\kappa,\bar v,\xi,\rho,v_0)=(3,.045,.23,-.55,.045)`$. The step study covers $`h=1/384,1/768,1/1536`$; the second point uses $`h=1/768`$. All reported price enclosures are deterministic and outward rounded.

## Mathematical contributions

**Weighted control of the payoff kink.** A Gaussian factor shared by all observation dates converts the arithmetic payoff into an exact linear-reference decomposition plus a nonnegative remainder. The key quantity is

```math
E\!\left[(A-cG)^2I_1^{-1/2}\right],
```

where $`A`$ and $`G`$ are the arithmetic and geometric averages, and $`I_1`$ is first-period integrated variance. This structure connects the nonsmooth payoff directly to quantities that can be enclosed by validated transforms. [Sections 3–4](manuscript/report.md#3-the-core-argument-from-a-common-gaussian-factor-to-a-weighted-remainder) develop the argument and the price theorem.

**Certification of the actual discrete law.** The proof accounts for the original projected variance update, including the correction between the algebraic transform recursion and the positive-part Euler law. The full budget includes payoff conversion, projection, transform inversion, infinite tails, complex-logarithm branches and arithmetic rounding. Exact rational endpoints connect each contribution to the final signed price interval.

**A sharper coupled construction.** The deterministic example couples both models through the same twelve Gaussian increments and evaluates the mixed moments in closed form. Executions at **384-bit and 512-bit precision**, each with **459 Gaussian-moment identity checks**, establish strict narrowing of the nonlinear remainder. [The execution record](code/revision/round2/results/coupling-v004-result.json) retains the exact width ratio and both precision runs.

The framework builds on established Asian conditioning and Heston transform methods. Its specific research contribution is the weighted remainder and complete error accounting for the stated original discrete kernel. [The literature comparison](manuscript/report.md#11-comparison-with-conditional-asian-bounds) identifies the relationship to Fusai–Kyriakou.

## Inspect and reproduce

Start with the [paper](manuscript/report.md) for the theory and the [evidence index](EVIDENCE.md) for exact ledgers, source identities and execution archives. The [calculation guide](code/README.md) maps the original certificates, weak expansions and posterior-quantile transfer experiment to their commands.

For the original Asian calculation, use **Windows x86-64 and unoptimized CPython 3.12** with the pinned dependency:

```powershell
git clone --branch paper --depth 1 https://github.com/130U/certified-valuation-arithmetic-asian-options.git
cd certified-valuation-arithmetic-asian-options
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r code/requirements.txt
.\.venv\Scripts\python.exe code/run.py verify
.\.venv\Scripts\python.exe code/run.py run --module asian --independent
```

The runner verifies the calculation package and writes fresh interval results with source identities, exact endpoints and execution records. [Environment](code/ENVIRONMENT.md) · [Step-grid calculations](code/revision/README.md) · [Second-point execution](code/revision/round2/README.md)

## Research timeline

Research began in the second half of 2023. The initial manuscript was written in the first half of 2024. The project was published on GitHub in 2026.

[theodore.oy2025@gmail.com](mailto:theodore.oy2025@gmail.com) · [10@alumni.duke.edu](mailto:10@alumni.duke.edu)

© Theodore Ouyang. All rights reserved.
