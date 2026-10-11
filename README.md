# Certified Valuation of Arithmetic Asian Options

**Theodore Ouyang**

[Paper](manuscript/report.md) · [English PDF](paper/paper.pdf) · [Results](code/revision/results/revision-summary.json) · [Code and evidence](EVIDENCE.md)

An arithmetic Asian option depends on the average asset price along a path. Under Heston stochastic volatility, computing that average brings together a nonsmooth payoff, a random variance process and a time-discretized simulation law. The difficult question is how to connect the price produced by a particular implementation to the price defined by the continuous model, with an explicit error in monetary units.

My main contribution is a weighted payoff decomposition that makes this connection possible for the original positive-part variance Euler scheme. I condition on a Gaussian factor shared by every observation date, smooth the payoff kink, and separate a linear reference from a nonnegative remainder. The remainder is controlled by

```math
E\!\left[(A-cG)^2I_1^{-1/2}\right],
```

where $`A`$ and $`G`$ are the arithmetic and geometric averages, and $`I_1`$ is the first observation period's integrated variance. The weight captures how strongly that common Gaussian factor smooths the payoff. It turns the kink into a moment problem that can be handled analytically and enclosed numerically.

I then combine this structure with validated characteristic transforms and a correction for the variance projection used by the actual Euler implementation. Projection, transform inversion, infinite tails, complex-logarithm branches and rounding enter the same price bound. This produces a signed enclosure of the implementation error, with every analytical contribution carried through to the final monetary result.

For a one-year arithmetic Asian call spread with twelve monthly fixings and strikes 95 and 110, the result is

```math
p_h-p_c\in[-0.011024692273,\;0.010642371599],
\qquad |p_h-p_c|\lt0.011025.
```

Here $`p_h`$ is the projected-Euler price and $`p_c`$ the continuous Heston price. The calculation uses $`h=1/768`$, $`S_0=100`$, $`r=.01`$, and $`(\kappa,\bar v,\xi,\rho,v_0)=(3,.045,.23,-.55,.045)`$. The continuous price is enclosed by $`[6.508371733,6.518868974]`$.

A second contribution exploits the relationship between the two model paths directly. In the deterministic-variance example, $`\xi=0`$, I couple their Gaussian increments and derive closed mixed-moment bounds for the difference of the payoff remainders. At $`v_0=.04`$ and the same fixing schedule and step size, the nonlinear remainder width falls from approximately **0.01538363715 to 0.00008815020**, a **99.4% reduction**. The improvement comes from controlling the difference between the models before bounding it, preserving information that separate remainder bounds discard.

The practical consequence is a mathematically justified bridge from a discrete valuation to a continuous-model price interval. A valuation system can combine its discrete-price enclosure with the signed error certificate to assess a monetary accuracy budget. The decomposition also reveals which part of the mathematics determines that budget and where a sharper argument can have the greatest effect.

The research builds on established Asian conditioning and Heston transform methods, including Fusai–Kyriakou. Its specific advance is the weighted kink control and complete price-error construction for the stated projected kernel. The paper also develops common weak expansions and posterior-quantile transfer on their specified model families.

Research began in the second half of 2023. The initial manuscript was written in the first half of 2024. The project was published on GitHub in 2026.

[Coupling proof](docs/revision-round2/coupling-v004-proof.md) · [Coupling result](code/revision/round2/results/coupling-v004-result.json)

[theodore.oy2025@gmail.com](mailto:theodore.oy2025@gmail.com) · [10@alumni.duke.edu](mailto:10@alumni.duke.edu)

© Theodore Ouyang. All rights reserved.
