"""Reproduce the three posterior meshes without changing original numerical kernels.

8192 is a finite extra grid selection; all mathematical formulas, precision,
whole-cell weights, target fees and independent verification are retained.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,bisect,ctypes,hashlib,importlib.util,json,os,shutil,subprocess,sys,time

CODE=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
def replace_exact(s,old,new,count=1):
    assert s.count(old)==count,(old,s.count(old),count)
    return s.replace(old,new)

def run(cells,base_run,dest):
    assert cells in (8192,16384) and not dest.exists()
    assert sys.version_info[:2]==(3,12) and not sys.flags.optimize
    from flint import __version__
    assert __version__=='0.8.0'
    base=read(base_run/'run-receipt.json')
    assert base['status']=='COMPLETE' and base['mathematical_check_status']=='PASS_EXACT_MATHEMATICAL_PAYLOAD'
    work=dest/'work';core=work/'core';core.mkdir(parents=True)
    shutil.copytree(CODE/'data',work/'data');shutil.copyfile(CODE/'SCOPE.md',work/'SCOPE.md')
    shutil.copyfile(CODE/'core'/'resource_limits.py',core/'resource_limits.py')
    patches=[]
    for name in ('posterior-certificate.py','posterior-compat-certificate.py'):
        src=CODE/'core'/name;s=src.read_text(encoding='utf8')
        s=replace_exact(s,'assert cells in (4096,16384)','assert cells in (4096,8192,16384)')
        s=replace_exact(s,"'permitted_grid_sequence':[4096,16384]","'permitted_grid_sequence':[4096,8192,16384]")
        (core/name).write_text(s,encoding='utf8')
        patches.append({'file':name,'original_sha256':sha(src),'executed_sha256':sha(core/name),'changes':['Add finite mesh 8192 to grid selection and contract; mathematical formulas unchanged.']})
    name='check-posterior.py';src=CODE/'core'/name;s=src.read_text(encoding='utf8')
    s=replace_exact(s,"AUTHOR=HERE/'posterior-compat-4096-result.json'",f"AUTHOR=HERE/'posterior-compat-{cells}-result.json'")
    s=replace_exact(s,'M=4096;left=',f'M={cells};left=')
    s=replace_exact(s,'all 4096 cells',f'all {cells} cells')
    (core/name).write_text(s,encoding='utf8')
    patches.append({'file':name,'original_sha256':sha(src),'executed_sha256':sha(core/name),'changes':['Set declared finite mesh and author path; independent erfc, integer quadratic intervals and advancing-pointer coupling unchanged.']})
    zeroname='posterior-zero-4096-result.json'
    shutil.copyfile(base_run/'work'/'core'/zeroname,core/zeroname)
    receipt={'status':'RUNNING','cells':cells,'baseline_run':str(base_run),'baseline_run_receipt_sha256':sha(base_run/'run-receipt.json'),
             'source_patches':patches,'original_zero_reference_sha256':sha(core/zeroname),'script_sha256':sha(__file__),'jobs':[]}
    write(dest/'receipt.json',receipt)
    for name,result,args in [('posterior-certificate.py',f'posterior-{cells}-result.json',[str(cells)]),('posterior-compat-certificate.py',f'posterior-compat-{cells}-result.json',[str(cells)]),('check-posterior.py','check-posterior-result.json',[])]:
        log=dest/(name+'.log');started=time.perf_counter()
        with log.open('x',encoding='utf8') as f:
            p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(core/name)]+args,stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000)
            try:p.wait(timeout=110)
            except subprocess.TimeoutExpired:
                subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000,timeout=15)
                raise RuntimeError('Owned finite job exceeded 110 seconds')
        row={'source':name,'seconds':time.perf_counter()-started,'returncode':p.returncode,'log':log.name}
        if p.returncode or not (core/result).is_file():
            receipt['jobs'].append(row);receipt['status']='STOPPED';write(dest/'receipt.json',receipt)
            raise RuntimeError('Kernel or independent audit stopped; see '+str(log))
        obj=read(core/result);assert obj['source_sha256']==sha(core/name)
        row.update(result=result,result_sha256=sha(core/result),status=obj['status']);receipt['jobs'].append(row);write(dest/'receipt.json',receipt)
    principal=read(core/f'posterior-{cells}-result.json');compat=read(core/f'posterior-compat-{cells}-result.json')
    def payload(v):
        if isinstance(v,dict):return {k:payload(z) for k,z in v.items() if not k.endswith('sha256') and k not in ('elapsed_seconds','scheme')}
        if isinstance(v,list):return list(map(payload,v))
        return v
    pp=payload(principal);cc=payload(compat);cc['Asian_zero_xi_reference_P_parameter_Lipschitz_bound']=cc.pop('Asian_P_parameter_Lipschitz_bound')
    assert pp==cc,'Principal and compatibility mathematical payload mismatch'
    receipt.update(status='COMPLETE',principal_compatibility_all_mathematical_fields_equal=True,
                   independent_status=read(core/'check-posterior-result.json')['status'])
    write(dest/'receipt.json',receipt);print(json.dumps({'cells':cells,'status':'COMPLETE','directory':str(dest)}),flush=True)

def summarize(paths,output):
    rows=[];cdf=[];quantiles=[]
    for path in paths:
        obj=read(path);cells=obj['cells'];dx=F(obj['cell_width']);left=F(obj.get('prior_left','3/100'))
        L=F(obj['Asian_zero_xi_reference_P_parameter_Lipschitz_bound']['exact_interval'][1])
        common=F(obj['Asian_positive_xi_same_parameter_PQ_bound']['exact_interval'][1])
        for name,tr in obj['transports'].items():
            dv=F(tr['all_p_parameter_Winfinity_bound']);bound=F(tr['all_target_quantile_levels_absolute_PQ_difference_bound']['exact_interval'][1])
            rows.append({'cells':cells,'quotes':1 if name=='d1' else 9,'delta_u':str(dx),'grid_steps':tr['max_grid_steps'],
                         'delta_parameter':str(dv),'price_bound_upper_exact':str(bound),'price_bound_upper_decimal':tr['all_target_quantile_levels_absolute_PQ_difference_bound']['outward18'][1],
                         'common_fee_upper_exact':str(common),'mesh_transfer_fee_upper_exact':str(L*dv),'mesh_transfer_share_upper_diagnostic':float(L*dv/bound),
                         'execution_result':str(path),'result_sha256':sha(path)})
            for model in ('P','Q'):
                weights=obj['whole_cell_weights_integer_bounds'][model][name];tl=sum(x[0] for x in weights);tu=sum(x[1] for x in weights)
                ll=[F(0)];uu=[F(0)];pl=pu=0
                for low,high in weights:
                    pl+=low;pu+=high;ll.append(F(pl,pl+tu-pu));uu.append(F(pu,pu+tl-pl))
                for i in range(0,cells+1,max(1,cells//128)):
                    cdf.append({'cells':cells,'quotes':1 if name=='d1' else 9,'model':model,'v0':str(left+i*dx),'cdf_lower':str(ll[i]),'cdf_upper':str(uu[i])})
                for p in (F(1,40),F(1,2),F(39,40)):
                    il=max(0,bisect.bisect_left(uu,p)-1);ir=min(cells,bisect.bisect_left(ll,p))
                    a=left+il*dx;b=left+ir*dx
                    quantiles.append({'cells':cells,'quotes':1 if name=='d1' else 9,'model':model,'probability':str(p),'v0_quantile_bracket':[str(a),str(b)],'decimal_bracket':[float(a),float(b)]})
    result={'scope':'Positive-xi small prior; CDF and absolute quantile brackets concern the v0 marginal. Asian target only has an all-level P/Q displacement bound. No absolute Asian-price posterior quantile is calculated.',
            'table':rows,'v0_cdf_envelopes':cdf,'v0_quantile_brackets':quantiles,'source_sha256':sha(__file__)}
    write(output,result);print(json.dumps(rows,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True)
    q=sub.add_parser('run');q.add_argument('--cells',type=int,required=True);q.add_argument('--base-run',type=Path,required=True);q.add_argument('--output',type=Path,required=True)
    q=sub.add_parser('summary');q.add_argument('--result',type=Path,action='append',required=True);q.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.mode=='run':run(a.cells,a.base_run.resolve(),a.output.resolve())
    else:summarize(a.result,a.output)
