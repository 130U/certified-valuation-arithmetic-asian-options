"""The cost of the kink for market-style contracts under Heston, by simulation.

Each path keeps the shape of the fixings and the volatility of the common
factor; the stock noise before the first fixing is integrated in closed form
(Proposition 3.2).  The program reports, with standard errors,

    the option value and its proxy-exercise value,
    the cost of the kink (their difference), and
    the two bounds of Theorem 3.3 at their best scales.

These are binary64 Monte Carlo estimates under absorbed Euler with a fine
step.

    python studies/run_heston_contracts.py --output studies/results/heston-contracts.json
"""
from pathlib import Path
import argparse
import json
import math
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import heston  # noqa: E402

OIL = dict(kappa=2.0, vbar=0.1225, xi=0.7, rho=-0.3, v0=0.1225)
OIL_HIGH = dict(kappa=2.0, vbar=0.16, xi=0.8, rho=-0.3, v0=0.16)
RATE = 0.04

CONTRACTS = [
    # name, description, model, forward, strike, kind, lead days, fixings, steps per day, paths
    ('wti-1m', 'Crude oil average price option, one month ahead', OIL, 70.0, 70.0, 'call', 21, 21, 4, 1 << 19),
    ('wti-3m', 'Three months ahead', OIL, 70.0, 70.0, 'call', 63, 21, 4, 1 << 19),
    ('wti-6m', 'Six months ahead', OIL, 70.0, 70.0, 'call', 126, 21, 4, 1 << 19),
    ('wti-12m', 'Twelve months ahead', OIL, 70.0, 70.0, 'call', 252, 21, 4, 1 << 19),
    ('annual-put', 'Annual-average put, strike 70, four months ahead', OIL_HIGH, 100.0, 70.0, 'put', 84, 252, 2, 1 << 18),
]


def study(name, description, model, forward, strike, kind, lead, fixings, per_day, paths, seed):
    h = 1.0 / (252 * per_day)
    steps = [(lead + k) * per_day for k in range(fixings)]
    a_i, I1 = heston.conditional_paths(paths, steps, h, forward, 0.0, seed=seed, **model)
    sigma = np.sqrt((1.0 - model['rho'] ** 2) * I1)
    a = a_i.mean(axis=1)
    g = np.exp(np.log(a_i).mean(axis=1))
    X, w = a / g, 1.0 / sigma
    D = math.exp(-RATE * (lead + fixings - 1) / 252)
    tilt = np.exp(2 * sigma ** 2)
    c_log = float((X * w).mean() / w.mean())
    c_quad = float((a * g * tilt * w).mean() / (g * g * tilt * w).mean())
    peak = sigma * math.sqrt(2.0 * math.pi)
    call = D * heston.conditional_call(a, sigma, strike)
    proxy_call = D * heston.conditional_proxy(a, c_log * g, sigma, strike)
    cost = call - proxy_call
    if kind == 'put':
        parity = D * (a * np.exp(0.5 * sigma ** 2) - strike)
        value, proxy = call - parity, proxy_call - parity
    else:
        value, proxy = call, proxy_call
    x = X / c_log
    log_form = D * strike * (x - 1.0 - np.log(x)) / peak
    quad_form = D * tilt * (a - c_quad * g) ** 2 / (2.0 * strike * peak)
    row = {'name': name, 'description': description, 'kind': kind,
           'model': dict(model, rate=RATE, forward=forward, strike=strike),
           'lead_days': lead, 'fixings': fixings, 'steps_per_day': per_day, 'paths': paths, 'seed': seed,
           'feller_index': 2 * model['kappa'] * model['vbar'] / model['xi'] ** 2,
           'scale_log': c_log, 'scale_quadratic': c_quad}
    for key, sample in (('value', value), ('proxy_value', proxy), ('cost_of_kink', cost),
                        ('bound_log_form', log_form), ('bound_quadratic_form', quad_form),
                        ('inverse_common_volatility', w)):
        mean, se = heston.mean_se(sample)
        row[key] = mean
        row[key + '_standard_error'] = se
    row['mean_log_deviation'] = float(math.log(c_log) - (np.log(X) * w).mean() / w.mean())
    row['bound_over_cost'] = min(row['bound_log_form'], row['bound_quadratic_form']) / row['cost_of_kink']
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--seed', type=int, default=20261113)
    args = ap.parse_args()
    rows = []
    for i, spec in enumerate(CONTRACTS):
        row = study(*spec, seed=args.seed + i)
        rows.append(row)
        print(f"{row['name']:11s} value={row['value']:.4f} ({row['value_standard_error']:.1e})  "
              f"cost={row['cost_of_kink']:.3e} ({row['cost_of_kink_standard_error']:.0e})  "
              f"log={row['bound_log_form']:.3e}  quad={row['bound_quadratic_form']:.3e}  ratio={row['bound_over_cost']:.2f}  "
              f"c*={row['scale_log']:.6f}  E[1/sigma]={row['inverse_common_volatility']:.3f}", flush=True)
    record = {'status': 'HESTON_SIMULATION_ESTIMATES',
              'law': 'absorbed Euler at the stated number of steps per trading day; 252 trading days per year',
              'contracts': rows}
    if args.output:
        args.output.write_text(json.dumps(record, indent=1) + '\n', encoding='utf8', newline='\n')


if __name__ == '__main__':
    main()
