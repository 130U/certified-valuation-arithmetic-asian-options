"""Controlled real-child tests for runner lifecycle; no pricing implementation.

The JSON used by controlled children is a small invented process-test record.
Separate schema tests read existing frozen pricing outputs without evaluating
or copying any numerical kernel. All fixtures use new directories.
"""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,os,subprocess,sys,time,uuid

HERE=Path(__file__).resolve().parent
RUNNER=HERE/'asian_parameter_point.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
def load(name,p):
    sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def one_case(case,dest):
    runner=load('controlled_round2_runner',RUNNER)
    core=dest/'work'/'core';core.mkdir(parents=True)
    write(dest/'receipt.json',{'status':'PREPARED_NOT_EXECUTED','jobs':[],'scope':'Controlled subprocess fixture; no numerical certificate.'})
    source=core/'controlled-child.py';out=core/'controlled-result.json'
    source.write_text('''from pathlib import Path
import json,sys,time
here=Path(__file__).resolve().parent
(here/'started.marker').write_text('started')
case=sys.argv[1]
if case=='missing':sys.exit(0)
if case=='invalid_json':(here/'controlled-result.json').write_text('{invalid');sys.exit(0)
data={'status':'CONTROLLED_COMPLETE','entries':[1,2,3]}
if case=='incomplete':data.pop('entries')
if case=='invalid_status':data['status']='CONTROLLED_STOPPED'
(here/'controlled-result.json').write_text(json.dumps(data))
if case=='nonzero':sys.exit(7)
if case=='timeout':time.sleep(60)
''',encoding='utf8')
    if case=='existing':write(out,{'status':'CONTROLLED_COMPLETE','entries':[1,2,3]})
    def validate(id,result,unused_core,unused_source):
        runner.require(result.get('status')=='CONTROLLED_COMPLETE','Controlled result has wrong status')
        runner.require(result.get('entries')==[1,2,3],'Controlled result is incomplete')
    def finalize(directory,path):
        if case=='finalizer_failure':raise RuntimeError('Controlled finalizer rejects the output')
        write(path,{'status':'CONTROLLED_TEST_MARKER','scope':'No numerical certificate; tests orchestration only.'})
        if case=='finalizer_after_output':raise RuntimeError('Controlled failure after a capsule artifact was written')
    return runner.run_prepared(dest,os.environ.copy(),{'scope':'Controlled process test'},
        [('controlled','controlled-child.py',[case],'controlled-result.json',.4 if case=='timeout' else 10)],validate,finalize)

