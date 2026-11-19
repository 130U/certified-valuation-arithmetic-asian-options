"""Bounded 13-ray actual original Asian P/Q certificate. No Monte Carlo."""
from pathlib import Path
from fractions import Fraction as F
import ctypes,hashlib,importlib.util,json,subprocess,sys,time
HERE=Path(__file__).resolve().parent
HELP=HERE/'resource_limits.py'
sp=importlib.util.spec_from_file_location('limit',HELP);limit=importlib.util.module_from_spec(sp);sp.loader.exec_module(limit)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def worker(pilot):
    limit.hard_job();t0=time.perf_counter()
    from flint import arb,acb,fmpq,ctx
    ctx.prec=256;ctx.threads=1
    def ar(x):
        x=F(x);return arb(fmpq(x.numerator,x.denominator))
    def lo(x):return F(str(x.lower().fmpq()))
    def hi(x):return F(str(x.upper().fmpq()))
    def rec(x):return span(lo(x),hi(x))
    def span(l,u):return {'exact_interval':[str(l),str(u)],'outward24':limit.decimal_enclosure(l,u)}
    k=ar(3);a=ar(F(529,20000));d=ar(F(27,200));rx=ar(F(-253,2000));v0=ar(F(9,200));r=ar(F(1,100));h=ar(F(1,768));dt=ar(F(1,96));dw=ar(F(1,5));pi=arb.pi();rho=ar(F(-11,20));cscale=ar(F(1254433,1250000));delta=ar(F(1,2));disc=(-r).exp()
    y95=(95/(100*cscale)).log();y110=(110/(100*cscale)).log();N=8 if pilot else 641
    P=arb(0);Q=arb(0);csum=arb(0);counts={'Q_layers':0,'P_full_path_branch_guards':0,'profiles':0};rows=[]
    for n in range(N):
        z=acb(delta,ar(F(n,5)));coef0=disc*dw/pi*((z*y95).exp()*95-(z*y110).exp()*110)/z
        coefA=disc*dw/pi*((z*y110).exp()-(z*y95).exp())/z*ar(F(100,12))
        if n==0:coef0/=2;coefA/=2
        cache={}
        for block in range(1,13):
            for extra in (0,1):
                q=-z*ar(F(block,12))+extra;g=(q*q-q)/2;cm=k-rx*q;D=(cm*cm-4*a*g).sqrt()
                ch=(D*dt/2).cosh();sd=(D*dt/2).sinh()/D
                matrix=(ch-cm*sd,2*g*sd,-2*a*sd,ch+cm*sd)
                guard=(abs(D)*dt/2).cosh()
                cache[(block,extra)]=(q,g,cm,matrix,guard,(-cm).real,(-cm).imag,g.real,g.imag)
        pn=arb(0);qn=arb(0);sn=arb(0)
        for target in range(-1,12):
            bp=acb(0);ap=acb(0);x=y=ax=ay=arb(0)
            for block in range(1,13):
                fixing_index=12-block;extra=int(target>=fixing_index)
                q,g,cm,mm,guard,lr,li,gr,gi=cache[(block,extra)]
                m11,m12,m21,m22=mm
                for unused in range(8):
                    assert guard-1+abs(cm-2*a*bp)*dt*guard/2<1
                    den=m21*bp+m22
                    ap+=r*q*dt+d*(cm*dt/2-den.log())/a
                    bp=(m11*bp+m12)/den
                    counts['P_full_path_branch_guards']+=1
                pr=q.real;qi=q.imag
                for unused in range(64):
                    nx=ax+h*(r*pr+d*x);ny=ay+h*(r*qi+d*y)
                    xx=x+h*(a*(x*x-y*y)+lr*x-li*y+gr)
                    yy=y+h*(2*a*x*y+lr*y+li*x+gi)
                    x,y,ax,ay=xx,yy,nx,ny
                    assert x<1 and x*x+y*y<1024**2
                    counts['Q_layers']+=1
            phiP=(ap+bp*v0).exp();phiQ=acb(ax+v0*x,ay+v0*y).exp()
            coeff=coef0 if target==-1 else coefA
            pn+=(coeff*phiP).real;qn+=(coeff*phiQ).real;sn+=abs(coeff);counts['profiles']+=1
        P+=pn;Q+=qn;csum+=sn
        rows.append({'n':n,'P_term':rec(pn),'proxy_term':rec(qn),'coefficient_sum':rec(sn)})
        if n%16==0:assert time.perf_counter()-t0<170
    base={'source_sha256':sha(__file__),'scope_sha256':sha(HERE.parent/'SCOPE.md'),
          'weighted_square_source_sha256':sha(HERE/'asian-remainder-certificate.py'),'weighted_square_result_sha256':sha(HERE/'asian-remainder-result.json'),
          'precision_bits':256,'threads':1,'memory_MiB':256,'frequencies':N,'counts':counts,
          'P_linear_finite':rec(15*disc+P),'Q_proxy_linear_finite':rec(15*disc+Q),'linear_bias_finite':rec(Q-P),'coefficient_abs_sum':rec(csum),'frequency_rows':rows}
    if pilot:
        base.update(status='PILOT_ONLY_NO_PRICE_CLAIM',worker_seconds=time.perf_counter()-t0,full_linear_time_estimate=(time.perf_counter()-t0)*641/8)
        (HERE/'asian-linear-pilot-result.json').write_text(json.dumps(base,indent=2)+'\n')
        print(json.dumps({k:v for k,v in base.items() if k!='frequency_rows'},indent=2));return
    # Every fee below is an outward Arb upper bound under the stated inequalities.
    eta=1-ar(F(6253,2000))*h;gamma=ar(F(3,8));lam=ar(12)
    beta=min(lo(s*eta-a*s*s-gamma*h*h) for s in (lam,lam+1024*h));assert beta>8
    u=ar(8);sumu=arb(0);sumL=arb(0)
    for j in range(768):
        sumL+=(-d*sumu-v0*u/h).exp();sumu+=u;u=eta*u-a*u*u-gamma*h*h;assert u>0
    projection_delta=ar(F(256,3))*(2*r+d-12*d-1).exp()*h*sumL
    projection=csum*projection_delta
    M2=ar(F(39,50)).exp();U=ar(128);s=1-rho*rho;i0=h*v0
    Cprice=disc*(195*(delta*y95).exp()+210*(delta*y110).exp())
    lapA=lapB=arb(0)
    for unused in range(64):
        lapA+=d*h*lapB;lapB+=h*(a*lapB*lapB-k*lapB-s*U*U);assert lapB<0
    LQ=(lapA+lapB*v0).exp()
    tailQ=Cprice*(M2*LQ).sqrt()/(pi*s*i0*U*U)
    month=ar(F(1,12));D=(k*k+4*a*s*U*U).sqrt();assert D*month>1
    C0=k/(2*a);C1=C0+D*(-D*month).exp()/a
    CP=(d*(month*C0+ar(2).log()/a)+v0*C1).exp();gam=(s/a).sqrt()*(d*month+v0)/2
    tailP=Cprice*(M2*CP).sqrt()*(-gam*U).exp()/(pi*gam*U)
    alias=disc*(205+200*r.exp()+M2*(195*y95.exp()+210*y110.exp()))/((5*pi).exp()-1)
    linearfee=projection+tailP+tailQ+2*alias
    W=json.loads((HERE/'asian-remainder-result.json').read_text())
    assert W['source_sha256']==sha(HERE/'asian-remainder-certificate.py')
    rl=F(W['discounted_bias_remainder_lower_bound']['exact_interval'][0]);ru=F(W['discounted_bias_remainder_upper_bound']['exact_interval'][1])
    bl=lo(Q-P)-hi(linearfee)+rl;bu=hi(Q-P)+hi(linearfee)+ru
    wp=F(W['WP_upper_bound']['exact_interval'][1]);wq=F(W['WQ_upper_bound']['exact_interval'][1]);kap=disc/(2*(2*pi*s).sqrt())
    pp=15*disc+P;qq=15*disc+Q
    pleft=lo(pp)-hi(alias+tailP+kap*ar(wp)/110);pright=hi(pp)+hi(alias+tailP+kap*ar(wp)/95)
    qleft=lo(qq)-hi(alias+tailQ+projection+kap*ar(wq)/110);qright=hi(qq)+hi(alias+tailQ+projection+kap*ar(wq)/95)
    base.update(status='COMPLETE_ORIGINAL_ASIAN_PQ_CERTIFICATE',projection_beta_min=str(beta),projection_delta=rec(projection_delta),projection_price_fee=rec(projection),
       Q_firstmonth_Laplace_upper=rec(LQ),P_frequency_tail=rec(tailP),Q_frequency_tail=rec(tailQ),one_law_alias=rec(alias),
       total_linear_bias_fee=rec(linearfee),true_linear_bias=span(lo(Q-P)-hi(linearfee),hi(Q-P)+hi(linearfee)),
       true_original_Asian_bias=span(bl,bu),true_original_Asian_P=span(pleft,pright),true_original_Asian_Q=span(qleft,qright),
       bias_absolute_upper=str(max(abs(bl),abs(bu))),original_theta_star_Asian_pass_0025=max(abs(bl),abs(bu))<F(1,40),
       worker_seconds=time.perf_counter()-t0,paths=0)
    assert counts['Q_layers']==6399744 and counts['P_full_path_branch_guards']==799968
    (HERE/'asian-linear-result.json').write_text(json.dumps(base,indent=2)+'\n')
    print(json.dumps({k:v for k,v in base.items() if k!='frequency_rows'},indent=2))

