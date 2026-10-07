"""One new stochastic-Heston point, through all five original Asian jobs.

The original package is preserved. Numerical formula changes are prohibited;
the parameter copies change v0 to 1/25 and retain the conservative original
moment constant exp(.78), justified by exp(.6+4v0)<=exp(.78). Every finite
coefficient, projection, recurrence, branch, moment and tail guard remains.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,importlib.util,json,os,platform,shutil,subprocess,sys,time,zipfile

CODE=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def change(s,a,b,count=1):
    assert s.count(a)==count,(a,s.count(a),count)
    return s.replace(a,b)
def load_module(name,path):
    sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def mathematical_preflight():
    from flint import arb,fmpq,ctx
    ctx.prec=256;ctx.threads=1
    def ar(x):x=F(x);return arb(fmpq(x.numerator,x.denominator))
    def rec(x):
        a=F(str(x.lower().fmpq()));b=F(str(x.upper().fmpq()))
        lim=load_module('round2_limits',CODE/'core'/'resource_limits.py')
        return {'exact_interval':[str(a),str(b)],'outward24':lim.decimal_enclosure(a,b)}
    h=F(1,768);alpha=F(529,20000);rx=F(-253,2000);k=F(3);d=F(27,200);r=F(1,100);v0=F(1,25)
    betaW=min(s*(1-F(3253,1000)*h)-alpha*s*s-h*h for s in (F(12),F(12)+512*h))
    betaL=min(s*(1-F(6253,2000)*h)-alpha*s*s-F(3,8)*h*h for s in (F(12),F(12)+1024*h))
    ui_beta=12*(1-(k-rx*F(5,2))*h)-144*alpha-F(15,8)*h*h
    loading_range=(F(-5,4),F(5,2))
    generator=[16*alpha+4*(rx*p-k)+(p*p-p)/2 for p in loading_range]
    growth=4*ar(d)+ar(F(1,40))+ar(F(1,3))*(-12*ar(d)-1).exp()
    assert betaW>8 and betaL>8 and ui_beta>0 and max(generator)<0 and growth<ar(F(3,5))
    assert 0<v0<=F(9,200) and F(3,5)+4*v0==F(19,25) and F(19,25)<F(39,50)
    assert (1-h*k)>0 and 1-F(121,400)>0 and h*v0==F(1,19200)
    return {'status':'PASS_FIXED_PARAMETER_ANALYTICAL_PREFLIGHT',
        'theta_order':['kappa','vbar','xi','rho','v0'],'theta':['3','9/200','23/100','-11/20','1/25'],
        'S0':'100','r':'1/100','h':'1/768','fixings':'m/12, m=1,...,12','payoff':'(A-95)+-(A-110)+',
        'c':'1254433/1250000','weighted_projection_beta_exact':str(betaW),'linear_projection_beta_exact':str(betaL),
        'UI_beta_exact':str(ui_beta),'UI_loading_range':list(map(str,loading_range)),
        'continuous_generator_endpoint_coefficients_exact':list(map(str,generator)),'UI_growth_upper':rec(growth),
        'new_point_moment_exponent_bound_exact':'19/25','retained_conservative_M2_exponent_exact':'39/50',
        'moment_reason':'B.5-B.6 growth is independent of v0; .6+4*.04=.76<.78, so exp(.78) still bounds all required price-profile moments.',
        'first_Euler_integrated_variance_floor_exact':'1/19200','Feller_index_exact':'2700/529',
        'must_recompute_at_new_v0':['All affine e^(A+Bv0) evaluations','Every exp(-v0*u/h) projection prefix',
            'Weighted-tail C and zeta','Q weighted-tail denominator 128*h*v0','First-month Q Laplace LQ',
            'Continuous price-tail CP and gamma','Discrete price-tail i0=h*v0 denominator',
            'Both signed remainders, complete bias and separate P/Q prices'],
        'must_pass_during_execution':['All 91-profile real coefficient and denominator guards','Positive projection u recurrence',
            'All 641-frequency 13-ray Euler coefficient guards','All continuous complex-log branch guards',
            'All first-month Laplace coefficient sign guards','All independent node/frequency/fee checks'],
        'scope':'This is a preflight for one changed-v0 point, not a uniform parameter-region certificate.'}

def prepare(dest):
    assert not dest.exists() and not sys.flags.optimize and not os.environ.get('PYTHONOPTIMIZE')
    baseline=load_module('round2_baseline_runner',CODE/'run.py')
    package=baseline.verify();env,environment=baseline.environment()
    pre=mathematical_preflight();core=dest/'work'/'core';core.mkdir(parents=True)
    scope='''# Round 2 stochastic Heston parameter point

This isolated execution changes only initial variance to v0=1/25. Parameters
(kappa,vbar,xi,rho,v0)=(3,9/200,23/100,-11/20,1/25); S0=100, r=1/100,
h=1/768, twelve fixings at m/12, and payoff (A-95)+-(A-110)+. Bias is Q-P.
The raw positive-part Euler scheme and continuous Heston model are retained.
The original exp(.78) moment envelope is conservative at this point because
the same growth bound gives exp(.6+4v0)=exp(.76). All v0-dependent transforms,
prefixes, integrated-variance floors and infinite tails are recomputed.
The preflight does not certify a price. A complete pointwise enclosure requires
all principal and independent jobs and their finite node/fee checks to finish.
This execution makes no claim about a larger parameter region, posterior,
stochastic-Heston first-order expansion or signed Asian leading coefficient.
'''
    (dest/'work'/'SCOPE.md').write_text(scope,encoding='utf8')
    shutil.copyfile(CODE/'core'/'resource_limits.py',core/'resource_limits.py')
    journal=[]
    for name in ('asian-remainder-certificate.py','asian-linear-certificate.py','check-asian-remainder.py','check-asian-linear.py'):
        src=CODE/'core'/name;s=src.read_text(encoding='utf8');patches=[]
        old='v=ar(F(9,200))' if name=='check-asian-remainder.py' else 'v0=ar(F(9,200))'
        new='v=ar(F(1,25))' if name=='check-asian-remainder.py' else 'v0=ar(F(1,25))'
        s=change(s,old,new);patches.append({'old':old,'new':new,'kind':'actual_numerical_parameter'})
        if name=='asian-remainder-certificate.py':
            a="'theta':['3','9/200','23/100','-11/20','9/200']";b="'theta':['3','9/200','23/100','-11/20','1/25']"
            s=change(s,a,b);patches.append({'old':a,'new':b,'kind':'input_metadata'})
            s=change(s,'assert high(radius)<F(11,1000)',"result['original_remainder_radius_target_pass']=high(radius)<F(11,1000)")
            patches.append({'kind':'result_acceptance_only','note':'Record old .011 target as a boolean; no analytical enclosure premise relaxed.'})
        if name=='check-asian-remainder.py':
            s=change(s,'assert radius<ar(F(11,1000))','original_remainder_radius_target_pass=radius<ar(F(11,1000))')
            s=change(s,"'unpaid':['linearized thirteen-profile price difference and all its fees'],", "'original_remainder_radius_target_pass':original_remainder_radius_target_pass,\n        'unpaid':['linearized thirteen-profile price difference and all its fees'],")
            patches.append({'kind':'result_acceptance_only','note':'Independently record old .011 radius target rather than using it as an enclosure premise.'})
        if name=='check-asian-linear.py':
            oldhash='dbe13d37a5ad6db8dcda674cc1bddae7b6049329de2cc23e8b115af10409c5a8';newhash=sha(core/'asian-linear-certificate.py')
            s=change(s,oldhash,newhash);patches.append({'old':oldhash,'new':newhash,'kind':'bind_actual_executed_author_source'})
            s=change(s,'assert max(abs(bl),abs(bu))<F(1,40)','original_price_absolute_target_pass=max(abs(bl),abs(bu))<F(1,40)')
            s=change(s,"'original_theta_star_Asian_pass_0025':True","'original_theta_star_Asian_pass_0025':original_price_absolute_target_pass")
            s=change(s,"'scope':'Original theta-star parameter point, original payoff and positive-part Euler scheme.'", "'scope':'New point v0=1/25; original Asian payoff and positive-part Euler scheme, all other parameters unchanged.'")
            patches.append({'kind':'result_acceptance_only','note':'Report old .025 absolute-price target truthfully at the new point.'})
        # A finite declared two-times time budget handles concurrent desktop load.
        # Grid, arithmetic precision, all mathematical guards and 256 MiB stay fixed.
        if name in ('asian-remainder-certificate.py','check-asian-remainder.py'):
            s=change(s,'<55','<110');s=change(s,'timeout=60','timeout=120')
            s=change(s,"'hard_wall_seconds':60","'hard_wall_seconds':120")
        else:
            s=change(s,'<170','<340')
            if name=='asian-linear-certificate.py':
                s=change(s,"prior['full_linear_time_estimate']<140","prior['full_linear_time_estimate']<280")
                s=change(s,"'hard_wall_seconds':30 if pilot else 180","'hard_wall_seconds':30 if pilot else 360")
            else:
                s=change(s,"'hard_wall_seconds':180","'hard_wall_seconds':360");s=change(s,'timeout=180','timeout=360')
        patches.append({'kind':'finite_resource_contract','weighted_seconds':120,'linear_seconds':360,'threads':1,'worker_MiB':256,'note':'Only wall-time allowances change; mathematical premises and finite workloads retained.'})
        (core/name).write_text(s,encoding='utf8')
        journal.append({'file':name,'original_sha256':sha(src),'executed_sha256':sha(core/name),'patches':patches})
    # The author pin is set after its final source was written, including resource edits.
    assert sha(core/'asian-linear-certificate.py') in (core/'check-asian-linear.py').read_text(encoding='utf8')
    write(dest/'preflight.json',pre)
    receipt={'status':'PREPARED_NOT_EXECUTED','input':pre,'baseline_package_integrity':package,'environment':environment,
        'generator_sha256':sha(__file__),'preflight_sha256':sha(dest/'preflight.json'),'scope_sha256':sha(dest/'work'/'SCOPE.md'),
        'resource_helper_sha256':sha(core/'resource_limits.py'),'source_patches':journal,'jobs':[],'references_modified':False}
    write(dest/'receipt.json',receipt);print(json.dumps({'status':receipt['status'],'directory':str(dest),'theta':pre['theta']}),flush=True)

JOBS=[('asian-W','asian-remainder-certificate.py',[],'asian-remainder-result.json',135),
      ('asian-pilot','asian-linear-certificate.py',['--pilot'],'asian-linear-pilot-result.json',45),
      ('asian-linear','asian-linear-certificate.py',[],'asian-linear-result.json',375),
      ('asian-W-check','check-asian-remainder.py',[],'check-asian-remainder-result.json',135),
      ('asian-linear-check','check-asian-linear.py',[],'check-asian-linear-result.json',375)]
EXPECTED_STATUS={'asian-W':'CERTIFIED_ORIGINAL_ASIAN_WEIGHTED_REMAINDER_ONLY',
    'asian-pilot':'PILOT_ONLY_NO_PRICE_CLAIM','asian-linear':'COMPLETE_ORIGINAL_ASIAN_PQ_CERTIFICATE',
    'asian-W-check':'NONAUTHOR_FULL_WEIGHTED_REMAINDER_RECOMPUTATION_PASS',
    'asian-linear-check':'INDEPENDENT_FULL_ORIGINAL_ASIAN_CERTIFICATE_PASS'}

def require(ok,message):
    if not ok:raise RuntimeError(message)

def validate_result(id,result,core,source):
    """Reject partial/stopped output, without changing any numerical formula."""
    require(isinstance(result,dict),'Result is not a JSON object')
    require(result.get('status')==EXPECTED_STATUS[id],'Unexpected numerical result status')
    require(result.get('source_sha256')==sha(source),'Result source binding failed')
    require(result.get('scope_sha256')==sha(core.parent/'SCOPE.md'),'Result scope binding failed')
    require(result.get('precision_bits')==(384 if id.endswith('check') else 256),'Wrong arithmetic precision')
    def fields(keys):require(all(k in result for k in keys),'Incomplete result: missing required fields')
    def interval_record(value,label):
        require(isinstance(value,dict) and isinstance(value.get('exact_interval'),list) and len(value['exact_interval'])==2,
            'Incomplete interval record: '+label)
        require(isinstance(value.get('outward24'),list) and len(value['outward24'])==2,'Missing outward endpoints: '+label)
        require(all(isinstance(v,str) for v in value['exact_interval']+value['outward24']),'Non-string exact endpoints: '+label)
        lo,hi=map(F,value['exact_interval']);dl,du=map(F,value['outward24'])
        require(dl<=lo<=hi<=du,'Invalid interval or outward endpoints: '+label)
    def points(key,count):
        require(isinstance(result.get(key),list) and len(result[key])==count,'Incomplete '+key)
        for point in result[key]:interval_record(point,key)
    def rational_intervals(x):
        if isinstance(x,dict):
            if 'exact_interval' in x:
                require(isinstance(x['exact_interval'],list) and len(x['exact_interval'])==2,'Incomplete exact interval')
                lo,hi=map(F,x['exact_interval']);require(lo<=hi,'Reversed exact interval')
                require(isinstance(x.get('outward24'),list) and len(x['outward24'])==2,'Missing outward endpoints')
                dl,du=map(F,x['outward24']);require(dl<=lo<=hi<=du,'Invalid outward endpoints')
            for value in x.values():rational_intervals(value)
        elif isinstance(x,list):
            for value in x:rational_intervals(value)
    if id in ('asian-W','asian-W-check'):
        points('all_points_P',257);points('all_points_Q',129)
        if id=='asian-W':
            fields(('theta','c','h','P_nodes','Q_nodes','catalog_profiles','projection_beta_min','Q_per_profile_projection_bound',
                'Q_square_expansion_point_error','P_integral_tail_upper','Q_integral_tail_upper','WP_lower_bound','WP_upper_bound',
                'WQ_lower_bound','WQ_upper_bound','discounted_bias_remainder_lower_bound','discounted_bias_remainder_upper_bound',
                'discounted_bias_remainder_center','discounted_bias_remainder_radius','original_remainder_radius_target_pass'))
            require(result['counts']=={'Q_steps':815360,'P_month_blocks':24388},'Incomplete weighted finite workload')
            require(result['theta']==['3','9/200','23/100','-11/20','1/25'] and result['h']=='1/768','Wrong point inputs')
            require(result['P_nodes']==257 and result['Q_nodes']==129 and result['catalog_profiles']==91,'Wrong weighted grid')
            interval_fields=('Q_per_profile_projection_bound','Q_square_expansion_point_error','P_integral_tail_upper',
                'Q_integral_tail_upper','WP_lower_bound','WP_upper_bound','WQ_lower_bound','WQ_upper_bound',
                'discounted_bias_remainder_lower_bound','discounted_bias_remainder_upper_bound',
                'discounted_bias_remainder_center','discounted_bias_remainder_radius')
        else:
            fields(('projection_beta','projection_bound','point_projection_fee','P_tail','Q_tail','WP_lower_bound','WP_upper_bound',
                'WQ_lower_bound','WQ_upper_bound','remainder_lower_bound','remainder_upper_bound','remainder_radius','exact_scalar_overlap_checks'))
            require(result['counts']=={'P_blocks':24388,'Q_steps':815360},'Incomplete independent weighted workload')
            require(result['P_all_node_interval_overlap_checks']==257 and result['Q_all_node_independent_interval_containment_checks']==129,
                'Incomplete independent weighted checks')
            interval_fields=('projection_bound','point_projection_fee','P_tail','Q_tail','WP_lower_bound','WP_upper_bound',
                'WQ_lower_bound','WQ_upper_bound','remainder_lower_bound','remainder_upper_bound','remainder_radius')
    else:
        n=8 if id=='asian-pilot' else 641
        require(isinstance(result.get('frequency_rows'),list) and len(result['frequency_rows'])==n,'Incomplete frequency_rows')
        for i,row in enumerate(result['frequency_rows']):
            require(isinstance(row,dict) and row.get('n')==i,'Incomplete frequency index sequence')
            keys=('P_term','Q_proxy_term' if id.endswith('check') else 'proxy_term','coefficient_sum')
            require(all(k in row for k in keys),
                'Incomplete frequency row')
            for key in keys:interval_record(row[key],key)
        if id=='asian-pilot':
            fields(('P_linear_finite','Q_proxy_linear_finite','linear_bias_finite','coefficient_abs_sum','full_linear_time_estimate'))
            require(result['frequencies']==8 and result['counts']=={'Q_layers':79872,'P_full_path_branch_guards':9984,'profiles':104},
                'Incomplete pilot workload')
            interval_fields=('P_linear_finite','Q_proxy_linear_finite','linear_bias_finite','coefficient_abs_sum')
        elif id=='asian-linear':
            fields(('P_linear_finite','Q_proxy_linear_finite','linear_bias_finite','coefficient_abs_sum','projection_beta_min',
                'projection_delta','projection_price_fee','Q_firstmonth_Laplace_upper','P_frequency_tail','Q_frequency_tail',
                'one_law_alias','total_linear_bias_fee','true_linear_bias','true_original_Asian_bias','true_original_Asian_P',
                'true_original_Asian_Q','bias_absolute_upper','original_theta_star_Asian_pass_0025'))
            require(result['frequencies']==641 and result['counts']=={'Q_layers':6399744,'P_full_path_branch_guards':799968,'profiles':8333},
                'Incomplete full linear workload')
            interval_fields=('P_linear_finite','Q_proxy_linear_finite','linear_bias_finite','coefficient_abs_sum',
                'projection_delta','projection_price_fee','Q_firstmonth_Laplace_upper','P_frequency_tail','Q_frequency_tail',
                'one_law_alias','total_linear_bias_fee','true_linear_bias','true_original_Asian_bias','true_original_Asian_P','true_original_Asian_Q')
        else:
            fields(('fees','linear_bias_finite','coefficient_abs_sum','true_original_Asian_bias','true_original_Asian_P',
                'true_original_Asian_Q','original_theta_star_Asian_pass_0025'))
            require(result['counts']=={'Q_layers':6399744,'P_path_guards':799968,'frequency_real_interval_overlaps':1923},
                'Incomplete independent linear workload')
            require(set(result['fees'])=={'projection_delta','projection_price_fee','Q_firstmonth_Laplace_upper','P_frequency_tail',
                'Q_frequency_tail','one_law_alias','total_linear_bias_fee'},'Incomplete independent fee ledger')
            for key,value in result['fees'].items():interval_record(value,key)
            interval_fields=('linear_bias_finite','coefficient_abs_sum','true_original_Asian_bias','true_original_Asian_P','true_original_Asian_Q')
    for key in interval_fields:interval_record(result[key],key)
    if id!='asian-W':
        require(result.get('weighted_square_result_sha256',result.get('author_result_sha256') if id=='asian-W-check' else None)
            ==sha(core/'asian-remainder-result.json'),'Weighted result binding failed')
    if id.endswith('check'):
        author='asian-remainder' if id=='asian-W-check' else 'asian-linear'
        require(result.get('author_source_sha256')==sha(core/(author+'-certificate.py')) and
            result.get('author_result_sha256')==sha(core/(author+'-result.json')),'Independent author binding failed')
    rational_intervals(result)

def execute_job(command,env,source,out,log,seconds,validator):
    """Owned real subprocess boundary. Timeout is always failure, even after output."""
    started=time.perf_counter();p=None
    row={'source_sha256':sha(source),'external_timeout_seconds':seconds,'timed_out':False,'reaped':False,'returncode':None}
    try:
        require(not out.exists(),'Refuse pre-existing result output')
        with log.open('x',encoding='utf8') as stream:
            p=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,env=env,creationflags=0x08000000)
            row['pid']=p.pid
            try:p.wait(timeout=seconds)
            except subprocess.TimeoutExpired:
                row['timed_out']=True
                try:
                    killed=subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],stdout=stream,stderr=subprocess.STDOUT,
                        creationflags=0x08000000,timeout=15)
                    row['taskkill_returncode']=killed.returncode
                except Exception as exc:row['taskkill_error']=str(exc)
                finally:
                    try:p.wait(timeout=15)
                    except subprocess.TimeoutExpired:p.kill();p.wait(timeout=15)
                row.update(returncode=p.returncode,reaped=p.returncode is not None)
                raise RuntimeError('External timeout stopped the owned process tree; output is not accepted')
        row.update(returncode=p.returncode,reaped=p.returncode is not None)
        require(p.returncode==0,'Nonzero subprocess return code '+str(p.returncode))
        require(out.is_file(),'Missing numerical result output')
        result=read(out);validator(result)
        row.update(status='COMPLETE',result=out.name,result_sha256=sha(out),numerical_status=result['status'])
    except Exception as exc:
        if p is not None and p.poll() is None:
            p.kill();p.wait(timeout=15)
        if p is not None:row.update(returncode=p.returncode,reaped=p.returncode is not None)
        row.update(status='STOPPED',reason=str(exc))
    row['seconds']=time.perf_counter()-started
    return row

def run_prepared(dest,env,environment,jobs,validator,finalizer):
    """Production orchestration, also exercised with controlled non-numerical jobs."""
    receipt=read(dest/'receipt.json');core=dest/'work'/'core'
    require(receipt['status']=='PREPARED_NOT_EXECUTED','Run is not fresh and prepared')
    require(not (dest/'result-capsule.json').exists(),'Refuse pre-existing final capsule')
    receipt.update(status='RUNNING',execution_environment=environment);write(dest/'receipt.json',receipt)
    for id,name,args,filename,seconds in jobs:
        source=core/name;log=dest/(id+'.log')
        row=execute_job([sys.executable,'-B','-X','utf8',str(source)]+args,env,source,core/filename,log,seconds,
            lambda result:validator(id,result,core,source))
        row.update(id=id,file=name,log=log.name);receipt['jobs'].append(row)
        if row['status']!='COMPLETE':
            receipt['status']='STOPPED';write(dest/'receipt.json',receipt)
            print(json.dumps({'status':'STOPPED','job':id,'receipt':str(dest/'receipt.json'),'reason':row['reason']}),flush=True)
            return 1
        write(dest/'receipt.json',receipt)
        print(json.dumps({'status':'COMPLETE','job':id,'seconds':row['seconds']}),flush=True)
    receipt.update(status='COMPLETE',all_five_jobs_completed=len(jobs)==5,independent_all_nodes_frequencies_and_fees_pass=len(jobs)==5)
    write(dest/'receipt.json',receipt)
    try:finalizer(dest,dest/'result-capsule.json')
    except Exception as exc:
        final=dest/'result-capsule.json'
        if final.exists():final.rename(dest/'failed-capsule-artifact.json')
        receipt.update(status='STOPPED',reason='Final capsule verification failed: '+str(exc))
        write(dest/'receipt.json',receipt);print(json.dumps({'status':'STOPPED','reason':receipt['reason']}),flush=True);return 1
    return 0

def run(dest):
    try:
        require(not sys.flags.optimize and not os.environ.get('PYTHONOPTIMIZE'),'Optimized Python is prohibited')
        baseline=load_module('round2_base',CODE/'run.py');env,environment=baseline.environment()
        receipt=read(dest/'receipt.json');core=dest/'work'/'core'
        for j in receipt['source_patches']:require(sha(core/j['file'])==j['executed_sha256'],'Prepared source binding failed')
        require(receipt['generator_sha256']==sha(__file__),'Prepared runner binding failed')
        require(receipt['preflight_sha256']==sha(dest/'preflight.json') and receipt['scope_sha256']==sha(dest/'work'/'SCOPE.md'),
            'Prepared preflight or scope binding failed')
        require(receipt['resource_helper_sha256']==sha(core/'resource_limits.py'),'Prepared resource-helper binding failed')
        return run_prepared(dest,env,environment,JOBS,validate_result,capsule)
    except Exception as exc:
        receipt=read(dest/'receipt.json');receipt.update(status='STOPPED',reason=str(exc));write(dest/'receipt.json',receipt)
        print(json.dumps({'status':'STOPPED','receipt':str(dest/'receipt.json'),'reason':str(exc)}),flush=True);return 1

def capsule(dest,out):
    require(not out.exists(),'Refuse pre-existing final capsule')
    r=read(dest/'receipt.json');assert r['status']=='COMPLETE' and len(r['jobs'])==5
    core=dest/'work'/'core'
    for j in r['jobs']:
        assert j['status']=='COMPLETE' and j['returncode']==0 and not j.get('timed_out',False) and j.get('reaped',True)
        assert sha(core/j['file'])==j['source_sha256'] and sha(core/j['result'])==j['result_sha256']
        validate_result(j['id'],read(core/j['result']),core,core/j['file'])
    budget=load_module('round2_budget',CODE/'revision'/'read_budget.py')
    row=budget.certificate(core,'1/768',dest/'receipt.json')
    w=read(core/'asian-remainder-result.json');a=read(core/'asian-linear-result.json');c=read(core/'check-asian-linear-result.json');cw=read(core/'check-asian-remainder-result.json')
    assert w['theta']==r['input']['theta']
    assert c['author_source_sha256']==sha(core/'asian-linear-certificate.py') and c['author_result_sha256']==sha(core/'asian-linear-result.json')
    assert cw['author_source_sha256']==sha(core/'asian-remainder-certificate.py') and cw['author_result_sha256']==sha(core/'asian-remainder-result.json')
    cap={'status':'COMPLETE_NEW_STOCHASTIC_HESTON_POINT_CERTIFICATE','scope':r['input']['scope'],'input':r['input'],
         'six_component_exact_width_ledger':row,'principal_bias_Q_minus_P':a['true_original_Asian_bias'],
         'independent_bias_Q_minus_P':c['true_original_Asian_bias'],'principal_P_price':a['true_original_Asian_P'],
         'principal_Q_price':a['true_original_Asian_Q'],'independent_P_price':c['true_original_Asian_P'],'independent_Q_price':c['true_original_Asian_Q'],
         'recorded_five_job_seconds':sum(j['seconds'] for j in r['jobs']),'receipt_sha256':sha(dest/'receipt.json'),
         'preflight_sha256':sha(dest/'preflight.json'),'capsule_generator_sha256':sha(__file__),
         'independent_weighted_checks':{'P_nodes':cw['P_all_node_interval_overlap_checks'],'Q_nodes':cw['Q_all_node_independent_interval_containment_checks'],'precision_bits':cw['precision_bits']},
         'independent_linear_checks':c['counts'],'no_claim':['No parameter-box or prior-region certificate.','No stochastic-Heston weak leading coefficient is computed.']}
    pending=out.with_suffix('.pending');write(pending,cap);pending.replace(out)
    print(json.dumps({'status':cap['status'],'output':str(out),'bias':cap['principal_bias_Q_minus_P']['outward24'],
              'width':row['interval_width']['outward_decimal_upper'],'seconds':cap['recorded_five_job_seconds']}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True)
    for mode in ('prepare','run','capsule'):
        s=sub.add_parser(mode);s.add_argument('--directory',type=Path,required=True)
        if mode=='capsule':s.add_argument('--output',type=Path,required=True)
    a=p.parse_args();dest=a.directory.resolve()
    if a.mode=='prepare':prepare(dest)
    elif a.mode=='run':sys.exit(run(dest))
    else:capsule(dest,a.output.resolve())
