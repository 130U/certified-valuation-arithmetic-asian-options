"""Independent full-node 384-bit certification of the weighted Asian remainder.
P uses a hyperbolic 2x2 Riccati flow, not the author's root/cross-ratio flow.
Q uses a separately indexed reverse grid. No author numerical functions imported.
"""
from pathlib import Path
from fractions import Fraction as F
import ctypes, hashlib, importlib.util, json, subprocess, sys, time
HERE=Path(__file__).resolve().parent
HELPER=HERE/'resource_limits.py'
sp=importlib.util.spec_from_file_location('independent_limits',HELPER)
resource=importlib.util.module_from_spec(sp);sp.loader.exec_module(resource)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OUT=HERE/'check-asian-remainder-result.json'
PRE=HERE/'check-asian-remainder-contract.json'
CONTROL=HERE/'check-asian-remainder-controller.json'
LOG=HERE/'check-asian-remainder-console.txt'

def worker():
    assert not OUT.exists();resource.hard_job();start=time.perf_counter()
    pre=json.loads(PRE.read_text(encoding='utf-8'));assert pre['source_sha256']==sha(__file__)
    oldpath=HERE/'asian-remainder-result.json'
    assert pre['author_result_sha256']==sha(oldpath)
    author=json.loads(oldpath.read_text(encoding='utf-8'))
    assert author['source_sha256']==sha(HERE/'asian-remainder-certificate.py')
    from flint import arb,fmpq,ctx
    ctx.prec=384;ctx.threads=1
    def ar(x):
        x=F(x);return arb(fmpq(x.numerator,x.denominator))
    def low(x):return F(str(x.lower().fmpq()))
    def high(x):return F(str(x.upper().fmpq()))
    def rec(x):return bounds(low(x),high(x))
    def bounds(a,b):return {'exact_interval':[str(a),str(b)],'outward24':resource.decimal_enclosure(a,b)}
    k=ar(3);h=ar(F(1,768));d=ar(F(27,200));v=ar(F(9,200));r=ar(F(1,100))
    aa=ar(F(529,20000));rx=ar(F(-253,2000));dt=ar(F(1,12));cex=F(1254433,1250000);c=ar(cex)
    # Build the A^2 part from ordered pairs, then combine duplicate profiles.
    catalog={}
    for i in range(12):
        for j in range(12):
            x=[F(0)]*12;x[i]+=1;x[j]+=1;t=tuple(x)
            catalog[t]=catalog.get(t,F(0))+F(10000,144)
    for i in range(12):
        x=[F(1,12)]*12;x[i]+=1;t=tuple(x);catalog[t]=-F(20000,12)*cex
    catalog[tuple([F(1,6)]*12)]=10000*cex*cex
    assert len(catalog)==91 and sum(abs(w) for w in catalog.values())==10000*(1+cex)**2
    profiles=sorted(catalog.items());counts={'P_blocks':0,'Q_steps':0};bmin=F(0);bmax=F(0)
    def qguard(B):
        nonlocal bmin,bmax
        l,u=low(B),high(B);assert l>-512 and u<=1
        bmin=min(bmin,l);bmax=max(bmax,u)
    def pflow(A,B,p,kill):
        b=rx*p-k;q=(p*p-p)/2-kill;D=(b*b-4*aa*q).sqrt()
        cc=(D*dt/2).cosh();ss=(D*dt/2).sinh()
        den=cc-(b+2*aa*B)*ss/D;assert den>0
        BB=(B*cc+(b*B+2*q)*ss/D)/den
        integ=-(den.log()+b*dt/2)/aa
        assert BB<=1
        counts['P_blocks']+=1
        return A+d*integ+r*p*dt,BB
    future=[]
    for alpha,wgt in profiles:
        A=B=arb(0);p=F(0)
        for month in range(11,0,-1):
            p+=alpha[month];A,B=pflow(A,B,ar(p),arb(0))
        AP,BP=A,B
        A=B=arb(0);p=F(0)
        for n in range(767,63,-1):
            if (n+1)%64==0:p+=alpha[(n+1)//64-1]
            pa=ar(p)
            A,B=A+h*(r*pa+d*B),(1+h*(rx*pa-k))*B+h*(aa*B*B+(pa*pa-pa)/2)
            qguard(B);counts['Q_steps']+=1
        assert p+alpha[0]==2
        future.append((ar(wgt),AP,BP,A,B))
    # Projection ledger: prefix product rather than exponentiating a prefix sum.
    eta=1-ar(F(3253,1000))*h;s0=ar(12);s1=s0+512*h
    beta=min(low(s0*eta-aa*s0*s0-h*h),low(s1*eta-aa*s1*s1-h*h));assert beta>8
    u=ar(8);prod=arb(1);total=arb(0)
    for n in range(768):
        total+=prod*(-v*u/h).exp();prod*=(-d*u).exp()
        u=eta*u-aa*u*u-h*h;assert u>0
    delta=ar(F(128,3))*h*(4*r+d-12*d-1).exp()*total
    ferr=10000*(1+c)*(1+c)*delta;err=high(ferr)
    # Uniform-integrability conditions at exponent 5/4, checked exactly.
    pmax=F(5,2);gamma_max=F(15,8);eta_ui=1-(F(3)-F(-253,2000)*pmax)*F(1,768)
    beta_ui=12*eta_ui-F(529,20000)*144-gamma_max*F(1,768)**2
    assert beta_ui>0
    coefficient_ui=16*F(529,20000)-12+gamma_max
    assert coefficient_ui<0
    growth_ui=4*d+ar(F(1,40))+ar(F(1,3))*(-12*d-1).exp()
    assert growth_ui<ar(F(3,5))
    pv=[];qv=[];P_overlap=Q_containment=0
    for node in range(257):
        kill=ar(F(node*node,4));PS=arb(0);QS=arb(0)
        for weight,AP,BP,AQ,BQ in future:
            AP2,BP2=pflow(AP,BP,ar(2),kill)
            PS+=weight*(AP2+BP2*v).exp()
            if node<=128:
                A,B=AQ,BQ
                for n in range(63,-1,-1):
                    A,B=A+h*(2*r+d*B),(1+h*(2*rx-k))*B+h*(aa*B*B+1-kill)
                    qguard(B);counts['Q_steps']+=1
                QS+=weight*(A+B*v).exp()
        pl,pu=low(PS),high(PS);oldl,oldu=map(F,author['all_points_P'][node]['exact_interval'])
        assert max(pl,oldl)<=min(pu,oldu)
        P_overlap+=1;pv.append((pl,pu))
        if node<=128:
            ql,qu=low(QS)-err,high(QS)+err
            oldl,oldu=map(F,author['all_points_Q'][node]['exact_interval'])
            assert oldl<=ql<=qu<=oldu
            Q_containment+=1;qv.append((ql,qu))
        assert time.perf_counter()-start<55
    # Independent Darboux sums use exact fractions before applying 2/sqrt(pi).
    PL=sum(max(F(0),x[0]) for x in pv[1:])/2;PU=sum(max(F(0),x[1]) for x in pv[:-1])/2
    QL=sum(max(F(0),x[0]) for x in qv[1:])/2;QU=sum(max(F(0),x[1]) for x in qv[:-1])/2
    X=ar(128);kp=ar(F(3253,1000));DD=(kp*kp+4*aa*(X*X-1)).sqrt()
    assert DD*dt>1 and kp/aa>2
    root2=(kp+DD)/(2*aa);assert root2>1
    c0=kp/(2*aa)+1/(X*aa.sqrt());c1=c0+DD*(-DD*dt).exp()/aa
    rate=(d*dt+v)/aa.sqrt()
    tailP=20000*(1+c*c)*(2*r+d+2*r*dt+d*(dt*c0+ar(2).log()/aa)+v*c1-rate*X).exp()/rate
    tailQ=ar(max(F(0),qv[-1][1]))/(128*h*v)
    factor=2/arb.pi().sqrt();WPU=factor*(ar(PU)+tailP);WQU=factor*(ar(QU)+tailQ)
    WPL=factor*ar(PL);WQL=factor*ar(QL)
    kap=(-r).exp()/(2*(2*arb.pi()*(1-ar(F(121,400)))).sqrt())
    Rlo=-kap*(WQU/110+WPU/95);Rhi=kap*(WQU/95+WPU/110)
    radius=(Rhi-Rlo)/2;center=(Rhi+Rlo)/2
    exact_checks=0
    for key,value in [('Q_per_profile_projection_bound',delta),('Q_square_expansion_point_error',ferr),('P_integral_tail_upper',tailP)]:
        l,u2=map(F,author[key]['exact_interval']);assert max(l,low(value))<=min(u2,high(value));exact_checks+=1
    for key,value in [('WP_upper_bound',WPU),('WQ_upper_bound',WQU),('discounted_bias_remainder_radius',radius)]:
        assert high(value)<=F(author[key]['exact_interval'][1])+F(1,10**60)
    assert radius<ar(F(11,1000))
    result={'status':'NONAUTHOR_FULL_WEIGHTED_REMAINDER_RECOMPUTATION_PASS','precision_bits':384,
        'method':'P hyperbolic matrix flow; ordered-pair catalog; Q separate reverse-step indexing; exact rational Darboux and tighter Q error endpoints',
        'source_sha256':sha(__file__),'author_result_sha256':sha(oldpath),'author_source_sha256':sha(HERE/'asian-remainder-certificate.py'),
        'scope_sha256':sha(HERE.parent/'SCOPE.md'),'run_contract_sha256':sha(PRE),
        'counts':counts,'P_all_node_interval_overlap_checks':P_overlap,'Q_all_node_independent_interval_containment_checks':Q_containment,
        'exact_scalar_overlap_checks':exact_checks,'beta_ui_exact':str(beta_ui),'ui_variance_generator_upper_exact':str(coefficient_ui),
        'ui_growth_upper':rec(growth_ui),'projection_beta':str(beta),'projection_u768':rec(u),
        'Q_coefficient_min':str(bmin),'Q_coefficient_max':str(bmax),'projection_bound':rec(delta),'point_projection_fee':rec(ferr),
        'P_tail':rec(tailP),'Q_tail':rec(tailQ),'WP_lower_bound':rec(WPL),'WP_upper_bound':rec(WPU),
        'WQ_lower_bound':rec(WQL),'WQ_upper_bound':rec(WQU),'remainder_lower_bound':rec(Rlo),'remainder_upper_bound':rec(Rhi),
        'remainder_center':rec(center),'remainder_radius':rec(radius),
        'all_points_P':[bounds(l,u2) for l,u2 in pv],'all_points_Q':[bounds(l,u2) for l,u2 in qv],
        'unpaid':['linearized thirteen-profile price difference and all its fees'],
        'worker_seconds':time.perf_counter()-start,'memory_limit_MiB':256,'threads':1}
    assert pre['source_sha256']==sha(__file__) and pre['author_result_sha256']==sha(oldpath)
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['status','counts','P_all_node_interval_overlap_checks','Q_all_node_independent_interval_containment_checks','WP_upper_bound','WQ_upper_bound','remainder_radius','ui_growth_upper','worker_seconds']},ensure_ascii=False))

