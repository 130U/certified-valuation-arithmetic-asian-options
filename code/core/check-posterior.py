"""Independent endpoint/interval-arithmetic/coupling verification of all 4096 cells."""
from pathlib import Path
from fractions import Fraction as F
import bisect, ctypes, hashlib, importlib.util, json, os, subprocess, sys, time

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
AUTHOR=HERE/'posterior-compat-4096-result.json'
QUOTES=HERE.parent/'data'/'synthetic_quotes.json'
HELPER=HERE/'resource_limits.py'
spec=importlib.util.spec_from_file_location('certificate_limits',HELPER)
limits=importlib.util.module_from_spec(spec);spec.loader.exec_module(limits)
OUT=HERE/'check-posterior-result.json'
CONTROL=HERE/'check-posterior-controller.json'
FREEZE=HERE/'check-posterior-contract.json'
CONSOLE=HERE/'check-posterior-console.txt'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def worker():
    assert not OUT.exists()
    start=time.perf_counter();limits.hard_job()
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
    from flint import arb,fmpq,ctx
    ctx.prec=384;ctx.threads=1
    def ar(x):
        x=F(x);return arb(fmpq(x.numerator,x.denominator))
    def lo(x):return F(str(x.lower().fmpq()))
    def hi(x):return F(str(x.upper().fmpq()))
    def rec(x):return {'exact_interval':[str(lo(x)),str(hi(x))],'outward24':limits.decimal_enclosure(lo(x),hi(x),24)}
    def floor_scaled(x,s):return x.numerator*s//x.denominator
    def ceil_scaled(x,s):return -((-x.numerator*s)//x.denominator)
    author=json.loads(AUTHOR.read_text(encoding='utf-8'))
    q=[F.from_float(x) for x in json.loads(QUOTES.read_text(encoding='utf-8'))['quotes']]
    assert list(map(str,q))==author['quotes_exact_dyadic']
    assert author['source_sha256']==sha(HERE/'posterior-compat-certificate.py')
    assert author['quotes_source_sha256']==sha(QUOTES)
    M=4096;left=F(3,100);dx=F(3,100*M);vb=ar(F(9,200));r=ar(F(1,100))
    PS=1<<128;WS=1<<96
    qi=[int(x*PS) for x in q];assert all(F(y,PS)==x for x,y in zip(q,qi))
    tt=[F(1,4),F(1,2),F(1)];sqrt2=ar(2).sqrt()
    eta=ar(F(255,256))
    def b(m,t):return (1-(-3*ar(t)).exp())/3 if m=='P' else (1-eta**int(768*t))/3
    bb={m:[b(m,t) for t in tt] for m in ('P','Q')}
    dd=[(-r*ar(t)).exp() for t in tt]
    logsk=[ar(F(100,k)).log() for k in (90,100,110)]
    xi=ar(F(1,10**6));vmin=ar(F(3,100))
    assert F(1,10)**2==F(3,50)/6 and F(1,5)**2==F(3,50)*2/3
    radii={};radius_int={};target_radii={}
    for m,C in (('P',ar(F(1,10))),('Q',ar(F(1,5)))):
        radii[m]=[]
        for ti,t in enumerate(tt):
            D=xi*C*(ar(t)/2+2*(ar(t)/vmin).sqrt())
            radii[m].extend([ar(K)*dd[ti]*D for K in (90,100,110)])
        radius_int[m]=[ceil_scaled(hi(x),PS) for x in radii[m]]
        target_radii[m]=110*(-r).exp()*xi*C*(ar(F(1,2))+2/vmin.sqrt())
        for j,x in enumerate(radii[m]):
            old=author['comparison_to_zero_xi_price_radii'][m][j]['exact_interval']
            assert max(lo(x),F(old[0]))<=min(hi(x),F(old[1]))
        old=author['comparison_to_zero_xi_target_radii'][m]['exact_interval']
        assert max(lo(target_radii[m]),F(old[0]))<=min(hi(target_radii[m]),F(old[1]))
    def price_endpoints(m,u):
        out=[]
        for j,t in enumerate(tt):
            v=vb*ar(t)+(ar(u)-vb)*bb[m][j];s=v.sqrt()
            for ki,K in enumerate((90,100,110)):
                d1=(logsk[ki]+r*ar(t)+v/2)/s;d2=d1-s
                # Direct complementary-error-function tails; no author helper.
                p=(K*dd[j]*(d2/sqrt2).erfc()-100*(d1/sqrt2).erfc())/2
                out.append((floor_scaled(lo(p),PS),ceil_scaled(hi(p),PS)))
        return out
    def square_range(l,u):
        return (0 if l<=0<=u else min(l*l,u*u),max(l*l,u*u))
    weights={m:{'d1':[],'d9':[]} for m in ('P','Q')};containment=0
    for m in ('P','Q'):
        prev=price_endpoints(m,left)
        for i in range(M):
            nxt=price_endpoints(m,left+(i+1)*dx)
            rr=[(prev[j][0]-qi[j]-radius_int[m][j],nxt[j][1]-qi[j]+radius_int[m][j]) for j in range(9)]
            for name,rs in (('d1',[rr[7]]),('d9',rr)):
                n=len(rs);ql=qu=0
                for l,u in rs:
                    x,y=square_range(l,u);ql+=3*x;qu+=3*y
                for j in range(n):
                    for k in range(j+1,n):
                        x,y=square_range(rs[j][0]-rs[k][1],rs[j][1]-rs[k][0]);ql+=x;qu+=y
                potlo=F(32*ql,27*(n+3)*PS*PS);pothi=F(32*qu,27*(n+3)*PS*PS)
                wl=(-ar(pothi)).exp();wu=(-ar(potlo)).exp()
                wi=[floor_scaled(lo(wl),WS),ceil_scaled(hi(wu),WS)]
                assert 0<wi[0]<=wi[1]<=WS
                old=author['whole_cell_weights_integer_bounds'][m][name][i]
                assert old[0]<=wi[0]<=wi[1]<=old[1],(m,name,i,old,wi)
                containment+=1;weights[m][name].append(wi)
            prev=nxt
    def envelopes(rows):
        total_l=sum(x[0] for x in rows);total_u=sum(x[1] for x in rows)
        ll=[F(0)];uu=[F(0)];pl=pu=0
        for l,u in rows:
            pl+=l;pu+=u
            ll.append(F(pl,pl+total_u-pu));uu.append(F(pu,pu+total_l-pl))
        assert all(ll[i]<=ll[i+1] and uu[i]<=uu[i+1] for i in range(M))
        return ll,uu,[str(F(total_l,M*WS)),str(F(total_u,M*WS))]
    transport={};author_transport_checks=0
    for name in ('d1','d9'):
        # Reconstruct both principal and independently paid boxes using independently
        # ordered advancing pointers; no binary-search convention is shared.
        record={}
        for typ,ww in (('author',author['whole_cell_weights_integer_bounds']),('independent',weights)):
            lp,up,zp=envelopes(ww['P'][name]);lq,uq,zq=envelopes(ww['Q'][name])
            lowj=highj=0;maxdist=0;witness=None
            for i in range(M):
                while lowj<M-1 and uq[lowj+1]<lp[i]:lowj+=1
                while highj<M-1 and lq[highj+1]<=up[i+1]:highj+=1
                assert lowj<=highj
                d=max(abs(i-highj-1),abs(i+1-lowj))
                if d>maxdist:maxdist=d;witness=[i,lowj,highj]
            record[typ]={'delta_u':str(maxdist*dx),'max_steps':maxdist,'witness':witness,
                         'normalizer_P':zp,'normalizer_Q':zq}
            if typ=='author':
                assert str(maxdist*dx)==author['transports'][name]['all_p_parameter_Winfinity_bound']
                author_transport_checks+=M
        transport[name]=record
    Ip=arb(0);Is=arb(0);months=[]
    for j in range(1,13):
        t0=F(j-1,12);t1=F(j,12)
        ap=b('P',t1)-b('P',t0);aq=b('Q',t1)-b('Q',t0)
        sp=vb/12+(ar(left)-vb)*ap;sq=vb/12+(ar(left)-vb)*aq
        sm=ar(min(lo(sp),lo(sq)));delta=ar(F(3,200))*(aq-ap)
        Ip+=ap*ap*(1/(2*sp*sp)+1/(4*sp))
        Is+=delta*delta*(1/(2*sm*sm)+1/(4*sm))
        months.append({'j':j,'continuous_increment_at_vmin':rec(sp),'discrete_increment_at_vmin':rec(sq)})
    B=15*(-r).exp();L=B*Ip.sqrt()/2;eps=B*Is.sqrt()/2
    for name,record in transport.items():
        d=F(record['independent']['delta_u']);bound=eps+target_radii['P']+target_radii['Q']+L*ar(d)
        record['independent_target_bound']=rec(bound);assert hi(bound)<F(1,10)
        # Precision-dependent rational lower endpoints make eps an upper bound,
        # not exactly the same number at 192/384 bits. Check close values.
        old=author['transports'][name]['all_target_quantile_levels_absolute_PQ_difference_bound']['exact_interval']
        author_bound=eps+target_radii['P']+target_radii['Q']+L*ar(F(record['author']['delta_u']))
        assert abs(hi(author_bound)-F(old[1]))<F(1,10**40)
    result={'status':'INDEPENDENT_POSITIVE_XI_3D_POSTERIOR_AUDIT_PASS',
            'source_sha256':sha(__file__),'author_result_sha256':sha(AUTHOR),
            'author_source_sha256':sha(HERE/'posterior-compat-certificate.py'),
            'quotes_sha256':sha(QUOTES),'cells':M,'precision_bits':384,
            'new_method':'erfc Black tails; exact 128-bit integer price interval quadratic squares; two advancing pointers for coupling',
            'certified_author_whole_cell_weight_containments':containment,
            'author_transport_cell_checks':author_transport_checks,
            'whole_cell_weights_integer_bounds':weights,'transports':transport,
            'L':rec(L),'epsilon_reference':rec(eps),'positive_xi_target_radii':{m:rec(x) for m,x in target_radii.items()},
            'positive_xi_price_radii':{m:[rec(x) for x in xx] for m,xx in radii.items()},'month_checks':months,
            'all_quantile_levels_pass_0.10':True,'Asian_price_queries':0,
            'worker_seconds':time.perf_counter()-start,'job_limit_bytes':256<<20,'threads':1}
    with OUT.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2)
    print(json.dumps({k:result[k] for k in ('status','certified_author_whole_cell_weight_containments','author_transport_cell_checks','L','epsilon_reference','positive_xi_target_radii','worker_seconds')}))

