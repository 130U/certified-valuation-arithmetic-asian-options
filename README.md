# Certified Valuation of Arithmetic Asian Options

**Theodore Ouyang · 2026**

[Paper](manuscript/report.md) · [English PDF](paper/paper.pdf) · [Mathematical structure](docs/MATHEMATICAL-STRUCTURE.md) · [Code and evidence](docs/EVIDENCE.md)

An arithmetic Asian price computed under a projected Euler scheme need not equal the price of the Heston model that was calibrated. For a specified Heston model I bound the difference: a finite, signed interval for the price gap between the continuous model and positive-part variance Euler with a current-variance log-price update.

The method starts from an **exact conditional price**. Every fixing carries the stock noise accumulated before the first observation, so one Gaussian integral can be evaluated explicitly. The geometric average keeps that common factor, and its logarithm is linear in the observed log prices, which makes it a reference that Heston transforms can handle. Convexity and conditional curvature then bound what is left of the arithmetic payoff by a weighted second moment.

The payoff decomposition fixes the transform catalog: for the twelve-fixing contract, 13 complex loadings for the linear term and 91 real loadings for the squared remainder. The validated evaluation puts variance projection, inversion, integration tails, complex-logarithm branches and rounding into one error budget in price units.

For the paper's one-year, twelve-fixing **95–110 Asian call spread**, the complete certificate is

```math
p_h-p_c\in[-0.011024692273,\;0.010642371599],
\qquad |p_h-p_c|\lt0.011025.
```

Here $`p_h`$ is the projected-Euler price and $`p_c`$ the continuous Heston price. The calculation uses $`h=1/768`$, $`S_0=100`$, $`r=.01`$, and $`(\kappa,\bar v,\xi,\rho,v_0)=(3,.045,.23,-.55,.045)`$. The continuous price is enclosed by $`[6.508371733,6.518868974]`$.

A direct coupling argument keeps the cancellation between the two nonlinear remainders. In a separate **deterministic-variance** example with $`\xi=0`$, $`v_0=.04`$, the same fixing dates and $`h=1/768`$, it cuts the nonlinear remainder width from approximately **0.01538363715 to 0.00008815020**, a **99.4%** reduction.

The work builds on established conditioning and geometric-reference methods for Asian options, Fusai–Kyriakou among them. What it adds is the weighted control of the payoff kink and a complete error construction for the specified projected kernel. The weak expansions and the posterior-quantile transfer are separate applications on explicitly restricted model families.

The [computational details](docs/COMPUTATION.md) connect the proof to its finite moment calculations, parameter inputs and exact error ledgers. [Code and evidence](docs/EVIDENCE.md) has the results and the commands that reproduce them.

[theodore.oy2025@gmail.com](mailto:theodore.oy2025@gmail.com) · [10@alumni.duke.edu](mailto:10@alumni.duke.edu)

© Theodore Ouyang. All rights reserved.
