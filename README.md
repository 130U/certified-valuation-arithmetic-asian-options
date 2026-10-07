# Certified Valuation of Arithmetic Asian Options

**Theodore Ouyang**

[English paper](paper/paper.pdf) · [中文论文](paper/paper-zh.pdf) · [Read online](manuscript/report.md) · [中文说明](README-zh.md)

Common Gaussian smoothing gives a weighted payoff remainder. Validated transform calculations combine it with projection, inversion, infinite-tail and rounding errors to bound the price difference between a Heston model and its original projected Euler scheme.

For a one-year arithmetic Asian call spread with twelve monthly fixings, strikes 95 and 110, and $`h=1/768`$:

```math
p_h-p_c\in[-0.011024692273,\;0.010642371599],
\qquad p_c\in[6.508371733,\;6.518868974].
```

The parameter order is $`(\kappa,\bar v,\xi,\rho,v_0)`$; this calculation uses $`(3,.045,.23,-.55,.045)`$, $`S_0=100`$ and $`r=.01`$.

| Result | Scope |
| --- | --- |
| Complete Heston price certificates | Original point at $`h=1/384,1/768,1/1536`$; second point $`v_0=.04`$ at $`h=1/768`$ |
| Joint weak expansion | Nine puts and the Asian spread on the deterministic-variance family $`\xi=0`$ |
| Coupled nonlinear remainder | A completed deterministic-variance example; its width is about **0.573%** of the separate-law width |
| Posterior quantile transfer | Restricted continuous prior with $`\xi\in[10^{-7},10^{-6}]`$ and synthetic quotes |

The coupled calculation concerns the nonlinear component of the deterministic example. A coupled certificate for the stochastic Heston points remains open. The weak expansion and posterior application have the separate domains stated in the paper.

## Reproduction

Use the [`paper` tag](https://github.com/130U/certified-valuation-arithmetic-asian-options/tree/paper) for the complete publication package. On Windows x86-64 with CPython 3.12:

```powershell
py -3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install -r code/requirements.txt
./.venv/Scripts/python.exe code/run.py verify
./.venv/Scripts/python.exe code/run.py run --module asian --independent
```

[Original modules](code/README.md) · [Second point and coupling](code/revision/round2/README.md) · [Grid experiments](code/revision/README.md) · [Evidence inventory](EVIDENCE.md)

The computations use `python-flint==0.8.0` and Arb outward arithmetic. The original kernel and historical evidence archives retain their recorded hashes.

## Manuscript and build

[Editable source](manuscript/report-source.tex) · [Chinese source](manuscript/report-source-zh.tex) · [PDF build instructions](manuscript/FORMAT.md) · [Build and inspection records](paper/build-record.json) · [Response to review](REVIEW-RESPONSE-zh.md)

The delivered PDFs are built with ReportLab and MathJax. The source, fonts, dependencies and build scripts are included. The mathematical formulas have vector outlines and a searchable TeX text layer.

The research and initial writing took place in 2023–2024. The manuscript was prepared and checked for submission in 2026.

[theodore.oy2025@gmail.com](mailto:theodore.oy2025@gmail.com) · [10@alumni.duke.edu](mailto:10@alumni.duke.edu)
