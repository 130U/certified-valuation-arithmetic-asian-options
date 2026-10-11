# Certified Valuation of Arithmetic Asian Options

**Theodore Ouyang**

[Paper](manuscript/report.md) · [English PDF](paper/paper.pdf) · [Results](code/revision/results/revision-summary.json) · [Code and evidence](EVIDENCE.md)

I develop a mathematical method for certifying arithmetic Asian valuations through the structure of the payoff. For pricing laws satisfying a common conditional Gaussian structure and explicit moment conditions, I prove a weighted bound on the nonlinear payoff remainder. Combined with validated transform enclosures, this yields a signed bound on the price difference between two models.

I apply the method to the continuous Heston model and its original positive-part variance Euler discretization. The construction accounts for payoff conversion, variance projection, transform inversion, integration tails, complex-logarithm branches and rounding within one monetary error budget. For the paper’s one-year, twelve-fixing **95–110 Asian call spread**, the complete discretization-error bound is below **0.011025 price units**.

A further coupling argument bounds the difference of the two models’ nonlinear remainders directly. In a separate deterministic-variance example, it reduces the remainder width by **99.4%**, demonstrating the value of preserving the relationship between the model laws throughout the error analysis.

The signed certificate for the Heston example is

```math
p_h-p_c\in[-0.011024692273,\;0.010642371599],
\qquad |p_h-p_c|\lt0.011025.
```

Here $`p_h`$ is the projected-Euler price and $`p_c`$ the continuous Heston price. The calculation uses $`h=1/768`$, $`S_0=100`$, $`r=.01`$, and $`(\kappa,\bar v,\xi,\rho,v_0)=(3,.045,.23,-.55,.045)`$. The continuous price is enclosed by $`[6.508371733,6.518868974]`$.

In that separate coupling example, $`\xi=0`$ and $`v_0=.04`$, with the same fixing schedule and step size. The nonlinear remainder width falls from approximately **0.01538363715 to 0.00008815020**.

The research builds on established Asian conditioning and Heston transform methods, including Fusai–Kyriakou. Its specific advance is the weighted kink control and complete price-error construction for the stated projected kernel. The paper also develops common weak expansions and posterior-quantile transfer on their specified model families.

Research began in the second half of 2023. The initial manuscript was written in the first half of 2024. The project was published on GitHub in 2026.

[Coupling proof](docs/revision-round2/coupling-v004-proof.md) · [Coupling result](code/revision/round2/results/coupling-v004-result.json)

[theodore.oy2025@gmail.com](mailto:theodore.oy2025@gmail.com) · [10@alumni.duke.edu](mailto:10@alumni.duke.edu)

© Theodore Ouyang. All rights reserved.
