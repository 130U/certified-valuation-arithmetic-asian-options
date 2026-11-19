"""Finite Gaussian certificates for the unchanged AE scheme on xi=0 only.

No simulation, no multi-dimensional quadrature, no stochastic-Heston TT claim.
The controller records the source hash before one bounded worker is launched.
"""
from pathlib import Path
from fractions import Fraction as F
import ctypes, hashlib, importlib.util, json, os, subprocess, sys, time

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
HELPER =HERE/'resource_limits.py'
SPEC = importlib.util.spec_from_file_location('tt_resource_helper', HELPER)
RESOURCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RESOURCE)
OUT = HERE / 'deterministic-tt-result.json'
PREFREEZE = HERE / 'deterministic-tt-contract.json'
CONTROL = HERE / 'deterministic-tt-controller.json'
CONSOLE = HERE / 'deterministic-tt-console.txt'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def worker():
    assert not OUT.exists()
    start = time.perf_counter()
    RESOURCE.hard_job()
    for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        os.environ[key] = '1'
    from flint import arb, fmpq, ctx
    ctx.threads = 1
    def ar(x):
        x = F(x)
        return arb(fmpq(x.numerator, x.denominator))
    def lo(x): return F(str(x.lower().fmpq()))
    def hi(x): return F(str(x.upper().fmpq()))
    def rec(x):
        return {'exact_interval': [str(lo(x)), str(hi(x))],
                'outward24': RESOURCE.decimal_enclosure(lo(x), hi(x))}
    def upper_abs(x): return ar(max(abs(lo(x)), abs(hi(x))))
    def normal_cdf(x): return (1 + (x / ar(2).sqrt()).erf()) / 2
    def put(S, K, r, T, I):
        d1 = ((S/K).log() + r*T + I/2) / I.sqrt()
        d2 = d1-I.sqrt()
        return K*(-r*T).exp()*normal_cdf(-d2)-S*normal_cdf(-d1)
    runs = []
    for bits in (384, 512):
        ctx.prec = bits
        h=ar(F(1,768)); k=ar(3); vb=ar(F(9,200)); dv=ar(F(3,200))
        S=ar(100); r=ar(F(1,100)); eta=1-k*h
        u=ar(F(1,400)); upoint=ar(F(3,800))
        times=[ar(F(m,12)) for m in range(13)]
        I=[]; Ih=[]; linear=[]; RI=[]; e=[]
        for m,t in enumerate(times):
            ex=(-k*t).exp()
            I.append(vb*t+dv*(1-ex)/k)
            Ih.append(vb*t+dv*(1-eta**(64*m))/k)
            linear.append(dv*k*t*ex/2)
            RI.append(dv*ex*(k*k*t/(3*eta)+k**3*t*t/(8*eta**2)))
            e.append((ex-eta**(64*m))/k)
        steps=[]; TV2=ar(0); point_affinity=ar(1)
        fisher_u=ar(0); fisher_p=ar(0)
        term1=ar(0); term2=ar(0); term1p=ar(0); term2p=ar(0)
        for m in range(1,13):
            s=I[m]-I[m-1]; sh=Ih[m]-Ih[m-1]
            delta=sh-s; a=linear[m]-linear[m-1]; Rm=RI[m]+RI[m-1]
            assert lo(s-upoint)>=0 and lo(sh-upoint)>=0
            delta_sup=upper_abs(dv*(e[m]-e[m-1]))
            a_sup=upper_abs(a)
            tvterm=delta_sup**2*(1/(8*u*u)+1/(16*u))
            TV2+=tvterm
            point_affinity *= (2*(s*sh).sqrt()/(s+sh)).sqrt()*(-delta*delta/(16*(s+sh))).exp()
            fisher_u+=a*a*(1/(2*u*u)+1/(4*u))
            fisher_p+=a*a*(1/(2*s*s)+1/(4*s))
            term1+=Rm*Rm*(1/(2*u*u)+1/(4*u))
            term2+=(a_sup+h*Rm)**2*(2/(u*u)+1/(2*u))
            term1p+=Rm*Rm*(1/(2*upoint*upoint)+1/(4*upoint))
            term2p+=(a_sup+h*Rm)**2*(2/(upoint*upoint)+1/(2*upoint))
            assert hi(upper_abs(delta-h*a)-h*h*Rm)<=0
            steps.append({'m':m,'s':rec(s),'s_h':rec(sh),'delta':rec(delta),
                          'first_variance_coefficient':rec(a),'variance_remainder_upper':rec(Rm)})
        TV=TV2.sqrt(); point_TV=(1-point_affinity**2).sqrt()
        C_density=term1.sqrt()+term2/2
        Cp_density=term1p.sqrt()+term2p/2
        Asian=15*(-r).exp()*TV
        Asian_point=15*(-r).exp()*point_TV
        Asian_R=ar(F(15,2))*(-r).exp()*C_density*h*h
        Asian_Rpoint=ar(F(15,2))*(-r).exp()*Cp_density*h*h
        beta_As_bound=ar(F(15,2))*(-r).exp()*fisher_p.sqrt()
        beta_As_uniform=ar(F(15,2))*(-r).exp()*fisher_u.sqrt()
        assert hi(Asian)<F(1,40)
        rows=[]
        for m in (3,6,12):
            T=times[m]; delta=Ih[m]-I[m]
            minI=ar(F(3,100))*T
            upper_vega=S/(2*(2*arb.pi()*minI).sqrt())
            put_bias_uniform=upper_vega*upper_abs(delta)
            for Kf in (90,100,110):
                K=ar(Kf)
                P=put(S,K,r,T,I[m]); Q=put(S,K,r,T,Ih[m])
                d1=((S/K).log()+r*T+I[m]/2)/I[m].sqrt()
                vegaI=S*(-d1*d1/2).exp()/(2*(2*arb.pi()*I[m]).sqrt())
                beta=linear[m]*vegaI
                remainder=Q-P-h*beta
                Rgeneric=K/2*(-r*T).exp()*C_density*h*h
                assert lo(beta)>0
                assert hi(upper_abs(Q-P))<=hi(put_bias_uniform)
                assert hi(upper_abs(remainder))<=hi(Rgeneric)
                assert hi(put_bias_uniform)<F(1,40)
                rows.append({'T':str(F(m,12)),'K':Kf,'P':rec(P),'Q':rec(Q),
                             'signed_bias_Q_minus_P':rec(Q-P),'TT_coefficient':rec(beta),
                             'true_remainder_at_h':rec(remainder),'generic_TT_remainder_upper':rec(Rgeneric),
                             'uniform_v0_put_bias_upper':rec(put_bias_uniform)})
        runs.append({'precision_bits':bits,'steps':steps,'uniform_TV_upper':rec(TV),
                     'point_Hellinger_TV_upper':rec(point_TV),'density_remainder_C':rec(C_density),
                     'Asian_uniform_bias_upper':rec(Asian),'Asian_point_bias_upper':rec(Asian_point),
                     'Asian_uniform_TT_remainder_upper':rec(Asian_R),
                     'Asian_point_TT_remainder_upper':rec(Asian_Rpoint),
                     'Asian_TT_coefficient_absolute_upper_point':rec(beta_As_bound),
                     'Asian_TT_coefficient_absolute_upper_uniform':rec(beta_As_uniform),'puts':rows})
    scalar_keys=[key for key,value in runs[0].items() if isinstance(value,dict) and 'exact_interval' in value]
    overlap_checks=0
    for key in scalar_keys:
        a,b=map(F,runs[0][key]['exact_interval']);c,d=map(F,runs[1][key]['exact_interval'])
        assert max(abs(a-d),abs(b-c)) < F(1,10**80);overlap_checks+=1
    for row0,row1 in zip(runs[0]['puts'],runs[1]['puts']):
        for key in ('P','Q','signed_bias_Q_minus_P','TT_coefficient','true_remainder_at_h'):
            a,b=map(F,row0[key]['exact_interval']);c,d=map(F,row1[key]['exact_interval'])
            assert max(a,c)<=min(b,d);overlap_checks+=1
    result={'status':'CERTIFIED_DETERMINISTIC_VARIANCE_TEN_PAYOFF_BIAS_AND_TT',
            'scope':'xi=0 only; original AE updates and twelve fixings retained; not original positive-xi domain',
            'source_sha256':sha(__file__),'resource_helper_sha256':sha(HELPER),
            'inputs':{'kappa':'3','vbar':'9/200','xi':'0','v0_uniform':['3/100','3/50'],
                      'v0_point':'3/50','h':'1/768','S0':'100','r':'1/100','fixings':'m/12, m=1,...,12',
                      'put_K':[90,100,110],'put_T':['1/4','1/2','1'],'Asian_K':['95','110']},
            'runs':runs,'cross_precision_checks':overlap_checks,'comparison_note':'Conservative endpoints depend on precision: their change is below 1e-80; 45 actual-price/coefficient/remainder intervals must overlap',
            'Asian_coefficient_computed_as_scalar':False,
            'Asian_coefficient_has_exact_score_formula_and_rigorous_enclosure':True,
            'joint_TT_vector_nonzero_certified_by_all_nine_put_coefficients':True,
            'SDE_paths':0,'multidimensional_quadrature_calls':0,'threads':1,
            'job_limit_bytes':256<<20,'worker_seconds':time.perf_counter()-start}
    with OUT.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2)
    print(json.dumps({'status':result['status'],'Asian_uniform_bias_upper':runs[-1]['Asian_uniform_bias_upper']['outward24'],
                      'Asian_uniform_TT_remainder_upper':runs[-1]['Asian_uniform_TT_remainder_upper']['outward24'],
                      'worker_seconds':result['worker_seconds']}))

