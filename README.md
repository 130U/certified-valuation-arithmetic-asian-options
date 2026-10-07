# Certified Valuation of Arithmetic Asian Options

**Theodore Ouyang · Mathematical finance**

Targeted revision, **7 October 2026**; original manuscript **2024**.

[Revised PDF](paper/Theodore-Ouyang-Certified-Asian-Valuation-Targeted-Revision-20261007.pdf) · [Editable LaTeX](manuscript/report.tex) · [本轮修稿回应](TARGETED-REVISION-RESPONSE-zh.md) · [New experiment commands and scope](code/revision/round2/README.md).

The targeted revision repairs the PDF reproduction commands and immutable version entries, condenses the main text, completes a second stochastic Heston parameter-point certificate, and executes the coupled-remainder bound on the deterministic-variance face. The step-grid, common-scale and posterior-grid studies remain available. Tight signed Asian coefficient integration, positive-volatility coupled moments, and absolute target-price posterior quantiles remain open.

A theory-led study of a practical pricing question: **how much can a finite-step implementation change the value of an arithmetic Asian option, and how can that change be certified?**

The project connects a common Gaussian factor, a weighted payoff remainder, and validated transform arithmetic to obtain explicit error bounds for a specified Heston model and its projected Euler scheme. The analysis retains the actual arithmetic payoff and accounts for projection, transform inversion, infinite tails, and rounding in one finite calculation.

**[Read the full paper](manuscript/report.md)** · **[Reproduce the certificates](code/README.md)**

## Principal result

For a one-year arithmetic Asian call spread with 12 monthly observations, initial stock price 100, strikes 95 and 110, and Euler step size $`h=1/768`$, the certified price difference is

```math
p_h-p_c\in[-0.011024692273,\;0.010642371599],
\qquad |p_h-p_c|<0.011025.
```

The continuous-model price is enclosed by

```math
p_c\in[6.508371733,\;6.518868974].
```

These are deterministic enclosures in price units at

```math
(\kappa,\bar v,\xi,\rho,v_0)=(3,\;0.045,\;0.23,\;-0.55,\;0.045),\qquad r=0.01.
```

They bound implementation bias at the stated grid, rather than statistical uncertainty from sampled paths. The complete definitions and proof appear in Sections 2–5 and Appendices A–C of the paper.

At the second point, changing only $`v_0`$ to $`0.04`$, all five tasks and both
alternative-construction checks yield

```math
p_h-p_c\in[-0.011798506840,\;0.011383739259].
```

This is another pointwise certificate with the same contract, monthly fixing
schedule, and step size. It does not certify a parameter region. On $`\xi=0`$,
a separate closed-moment coupling example gives a nonlinear interval width at
most **0.000088150195865**, compared with a separate-law width at least
**0.015383637151510** under the same conditioning. These two calculations have
different parameter scopes.

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
| Complete arithmetic Asian certificate | The Heston parameter point above; 12 monthly observations; original positive-part variance Euler and current-variance log-price update; $`h=1/768`$ | Absolute pricing bias below **0.011025** and a continuous-price interval |
| Joint weak expansion | Volatility of volatility $`\xi=0`$; aligned grids; bounded payoffs; a deterministic-variance family with explicit bounds | A common first-order representation and computable second-order remainder; a uniform Asian remainder bound below **0.000165217** on the stated family |
| Uniform small-volatility price control | The positive-volume five-parameter box in equation (7.4) | Asian bias at most **0.020948**; each of nine put biases at most **0.016702** |
| Posterior target quantiles | The three-dimensional continuous prior in equation (7.5), with $`\xi\in[10^{-7},10^{-6}]`$ and the exact synthetic observations in Appendix F | Every quantile shifts by at most **0.006061495591** for the single-quote case or **0.009584682511** for nine quotes at 16384 cells |

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

To reproduce all modules and their independent checks, replace `asian` with `all`. Calculations use `python-flint==0.8.0` and Arb outward arithmetic. The immutable [first revision](https://github.com/130U/certified-valuation-arithmetic-asian-options/tree/cf0d242f1590c7ca07ab8ca7afb57da5a583032b) and [second-point data revision](https://github.com/130U/certified-valuation-arithmetic-asian-options/tree/1959f8f078e1fedd590000d6166cb20429ff31db) provide the additional experiments. See the [new-point commands and replay](code/revision/round2/README.md), [execution guide](code/README.md), [mathematical scope](code/SCOPE.md), and [data description](code/DATA.md).

## Explore the project

| Material | Purpose |
| --- | --- |
| [Full paper](manuscript/report.md) | The structural framework, theorems, proofs, applications, and references |
| [Numerical code](code/) | Deterministic calculations, independent checks, and exact reference results |
| [Validation receipt](code/verification/validation.json) | Recorded execution and reference-comparison outcomes |
| [Manuscript structure](manuscript/FORMAT.md) | Source and structured formats used to reproduce the presentation |

Independent research originating in 2024.

**Contact:** [10@alumni.duke.edu](mailto:10@alumni.duke.edu) · [theodore.oy2025@gmail.com](mailto:theodore.oy2025@gmail.com)
