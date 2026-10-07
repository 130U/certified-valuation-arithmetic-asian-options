"""Finite-grid weighted-moment diagnostics; retain every original analytical fee.

The independent mode uses a hyperbolic Riccati matrix flow and a separate reverse
Q grid. Formula derivations and scope are in revision/README.md. No claim of a
complete price-bias certificate is made by this weighted-remainder calculation.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse, hashlib, importlib.util, json, sys, time

CODE=Path(__file__).resolve().parents[1]
HELPER=CODE/'core'/'resource_limits.py'
spec=importlib.util.spec_from_file_location('limits',HELPER)
lim=importlib.util.module_from_spec(spec);spec.loader.exec_module(lim)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def compute(denominator, independent, output, candidates):
    assert denominator in (192,384,768,1536) and denominator%12==0
    assert not output.exists(), 'Preserve completed execution outputs.'
    assert not sys.flags.optimize
    lim.hard_job();start=time.perf_counter();source_at_start=sha(__file__)
    wall_guard=(110 if independent else 80)*max(1,(denominator+767)//768)
    from flint import arb,fmpq,ctx
    ctx.prec=384 if independent else 256;ctx.threads=1
    def ar(x):
        x=F(x);return arb(fmpq(x.numerator,x.denominator))
    def low(x):return F(str(x.lower().fmpq()))
    def high(x):return F(str(x.upper().fmpq()))
    def span(l,u):return {'exact_interval':[str(l),str(u)],'outward24':lim.decimal_enclosure(l,u)}
    def rec(x):return span(low(x),high(x))
    h=ar(F(1,denominator));nm=denominator//12
    k=ar(3);d=ar(F(27,200));v0=ar(F(9,200));rho=ar(F(-11,20));r=ar(F(1,100))
    a=ar(F(529,20000));rx=ar(F(-253,2000));dt=ar(F(1,12))
    counts={'P_blocks':0,'Q_steps':0};bmin=F(0);bmax=F(0)
    def guard(b):
        nonlocal bmin,bmax
        assert low(b)>-512 and high(b)<=1
        bmin=min(bmin,low(b));bmax=max(bmax,high(b))
    def pflow(A,B,p,kill=0):
        bb=rx*p-k;cc=(p*p-p)/2-ar(kill);D=(bb*bb-4*a*cc).sqrt()
        if independent:
            ch=(D*dt/2).cosh();ss=(D*dt/2).sinh()
            den=ch-(bb+2*a*B)*ss/D;assert den>0
            B2=(B*ch+(bb*B+2*cc)*ss/D)/den
            integ=-(den.log()+bb*dt/2)/a
        else:
            lo=(-bb-D)/(2*a);hi=(-bb+D)/(2*a);g=(B-lo)/(B-hi);u=(-D*dt).exp()
            den=1-g*u;assert den>0 and 1-g>0
            integ=lo*dt-(den/(1-g)).log()/a;B2=(lo-g*u*hi)/den
        assert high(B2)<=1;counts['P_blocks']+=1
        return A+d*integ+r*p*dt,B2
    # Positive A^2, AG and G^2 groups. The e=AG-G^2 function is nonnegative
    # pathwise by AM-GM, and hence also nonincreasing in its Laplace variable.
    catalog={}
    for i in range(12):
        for j in range(12):
            v=[F(0)]*12;v[i]+=1;v[j]+=1;t=tuple(v)
            old=catalog.get(t,(F(0),F(0),F(0)))
            catalog[t]=(old[0]+F(10000,144),old[1],old[2])
    for i in range(12):
        v=[F(1,12)]*12;v[i]+=1;catalog[tuple(v)]=(F(0),F(10000,12),F(0))
    catalog[tuple([F(1,6)]*12)]=(F(0),F(0),F(10000))
    assert len(catalog)==91 and all(sum(w[z] for w in catalog.values())==10000 for z in range(3))
    items=sorted(catalog.items()) if independent else list(catalog.items())
    future=[]
    for profile,weights in items:
        AP=BP=AQ=BQ=arb(0);p=F(0)
        for month in range(11,0,-1):
            p+=profile[month];AP,BP=pflow(AP,BP,ar(p))
        if independent:
            p=F(0)
            for step in range(denominator-1,nm-1,-1):
                if (step+1)%nm==0:p+=profile[(step+1)//nm-1]
                pa=ar(p);AQ,BQ=AQ+h*(r*pa+d*BQ),(1+h*(rx*pa-k))*BQ+h*(a*BQ*BQ+(pa*pa-pa)/2)
                guard(BQ);counts['Q_steps']+=1
        else:
            p=F(0)
            for month in range(11,0,-1):
                p+=profile[month];pa=ar(p)
                for unused in range(nm):
                    AQ=AQ+h*(r*pa+d*BQ);BQ=BQ+h*(a*BQ*BQ+(rx*pa-k)*BQ+(pa*pa-pa)/2)
                    guard(BQ);counts['Q_steps']+=1
        assert p+profile[0]==2;future.append((list(map(ar,weights)),AP,BP,AQ,BQ))
    eta=1-ar(F(3253,1000))*h;lam=ar(12);smax=lam+512*h
    beta=min(low(lam*eta-a*lam*lam-h*h),low(smax*eta-a*smax*smax-h*h));assert beta>8
    u=ar(8);su=arb(0);total=arb(0)
    for unused in range(denominator):
        total+=(-d*su-v0*u/h).exp();su+=u;u=eta*u-a*u*u-h*h;assert u>0
    delta=ar(F(128,3))*(4*r+d-12*d-1).exp()*h*total
    ui_eta=1-(F(3)-F(-253,2000)*F(5,2))*F(1,denominator)
    ui_beta=12*ui_eta-F(529,20000)*144-F(15,8)*F(1,denominator)**2
    ui_generator=16*F(529,20000)-12+F(15,8)
    ui_growth=4*d+ar(F(1,40))+ar(F(1,3))*(-12*d-1).exp()
    assert ui_beta>0 and ui_generator<0 and ui_growth<ar(F(3,5))
    raw={'P':[],'Q':[]}
    for node in range(257):
        kill=F(node*node,4);pp=[arb(0) for z in range(3)];qq=[arb(0) for z in range(3)]
        for weights,AP,BP,AQ,BQ in future:
            A,B=pflow(AP,BP,ar(2),kill);fp=(A+B*v0).exp()
            for z in range(3):pp[z]+=weights[z]*fp
            if node<=128:
                A,B=AQ,BQ
                for unused in range(nm):
                    if independent:A,B=A+h*(2*r+d*B),(1+h*(2*rx-k))*B+h*(a*B*B+1-ar(kill))
                    else:A=A+h*(2*r+d*B);B=B+h*(a*B*B+(2*rx-k)*B+1-ar(kill))
                    guard(B);counts['Q_steps']+=1
                fq=(A+B*v0).exp()
                for z in range(3):qq[z]+=weights[z]*fq
        raw['P'].append(pp)
        if node<=128:raw['Q'].append(qq)
        assert time.perf_counter()-start<wall_guard, 'Finite workload time guard.'
    X=ar(128);kp=ar(F(3253,1000));DD=(kp*kp+4*a*(X*X-1)).sqrt();assert DD*dt>1
    C0=kp/(2*a)+1/(X*a.sqrt());C1=C0+DD*(-DD*dt).exp()/a
    C=(2*r+d+2*r*dt+d*(dt*C0+ar(2).log()/a)+v0*C1).exp();rate=(d*dt+v0)/a.sqrt()
    unit_P_tail=10000*C*(-rate*X).exp()/rate;factor=2/arb.pi().sqrt()
    def integrate(vals,tail):
        lower=factor*ar(sum(max(F(0),low(x)) for x in vals[1:])/2)
        upper=factor*(ar(sum(max(F(0),high(x)) for x in vals[:-1])/2)+tail)
        return span(low(lower),high(upper))
    moments={};nodes={}
    for model in ('P','Q'):
        err=arb(0,ar(high(10000*delta))) if model=='Q' else arb(0)
        dvals=[v[2]+err for v in raw[model]]
        evals=[v[1]-v[2]+(2*err if model=='Q' else arb(0)) for v in raw[model]]
        atail=unit_P_tail if model=='P' else ar(max(F(0),high(dvals[-1])))/(128*h*v0)
        etail=unit_P_tail if model=='P' else ar(max(F(0),high(evals[-1])))/(128*h*v0)
        moments[model]={'G2_over_sqrtI':integrate(dvals,atail),'AGminusG2_over_sqrtI':integrate(evals,etail)}
        nodes[model]={'G2':[rec(x) for x in dvals],'AGminusG2':[rec(x) for x in evals]}
    dl=sum(F(moments[m]['G2_over_sqrtI']['exact_interval'][0]) for m in ('P','Q'))
    du=sum(F(moments[m]['G2_over_sqrtI']['exact_interval'][1]) for m in ('P','Q'))
    el=sum(F(moments[m]['AGminusG2_over_sqrtI']['exact_interval'][0]) for m in ('P','Q'))
    eu=sum(F(moments[m]['AGminusG2_over_sqrtI']['exact_interval'][1]) for m in ('P','Q'))
    assert dl>0 and el>=0
    cstar=span(1+el/du,1+eu/dl)
    midpoint=(F(cstar['exact_interval'][0])+F(cstar['exact_interval'][1]))/2
    selected=F(round(midpoint*10**7),10**7)
    cs=list(dict.fromkeys([F(1),F(1254433,1250000),selected]+list(map(F,candidates))))
    rows=[];kap=(-r).exp()/(2*(2*arb.pi()*(1-rho*rho)).sqrt())
    for ce in cs:
        c=ar(ce);ww={};details={}
        for model in ('P','Q'):
            pointfee=10000*(1+c)*(1+c)*delta if model=='Q' else arb(0)
            vals=[v[0]-2*c*v[1]+c*c*v[2]+(arb(0,ar(high(pointfee))) if model=='Q' else arb(0)) for v in raw[model]]
            tail=2*(1+c*c)*unit_P_tail if model=='P' else ar(max(F(0),high(vals[-1])))/(128*h*v0)
            ww[model]=integrate(vals,tail);details[model]={'tail':rec(tail),'point_projection_fee':rec(pointfee),'F0':rec(vals[0]),'FX':rec(vals[-1])}
        wp=ar(F(ww['P']['exact_interval'][1]));wq=ar(F(ww['Q']['exact_interval'][1]))
        rlo=-kap*(wq/110+wp/95);rhi=kap*(wq/95+wp/110)
        rows.append({'c':str(ce),'W_P':ww['P'],'W_Q':ww['Q'],'bias_remainder':span(low(rlo),high(rhi)),
                     'nonlinear_width':rec(rhi-rlo),'details':details})
    result={'status':'OUTWARD_WEIGHTED_MOMENT_AND_REMAINDER_CALCULATION_COMPLETE','scope':'Original theta=(3,.045,.23,-.55,.045); 12-fixing Asian call spread 95/110; weighted remainder only, not full price bias.',
       'h':str(F(1,denominator)),'steps_per_month':nm,'precision_bits':ctx.prec,'independent_construction':independent,
       'source_sha256':source_at_start,'resource_helper_sha256':sha(HELPER),'base_scope_sha256':sha(CODE/'SCOPE.md'),
       'P_method':'hyperbolic matrix' if independent else 'root cross-ratio','Q_method':'separate reverse grid' if independent else 'month block grid',
       'moments':moments,'c_star_enclosure':cstar,'selected_rational_c':str(selected),'rows':rows,'nodes':nodes,
       'projection_per_profile_fee':rec(delta),'projection_beta_min':str(beta),'UI_beta_exact':str(ui_beta),
       'UI_variance_generator_exact':str(ui_generator),'UI_growth_upper':rec(ui_growth),'counts':counts,
       'Q_coefficient_min':str(bmin),'Q_coefficient_max':str(bmax),'elapsed_seconds':time.perf_counter()-start,'memory_limit_MiB':256,'wall_guard_seconds':wall_guard,
       'no_claim':['These c values optimize or diagnose the nonlinear part only.','No signed Asian leading coefficient is evaluated.','No full Heston parameter-domain certificate.']}
    assert sha(__file__)==source_at_start, 'Executed source changed during the calculation.'
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:result[k] for k in ('status','h','precision_bits','c_star_enclosure','selected_rational_c','elapsed_seconds')}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--steps',type=int,required=True);p.add_argument('--independent',action='store_true');p.add_argument('--output',type=Path,required=True);p.add_argument('--c',action='append',default=[])
    args=p.parse_args();compute(args.steps,args.independent,args.output,args.c)
