# Certified Valuation of Arithmetic Asian Options

**Theodore Ouyang**

[Paper](manuscript/report.md) · [English PDF](paper/paper.pdf) · [Mathematical structure](docs/MATHEMATICAL-STRUCTURE.md) · [Code and evidence](EVIDENCE.md)

How much pricing error does a particular time discretization introduce into a Heston arithmetic Asian valuation? This paper derives a finite, signed bound for the difference between the continuous-model price and the price under positive-part variance Euler with a current-variance log-price update.

The method starts from an **exact conditional price**. Every fixing shares the stock noise accumulated before the first observation, so one Gaussian integral can be evaluated explicitly. The geometric average preserves that common factor and has a logarithm that is linear in the observed log prices. It therefore provides a reference compatible with Heston transforms. Convexity and conditional curvature bound the remaining arithmetic-payoff contribution by a weighted second moment.

The resulting transform catalog follows from the payoff decomposition: 13 complex loadings for the linear term and 91 real loadings for the squared remainder in the twelve-fixing contract. Validated evaluation includes variance projection, inversion, integration tails, complex-logarithm branches and rounding in one price-unit error budget.

For the paper's one-year, twelve-fixing **95–110 Asian call spread**, the complete certificate is

```math
p_h-p_c\in[-0.011024692273,\;0.010642371599],
\qquad |p_h-p_c|\lt0.011025.
```

Here $`p_h`$ is the projected-Euler price and $`p_c`$ the continuous Heston price. The calculation uses $`h=1/768`$, $`S_0=100`$, $`r=.01`$, and $`(\kappa,\bar v,\xi,\rho,v_0)=(3,.045,.23,-.55,.045)`$. The continuous price is enclosed by $`[6.508371733,6.518868974]`$. These are certified bounds for this configuration, not measurements of the actual pricing error.

The analysis also explains a limitation: separate bounds on the two payoff remainders can lose their cancellation, leaving a positive interval width even when the laws coincide. A direct coupling inequality addresses that loss. In a separate **deterministic-variance** example with $`\xi=0`$ and $`v_0=.04`$, it reduces the nonlinear remainder width from approximately **0.01538363715 to 0.00008815020**, a **99.4%** reduction. Those coupled moments have not been certified at the stochastic-variance Heston points. The main fixed-step certificate does not establish a vanishing-width rate.

The work builds on established Asian conditioning and geometric-reference methods, including Fusai–Kyriakou. Its contribution is the weighted kink control and complete error construction for the specified projected kernel. Weak expansions and posterior-quantile transfer are separate applications on explicitly restricted model families.

The [26 October 2026 revision](docs/REVISION-2026-10-26.md) makes the conditional representation, choice of reference and limits of the certificate explicit. The numerical code, results and execution archives retain their original identities.

Research began in the second half of 2023. The initial manuscript was written in the first half of 2024. The project was published on GitHub in 2026.

[theodore.oy2025@gmail.com](mailto:theodore.oy2025@gmail.com) · [10@alumni.duke.edu](mailto:10@alumni.duke.edu)

© Theodore Ouyang. All rights reserved.
