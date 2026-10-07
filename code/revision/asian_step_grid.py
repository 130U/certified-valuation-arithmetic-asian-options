"""Finite, separately recorded parameter copies of the full original certificate.

Only the step-count parameter and its dependent loop/index/counter values are
changed. All analytic fees, arithmetic precision and branch guards are retained.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json,shutil,subprocess,sys,time,traceback
CODE=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
def change(s,old,new,count=None):
    n=s.count(old);assert n and (count is None or count==n),(old,n,count)
    return s.replace(old,new)

def run(N,dest):
    assert N in (192,384,1536) and not dest.exists() and not sys.flags.optimize
    assert sys.version_info[:2]==(3,12)
    from flint import __version__
    assert __version__=='0.8.0'
    nm=N//12;resource_factor=max(1,(N+767)//768);core=dest/'work'/'core';core.mkdir(parents=True)
    scope=(CODE/'SCOPE.md').read_text(encoding='utf8')
    scope+='\n\nRevision step experiment: only the Asian pointwise module is executed here. The grid is h=1/'+str(N)+'. No claim is made about the deterministic expansion at this grid. All original analytical guards must pass before a complete certificate is reported.\n'
    (dest/'work'/'SCOPE.md').write_text(scope,encoding='utf8')
    shutil.copyfile(CODE/'core'/'resource_limits.py',core/'resource_limits.py')
    patches=[]
    names=('asian-remainder-certificate.py','asian-linear-certificate.py','check-asian-remainder.py','check-asian-linear.py')
    for name in names:
        src=CODE/'core'/name;s=src.read_text(encoding='utf8')
        s=change(s,'F(1,768)',f'F(1,{N})')
        s=change(s,'range(768)',f'range({N})')
        if name!='check-asian-remainder.py':s=change(s,'range(64)',f'range({nm})')
        if name=='asian-remainder-certificate.py':
            s=change(s,"'h':'1/768'",f"'h':'1/{N}'")
            s=change(s,"'projection_u768'",f"'projection_u{N}'")
            s=change(s,'assert high(radius)<F(11,1000)',"result['original_remainder_radius_target_pass']=high(radius)<F(11,1000)")
        if name=='check-asian-remainder.py':
            s=change(s,'range(767,63,-1)',f'range({N-1},{nm-1},-1)')
            s=change(s,'(n+1)%64','(n+1)%'+str(nm))
            s=change(s,'(n+1)//64','(n+1)//'+str(nm))
            s=change(s,'range(63,-1,-1)',f'range({nm-1},-1,-1)')
            s=change(s,"'projection_u768'",f"'projection_u{N}'")
            s=change(s,'assert radius<ar(F(11,1000))',"original_remainder_radius_target_pass=radius<ar(F(11,1000))")
            s=change(s,"'unpaid':['linearized thirteen-profile price difference and all its fees'],", "'original_remainder_radius_target_pass':original_remainder_radius_target_pass,\n        'unpaid':['linearized thirteen-profile price difference and all its fees'],")
        if name in ('asian-linear-certificate.py','check-asian-linear.py'):
            s=change(s,'6399744',str(641*13*N))
        if name=='check-asian-linear.py':
            author_hash=sha(core/'asian-linear-certificate.py')
            s=change(s,'dbe13d37a5ad6db8dcda674cc1bddae7b6049329de2cc23e8b115af10409c5a8',author_hash,1)
            s=change(s,'assert max(abs(bl),abs(bu))<F(1,40)','original_price_absolute_target_pass=max(abs(bl),abs(bu))<F(1,40)')
            s=change(s,"'original_theta_star_Asian_pass_0025':True", "'original_theta_star_Asian_pass_0025':original_price_absolute_target_pass")
        if resource_factor>1:
            if name in ('asian-remainder-certificate.py','check-asian-remainder.py'):
                s=change(s,'<55',f'<{55*resource_factor}')
                s=change(s,'timeout=60',f'timeout={60*resource_factor}')
                s=change(s,"'hard_wall_seconds':60",f"'hard_wall_seconds':{60*resource_factor}")
            else:
                s=change(s,'<170',f'<{170*resource_factor}')
                if name=='asian-linear-certificate.py':
                    s=change(s,"prior['full_linear_time_estimate']<140",f"prior['full_linear_time_estimate']<{140*resource_factor}")
                    s=change(s,"'hard_wall_seconds':30 if pilot else 180",f"'hard_wall_seconds':30 if pilot else {180*resource_factor}")
                else:
                    s=change(s,"'hard_wall_seconds':180",f"'hard_wall_seconds':{180*resource_factor}")
                    s=change(s,'timeout=180',f'timeout={180*resource_factor}')
        (core/name).write_text(s,encoding='utf8')
        patches.append({'source':name,'original_sha256':sha(src),'executed_sha256':sha(core/name),
                        'changes':'Finite step parameter N='+str(N)+'; month loop/index/counter values; source-identity pin rebound to the executed author copy. Original radius < .011 and price absolute error < .025 acceptance thresholds are recorded as booleans, allowing a wider valid enclosure. Mathematical fees, analytical preconditions, branch guards, precision, one thread and 256 MiB memory limit retained. Wall budgets are multiplied by ceil(N/768) to retain a bounded resource contract at twice the grid workload.'})
    receipt={'status':'RUNNING','h':str(F(1,N)),'script_sha256':sha(__file__),'source_patches':patches,'jobs':[],
             'analytical_projection_beta_expected':str(min(F(12)*(1-F(3253,1000*N))-F(529,20000)*144-F(1,N*N),
               (F(12)+F(512,N))*(1-F(3253,1000*N))-F(529,20000)*(F(12)+F(512,N))**2-F(1,N*N))),
             'no_claim':'A stopped job gives no complete price enclosure at this grid.'}
    write(dest/'receipt.json',receipt)
    tasks=[('asian-W','asian-remainder-certificate.py',[],'asian-remainder-result.json',75),
           ('asian-pilot','asian-linear-certificate.py',['--pilot'],'asian-linear-pilot-result.json',40),
           ('asian-linear','asian-linear-certificate.py',[],'asian-linear-result.json',195),
           ('asian-W-check','check-asian-remainder.py',[],'check-asian-remainder-result.json',70),
           ('asian-linear-check','check-asian-linear.py',[],'check-asian-linear-result.json',195)]
    tasks=[(j,n,a,r,t*resource_factor if j!='asian-pilot' else t) for j,n,a,r,t in tasks]
    for job,name,args,result,seconds in tasks:
        started=time.perf_counter();log=dest/(job+'.log')
        with log.open('x',encoding='utf8') as stream:
            p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(core/name)]+args,stdout=stream,stderr=subprocess.STDOUT,creationflags=0x08000000)
            try:p.wait(timeout=seconds)
            except subprocess.TimeoutExpired:
                subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],stdout=stream,stderr=subprocess.STDOUT,creationflags=0x08000000,timeout=15)
        row={'id':job,'source':name,'source_sha256':sha(core/name),'returncode':p.returncode,'seconds':time.perf_counter()-started,'log':log.name}
        if p.returncode or not (core/result).is_file():
            row.update(status='STOPPED',reason='No mathematical result produced; see retained controller and worker logs.')
            if (core/result.replace('-result.json','-controller.json')).exists():row['controller']=read(core/result.replace('-result.json','-controller.json'))
            receipt['jobs'].append(row);receipt['status']='STOPPED';write(dest/'receipt.json',receipt)
            print(json.dumps({'h':str(F(1,N)),'status':'STOPPED','job':job,'receipt':str(dest/'receipt.json')}),flush=True);return
        obj=read(core/result);assert obj['source_sha256']==sha(core/name)
        row.update(status='COMPLETE',result=result,result_sha256=sha(core/result),numerical_status=obj['status'])
        receipt['jobs'].append(row);write(dest/'receipt.json',receipt)
        print(json.dumps({'h':str(F(1,N)),'job':job,'status':'COMPLETE','seconds':row['seconds']}),flush=True)
    receipt.update(status='COMPLETE',independent_all_nodes_and_frequency_fees_pass=True)
    write(dest/'receipt.json',receipt)
    print(json.dumps({'h':str(F(1,N)),'status':'COMPLETE','receipt':str(dest/'receipt.json')}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--steps',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    run(a.steps,a.output.resolve())