def controller():
    assert all(not p.exists() for p in (OUT,PRE,CONTROL,LOG))
    mem=resource.MEMORY();mem.length=ctypes.sizeof(mem);assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    pre={'source_sha256':sha(__file__),'author_result_sha256':sha(HERE/'asian-remainder-result.json'),
         'scope_before_execution_sha256':sha(HERE.parent/'SCOPE.md'),'precision_bits':384,'P_nodes':257,'Q_nodes':129,
         'profiles':91,'hard_wall_seconds':60,'memory_limit_MiB':256,'threads':1,'available_commit':mem.available_commit,
         'available_physical':mem.available_physical,'required_available_bytes':512<<20}
    PRE.write_text(json.dumps(pre,indent=2)+'\n',encoding='utf-8')
    if min(mem.available_commit,mem.available_physical)<512<<20:
        control={'status':'NOT_RUN_MEMORY_PREFLIGHT'}
    else:
        start=time.perf_counter()
        with LOG.open('x',encoding='utf-8') as stream:
            child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'--worker'],stdout=stream,stderr=subprocess.STDOUT,creationflags=0x08000000)
            try:child.wait(timeout=60);control={'status':'FINISHED','returncode':child.returncode}
            except subprocess.TimeoutExpired:child.kill();child.wait();control={'status':'HARD_WALL_STOPPED','returncode':child.returncode}
        control['outer_seconds']=time.perf_counter()-start
    CONTROL.write_text(json.dumps(control,indent=2)+'\n',encoding='utf-8');print(json.dumps(control))

if __name__=='__main__':worker() if '--worker' in sys.argv else controller()
