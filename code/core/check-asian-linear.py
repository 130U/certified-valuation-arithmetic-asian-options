"""Independent full 384-bit verification of the original-theta-star 13-ray Asian.

Complex Q recursion and exponential P blocks replace the author's real/imag Q
and hyperbolic matrix construction. Every frequency and every fee is checked.
"""
from pathlib import Path
from fractions import Fraction as F
import ctypes,hashlib,importlib.util,json,os,subprocess,sys,time
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'asian-linear-certificate.py'
AUTHOR=HERE/'asian-linear-result.json'
PROOF=HERE.parent/'SCOPE.md'
WRESULT=HERE/'asian-remainder-result.json'
HELP=HERE/'resource_limits.py'
spec=importlib.util.spec_from_file_location('independent_limits',HELP)
limits=importlib.util.module_from_spec(spec);spec.loader.exec_module(limits)
PREFIX='check-asian-linear'
OUT=HERE/(PREFIX+'-result.json');FREEZE=HERE/(PREFIX+'-contract.json')
CONTROL=HERE/(PREFIX+'-controller.json');CONSOLE=HERE/(PREFIX+'-console.txt')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def worker():
    assert not OUT.exists()
    start=time.perf_counter();limits.hard_job()
    for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
    from flint import arb,acb,fmpq,ctx
    ctx.prec=384;ctx.threads=1
    def ar(x):
        x=F(x);return arb(fmpq(x.numerator,x.denominator))
    def lo(x):return F(str(x.lower().fmpq()))
    def hi(x):return F(str(x.upper().fmpq()))
    def span(a,b):return {'exact_interval':[str(a),str(b)],'outward24':limits.decimal_enclosure(a,b)}
    def rec(x):return span(lo(x),hi(x))
    def overlap(x,old):
        l,u=map(F,old['exact_interval']);assert max(lo(x),l)<=min(hi(x),u)
    author=json.loads(AUTHOR.read_text());W=json.loads(WRESULT.read_text())
    assert author['source_sha256']==sha(SOURCE)=='dbe13d37a5ad6db8dcda674cc1bddae7b6049329de2cc23e8b115af10409c5a8'
    assert author['weighted_square_result_sha256']==sha(WRESULT)
    assert W['source_sha256']==sha(HERE/'asian-remainder-certificate.py')
    k=ar(3);a=ar(F(529,20000));d=ar(F(27,200));rx=ar(F(-253,2000))
    v0=ar(F(9,200));r=ar(F(1,100));h=ar(F(1,768));dt=ar(F(1,96))
    delta=ar(F(1,2));dw=ar(F(1,5));disc=(-r).exp();pi=arb.pi()
    scale=ar(F(1254433,1250000));ylo=(ar(95)/(100*scale)).log();yhi=(ar(110)/(100*scale)).log()
    totalsP=arb(0);totalsQ=arb(0);totalcoeff=arb(0);rows=[]
    counts={'Q_layers':0,'P_path_guards':0,'frequency_real_interval_overlaps':0}
    for n in range(641):
        z=acb(delta,ar(F(n,5)));w=ar(F(1,2)) if n==0 else ar(1)
        c0=disc*dw*w/pi/z*(95*(z*ylo).exp()-110*(z*yhi).exp())
        ca=disc*dw*w/pi/z*ar(F(100,12))*((z*yhi).exp()-(z*ylo).exp())
        cache={}
        for m in range(12):
            for extra in (0,1):
                q=extra-z*ar(F(12-m,12));g=(q*q-q)/2;cm=k-rx*q
                D=(cm*cm-4*a*g).sqrt();ep=(D*dt/2).exp();em=(-D*dt/2).exp()
                ch=(ep+em)/2;twosh_over_D=(ep-em)/D
                mag=abs(D)*dt/2;bound=(mag.exp()+(-mag).exp())/2
                cache[m,extra]=(q,g,cm,ch,twosh_over_D,bound)
        sumP=arb(0);sumQ=arb(0);sumC=arb(0)
        for stock in range(-1,12):
            bp=acb(0);ap=acb(0);bq=acb(0);aq=acb(0)
            for m in range(11,-1,-1):
                q,g,cm,ch,twosh,guard=cache[m,int(stock>=m)]
                for j in range(8):
                    assert guard-1+abs(cm-2*a*bp)*dt*guard/2<1
                    den=ch+(cm/2-a*bp)*twosh
                    ap+=r*q*dt+(d/a)*(cm*dt/2-den.log())
                    bp=(bp*(ch-cm*twosh/2)+g*twosh)/den
                    counts['P_path_guards']+=1
                for j in range(64):
                    aq+=h*(r*q+d*bq)
                    bq+=h*(a*bq*bq-cm*bq+g)
                    assert bq.real<1 and abs(bq)<1024
                    counts['Q_layers']+=1
            coeff=c0 if stock<0 else ca
            sumP+=(coeff*(ap+v0*bp).exp()).real
            sumQ+=(coeff*(aq+v0*bq).exp()).real
            sumC+=abs(coeff)
        old=author['frequency_rows'][n];assert old['n']==n
        for x,key in ((sumP,'P_term'),(sumQ,'proxy_term'),(sumC,'coefficient_sum')):
            overlap(x,old[key]);counts['frequency_real_interval_overlaps']+=1
        totalsP+=sumP;totalsQ+=sumQ;totalcoeff+=sumC
        rows.append({'n':n,'P_term':rec(sumP),'Q_proxy_term':rec(sumQ),'coefficient_sum':rec(sumC)})
        if n%16==0:assert time.perf_counter()-start<170
    # Exact real arithmetic proof constants: reuse no author fee function.
    eta=1-ar(F(6253,2000))*h;gamma=ar(F(3,8))
    beta=min(lo(s*eta-a*s*s-gamma*h*h) for s in (ar(12),ar(12)+1024*h));assert beta>8
    u=ar(8);Su=arb(0);occup=arb(0)
    for j in range(768):
        occup+=(-d*Su-v0*u/h).exp();Su+=u;u=eta*u-a*u*u-gamma*h*h;assert u>0
    deltaQ=(ar(1024)/12)*(2*r+d-12*d).exp()/ar(1).exp()*h*occup
    projection=deltaQ*totalcoeff
    s=ar(F(279,400));U=ar(128);i0=h*v0;M2=ar(F(39,50)).exp()
    Cprice=disc*(195*(delta*ylo).exp()+210*(delta*yhi).exp())
    lapA=arb(0);lapB=arb(0)
    for j in range(64):
        lapA+=d*h*lapB;lapB+=h*(a*lapB*lapB-k*lapB-s*U*U);assert lapB<0
    LQ=(lapA+v0*lapB).exp()
    feeQ=Cprice*(M2*LQ).sqrt()/(pi*s*i0*U*U)
    tau=ar(F(1,12));D=(k*k+4*a*s*U*U).sqrt();assert D*tau>1
    C0=k/(2*a);C1=C0+(D/a)*(-D*tau).exp()
    CP=(d*(tau*C0+ar(2).log()/a)+v0*C1).exp()
    gam=(s/a).sqrt()*(d*tau+v0)/2
    feeP=Cprice*(M2*CP).sqrt()*(-gam*U).exp()/(pi*gam*U)
    feeAlias=disc*(205+200*r.exp()+M2*(195*ylo.exp()+210*yhi.exp()))/((5*pi).exp()-1)
    fee=projection+feeQ+feeP+2*feeAlias
    center=totalsQ-totalsP
    fees={'projection_delta':deltaQ,'projection_price_fee':projection,'Q_firstmonth_Laplace_upper':LQ,
          'P_frequency_tail':feeP,'Q_frequency_tail':feeQ,'one_law_alias':feeAlias,'total_linear_bias_fee':fee}
    for key,x in fees.items():overlap(x,author[key])
    overlap(center,author['linear_bias_finite']);overlap(totalcoeff,author['coefficient_abs_sum'])
    rl=F(W['discounted_bias_remainder_lower_bound']['exact_interval'][0]);ru=F(W['discounted_bias_remainder_upper_bound']['exact_interval'][1])
    bl=lo(center)-hi(fee)+rl;bu=hi(center)+hi(fee)+ru
    assert max(abs(bl),abs(bu))<F(1,40)
    old=author['true_original_Asian_bias']['exact_interval']
    assert abs(bl-F(old[0]))<F(1,10**60) and abs(bu-F(old[1]))<F(1,10**60)
    wp=F(W['WP_upper_bound']['exact_interval'][1]);wq=F(W['WQ_upper_bound']['exact_interval'][1])
    pref=disc/(2*(2*pi*s).sqrt());Pfinite=15*disc+totalsP;Qfinite=15*disc+totalsQ
    pleft=lo(Pfinite)-hi(feeAlias+feeP+pref*ar(wp)/110)
    pright=hi(Pfinite)+hi(feeAlias+feeP+pref*ar(wp)/95)
    qleft=lo(Qfinite)-hi(feeAlias+feeQ+projection+pref*ar(wq)/110)
    qright=hi(Qfinite)+hi(feeAlias+feeQ+projection+pref*ar(wq)/95)
    assert counts['Q_layers']==6399744 and counts['P_path_guards']==799968
    result={'status':'INDEPENDENT_FULL_ORIGINAL_ASIAN_CERTIFICATE_PASS','source_sha256':sha(__file__),
        'author_source_sha256':sha(SOURCE),'author_result_sha256':sha(AUTHOR),'scope_sha256':sha(PROOF),
        'weighted_square_result_sha256':sha(WRESULT),'precision_bits':384,'counts':counts,
        'fees':{key:rec(x) for key,x in fees.items()},'linear_bias_finite':rec(center),
        'coefficient_abs_sum':rec(totalcoeff),'true_original_Asian_bias':span(bl,bu),
        'true_original_Asian_P':span(pleft,pright),'true_original_Asian_Q':span(qleft,qright),
        'original_theta_star_Asian_pass_0025':True,'frequency_rows':rows,
        'worker_seconds':time.perf_counter()-start,'job_limit_bytes':256<<20,'threads':1,
        'scope':'Original theta-star parameter point, original payoff and positive-part Euler scheme.'}
    with OUT.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps({key:result[key] for key in ('status','counts','true_original_Asian_bias','true_original_Asian_P','true_original_Asian_Q','worker_seconds')}))

