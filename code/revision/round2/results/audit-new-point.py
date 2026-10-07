"""Independent finite source and exact-constant audit for v0=1/25 copies.

This checks preparation and, when present, completed-result identities. It never
runs a numerical pricing kernel. A preparation pass is not a price certificate.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib, json, math, re

BASE = Path(__file__).resolve().parents[1]
CODE = BASE / 'repository' / 'code'
RUN = CODE / 'revision' / 'round2' / 'runs' / 'point-v004'
OUT = Path(__file__).with_name('new-point-independent-receipt.json')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text(encoding='utf8'))


def replace_exact(text, before, after, count=1):
    assert text.count(before) == count, (before, text.count(before), count)
    return text.replace(before, after)


def main():
    h = F(1, 768)
    alpha = F(529, 20000)
    rx = F(-253, 2000)
    k = F(3)
    d = F(27, 200)
    v0 = F(1, 25)
    betaW = min(s * (1 - (k - 2 * rx) * h) - alpha * s * s - h * h
                for s in (F(12), F(12) + 512 * h))
    betaL = min(s * (1 - (k - rx) * h) - alpha * s * s - F(3, 8) * h * h
                for s in (F(12), F(12) + 1024 * h))
    betaUI = 12 * (1 - (k - F(5, 2) * rx) * h) - 144 * alpha - F(15, 8) * h * h
    generator = [16 * alpha - 4 * k + 4 * rx * p + (p * p - p) / 2
                 for p in (F(-5, 4), F(5, 2))]
    assert betaW > 8 and betaL > 8 and betaUI > 0 and max(generator) < 0
    # Rational Taylor lower bound exp(131/50) >= sum_{j=0}^6 x^j/j!.
    # It certifies 4d+5r/2+exp(-12d-1)/3 < .6 without relying on Arb.
    x = 12 * d + 1
    lower_exp = sum(x ** j / math.factorial(j) for j in range(7))
    growth_upper = 4 * d + F(1, 40) + 1 / (3 * lower_exp)
    assert growth_upper < F(3, 5)
    assert F(3, 5) + 4 * v0 == F(19, 25) < F(39, 50)
    assert h * v0 == F(1, 19200)
    pre = read(RUN / 'preflight.json')
    assert pre['theta'] == ['3', '9/200', '23/100', '-11/20', '1/25']
    for key, value in [('weighted_projection_beta_exact', betaW), ('linear_projection_beta_exact', betaL),
                       ('UI_beta_exact', betaUI)]:
        assert F(pre[key]) == value
    assert list(map(F, pre['continuous_generator_endpoint_coefficients_exact'])) == generator

    files = []
    core = RUN / 'work' / 'core'
    receipt = read(RUN / 'receipt.json')
    journal = {row['file']: row for row in receipt['source_patches']}
    for name in ('asian-remainder-certificate.py', 'asian-linear-certificate.py',
                 'check-asian-remainder.py', 'check-asian-linear.py'):
        oldpath = CODE / 'core' / name
        newpath = core / name
        s = oldpath.read_text(encoding='utf8')
        tag = 'v' if name == 'check-asian-remainder.py' else 'v0'
        s = replace_exact(s, tag + '=ar(F(9,200))', tag + '=ar(F(1,25))')
        if name == 'asian-remainder-certificate.py':
            s = replace_exact(s, "'theta':['3','9/200','23/100','-11/20','9/200']",
                              "'theta':['3','9/200','23/100','-11/20','1/25']")
            s = replace_exact(s, 'assert high(radius)<F(11,1000)',
                              "result['original_remainder_radius_target_pass']=high(radius)<F(11,1000)")
        if name == 'check-asian-remainder.py':
            s = replace_exact(s, 'assert radius<ar(F(11,1000))',
                              'original_remainder_radius_target_pass=radius<ar(F(11,1000))')
            s = replace_exact(s, "'unpaid':['linearized thirteen-profile price difference and all its fees'],",
                              "'original_remainder_radius_target_pass':original_remainder_radius_target_pass,\n        'unpaid':['linearized thirteen-profile price difference and all its fees'],")
        if name == 'check-asian-linear.py':
            s = replace_exact(s, 'dbe13d37a5ad6db8dcda674cc1bddae7b6049329de2cc23e8b115af10409c5a8',
                              sha(core / 'asian-linear-certificate.py'))
            s = replace_exact(s, 'assert max(abs(bl),abs(bu))<F(1,40)',
                              'original_price_absolute_target_pass=max(abs(bl),abs(bu))<F(1,40)')
            s = replace_exact(s, "'original_theta_star_Asian_pass_0025':True",
                              "'original_theta_star_Asian_pass_0025':original_price_absolute_target_pass")
            s = replace_exact(s, "'scope':'Original theta-star parameter point, original payoff and positive-part Euler scheme.'",
                              "'scope':'New point v0=1/25; original Asian payoff and positive-part Euler scheme, all other parameters unchanged.'")
        if 'remainder' in name:
            s = replace_exact(s, '<55', '<110')
            s = replace_exact(s, 'timeout=60', 'timeout=120')
            s = replace_exact(s, "'hard_wall_seconds':60", "'hard_wall_seconds':120")
        else:
            s = replace_exact(s, '<170', '<340')
            if name == 'asian-linear-certificate.py':
                s = replace_exact(s, "prior['full_linear_time_estimate']<140", "prior['full_linear_time_estimate']<280")
                s = replace_exact(s, "'hard_wall_seconds':30 if pilot else 180", "'hard_wall_seconds':30 if pilot else 360")
            else:
                s = replace_exact(s, "'hard_wall_seconds':180", "'hard_wall_seconds':360")
                s = replace_exact(s, 'timeout=180', 'timeout=360')
        actual = newpath.read_text(encoding='utf8')
        assert s == actual, 'An unreviewed source change exists: ' + name
        assert sha(oldpath) == journal[name]['original_sha256']
        assert sha(newpath) == journal[name]['executed_sha256']
        files.append({'file': name, 'baseline_sha256': sha(oldpath), 'executed_sha256': sha(newpath),
                      'source_equals_exact_reviewed_transform': True})
    assert '204cdd128f4b706999d14d581830cf0a35014c1e488cc715a1a821adad90a3ea' == sha(core / 'asian-linear-certificate.py')
    assert sha(core / 'asian-linear-certificate.py') in (core / 'check-asian-linear.py').read_text(encoding='utf8')
    result = {
        'status': 'ANALYTICAL_AND_SOURCE_PREFLIGHT_PASS_NOT_A_PRICE_CERTIFICATE',
        'scope': pre['theta'], 'review_script_sha256': sha(__file__),
        'preflight_sha256': sha(RUN / 'preflight.json'), 'source_files': files,
        'exact_independently_recomputed_constants': {'beta_weighted': str(betaW), 'beta_linear': str(betaL),
            'beta_UI': str(betaUI), 'continuous_generator_endpoint_values': list(map(str, generator)),
            'rational_growth_upper_by_Taylor': str(growth_upper), 'new_moment_exponent': '19/25',
            'retained_conservative_moment_exponent': '39/50', 'first_month_discrete_I_floor': '1/19200'},
        'current_execution_receipt_status': receipt['status'],
        'full_price_execution_completed': receipt['status'] == 'COMPLETE',
        'explanation': 'Every analytical guard is retained. The source changes are the actual v0 parameter, input/scope metadata, old numerical targets as flags, source pin and declared wall-time allowances.',
    }
    if receipt['status'] == 'COMPLETE':
        assert len(receipt['jobs']) == 5 and all(row['status'] == 'COMPLETE' for row in receipt['jobs'])
        for row in receipt['jobs']:
            assert sha(core / row['file']) == row['source_sha256']
            assert sha(core / row['result']) == row['result_sha256']
        iw = read(core / 'check-asian-remainder-result.json')
        il = read(core / 'check-asian-linear-result.json')
        assert iw['P_all_node_interval_overlap_checks'] == 257
        assert iw['Q_all_node_independent_interval_containment_checks'] == 129
        assert il['counts']['Q_layers'] == 6399744
        assert il['counts']['P_path_guards'] == 799968
        assert il['counts']['frequency_real_interval_overlaps'] == 1923
        assert il['author_source_sha256'] == sha(core / 'asian-linear-certificate.py')
        assert il['author_result_sha256'] == sha(core / 'asian-linear-result.json')
        result.update(status='ANALYTICAL_SOURCE_AND_COMPLETED_RESULT_READBACK_PASS',
                      completed_receipt_sha256=sha(RUN / 'receipt.json'), independent_weighted_nodes={'P': 257, 'Q': 129},
                      independent_linear_counts=il['counts'])
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'status': result['status'], 'execution_status': receipt['status'], 'source_files': len(files)}))


if __name__ == '__main__':
    main()
