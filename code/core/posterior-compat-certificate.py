"""Finite positive-xi P/Q posterior transport certificate on a specified 3D prior.

No Asian price approximation: a proved density-score Lipschitz bound transfers
the certified parameter quantile coupling to the true Asian price quantiles.
"""
from pathlib import Path
from fractions import Fraction as F
import bisect, ctypes, hashlib, importlib.util, json, os, sys, time

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
SOURCE=HERE.parent/'data'/'synthetic_quotes.json'
LIMITS=HERE/'resource_limits.py'
spec=importlib.util.spec_from_file_location('resource_limits',LIMITS)
limits=importlib.util.module_from_spec(spec);spec.loader.exec_module(limits)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    cells=int(sys.argv[1]) if len(sys.argv)>1 else 4096
    assert cells in (4096,16384)
    out=HERE/f'posterior-compat-{cells}-result.json'
    assert not out.exists(), 'preserve completed receipt'
    source_hash=sha(__file__); input_hash=sha(SOURCE)
    mem=limits.MEMORY();mem.length=ctypes.sizeof(mem)
    assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    prepath=HERE/f'posterior-compat-{cells}-contract.json'
    assert not prepath.exists()
    pre={'source_sha256':source_hash,'quotes_sha256':input_hash,
         'scope_before_execution_sha256':sha(HERE.parent/'SCOPE.md'),
         'perturbation_scope_sha256':sha(HERE.parent/'SCOPE.md'),
         'original_zero_xi_result_sha256':sha(HERE/'posterior-zero-4096-result.json'),
         'cells':cells,'available_commit_bytes':mem.available_commit,
         'available_physical_bytes':mem.available_physical,'required_available_bytes':512<<20,
         'job_limit_bytes':256<<20,'polling_wall_guard_seconds':90,'threads':1,
         'permitted_grid_sequence':[4096,16384],'attempts':1,
         'prior':'independent uniform v0[.03,.06],xi[1e-7,1e-6],rho[-.8,-.3]; kappa3,vbar.045',
         'status':'PREFLIGHT_OK' if min(mem.available_commit,mem.available_physical)>=512<<20 else 'NOT_RUN_MEMORY_PREFLIGHT'}
    prepath.write_text(json.dumps(pre,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if pre['status']!='PREFLIGHT_OK':
        print(json.dumps(pre));return
    limits.hard_job(); start=time.perf_counter()
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
        os.environ[key]='1'
    from flint import arb, fmpq, ctx
    ctx.prec=192;ctx.threads=1
    def ar(x):
        x=F(x);return arb(fmpq(x.numerator,x.denominator))
    def lo(x):return F(str(x.lower().fmpq()))
    def hi(x):return F(str(x.upper().fmpq()))
    def box(a,b):
        assert a<=b
        return arb(ar((a+b)/2),ar((b-a)/2))
    def rec(x):
        a,b=lo(x),hi(x)
        return {'exact_interval':[str(a),str(b)],'outward18':limits.decimal_enclosure(a,b,18)}
    def exactrec(a,b):
        return {'exact_interval':[str(a),str(b)],'outward18':limits.decimal_enclosure(a,b,18)}
    y=[F.from_float(x) for x in json.loads(SOURCE.read_text(encoding='utf-8'))['quotes']]
    assert len(y)==9
    h=F(1,768);kap=F(3);vb=F(9,200);left=F(3,100);right=F(3,50)
    width=(right-left)/cells
    eta=ar(1-kap*h);r=ar(F(1,100));a=ar(left);vbar=ar(vb)
    times=(F(1,4),F(1,2),F(1))
    def loading(model,t):
        return (1-(-ar(kap*t)).exp())/ar(kap) if model=='P' else (1-eta**int(t/h))/ar(kap)
    load={m:[loading(m,t) for t in times] for m in ('P','Q')}
    dis=[(-r*ar(t)).exp() for t in times]
    xi_upper=ar(F(1,10**6));v_min=ar(F(3,100));v_max=ar(F(3,50))
    coupling_C={'P':ar(F(1,10)),'Q':ar(F(1,5))}
    assert F(1,10)**2==F(3,50)/(2*kap)
    assert F(1,5)**2==2*F(3,50)/kap
    assert xi_upper<(ar(kap)*v_max/2).sqrt()
    price_radius={};target_radius={}
    for model in ('P','Q'):
        price_radius[model]=[]
        for ti,t in enumerate(times):
            log_radius=xi_upper*coupling_C[model]*(ar(t)/2+2*(ar(t)/v_min).sqrt())
            price_radius[model].extend([ar(k)*dis[ti]*log_radius for k in (90,100,110)])
        target_radius[model]=110*(-r).exp()*xi_upper*coupling_C[model]*(ar(F(1,2))+2/ar(F(3,100)).sqrt())
    normal=lambda x:(1+(x/ar(2).sqrt()).erf())/2
    logs=[ar(F(100,k)).log() for k in (90,100,110)]
    def prices(model,u):
        values=[]
        for ti,t in enumerate(times):
            variance=vbar*ar(t)+(u-vbar)*load[model][ti]
            assert variance>0
            sd=variance.sqrt()
            for ki,k in enumerate((90,100,110)):
                d1=(logs[ki]+r*ar(t)+variance/2)/sd;d2=d1-sd
                p=ar(k)*dis[ti]*normal(-d2)-100*normal(-d1)
                values.append((lo(p),hi(p)))
        return values
    scale=1<<96
    def outward_weight(w):
        low=max(F(0),lo(w));up=min(F(1),hi(w))
        wl=low.numerator*scale//low.denominator
        wu=-((-up.numerator*scale)//up.denominator)
        assert 0<wl<=wu<=scale
        return [wl,wu]
    weights={m:{'d1':[],'d9':[]} for m in ('P','Q')}
    for model in ('P','Q'):
        previous=prices(model,ar(left))
        for i in range(cells):
            current=prices(model,ar(left+(i+1)*width))
            # Positive Black vega and positive integrated-variance loading give
            # whole-cell inclusion from the two exact endpoint price values.
            residual=[box(previous[k][0]-hi(price_radius[model][k])-y[k],
                          current[k][1]+hi(price_radius[model][k])-y[k]) for k in range(9)]
            for name,rr in (('d1',[residual[7]]),('d9',residual)):
                d=len(rr)
                quadratic=3*sum((x*x for x in rr),arb(0))
                quadratic+=sum(((rr[j]-rr[k])**2 for j in range(d) for k in range(j+1,d)),arb(0))
                potential=ar(F(32,27*(d+3)))*quadratic
                weights[model][name].append(outward_weight((-potential).exp()))
            previous=current
            if i%256==0:assert time.perf_counter()-start<90,'finite wall-time guard'
    def cdf_envelope(rows):
        total_l=sum(x[0] for x in rows);total_u=sum(x[1] for x in rows)
        lows=[F(0)];ups=[F(0)];pl=pu=0
        for wl,wu in rows:
            pl+=wl;pu+=wu
            lows.append(F(pl,pl+total_u-pu))
            ups.append(F(pu,pu+total_l-pl))
        assert lows[-1]==ups[-1]==1
        assert all(x<=z for x,z in zip(lows,ups))
        return lows,ups,exactrec(F(total_l,scale*cells),F(total_u,scale*cells))
    # Exact one-dimensional quantile coupling: possible probability ranges for
    # each parameter cell are [CDF_lower(left), CDF_upper(right)].
    transports={}
    for name in ('d1','d9'):
        lp,up,zp=cdf_envelope(weights['P'][name])
        lq,uq,zq=cdf_envelope(weights['Q'][name])
        maxsteps=0;witness=None
        for i in range(cells):
            jmin=max(0,bisect.bisect_left(uq,lp[i])-1)
            jmax=min(cells-1,bisect.bisect_right(lq,up[i+1])-1)
            assert jmin<=jmax
            steps=max(abs(i-(jmax+1)),abs(i+1-jmin))
            if steps>maxsteps:maxsteps=steps;witness=[i,jmin,jmax]
        def qparam(ll,uu,p):
            il=max(0,bisect.bisect_left(uu,p)-1)
            ir=min(cells,bisect.bisect_left(ll,p))
            return exactrec(left+il*width,left+ir*width)
        transports[name]={'normalizer_P':zp,'normalizer_Q':zq,
            'all_p_parameter_Winfinity_bound':str(maxsteps*width),
            'max_grid_steps':maxsteps,'max_steps_witness_Pcell_Qrange':witness,
            'parameter_quantile_brackets':{
                m:{str(p):qparam(ll,uu,p) for p in (F(1,40),F(39,40))}
                for m,ll,uu in (('P',lp,up),('Q',lq,uq))}}
    # Twelve independent log-increment variances. The Asian target is the true
    # bounded [0,15 exp(-r)] call spread of the arithmetic average, not a proxy.
    increment=[];Iparam=arb(0);Ischeme=arb(0)
    for j in range(1,13):
        t0=F(j-1,12);t1=F(j,12)
        ac=loading('P',t1)-loading('P',t0)
        aq=loading('Q',t1)-loading('Q',t0)
        zc=vbar/ar(12)+(a-vbar)*ac
        zq=vbar/ar(12)+(a-vbar)*aq
        zmin=min(lo(zc),lo(zq));assert zmin>0
        delta=ar(F(3,200))*abs(aq-ac)
        Iparam+=ac*ac*(1/(2*zc*zc)+1/(4*zc))
        Ischeme+=delta*delta*(1/(2*ar(zmin)**2)+1/(4*ar(zmin)))
        increment.append({'j':j,'P_loading':rec(ac),'Q_loading':rec(aq),
            'variance_min':str(zmin),'max_same_parameter_variance_difference':rec(delta)})
    B=15*(-r).exp();L=B*Iparam.sqrt()/2;eps=B*Ischeme.sqrt()/2
    for name in transports:
        dv=F(transports[name]['all_p_parameter_Winfinity_bound'])
        bound=eps+target_radius['P']+target_radius['Q']+L*ar(dv)
        transports[name]['all_target_quantile_levels_absolute_PQ_difference_bound']=rec(bound)
        transports[name]['p025_and_p975_each_pass_0.10']=hi(bound)<F(1,10)
    result={'scope':'kappa=3,vbar=.045; independent uniform v0[.03,.06],xi[1e-7,1e-6],rho[-.8,-.3]; original positive-xi P/Q and actual 12-fixing Asian; not original 5D prior',
        'scheme':'V(n+1)=(Vn+3(.045-Vn)/768)+; X increments current Vn; N=768',
        'source_sha256':source_hash,'quotes_source_sha256':input_hash,
        'run_contract_sha256':sha(prepath),
        'prior_coordinates':{'v0':['3/100','3/50'],'xi':['1/10000000','1/1000000'],'rho':['-4/5','-3/10']},
        'nuisance_integration':'Whole xi/rho slab pointwise likelihood enclosure, integrated against the exact probability measure; target disintegration is retained.',
        'comparison_to_zero_xi_price_radii':{m:[rec(x) for x in radii] for m,radii in price_radius.items()},
        'comparison_to_zero_xi_target_radii':{m:rec(x) for m,x in target_radius.items()},
        'quotes_exact_dyadic':list(map(str,y)),
        'prior_left':str(left),'prior_right':str(right),'cells':cells,'cell_width':str(width),
        'arb_precision_bits':192,'weight_integer_scale':str(scale),
        'Gaussian_inverse':'Q_d=(64/27)(I-11^T/(d+3)); d1 uses quote index7',
        'whole_cell_weights_integer_bounds':weights,
        'increment_records':increment,'Asian_P_parameter_Lipschitz_bound':rec(L),
        'Asian_reference_zero_xi_same_parameter_PQ_bound':rec(eps),
        'Asian_positive_xi_same_parameter_PQ_bound':rec(eps+target_radius['P']+target_radius['Q']),
        'transports':transports,
        'all_four_tail_difference_bounds_pass':all(x['p025_and_p975_each_pass_0.10'] for x in transports.values()),
        'computations':{'Black_point_prices':2*(cells+1)*9,'Gaussian_weight_cell_boxes':4*cells,
            'parameter_transport_cell_scans':2*cells,'Asian_absolute_price_queries':0},
        'elapsed_seconds':time.perf_counter()-start,'memory_limit_MiB':256,
        'status':'PASS_CONDITIONAL_ON_ARB_INCLUSIONS'}
    assert sha(__file__)==source_hash and sha(SOURCE)==input_hash
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'result':str(out),'pass':result['all_four_tail_difference_bounds_pass'],
        'L':rec(L)['outward18'],'eps':rec(eps)['outward18'],
        'transports':{k:{q:v for q,v in x.items() if q!='parameter_quantile_brackets'} for k,x in transports.items()},
        'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