def controller():
    assert all(not p.exists() for p in (OUT,FREEZE,CONTROL,CONSOLE))
    m=limits.MEMORY();m.length=ctypes.sizeof(m);assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    contract={'source_sha256':sha(__file__),'author_source_sha256':sha(SOURCE),'author_result_sha256':sha(AUTHOR),
      'scope_sha256':sha(PROOF),'W_result_sha256':sha(WRESULT),'precision_bits':384,'frequencies':641,
      'Q_layers':6399744,'P_guards':799968,'required_available_bytes':512<<20,
      'available_commit_bytes':m.available_commit,'available_physical_bytes':m.available_physical,
      'job_limit_bytes':256<<20,'threads':1,'hard_wall_seconds':180,'attempts':0}
    with FREEZE.open('x',encoding='utf-8') as f:json.dump(contract,f,indent=2)
    if min(m.available_commit,m.available_physical)<512<<20:contract['status']='NOT_RUN_MEMORY_PREFLIGHT'
    else:
        start=time.perf_counter();contract['attempts']=1
        with CONSOLE.open('x',encoding='utf-8') as f:
            child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'--worker'],stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000)
            try:child.wait(timeout=180);contract.update(status='FINISHED',returncode=child.returncode)
            except subprocess.TimeoutExpired:child.kill();child.wait();contract.update(status='HARD_WALL_STOPPED',returncode=child.returncode)
        contract['outer_seconds']=time.perf_counter()-start
    with CONTROL.open('x',encoding='utf-8') as f:json.dump(contract,f,indent=2)
    print(json.dumps(contract))

if __name__=='__main__':worker() if '--worker' in sys.argv else controller()
