"""Closed Gaussian-moment enclosure of an Appendix-H coupling bound.

Scope: xi=0, v0=1/25, h=1/768, twelve monthly fixings, call spread 95/110.
No Monte Carlo, no signed Asian coefficient integration, no full price enclosure.
This isolated example does not alter any original numerical kernel or result.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse, ctypes, hashlib, importlib.util, json, sys, time

CODE = Path(__file__).resolve().parents[1]
HELPER = CODE / 'core' / 'resource_limits.py'
sp = importlib.util.spec_from_file_location('coupling_limits', HELPER)
lim = importlib.util.module_from_spec(sp)
sp.loader.exec_module(lim)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(output):
    assert not output.exists(), 'Keep completed evidence immutable.'
    assert sys.version_info[:2] == (3, 12) and not sys.flags.optimize
    from flint import arb, fmpq, ctx, __version__
    assert __version__ == '0.8.0'
    mem = lim.MEMORY()
    mem.length = ctypes.sizeof(mem)
    assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    assert min(mem.available_commit, mem.available_physical) >= 512 << 20
    lim.hard_job()
    ctx.threads = 1
    start = time.perf_counter()
    source_hash = sha(__file__)

    def ar(x):
        x = F(x)
        return arb(fmpq(x.numerator, x.denominator))

    def lo(x): return F(str(x.lower().fmpq()))
    def hi(x): return F(str(x.upper().fmpq()))
    def span(l, u):
        assert l <= u
        return {'exact_interval': [str(l), str(u)],
                'outward24': lim.decimal_enclosure(l, u)}
    def rec(x): return span(lo(x), hi(x))
    def nonnegative(x):
        assert hi(x) >= 0
        return span(max(F(0), lo(x)), hi(x))

    precision_runs = []
    for bits in (384, 512):
        ctx.prec = bits
        n = 12
        h = ar(F(1, 768))
        k = ar(3)
        vb = ar(F(9, 200))
        v0 = ar(F(1, 25))
        r = ar(F(1, 100))
        c = ar(F(1254433, 1250000))
        S0 = ar(100)
        eta = 1 - k * h
        assert eta > 0
        models = {}
        for name in ('P', 'Q'):
            cumulative = []
            for j in range(n + 1):
                t = ar(F(j, n))
                decay = (-k * t).exp() if name == 'P' else eta ** (64 * j)
                cumulative.append(vb * t + (v0 - vb) * (1 - decay) / k)
            inc = [cumulative[j] - cumulative[j - 1] for j in range(1, n + 1)]
            assert all(x > 0 for x in inc)
            roots = [x.sqrt() for x in inc]
            log_means = [r * ar(F(j, n)) - cumulative[j] / 2 for j in range(1, n + 1)]
            # The first normal has been integrated conditionally. There remain
            # eleven normals, with row i using normals 2,...,i+1.
            vectors = [[roots[j] if j <= i else arb(0) for j in range(1, n)]
                       for i in range(n)]
            gm = sum(log_means, arb(0)) / n
            gv = [sum(row[j] for row in vectors) / n for j in range(n - 1)]
            models[name] = {'cum': cumulative, 'inc': inc, 'roots': roots,
                            'means': log_means, 'vectors': vectors,
                            'gmean': gm, 'gvector': gv, 'sigma': roots[0]}

        def pair(m1, v1, m2, v2):
            # E[100 exp(m1+v1.Z) * 100 exp(m2+v2.Z)] exactly.
            return S0 * S0 * (m1 + m2 + sum((x + y) ** 2 for x, y in zip(v1, v2)) / 2).exp()

        def pair_cov(m1, v1, m2, v2):
            # Separate variance/covariance form of the same closed moment.
            vleft = sum(x * x for x in v1)
            vright = sum(y * y for y in v2)
            cov = sum(x * y for x, y in zip(v1, v2))
            return S0 * S0 * (m1 + m2 + (vleft + vright) / 2 + cov).exp()

        moment_checks = 0
        def checked(m1, v1, m2, v2):
            nonlocal moment_checks
            x = pair(m1, v1, m2, v2)
            y = pair_cov(m1, v1, m2, v2)
            assert max(lo(x), lo(y)) <= min(hi(x), hi(y))
            moment_checks += 1
            return x

        aa = {}
        ag = {}
        gg = {}
        residual = {}
        for name, md in models.items():
            aa[name] = sum(checked(md['means'][i], md['vectors'][i],
                                   md['means'][j], md['vectors'][j])
                           for i in range(n) for j in range(n)) / (n * n)
            ag[name] = sum(checked(md['means'][i], md['vectors'][i], md['gmean'], md['gvector'])
                           for i in range(n)) / n
            gg[name] = checked(md['gmean'], md['gvector'], md['gmean'], md['gvector'])
            residual[name] = aa[name] - 2 * c * ag[name] + c * c * gg[name]
            assert residual[name] > 0

        mp, mq = models['P'], models['Q']
        across = sum(checked(mp['means'][i], mp['vectors'][i], mq['means'][j], mq['vectors'][j])
                     for i in range(n) for j in range(n)) / (n * n)
        gcross = checked(mp['gmean'], mp['gvector'], mq['gmean'], mq['gvector'])
        da2 = aa['P'] + aa['Q'] - 2 * across
        db2 = c * c * (gg['P'] + gg['Q'] - 2 * gcross)
        assert da2 > 0 and db2 > 0
        z2_upper = ar(hi(residual['P'] + residual['Q']))
        da_upper = ar(hi(da2)).sqrt()
        db_upper = ar(hi(db2)).sqrt()
        sigma_minus = ar(min(lo(mp['sigma']), lo(mq['sigma'])))
        sigma_plus = ar(max(hi(mp['sigma']), hi(mq['sigma'])))
        sigma_change = ar(hi(abs(mq['sigma'] - mp['sigma'])))
        assert sigma_minus > 0
        common_M = (2 * sigma_plus * sigma_plus).exp() / (sigma_minus * (2 * arb.pi()).sqrt())
        common_N = ((2 * sigma_plus * sigma_plus).exp() *
                    (1 + 4 / ar(1).exp() + 8 * sigma_plus * sigma_plus) /
                    (sigma_minus * sigma_minus * (2 * arb.pi()).sqrt()))
        # max(delta_P^2,delta_Q^2) <= delta_P^2+delta_Q^2,
        # followed by Cauchy--Schwarz for each coupled displacement.
        common_B = (common_M * z2_upper.sqrt() * (da_upper + db_upper) +
                    common_N * z2_upper * sigma_change / 2)
        B95 = common_B / 95
        B110 = common_B / 110
        discount = (-r).exp()
        direct_price_radius = discount * (B95 + B110)
        Dp = (2 * mp['sigma'] ** 2).exp() * residual['P'] / mp['sigma']
        Dq = (2 * mq['sigma'] ** 2).exp() * residual['Q'] / mq['sigma']
        gamma = discount / (2 * (2 * arb.pi()).sqrt())
        separate_lower = -gamma * (Dq / 110 + Dp / 95)
        separate_upper = gamma * (Dq / 95 + Dp / 110)
        separate_width = separate_upper - separate_lower
        direct_width = 2 * direct_price_radius
        assert hi(direct_width) < lo(separate_width), 'Do not claim an improvement without outward proof.'
        reduction = direct_width / separate_width
        recs = {
            'sigma_P': rec(mp['sigma']), 'sigma_Q': rec(mq['sigma']),
            'conditional_residual_second_moments': {name: rec(residual[name]) for name in ('P', 'Q')},
            'coupled_a_displacement_second_moment': nonnegative(da2),
            'coupled_cg_displacement_second_moment': nonnegative(db2),
            'E_z_squared_upper': rec(z2_upper), 'sigma_change_upper': rec(sigma_change),
            'common_curvature_constant': rec(common_M), 'common_sigma_derivative_constant': rec(common_N),
            'E_Xi_95_enclosure': span(F(0), hi(B95)),
            'E_Xi_110_enclosure': span(F(0), hi(B110)),
            'direct_discounted_nonlinear_interval': span(-hi(direct_price_radius), hi(direct_price_radius)),
            'direct_nonlinear_width': rec(direct_width),
            'separate_law_nonlinear_interval': span(lo(separate_lower), hi(separate_upper)),
            'separate_law_nonlinear_width': rec(separate_width),
            'width_ratio_direct_over_separate': rec(reduction),
            'strict_improvement_proved_by_disjoint_width_bounds': True,
        }
        precision_runs.append({'precision_bits': bits, 'closed_pair_moment_identity_checks': moment_checks,
                               'results': recs})
        assert time.perf_counter() - start < 25

    # The conservative upper endpoints fed into the bound vary with precision;
    # the resulting bounds need not overlap. Check their convergence in value.
    # This is a computation check, not an independent proof.
    for key in ('direct_nonlinear_width', 'separate_law_nonlinear_width', 'width_ratio_direct_over_separate'):
        a = precision_runs[0]['results'][key]
        b = precision_runs[1]['results'][key]
        al, au = map(F, a['exact_interval'])
        bl, bu = map(F, b['exact_interval'])
        assert abs(au - bu) < F(1, 10 ** 90)
    assert sha(__file__) == source_hash
    result = {
        'status': 'CLOSED_LOGNORMAL_COUPLING_REMAINDER_ENCLOSURE_COMPLETE',
        'scope': {'kappa': '3', 'vbar': '9/200', 'xi': '0', 'v0': '1/25',
                  'h': '1/768', 'S0': '100', 'r': '1/100', 'fixings': 12,
                  'strikes': [95, 110], 'c': '1254433/1250000'},
        'construction': 'Common twelve standard normals; first normal integrated for smoothing, remaining eleven used in coupled conditional a and g.',
        'method': 'Finite closed Gaussian exponential moments plus validated Cauchy--Schwarz inequalities. No statistical estimate.',
        'source_sha256': source_hash, 'resource_helper_sha256': sha(HELPER),
        'python_version': sys.version, 'python_flint_version': __version__,
        'precision_runs': precision_runs, 'elapsed_seconds': time.perf_counter() - start,
        'threads': 1, 'memory_limit_MiB': 256,
        'no_claim': ['No positive-xi coupling certificate.', 'No full price or signed Asian beta is evaluated.',
                     'The E_Xi enclosures bound the expectation via inequalities rather than integrating the max function exactly.',
                     'Two precisions and two Gaussian-moment expressions share the analytical proof and Arb.'],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    concise = {k: precision_runs[-1]['results'][k]['outward24'] for k in
               ('E_Xi_95_enclosure', 'E_Xi_110_enclosure', 'direct_nonlinear_width',
                'separate_law_nonlinear_width', 'width_ratio_direct_over_separate')}
    print(json.dumps({'status': result['status'], 'results': concise, 'seconds': result['elapsed_seconds']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.output.resolve())