def controller(pilot):
    prefix='asian-linear-pilot' if pilot else 'asian-linear';OUT=HERE/(prefix+'-result.json');CON=HERE/(prefix+'-controller.json');LOG=HERE/(prefix+'-console.txt')
    assert not OUT.exists() and not CON.exists() and not LOG.exists()
    if not pilot:
        prior=json.loads((HERE/'asian-linear-pilot-result.json').read_text());assert prior['source_sha256']==sha(__file__)
        assert prior['full_linear_time_estimate']<140
    m=limit.MEMORY();m.length=ctypes.sizeof(m);assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    rr={'source_sha256':sha(__file__),'scope_sha256':sha(HERE.parent/'SCOPE.md'),'required_memory_bytes':512<<20,
        'available_physical_bytes':m.available_physical,'available_commit_bytes':m.available_commit,'hard_wall_seconds':30 if pilot else 180,'job_MiB':256,'attempts':0}
    if min(m.available_physical,m.available_commit)<512<<20:rr['status']='MEMORY_PREFLIGHT_STOP'
    else:
        t=time.perf_counter();rr['attempts']=1
        with LOG.open('x') as f:
            args=[sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'--worker']+(['--pilot'] if pilot else [])
            p=subprocess.Popen(args,stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000)
            try:p.wait(timeout=rr['hard_wall_seconds']);rr.update(status='FINISHED',returncode=p.returncode)
            except subprocess.TimeoutExpired:p.kill();p.wait();rr.update(status='HARD_WALL_STOPPED',returncode=p.returncode)
        rr['outer_seconds']=time.perf_counter()-t
    CON.write_text(json.dumps(rr,indent=2)+'\n');print(json.dumps(rr,indent=2))
if __name__=='__main__':
    pilot='--pilot' in sys.argv
    worker(pilot) if '--worker' in sys.argv else controller(pilot)
