"""Isolated runner for Heston numerical certificates (Windows)."""
from __future__ import annotations
import argparse, ast, ctypes, hashlib, json, os, platform, shutil, subprocess, sys, time, uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = Path('core')
REFERENCE = HERE/'reference'
META_KEYS = {'worker_seconds','elapsed_seconds','seconds','outer_seconds','envelope_worker_seconds','full_linear_time_estimate'}
EXECUTION_MANIFEST_SHA256 = '33eaee125bc49f5755ec74ab24fa9bf655afaab5f884decf1576687eacdbf0c2'

def read(path): return json.loads(Path(path).read_text(encoding='utf8'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
def report(obj): print(json.dumps(obj, ensure_ascii=True), flush=True)
def need(ok, message):
    if not ok: raise RuntimeError(message)
def payload(obj):
    """Retain every non-metadata field, including all numerical arrays/fees."""
    if isinstance(obj, dict): return {k:payload(v) for k,v in obj.items() if not k.endswith('sha256') and k not in META_KEYS}
    if isinstance(obj, list): return [payload(v) for v in obj]
    return obj
def digest_payload(obj):
    return hashlib.sha256(json.dumps(payload(obj),sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf8')).hexdigest()

def verify():
    manifest=read(HERE/'MANIFEST.json')
    for rel, info in manifest['files'].items():
        p=HERE/rel
        need(p.is_file() and p.stat().st_size==info['bytes'] and sha(p)==info['sha256'], 'Package integrity failure: '+rel)
    for path in (HERE/'core').glob('*.py'): ast.parse(path.read_text(encoding='utf8'),filename=path.name)
    return {'status':'PASS_PACKAGE_INTEGRITY','files':len(manifest['files']),'manifest_sha256':sha(HERE/'MANIFEST.json')}

class Memory(ctypes.Structure):
    _fields_=[('length',ctypes.c_uint32),('load',ctypes.c_uint32)]+[(k,ctypes.c_uint64) for k in ('total_physical','available_physical','total_commit','available_commit','total_virtual','available_virtual','available_extended_virtual')]

def environment():
    need(sys.platform=='win32' and sys.version_info[:2]==(3,12) and platform.machine().lower() in ('amd64','x86_64'), 'This resource-controlled runtime requires Windows x86-64 CPython 3.12. See ENVIRONMENT.md.')
    need(not sys.flags.optimize and not os.environ.get('PYTHONOPTIMIZE'), 'Do not use python -O or PYTHONOPTIMIZE: source assertions are part of the certificate.')
    mem=Memory();mem.length=ctypes.sizeof(mem)
    need(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)), 'Cannot read available memory')
    need(min(mem.available_physical,mem.available_commit)>=512<<20, 'Resource preflight stopped: at least 512 MiB free physical and commit memory required.')
    env=os.environ.copy()
    env.pop('PYTHONPATH',None)
    env.update(PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    probe=subprocess.run([sys.executable,'-B','-X','utf8','-c','import flint,json;print(json.dumps({"version":flint.__version__}))'],env=env,capture_output=True,text=True,timeout=15,creationflags=0x08000000)
    need(probe.returncode==0, 'Installed python-flint import failed. Install requirements.txt in this interpreter environment. '+probe.stderr[-1000:])
    imported=json.loads(probe.stdout)
    need(imported['version']=='0.8.0', 'Require python-flint==0.8.0')
    return env, {'python_version':platform.python_version(),'platform':platform.system(),'machine':platform.machine(),'python_flint':imported['version'],'available_physical_bytes':mem.available_physical,'available_commit_bytes':mem.available_commit,'network_calls':0}

def compare_result(result, reference):
    actual=read(result);expected=read(reference)
    aa=payload(actual);ee=payload(expected)
    if aa!=ee:
        differing=[k for k in sorted(set(aa)|set(ee)) if aa.get(k)!=ee.get(k)]
        raise RuntimeError('Mathematical/reference mismatch in '+result.name+': '+', '.join(differing))
    return {'reference':reference.name,'mathematical_payload_sha256':digest_payload(actual),'all_nonmetadata_fields_exactly_equal':True}

def expected_jobs(config, modules, independent):
    need(isinstance(modules,list) and modules and all(isinstance(name,str) for name in modules), 'Run modules must be a nonempty list')
    need(isinstance(independent,bool), 'Run independent_checks must be a boolean')
    if 'all' in modules:
        need(modules==['all'], 'Use all alone')
        modules=list(config['modules'])
    need(all(name in config['modules'] for name in modules), 'Unknown run module')
    ids=[]
    for name in modules:
        for key in config['modules'][name]['author']:
            if key not in ids:ids.append(key)
    if independent:
        for name in modules:
            for key in config['modules'][name]['independent']:
                if key not in ids:ids.append(key)
    return ids

def check_run(folder, *, allow_running=False):
    folder=Path(folder).resolve();rec=read(folder/'run-receipt.json');config=read(HERE/'configuration.json')
    allowed_status={'COMPLETE','RUNNING'} if allow_running else {'COMPLETE'}
    need(rec.get('status') in allowed_status, 'Run is not complete')
    manifest=read(HERE/'MANIFEST.json')
    compatible=manifest.get('execution_manifest_identifiers',[])
    need(isinstance(compatible,list) and all(value==EXECUTION_MANIFEST_SHA256 for value in compatible), 'Unrecognized execution manifest identifier')
    accepted={sha(HERE/'MANIFEST.json')}
    accepted.update(compatible)
    need(rec.get('manifest_sha256') in accepted, 'Run/package manifest mismatch')
    jobs=rec.get('jobs')
    need(isinstance(jobs,list) and jobs and all(isinstance(job,dict) for job in jobs), 'Run must contain completed jobs')
    ids=[job.get('id') for job in jobs]
    need(all(isinstance(key,str) for key in ids) and len(ids)==len(set(ids)), 'Run contains duplicate or invalid jobs')
    expected=expected_jobs(config,rec.get('modules'),rec.get('independent_checks'))
    need(set(ids)==set(expected), 'Run job set does not match its requested modules')
    rows=[]
    for job in jobs:
        need(job['status']=='COMPLETE', 'Run contains incomplete job: '+job['id'])
        src,argv,timeout,filename=config['jobs'][job['id']]
        result=folder/'work'/REL/filename;source=folder/'work'/REL/src
        need(sha(result)==job['result_sha256'], 'Run result identity mismatch: '+filename)
        need(sha(source)==sha(HERE/REL/src)==job['source_sha256'], 'Run source identity mismatch: '+src)
        need(read(result)['source_sha256']==sha(source), 'Result/source identity mismatch: '+filename)
        rows.append({'job':job['id'],**compare_result(result,REFERENCE/filename)})
    if any(j['id']=='posterior-compat' for j in rec['jobs']):
        v2=payload(read(folder/'work'/REL/'posterior-compat-4096-result.json'))
        v3=payload(read(folder/'work'/REL/'posterior-4096-result.json'))
        v2['Asian_zero_xi_reference_P_parameter_Lipschitz_bound']=v2.pop('Asian_P_parameter_Lipschitz_bound')
        v2.pop('scheme',None);v3.pop('scheme',None)
        need(v2==v3, 'Posterior compatibility and current mathematical payload mismatch')
    out={'status':'PASS_EXACT_MATHEMATICAL_PAYLOAD','jobs':rows,'compared_fields':'All JSON fields except hashes and explicitly named elapsed-time metadata. No tolerances, midpoint comparisons, or omitted arrays.','metadata_exclusions':sorted(META_KEYS),'hash_fields_excluded':'keys ending sha256'}
    write(folder/'mathematical-check.json',out);return out

def run(modules, independent):
    integrity=verify();env,env_receipt=environment();config=read(HERE/'configuration.json')
    if 'all' in modules:need(modules==['all'],'Use all alone');modules=list(config['modules'])
    job_ids=[]
    for name in modules:
        for key in config['modules'][name]['author']:
            if key not in job_ids:job_ids.append(key)
    if independent:
        for name in modules:
            for key in config['modules'][name]['independent']:
                if key not in job_ids:job_ids.append(key)
    run_id='run-'+uuid.uuid4().hex
    dest=HERE/'runs'/run_id;dest.mkdir(parents=True,exist_ok=False)
    for directory in ('core','data'):
        shutil.copytree(HERE/directory,dest/'work'/directory,ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copyfile(HERE/'SCOPE.md',dest/'work'/'SCOPE.md')
    rec={'status':'RUNNING','run_id':run_id,'modules':modules,'independent_checks':independent,'manifest_sha256':integrity['manifest_sha256'],'environment':env_receipt,'jobs':[],'reference_outputs_modified':False}
    write(dest/'run-receipt.json',rec);report({'status':'STARTED','run_directory':str(dest),'jobs':job_ids})
    for index,key in enumerate(job_ids,1):
        script,args,seconds,result_name=config['jobs'][key];source=dest/'work'/REL/script
        # Number + job id keeps pilot/full outer logs distinct from core logs.
        log=dest/'logs'/f'{index:02d}-{key}.txt';log.parent.mkdir(exist_ok=True)
        row={'id':key,'script':script,'source_sha256':sha(source),'external_timeout_seconds':seconds,'console':str(log.relative_to(dest))};started=time.perf_counter()
        try:
            with log.open('x',encoding='utf8') as stream:
                proc=subprocess.Popen([sys.executable,'-B','-X','utf8',str(source)]+args,stdout=stream,stderr=subprocess.STDOUT,env=env,creationflags=0x08000000)
                try:proc.wait(timeout=seconds)
                except subprocess.TimeoutExpired:
                    subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],stdout=stream,stderr=subprocess.STDOUT,creationflags=0x08000000,timeout=15)
                    proc.wait(timeout=15)
                    raise RuntimeError('External timeout stopped the owned process tree')
            need(proc.returncode==0,'Nonzero return code '+str(proc.returncode))
            result=dest/'work'/REL/result_name
            need(result.is_file(), 'No certificate produced; inspect resource preflight and console')
            need(read(result)['source_sha256']==sha(source), 'Result source binding failed')
            checked=compare_result(result,REFERENCE/result_name)
            row.update(status='COMPLETE',returncode=proc.returncode,result=result_name,result_sha256=sha(result),**checked)
        except Exception as exc:
            row.update(status='STOPPED',reason=str(exc))
        row['outer_seconds']=time.perf_counter()-started;rec['jobs'].append(row);write(dest/'run-receipt.json',rec)
        report({'job':key,'status':row['status'],'seconds':row['outer_seconds'],'reason':row.get('reason')})
        if row['status']!='COMPLETE':rec['status']='STOPPED';write(dest/'run-receipt.json',rec);return 1
    try:checked=check_run(dest,allow_running=True)
    except Exception as exc:
        rec.update(status='STOPPED',reason=str(exc));write(dest/'run-receipt.json',rec);raise
    rec['status']='COMPLETE';rec['mathematical_check_status']=checked['status'];write(dest/'run-receipt.json',rec)
    report({'status':'COMPLETE','run_directory':str(dest),'mathematical_check':checked['status'],'jobs':len(job_ids)});return 0

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('list');sub.add_parser('verify');sub.add_parser('environment')
    p=sub.add_parser('run');p.add_argument('--module',nargs='+',choices=['all','tt','small-xi','posterior-zero','posterior','asian'],default=['all']);p.add_argument('--independent',action='store_true')
    p=sub.add_parser('check');p.add_argument('--run',required=True)
    args=parser.parse_args()
    if args.command=='list':report(read(HERE/'configuration.json')['domains'])
    elif args.command=='verify':report(verify())
    elif args.command=='environment':verify();report(environment()[1])
    elif args.command=='check':verify();report(check_run(args.run))
    else:return run(args.module,args.independent)
    return 0
if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as exc:report({'status':'STOPPED','reason':str(exc)});raise SystemExit(1)
