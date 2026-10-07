"""Reproducible Monte Carlo diagnostics; no continuous-price certification.

Two implementations of the same original projected Euler kernel are coupled by
aggregating pairs of fine independent normal increments into a coarse increment.
Reported 95% intervals use a normal approximation and estimated sampling error.
The fine price still contains discretization bias and is not a true-price oracle.
"""
from pathlib import Path
import argparse, hashlib, json, math, time
import numpy as np

def payoff(a, k1, k2):
    return np.maximum(a-k1, 0)-np.maximum(a-k2, 0)

def case(name, steps=768, fixings=12, xi=.23, rho=-.55, v0=.045,
         k1=95, k2=110):
    assert steps % fixings == 0 and k1 < k2 and abs(rho) < 1
    return dict(name=name, steps=steps, fixings=fixings, kappa=3., vbar=.045,
                xi=xi, rho=rho, v0=v0, r=.01, S0=100., K1=k1, K2=k2)

def calculate(c, paths, seed):
    rng=np.random.default_rng(seed)
    n=c['steps']; h=1/n; hf=h/2; every=n//c['fixings']
    vf=np.full(paths,c['v0']);vc=vf.copy()
    zf=np.zeros(paths);zc=zf.copy();af=zf.copy();ac=zf.copy();first=zf.copy()
    coarse_projection=fine_projection=0
    sr=math.sqrt(1-c['rho']**2)
    def fine_step(g,b,j):
        nonlocal vf,zf,fine_projection
        old=vf; root=np.sqrt(hf*old)
        zf=zf+(c['r']-.5*old)*hf+root*(c['rho']*g+sr*b)
        if j < 2*every:first[:] += hf*old
        raw=(1-c['kappa']*hf)*old+c['kappa']*c['vbar']*hf+c['xi']*root*g
        fine_projection += int(np.count_nonzero(raw<0))
        vf=np.maximum(raw,0)
    for j in range(n):
        g1,b1,g2,b2=rng.standard_normal((4,paths))
        old=vc;root=np.sqrt(h*old)
        zc=zc+(c['r']-.5*old)*h+root*(c['rho']*(g1+g2)/math.sqrt(2)+sr*(b1+b2)/math.sqrt(2))
        raw=(1-c['kappa']*h)*old+c['kappa']*c['vbar']*h+c['xi']*root*(g1+g2)/math.sqrt(2)
        coarse_projection += int(np.count_nonzero(raw<0));vc=np.maximum(raw,0)
        fine_step(g1,b1,2*j);fine_step(g2,b2,2*j+1)
        if (j+1)%every==0:
            ac += c['S0']*np.exp(zc);af += c['S0']*np.exp(zf)
    disc=math.exp(-c['r'])
    coarse=disc*payoff(ac/c['fixings'],c['K1'],c['K2'])
    fine=disc*payoff(af/c['fixings'],c['K1'],c['K2']);delta=coarse-fine
    def stats(x):
        mean=float(x.mean());se=float(x.std(ddof=1)/math.sqrt(paths))
        return dict(estimate=mean,standard_error=se,normal_approximation_95_interval=[mean-1.96*se,mean+1.96*se])
    return dict(input=c,paths=paths,seed=seed,
        fine_step=f'1/{2*n}',coarse_step=f'1/{n}',
        feller_index=2*c['kappa']*c['vbar']/c['xi']**2,
        coarse_price=stats(coarse),fine_price=stats(fine),coupled_coarse_minus_fine=stats(delta),
        fine_mean_first_integrated_variance_inverse_sqrt=float(np.mean(1/np.sqrt(first))),
        projected_negative_transition_fraction_coarse=coarse_projection/(n*paths),
        projected_negative_transition_fraction_fine=fine_projection/(2*n*paths),
        status='STATISTICAL_DIAGNOSTIC',certified_continuous_model_interval=None,
        limitations='Sampling intervals are approximate; fine Euler retains unknown continuous-model bias. No rigorous tails or moment inequalities are inferred from these paths.')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--paths',type=int,default=32768)
    ap.add_argument('--out',type=Path,default=Path('out/revision/path-diagnostics.json'))
    args=ap.parse_args();assert args.paths>=2
    cases=[case('h192',steps=192),case('h384',steps=384),case('main_h768'),case('h1536',steps=1536),
           case('feller_near_one',xi=.52),case('feller_below_one',xi=.65),
           case('rho_minus_08',rho=-.8),case('rho_minus_03',rho=-.3),
           case('v0_003',v0=.03),case('v0_006',v0=.06),
           case('strikes_90_105',k1=90,k2=105),case('strikes_105_120',k1=105,k2=120),
           case('fixings_52',fixings=52,steps=832),case('fixings_252',fixings=252,steps=1008)]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    result=dict(schema_version=1,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
       numpy_version=np.__version__,status='RUNNING',rows=[],
       interpretation='All rows are statistical diagnostics, independent from validated transform implementations. They do not certify continuous prices. The fixing-count experiment also changes the aligned Euler grid.')
    started=time.perf_counter()
    for i,c in enumerate(cases):
        row=calculate(c,args.paths,20261007+i);result['rows'].append(row)
        args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
        print(json.dumps({'case':c['name'],'difference':row['coupled_coarse_minus_fine'],'seconds':time.perf_counter()-started}),flush=True)
    result.update(status='COMPLETE_STATISTICAL_DIAGNOSTICS',elapsed_seconds=time.perf_counter()-started)
    args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
