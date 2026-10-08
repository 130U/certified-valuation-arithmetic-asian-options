# Certified Valuation of Arithmetic Asian Options

Mathematical finance research by **Theodore Ouyang**.

**[English PDF](paper/paper.pdf) · [Read online](manuscript/report.md)**

I derive a weighted payoff remainder through common Gaussian smoothing, then turn it into a computable bound on the pricing error of the original projected Euler scheme. The certificate accounts for variance projection, transform inversion, infinite tails, complex-logarithm branches and outward rounding in one price-unit error budget.

The work combines stochastic analysis with validated computation. Full price-bias certificates are completed at two stochastic Heston parameter points, including three step sizes at the original point. Every reported numerical endpoint is tied to frozen inputs, an exact error ledger and executable checks.

## Main result

For a one-year arithmetic Asian call spread with twelve monthly fixings, strikes 95 and 110, and $`h=1/768`$:

```math
p_h-p_c\in[-0.011024692273,\;0.010642371599],
\qquad |p_h-p_c|\lt0.011025.
```

The parameter order is $`(\kappa,\bar v,\xi,\rho,v_0)`$; the original point is $`(3,.045,.23,-.55,.045)`$, with $`S_0=100`$ and $`r=.01`$. The article gives the continuous-price enclosure and all error contributions.

| Completed result | Mathematical scope |
| --- | --- |
| Signed Heston pricing-error certificates | Original point at $`h=1/384,1/768,1/1536`$; second point $`v_0=.04`$ at $`h=1/768`$ |
| Direct coupled payoff remainder | In a deterministic-variance example, the nonlinear width is about **0.573%** of the separate-law width |
| Joint first-order expansion with explicit remainder bounds | Nine puts and the Asian spread on the deterministic-variance family $`\xi=0`$ |
| Posterior quantile transfer | Restricted continuous prior with $`\xi\in[10^{-7},10^{-6}]`$ and synthetic quotes |

The coupling improvement concerns the nonlinear component of the deterministic example. Each auxiliary result retains the parameter domain stated in the article.

## Verification

[Code and evidence](EVIDENCE.md) · [Current release](https://github.com/130U/certified-valuation-arithmetic-asian-options/releases/tag/paper)

The numerical package preserves the original kernel, exact rational endpoints, execution records and alternative-construction checks. Both constructions use Arb interval arithmetic; their agreement checks implementation consistency within the stated analytical bounds.

<details>
<summary>Run the original Asian certificate</summary>

On Windows x86-64 with CPython 3.12:

```powershell
py -3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install -r code/requirements.txt
./.venv/Scripts/python.exe code/run.py verify
./.venv/Scripts/python.exe code/run.py run --module asian --independent
```

[Second parameter point and coupling](code/revision/round2/README.md) · [Step and posterior-grid experiments](code/revision/README.md)

</details>

## Research timeline

Research began in the second half of 2023. The initial manuscript was written in the first half of 2024. The project was published on GitHub in 2026.

[theodore.oy2025@gmail.com](mailto:theodore.oy2025@gmail.com) · [10@alumni.duke.edu](mailto:10@alumni.duke.edu)

© Theodore Ouyang. All rights reserved.
