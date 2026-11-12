# Mathematical structure

The [paper](../manuscript/report.md) studies the signed price difference for one fixed arithmetic Asian contract, continuous model and discrete implementation. The construction follows six steps.

1. **Integrate a common source of noise exactly.** Conditional on the variance driver and the later independent stock increments, all fixing prices share the first-period Gaussian term. Proposition 2.1 evaluates its call integral and gives an exact conditional price representation. An outer expectation remains.
2. **Choose a reference compatible with both conditioning and transforms.** The geometric average has the same multiplier as the arithmetic average, and its logarithm is a linear loading of the fixing-date log prices. Section 3.1 explains these properties and the restricted characterization among symmetric, degree-one monomials.
3. **Derive the weight from curvature.** Lemma 3.1 bounds the convex call remainder by a squared arithmetic–geometric residual divided by the conditional standard deviation. In Heston this gives the inverse square root of first-period integrated variance. Section 4.1 identifies the scale minimizing the exact nonlinear bound and distinguishes it from the rational scale and total computed width.
4. **Evaluate the quantities required by the identity.** Section 3 and Appendix A derive 13 linear-transform loadings and 91 second-moment loadings for twelve fixings. The algebraic discrete recursion is not the exact transform of the projected scheme: Appendix B bounds their difference. Appendix C controls inversion and its infinite tails.
5. **Combine the estimates in price units.** Theorem 4.1 gives a signed enclosure. Corollary 4.2 supplies the complete calculation at the principal Heston point. The code and exact endpoints are indexed in [EVIDENCE.md](EVIDENCE.md).
6. **Identify the information lost by the bound.** Separate-law remainder estimates can remain positive for identical laws. The coupled-remainder appendix compares remainders under a coupling and evaluates the additional moments in a deterministic-variance example. The corresponding stochastic-variance calculation remains open.

Three limits apply. The exact conditional representation does not evaluate the full Heston Asian price in closed form. The finite certificate is not a convergence-rate theorem. The coupling result is established for deterministic variance and is not a general improvement under stochastic variance. The Gaussian weak expansion in Section 6 and the posterior transfer in Section 7 each have their own hypotheses.

[Computational details](COMPUTATION.md) · [Evidence and reproduction](EVIDENCE.md)
