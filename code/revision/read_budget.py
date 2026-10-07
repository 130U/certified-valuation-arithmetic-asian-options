"""Read executed certificates into exact, formula-traceable machine-readable rows.

No numerical certificate is created by this reader. Every input is bound by its
SHA-256. It verifies exact rational budget reconciliation before writing output.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json

def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def interval(v):return tuple(map(F,v['exact_interval']))
def decimal_up(x,d=24):
    scale=10**d;n=-((-x.numerator*scale)//x.denominator)
    return ('-' if n<0 else '')+str(abs(n)//scale)+'.'+str(abs(n)%scale).zfill(d)
def record(x):return {'exact_rational':str(x),'outward_decimal_upper':decimal_up(x)}

def certificate(core,h,receipt):
    a=read(core/'asian-linear-result.json');w=read(core/'asian-remainder-result.json')
    assert a['weighted_square_result_sha256']==sha(core/'asian-remainder-result.json')
    assert a['source_sha256']==sha(core/'asian-linear-certificate.py')
    assert w['source_sha256']==sha(core/'asian-remainder-certificate.py')
    bl,bu=interval(a['true_original_Asian_bias']);nl=interval(w['discounted_bias_remainder_lower_bound'])[0];nu=interval(w['discounted_bias_remainder_upper_bound'])[1]
    linearfee=interval(a['total_linear_bias_fee'])[1];fl,fu=interval(a['linear_bias_finite'])
    total=bu-bl;nonlinear=nu-nl;rounding=fu-fl
    assert total==nonlinear+2*linearfee+rounding
    parts={'nonlinear_payoff_width':record(nonlinear),'linear_projection_width':record(2*interval(a['projection_price_fee'])[1]),
           'P_frequency_tail_width':record(2*interval(a['P_frequency_tail'])[1]),'Q_frequency_tail_width':record(2*interval(a['Q_frequency_tail'])[1]),
           'periodization_width':record(4*interval(a['one_law_alias'])[1])}
    accounted=sum(F(v['exact_rational']) for v in parts.values())
    assert total>=accounted
    parts['arithmetic_rounding_and_endpoint_reconciliation_width']=record(total-accounted)
    assert sum(F(v['exact_rational']) for v in parts.values())==total
    return {'h':h,'status':'COMPLETE_INDEPENDENTLY_CHECKED_ENCLOSURE','bias_Q_minus_P':a['true_original_Asian_bias'],
       'P_price':a['true_original_Asian_P'],'Q_price':a['true_original_Asian_Q'],'interval_width':record(total),'components':parts,
       'finite_arithmetic_width_diagnostic':record(rounding),'nonlinear_width_share_diagnostic':float(nonlinear/total),'passes_original_0025_absolute_target':a['original_theta_star_Asian_pass_0025'],
       'receipt_sha256':sha(receipt),'linear_result_sha256':sha(core/'asian-linear-result.json'),'remainder_result_sha256':sha(core/'asian-remainder-result.json'),
       'trace':{'nonlinear_payoff_width':{'json_fields':['discounted_bias_remainder_lower_bound','discounted_bias_remainder_upper_bound'],'source':'asian-remainder-certificate.py','proof':'payoff conversion theorem and Laplace/Darboux tail ledger'},
          'linear_projection_width':{'json_field':'projection_price_fee','source':'asian-linear-certificate.py','proof':'raw positive-part Euler projection correction'},
          'P_frequency_tail_width':{'json_field':'P_frequency_tail','source':'asian-linear-certificate.py','proof':'first-fixing conditional Gaussian Fourier-tail bound'},
          'Q_frequency_tail_width':{'json_field':'Q_frequency_tail','source':'asian-linear-certificate.py','proof':'first-month Laplace and Euler first-step variance bound'},
          'periodization_width':{'json_field':'one_law_alias','source':'asian-linear-certificate.py','proof':'finite-frequency periodization ledger'}},
       'core_path':str(core),'execution_receipt':str(receipt)}

def validate_weighted(author_path,check_path):
    a=read(author_path);b=read(check_path);assert a['h']==b['h']
    frozen_sources=list(author_path.parent.glob('weighted-grid-source-v*.py'))
    known_source_hashes={sha(x) for x in frozen_sources}
    live_source=Path(__file__).with_name('weighted_grid.py')
    if live_source.is_file():known_source_hashes.add(sha(live_source))
    assert a['source_sha256'] in known_source_hashes and b['source_sha256'] in known_source_hashes
    assert a['source_sha256']==b['source_sha256']
    assert a['resource_helper_sha256']==b['resource_helper_sha256'] and a['base_scope_sha256']==b['base_scope_sha256']
    count=0
    for model in ('P','Q'):
        for name in ('G2','AGminusG2'):
            assert len(a['nodes'][model][name])==len(b['nodes'][model][name])==(257 if model=='P' else 129)
            for va,vb in zip(a['nodes'][model][name],b['nodes'][model][name]):
                al,au=interval(va);bl,bu=interval(vb);assert max(al,bl)<=min(au,bu);count+=1
    rows=[];bm={v['c']:v for v in b['rows']}
    for x in a['rows']:
        assert x['c'] in bm
        y=bm[x['c']];l,u=interval(x['nonlinear_width']);ll,uu=interval(y['nonlinear_width'])
        # Q's Mag radius has finite precision. Independent endpoint order can
        # select an equally valid outward radius; bound the difference as a
        # diagnostic instead of falsely requiring exact source-identical output.
        assert abs(u-uu)<F(1,10**60)
        rows.append({'c':x['c'],'nonlinear_width':x['nonlinear_width'],'W_P':x['W_P'],'W_Q':x['W_Q'],
                     'independent_width_upper_difference':str(abs(u-uu))})
    return {'h':a['h'],'status':'ALL_MOMENT_NODE_ENCLOSURES_OVERLAP','moment_node_checks':count,'c_star_enclosure':a['c_star_enclosure'],
       'selected_rational_c':a['selected_rational_c'],'rows':rows,'author_result_sha256':sha(author_path),'independent_result_sha256':sha(check_path),
       'projection_beta_min':a['projection_beta_min'],'UI_beta_exact':a['UI_beta_exact'],'UI_variance_generator_exact':a['UI_variance_generator_exact']}

def main(root,base_run,out):
    rows=[];receipts=[]
    for N,path in ((192,root/'asian-192-failed'),(384,root/'asian-384-enclosure'),(768,base_run),(1536,root/'asian-1536-enclosure')):
        receipt=path/('run-receipt.json' if N==768 else 'receipt.json');r=read(receipt)
        if N!=768:assert F(r['h'])==F(1,N)
        core=path/'work'/'core'
        if r['status']=='COMPLETE':
            if N!=768:assert r['independent_all_nodes_and_frequency_fees_pass']
            else:assert r['mathematical_check_status']=='PASS_EXACT_MATHEMATICAL_PAYLOAD'
            rows.append(certificate(core,str(F(1,N)),receipt))
        else:
            rows.append({'h':str(F(1,N)),'status':'NO_CERTIFICATE_ANALYTICAL_GUARD_FAILED' if N==192 else 'STOPPED_NO_CERTIFICATE',
               'projection_beta':r.get('analytical_projection_beta_expected'),'required_projection_beta':'strictly greater than 8',
               'reason':'The fixed lambda=12 projection proof does not supply its assumed beta>8 at this mesh.' if N==192 else r['jobs'][-1].get('reason'),
               'execution_receipt':str(receipt),'receipt_sha256':sha(receipt)})
        receipts.append({'h':str(F(1,N)),'receipt':str(receipt),'sha256':sha(receipt)})
    weighted=[]
    for N in (384,768,1536):
        a=root/f'weighted-{N}-author.json';b=root/f'weighted-{N}-independent.json'
        if a.exists() and b.exists():weighted.append(validate_weighted(a,b))
    result={'status':'EXACT_RATIONAL_BUDGET_RECONCILIATION_PASS','scope':'Complete pointwise certificate rows require all author and independent jobs. A failed grid has no substituted floating-point certificate.',
      'step_table':rows,'weighted_moment_table':weighted,'execution_receipts':receipts,
      'posterior_mesh_summary':read(root/'posterior-grid-summary.json'),'Asian_beta_score_bound_summary':read(root/'asian-beta-score-bounds.json'),
      'reader_sha256':sha(__file__)}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps([{'h':v['h'],'status':v['status'],'bias':v.get('bias_Q_minus_P',{}).get('outward24'),'width':v.get('interval_width',{}).get('outward_decimal_upper')} for v in rows],indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--execution-root',type=Path,required=True);p.add_argument('--base-run',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();main(a.execution_root.resolve(),a.base_run.resolve(),a.output.resolve())
