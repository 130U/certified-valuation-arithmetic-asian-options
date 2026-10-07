"""Verify the frozen revision bytes and exact price-unit ledger, offline.

Saved-result verification is distinct from fresh interval-kernel execution.
Commands for the latter are in code/revision/README.md.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',type=Path,default=ROOT/'REVISION-MANIFEST.json')
    a=ap.parse_args();m=json.loads(a.manifest.read_text(encoding='utf8'))
    for name,row in m['files'].items():
        p=ROOT/name
        assert p.is_file() and p.stat().st_size==row['bytes'],name
        assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],name
    baseline=json.loads((ROOT/'code/MANIFEST.json').read_text(encoding='utf8'))
    for name,row in baseline['files'].items():
        p=ROOT/'code'/name
        assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],name
    ledger=json.loads((ROOT/'code/revision/results/revision-summary.json').read_text(encoding='utf8'))
    assert ledger['status']=='EXACT_RATIONAL_BUDGET_RECONCILIATION_PASS'
    assert [r['h'] for r in ledger['step_table']]==['1/192','1/384','1/768','1/1536']
    complete=0
    for r in ledger['step_table']:
        if r['status']=='NO_CERTIFICATE_ANALYTICAL_GUARD_FAILED':
            assert r['h']=='1/192' and F(r['projection_beta'])<=8
            continue
        assert r['status']=='COMPLETE_INDEPENDENTLY_CHECKED_ENCLOSURE'
        lo,hi=map(F,r['bias_Q_minus_P']['exact_interval'])
        assert lo<=hi and hi-lo==F(r['interval_width']['exact_rational'])
        assert sum(F(x['exact_rational']) for x in r['components'].values())==hi-lo
        complete+=1
    assert complete==3
    grids=ledger['posterior_mesh_summary']['table']
    assert len(grids)==6
    with zipfile.ZipFile(ROOT/'code/revision/results/evidence.zip') as archive:
        for r in grids:
            cells=r['cells'];assert cells in [4096,8192,16384] and r['quotes'] in [1,9]
            directory='base-run' if cells==4096 else f'posterior-{cells}'
            source=json.loads(archive.read(f'execution/{directory}/work/core/posterior-{cells}-result.json'))
            common=list(map(F,source['Asian_positive_xi_same_parameter_PQ_bound']['exact_interval']))
            lip=list(map(F,source['Asian_zero_xi_reference_P_parameter_Lipschitz_bound']['exact_interval']))
            transport=source['transports']['d1' if r['quotes']==1 else 'd9']
            delta=F(transport['all_p_parameter_Winfinity_bound'])
            total=list(map(F,transport['all_target_quantile_levels_absolute_PQ_difference_bound']['exact_interval']))
            assert F(r['price_bound_upper_exact'])==total[1]
            assert F(r['common_fee_upper_exact'])==common[1]
            assert F(r['mesh_transfer_fee_upper_exact'])==lip[1]*delta
            # Independent Arb operations round interval endpoints separately.
            # Exact endpoint sums need not be identical. Check saved interval
            # consistency using rational overlap, without numerical tolerance.
            assert common[0]+lip[0]*delta<=total[1]
            assert total[0]<=common[1]+lip[1]*delta
    for quotes in [1,9]:
        rows=[r for r in grids if r['quotes']==quotes]
        assert F(rows[2]['price_bound_upper_exact'])<F(rows[1]['price_bound_upper_exact'])<F(rows[0]['price_bound_upper_exact'])
    beta=ledger['Asian_beta_score_bound_summary']
    for run in beta['runs']:
        assert len(run['rows'])==4
        for r in run['rows']:
            l,u=map(F,r['beta_Asian_signed_enclosure']['exact_interval'])
            assert l<=0<=u and u==F(r['absolute_score_bound']['exact_interval'][1]) and l==-u
    for name in ['path-diagnostics.json','asian-beta-diagnostic.json']:
        d=json.loads((ROOT/'code/revision/results'/name).read_text(encoding='utf8'))
        assert 'DIAGNOSTIC' in d['status']
    print(json.dumps(dict(status='PASS_FROZEN_REVISION_AND_EXACT_LEDGER',frozen_files=len(m['files']),unchanged_baseline_files=len(baseline['files']),complete_step_certificates=complete,analytical_guard_failures=1,posterior_grid_rows=len(grids),scope='Byte identity and exact saved mathematical ledger. Fresh kernel execution and mathematical proofs are separate checks.')))
if __name__=='__main__':main()
