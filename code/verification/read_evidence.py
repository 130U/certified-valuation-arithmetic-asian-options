"""Verify saved execution identities and exact arithmetic without pricing reruns."""
from pathlib import Path, PurePosixPath
from fractions import Fraction as F
import argparse, hashlib, importlib.util, json, os, sys, zipfile

CODE = Path(__file__).resolve().parents[1]
def read(p): return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, value):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(value, indent=2)+'\n', encoding='utf8')
def module(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj
def interval(v):
    lo,hi=map(F,v['exact_interval']);assert lo<=hi;return lo,hi
def overlap(a,b):
    lo,hi=interval(a);ll,uu=interval(b);assert max(lo,ll)<=min(hi,uu)
def without_locations(x):
    if isinstance(x,dict):
        return {k:without_locations(v) for k,v in x.items() if k not in
                ('core_path','execution_receipt','execution_result','receipt','reader_sha256')}
    if isinstance(x,list):return [without_locations(v) for v in x]
    return x

def verify_inventory(directory, receipt):
    assert sha(directory/'inventory.json')==receipt['inventory_sha256']
    inv=read(directory/'inventory.json')
    assert len(inv['files'])==receipt['file_count']
    for name,item in inv['files'].items():
        path=directory.joinpath(*PurePosixPath(name).parts)
        assert path.is_file() and path.stat().st_size==item['bytes'] and sha(path)==item['sha256'],name
    for source_hash,name in inv['source_objects'].items():assert inv['files'][name]['sha256']==source_hash
    return inv

def extract_archive(archive,receipt,directory):
    assert sha(archive)==receipt['archive_sha256']
    assert not directory.exists(),'Use a fresh extraction directory.'
    directory.mkdir(parents=True)
    with zipfile.ZipFile(archive) as bundle:
        names=bundle.namelist();assert len(names)==len(set(names))
        for name in names:
            path=PurePosixPath(name);info=bundle.getinfo(name)
            assert not path.is_absolute() and '..' not in path.parts and '\\' not in name and ':' not in name
            assert not info.is_dir() and (info.external_attr>>16)&0o170000!=0o120000
            assert directory.joinpath(*path.parts).resolve().is_relative_to(directory.resolve())
        bundle.extractall(directory)
    inv=verify_inventory(directory,receipt)
    assert set(names)=={'inventory.json'}|set(inv['files'])
    return inv

def verify_jobs(run, complete=True):
    r=read(run/'receipt.json');core=run/'work'/'core'
    assert r['status']==('COMPLETE' if complete else 'STOPPED')
    for item in r.get('source_patches',[]):
        name=item.get('file',item.get('source'))
        assert sha(core/name)==item['executed_sha256']
        assert sha(CODE/'core'/name)==item['original_sha256']
    for job in r['jobs']:
        name=job.get('file',job.get('source'));source=core/name
        if 'source_sha256' in job:assert sha(source)==job['source_sha256']
        if not complete:continue
        assert job['returncode']==0 and not job.get('timed_out',False) and job.get('reaped',True)
        result=core/job['result'];assert sha(result)==job['result_sha256']
        value=read(result);assert value['source_sha256']==sha(source)
    if 'preflight_sha256' in r:assert sha(run/'preflight.json')==r['preflight_sha256']
    if 'scope_sha256' in r:assert sha(run/'work'/'SCOPE.md')==r['scope_sha256']
    if 'resource_helper_sha256' in r:assert sha(core/'resource_limits.py')==r['resource_helper_sha256']
    return r

def verify_asian(run, steps):
    r=verify_jobs(run);assert len(r['jobs'])==5
    core=run/'work'/'core'
    a=read(core/'asian-linear-result.json');w=read(core/'asian-remainder-result.json')
    c=read(core/'check-asian-linear-result.json');cw=read(core/'check-asian-remainder-result.json')
    assert F(w['h'])==F(1,steps)
    assert a['precision_bits']==w['precision_bits']==256 and c['precision_bits']==cw['precision_bits']==384
    assert a['counts']=={'Q_layers':8333*steps,'P_full_path_branch_guards':799968,'profiles':8333}
    assert c['counts']=={'Q_layers':8333*steps,'P_path_guards':799968,'frequency_real_interval_overlaps':1923}
    assert w['counts']=={'Q_steps':3185*steps//3,'P_month_blocks':24388}
    assert cw['counts']=={'P_blocks':24388,'Q_steps':3185*steps//3}
    assert a['weighted_square_result_sha256']==sha(core/'asian-remainder-result.json')
    for result,stem in ((c,'asian-linear'),(cw,'asian-remainder')):
        assert result['author_source_sha256']==sha(core/(stem+'-certificate.py'))
        assert result['author_result_sha256']==sha(core/(stem+'-result.json'))
    nodes=frequencies=fees=0
    for key,count in (('all_points_P',257),('all_points_Q',129)):
        assert len(w[key])==len(cw[key])==count
        for x,y in zip(w[key],cw[key]):
            if key.endswith('P'):overlap(x,y)
            else:
                lo,hi=interval(x);ll,uu=interval(y);assert lo<=ll<=uu<=hi
            nodes+=1
    assert len(a['frequency_rows'])==len(c['frequency_rows'])==641
    for i,(x,y) in enumerate(zip(a['frequency_rows'],c['frequency_rows'])):
        assert x['n']==y['n']==i
        for ka,kb in (('P_term','P_term'),('proxy_term','Q_proxy_term'),('coefficient_sum','coefficient_sum')):
            overlap(x[ka],y[kb]);frequencies+=1
    assert set(c['fees'])=={'projection_delta','projection_price_fee','Q_firstmonth_Laplace_upper',
                            'P_frequency_tail','Q_frequency_tail','one_law_alias','total_linear_bias_fee'}
    for key,value in c['fees'].items():overlap(a[key],value);fees+=1
    for key in ('linear_bias_finite','coefficient_abs_sum','true_original_Asian_bias','true_original_Asian_P','true_original_Asian_Q'):
        overlap(a[key],c[key])
    return {'weighted_node_exact_checks':nodes,'frequency_exact_interval_overlap_checks':frequencies,
            'linear_fee_exact_interval_overlap_checks':fees,'completed_jobs':len(r['jobs'])}

def verify_posterior(run,cells,base):
    r=verify_jobs(run);assert len(r['jobs'])==3
    assert r['baseline_run_receipt_sha256']==sha(base/'run-receipt.json')
    core=run/'work'/'core';runner=module('posterior_payload_reader',CODE/'run.py')
    a=runner.payload(read(core/f'posterior-{cells}-result.json'))
    b=runner.payload(read(core/f'posterior-compat-{cells}-result.json'))
    b['Asian_zero_xi_reference_P_parameter_Lipschitz_bound']=b.pop('Asian_P_parameter_Lipschitz_bound')
    a.pop('scheme',None);b.pop('scheme',None);assert a==b
    c=read(core/'check-posterior-result.json')
    assert c['status']=='INDEPENDENT_POSITIVE_XI_3D_POSTERIOR_AUDIT_PASS'
    return {'cells':cells,'completed_jobs':3,'all_principal_compatibility_mathematical_fields_equal':True}

def main(archive,receipt_path,directory,output):
    if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):
        raise RuntimeError('Optimized Python is prohibited; assertions enforce the certificate checks.')
    receipt=read(receipt_path);inv=extract_archive(archive,receipt,directory)
    execution=directory/'execution';base=execution/'base-run'
    runner=module('baseline_payload_reader',CODE/'run.py')
    baseline=runner.check_run(base);assert len(baseline['jobs'])==10
    grid=[]
    for n in (384,1536):grid.append({'steps':n,**verify_asian(execution/f'asian-{n}-enclosure',n)})
    stopped=verify_jobs(execution/'asian-192-failed',complete=False)
    assert F(stopped['analytical_projection_beta_expected'])<=8
    posterior=[verify_posterior(execution/f'posterior-{n}',n,base) for n in (8192,16384)]
    driver_checks=0
    for run_name in ('asian-192-failed','asian-384-enclosure','asian-1536-enclosure','posterior-8192','posterior-16384'):
        identifier=read(execution/run_name/'receipt.json')['script_sha256']
        assert sha(directory/inv['source_objects'][identifier])==identifier
        driver_checks+=1
    budget=module('exact_budget_reader',CODE/'verification'/'read_budget.py')
    budget.main(execution,base,directory/'step-grid-readback.json')
    ledger=read(directory/'step-grid-readback.json')
    assert without_locations(ledger)==without_locations(read(CODE/'results'/'step-grid.json'))
    assert without_locations(ledger['posterior_mesh_summary'])==without_locations(read(CODE/'results'/'posterior-grid.json'))
    assert ledger['Asian_beta_score_bound_summary']==read(CODE/'results'/'asian-beta-score-bounds.json')
    posterior_rows=ledger['posterior_mesh_summary']['table'];assert len(posterior_rows)==6
    assert {(r['cells'],r['quotes']) for r in posterior_rows}=={(n,q) for n in (4096,8192,16384) for q in (1,9)}
    for row in posterior_rows:
        cells=row['cells'];path=base if cells==4096 else execution/f'posterior-{cells}'
        value=read(path/'work'/'core'/f'posterior-{cells}-result.json')
        common=interval(value['Asian_positive_xi_same_parameter_PQ_bound'])
        lip=interval(value['Asian_zero_xi_reference_P_parameter_Lipschitz_bound'])
        transport=value['transports']['d1' if row['quotes']==1 else 'd9']
        delta=F(transport['all_p_parameter_Winfinity_bound'])
        total=interval(transport['all_target_quantile_levels_absolute_PQ_difference_bound'])
        assert F(row['price_bound_upper_exact'])==total[1]
        assert F(row['common_fee_upper_exact'])==common[1]
        assert F(row['mesh_transfer_fee_upper_exact'])==lip[1]*delta
        assert common[0]+lip[0]*delta<=total[1] and total[0]<=common[1]+lip[1]*delta
    for name in ('asian-beta-score-bounds.json','asian-beta-diagnostic.json','path-diagnostics.json'):
        identifier=read(CODE/'results'/name)['source_sha256']
        assert sha(directory/inv['source_objects'][identifier])==identifier
    point=module('parameter_point_readback',CODE/'verification'/'replay_point.py')
    point_result=point.main(directory,directory/'parameter-point-readback.json',verified_inventory=inv)
    result={'status':'PASS_EXECUTION_EVIDENCE_AND_EXACT_ARITHMETIC',
      'scope':'Saved-source/result consistency, exact interval comparisons, and ledger reconciliation. Pricing kernels are not rerun.',
      'archive_sha256':sha(archive),'inventory_sha256':sha(directory/'inventory.json'),'inventory_file_count':len(inv['files']),
      'baseline_jobs_exactly_checked':len(baseline['jobs']),'step_grid':grid,'analytical_h192_guard_retained':True,
      'saved_grid_driver_source_identities_checked':driver_checks,'diagnostic_source_identities_checked':3,
      'posterior_exact_transport_ledger_rows_checked':len(posterior_rows),
      'posterior_grids':posterior,'weighted_moment_node_checks':sum(x['moment_node_checks'] for x in ledger['weighted_moment_table']),
      'step_ledger_all_nonlocation_fields_equal':True,'parameter_point':point_result,'reader_sha256':sha(__file__)}
    write(output,result);print(json.dumps(result,indent=2));return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,default=CODE/'evidence'/'executions.zip')
    parser.add_argument('--receipt',type=Path,default=CODE/'evidence'/'receipt.json')
    parser.add_argument('--directory',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();main(args.archive.resolve(),args.receipt.resolve(),args.directory.resolve(),args.output.resolve())
