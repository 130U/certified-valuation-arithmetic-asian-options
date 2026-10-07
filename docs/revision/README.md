# Revision review evidence

These reviews support the 7 October 2026 revision. They are source/proof and
saved-result reviews by collaborating agents, not external peer review or
independent third-party numerical certification. The exact executed numerical
sources, outputs and failed attempts are in `../../code/revision/results/evidence.zip`.

- `PROOF_PACKAGE.md`: derivation of common-scale optimization and the sufficient
  coupled-remainder bound. Appendix H in the manuscript is the final statement.
- `coupling-proof-review.md`: mathematical review and the resolved marginal
  integrability issue.
- `numerical-extension-review.md`: scope, retained guards and source review of
  the step, moment, posterior and score-bound extensions.
- `source-audit.md`: primary-source Fusai--Kyriakou comparison with exact locators.
- `final-number-review.md`: beta, posterior and diagnostic result read-back.
- `final-step-review.md`: exact step/fee reconciliation and stopping reasons.

Reviews do not fill the outstanding computations listed in
`../../REVISION-RESPONSE-zh.md`. The subsequent targeted revision adds one different stochastic Heston point
and a deterministic-variance closed-moment coupling example; see
`../revision-round2/`. Tight signed twelve-dimensional Asian coefficient
integration and positive-volatility coupled moments remain uncomputed.