def controller():
    assert all(not p.exists() for p in (OUT,PREFREEZE,CONTROL,CONSOLE))
    mem=RESOURCE.MEMORY();mem.length=ctypes.sizeof(mem)
    assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    contract={'source_sha256':sha(__file__),'resource_helper_sha256':sha(HELPER),
              'available_commit_bytes':mem.available_commit,'available_physical_bytes':mem.available_physical,
              'required_available_bytes':512<<20,'job_limit_bytes':256<<20,'hard_wall_seconds':60,
              'threads':1,'precisions':[384,512],'attempts':0,
              'scope':'deterministic xi=0; 12 increment scalars and 9 Black prices per precision'}
    with PREFREEZE.open('x',encoding='utf-8') as stream:json.dump(contract,stream,indent=2)
    if min(mem.available_commit,mem.available_physical)<512<<20:
        contract['status']='NOT_RUN_MEMORY_PREFLIGHT'
    else:
        start=time.perf_counter();contract['attempts']=1
        with CONSOLE.open('x',encoding='utf-8') as stream:
            child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'--worker'],
                                   stdout=stream,stderr=subprocess.STDOUT,creationflags=0x08000000)
            try:
                child.wait(timeout=60)
                contract.update(status='FINISHED',returncode=child.returncode)
            except subprocess.TimeoutExpired:
                child.kill();child.wait();contract.update(status='HARD_WALL_STOPPED',returncode=child.returncode)
        contract['outer_seconds']=time.perf_counter()-start
    with CONTROL.open('x',encoding='utf-8') as stream:json.dump(contract,stream,indent=2)
    print(json.dumps(contract))

if __name__=='__main__':
    worker() if '--worker' in sys.argv else controller()
