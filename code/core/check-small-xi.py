"""Independent stable-expm1 384-bit readback of the positive-xi box constants."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,time,hashlib,importlib.util
HERE=Path(__file__).resolve().parent
helperpath=HERE/'resource_limits.py'
spec=importlib.util.spec_from_file_location('lim',helperpath);lim=importlib.util.module_from_spec(spec);spec.loader.exec_module(lim)
lim.hard_job();start=time.perf_counter()
from flint import arb,fmpq,ctx
ctx.prec=384;ctx.threads=1
def ar(x):
    x=F(x);return arb(fmpq(x.numerator,x.denominator))
def hi(x):return F(str(x.upper().fmpq()))
def rec(x):
    low=F(str(x.lower().fmpq()));up=hi(x)
    return {'exact_interval':[str(low),str(up)],'outward24':lim.decimal_enclosure(low,up)}
N=128;klo=F(2999,1000);dk=F(1,500)/N;m=F(3001,100000);M=F(5999,100000);h=F(1,768)
assert F(1,25000)**2<=klo*M/2 and (klo+N*dk)*h<=1
factor=3*ar(M/(2*klo)).sqrt()*(ar(F(1,2))+2/ar(m).sqrt())
pert=ar(F(110,25000))*factor
aa=F(0);pp=F(0);rows=[]
for n in range(N):
    k=arb(ar(klo+(n+F(1,2))*dk),ar(dk/2));kh=k*ar(h)
    base=(1-kh).log()+kh
    e=[arb(0)]
    for j in range(1,13):
        t=ar(F(j,12));e.append((-k*t).exp()*(-(base*(64*j)).expm1())/k)
    norm2=sum(((e[j]-e[j-1])**2 for j in range(1,13)),arb(0))
    detA=15*(-ar(F(1,100))).exp()*ar(F(3,200))*((18/ar(m)**2+ar(F(3,4))/ar(m))*norm2).sqrt()
    detP=[]
    for j in (3,6,12):detP.append(50*ar(F(3,200))*abs(e[j])/(2*arb.pi()*ar(m*F(j,12))).sqrt())
    aa=max(aa,hi(detA));pp=max(pp,*map(hi,detP));rows.append({'cell':n,'Asian':rec(detA),'puts':[rec(x) for x in detP]})
    assert time.perf_counter()-start<30
out={'status':'INDEPENDENT_384_BIT_STABLE_FORM_ALL_TEN_PASS','method':'128 kappa cells, cancellation-free expm1 expression; distinct from author direct subtraction/256 cells',
     'Asian_bound':rec(ar(aa)+pert),'put_bound':rec(ar(pp)+pert),'positive_xi_perturbation':rec(pert),'all_ten_pass':max(aa,pp)+hi(pert)<F(1,40),
     'precision_bits':384,'memory_MiB':256,'threads':1,'seconds':time.perf_counter()-start,'rows':rows,
     'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
     'scope_sha256':hashlib.sha256((HERE.parent/'SCOPE.md').read_bytes()).hexdigest(),
     'author_result_sha256':hashlib.sha256((HERE/'small-xi-result.json').read_bytes()).hexdigest()}
assert out['all_ten_pass']
(HERE/'check-small-xi-result.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
