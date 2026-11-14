"""Proved price intervals for market-style average-price options under Black's model.

For each contract the program encloses, in Arb ball arithmetic,

    the proxy-exercise value L,
    the two kink bounds of Theorem 3.3, and
    the price interval [L, L + min(bounds)].

It adds three binary64 diagnostics that are not part of any proof: the cubic
law, the classical first-order bound (D/2) E[sd(A | G)], and a Monte Carlo
estimate of the true cost of the kink.

    python studies/run_black.py --output studies/results/black-contracts.json
    python studies/run_black.py --check  studies/results/black-contracts.json
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import black  # noqa: E402

DAY = Q(1, 252)
DIGITS = 12


def daily(lead_days, fixings):
    return [(lead_days + k) * DAY for k in range(fixings)]


CONTRACTS = [
    # name, description, Contract, strike, kind, price unit, quote step, volume
    ('wti-1m', 'Crude oil average price option: one calendar month of daily settlements, one month ahead',
     black.Contract(daily(21, 21), 70, Q(49, 400), rate=Q(4, 100)), 70, 'call', 'USD per barrel', Q(1, 100), None),
    ('wti-3m', 'The same option three months ahead',
     black.Contract(daily(63, 21), 70, Q(49, 400), rate=Q(4, 100)), 70, 'call', 'USD per barrel', Q(1, 100), None),
    ('wti-6m', 'The same option six months ahead',
     black.Contract(daily(126, 21), 70, Q(49, 400), rate=Q(4, 100)), 70, 'call', 'USD per barrel', Q(1, 100), None),
    ('wti-12m', 'The same option twelve months ahead',
     black.Contract(daily(252, 21), 70, Q(49, 400), rate=Q(4, 100)), 70, 'call', 'USD per barrel', Q(1, 100), None),
    ('wti-3m-put60', 'Three months ahead, put struck at 60',
     black.Contract(daily(63, 21), 70, Q(49, 400), rate=Q(4, 100)), 60, 'put', 'USD per barrel', Q(1, 100), None),
    ('wti-3m-call80', 'Three months ahead, call struck at 80',
     black.Contract(daily(63, 21), 70, Q(49, 400), rate=Q(4, 100)), 80, 'call', 'USD per barrel', Q(1, 100), None),
    ('copper-3m', 'Copper traded average price option: one month of official settlements, three months ahead',
     black.Contract(daily(63, 22), 9500, Q(121, 2500), rate=Q(4, 100)), 9500, 'call', 'USD per tonne', Q(1, 100), None),
    ('eurusd-quarter', 'EUR/USD average-rate call: one quarter of daily fixings, three months ahead',
     black.Contract(daily(63, 63), Q(11, 10), Q(4, 625), rate=Q(4, 100)), Q(11, 10), 'call', 'USD per EUR', Q(1, 10000), None),
    ('annual-put', 'Annual-average put on the scale of a sovereign oil hedge: strike 70, 330 million barrels',
     black.Contract(daily(84, 252), 100, Q(4, 25), rate=Q(4, 100)), 70, 'put', 'USD per barrel', Q(1, 100), 330_000_000),
    ('twelve-monthly-95', 'Twelve monthly fixings over one year, call struck at 95 (the Black face of Section 5)',
     black.Contract([Q(i, 12) for i in range(1, 13)], 100, Q(9, 200), carry=Q(1, 100), rate=Q(1, 100)), 95, 'call', 'price units', Q(1, 100), None),
    ('twelve-monthly-110', 'The same contract, call struck at 110',
     black.Contract([Q(i, 12) for i in range(1, 13)], 100, Q(9, 200), carry=Q(1, 100), rate=Q(1, 100)), 110, 'call', 'price units', Q(1, 100), None),
    ('starts-tomorrow', 'One year of daily fixings starting the next day: the unfavourable limit',
     black.Contract(daily(1, 252), 100, Q(1, 25), rate=Q(4, 100)), 100, 'call', 'price units', Q(1, 100), None),
]


def endpoints(x):
    """Exact rational endpoints of an Arb ball."""
    def exact(y):
        man, exp = y.man_exp()
        return Q(int(man)) * Q(2) ** int(exp)
    mid, rad = exact(x.mid()), exact(x.rad())
    return mid - rad, mid + rad


def outward(x, digits=DIGITS):
    """Decimal strings [lo, hi] that contain the ball, rounded outward."""
    lo, hi = endpoints(x)
    scale = 10 ** digits
    lo_i = (lo * scale).numerator // (lo * scale).denominator
    hi_i = -((-hi * scale).numerator // (-hi * scale).denominator)
    def text(k):
        sign = '-' if k < 0 else ''
        k = abs(k)
        return f'{sign}{k // scale}.{k % scale:0{digits}d}'
    return [text(lo_i), text(hi_i)]


def certify(bits=256):
    ops = black.BallOps(bits)
    rows = []
    for name, description, contract, strike, kind, unit, step, volume in CONTRACTS:
        bounds = black.kink_bounds(ops, contract, strike)
        best = bounds['log_form'].min(bounds['quadratic_form'])
        form = 'log' if float(bounds['log_form'].mid()) <= float(bounds['quadratic_form'].mid()) else 'quadratic'
        scale = bounds['scale_log'] if form == 'log' else bounds['scale_quadratic']
        proxy = black.proxy_value(ops, contract, strike, scale, kind)
        K = ops.num(strike)
        row = {
            'name': name, 'description': description, 'kind': kind, 'unit': unit,
            'inputs': {'spot': str(contract.spot), 'strike': str(Q(strike)), 'variance_rate': str(contract.variance),
                       'carry': str(contract.carry), 'rate': str(contract.rate), 'fixings': contract.n,
                       'first_fixing_years': str(contract.times[0]), 'last_fixing_years': str(contract.times[-1])},
            'proxy_value': outward(proxy),
            'bound_log_form': outward(bounds['log_form']),
            'bound_quadratic_form': outward(bounds['quadratic_form']),
            'bound_used': form,
            'scale': outward(scale),
            'price_interval': [outward(proxy)[0], outward(proxy + best)[1]],
            'bound_over_strike': outward(best / K, 15),
            'bound_in_quote_steps': outward(best / ops.num(step), 6),
            'quote_step': str(step),
        }
        if volume:
            row['volume'] = volume
            row['bound_times_volume'] = outward(best * volume, 2)
            row['proxy_value_times_volume'] = outward(proxy * volume, 2)
        rows.append((row, contract, strike, float(scale.mid())))
    return rows


def diagnostics(contract, strike, scale):
    paths = 1 << 20
    cost, se = black.simulated_cost(contract, strike, scale, paths=paths)
    return {'cubic_law_over_strike': black.cubic_law(contract),
            'first_order_bound': black.first_order_bound(contract),
            'simulated_cost': cost, 'simulated_cost_standard_error': se, 'paths': paths, 'seed': 20261113}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--check', type=Path, help='recompute the enclosures and compare with a saved result')
    args = ap.parse_args()
    rows = certify()
    if args.check:
        saved = {r['name']: r for r in json.loads(args.check.read_text(encoding='utf8'))['contracts']}
        keys = ('proxy_value', 'bound_log_form', 'bound_quadratic_form', 'scale', 'price_interval',
                'bound_over_strike', 'bound_in_quote_steps')
        for row, *_ in rows:
            for key in keys:
                new, old = [Q(x) for x in row[key]], [Q(x) for x in saved[row['name']][key]]
                assert max(new[0], old[0]) <= min(new[1], old[1]), (row['name'], key)
            assert row['bound_used'] == saved[row['name']]['bound_used'], row['name']
        print(json.dumps({'status': 'PASS', 'contracts': len(rows),
                          'comparison': 'every recomputed enclosure meets the saved one'}))
        return
    out = []
    for row, contract, strike, scale in rows:
        row['binary64_diagnostics'] = diagnostics(contract, strike, scale)
        out.append(row)
    record = {
        'status': 'BLACK_MODEL_PRICE_INTERVALS',
        'arithmetic': 'Arb ball arithmetic at 256 bits; decimal endpoints rounded outward',
        'statement': 'Under Black\'s model with the stated inputs, each price lies in price_interval.',
        'diagnostics_are_not_proofs': True,
        'contracts': out,
    }
    text = json.dumps(record, indent=1) + '\n'
    if args.output:
        args.output.write_text(text, encoding='utf8', newline='\n')
    for row in out:
        d = row['binary64_diagnostics']
        print(f"{row['name']:20s} L={row['proxy_value'][0][:14]:>16s}  bound={float(row['price_interval'][1]) - float(row['price_interval'][0]):.3e}"
              f" ({row['bound_used']:9s}) steps={float(row['bound_in_quote_steps'][1]):9.4f}  cost~{d['simulated_cost']:.3e}"
              f"  first-order={d['first_order_bound']:.3e}  law*K={d['cubic_law_over_strike'] * float(Q(row['inputs']['strike'])):.3e}")


if __name__ == '__main__':
    main()
