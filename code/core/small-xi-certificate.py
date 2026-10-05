"""Finite five-dimensional positive-xi P/Q certificate; no Monte Carlo."""
from pathlib import Path
from fractions import Fraction as F
import hashlib, importlib.util, json, sys, time

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
LIMITS =HERE/'resource_limits.py'
spec = importlib.util.spec_from_file_location("limits", LIMITS)
limits = importlib.util.module_from_spec(spec)
spec.loader.exec_module(limits)
OUT = HERE / "small-xi-result.json"

def main():
    assert not OUT.exists(), "Preserve completed receipt"
    limits.hard_job()
    started = time.perf_counter()
    from flint import arb, fmpq, ctx
    ctx.prec = 192
    ctx.threads = 1
    def ar(x):
        x = F(x)
        return arb(fmpq(x.numerator, x.denominator))
    def lo(x): return F(str(x.lower().fmpq()))
    def hi(x): return F(str(x.upper().fmpq()))
    def box(a,b): return arb(ar((a+b)/2), ar((b-a)/2))
    def rec(x):
        a,b = lo(x),hi(x)
        return {"exact_interval": [str(a),str(b)],
                "outward18": limits.decimal_enclosure(a,b,18)}
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    source_sha = sha(__file__)
    h = F(1,768)
    k0,k1 = F("2.999"),F("3.001")
    m,M = F(".03001"),F(".05999")
    xi_min,xi_max = F(".00001"),F(".00004")
    assert h*k1 <= 1 and xi_max**2 <= k0*M/2
    subdivisions = 256
    width = (k1-k0)/subdivisions
    delta_bound = ar(F(".015"))
    u = ar(m/12)
    fisher = 1/(8*u*u) + 1/(16*u)
    discounted_cap = 15*(-ar(F(".01"))).exp()
    cc = ar(M/(2*k0)).sqrt()
    cd = ar(2*M/k0).sqrt()
    logfactor = (cc+cd)*(ar(F(1,2))+2/ar(m).sqrt())
    perturbation = 110*ar(xi_max)*logfactor
    records = []
    max_asian,max_put = F(0),F(0)
    worst_a=worst_p=None
    for cell in range(subdivisions):
        k = box(k0+cell*width,k0+(cell+1)*width)
        a = 1-k*ar(h)
        ec = [arb(0)]
        for j in range(1,13):
            t=F(j,12)
            ec.append(((-k*ar(t)).exp()-a**(64*j))/k)
        deltas = [delta_bound*abs(ec[j]-ec[j-1]) for j in range(1,13)]
        tv = sum((d*d*fisher for d in deltas),arb(0)).sqrt()
        asian = discounted_cap*tv
        puts = []
        for j in (3,6,12):
            T=F(j,12)
            err = 100*delta_bound*abs(ec[j])/(2*(2*arb.pi()*ar(m*T)).sqrt())
            puts.append({"T":str(T),"all_three_strikes_bound":rec(err)})
            if hi(err)>max_put:
                max_put=hi(err);worst_p=[cell,str(T)]
        if hi(asian)>max_asian:
            max_asian=hi(asian);worst_a=cell
        records.append({"cell":cell,"kappa_interval":[str(k0+cell*width),str(k0+(cell+1)*width)],
                        "deterministic_Asian_bound":rec(asian),
                        "deterministic_put_bounds":puts})
        assert time.perf_counter()-started<60,"finite wall-time guard"
    final_asian=ar(max_asian)+perturbation
    final_put=ar(max_put)+perturbation
    result = {
        "scope":"Original Q and original ten payoffs; Specified positive-xi five-dimensional box outside original xi domain.",
        "parameters":{"kappa":["2.999","3.001"],"vbar":[".04499",".04501"],
                      "v0":[".03001",".05999"],"xi":[".00001",".00004"],"rho":["-.8","-.3"]},
        "h":"1/768","S0":100,"r":".01","fixings":12,"Asian_strikes":[95,110],
        "gaussian_kappa_subcells":subdivisions,"kappa_subcell_width":str(width),
        "continuous_L2_coefficient":rec(cc),"discrete_L2_coefficient":rec(cd),
        "combined_log_path_coefficient":rec(logfactor),
        "all_ten_positive_xi_perturbation_bound":rec(perturbation),
        "deterministic_Asian_uniform_upper":str(max_asian),
        "deterministic_put_uniform_upper":str(max_put),
        "worst_Asian_subcell":worst_a,"worst_put_subcell_and_T":worst_p,
        "original_Asian_positive_xi_bias_bound":rec(final_asian),
        "all_nine_put_positive_xi_bias_bound":rec(final_put),
        "all_ten_pass_0.025":max(hi(final_asian),hi(final_put)) < F(1,40),
        "cell_evidence":records,
        "source_sha256":source_sha,"scope_sha256":sha(HERE.parent/'SCOPE.md'),
        "runtime":{"precision_bits":192,"threads":1,"memory_limit_MiB":256,
                   "wall_guard_seconds":60,"elapsed_seconds":time.perf_counter()-started,
                   "path_samples":0},
        "status":"PASS_CONDITIONAL_ON_ARB_INCLUSIONS"
    }
    assert sha(__file__)==source_sha
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("all_ten_pass_0.025",
        "original_Asian_positive_xi_bias_bound","all_nine_put_positive_xi_bias_bound",
        "all_ten_positive_xi_perturbation_bound","runtime")},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
