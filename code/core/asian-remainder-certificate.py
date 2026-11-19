"""Outward certification of the SAME original Asian weighted quadratic remainders.
No linearized price, no absolute Asian price, no price bias certificate is claimed.
"""
from pathlib import Path
from fractions import Fraction as F
import sys,json,time,hashlib,importlib.util,ctypes,subprocess,os
HERE=Path(__file__).resolve().parent
HELPER=HERE/'resource_limits.py'
spec=importlib.util.spec_from_file_location('lim',HELPER);lim=importlib.util.module_from_spec(spec);spec.loader.exec_module(lim)
OUT=HERE/'asian-remainder-result.json';CONTROL=HERE/'asian-remainder-controller.json'
CONSOLE=HERE/'asian-remainder-console.txt'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def worker():
    assert not OUT.exists();lim.hard_job();start=time.perf_counter()
    from flint import arb,fmpq,ctx
    ctx.prec=256;ctx.threads=1
    def ar(x):
        x=F(x);return arb(fmpq(x.numerator,x.denominator))
    def low(x):return F(str(x.lower().fmpq()))
    def high(x):return F(str(x.upper().fmpq()))
    def rec(x):
        l,u=low(x),high(x);return {'exact_interval':[str(l),str(u)],'outward24':lim.decimal_enclosure(l,u)}
    h=ar(F(1,768));k=ar(3);d=ar(F(27,200));v0=ar(F(9,200));rho=ar(F(-11,20));r=ar(F(1,100));a=ar(F(529,20000));rxi=ar(F(-253,2000));c=ar(F(1254433,1250000));dt=ar(F(1,12))
    c_exact=F(1254433,1250000);profiles=[];weights=[]
    for i in range(12):
        for j in range(i,12):
            v=[F(0)]*12;v[i]+=1;v[j]+=1
            profiles.append(v);weights.append(F(10000*(1 if i==j else 2),144))
    for i in range(12):
        v=[F(1,12)]*12;v[i]+=1;profiles.append(v);weights.append(-F(20000,12)*c_exact)
    profiles.append([F(1,6)]*12);weights.append(10000*c_exact*c_exact)
    ww=list(map(ar,weights));assert sum(abs(w) for w in weights)==10000*(1+c_exact)**2
    counts={'Q_steps':0,'P_month_blocks':0};bmin=F(0);bmax=F(0)
    def check(b):
        nonlocal bmin,bmax
        assert b<=1 and abs(b)<512
        bmin=min(bmin,low(b));bmax=max(bmax,high(b))
    def pflow(A,B,p,kill=0):
        bb=rxi*p-k;cc=(p*p-p)/2-ar(kill);D=(bb*bb-4*a*cc).sqrt()
        lo=(-bb-D)/(2*a);hi=(-bb+D)/(2*a);g=(B-lo)/(B-hi);u=(-D*dt).exp()
        den=1-g*u;assert den>0 and 1-g>0
        integral=lo*dt-(den/(1-g)).log()/a
        result=(A+d*integral+r*p*dt,(lo-g*u*hi)/den)
        assert result[1]<=1
        counts['P_month_blocks']+=1
        return result
    # Future eleven months shared by every Laplace node.
    pcache=[];qcache=[]
    for v in profiles:
        Ap=Bp=Aq=Bq=arb(0);p=F(0)
        for j in range(11,0,-1):
            p+=v[j];pa=ar(p);Ap,Bp=pflow(Ap,Bp,pa)
            for unused in range(64):
                Aq=Aq+h*(r*pa+d*Bq)
                Bq=Bq+h*(a*Bq*Bq+(rxi*pa-k)*Bq+(pa*pa-pa)/2)
                check(Bq);counts['Q_steps']+=1
        assert p+v[0]==2
        pcache.append((Ap,Bp));qcache.append((Aq,Bq))
    # Positive stock loading version of the direct weighted Laplace projection bound.
    eta=1-ar(F(3253,1000))*h;lam=ar(12);smax=lam+512*h
    beta=min(low(lam*eta-a*lam*lam-h*h),low(smax*eta-a*smax*smax-h*h));assert beta>8
    u=ar(8);su=arb(0);SL=arb(0)
    for n in range(768):
        SL+=(-d*su-v0*u/h).exp();su+=u;u=eta*u-a*u*u-h*h;assert u>0
    delta=ar(F(512,12))*(2*r+d+2*r-12*d-1).exp()*h*SL
    ferr=ar(10000*(1+c_exact)**2)*delta
    # Real-prefix exp(4V) barrier constants, checked with exact rational inequalities.
    barrier_extra=ar(F(1,3))*(-12*d-1).exp()
    assert 4*d+2*r+barrier_extra<ar(F(3,5))
    assert F(16)*F(529,20000)-12+1<0
    Pvals=[];Qvals=[]
    for j in range(257):
        x=F(j,2);sp=arb(0)
        for weight,(A,B) in zip(ww,pcache):
            A2,B2=pflow(A,B,ar(2),x*x);sp+=weight*(A2+B2*v0).exp()
        Pvals.append(sp)
        if j<=128:
            sq=arb(0);kill=ar(x*x);qcoef=rxi*2-k
            for weight,(A,B) in zip(ww,qcache):
                for unused in range(64):
                    A=A+h*(2*r+d*B);B=B+h*(a*B*B+qcoef*B+1-kill)
                    check(B);counts['Q_steps']+=1
                sq+=weight*(A+B*v0).exp()
            Qvals.append(sq+arb(0,ar(high(ferr))))
        assert time.perf_counter()-start<55
    def darboux(vals):
        return (ar(sum(max(F(0),low(v)) for v in vals[1:])/2),
                ar(sum(max(F(0),high(v)) for v in vals[:-1])/2))
    pl,pu=darboux(Pvals);ql,qu=darboux(Qvals)
    X=ar(128);kp=ar(F(3253,1000));DX=(kp*kp+4*a*(X*X-1)).sqrt();assert DX*dt>1
    C0=kp/(2*a)+1/(X*a.sqrt());C1=C0+DX*(-DX*dt).exp()/a
    C=(2*r+d+2*r*dt+d*(dt*C0+ar(2).log()/a)+v0*C1).exp()
    zeta=(d*dt+v0)/a.sqrt()
    ptail=20000*(1+c*c)*C*(-zeta*X).exp()/zeta
    qtail=ar(max(F(0),high(Qvals[-1])))/(128*h*v0)
    factor=2/arb.pi().sqrt();WPupper=factor*(pu+ptail);WQupper=factor*(qu+qtail)
    WPlo=factor*pl;WQlo=factor*ql
    kap=(-r).exp()/(2*(2*arb.pi()*(1-rho*rho)).sqrt())
    remlo=-kap*(WQupper/110+WPupper/95);remhi=kap*(WQupper/95+WPupper/110)
    radius=(remhi-remlo)/2;center=(remhi+remlo)/2
    result={'status':'CERTIFIED_ORIGINAL_ASIAN_WEIGHTED_REMAINDER_ONLY','theta':['3','9/200','23/100','-11/20','9/200'],
      'c':str(c_exact),'h':'1/768','P_nodes':257,'Q_nodes':129,'node_step':'1/2','catalog_profiles':91,'counts':counts,
      'Q_coefficient_min':str(bmin),'Q_coefficient_max':str(bmax),'projection_beta_min':str(beta),'projection_u768':rec(u),
      'Q_per_profile_projection_bound':rec(delta),'Q_square_expansion_point_error':rec(ferr),
      'P_integral_tail_upper':rec(ptail),'Q_integral_tail_upper':rec(qtail),
      'WP_lower_bound':rec(WPlo),'WP_upper_bound':rec(WPupper),'WQ_lower_bound':rec(WQlo),'WQ_upper_bound':rec(WQupper),
      'discounted_bias_remainder_lower_bound':rec(remlo),'discounted_bias_remainder_upper_bound':rec(remhi),
      'discounted_bias_remainder_center':rec(center),'discounted_bias_remainder_radius':rec(radius),
      'P_F0':rec(Pvals[0]),'P_F128':rec(Pvals[-1]),'Q_F0':rec(Qvals[0]),'Q_F64':rec(Qvals[-1]),
      'all_points_P':[rec(v) for v in Pvals],'all_points_Q':[rec(v) for v in Qvals],
      'source_sha256':sha(__file__),'scope_sha256':sha(HERE.parent/'SCOPE.md'),'helper_sha256':sha(HELPER),
      'precision_bits':256,'threads':1,'memory_limit_MiB':256,'worker_seconds':time.perf_counter()-start,
      'unpaid':['Linearized 13-profile P/Q price difference','Linearized price finite-frequency and alias tails','Linearized price quadrature and projection fees'],
      'no_claim':['This remainder module alone does not give the complete Asian price bias certificate','No assertion about a separate 13-dimensional trial field','No original full-Theta uniform certificate']}
    assert high(radius)<F(11,1000)
    OUT.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('all_points_P','all_points_Q')},indent=2))

def controller():
    assert not OUT.exists() and not CONTROL.exists() and not CONSOLE.exists()
    mem=lim.MEMORY();mem.length=ctypes.sizeof(mem);assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    rr={'available_physical':mem.available_physical,'available_commit':mem.available_commit,'required':512<<20,'hard_wall_seconds':60,'memory_limit_MiB':256,'source_sha256':sha(__file__)}
    if min(mem.available_physical,mem.available_commit)<512<<20:rr['status']='NOT_RUN_MEMORY_PREFLIGHT'
    else:
        t=time.perf_counter()
        with CONSOLE.open('x') as f:
            p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'--worker'],stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000)
            try:p.wait(timeout=60);rr.update(status='FINISHED',returncode=p.returncode)
            except subprocess.TimeoutExpired:p.kill();p.wait();rr.update(status='HARD_WALL_STOPPED',returncode=p.returncode)
        rr['outer_seconds']=time.perf_counter()-t
    CONTROL.write_text(json.dumps(rr,indent=2)+'\n');print(json.dumps(rr,indent=2))
if __name__=='__main__':worker() if '--worker' in sys.argv else controller()
