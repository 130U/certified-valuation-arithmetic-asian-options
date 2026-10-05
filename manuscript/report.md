# Certified Valuation of Arithmetic Asian Options via Common Gaussian Smoothing

Computable Error Bounds for Projected Euler, Joint Weak Expansions, and Posterior Quantile Transfer

**Theodore Ouyang** · Duke University

[10@alumni.duke.edu](mailto:10@alumni.duke.edu) · [theodore.oy2025@gmail.com](mailto:theodore.oy2025@gmail.com)

**Keywords:** Arithmetic Asian options; Heston model; projected Euler; conditional Gaussian smoothing; computable error bounds; weak error expansions; posterior quantiles.

## Abstract

We study the continuous-model valuation of arithmetic Asian payoffs at fixed observation dates, their valuation under a projected Euler scheme, and the numerical difference between the two. We establish a sufficient condition based on a common Gaussian factor and a weighted second moment: we first integrate conditionally over the Gaussian factor shared by all observed prices, and then control the difference between the arithmetic average and a geometric reference through a second-order payoff remainder. This structure reduces the error for a payoff with kinks to finitely many transforms and a nonnegative Laplace integral. For the Heston model and its positive-part variance Euler scheme, all integration tails, discrete projection corrections, complex-logarithm branches, and finite-precision rounding can be included in an explicit error budget. At a specified parameter point, with twelve monthly observation dates and step size $`h=1/768`$, we obtain the rigorous enclosure

```math
[-0.011024692273,\;0.010642371599],
```

for the true Euler-minus-continuous price difference, together with the continuous arithmetic Asian price interval

```math
[6.508371733,\;6.518868974].
```

We further use a single Gaussian density perturbation to establish a joint first-order weak expansion, with an explicit second-order remainder, for nine put payoffs and the arithmetic Asian payoff on a nonconstant deterministic-variance family. Under a three-dimensional continuous prior with strictly positive volatility of volatility, a coupling of parameter posteriors that retains their normalizing constants yields a bound, in price units, on the displacement of every quantile of the posterior distribution of the true Asian price. The contribution is to combine conditional smoothing, error bounds for the original discrete kernel, and finite arithmetic verification into a complete executable certificate, with a specific domain of validity for each conclusion.

## 1. Introduction

Numerical valuation of derivatives involves two distinct questions: computing a model price, and proving how closely the discrete model used in the computation approximates the continuous model. For arithmetic Asian options with fixed observation dates, the positive-part payoff, stochastic variance, and projection of the discrete variance are all present. A practically useful conclusion should provide an error in price units at the specified step size and account for payoff conversion, transform evaluation, infinite tails, and rounding within a single error budget.

We organize the theory around this requirement. We study the risk-neutral Heston model and a precisely specified scheme that applies a positive-part projection to the variance Euler update and uses the current variance in the log-price update. The object of interest is the difference between expectations of the actual arithmetic-average payoff. The method begins at the payoff level: identify a Gaussian random factor shared by all observed prices, integrate it exactly, and use the structure of the remaining variables to bound the error. The key quantity is not a negative moment of the variance at an individual time, but

```math
E\!\left[(A-cG)^2 I^{-1/2}\right],
```

where $`A`$ is the arithmetic average, $`G`$ is the geometric average, and $`I`$ is the integrated variance over the first observation interval.

