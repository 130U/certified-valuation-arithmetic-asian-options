"""Standard-library readback of the frozen second Heston point.

This verifies saved enclosures, source identities and exact ledger arithmetic.
It does not recompute the numerical pricing kernels or claim a second proof.
"""
from pathlib import Path, PurePosixPath
from fractions import Fraction as F
import argparse, hashlib, importlib.util, json, zipfile

def read(p): return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x): Path(p).write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def interval(v):
    l,u=map(F,v['exact_interval']);assert l<=u;return l,u
def overlap(a,b):
    al,au=interval(a);bl,bu=interval(b);assert max(al,bl)<=min(au,bu)
def without_paths(x):
    if isinstance(x,dict):return {k:without_paths(v) for k,v in x.items() if k not in ('core_path','execution_receipt')}
    if isinstance(x,list):return [without_paths(v) for v in x]
    return x

def main(archive,receipt,dest,out):
    frozen=read(receipt)
    assert frozen['archive_sha256']==sha(archive)
    assert not dest.exists(), 'Use a fresh extraction directory.'
    dest.mkdir(parents=True)
    with zipfile.ZipFile(archive) as z:
        names=z.namelist();assert len(names)==len(set(names))
        for name in names:
            p=PurePosixPath(name)
            assert not p.is_absolute() and '..' not in p.parts and '\\' not in name and ':' not in name
            info=z.getinfo(name);assert not info.is_dir() and (info.external_attr>>16)&0o170000!=0o120000
            target=dest.joinpath(*p.parts).resolve();assert target.is_relative_to(dest.resolve())
        z.extractall(dest)
    inventory=read(dest/'inventory.json')
    assert sha(dest/'inventory.json')==frozen['inventory_sha256']
    assert set(names)=={'inventory.json'}|set(inventory['files'])
    for name,item in inventory['files'].items():
        p=dest.joinpath(*PurePosixPath(name).parts)
        assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256']
    code=dest/'repository'/'code';run=code/'revision'/'round2'/'runs'/'point-v004';core=run/'work'/'core'
    r=read(run/'receipt.json');cap=read(run/'result-capsule.json')
    assert cap==read(code/'revision'/'round2'/'results'/'point-v004-result.json')
    assert r['status']=='COMPLETE' and len(r['jobs'])==5
    assert sha(run/'receipt.json')==cap['receipt_sha256']
    assert sha(run/'preflight.json')==cap['preflight_sha256']==r['preflight_sha256']
    assert sha(run/'work'/'SCOPE.md')==r['scope_sha256']
    assert sha(core/'resource_limits.py')==r['resource_helper_sha256']
    for job in r['jobs']:
        assert job['status']=='COMPLETE' and job['returncode']==0
        assert sha(core/job['file'])==job['source_sha256'] and sha(core/job['result'])==job['result_sha256']
    # Replay the separately authored exact-constant and literal-source audit.
    audit=module('frozen_round2_independent_audit',dest/'round2-theory'/'audit-new-point.py')
    saved_audit=read(dest/'round2-theory'/'new-point-independent-receipt.json')
    audit.OUT=dest/'replayed-independent-audit.json';audit.main()
    assert saved_audit==read(audit.OUT)
    # Rebuild the capsule using the archived generator and unchanged reader.
    generator=module('frozen_round2_generator',code/'revision'/'round2'/'asian_parameter_point.py')
    assert sha(generator.__file__)==cap['capsule_generator_sha256']==r['generator_sha256']
    rebuilt=dest/'replayed-result-capsule.json';generator.capsule(run,rebuilt)
    assert without_paths(read(rebuilt))==without_paths(cap)
    a=read(core/'asian-linear-result.json');w=read(core/'asian-remainder-result.json')
    c=read(core/'check-asian-linear-result.json');cw=read(core/'check-asian-remainder-result.json')
    assert a['precision_bits']==w['precision_bits']==256 and c['precision_bits']==cw['precision_bits']==384
    assert c['counts']=={'Q_layers':6399744,'P_path_guards':799968,'frequency_real_interval_overlaps':1923}
    assert a['counts']=={'Q_layers':6399744,'P_full_path_branch_guards':799968,'profiles':8333}
    assert w['counts']=={'Q_steps':815360,'P_month_blocks':24388}
    assert cw['counts']=={'P_blocks':24388,'Q_steps':815360}
    nodes=frequencies=fees=0
    for key,n in [('all_points_P',257),('all_points_Q',129)]:
        assert len(w[key])==len(cw[key])==n
        for principal,independent in zip(w[key],cw[key]):
            if key.endswith('P'):overlap(principal,independent)
            else:
                l,u=interval(principal);ll,uu=interval(independent);assert l<=ll<=uu<=u
            nodes+=1
    assert len(a['frequency_rows'])==len(c['frequency_rows'])==641
    for index,(principal,independent) in enumerate(zip(a['frequency_rows'],c['frequency_rows'])):
        assert principal['n']==independent['n']==index
        for pa,pb in [('P_term','P_term'),('proxy_term','Q_proxy_term'),('coefficient_sum','coefficient_sum')]:
            overlap(principal[pa],independent[pb]);frequencies+=1
    for key,value in c['fees'].items():overlap(a[key],value);fees+=1
    for key in ('linear_bias_finite','coefficient_abs_sum','true_original_Asian_bias','true_original_Asian_P','true_original_Asian_Q'):
        overlap(a[key],c[key])
    ledger=cap['six_component_exact_width_ledger'];lo,hi=interval(cap['principal_bias_Q_minus_P'])
    width=F(ledger['interval_width']['exact_rational']);assert width==hi-lo
    assert len(ledger['components'])==6 and sum(F(v['exact_rational']) for v in ledger['components'].values())==width
    result={'status':'FROZEN_SECOND_POINT_STDLIB_READBACK_PASS','scope':'Saved-result/source consistency; pricing kernels are not rerun.',
        'archive_sha256':sha(archive),'archive_receipt_sha256':sha(receipt),'inventory_sha256':sha(dest/'inventory.json'),
        'inventory_file_count':len(inventory['files']),'independent_math_and_literal_source_replay':'PASS',
        'capsule_exact_nonpath_payload_replay':'PASS','weighted_node_exact_checks':nodes,
        'frequency_exact_interval_overlap_checks':frequencies,'linear_fee_exact_interval_overlap_checks':fees,
        'exact_six_component_width_reconciliation':'PASS','bias_outward24':cap['principal_bias_Q_minus_P']['outward24'],
        'width_outward24_upper':ledger['interval_width']['outward_decimal_upper'],'replay_script_sha256':sha(__file__)}
    write(out,result);print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();main(a.archive.resolve(),a.receipt.resolve(),a.directory.resolve(),a.output.resolve())