def suite(dest,reference):
    assert not dest.exists();dest.mkdir(parents=True)
    rows=[]
    for case in ('timeout','nonzero','existing','missing','incomplete','invalid_status','invalid_json','finalizer_failure','finalizer_after_output','success'):
        path=dest/case
        child=subprocess.run([sys.executable,'-B','-X','utf8',str(__file__),'--case',case,'--directory',str(path)],
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf8',timeout=35,creationflags=0x08000000)
        (dest/(case+'.log')).write_text(child.stdout,encoding='utf8')
        r=read(path/'receipt.json');success=case=='success'
        assert (child.returncode==0)==success
        assert r['status']==('COMPLETE' if success else 'STOPPED')
        assert (path/'result-capsule.json').exists()==success
        job=r['jobs'][0]
        if case=='timeout':
            assert job['timed_out'] and job['reaped'] and job['returncode'] is not None
            assert (path/'work'/'core'/'controlled-result.json').exists(), 'Timeout fixture must already have produced output.'
        elif case=='existing':assert 'pid' not in job and not (path/'work'/'core'/'started.marker').exists()
        else:assert job['reaped'] and job['returncode'] is not None
        if case=='nonzero':assert job['returncode']==7 and (path/'work'/'core'/'controlled-result.json').exists()
        if case=='finalizer_after_output':assert (path/'failed-capsule-artifact.json').exists()
        rows.append({'case':case,'cli_returncode':child.returncode,'receipt_status':r['status'],'job_status':job['status'],
            'timed_out':job['timed_out'],'returncode':job['returncode'],'reaped':job['reaped'],
            'final_capsule_present':(path/'result-capsule.json').exists(),'receipt_sha256':sha(path/'receipt.json')})
    runner=load('production_result_schema',RUNNER)
    core=reference/'work'/'core';checks=[]
    for id,name,args,filename,seconds in runner.JOBS:
        result=read(core/filename);runner.validate_result(id,result,core,core/name)
        broken=copy.deepcopy(result)
        if id in ('asian-W','asian-W-check'):broken['all_points_Q'].pop()
        elif id=='asian-linear-check':broken['fees'].pop('Q_frequency_tail')
        else:broken['frequency_rows'].pop()
        try:runner.validate_result(id,broken,core,core/name)
        except Exception:pass
        else:raise AssertionError('Production schema accepted truncated '+id)
        wrong=copy.deepcopy(result);wrong['status']='STOPPED'
        try:runner.validate_result(id,wrong,core,core/name)
        except Exception:pass
        else:raise AssertionError('Production schema accepted wrong status '+id)
        empty=copy.deepcopy(result)
        if id in ('asian-W','asian-W-check'):empty['all_points_Q'][0]={}
        elif id=='asian-linear-check':empty['fees']['Q_frequency_tail']={}
        else:empty['linear_bias_finite']={}
        try:runner.validate_result(id,empty,core,core/name)
        except Exception:pass
        else:raise AssertionError('Production schema accepted empty interval '+id)
        checks.append({'job':id,'complete_frozen_result_accepted':True,'truncated_result_rejected':True,'wrong_status_rejected':True,'empty_interval_rejected':True,
            'frozen_result_sha256':sha(core/filename)})
    result={'status':'REAL_SUBPROCESS_RUNNER_BOUNDARY_TESTS_PASS','scope':'Ten controlled process cases and five frozen-result schema tests. No pricing implementation is simulated.',
        'runner_sha256':sha(RUNNER),'test_source_sha256':sha(__file__),'controlled_cases':rows,'production_schema_checks':checks}
    write(dest/'test-receipt.json',result)
    print(json.dumps({'status':result['status'],'controlled_cases':len(rows),'production_schema_checks':len(checks),'receipt':str(dest/'test-receipt.json')}))

def compare_fresh(fresh,reference,output):
    code=HERE.parents[1];baseline=load('unchanged_mathematical_payload_reader',code/'run.py')
    a=read(fresh/'receipt.json');b=read(reference/'receipt.json')
    assert a['status']==b['status']=='COMPLETE' and len(a['jobs'])==len(b['jobs'])==5
    assert all(j['returncode']==0 and not j['timed_out'] and j['reaped'] for j in a['jobs'])
    rows=[]
    for actual,expected in zip(a['jobs'],b['jobs']):
        assert actual['id']==expected['id'] and actual['file']==expected['file'] and actual['result']==expected['result']
        src=fresh/'work'/'core'/actual['file'];oldsrc=reference/'work'/'core'/expected['file']
        assert sha(src)==sha(oldsrc)==actual['source_sha256']==expected['source_sha256']
        current=fresh/'work'/'core'/actual['result'];prior=reference/'work'/'core'/expected['result']
        assert sha(current)==actual['result_sha256'] and sha(prior)==expected['result_sha256']
        rows.append({'job':actual['id'],'unchanged_executed_numerical_source_sha256':sha(src),
            'fresh_result_sha256':sha(current),'frozen_result_sha256':sha(prior),**baseline.compare_result(current,prior)})
    result={'status':'FRESH_FIVE_JOB_EXACT_FROZEN_MATHEMATICAL_PAYLOAD_PASS','jobs':rows,
        'comparison':'Every result field and array exactly equals the frozen reference after removing SHA256 fields and the original explicitly named elapsed-time metadata; no numerical tolerance.',
        'metadata_exclusions':sorted(baseline.META_KEYS),'hash_exclusion':'keys ending sha256','runner_sha256':sha(RUNNER),
        'unchanged_baseline_payload_reader_sha256':sha(code/'run.py'),'fresh_execution_receipt_sha256':sha(fresh/'receipt.json'),
        'frozen_execution_receipt_sha256':sha(reference/'receipt.json'),'fresh_capsule_sha256':sha(fresh/'result-capsule.json')}
    write(output,result);print(json.dumps({'status':result['status'],'jobs':len(rows),'receipt':str(output)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case');p.add_argument('--directory',type=Path);p.add_argument('--reference',type=Path)
    p.add_argument('--compare-run',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args()
    if a.case:sys.exit(one_case(a.case,a.directory.resolve()))
    elif a.compare_run:compare_fresh(a.compare_run.resolve(),a.reference.resolve(),a.output.resolve())
    else:suite(a.directory.resolve(),a.reference.resolve())
