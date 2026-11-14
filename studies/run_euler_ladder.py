"""The Euler bias of the proxy value, step by step, and what the kink adds to it.

Part 1 (deterministic).  The Euler kernel without projection is affine, and its
transform coefficients are explicit Euler iterates of the Riccati system
(Proposition 6.1).  The program evaluates the proxy-exercise value of the 95-110
spread with the inversion design of Appendix C under the continuous model and
under that kernel for a ladder of step sizes, compares three rungs and a second
parameter point with the finite sums stored in the certified package, and fits
the first two coefficients of the bias expansion.

Part 2 (simulation).  The Euler bias of the option also contains the change in
the cost of the kink between the two laws.  Coupled paths estimate that change
between each step size and the finest one.

Binary64; the proved enclosures are in `code/`.

    python studies/run_euler_ladder.py --output studies/results/euler-ladder.json
    python studies/run_euler_ladder.py --check  studies/results/euler-ladder.json
"""
from pathlib import Path
import argparse
import json
import math
import sys
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import heston  # noqa: E402

MODEL = dict(S0=100.0, r=0.01, kappa=3.0, vbar=0.045, xi=0.23, rho=-0.55, v0=0.045)
SCALE = 1254433 / 1250000
FIXINGS = [(i + 1) / 12 for i in range(12)]
STORED = {384: 'asian-384-enclosure', 768: 'base-run', 1536: 'asian-1536-enclosure'}


def stored_sums():
    """Finite sums of the certified package: lower ends of their 24-digit enclosures."""
    out = {}
    with zipfile.ZipFile(ROOT / 'code/evidence/executions.zip') as archive:
        for steps, run in list(STORED.items()) + [('second point', 'asian-v004')]:
            data = json.loads(archive.read(f'execution/{run}/work/core/asian-linear-result.json'))
            out[steps] = {key: float(data[key]['outward24'][0])
                          for key in ('P_linear_finite', 'Q_proxy_linear_finite')}
    return out


def value(**kw):
    return heston.proxy_spread_value(fixing_times=FIXINGS, K1=95.0, K2=110.0, scale=SCALE, **kw)


def ladder():
    continuous = value(**MODEL)
    rungs = []
    for k in range(12):
        per_month = 2 ** k
        euler = value(euler_steps_per_interval=per_month, **MODEL)
        rungs.append({'steps_per_year': 12 * per_month, 'euler_proxy_value': euler, 'bias': euler - continuous,
                      'bias_times_steps': (euler - continuous) * 12 * per_month})
    # bias = b1 h + b2 h^2 + ...; eliminate the h^2 term from the two finest rungs
    (n1, e1), (n2, e2) = [(r['steps_per_year'], r['bias']) for r in rungs[-2:]]
    b1 = (e2 * n2 * n2 / n1 - e1 * n1) / (n2 / n1 - 1.0)
    b2 = (e1 * n1 - b1) * n1
    second = dict(MODEL, v0=0.04)
    return {'continuous_proxy_value': continuous, 'rungs': rungs,
            'first_order_coefficient': b1, 'second_order_coefficient': b2,
            'second_point': {'v0': 0.04, 'continuous_proxy_value': value(**second),
                             'euler_proxy_value_768': value(euler_steps_per_interval=64, **second)}}


def compare(result):
    stored = stored_sums()
    rows = []
    by_steps = {r['steps_per_year']: r for r in result['rungs']}
    for steps in STORED:
        gap_p = result['continuous_proxy_value'] - stored[steps]['P_linear_finite']
        gap_q = by_steps[steps]['euler_proxy_value'] - stored[steps]['Q_proxy_linear_finite']
        rows.append({'steps_per_year': steps,
                     'stored_bias': stored[steps]['Q_proxy_linear_finite'] - stored[steps]['P_linear_finite'],
                     'continuous_difference': gap_p, 'euler_difference': gap_q})
        assert abs(gap_p) < 1e-11 and abs(gap_q) < 1e-11, rows[-1]
    point = result['second_point']
    gaps = (point['continuous_proxy_value'] - stored['second point']['P_linear_finite'],
            point['euler_proxy_value_768'] - stored['second point']['Q_proxy_linear_finite'])
    assert max(abs(x) for x in gaps) < 1e-11, gaps
    return rows


def kink_change(paths, seed):
    """Coupled estimate of R_Q(K) - R_P(K), the finest level standing in for P."""
    levels = [16, 32, 64, 128, 256]
    disc = math.exp(-MODEL['r'])
    sums = np.zeros((len(levels), 3))
    squares = np.zeros((len(levels), 3))
    count = 0
    for chunk in heston.coupled_levels(paths, levels, 12, 1.0 / 12, seed=seed, **MODEL):
        costs = []
        for a_i, I1 in chunk:
            sigma = np.sqrt((1.0 - MODEL['rho'] ** 2) * I1)
            a = a_i.mean(axis=1)
            b = SCALE * np.exp(np.log(a_i).mean(axis=1))
            costs.append([disc * (heston.conditional_call(a, sigma, K) - heston.conditional_proxy(a, b, sigma, K))
                          for K in (95.0, 110.0)])
        for l in range(len(levels)):
            d95 = costs[l][0] - costs[-1][0]
            d110 = costs[l][1] - costs[-1][1]
            for j, d in enumerate((d95, d110, d95 - d110)):
                sums[l, j] += d.sum()
                squares[l, j] += (d * d).sum()
        count += len(chunk[0][1])
    rows = []
    for l, per_month in enumerate(levels[:-1]):
        mean = sums[l] / count
        se = np.sqrt(np.maximum(squares[l] / count - mean ** 2, 0.0) / count)
        rows.append({'steps_per_year': 12 * per_month, 'reference_steps_per_year': 12 * levels[-1],
                     'change_at_95': [float(mean[0]), float(se[0])],
                     'change_at_110': [float(mean[1]), float(se[1])],
                     'change_in_spread': [float(mean[2]), float(se[2])]})
    return {'paths': count, 'seed': seed, 'rows': rows}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--check', type=Path, help='recompute the deterministic part and compare with a saved result')
    ap.add_argument('--paths', type=int, default=1 << 20)
    ap.add_argument('--seed', type=int, default=20261113)
    args = ap.parse_args()
    result = ladder()
    result['comparison_with_certified_sums'] = compare(result)
    if args.check:
        saved = json.loads(args.check.read_text(encoding='utf8'))
        assert abs(saved['continuous_proxy_value'] - result['continuous_proxy_value']) < 1e-10
        for new, old in zip(result['rungs'], saved['rungs']):
            assert new['steps_per_year'] == old['steps_per_year'] and abs(new['bias'] - old['bias']) < 1e-10
        print(json.dumps({'status': 'PASS', 'rungs': len(result['rungs']),
                          'certified_sums_reproduced_within': 1e-11}))
        return
    result['kink_cost_change'] = kink_change(args.paths, args.seed)
    record = {'status': 'EULER_LADDER', 'binary64': True, 'model': MODEL, 'scale': SCALE, **result}
    if args.output:
        args.output.write_text(json.dumps(record, indent=1) + '\n', encoding='utf8', newline='\n')
    for r in result['rungs']:
        print(f"{r['steps_per_year']:6d}  bias {r['bias']:+.6e}  steps x bias {r['bias_times_steps']:+.6f}")
    print('b1, b2 =', result['first_order_coefficient'], result['second_order_coefficient'])
    for r in result['comparison_with_certified_sums']:
        print(r)
    for r in result['kink_cost_change']['rows']:
        print(r)


if __name__ == '__main__':
    main()
