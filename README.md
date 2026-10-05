# Certified Valuation of Arithmetic Asian Options

**Theodore Ouyang · Mathematical finance**

A theory-led study of a practical pricing question: **how much can a finite-step implementation change the value of an arithmetic Asian option, and how can that change be certified?**

The project connects a common Gaussian factor, a weighted payoff remainder, and validated transform arithmetic to obtain explicit error bounds for a specified Heston model and its projected Euler scheme. The analysis retains the actual arithmetic payoff and accounts for projection, transform inversion, infinite tails, and rounding in one finite calculation.

**[Read the full paper](manuscript/report.md)** · **[HTML reading edition](docs/index.html)** · **[Reproduce the certificates](code/README.md)**

## Principal result

For a one-year arithmetic Asian call spread with 12 monthly observations, initial stock price 100, strikes 95 and 110, and Euler step size $h=1/768$, the certified price difference is

$$
p_h-p_c\in[-0.011024692273,\;0.010642371599],
\qquad |p_h-p_c|<0.011025.
$$

The continuous-model price is enclosed by

$$
p_c\in[6.508371733,\;6.518868974].
$$

These are deterministic enclosures in price units at

$$
(\kappa,\bar v,\xi,\rho,v_0)=(3,\;0.045,\;0.23,\;-0.55,\;0.045),\qquad r=0.01.
$$

They bound implementation bias at the stated grid, rather than statistical uncertainty from sampled paths. The complete definitions and proof appear in Sections 2–5 and Appendices A–C of the paper.

## Research contributions

- **A structural route from payoff to certificate.** The paper formulates independently checkable common-factor and finite-verification conditions. A conditional smoothing lemma produces a nonnegative convexity remainder controlled by a weighted second moment and explicit constants.
- **A complete calculation for the specified projected Euler kernel.** Ninety-one real loadings control the nonlinear remainder; thirteen complex loadings recover the linear term. The certificate includes the actual variance projection, infinite integration tails, inversion error, complex branches, and outward rounding.
- **One perturbation for ten payoffs.** On a nonconstant deterministic-variance family, a common Gaussian density perturbation gives a joint first-order weak expansion and an explicit second-order remainder for nine European puts and the arithmetic Asian payoff.
- **Quantile control after calibration.** A posterior coupling retains each model's likelihood normalization and separates direct target error from the change in parameter distribution. It bounds every target quantile on a specified continuous prior with positive volatility of volatility.
- **Executable mathematical evidence.** The numerical package includes principal and independent implementations, exact synthetic inputs, reference payloads, integrity checks, and explicit resource controls.

The contribution is the model-specific proof and effective certificate connecting these components. Conditional Asian pricing, affine transforms, weak-error expansions, and Bayesian approximation provide established foundations; the paper identifies those sources explicitly.

## Where the results apply

| Result | Domain of validity | Quantitative output |
| --- | --- | --- |
| Complete arithmetic Asian certificate | The Heston parameter point above; 12 monthly observations; original positive-part variance Euler and current-variance log-price update; $h=1/768$ | Absolute pricing bias below **0.011025** and a continuous-price interval |
| Joint weak expansion | Volatility of volatility $\xi=0$; aligned grids; bounded payoffs; a deterministic-variance family with explicit bounds | A common first-order representation and computable second-order remainder; a uniform Asian remainder bound below **0.000165217** on the stated family |
| Uniform small-volatility price control | The positive-volume five-parameter box in equation (7.4) | Asian bias at most **0.020948**; each of nine put biases at most **0.016702** |
| Posterior target quantiles | The three-dimensional continuous prior in equation (7.5), with $\xi\in[10^{-7},10^{-6}]$ and the exact synthetic observations in Appendix F | Every quantile shifts by at most **0.008018821658** for the single-quote case or **0.012716404217** for nine quotes |

Each row has its own parameter domain, assumptions, and proof. This makes the result directly checkable for its intended use.

## Applications

**Valuation and implementation control.** A desk or model-validation team can use the signed bias enclosure to convert a certified discrete-model price into a continuous-model enclosure. The absolute bound can be compared with a pricing tolerance or an implementation-risk allowance.

**Error-budget design.** The decomposition shows how payoff conversion, projection, transform inversion, tails, and arithmetic precision contribute to the final bound. It gives a concrete basis for deciding which component to refine when a tighter certified interval is required.

**Calibration and risk reporting.** Changing a pricing implementation changes both the fitted parameter distribution and the exotic target. The posterior theorem quantifies the combined effect on target-price quantiles for the specified prior and observations, providing an implementation-stability check for valuation and risk reports.

These applications concern numerical reliability. The worked calibration examples use exact synthetic observations, and the conclusions do not require a trading-performance claim.

## Reproduce a result

The numerical resource controls use Windows x86-64 and CPython 3.12. From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r code/requirements.txt
.\.venv\Scripts\python.exe code/run.py verify
.\.venv\Scripts\python.exe code/run.py run --module asian --independent
```

To reproduce all modules and their independent checks, replace `asian` with `all`. Calculations use `python-flint==0.8.0` and Arb outward arithmetic. See the [execution guide](code/README.md), [mathematical scope](code/SCOPE.md), and [data description](code/DATA.md).

## Explore the project

| Material | Purpose |
| --- | --- |
| [Full paper](manuscript/report.md) | The structural framework, theorems, proofs, applications, and references |
| [HTML reading edition](docs/index.html) | A self-contained reading layout with vector formulas, a navigable contents panel, and the complete proof appendices; see the [reading guide](docs/README.md) |
| [Numerical code](code/) | Deterministic calculations, independent checks, and exact reference results |
| [Validation receipt](code/verification/validation.json) | Recorded execution and reference-comparison outcomes |
| [Manuscript structure](manuscript/FORMAT.md) | Source and structured formats used to reproduce the presentation |

Independent research originating in 2023.

**Contact:** [10@alumni.duke.edu](mailto:10@alumni.duke.edu) · [theodore.oy2025@gmail.com](mailto:theodore.oy2025@gmail.com)
