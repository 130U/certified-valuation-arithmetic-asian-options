# Certified Valuation of Arithmetic Asian Options

**Theodore Ouyang · 2026**

[Paper](manuscript/report.md) · [English PDF](paper/paper.pdf) · [Mathematical structure](docs/MATHEMATICAL-STRUCTURE.md) · [Code and evidence](EVIDENCE.md)

I develop a mathematical framework for certifying arithmetic Asian valuations under a specified Heston model. The framework gives a finite, signed bound on the price difference between the continuous model and positive-part variance Euler with a current-variance log-price update.

The method starts from an **exact conditional price**. Every fixing shares the stock noise accumulated before the first observation, so one Gaussian integral can be evaluated explicitly. The geometric average preserves that common factor and has a logarithm that is linear in the observed log prices. It therefore provides a reference compatible with Heston transforms. Convexity and conditional curvature bound the remaining arithmetic-payoff contribution by a weighted second moment.

The resulting transform catalog follows from the payoff decomposition: 13 complex loadings for the linear term and 91 real loadings for the squared remainder in the twelve-fixing contract. Validated evaluation includes variance projection, inversion, integration tails, complex-logarithm branches and rounding in one price-unit error budget.

For the paper's one-year, twelve-fixing **95–110 Asian call spread**, the complete certificate is

```math
p_h-p_c\in[-0.011024692273,\;0.010642371599],
\qquad |p_h-p_c|\lt0.011025.
```

Here $`p_h`$ is the projected-Euler price and $`p_c`$ the continuous Heston price. The calculation uses $`h=1/768`$, $`S_0=100`$, $`r=.01`$, and $`(\kappa,\bar v,\xi,\rho,v_0)=(3,.045,.23,-.55,.045)`$. The continuous price is enclosed by $`[6.508371733,6.518868974]`$.

A direct coupling argument preserves cancellation between the two nonlinear remainders. In a separate **deterministic-variance** example with $`\xi=0`$, $`v_0=.04`$, the same fixing dates and $`h=1/768`$, it reduces the nonlinear remainder width from approximately **0.01538363715 to 0.00008815020**, a **99.4%** reduction.

The work builds on established Asian conditioning and geometric-reference methods, including Fusai–Kyriakou. Its contribution is the weighted kink control and complete error construction for the specified projected kernel. Weak expansions and posterior-quantile transfer are separate applications on explicitly restricted model families.

The [computational details](docs/COMPUTATION.md) connect the proof to its finite moment calculations, parameter inputs and exact error ledgers. [Code and evidence](EVIDENCE.md) provide the corresponding results and reproduction commands.

[theodore.oy2025@gmail.com](mailto:theodore.oy2025@gmail.com) · [10@alumni.duke.edu](mailto:10@alumni.duke.edu)

© Theodore Ouyang. All rights reserved.
