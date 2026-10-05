"""Nonauthor scalar recomputation of deterministic-variance finite-h TT.
Does not import the author's pricing, coefficient, or bound code.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib, importlib.util, json, sys, time
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
HELPER=HERE/'resource_limits.py'
sp=importlib.util.spec_from_file_location('limits_independent',HELPER)
resource=importlib.util.module_from_spec(sp);sp.loader.exec_module(resource)
resource.hard_job();start=time.perf_counter()
from flint import arb, fmpq, ctx
ctx.prec=448;ctx.threads=1
def ar(x):
    x=F(x);return arb(fmpq(x.numerator,x.denominator))
def low(x):return F(str(x.lower().fmpq()))
def high(x):return F(str(x.upper().fmpq()))
def rec(x):return {'exact_interval':[str(low(x)),str(high(x))],
                   'outward24':resource.decimal_enclosure(low(x),high(x))}
def maxabs(x):return ar(max(abs(low(x)),abs(high(x))))
author_path=HERE/'deterministic-tt-result.json'
author=json.loads(author_path.read_text(encoding='utf-8'))
assert author['source_sha256']==sha(HERE/'deterministic-tt-certificate.py')
h=ar(F(1,768));eta=ar(F(255,256));dv=ar(F(3,200));r=ar(F(1,100))
vb=ar(F(9,200));b=ar(F(1,400));Bp=15*(-r).exp()
def w(T,scheme):
    a=(1-(-3*T).exp())/3 if scheme=='P' else (1-eta**int(F(str(T.mid().fmpq()))*768))/3
    return vb*T+dv*a
# Use exact rational times for discrete exponents rather than rounded Arb T.
def total(m,scheme):
    t=ar(F(m,12));c=(-3*t).exp() if scheme=='P' else eta**(64*m)
    return vb*t+dv*(1-c)/3
def first(m):
    t=ar(F(m,12));return dv*3*t*(-3*t).exp()/2
def rem(m):
    t=ar(F(m,12));return dv*(-3*t).exp()*(3*t/eta+27*t*t/(8*eta*eta))
steps=[];density_linear=arb(0);density_quad=arb(0);tv_squared=arb(0)
for j in range(1,13):
    variance=total(j,'P')-total(j-1,'P');numeric=total(j,'Q')-total(j-1,'Q')
    delta=numeric-variance;a=first(j)-first(j-1);R=rem(j)+rem(j-1)
    assert variance>ar(F(3,800)) and numeric>ar(F(3,800))
    assert maxabs(delta-h*a)<h*h*R
    density_linear+=R*R*(1/(2*b*b)+1/(4*b))
    density_quad+=(maxabs(a)+h*R)**2*(2/(b*b)+1/(2*b))
    tv_squared+=maxabs(delta)**2*(1/(8*b*b)+1/(16*b))
    steps.append({'j':j,'variance':rec(variance),'Euler_variance':rec(numeric),
                  'first_variance_coefficient':rec(a),'remainder_coefficient_bound':rec(R)})
C=density_linear.sqrt()+density_quad/2
bound_bias=Bp*tv_squared.sqrt();bound_R=Bp*C*h*h/2
def put(K,m,W):
    t=ar(F(m,12));sd=W.sqrt()
    d1=((100/ar(K)).log()+r*t+W/2)/sd;d2=d1-sd
    root2=ar(2).sqrt()
    return (ar(K)*(-r*t).exp()*(d2/root2).erfc()-100*(d1/root2).erfc())/2
rows=[];comparisons=0
for m in (3,6,12):
    T=ar(F(m,12));I=total(m,'P');IH=total(m,'Q')
    for K in (90,100,110):
        P=put(K,m,I);Q=put(K,m,IH)
        d1=((100/ar(K)).log()+r*T+I/2)/I.sqrt()
        beta=first(m)*100*(-d1*d1/2).exp()/(2*(2*arb.pi()*I).sqrt())
        remainder=Q-P-h*beta;generic=ar(K)*(-r*T).exp()*C*h*h/2
        assert beta>0 and maxabs(remainder)<generic
        old=next(x for x in author['runs'][-1]['puts'] if x['T']==str(F(m,12)) and x['K']==K)
        for key,value in [('P',P),('Q',Q),('signed_bias_Q_minus_P',Q-P),('TT_coefficient',beta),('true_remainder_at_h',remainder)]:
            l,u=map(F,old[key]['exact_interval'])
            assert max(l,low(value))<=min(u,high(value)),key
            comparisons+=1
        rows.append({'T':str(F(m,12)),'K':K,'P':rec(P),'Q':rec(Q),
                     'TT_coefficient':rec(beta),'actual_remainder':rec(remainder),'generic_bound':rec(generic)})
for key,value in [('density_remainder_C',C),('Asian_uniform_bias_upper',bound_bias),('Asian_uniform_TT_remainder_upper',bound_R)]:
    l,u=map(F,author['runs'][-1][key]['exact_interval'])
    assert max(abs(l-high(value)),abs(u-low(value)))<F(1,10**100)
    comparisons+=1
assert bound_bias<ar(F(1,40))
result={'status':'NONAUTHOR_RECOMPUTATION_PASS','precision_bits':448,
    'source_sha256':sha(Path(__file__)),'author_result_sha256':sha(author_path),
    'author_source_sha256':sha(HERE/'deterministic-tt-certificate.py'),
    'method':'independent scalar code; erfc put pricing; no author functions imported; shares only Arb and resource helper',
    'steps':steps,'density_remainder_C':rec(C),'Asian_uniform_bias_upper':rec(bound_bias),
    'Asian_uniform_TT_remainder_upper':rec(bound_R),'puts':rows,'verified_comparisons':comparisons,
    'note':'45 actual prices/coefficient/remainders overlap; 3 conservative formula bounds differ by less than 1e-100',
    'elapsed_seconds':time.perf_counter()-start,'memory_limit_MiB':256}
out=HERE/'check-tt-result.json';assert not out.exists()
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'comparisons':comparisons,
    'Asian_bias':rec(bound_bias)['outward24'],'Asian_TT_R':rec(bound_R)['outward24'],
    'elapsed_seconds':result['elapsed_seconds']}))
