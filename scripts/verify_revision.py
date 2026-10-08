"""Verify the frozen revision bytes and exact price-unit ledger, offline.

Saved-result verification is distinct from fresh interval-kernel execution.
Commands for the latter are in code/revision/README.md.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json,zipfile,subprocess,sys,tempfile,re

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
    second=ROOT/'code/revision/round2/results'
    point=json.loads((second/'point-v004-result.json').read_text(encoding='utf8'))
    assert point['status']=='COMPLETE_NEW_STOCHASTIC_HESTON_POINT_CERTIFICATE'
    assert point['input']['theta']==['3','9/200','23/100','-11/20','1/25']
    row=point['six_component_exact_width_ledger']
    lo,hi=map(F,point['principal_bias_Q_minus_P']['exact_interval'])
    assert lo<=hi and hi-lo==F(row['interval_width']['exact_rational'])
    assert len(row['components'])==6
    assert sum(F(x['exact_rational']) for x in row['components'].values())==hi-lo
    assert row['passes_original_0025_absolute_target']
    # Extract, hash, and replay the completed second point, including each saved
    # moment node, frequency, error contribution and parameter-source change.
    replay_parent=ROOT/'code/runs'
    replay_parent.mkdir(parents=True,exist_ok=True)
    dest=Path(tempfile.mkdtemp(prefix='r2-',dir=replay_parent))
    assert dest.resolve().is_relative_to(replay_parent.resolve())
    replayed=subprocess.run([sys.executable,str(ROOT/'code/revision/round2/replay_point.py'),
        '--archive',str(second/'evidence-point-v004.zip'),
        '--receipt',str(second/'archive-receipt.json'),
        '--directory',str(dest/'x'),'--output',str(dest/'replay.json')],
        capture_output=True,text=True)
    if replayed.returncode:
        raise RuntimeError('Second-point saved-result replay failed: '+replayed.stderr)
    replay=json.loads((dest/'replay.json').read_text(encoding='utf8'))
    assert replay['status']=='FROZEN_SECOND_POINT_STDLIB_READBACK_PASS'
    coupled=json.loads((second/'coupling-v004-result.json').read_text(encoding='utf8'))
    assert coupled['status']=='CLOSED_LOGNORMAL_COUPLING_REMAINDER_ENCLOSURE_COMPLETE'
    assert coupled['scope']['xi']=='0' and coupled['scope']['v0']=='1/25'
    assert coupled['source_sha256']==hashlib.sha256((ROOT/'code/revision/round2_coupling_example.py').read_bytes()).hexdigest()
    assert [r['precision_bits'] for r in coupled['precision_runs']]==[384,512]
    for run in coupled['precision_runs']:
        r=run['results']
        dl,du=map(F,r['direct_nonlinear_width']['exact_interval'])
        sl,su=map(F,r['separate_law_nonlinear_width']['exact_interval'])
        assert 0<=dl<=du<sl<=su
        assert F(r['width_ratio_direct_over_separate']['exact_interval'][1])<F('0.005731')
        assert r['strict_improvement_proved_by_disjoint_width_bounds']
        assert run['closed_pair_moment_identity_checks']==459
    receipt=json.loads((ROOT/'docs/revision-round2/coupling-evidence-receipt.json').read_text(encoding='utf8'))
    for r in receipt['files']:
        assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
    # Historical export/parser evidence remains meaningful without publishing
    # the former PDF. Check the recorded arguments and their unchanged sources;
    # this is not a new PDF export check or a fresh kernel calculation.
    commands=json.loads((ROOT/'code/verification/exported-command-check.json').read_text(encoding='utf8'))
    assert commands['status']=='PASS_EXPORTED_PDF_COMMANDS_AND_REAL_ARGUMENT_PARSER'
    assert re.fullmatch('[0-9a-f]{64}',commands['pdf_sha256'])
    assert commands['parsed_arguments']=={'modules':['asian'],'independent':True,'run_placeholder':'code/runs/run-ID'}
    prefix='./.venv/Scripts/python.exe '
    assert commands['copied_commands']==[prefix+'code/run.py verify',prefix+'code/run.py run --module asian --independent',prefix+'code/run.py check --run code/runs/run-ID']
    assert commands['original_runner_sha256']==hashlib.sha256((ROOT/'code/run.py').read_bytes()).hexdigest()
    expected=[('code/revision/round2/asian_parameter_point.py','prepare --directory new-point',{'mode':'prepare','directory':'new-point'}),
              ('code/revision/round2/asian_parameter_point.py','run --directory new-point',{'mode':'run','directory':'new-point'}),
              ('code/revision/round2_coupling_example.py','--output coupling.json',{'output':'coupling.json'})]
    assert len(commands['additional_actual_source_parser_checks'])==len(expected)
    for entry,(path,arguments,parsed) in zip(commands['additional_actual_source_parser_checks'],expected):
        assert entry['command']==prefix+path+' '+arguments and entry['arguments']==parsed
        assert entry['source_sha256']==hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    print(json.dumps(dict(status='PASS_FROZEN_REVISION_AND_EXACT_LEDGER',frozen_files=len(m['files']),unchanged_baseline_files=len(baseline['files']),complete_step_certificates=complete,analytical_guard_failures=1,posterior_grid_rows=len(grids),complete_second_point_certificate=True,second_point_weighted_node_checks=replay['weighted_node_exact_checks'],second_point_frequency_checks=replay['frequency_exact_interval_overlap_checks'],deterministic_coupling_precisions=2,saved_parser_result_checked=True,scope='Byte identity, exact saved mathematical ledger and historical parser-result/source binding. No public PDF, fresh kernel execution or new proof verification is required.')))
if __name__=='__main__':main()