def controller():
    assert all(not p.exists() for p in (OUT,CONTROL,FREEZE,CONSOLE))
    mem=limits.MEMORY();mem.length=ctypes.sizeof(mem);assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    contract={'source_sha256':sha(__file__),'author_result_sha256':sha(AUTHOR),'quotes_sha256':sha(QUOTES),
              'resource_helper_sha256':sha(HELPER),'job_limit_bytes':256<<20,'threads':1,'hard_wall_seconds':60,
              'available_commit_bytes':mem.available_commit,'available_physical_bytes':mem.available_physical,'attempts':0}
    with FREEZE.open('x',encoding='utf-8') as stream:json.dump(contract,stream,indent=2)
    if min(mem.available_commit,mem.available_physical)<512<<20:contract['status']='NOT_RUN_MEMORY_PREFLIGHT'
    else:
        start=time.perf_counter();contract['attempts']=1
        with CONSOLE.open('x',encoding='utf-8') as stream:
            child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'--worker'],stdout=stream,stderr=subprocess.STDOUT,creationflags=0x08000000)
            try:child.wait(timeout=60);contract.update(status='FINISHED',returncode=child.returncode)
            except subprocess.TimeoutExpired:child.kill();child.wait();contract.update(status='HARD_WALL_STOPPED',returncode=child.returncode)
        contract['outer_seconds']=time.perf_counter()-start
    with CONTROL.open('x',encoding='utf-8') as stream:json.dump(contract,stream,indent=2)
    print(json.dumps(contract))

if __name__=='__main__':worker() if '--worker' in sys.argv else controller()
