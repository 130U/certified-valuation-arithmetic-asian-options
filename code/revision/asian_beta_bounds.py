"""Pointwise analytic score enclosures, not a signed 12D Asian beta integration."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,importlib.util,json,sys,time
CODE=Path(__file__).resolve().parents[1]
HELP=CODE/'core'/'resource_limits.py'
sp=importlib.util.spec_from_file_location('lim',HELP);lim=importlib.util.module_from_spec(sp);sp.loader.exec_module(lim)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main(output):
    assert not output.exists() and not sys.flags.optimize
    lim.hard_job();start=time.perf_counter()
    from flint import arb,fmpq,ctx
    ctx.threads=1
    def ar(x):x=F(x);return arb(fmpq(x.numerator,x.denominator))
    def lo(x):return F(str(x.lower().fmpq()))
    def hi(x):return F(str(x.upper().fmpq()))
    def rec(x):return {'exact_interval':[str(lo(x)),str(hi(x))],'outward24':lim.decimal_enclosure(lo(x),hi(x))}
    runs=[]
    for bits in (384,512):
        ctx.prec=bits;rows=[]
        k=ar(3);vb=ar(F(9,200));disc=(-ar(F(1,100))).exp();B=15*disc
        for vf in (F(3,100),F(1,25),F(1,20),F(3,50)):
            dv=ar(vf-F(9,200));I=[];coeff=[];density_fisher=arb(0);direct=arb(0)
            for j in range(13):
                t=ar(F(j,12));ex=(-k*t).exp()
                I.append(vb*t+dv*(1-ex)/k);coeff.append(dv*k*t*ex/2)
            increment=[]
            for j in range(1,13):
                s=I[j]-I[j-1];a=coeff[j]-coeff[j-1];assert s>0
                fisher=a*a*(1/(2*s*s)+1/(4*s));density_fisher+=fisher
                tj=ar(F(j,12));tp=ar(F(j-1,12))
                a2=dv*k*(tj*(-k*tj).exp()-tp*(-k*tp).exp())/2
                direct+=(a2/s)**2/2+a2*a2/(4*s)
                assert max(lo(a),lo(a2))<=min(hi(a),hi(a2))
                increment.append({'fixing':j,'continuous_increment_variance':rec(s),'first_variance_coefficient':rec(a)})
            bound=B*density_fisher.sqrt()/2;alternative=B*direct.sqrt()/2
            assert max(lo(bound),lo(alternative))<=min(hi(bound),hi(alternative))
            errors=[]
            for N in (768,1536):
                h=ar(F(1,N));eta=1-k*h;RI=[];Ih=[]
                for j in range(13):
                    t=ar(F(j,12));ex=(-k*t).exp()
                    Ih.append(vb*t+dv*(1-eta**(N*j//12))/k)
                    RI.append(abs(dv)*ex*(k*k*t/(3*eta)+k**3*t*t/(8*eta**2)))
                t1=arb(0);t2=arb(0)
                for j in range(1,13):
                    s=I[j]-I[j-1];sh=Ih[j]-Ih[j-1];a=coeff[j]-coeff[j-1];R=RI[j]+RI[j-1]
                    u=ar(min(lo(s),lo(sh)));assert u>0
                    assert hi(abs(sh-s-h*a)-h*h*R)<=0
                    t1+=R*R*(1/(2*u*u)+1/(4*u))
                    t2+=(abs(a)+h*R)**2*(2/(u*u)+1/(2*u))
                C=t1.sqrt()+t2/2;remainder=B*C*h*h/2
                errors.append({'h':str(F(1,N)),'analytic_absolute_bound_on_eh_minus_h_beta':rec(remainder)})
            rows.append({'v0':str(vf),'beta_Asian_signed_enclosure':{'exact_interval':[str(-hi(bound)),str(hi(bound))],
                        'outward24':lim.decimal_enclosure(-hi(bound),hi(bound))},'absolute_score_bound':rec(bound),
                        'increment_records':increment,'aligned_step_remainder_bounds':errors})
        runs.append({'precision_bits':bits,'rows':rows})
    for a,b in zip(runs[0]['rows'],runs[1]['rows']):
        assert abs(F(a['absolute_score_bound']['exact_interval'][1])-F(b['absolute_score_bound']['exact_interval'][1]))<F(1,10**80)
    result={'status':'ANALYTIC_SCORE_AND_ALIGNED_STEP_REMAINDER_ENCLOSURES_COMPLETE',
       'scope':'xi=0, kappa=3, vbar=.045, S0=100, r=.01, 12 equally spaced fixings, Asian call spread 95/110.',
       'source_sha256':sha(__file__),'base_formula_source_sha256':sha(CODE/'core'/'deterministic-tt-certificate.py'),
       'resource_helper_sha256':sha(HELP),'runs':runs,'elapsed_seconds':time.perf_counter()-start,'memory_limit_MiB':256,
       'no_claim':['No 12-dimensional integration of the signed Asian leading coefficient was performed.','Every signed enclosure contains zero; no nonzero Asian coefficient is certified.','The h^2 bounds are analytical; no empirical residual-order experiment is represented as completed.','Cross precision and algebraic re-expression are not independent proof derivations.']}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps([{'v0':x['v0'],'beta_interval':x['beta_Asian_signed_enclosure']['outward24'],'remainder_768':x['aligned_step_remainder_bounds'][0]['analytic_absolute_bound_on_eh_minus_h_beta']['outward24']} for x in runs[-1]['rows']],indent=2))
if __name__=='__main__':main(Path(sys.argv[1]).resolve())
