# Mathematical scope

Let P denote continuous-time Heston expectation and Q the positive-part Euler expectation on the fixed grid. Bias is Q minus P. Unless a module explicitly varies them, S0 = 100, r = 1/100, h = 1/768, and the Asian payoff is (A - 95)+ - (A - 110)+ with A the arithmetic average at twelve equally spaced fixings over one year. The nine puts have strikes 90, 100, 110 and maturities 1/4, 1/2, 1, ordered by maturity and then strike.

The numerical values below are outward enclosures under the standard inclusion semantics of Arb arithmetic and the analytical bounds proved in the accompanying paper. They are not statistical confidence intervals. Each module has a distinct parameter domain.

## Arithmetic Asian at the original parameter point

The parameter order is (kappa, vbar, xi, rho, v0), and the point is (3, 9/200, 23/100, -11/20, 9/200). The complete signed bias is enclosed by

```
[-0.011024692272353951236858, 0.010642371598649794390760].
```

This includes the conditional Gaussian remainder, finite-transform terms, transform tails, periodization, positive-part projection, and outward arithmetic. It is a pointwise result for the stated payoff and scheme. The weighted-square calculation alone is not the complete price-bias certificate. The linear pilot checks workload and guards; only its subsequent full run produces the complete result.

The separate price enclosures are

```
P: [6.508371733460267223617251, 6.518868973771394421053199]
Q: [6.507844281499040469816341, 6.519014105058917018008011].
```

## Talay-Tubaro expansion on the deterministic-variance face

Here xi = 0, kappa = 3, vbar = 9/200, and v0 ranges over [3/100, 3/50]. The theory applies to fixing-aligned step sizes h <= 1/768. The common ten-component first-order vector and a uniform remainder bound are established through Gaussian density differentiation. The scalar Asian first-order coefficient is represented and enclosed, not evaluated by high-dimensional quadrature. The nine put coefficients imply that the common vector is nonzero when v0 differs from vbar; at v0 = vbar the first-order vector vanishes. The pointwise coefficient checks in the program use v0 = 3/50. These claims do not extend the expansion to the original positive-xi point.

## Positive-volume small-xi price region

The five-dimensional box is

```
kappa in [2.999, 3.001]; vbar in [0.04499, 0.04501];
xi in [0.00001, 0.00004]; rho in [-0.8, -0.3];
v0 in [0.03001, 0.05999].
```

The original payoff definitions, grid and positive-part Euler update are retained. Both the continuous and discrete xi-to-zero perturbations are paid. This box is outside the original xi range [0.18, 0.28]; its bounds do not certify that larger domain.

## Posterior quantile displacement

The positive-xi posterior uses fixed kappa = 3, vbar = 9/200 and independent uniform priors on v0 in [0.03, 0.06], xi in [1e-7, 1e-6], and rho in [-0.8, -0.3]. The likelihood covariance is (3/4)^2 times [(3/4)I + (1/4)11^T]. The nine observations in `data/synthetic_quotes.json` are synthetic and are held as exact binary64 inputs. One-observation and nine-observation likelihoods are evaluated separately. The former uses the annual at-the-money put, the eighth entry in the nine-price ordering.

The result controls the displacement between corresponding continuous and Euler posterior target quantiles for every probability level in (0, 1). It does not compute absolute posterior endpoints and does not cover the original five-dimensional prior. The zero-xi posterior is a reference calculation on the one-dimensional v0 interval. No historical quotation or empirical trading claim is made by these modules.

## Program identities

Source and helper hashes bind each result to the executed implementation. `scope_sha256` and related keys bind this scope statement, not a machine-checked proof. The proof is in the accompanying paper. The principal and independent implementations use different numerical constructions where indicated in their source. Agreement verifies the stated finite calculations; it does not enlarge their domains.
