"""The cost of the kink across strikes for the Heston contract of Section 5, by simulation.

Twelve monthly fixings over one year, S0 = 100, r = 1%, and
(kappa, vbar, xi, rho, v0) = (3, 0.045, 0.23, -0.55, 0.045).  The program
estimates, on a grid of strikes,

    R(K) = E[(A - K)^+] - E[(A - K) 1{cG > K}]      (undiscounted),

its second-order (gamma) term, and the two bounds of Theorem 3.3.  It then
checks the two conservation laws of Proposition 3.1,

    integral of R(K) dK       = E[(A - cG)^2] / 2,
    integral of R(K) dK / K^2 = E[d(A / cG)],

and records a sample of (cG, A) pairs for Figure 1.  Binary64 Monte Carlo under
absorbed Euler with 3072 steps per year; an illustration, not a certificate.

    python studies/run_gap_profile.py --output studies/results/gap-profile.json
"""
from pathlib import Path
import argparse
import json
import math
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import heston  # noqa: E402

MODEL = dict(S0=100.0, r=0.01, kappa=3.0, vbar=0.045, xi=0.23, rho=-0.55, v0=0.045)
SCALE = 1254433 / 1250000
STEPS_PER_MONTH = 256


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--paths', type=int, default=1 << 20)
    ap.add_argument('--seed', type=int, default=20261113)
    args = ap.parse_args()
    h = 1.0 / (12 * STEPS_PER_MONTH)
    steps = [STEPS_PER_MONTH * (i + 1) for i in range(12)]
    a_i, I1 = heston.conditional_paths(args.paths, steps, h, seed=args.seed, **MODEL)
    sigma = np.sqrt((1.0 - MODEL['rho'] ** 2) * I1)
    a = a_i.mean(axis=1)
    g = np.exp(np.log(a_i).mean(axis=1))
    del a_i
    b = SCALE * g
    X, w = a / g, 1.0 / sigma
    peak = sigma * math.sqrt(2.0 * math.pi)
    x = a / b
    bregman = x - 1.0 - np.log(x)
    second = np.exp(2 * sigma ** 2) * (a - b) ** 2

    c_star = float((X * w).mean() / w.mean())
    summary = {
        'paths': args.paths, 'seed': args.seed, 'steps_per_year': 12 * STEPS_PER_MONTH, 'scale': SCALE,
        'inverse_common_volatility': heston.mean_se(w),
        'mean_ratio_A_over_G': heston.mean_se(X),
        'best_log_scale': c_star,
        'mean_log_deviation': float(math.log(c_star) - (np.log(X) * w).mean() / w.mean()),
        'bregman_mass': heston.mean_se(bregman),
        'half_second_moment': heston.mean_se(0.5 * second),
        'log_form_bound_over_strike': heston.mean_se(bregman / peak),
        'quadratic_form_bound_times_strike': heston.mean_se(0.5 * second / peak),
    }

    grid = np.exp(np.linspace(math.log(30.0), math.log(330.0), 481))
    rows = []
    for K in grid:
        cost = heston.conditional_call(a, sigma, K) - heston.conditional_proxy(a, b, sigma, K)
        gamma = K * np.exp(-0.5 * (np.log(b / K) / sigma) ** 2) / (peak * b * b)
        rows.append((float(K), *heston.mean_se(cost), float((0.5 * (a - b) ** 2 * gamma).mean())))
    K = np.array([r[0] for r in rows])
    R = np.array([r[1] for r in rows])
    summary['integral_R_dK'] = float(np.trapezoid(R, K))
    summary['integral_R_dK_over_K2'] = float(np.trapezoid(R / K ** 2, K))

    disc = math.exp(-MODEL['r'])
    named = {}
    for strike in (95.0, 110.0):
        call = disc * heston.conditional_call(a, sigma, strike)
        proxy = disc * heston.conditional_proxy(a, b, sigma, strike)
        named[str(int(strike))] = {
            'call': heston.mean_se(call), 'proxy_value': heston.mean_se(proxy),
            'cost_of_kink': heston.mean_se(call - proxy),
            'bound_log_form': heston.mean_se(disc * strike * bregman / peak),
            'bound_quadratic_form': heston.mean_se(disc * 0.5 * second / (strike * peak))}
    spread = disc * (heston.conditional_call(a, sigma, 95.0) - heston.conditional_call(a, sigma, 110.0))
    spread_proxy = disc * (heston.conditional_proxy(a, b, sigma, 95.0) - heston.conditional_proxy(a, b, sigma, 110.0))
    named['spread'] = {'value': heston.mean_se(spread), 'proxy_value': heston.mean_se(spread_proxy),
                       'value_minus_proxy': heston.mean_se(spread - spread_proxy)}

    rng = np.random.default_rng(args.seed + 1)
    pick = rng.choice(args.paths, size=6000, replace=False)
    U = sigma[pick] * rng.standard_normal(6000)
    sample = [[round(float(u), 5), round(float(v), 5)]
              for u, v in zip(b[pick] * np.exp(U), a[pick] * np.exp(U))]

    record = {'status': 'HESTON_SIMULATION_ESTIMATES', 'estimates_are_not_proofs': True, 'model': MODEL,
              'summary': summary, 'strikes_95_110': named,
              'profile': [{'strike': r[0], 'cost': r[1], 'standard_error': r[2], 'gamma_term': r[3]}
                          for r in rows[::4]],
              'sample_cG_A': sample}
    if args.output:
        args.output.write_text(json.dumps(record, indent=1) + '\n', encoding='utf8', newline='\n')
    print(json.dumps(summary, indent=1))
    print(json.dumps(named, indent=1))


if __name__ == '__main__':
    main()
