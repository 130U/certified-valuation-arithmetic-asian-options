# Synthetic observations

The nine observations are model-generated test inputs, not market quotations. Their decimal forms are stored as JSON numbers, then converted by `Fraction.from_float` to the exact dyadic rational represented by binary64. No additional rounding interval is silently introduced. The calibration covariance and parameter domains are stated in `SCOPE.md`.

| Index | Maturity | Strike | Exact observation |
| --- | --- | --- | --- |
| 1 | 1/4 | 90 | 526706580970763/562949953421312 |
| 2 | 1/4 | 100 | 285901443526503/70368744177664 |
| 3 | 1/4 | 110 | 754049251176359/70368744177664 |
| 4 | 1/2 | 90 | 580752698287259/281474976710656 |
| 5 | 1/2 | 100 | 794307614955649/140737488355328 |
| 6 | 1/2 | 110 | 830842010134081/70368744177664 |
| 7 | 1 | 90 | 269207942741719/70368744177664 |
| 8 | 1 | 100 | 137257851354697/17592186044416 |
| 9 | 1 | 110 | 1918003280297167/140737488355328 |

The numerical certificates condition on these supplied values. Reproducing the simulation that originally supplied synthetic observations is neither required nor claimed by this package. References contain exact rational interval endpoints from deterministic calculations; they are not additional observations.