Conditioning and geometric reference variables have a well-established role in Asian option pricing [[1](#ref-1), [2](#ref-2), [3](#ref-3), [4](#ref-4)]. In particular, the framework of Fusai and Kyriakou covers the Heston model and includes error upper bounds based on conditional variances [[4](#ref-4)]. The affine structure of Heston's model supplies the transform machinery [[5](#ref-5)], while discrete geometric Asian options also admit specialized recursions and publicly available implementations [[6](#ref-6)]. Building on these foundations, we carry out three specific tasks.

First, we formulate a structural condition $`\mathsf H`$ that can be checked independently. Conditional Gaussian smoothing yields a nonnegative convexity remainder with explicit constants; combining this remainder with a certificate for finitely many transforms gives an enclosure of the true price difference. The condition applies both to lognormal models with deterministic variance and to the stochastic-variance model and actual projected Euler kernel verified here.

Second, we account for every computable error contribution for the specified original scheme. The quadratic remainder of the arithmetic payoff is controlled by 91 real loadings and a nonnegative Laplace integral; the linear part is computed from thirteen complex loadings. The result is a complete one-year price certificate at the original parameter point, rather than an asymptotic order with an unknown constant.

Third, we develop two further mathematical applications: a joint weak expansion for ten payoffs on a deterministic-variance reference family, and control of the true target quantiles under a continuous prior with small positive volatility of volatility, using likelihood enclosures over the full parameter cells and a joint posterior coupling. Each application has explicit assumptions and quantitative conclusions.

The logical structure of the paper is

```math
\begin{gathered}
\left.
\begin{array}{l}
\mathsf A:\ \text{deterministic positive integrated variance}\\
\mathsf C:\ \text{verifiable Heston/projected Euler conditions}
\end{array}
\right\}\Longrightarrow\mathsf H,\\[4pt]
\mathsf H\overset{\ \Phi\ }{\Longrightarrow}\mathsf M\Longrightarrow\mathsf B .
\end{gathered}
\tag{1.1}
```

Here $`\Phi`$ denotes conditional Gaussian smoothing and rigorous transform error accounting; $`\mathsf M`$ consists of the payoff decomposition with explicit constants and transform error bounds; and $`\mathsf B`$ is a rigorous enclosure of the actual price difference. Section 2 defines these objects precisely, and Sections 3–5 prove the main chain of implications. Sections 6 and 7 develop the weak expansion and posterior transfer, respectively. Section 8 presents the numerical certificates and their financial use, and Section 9 specifies the domain of validity.

## 2. Models and structural conditions

### 2.1 The continuous model, discrete kernel, and payoff

Let $`W,B`$ be independent standard Brownian motions, and let $`\theta=(\kappa,\bar v,\xi,\rho,v_0)`$. Assume $`S_0,\kappa,\bar v,v_0>0`$, $`\xi\ge0`$, $`|\rho|<1`$, and $`r\in\mathbb R`$. The discrete model uses $`h>0`$, with each $`t_i/h`$ a positive integer. The continuous model is

```math
\begin{aligned}
dV_t&=\kappa(\bar v-V_t)\,dt+\xi\sqrt{V_t}\,dW_t,\\
dZ_t&=(r-V_t/2)\,dt+
\sqrt{V_t}\bigl(\rho\,dW_t+\sqrt{1-\rho^2}\,dB_t\bigr),\\
S_t&=S_0e^{Z_t},\qquad Z_0=0,\quad V_0=v_0.
\end{aligned}
\tag{2.1}
```

On the aligned grid with step size $`h`$, define the original discrete kernel $`Q_h`$ by

```math
\begin{aligned}
V_{j+1}^h&=\left[(1-\kappa h)V_j^h+\kappa\bar v h+
\xi\sqrt{hV_j^h}\,G_j\right]^+,\\
Z_{j+1}^h&=Z_j^h+(r-V_j^h/2)h+
\sqrt{hV_j^h}\bigl(\rho G_j+\sqrt{1-\rho^2}H_j\bigr),
\end{aligned}
\tag{2.2}
```

where $`G_j,H_j`$ are independent standard normal variables, the two updates at the same step share $`G_j`$, and the initial conditions agree. In particular, the price update uses $`V_j^h`$.

Fix $`0<t_1<\cdots<t_n=T`$, and set

```math
\begin{gathered}
A=\frac1n\sum_{i=1}^nS_{t_i},\qquad
G=\left(\prod_{i=1}^nS_{t_i}\right)^{1/n},\qquad
\psi(x)=(x-K_1)^+-(x-K_2)^+,
\end{gathered}
\tag{2.3}
```

where $`0<K_1<K_2`$. Write

```math
\begin{gathered}
p_c=e^{-rT}E_P\psi(A),\qquad
p_h=e^{-rT}E_{Q_h}\psi(A),\qquad e_h=p_h-p_c.
\end{gathered}
\tag{2.4}
```

This sign convention for the error is used throughout. The numerical example uses $`n=12,t_i=i/12,T=1`$, and

```math
\begin{gathered}
S_0=100,\quad r=.01,\quad K_1=95,\quad K_2=110,\quad h=1/768.
\end{gathered}
\tag{2.5}
```

The calibration payoffs are the nine European puts with maturities $`1/4,1/2,1`$ and strikes $`90,100,110`$.

### 2.2 The common Gaussian structure $`\mathsf H_s`$

A pricing law $`\nu`$ is said to satisfy $`\mathsf H_s(c)`$ if there exist a sub-$`\sigma`$-algebra $`\mathcal G`$, positive $`\mathcal G`$-measurable random variables $`a_1,\ldots,a_n,\sigma`$, and a random variable $`U`$ such that

```math
\begin{gathered}
U\mid\mathcal G\sim N(0,\sigma^2),\qquad S_{t_i}=e^Ua_i.
\end{gathered}
\tag{2.6}
```

Set $`a=n^{-1}\sum_i a_i`$ and $`g=(\prod_i a_i)^{1/n}`$. We require

```math
\begin{gathered}
E_\nu(A+G)<\infty,\qquad
D_\nu(c):=E_\nu\!\left[\frac{(A-cG)^2}{\sigma}\right]<\infty.
\end{gathered}
\tag{2.7}
```

Here $`c>0`$ is a constant chosen in advance. Condition (2.6) describes the stochastic structure of the model, while (2.7) is an integrability condition that can be checked through moments or Laplace transforms. Neither condition already contains the price-difference conclusion to be proved.

### 2.3 The finite verification condition $`\mathsf H_v`$

The structural condition must also be connected to finite computation. The condition $`\mathsf H_v`$ used here consists of the following inputs:

1. A computable upper bound for $`D_\nu(c)`$, obtained from enclosures at finitely many Laplace nodes, provable quadrature enclosures, and a bound on the infinite tail.
2. Outward enclosures for the finite set of transform loadings required in Section 3. For the discrete kernel, each loading also has a computable bound on the difference between the true kernel and its algebraic recursion.
3. Complete bounds on the infinite-frequency tail and periodization error in Fourier inversion, together with branch control for the continuous complex transform.

These inputs are defined in terms of specific transforms or moments. Their connection to the target price is established by the theorems below. We write $`\mathsf H=\mathsf H_s+\mathsf H_v`$. The finite catalogs, precision, tail-bound constants, and kernel error formulas are specified in Appendices A–C.

### 2.4 The intermediate property and target conclusion

The property $`\mathsf M`$ has two components: an exact decomposition of the actual payoff into a linear term and a remainder, and signed enclosures for each remainder and each linear-transform error. The target conclusion $`\mathsf B`$ is a definite finite interval $`[\underline e,\overline e]`$ such that

```math
\begin{gathered}
e_h\in[\underline e,\overline e].
\end{gathered}
\tag{2.8}
```

Each endpoint is obtained by finitely many rational operations and validated enclosures of transcendental functions.

## 3. The core argument: from a common Gaussian factor to a weighted remainder

### 3.1 A conditional smoothing lemma

**Lemma 3.1.** Suppose that $`\mathsf H_s(c)`$ holds. For $`K>0`$, define

```math
\begin{gathered}
R_{K,\nu}=E_\nu\!\left[(A-K)^+-(cG-K)^+
-(A-cG)\mathbf1_{\{cG>K\}}\right].
\end{gathered}
\tag{3.1}
```

Then

```math
\begin{gathered}
0\le R_{K,\nu}\le \frac{D_\nu(c)}{2K\sqrt{2\pi}}.
\end{gathered}
\tag{3.2}
```

*Proof.* Convexity of the positive-part function gives pathwise nonnegativity. Conditional on $`\mathcal G`$, let

```math
F_K(x)=E[(xe^U-K)^+\mid\mathcal G],\qquad x>0.
```

Since $`\sigma>0`$, this function is twice differentiable, with

```math
\begin{gathered}
F_K''(x)=\frac{K}{\sigma x^2}
\varphi\!\left(\frac{\log(x/K)}{\sigma}\right)
\le\frac{e^{2\sigma^2}}{K\sigma\sqrt{2\pi}},
\end{gathered}
\tag{3.3}
```

where $`\varphi`$ is the standard normal density. The final bound follows by maximizing at $`\log(x/K)=-2\sigma^2`$.

Applying Taylor's formula with integral remainder between the positive arguments $`a,cg`$ gives

```math
0\le F_K(a)-F_K(cg)-(a-cg)F_K'(cg)
\le \frac{e^{2\sigma^2}(a-cg)^2}{2K\sigma\sqrt{2\pi}}.
```

The conditional derivative satisfies

```math
(a-cg)F_K'(cg)
=E[(A-cG)\mathbf1_{\{cG>K\}}\mid\mathcal G].
```

Since

```math
E[(A-cG)^2\mid\mathcal G]=e^{2\sigma^2}(a-cg)^2,
```

taking expectations proves (3.2). The call and linear terms are integrable because $`E(A+G)<\infty`$. The conditional second-moment identity is used in the sense of nonnegative conditional expectations, and the weighted remainder is controlled by $`D_\nu(c)<\infty`$.  $`\square`$

The crucial point is that the two factors $`e^{2\sigma^2}`$ match exactly. Consequently, the curvature contribution from conditional smoothing can be expressed directly as a weighted second moment under the true model. The residual $`A-cG`$ may have either sign.

### 3.2 The payoff decomposition

Define

```math
\begin{gathered}
\mathcal L=\psi(cG)+(A-cG)\mathbf1_{\{K_1<cG\le K_2\}}.
\end{gathered}
\tag{3.4}
```

The conditional normal variance is strictly positive, so $`G`$ has no atom at any positive threshold. By (3.1),

```math
\begin{gathered}
E_\nu\psi(A)=E_\nu\mathcal L+R_{K_1,\nu}-R_{K_2,\nu}.
\end{gathered}
\tag{3.5}
```

This identity retains the original arithmetic payoff as the object of interest, while producing a linear part that can be computed using a small number of transforms.

Let $`Y=\log(G/S_0)`$ and $`y_K=\log(K/(cS_0))`$, and define the distribution functions of two positive measures by

```math
F_{0,\nu}(y)=\nu(Y\le y),\qquad
F_{A,\nu}(y)=E_\nu[A\mathbf1_{\{Y\le y\}}].
```

Expanding (3.4) on each of its intervals gives

```math
\begin{gathered}
E_\nu\mathcal L=(K_2-K_1)
+K_1F_{0,\nu}(y_{K_1})-K_2F_{0,\nu}(y_{K_2})
-F_{A,\nu}(y_{K_1})+F_{A,\nu}(y_{K_2}).
\end{gathered}
\tag{3.6}
```

The corresponding transforms are

```math
\begin{gathered}
\widehat\mu_0(z)=E_\nu e^{zY},\qquad
\widehat\mu_A(z)=\frac{S_0}{n}\sum_{i=1}^n
E_\nu e^{Z_{t_i}+zY}.
\end{gathered}
\tag{3.7}
```

Thus the linear part requires thirteen loadings when $`n=12`$.

## 4. The main theorem and the complete price certificate

**Theorem 4.1 (A signed enclosure of the price difference between two models).** Suppose that $`P,Q_h`$ each satisfy $`\mathsf H_s(c)`$, and that computable constants satisfy $`D_P(c)\le d_P,D_Q(c)\le d_Q`$. If $`\mathsf H_v`$ provides

```math
\begin{gathered}
e^{-rT}(E_Q\mathcal L-E_P\mathcal L)\in[\ell,u],
\end{gathered}
\tag{4.1}
```

then, with $`\gamma=e^{-rT}/(2\sqrt{2\pi})`$,

```math
\begin{gathered}
\boxed{
e_h\in
\left[
\ell-\gamma\!\left(\frac{d_Q}{K_2}+\frac{d_P}{K_1}\right),
\quad
u+\gamma\!\left(\frac{d_Q}{K_1}+\frac{d_P}{K_2}\right)
\right].}
\end{gathered}
\tag{4.2}
```

*Proof.* Apply (3.5) to each law and subtract. The lower-end contributions are $`-R_{K_2,Q}-R_{K_1,P}`$, and the upper-end contributions are $`R_{K_1,Q}+R_{K_2,P}`$. Lemma 3.1 and (4.1) give the result.  $`\square`$

The final step of the main theorem consists only of combining intervals. Its mathematical substance lies in Lemma 3.1 and the rigorous verification of $`\mathsf H_v`$. The resulting interval is generally not symmetric about zero, and its center is retained in the computation.

**Corollary 4.2 (The specified Heston parameter point).** For (2.1)–(2.5), take

```math
\begin{gathered}
\theta_*=(3,\;9/200,\;23/100,\;-11/20,\;9/200),\qquad
c=\frac{1254433}{1250000}.
\end{gathered}
\tag{4.3}
```

Then

```math
\begin{gathered}
e_h\in[-.011024692273,\;.010642371599],\qquad |e_h|<.011025<.025.
\end{gathered}
\tag{4.4}
```

Furthermore,

```math
\begin{aligned}
p_c&\in[6.508371733,\;6.518868974],\\
p_h&\in[6.507844281,\;6.519014106].
\end{aligned}
\tag{4.5}
```

*Proof.* Section 5 establishes the common Gaussian structure. Appendices A–C specify all requirements for the validated arithmetic computation, which yields

```math
\begin{gathered}
W_P:=E_P[(A-cG)^2I^{-1/2}]\le2.172471592802,\qquad
W_Q\le2.242189951600.
\end{gathered}
\tag{4.6}
```

Here $`d_\nu=W_\nu/\sqrt{1-\rho^2}`$. The center of the finite linear difference is approximately $`-.000202992309237006`$, and its complete error radius is at most $`.000594238060`$. Combining the exact rational endpoints outward with (4.2) gives (4.4). Applying the corresponding error contributions to (3.5) separately for each law gives (4.5). The source code, exact endpoints, and the recomputation of the entire catalog by a second implementation together constitute the executable evidence specified in the appendices.  $`\square`$

## 5. Recovery of classical conditions and additional models covered

### 5.1 Deterministic positive integrated variance: $`\mathsf A\Rightarrow\mathsf H`$

Define $`\mathsf A`$ as follows: the model's variance coefficient itself is a deterministic function $`v(t)\ge0`$, the stock price follows the corresponding linear geometric diffusion, and

```math
\begin{gathered}
0<I_1=\int_0^{t_1}v(t)\,dt,\qquad \int_0^T v(t)\,dt<\infty.
\end{gathered}
\tag{5.1}
```

Computability conclusions additionally require these integrals to be supplied as effectively computable inputs.

Take the stock Brownian integral over the first interval as $`U`$. Then $`\sigma^2=I_1`$ is a positive constant; the remaining log increments and deterministic drift can all be included in $`\mathcal G`$. Every observed price has the common factor in (2.6). The finite positive moments of the joint lognormal distribution give

```math
D_\nu(c)=I_1^{-1/2}E_\nu(A-cG)^2<\infty.
```

The second moment is computed directly from

```math
\begin{gathered}
E(A-cG)^2=\frac1{n^2}\sum_{i,j}ES_iS_j
-\frac{2c}{n}\sum_iES_iG+c^2EG^2
\end{gathered}
\tag{5.2}
```

whose terms are all Gaussian exponential moments. The corresponding finite transforms and Gaussian tails likewise have explicit bounds. Thus, for a single law with effectively computable inputs, $`\mathsf A\Rightarrow\mathsf H`$; for two such laws, Theorem 4.1 further yields $`\mathsf B`$.

This shows that classical lognormal conditioning models fit within the framework. Identifying the common structure allows the same payoff-level argument to apply to different variance mechanisms; the model itself supplies the particular constants and computational catalog.

### 5.2 Heston and the actual projected kernel: $`\mathsf C\Rightarrow\mathsf H`$

Condition $`\mathsf C`$ requires $`\kappa,\bar v,\xi,v_0>0`$, $`|\rho|<1`$, the model (2.1) or (2.2), observation dates aligned with the discrete grid, and the finite-transform, moment-growth, projection, and infinite-tail inequalities listed in Appendices A–C. The actual verification in this section uses $`S_0,r,T,h`$ from (2.5) and the parameters in (4.3); the common Gaussian construction below is valid under the structural parameter assumptions just stated.

Condition on the entire variance driver $`W`$ and on the independent stock driver $`B`$ outside the first interval. Let

```math
I_P=\int_0^{t_1}V_t\,dt,\qquad
I_Q=h\sum_{j=0}^{t_1/h-1}V_j^h.
```

The contribution of $`B`$ over the first interval is shared by every observation date. Hence

```math
\begin{gathered}
U\mid\mathcal G\sim N(0,(1-\rho^2)I_\nu),\qquad S_{t_i}=e^Ua_i.
\end{gathered}
\tag{5.3}
```

For the continuous model, $`v_0>0`$ and continuity of the variance paths imply $`I_P>0`$ almost surely. For the discrete model, there is the exact lower bound

```math
\begin{gathered}
I_Q\ge hv_0>0.
\end{gathered}
\tag{5.4}
```

The transform and tail bounds in the appendices verify $`W_\nu<\infty`$ and supply an upper bound, while the exponential-moment growth bounds ensure integrability of the required price terms. Therefore $`\mathsf C\Rightarrow\mathsf H`$. At the parameters in (4.3), all these inequalities and finite-node checks hold.

### 5.3 A strict extension of the class of models covered

Let $`X_*`$ be the continuous/discrete model pair at (4.3). For the continuous model,

```math
\begin{gathered}
\operatorname{Var}(V_t)=\xi^2\int_0^t e^{-2\kappa(t-s)}EV_s\,ds>0
\quad(t>0),
\end{gathered}
\tag{5.5}
```

so its variance is not a deterministic function. The first step of the discrete model also satisfies

```math
\begin{gathered}
Q_h(V_1^h=0)=
\Phi\!\left(
-\frac{(1-\kappa h)v_0+\kappa\bar v h}{\xi\sqrt{hv_0}}
\right)\in(0,1).
\end{gathered}
\tag{5.6}
```

At the same time, (5.4) still holds. Thus $`X_*`$ satisfies $`\mathsf C`$ but not $`\mathsf A`$, and the main theorem yields (4.4). The additional model pair has both stochastic variance and a boundary atom induced by projection, while the common Gaussian structure at the payoff level remains valid.

## 6. A common density perturbation and weak expansions for ten payoffs

For background on weak error expansions and distributional error analysis, see [[7](#ref-7), [8](#ref-8), [9](#ref-9)]. This section works directly with the differentiability of Gaussian densities. We set $`\xi=0`$, retain the original update (2.2), and assume

```math
\begin{gathered}
\kappa>0,\quad \bar v,v_0>0,\quad
t_j=j/12,\quad h=1/(12m)\le h_0<1/\kappa,\quad m\in\mathbb N.
\end{gathered}
\tag{6.1}
```

Let $`D=v_0-\bar v`$. The continuous and discrete cumulative variances are

```math
\begin{gathered}
I(t)=\bar vt+\frac D\kappa(1-e^{-\kappa t}),\qquad
I_h(t)=\bar vt+\frac D\kappa[1-(1-\kappa h)^{t/h}].
\end{gathered}
\tag{6.2}
```

The twelve independent components of the log-increment vector $`Y`$ have distributions

```math
\begin{gathered}
N(r/12-s_j/2,s_j),\qquad s_j=I(t_j)-I(t_{j-1}),
\end{gathered}
\tag{6.3}
```

and the discrete law replaces $`s_j`$ by $`s_{h,j}`$. Both satisfy the lower bound $`s_j,s_{h,j}\ge u_*:=\min(v_0,\bar v)/12>0`$.

Define

```math
\begin{gathered}
a(t)=\frac{D\kappa t e^{-\kappa t}}2,
\quad
B_I(t)=|D|e^{-\kappa t}
\left[
\frac{\kappa^2t}{3(1-\kappa h_0)}
+\frac{\kappa^3t^2}{8(1-\kappa h_0)^2}
\right].
\end{gathered}
\tag{6.4}
```

Set $`d_j=a(t_j)-a(t_{j-1})`$ and $`b_j=B_I(t_j)+B_I(t_{j-1})`$. Appendix D proves that

```math
\begin{gathered}
|s_{h,j}-s_j-hd_j|\le h^2b_j.
\end{gathered}
\tag{6.5}
```

**Theorem 6.1 (A common first-order expansion for bounded payoffs).** Under (6.1), let $`g(Y)`$ be any bounded Borel payoff with range contained in $`[l,l+L]`$, payable at time $`\tau`$. Then

```math
\begin{gathered}
p_h(g)-p_c(g)=h\beta_g+R_h(g),
\end{gathered}
\tag{6.6}
```

```math
\begin{aligned}
\beta_g&=e^{-r\tau}E_s\!\left[g(Y)\sum_jd_j\mathcal S_j(Y)\right],\\
|R_h(g)|&\le e^{-r\tau}\frac L2\,C_2h^2,
\end{aligned}
\tag{6.7}
```

where

```math
\mathcal S_j=\frac{G_j^2-1}{2s_j}-\frac{G_j}{2\sqrt{s_j}},
\quad
J(s)=\frac1{2s^2}+\frac1{4s},\quad
H_2(s)=\frac2{s^2}+\frac1{2s},
```

```math
\begin{gathered}
C_2=
\sqrt{\sum_jb_j^2J(u_*)}
+\frac12\sum_j(|d_j|+h_0b_j)^2H_2(u_*).
\end{gathered}
\tag{6.8}
```

Here $`G_j`$ denotes the standardized independent normal increments.

*Proof.* The Gaussian density is twice differentiable in $`L^1`$ with respect to its variance parameters. The norm of its first directional derivative is bounded by the corresponding square root of the Fisher information quadratic form, while its second directional derivative satisfies

```math
\|Dp_s[z]\|_1\le\sqrt{\sum_jz_j^2J(s_j)},\qquad
\|D^2p_s[z,z]\|_1\le\sum_jz_j^2H_2(s_j).
```

Substituting (6.5) into the $`L^1`$ Taylor formula for the density gives $`\|p_{s_h}-p_s-hDp_s[d]\|_1\le C_2h^2`$. The density remainder integrates to zero, so the payoff can be centered as $`g-l-L/2`$, yielding (6.7). Appendix D gives the derivative calculations and the full justification by dominated convergence.  $`\square`$

The theorem applies the same leading density perturbation to all ten payoffs. For a put,

```math
\begin{gathered}
\beta_{K,\tau}
=a(\tau)\frac{S_0\varphi(d_1)}{2\sqrt{I(\tau)}},
\quad
d_1=\frac{\log(S_0/K)+r\tau+I(\tau)/2}{\sqrt{I(\tau)}}.
\end{gathered}
\tag{6.9}
```

When $`v_0\ne\bar v`$, all nine put components are nonzero and have the same sign as $`v_0-\bar v`$.

On the family

```math
\begin{gathered}
\kappa=3,\quad\bar v=.045,\quad v_0\in[.03,.06],\quad h_0=1/768,
\end{gathered}
\tag{6.10}
```

the second-order remainder for the original Asian payoff has the uniform upper bound $`.000165217`$. A separate finite-step density comparison also gives

```math
\begin{gathered}
|p_h(\psi)-p_c(\psi)|\le .004990924.
\end{gathered}
\tag{6.11}
```

The leading Asian coefficient has the exact integral representation (6.7) and an effective absolute bound. This common expansion treats several nonsmooth payoffs through one integrable density perturbation, with every remainder constant retained explicitly.

## 7. From a reference family to stochastic-volatility posterior quantiles

### 7.1 Price transfer for small positive volatility of volatility

Suppose that the deterministic reference variance and its Euler values lie in $`[m,M]`$, where $`0<m\le M<\infty`$ and $`\kappa\ge\kappa_->0`$, and assume

```math
\begin{gathered}
\kappa h\le1,\qquad
0\le\xi\le\sqrt{\kappa_-M/2}.
\end{gathered}
\tag{7.1}
```

Define

```math
C_P=\sqrt{M/(2\kappa_-)},\qquad C_Q=\sqrt{2M/\kappa_-}.
```

The Itô isometry for the continuous model and the 1-Lipschitz property of the discrete positive-part projection give, respectively,

```math
\begin{gathered}
E(V_t^\xi-v(t))^2\le\xi^2C_P^2,\qquad
E(V_j^{\xi,h}-v_j)^2\le\xi^2C_Q^2.
\end{gathered}
\tag{7.2}
```

Combining the deterministic reference lower bound $`m`$ with Doob's inequality yields

```math
\begin{gathered}
E\max|Z_\nu^\xi-Z_\nu^0|
\le\xi C_\nu\left(\frac T2+2\sqrt{T/m}\right),\quad \nu=P,Q.
\end{gathered}
\tag{7.3}
```

The original put payoff is $`K`$-Lipschitz in log stock price; the original spread payoff is $`K_2=110`$-Lipschitz in the maximum norm of the fixing log-price vector. Thus (7.3) provides uniform radii from all true calibration prices and the true target price to their reference-family counterparts. Appendix E gives the inductive proof, retaining the effect of projection on the mean.

For example, on the parameter box of positive five-dimensional volume

```math
\begin{gathered}
\kappa\in[2.999,3.001],\quad\bar v\in[.04499,.04501],\\
v_0\in[.03001,.05999],\quad \xi\in[10^{-5},4\cdot10^{-5}],
\quad\rho\in[-.8,-.3],
\end{gathered}
\tag{7.4}
```

finite verification gives an absolute bias bound of $`.020948`$ for the original Asian and $`.016702`$ for each of the nine puts.

### 7.2 The full joint posterior

The effect of forward numerical error on the likelihood and its normalizing constant is a basic issue in Bayesian approximation [[10](#ref-10)]. In this section, set $`\kappa=3,\bar v=.045`$, and let

```math
\begin{gathered}
u=v_0\sim U[.03,.06],\quad
\xi\sim U[10^{-7},10^{-6}],\quad
\rho\sim U[-.8,-.3]
\end{gathered}
\tag{7.5}
```

be mutually independent. Write $`\zeta=(\xi,\rho)`$ and denote its prior probability measure by $`\nu`$. For model $`m=P,Q`$, let $`c_m(u,\zeta)`$ be the true calibration vector and $`J_m(u,\zeta)`$ the true Asian price. Given synthetic quotes $`y`$ and a positive-definite covariance matrix $`\Sigma_d`$, define

```math
w_m(u,\zeta)=
\exp\!\left[-\frac12(c_m-y)^T\Sigma_d^{-1}(c_m-y)\right],
\quad \bar w_m(u)=\int w_m(u,\zeta)\nu(d\zeta),
```

```math
\begin{gathered}
Z_m=\frac1{.03}\int_{.03}^{.06}\bar w_m(u)\,du,\qquad
\mu_m(du,d\zeta)=\frac{w_m(u,\zeta)}{.03Z_m}\,du\,\nu(d\zeta).
\end{gathered}
\tag{7.6}
```

Each model uses its own calibration prices, normalizing constant, and target price.

### 7.3 A transfer theorem for every quantile level

**Theorem 7.1.** Suppose that the two marginal posteriors of $`u`$ admit a coupling $`(U_P,U_Q)`$ such that $`|U_P-U_Q|\le\delta_u`$ almost surely. Assume that the reference targets satisfy

```math
|J_P^0(u)-J_P^0(v)|\le L_0|u-v|,
\quad
|J_Q^0(u)-J_P^0(u)|\le\varepsilon_0,
```

and that the true targets satisfy $`|J_m(u,\zeta)-J_m^0(u)|\le e_{m,J}`$. Then the left generalized quantiles of the true targets under their respective full joint posteriors satisfy

```math
\begin{gathered}
\boxed{\quad
|q_Q(p)-q_P(p)|
\le \varepsilon_0+e_{P,J}+e_{Q,J}+L_0\delta_u
\quad(0<p<1).\quad}
\end{gathered}
\tag{7.7}
```

*Proof.* For each model, define the conditional probability kernel

```math
K_m(u,d\zeta)=\frac{w_m(u,\zeta)}{\bar w_m(u)}\nu(d\zeta).
```

Extend the marginal coupling above by drawing $`\zeta_P`$ and $`\zeta_Q`$ from $`K_P(U_P,\cdot)`$ and $`K_Q(U_Q,\cdot)`$, respectively. Fubini's theorem shows that the resulting full marginals are exactly $`\mu_P`$ and $`\mu_Q`$. The triangle inequality gives

```math
|J_Q(U_Q,\zeta_Q)-J_P(U_P,\zeta_P)|
\le\varepsilon_0+e_{P,J}+e_{Q,J}+L_0\delta_u=:E.
```

Consequently, $`F_P(z-E)\le F_Q(z)\le F_P(z+E)`$. Taking left generalized inverses yields (7.7). The argument also applies to target distributions with atoms.  $`\square`$

### 7.4 Effective inputs and numerical conclusions

Partition $`[.03,.06]`$ into 4096 equal intervals. On each interval and over the entire $`\zeta`$-domain, enclose the true likelihood using (7.3) and the reference Black prices. The same bounds remain valid after integration against the normalized prior $`\nu`$. Construct enclosures of the marginal CDFs while retaining their shared denominators; an inverse-CDF coupling driven by a common uniform variable then gives $`\delta_u`$. All constants and the finite pairing algorithm are given in Appendix F.

The single-quote case uses the put with $`T=1,K=100`$, and the nine-quote case uses the full calibration vector. Both use $`\Sigma_d=.75^2(.75I_d+.25\mathbf1\mathbf1^T)`$. The exact quotes are listed in Appendix F. The results are

```math
L_0\le213.792201829985,\quad
\varepsilon_0\le.004493504474,\quad
e_{P,J}+e_{Q,J}\le.000393595478,
```

```math
\begin{array}{c|c|c}
\text{Case}&\delta_u&\sup_{0<p<1}|q_Q(p)-q_P(p)|\\ \hline
\text{Single quote}&3/204800&\le.008018821658\\
\text{Nine quotes}&3/81920&\le.012716404217
\end{array}
\tag{7.8}
```

The finite partition encloses the continuous posterior and retains the full normalizing mass of each model.

## 8. Numerical certificates, computational scale, and financial uses

### 8.1 From formulas to certified monetary bounds

The complete price difference at the original parameter point is assembled from the terms below. All displayed numbers are rounded outward; exact rational endpoints are stored in the reference results distributed with the accompanying code.

| Quantity | Validated upper bound or enclosure |
| --- | --- |
| Nonlinear conversion interval | $`[-.010227461904,.010251125849]`$ |
| Q projection error per linear profile | $`.000000012711979137`$ |
| Q projection contribution over all linear profiles | $`.000004310413`$ |
| Omitted frequency tail for the continuous model | $`.000014095712`$ |
| Omitted frequency tail for the discrete model | $`.000184373301`$ |
| Periodization error for one model | $`.000195729318`$ |
| Total error bound for the linear difference between the two models | $`.000594238060`$ |
| **Absolute bound on the true arithmetic Asian bias** | $`\boldsymbol{.011025}`$ |

The nonlinear-moment module evaluates 24,388 continuous real-flow blocks and 815,360 discrete real-recursion steps. The linear module evaluates 641 frequencies and thirteen profiles, for a total of 6,399,744 discrete steps and 799,968 continuous branch checks. The author's implementation uses 256-bit Arb; each of the two modules was recomputed in full using a second implementation at 384-bit precision. The TT and posterior modules were also checked by finite recomputations using different implementation paths.

These are deterministic calculations, with outward arithmetic supplied by Arb [[11](#ref-11)]. Measured worker times for the two author modules at the original point were approximately 12.02 and 33.20 seconds, respectively, using one thread and a hard memory limit of 256 MiB per process. These timings describe the scale of this specific computation; the code explicitly records operation counts, memory constraints, and stopping conditions. Appendix G describes the environment and reproduction entry point.

### 8.2 Continuous-model valuation and numerical risk budgets

Suppose that a valuation system provides a price enclosure $`[q_L,q_U]`$ for the same discrete model. Theorem 4.1 gives $`e_h\in[\ell,u]`$, hence the continuous-model price satisfies

```math
\begin{gathered}
p_c\in[q_L-u,\ q_U-\ell].
\end{gathered}
\tag{8.1}
```

This is a directly usable transfer rule: a trading system can allocate separate budgets to simulation error, discretization bias, and other valuation errors, and check whether their sum meets a monetary tolerance.

For the contract instance (4.3), we also obtain the continuous-price enclosure (4.5) directly, with width less than $`.010498`$. A valuation audit can therefore use the full price interval or attach the signed bias certificate to an existing Euler computation.

### 8.3 Stability of the price distribution after calibration

A change in numerical implementation affects both the calibration likelihood and the target price. Theorem 7.1 retains both effects: $`\varepsilon_0+e_{P,J}+e_{Q,J}`$ controls the target-price difference at fixed parameters, and $`L_0\delta_u`$ controls the target change caused by movement of the parameter posterior.

For the prior (7.5) and the specified quotes, the displacement of any Asian posterior quantile is at most approximately $`.00802`$ in the single-quote case and $`.01272`$ in the nine-quote case. If an application sets a numerical tolerance of $`.10`$ for endpoint displacement, these certificates support acceptance at the implementation level. The use case is a stability check for numerical valuation and risk reporting after calibration, with both the quantity being checked and its admissible error specified explicitly.

## 9. Domain of validity

The main theorem provides sufficient conditions through the common Gaussian structure and finite verification inputs. Its scope consists of model classes for which those inputs can be established. Section 5 verifies a deterministic-variance class and the specified stochastic-variance model and projected kernel. Comparisons with other Asian bounds depend on their respective hypotheses and numerical inputs.

The complete small-error Heston Asian certificate applies to the specified $`\theta_*`$, step size, and fixing dates. A uniform certificate on a parameter neighborhood or an entire domain requires uniform moment, transform, projection, and tail inequalities. The five-dimensional box with small positive $`\xi`$ in Section 7 is a separately certified region of positive volume, with a volatility-of-volatility range distinct from that of $`\theta_*`$.

The ten-payoff expansion holds on the deterministic-variance family $`\xi=0`$. A corresponding expansion for positive $`\xi`$ would require higher-order regularity and integrable remainders for the combined effects of the projection kernel and the payoff kinks. For the Asian leading coefficient, the established conclusion consists of an exact score representation and an effective absolute bound. High-precision scalar evaluation and nonvanishing of that component are separate assertions. When $`v_0\ne\bar v`$, the nine put components establish nonvanishing of the ten-dimensional leading coefficient vector. The vector result expresses the common density construction; each component retains its stated scalar error budget.

The posterior quantile-displacement certificates use the three-dimensional prior (7.5) and the synthetic quotes in Appendix F. They compare two true target distributions at every quantile level. Determination of the absolute locations of specified quantiles is a separate valuation task. A quantile-displacement certificate on the five-dimensional parameter domain

```math
[2,4]\times[.03,.06]\times[.18,.28]\times[-.8,-.3]\times[.03,.06]
```

requires forward-error and posterior-transport inputs valid throughout that domain. The synthetic-quote application establishes the stated mathematical transfer under its specified inputs. Use with market quotes additionally calls for empirical assessment of quote quality, model fit, transaction costs, and strategy performance.

Conditioning, geometric-average reference variables, Fourier bounds, Gaussian scores, and posterior approximation have established literatures [[1](#ref-1), [2](#ref-2), [3](#ref-3), [4](#ref-4), [12](#ref-12), [7](#ref-7), [8](#ref-8), [10](#ref-10)]. The contribution here is their effective combination for the specified kernel, the payoff-level argument weighted by first-period integrated variance, the complete finite error budget, and the resulting model-specific quantitative certificates. Numerical validity uses the enclosure semantics of the stated interval-arithmetic library. The accompanying independent implementations provide reproducible comparisons of the finite arithmetic inputs and bounds.

## 10. Conclusion

The common Gaussian structure connects classical lognormal conditioning with stochastic-variance models discretized by projected Euler. The central lemma converts the kink remainder of the original arithmetic payoff into a second moment weighted by the inverse square root of integrated variance. The main theorem combines this quantity with a finite transform certificate to produce a signed price-difference enclosure. The specified Heston instance gives the complete monetary bound $`.011025`$, together with a validated interval for the continuous-model price.

The common density expansion and the full posterior coupling further illustrate this approach: state the structural assumptions explicitly and convert each transfer step into computable constants, so that the conclusions can be executed, checked, and used within a stated scope. The three results address fixed-step valuation, weak expansions for nonsmooth payoffs, and posterior quantile stability after calibration, respectively. Together, they form a collection of numerical-finance certificates with explicit mathematical interfaces.

## Appendix A. Finite certification of the weighted second moment

This appendix and Appendices B and C use the rational parameters in (4.3). Write

```math
\alpha=\xi^2/2,\quad d=\kappa\bar v,\quad
s=1-\rho^2,\quad t_1=1/12.
```

Throughout, $`c`$ denotes the geometric scaling coefficient in (4.3).

### A.1 A nonnegative integral and the loading catalog

For $`I>0`$,

```math
I^{-1/2}=\frac2{\sqrt\pi}\int_0^\infty e^{-x^2I}\,dx.
```

Applying Tonelli's theorem to the nonnegative square gives

```math
\begin{gathered}
W_\nu=\frac2{\sqrt\pi}\int_0^\infty F_\nu(x)\,dx,\qquad
F_\nu(x)=E_\nu[(A-cG)^2e^{-x^2I}].
\end{gathered}
\tag{A.1}
```

We have $`F_\nu\ge0`$, and the function is nonincreasing. In the expansion (5.2), the 144 ordered terms in $`A^2`$ combine into 78 terms; there are also 12 terms of the form $`S_iG`$ and one $`G^2`$ term. Each normalized exponential profile has total real stock loading 2, and the remaining loading in the backward monthly recursion satisfies $`p\in[0,2]`$. The sum of the absolute coefficients of the 91 terms is

```math
\begin{gathered}
S_0^2(1+c)^2=10000(1+c)^2.
\end{gathered}
\tag{A.2}
```

A killing rate $`x^2`$ is imposed in the first month and is zero in all other months.

### A.2 The true continuous flow and the discrete algebraic recursion

On an interval with stock loading $`q`$ and killing rate $`\lambda`$, write the normalized transform as $`\exp(\mathcal A+\mathcal Bv)`$. The continuous coefficients satisfy

```math
\begin{gathered}
\mathcal B'=\alpha\mathcal B^2-(\kappa-\rho\xi q)\mathcal B+
(q^2-q)/2-\lambda,\qquad
\mathcal A'=rq+d\mathcal B.
\end{gathered}
\tag{A.3}
```

Completing the square in the one-step Gaussian integral gives the discrete algebraic recursion

```math
\begin{aligned}
\mathcal A_j&=\mathcal A_f+h(rq+d\mathcal B_f),\\
\mathcal B_j&=\mathcal B_f+h\left[
\alpha\mathcal B_f^2-(\kappa-\rho\xi q)\mathcal B_f+
(q^2-q)/2-\lambda\right].
\end{aligned}
\tag{A.4}
```

Both updates use the value $`\mathcal B_f`$ before the update. Appendix B bounds the difference between the actual positive-part kernel and (A.4). Fixed observation dates are handled by adding the corresponding stock loadings in reverse chronological order.

For real loadings $`p\in[0,2]`$ and $`\lambda\ge0`$, the continuous vector field is strictly downward at $`\mathcal B=1`$. Thus the backward flow from terminal value 0 satisfies $`\mathcal B\le1`$, and $`\mathcal A\le(2r+d)T`$. The uniform integrability established in Appendix B.3 identifies this flow with the true transform.

### A.3 Validated Darboux enclosures

Take $`\Delta x=1/2`$. For the continuous model, use nodes $`x_j=j/2,\ 0\le j\le256`$; for the discrete model, use $`0\le j\le128`$. If the true nodal value lies in $`[f_j^-,f_j^+]`$, then

```math
\begin{gathered}
\Delta x\sum_{j=1}^{M}\max(0,f_j^-)
\le\int_0^{M\Delta x}F_\nu(x)\,dx
\le\Delta x\sum_{j=0}^{M-1}\max(0,f_j^+).
\end{gathered}
\tag{A.5}
```

These are the rectangular-sum bounds for a nonnegative, nonincreasing function. For $`Q`$, first multiply (A.2) by the per-profile error bound from Appendix B and enlarge the algebraic nodal enclosure in both directions. Then apply (A.5).

### A.4 The discrete infinite tail

Since $`I_Q\ge i_0=hv_0`$, for $`x\ge X`$,

```math
F_Q(x)\le F_Q(X)e^{-i_0(x^2-X^2)}.
```

Using $`x^2-X^2\ge2X(x-X)`$ gives

```math
\begin{gathered}
\int_X^\infty F_Q(x)\,dx\le\frac{\overline F_Q(X)}{2Xi_0},
\qquad X=64.
\end{gathered}
\tag{A.6}
```

The upper bound $`\overline F_Q(X)`$ includes the actual projection error and rounding.

### A.5 The continuous infinite tail

Let $`\kappa'=\kappa-2\rho\xi`$, and define

```math
\Delta(x)=\sqrt{\kappa'^2+4\alpha(x^2-1)},\quad
r_1=\frac{\kappa'-\Delta}{2\alpha},\quad
r_2=\frac{\kappa'+\Delta}{2\alpha}.
```

The bound $`\mathcal B\le1`$ in subsequent months allows each positive-loading profile to be bounded above by taking terminal value 1 for the first-month flow. For $`x\ge X=128`$,

```math
g=\frac{1-r_1}{1-r_2}\in(-1,0).
```

The cross-ratio solution of the Riccati equation yields

```math
\begin{gathered}
\mathcal B(t_1)\le r_1+\frac{\Delta}{\alpha}e^{-\Delta t_1},
\qquad
\int_0^{t_1}\mathcal B(t)\,dt
\le r_1t_1+\frac{\log2}{\alpha}.
\end{gathered}
\tag{A.7}
```

Furthermore, $`\Delta(x)\ge2\sqrt\alpha(x-1/X)`$ and $`\Delta(X)t_1>1`$, so $`\Delta e^{-\Delta t_1}`$ is decreasing throughout this tail region. Define

```math
C_0=\frac{\kappa'}{2\alpha}+\frac1{X\sqrt\alpha},\quad
C_1=C_0+\frac{\Delta(X)e^{-\Delta(X)t_1}}{\alpha},
```

```math
C=\exp\!\left\{2r+d+2rt_1+
d\left(t_1C_0+\frac{\log2}{\alpha}\right)+v_0C_1\right\},
\qquad \zeta=\frac{dt_1+v_0}{\sqrt\alpha}.
```

Each normalized real transform is therefore at most $`Ce^{-\zeta x}`$. Since $`(A-cG)^2\le2A^2+2c^2G^2`$,

```math
\begin{gathered}
\int_X^\infty F_P(x)\,dx
\le \frac{20000(1+c^2)C}{\zeta}e^{-\zeta X}.
\end{gathered}
\tag{A.8}
```

All root relations, signs, and transcendental functions are checked using outward-rounded arithmetic.

Combining (A.5)–(A.8) and multiplying by $`2/\sqrt\pi`$ gives

```math
\begin{aligned}
W_P&\le2.172471592801589415440352,\\
W_Q&\le2.242189951599049647468543.
\end{aligned}
\tag{A.9}
```

These moment bounds also establish the integrability required in (2.7).

## Appendix B. The actual projection kernel and affine identification

### B.1 The one-step projection correction

Let the current variance be $`v\ge0`$, and let $`p`$ be the real part of the stock loading. After the Gaussian tilt induced by the stock loading, the candidate next-step variance satisfies

```math
Y\sim N(\eta_pv+dh,\;\xi^2hv),\qquad
\eta_p=1-(\kappa-\rho\xi p)h,
```

with the external factor $`\exp(rph+\gamma_p hv)`$, where $`\gamma_p=(p^2-p)/2`$. For a future complex variance coefficient $`b`$, if the candidate is $`Y=-z<0`$, then

```math
\begin{gathered}
|e^{bY^+}-e^{bY}|
\le |b|z e^{|b|z}
\le \frac{|b|h}{\lambda e}
\exp[(\lambda/h+|b|)z].
\end{gathered}
\tag{B.1}
```

Set $`s_b=\lambda+h|b|`$. The Gaussian moment formula reduces the exponent in the state-dependent error bound to

```math
\begin{gathered}
-\frac v h\left(s_b\eta_p-\alpha s_b^2-\gamma_ph^2\right)-s_bd.
\end{gathered}
\tag{B.2}
```

Take $`\lambda=12`$. Suppose $`p`$ lies in the specified loading range, $`\eta_p\ge\eta_*`$, $`\gamma_p\le\gamma_*`$, and $`|b|\le b_*`$. Checking lower bounds for the concave quadratic at the two endpoints $`s_b=12`$ and $`s_b=12+b_*h`$ suffices to ensure that the expression in parentheses is at least 8.

### B.2 From local error bounds to true prefixes

Define

```math
\begin{gathered}
u_0=8,\qquad u_{j+1}=\eta_*u_j-\alpha u_j^2-\gamma_*h^2.
\end{gathered}
\tag{B.3}
```

Nonnegativity $`u_j\ge0`$ is checked at all 768 levels. For $`u\ge0`$, $`e^{-uY^+/h}\le e^{-uY/h}`$. Hence the actual stock-weighted prefix Laplace expectations can be bounded above by repeated application of Gaussian moment bounds. This yields the projection error bound for each complete profile:

```math
\begin{gathered}
\delta_Q=
\frac{b_*}{12e}\exp(C_f+C_{\rm pre}-12d)\,
h\sum_{j=0}^{767}
\exp\!\left[-d\sum_{k<j}u_k-\frac{v_0u_j}{h}\right].
\end{gathered}
\tag{B.4}
```

Here $`C_f`$ bounds the future constant term and $`C_{\rm pre}`$ bounds the stock drift over the true prefix. The two parameter sets are as follows.

| Use | Range of $`p`$ | $`b_*`$ | $`\eta_*`$ | $`\gamma_*`$ | $`C_f+C_{\rm pre}`$ |
| --- | --- | --- | --- | --- | --- |
| Weighted second moment | $`[0,2]`$ | 512 | $`1-(\kappa-2\rho\xi)h`$ | 1 | $`4r+d`$ |
| Thirteen linear transforms | $`[-1/2,1]`$ | 1024 | $`1-(\kappa-\rho\xi)h`$ | $`3/8`$ | $`2r+d`$ |

The finite catalog checks both $`\operatorname{Re}b\le1`$ and the modulus bound for the future coefficients. In the first case, (B.4) is multiplied by $`10000(1+c)^2`$ to obtain the error allowance at each Laplace node. In the second case, it is multiplied by the sum of the absolute values of all Fourier coefficients. No additional factor of $`h`$ is applied to this sum.

### B.3 Moment growth and removal of stopping

For real stock loading $`p`$, take $`e^{4V}`$ as the variance component of the test function. The coefficient of $`V`$ in the continuous generator calculation is

```math
\begin{gathered}
16\alpha-4\kappa+4\rho\xi p+\gamma_p.
\end{gathered}
\tag{B.5}
```

This coefficient is strictly negative for all required loadings, including their $`5/4`$-scaled range $`p\in[-5/4,5/2]`$. For $`Q`$, the positive coefficient 4 allows the direct use of $`1-e^{-4z}\le4z`$. Together with the Gaussian tail bound at $`\lambda=12`$, the additional growth rate caused by projection is at most

```math
\frac{4e^{-12d}}{12e}.
```

Over the same enlarged range, the state coefficient in the tilted exponent remains nonpositive. For example, using the worst-case values $`\eta_{5/2}`$ and $`\gamma_*=15/8`$, exact evaluation gives

```math
12\eta_{5/2}-144\alpha-\frac{15}{8}h^2
=\frac{8001336523}{983040000}>0.
```

The total constant growth satisfies

```math
\begin{gathered}
4d+\frac52r+\frac{4e^{-12d}}{12e}
<.589267620943<.6.
\end{gathered}
\tag{B.6}
```

Thus the required exponential moments of the true continuous and discrete models admit uniform finite upper bounds. In particular, the normalized moments for the original loading range $`p\in[-1,2]`$ are bounded by

```math
\begin{gathered}
M_2=e^{4v_0+.6}=e^{.78}
\end{gathered}
\tag{B.7}
```

First stop the continuous affine expression on bounded variance domains. Raising its modulus to the power $`5/4`$ scales the stock loadings into the range above. The future positive variance coefficient is at most $`5/4<4`$, and the nonpositive killing contribution can be omitted in an upper bound. Equations (B.5)–(B.6) therefore give a uniform $`L^{5/4}`$ bound for the stopped family, implying uniform integrability. Removing the stopping identifies the Riccati expression with the true transform expectation. The finite discrete telescoping sum involves only finitely many integrable conditional expectations, to which the same moment-growth estimate applies.

## Appendix C. Complete error control for inversion of the thirteen linear transforms

### C.1 Damped inversion and the finite sum

For a positive measure $`\mu`$, write $`\widehat\mu(z)=\int e^{zy}\mu(dy)`$. Take

```math
\begin{gathered}
\delta=1/2,\qquad \Delta u=1/5,\qquad N=640,\\
U=N\Delta u=128,\qquad L=2\pi/\Delta u=10\pi.
\end{gathered}
```

When the negative moment is finite, $`e^{-\delta y}F_\mu(y)`$ is integrable and has Fourier transform $`\widehat\mu(-\delta-iu)/(\delta+iu)`$. Consequently,

```math
\begin{gathered}
F_\mu(y)=\frac1{2\pi}\int_{\mathbb R}
\frac{e^{(\delta+iu)y}}{\delta+iu}\widehat\mu(-\delta-iu)\,du.
\end{gathered}
\tag{C.1}
```

Substitute (3.6), and set $`z_n=\delta+in\Delta u`$, $`w_0=1/2`$, and $`w_n=1`$ for $`n\ge1`$. The coefficients in the finite real sum are

```math
a_{0,n}=\frac{e^{-r}\Delta u\,w_n}{\pi z_n}
\left(95e^{z_ny_{95}}-110e^{z_ny_{110}}\right),
```

```math
\begin{gathered}
a_{i,n}=\frac{e^{-r}\Delta u\,w_n}{\pi z_n}\frac{100}{12}
\left(e^{z_ny_{110}}-e^{z_ny_{95}}\right),\qquad 1\le i\le12.
\end{gathered}
\tag{C.2}
```

The corresponding transforms are $`Ee^{-z_nY}`$ and $`Ee^{Z_i-z_nY}`$. The zero frequency receives half weight, while the highest retained frequency receives full weight. The real part of the remaining loading in a stock profile lies in $`[-1/2,1]`$; its squared modulus requires real loadings in $`[-1,2]`$.

### C.2 Periodization error

Poisson periodization gives

```math
\sum_{k\in\mathbb Z}e^{-\delta kL}F_\mu(y+kL).
```

For $`k>0`$, use the total mass $`M_{\mu,0}`$. For $`k=-j<0`$, use $`F_\mu(y-jL)\le e^{y-jL}M_{\mu,-1}`$. The sum of the nonzero-index terms is then at most

```math
\begin{gathered}
\frac{M_{\mu,0}}{e^{\delta L}-1}
+\frac{M_{\mu,-1}e^y}{e^{(1-\delta)L}-1}.
\end{gathered}
\tag{C.3}
```

Here $`M_{0,0}=1`$, $`M_{A,0}\le100e^{.01}`$, $`M_{0,-1}\le e^{.78}`$, and $`M_{A,-1}\le100e^{.78}`$. Taking absolute values term by term in the price combination gives the periodization error allowance for a single law:

```math
\begin{gathered}
E_{\rm alias}=
e^{-.01}\frac{
205+200e^{.01}
+e^{.78}(195e^{y_{95}}+210e^{y_{110}})
}{e^{5\pi}-1}.
\end{gathered}
\tag{C.4}
```

The difference between the two models is charged $`2E_{\rm alias}`$. The frequency tails below ensure absolute summability of the Fourier coefficients, while (C.3) ensures absolute and uniform convergence of the periodization on compact intervals. Fourier uniqueness therefore identifies both representations with the same continuous function.

### C.3 Frequency decay from the common Gaussian factor

Under the conditioning in (5.3), the total imaginary loading of each profile on the first-month factor $`U`$ is $`-u`$. Set $`K=E[e^{\text{real loading}}\mid\mathcal G]`$. Conditional Gaussian integration, followed by Cauchy–Schwarz and conditional Jensen, gives

```math
\begin{gathered}
|\Phi_\nu(u)|
\le E[K e^{-u^2sI/2}]
\le\sqrt{E e^{2\,\text{real loading}}}
\sqrt{E e^{-su^2I}}
\le\sqrt{M_2L_\nu(u)}.
\end{gathered}
\tag{C.5}
```

Here $`L_\nu(u)=E_\nu e^{-su^2I}`$. For the average of the twelve terms defining $`F_A`$, retain the additional price-level factor 100. Define

```math
C_*=
e^{-.01}\left(195e^{\delta y_{95}}+210e^{\delta y_{110}}\right).
```

Under $`Q`$, $`I\ge i_0=hv_0`$, so

```math
L_Q(u)\le L_Q(U)e^{-si_0(u^2-U^2)}\quad(u\ge U).
```

A validated upper bound for the true $`L_Q(U)`$ requires only 64 backward steps. Starting from $`b=A=0`$, use

```math
\begin{gathered}
A\leftarrow A+dhb,\qquad
b\leftarrow b+h(\alpha b^2-\kappa b-sU^2).
\end{gathered}
\tag{C.6}
```

At each level, verify $`b\le0`$. The inequality $`e^{bY^+}\le e^{bY}`$ then ensures that this Gaussian recursion is an upper bound for the actual positive-part kernel. At the end, $`\overline L_Q(U)=e^{A+bv_0}`$. Bounding the discrete sum of a positive decreasing envelope by its integral gives

```math
\begin{gathered}
E_{{\rm tail},Q}\le
\frac{C_*\sqrt{M_2\overline L_Q(U)}}{\pi s i_0U^2}.
\end{gathered}
\tag{C.7}
```

The integral inequality used here is

```math
\int_U^\infty e^{-a(u^2-U^2)}\frac{du}{u}\le\frac1{2aU^2}.
```

For $`P`$, define

```math
\Delta_U=\sqrt{\kappa^2+4\alpha sU^2},\quad
C_0=\kappa/(2\alpha),\quad
C_1=C_0+\Delta_Ue^{-\Delta_Ut_1}/\alpha,
```

```math
C_P=\exp\!\left\{
d(t_1C_0+\log2/\alpha)+v_0C_1\right\},\qquad
\gamma=\frac12\sqrt{s/\alpha}(dt_1+v_0).
```

The same CIR cross-ratio bound as in (A.7), now with terminal value $`b=0`$, gives $`L_P(u)\le C_Pe^{-2\gamma u}`$ for every $`u\ge U`$. Hence

```math
\begin{gathered}
E_{{\rm tail},P}\le
\frac{C_*\sqrt{M_2C_P}}{\pi\gamma U}e^{-\gamma U}.
\end{gathered}
\tag{C.8}
```

### C.4 Branches of the continuous complex flow

Write $`\kappa_q=\kappa-\rho\xi q`$, $`\gamma_q=(q^2-q)/2`$, and $`D_q=\sqrt{\kappa_q^2-4\alpha\gamma_q}`$. Divide each month into eight subintervals of length $`\Delta t=1/96`$. The denominator of the Möbius flow is

```math
\mathcal D_t=\cosh(D_qt/2)
+(\kappa_q-2\alpha b)\frac{\sinh(D_qt/2)}{D_q}.
```

The integral of the flow is

```math
\begin{gathered}
\int_0^{\Delta t}b(t)\,dt
=\frac{\kappa_q\Delta t/2-\log\mathcal D_{\Delta t}}{\alpha}.
\end{gathered}
\tag{C.9}
```

On every subinterval, verify

```math
\begin{gathered}
\cosh(|D_q|\Delta t/2)-1+
\frac{|\kappa_q-2\alpha b|\Delta t}{2}
\cosh(|D_q|\Delta t/2)<1.
\end{gathered}
\tag{C.10}
```

Absolute-value bounds on the power series imply $`|\mathcal D_t-1|<1`$ along the entire subinterval. The principal logarithm therefore remains continuously connected to the initial value 1 of the denominator. At the boundary $`\operatorname{Re}b=1`$, the imaginary-part quadratic form

```math
-\alpha(\operatorname{Im}b)^2
-\rho\xi(\operatorname{Im}q)(\operatorname{Im}b)
-(\operatorname{Im}q)^2/2
```

is nonpositive and the remaining real drift is strictly negative. Thus the continuous flow satisfies $`\operatorname{Re}b\le1`$. Appendix B.3 identifies the affine expression with the true transform.

### C.5 Combination and precision

Let $`\widehat e_L`$ be the finite proxy difference. The true linear difference is enclosed by

```math
\begin{gathered}
\widehat e_L+
[-E_L,E_L],\qquad
E_L=2E_{\rm alias}+E_{{\rm tail},P}
+E_{{\rm tail},Q}+\delta_Q\sum_{n,i}|a_{i,n}|.
\end{gathered}
\tag{C.11}
```

All finite sums and coefficients are evaluated as Arb enclosures. Substituting the exact rational endpoints gives

```math
E_L\le.000594238059839992574505.
```

Combining this with the asymmetric payoff remainder obtained from (A.9), according to Theorem 4.1, yields (4.4).

## Appendix D. Gaussian density expansions and finite-step bounds

### D.1 Variance expansion

For $`t/h\in\mathbb N`$, set

```math
x=-\frac th\log(1-\kappa h)-\kappa t\ge0.
```

The power series for the logarithm gives

```math
0\le x-\frac{\kappa^2th}{2}
\le\frac{\kappa^3th^2}{3(1-\kappa h)},\qquad
x\le\frac{\kappa^2th}{2(1-\kappa h)}.
```

Using $`|1-e^{-x}-x|\le x^2/2`$ and substituting

```math
I_h(t)-I(t)=\frac D\kappa e^{-\kappa t}(1-e^{-x})
```

yields $`|I_h(t)-I(t)-ha(t)|\le h^2B_I(t)`$. Adding the two cumulative remainder bounds at adjacent times gives (6.5).

### D.2 Density derivatives

For a single increment, let $`X=Y-r/12`$. Its density is

```math
f_s(y)=(2\pi s)^{-1/2}
\exp[-X^2/(2s)-X/2-s/8].
```

Hence

```math
\partial_s\log f_s=-\frac1{2s}+\frac{X^2}{2s^2}-\frac18,\qquad
\partial_s^2\log f_s=\frac1{2s^2}-\frac{X^2}{s^3}.
```

With $`X=-s/2+\sqrt{s}G`$, the first-order score has mean zero and second moment $`J(s)=1/(2s^2)+1/(4s)`$. Moreover,

```math
E|\partial_s^2\log f_s|
\le\frac3{2s^2}+\frac1{4s}.
```

Independence of the coordinates makes the cross-score expectations vanish, yielding the two $`L^1`$ derivative bounds used in the proof of Theorem 6.1. On a variance box with a positive lower bound and a finite upper bound, the first and second density derivatives are uniformly dominated by $`C(1+|y|^4)e^{-c|y|^2}`$. Difference quotients, parameter integrals, and payoff integrals may therefore be interchanged as required.

### D.3 A complete finite-step comparison

For two variance vectors $`s,\tilde s`$, suppose that their endpoints and the segment joining them satisfy $`s_j,\tilde s_j\ge u_j>0`$. Integrating the first-order score along the segment gives

```math
\begin{gathered}
\operatorname{TV}(p_s,p_{\tilde s})
\le\left\{
\sum_j(\tilde s_j-s_j)^2
\left(\frac1{8u_j^2}+\frac1{16u_j}\right)
\right\}^{1/2}.
\end{gathered}
\tag{D.1}
```

For a payoff with range length $`L`$, the price difference is at most $`Le^{-r\tau}\operatorname{TV}`$. On (6.10), using the uniform bounds $`|D|\le.015`$ and $`u_j\ge.03/12`$, finite computation gives

```math
|e_{h,\rm Asian}|\le.004990923469,\qquad
|R_{h,\rm Asian}|\le.000165216416.
```

The posterior module uses the tighter actual minimum variance for each month, so its reference bound $`\varepsilon_0`$ at fixed parameters can be smaller than this uniform bound.

### D.4 An effectively computable representation of the leading coefficient

For rational parameters and the explicit Lipschitz payoffs considered here, the leading coefficient in (6.7) is an effectively computable integral. Let

```math
S_d(G)=\sum_jd_j\left[\frac{G_j^2-1}{2s_j}-\frac{G_j}{2\sqrt{s_j}}\right],
\qquad F=\sum_jd_j^2J(s_j).
```

After centering the payoff, omitting the region $`\max_j|G_j|>R`$ incurs error at most

```math
\begin{gathered}
e^{-r\tau}\frac L2\sqrt{24F}\,e^{-R^2/4}.
\end{gathered}
\tag{D.2}
```

This follows directly from Cauchy–Schwarz and a union bound for Gaussian tails. On $`[-R,R]^{12}`$, define

```math
\begin{aligned}
M_S&=\sum_j|d_j|\left[\frac{R^2+1}{2s_j}+\frac R{2\sqrt{s_j}}\right],\\
L_S&=\sum_j|d_j|\left[\frac R{s_j}+\frac1{2\sqrt{s_j}}\right].
\end{aligned}
```

If the payoff has Lipschitz constant $`L_z`$ as a function of the fixing log-price vector, the integrand has Lipschitz constant at most

```math
L_H=L_z\left(\sum_j\sqrt{s_j}\right)M_S+\frac L2L_S.
```

The sum of box-midpoint values weighted by exact Gaussian box probabilities, for boxes of side length $`\ell`$, has total interior error at most $`e^{-r\tau}L_H\ell/2`$. Choosing $`R,\ell`$ together with (D.2) therefore gives a finite algorithm with at most $`\lceil2R/\ell\rceil^{12}`$ boxes. This representation establishes computability; Section 9 distinguishes this representation from an actually executed high-precision evaluation of the leading coefficient.

## Appendix E. Perturbation constants for positive volatility of volatility

In the continuous model, $`D_t=V_t^\xi-v(t)`$ admits a linear variation-of-constants representation. Since $`EV_t^\xi=v(t)\le M`$, the Itô isometry gives

```math
\begin{gathered}
ED_t^2=\xi^2\int_0^te^{-2\kappa(t-s)}EV_s^\xi\,ds
\le\frac{\xi^2M}{2\kappa_-}.
\end{gathered}
\tag{E.1}
```

The discrete deterministic reference remains nonnegative. The positive-part map is 1-Lipschitz, and the Gaussian innovation has conditional mean zero. Thus, writing $`D_j^{(2)}=E(V_j^\xi-v_j)^2`$, we obtain

```math
\begin{gathered}
D_{j+1}^{(2)}
\le(1-\kappa h)^2D_j^{(2)}+\xi^2hEV_j^\xi
\le(1-\kappa h)^2D_j^{(2)}
+\xi^2h(M+\sqrt{D_j^{(2)}}).
\end{gathered}
\tag{E.2}
```

Take $`C_Q^2=2M/\kappa_-`$. Condition (7.1) gives $`\xi C_Q\le M`$ and $`1-(1-\kappa h)^2\ge\kappa_-h`$. Induction from the zero initial error then yields $`D_j^{(2)}\le\xi^2C_Q^2`$. This step retains the effect of projection on $`EV_j^\xi`$.

For the deterministic reference $`v\ge m`$,

```math
|\sqrt{x}-\sqrt v|^2
=\frac{|x-v|^2}{(\sqrt x+\sqrt v)^2}\le |x-v|^2/m.
```

The drift contribution to the log-stock difference is bounded by $`T\xi C_\nu/2`$. The Itô isometry and Doob's $`L^2`$ inequality bound the martingale contribution by $`2\xi C_\nu\sqrt{T/m}`$, proving (7.3). Correlation between the stock Brownian motion and the variance driver does not alter these inequalities for adapted stochastic integrals.

For a put, the absolute derivative with respect to log stock price is at most $`K`$ on the active region. For the capped Asian, consider a line segment in the fixing log-price vector. On the active region $`K_1<A<K_2`$, the gradient has $`\ell^1`$-norm $`A\le K_2`$; elsewhere it is zero. Piecewise absolute continuity gives the global Lipschitz constant 110. Thus, for maturity $`T`$,

```math
e_{\nu,i}=K_i e^{-rT_i}\xi_{\max}C_\nu
\left(T_i/2+2\sqrt{T_i/m}\right),
```

```math
\begin{gathered}
e_{\nu,J}=110e^{-r}\xi_{\max}C_\nu
\left(1/2+2/\sqrt m\right).
\end{gathered}
\tag{E.3}
```

In (7.5), $`m=.03,M=.06,\kappa=3`$, so $`C_P=.1,C_Q=.2`$, giving

```math
\begin{gathered}
e_{P,J}\le.000131198492451391,\qquad
e_{Q,J}\le.000262396984902781.
\end{gathered}
\tag{E.4}
```

For (7.4), first enclose the reference variance difference over 256 closed intervals in $`\kappa`$ using outward arithmetic. Then apply

```math
|p_h^\xi-p_c^\xi|
\le |p_h^0-p_c^0|+
110\xi(C_P+C_Q)(1/2+2/\sqrt m)
```

to obtain the full-box price bound stated in the main text. The remaining parameters are enclosed through uniform bounds on $`m,M,|v_0-\bar v|`$, rather than by substituting endpoint samples for full enclosures.

## Appendix F. Posterior inputs, normalization, and finite coupling

### F.1 Exact quotes

The quotes are ordered by $`T=1/4,1/2,1`$, with $`K=90,100,110`$ within each maturity. The following rational numbers are taken as the given synthetic inputs:

```math
\begin{gathered}
y=\begin{pmatrix}
526706580970763/562949953421312\\
285901443526503/70368744177664\\
754049251176359/70368744177664\\
580752698287259/281474976710656\\
794307614955649/140737488355328\\
830842010134081/70368744177664\\
269207942741719/70368744177664\\
137257851354697/17592186044416\\
1918003280297167/140737488355328
\end{pmatrix}.
\end{gathered}
\tag{F.1}
```

These fractions are the exact binary64 values in the reference input file; the single-quote case uses the eighth entry. They are inputs to the likelihood, and the auxiliary computation that produced them need not be regarded as a proof of continuous-model prices.

### F.2 Reference prices and target constants

Let

```math
b_P(t)=\frac{1-e^{-3t}}3,\quad
b_Q(t)=\frac{1-(1-3h)^{t/h}}3,
```

```math
I_\nu(T;u)=.045T+(u-.045)b_\nu(T).
```

The reference put price is computed by the exact Black formula

```math
\begin{aligned}
p_\nu(K,T;u)&=Ke^{-rT}\Phi(-d_2)-S_0\Phi(-d_1),\\
d_1&=\frac{\log(S_0/K)+rT+I_\nu/2}{\sqrt{I_\nu}},\qquad
d_2=d_1-\sqrt{I_\nu}.
\end{aligned}
\tag{F.2}
```

Since $`b_\nu(T)>0`$ and vega is positive, the reference price over each entire $`u`$-cell is enclosed by its endpoint values. Expanding both endpoints by (E.3) then encloses the true prices over the entire cell and all $`\zeta`$.

Let

```math
\begin{aligned}
a_{\nu,j}&=b_\nu(t_j)-b_\nu(t_{j-1}),\\
z_{\nu,j}(u)&=.045/12+(u-.045)a_{\nu,j},\qquad B_*=15e^{-.01}.
\end{aligned}
```

The centered score bound in Appendix D gives

```math
L_0=\frac{B_*}2
\sqrt{\sum_ja_{P,j}^2J(z_{P,j}(.03))},
```

```math
\begin{aligned}
\varepsilon_0&=\frac{B_*}2
\sqrt{\sum_j\Delta_j^2J(\underline z_j)},\\
\Delta_j&=.015|a_{Q,j}-a_{P,j}|,\qquad
\underline z_j=\min(z_{P,j}(.03),z_{Q,j}(.03)).
\end{aligned}
\tag{F.3}
```

### F.3 Likelihood enclosures over entire cells

For $`d=1`$ or 9,

```math
\Sigma_d^{-1}=\frac{64}{27}\left(I_d-\frac{\mathbf1\mathbf1^T}{d+3}\right).
```

Writing the residual vector as $`r`$, its potential is a sum of nonnegative terms:

```math
\begin{gathered}
\frac12r^T\Sigma_d^{-1}r=
\frac{32}{27(d+3)}
\left(3\sum_i r_i^2+\sum_{i<j}(r_i-r_j)^2\right).
\end{gathered}
\tag{F.4}
```

Evaluate this expression and its exponential outward, then round to the exact integer lattice with spacing $`2^{-96}`$, to obtain

```math
0<l_{\nu,i}\le w_\nu(u,\zeta)\le u_{\nu,i}\le1
```

throughout the entire cell and nuisance-parameter domain. Integration against the probability measure $`\nu(d\zeta)`$ gives the same enclosure for $`\bar w_\nu(u)`$.

### F.4 Shared normalization and inverse-CDF pairing

Each cell has the same prior mass. At a node $`x_k`$, denote the sums of lower and upper mass bounds to its left by $`L_<,U_<`$, and those to its right by $`L_>,U_>`$. The marginal CDF $`G_\nu`$ satisfies

```math
\begin{gathered}
\underline G_\nu(x_k)=\frac{L_<}{L_<+U_>},
\qquad
\overline G_\nu(x_k)=\frac{U_<}{U_<+L_>}.
\end{gathered}
\tag{F.5}
```

The function $`A/(A+B)`$ increases in $`A`$ and decreases in $`B`$, so these enclosures retain the shared mass in the numerator and denominator. The normalizing constant is also enclosed directly by summing all weights.

Let $`U`$ be a common uniform random variable and set $`U_\nu=G_\nu^{-1}(U)`$. If $`U_\nu\in[x_i,x_{i+1}]`$, then

```math
\begin{gathered}
U\in[\underline G_\nu(x_i),\overline G_\nu(x_{i+1})].
\end{gathered}
\tag{F.6}
```

For each P-cell, enumerate the leftmost and rightmost indices $`j_-,j_+`$ of all Q-cell intervals whose corresponding ranges in (F.6) can intersect its range. Set

```math
\begin{gathered}
\delta_u=\Delta x\max_i\max\{|i-(j_++1)|,\ |i+1-j_-|\},
\quad \Delta x=.03/4096.
\end{gathered}
\tag{F.7}
```

The true cell pair must lie in this candidate set; hence $`|U_P-U_Q|\le\delta_u`$ almost surely. All comparisons use exact integers and fractions.

The enclosures of the normalizing constants for the true three-dimensional prior, obtained from all cells, are

| Case | $`Z_P`$ | $`Z_Q`$ |
| --- | --- | --- |
| Single quote | $`\begin{gathered}[c] [.935743002637584884,\\ .935913179433726711]\end{gathered}`$ | $`\begin{gathered}[c] [.935667223967444023,\\ .935927287640792653]\end{gathered}`$ |
| Nine quotes | $`\begin{gathered}[c] [.620128921272339539,\\ .621155228251382142]\end{gathered}`$ | $`\begin{gathered}[c] [.619743550733119263,\\ .621256330676942526]\end{gathered}`$ |

The target radii from Appendix E, together with (F.3) and (F.7), yield (7.8). This procedure encloses each model's own full posterior.

## Appendix G. Reproducible implementation

The public [implementation guide](../code/README.md) describes the numerical entry point `code/run.py`. The configuration in `code/configuration.json` specifies the parameter domain and module dependencies for each theorem. Core programs are stored in `code/core/`, reference results in `code/reference/`, and the exact synthetic calibration inputs in `code/data/synthetic_quotes.json`. Each execution creates an isolated output directory and preserves the reference results.

| Module | Corresponding result |
| --- | --- |
| `asian` | The complete certificate at the original point in Theorem 4.1 and Corollary 4.2 |
| `tt` | Theorem 6.1 and the effective constants on (6.10) |
| `small-xi` | The five-dimensional parameter box (7.4) |
| `posterior-zero` | Posterior and target constants for the Gaussian reference |
| `posterior` | Theorem 7.1 and the full three-dimensional prior (7.5) |

From the repository root, install the specified dependency with `python -m pip install -r code/requirements.txt`. Run all author modules and independent recomputations with `python code/run.py run --module all --independent`. The `--module` option also accepts any single module in the table. The `verify` command checks the per-file SHA manifest; the `check --run` command compares the mathematical fields of an execution directory with their reference values. Runtime and output-location metadata are separate from these mathematical comparisons.

The reference environment is Windows x86-64, CPython 3.12, and python-flint 0.8.0. Each numerical worker uses one thread and a hard memory limit of 256 MiB; an outer controller enforces timeouts and checks the results. The implementation's domains and theorem associations are documented in [the numerical scope guide](../code/SCOPE.md). The price conclusions rely on mathematical proofs and validated arithmetic enclosures; the implementation makes the finite numerical inputs and error bounds reproducible.

## References

<a id="ref-1"></a>

1. Curran, Michael. Valuing Asian and Portfolio Options by Conditioning on the Geometric Mean Price. *Management Science*, 40(12):1705–1711, 1994. [Source](https://doi.org/10.1287/mnsc.40.12.1705)

<a id="ref-2"></a>

2. Rogers, L. C. G., Shi, Z. The value of an Asian option. *Journal of Applied Probability*, 32(4):1077–1088, 1995. [Source](https://doi.org/10.2307/3215221)

<a id="ref-3"></a>

3. Thompson, G. W. P. Fast narrow bounds on the value of Asian options. Judge Institute of Management, University of Cambridge, WP09/2002, 2002. [Source](https://www.jbs.cam.ac.uk/wp-content/uploads/2020/08/wp0209.pdf)

<a id="ref-4"></a>

4. Fusai, Gianluca, Kyriakou, Ioannis. General Optimized Lower and Upper Bounds for Discrete and Continuous Arithmetic Asian Options. *Mathematics of Operations Research*, 41(2):531–559, 2016. [Source](https://doi.org/10.1287/moor.2015.0739)

<a id="ref-5"></a>

5. Heston, Steven L. A Closed-Form Solution for Options with Stochastic Volatility with Applications to Bond and Currency Options. *The Review of Financial Studies*, 6(2):327–343, 1993. [Source](https://doi.org/10.1093/rfs/6.2.327)

<a id="ref-6"></a>

6. QuantLib contributors. AnalyticDiscreteGeometricAveragePriceAsianHestonEngine. Official source code; fixed revision. [Source](https://github.com/lballabio/QuantLib/blob/966a4cc101049ca36a888b2ce223aa96d3f3b22d/ql/experimental/asian/analytic_discr_geom_av_price_heston.hpp)

<a id="ref-7"></a>

7. Talay, Denis, Tubaro, Luciano. Expansion of the global error for numerical schemes solving stochastic differential equations. *Stochastic Analysis and Applications*, 8(4):483–509, 1990. [Source](https://doi.org/10.1080/07362999008809220)

<a id="ref-8"></a>

8. Mickel, Annalena, Neuenkirch, Andreas. The weak convergence order of two Euler-type discretization schemes for the log-Heston model. arXiv:2106.10926v2, 2022. [Source](https://arxiv.org/abs/2106.10926v2)

<a id="ref-9"></a>

9. Bally, Vlad, Talay, Denis. The law of the Euler scheme for stochastic differential equations: I. Convergence rate of the distribution function. *Probability Theory and Related Fields*, 104(1):43–60, 1996. [Source](https://doi.org/10.1007/BF01303802)

<a id="ref-10"></a>

10. Cotter, S. L., Dashti, M., Stuart, A. M. Approximation of Bayesian Inverse Problems for PDEs. *SIAM Journal on Numerical Analysis*, 48(1):322–345, 2010. [Source](https://doi.org/10.1137/090770734)

<a id="ref-11"></a>

11. Johansson, Fredrik. Arb: Efficient Arbitrary-Precision Midpoint-Radius Interval Arithmetic. *IEEE Transactions on Computers*, 66(8):1281–1292, 2017. [Source](https://doi.org/10.1109/TC.2017.2690633)

<a id="ref-12"></a>

12. Lee, Roger W. Option Pricing by Transform Methods: Extensions, Unification, and Error Control. *The Journal of Computational Finance*, 7(3):51–86, 2004. [Source](https://doi.org/10.21314/JCF.2004.121)
