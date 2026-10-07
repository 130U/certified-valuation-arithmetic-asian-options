"""Sample the signed Gaussian coefficient and stable weak residuals (diagnostic).

The density ratio evaluates the finite-h weak error under the continuous
deterministic-variance Gaussian law, using the same sampled Y for every h.
No sample interval is a deterministic integral enclosure or nonzero proof.
"""
from pathlib import Path
import argparse,hashlib,json,math,time
import numpy as np

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--paths',type=int,default=2097152)
    ap.add_argument('--out',type=Path,default=Path('code/revision/results/asian-beta-diagnostic.json'))
    a=ap.parse_args();assert a.paths%32768==0
    rng=np.random.default_rng(2026100701);t=np.arange(13)/12
    result=dict(status='STATISTICAL_DIAGNOSTIC',paths=a.paths,seed=2026100701,
       numpy_version=np.__version__,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=[],
       limitations='Normal-approximation intervals use estimated sampling error. Neither signed coefficient nor continuous-model price is rigorously enclosed. Residuals use exact Gaussian law formulas evaluated in binary64.')
    started=time.perf_counter()
    for v in [.03,.04,.05,.06]:
        D=v-.045;I=.045*t+D*(-np.expm1(-3*t))/3;s=np.diff(I)
        d=np.diff(D*3*t*np.exp(-3*t)/2);m=.01/12-s/2
        totals=np.zeros(6);squares=np.zeros(6)
        Ns=[192,384,768,1536]
        shs=[np.diff(.045*t+D*(-np.expm1(N*t*np.log1p(-3/N)))/3) for N in Ns]
        for _ in range(a.paths//32768):
            z=rng.standard_normal((32768,12));y=m+np.sqrt(s)*z
            avg=100*np.exp(np.cumsum(y,axis=1)).mean(axis=1)
            pay=np.maximum(avg-95,0)-np.maximum(avg-110,0)
            centred=math.exp(-.01)*(pay-7.5)
            score=((z*z-1)/(2*s)-z/(2*np.sqrt(s)))@d
            cols=[centred*score,math.exp(-.01)*pay]
            for N,sh in zip(Ns,shs):
                mh=.01/12-sh/2
                logratio=(-.5*np.log(sh/s)-(y-mh)**2/(2*sh)+z*z/2).sum(axis=1)
                cols.append(centred*(np.expm1(logratio)-score/N)*N*N)
            values=np.column_stack(cols);totals+=values.sum(axis=0);squares+=(values*values).sum(axis=0)
        means=totals/a.paths;ses=np.sqrt((squares-a.paths*means*means)/(a.paths-1)/a.paths)
        def stats(i):return dict(estimate=float(means[i]),standard_error=float(ses[i]),normal_approximation_95_interval=[float(means[i]-1.96*ses[i]),float(means[i]+1.96*ses[i])])
        row=dict(v0=str(v),beta_Asian=stats(0),continuous_Asian_price=stats(1),scaled_weak_residuals=[dict(h=f'1/{N}',quantity='(e_h-h beta)/h^2',**stats(i+2)) for i,N in enumerate(Ns)])
        result['rows'].append(row)
        print(json.dumps({'v0':v,'beta':row['beta_Asian'],'residual_h768':row['scaled_weak_residuals'][2]}),flush=True)
    result['elapsed_seconds']=time.perf_counter()-started
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
