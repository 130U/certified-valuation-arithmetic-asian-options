"""Verify publication identities and exact saved price-unit calculations offline.

Fresh interval-kernel execution is provided by the commands in EVIDENCE.md.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json,subprocess,sys,tempfile,re

if sys.flags.optimize:
    raise RuntimeError('Run verification without -O or PYTHONOPTIMIZE; assertions are required.')

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',type=Path,default=ROOT/'PUBLICATION-MANIFEST.json')
    args=ap.parse_args();m=read(args.manifest)
    assert m['publication_year']==2026 and m['publication_tag']=='paper'
    for name,row in m['files'].items():
        p=ROOT/name
        assert p.resolve().is_relative_to(ROOT.resolve()) and p.is_file(),name
        assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name
    for name,row in read(ROOT/'code/MANIFEST.json')['files'].items():
        p=ROOT/'code'/name
        assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name
    pdf_record=read(ROOT/'paper/build-record-en.json')
    article_record=read(ROOT/'manuscript/content-verification.json')
    pdf=ROOT/pdf_record['pdf']['path']
    assert pdf_record['status']=='PASS' and pdf_record['language']=='en'
    assert pdf.read_bytes().startswith(b'%PDF-')
    assert pdf.stat().st_size==pdf_record['pdf']['bytes'] and sha(pdf)==pdf_record['pdf']['sha256']
    assert pdf_record['article']['sha256']==sha(ROOT/'manuscript/report.md')
    assert pdf_record['formula_sequence_sha256']==article_record['formula_sequence_sha256']
    assert pdf_record['mathematical_counts']=={k:article_record['counts'][k] for k in ('display_math','inline_math','equation_tags','tables','references')}

    ledger=read(ROOT/'code/results/step-grid.json')
    assert ledger['status']=='EXACT_RATIONAL_BUDGET_RECONCILIATION_PASS'
    assert [r['h'] for r in ledger['step_table']]==['1/192','1/384','1/768','1/1536']
    complete=0
    for row in ledger['step_table']:
        if row['status']=='NO_CERTIFICATE_ANALYTICAL_GUARD_FAILED':
            assert row['h']=='1/192' and F(row['projection_beta'])<=8
            continue
        assert row['status']=='COMPLETE_INDEPENDENTLY_CHECKED_ENCLOSURE'
        lo,hi=map(F,row['bias_Q_minus_P']['exact_interval'])
        assert lo<=hi and hi-lo==F(row['interval_width']['exact_rational'])
        assert sum(F(x['exact_rational']) for x in row['components'].values())==hi-lo
        complete+=1
    assert complete==3
    grids=ledger['posterior_mesh_summary']['table'];assert len(grids)==6
    for quotes in (1,9):
        rows=[r for r in grids if r['quotes']==quotes]
        assert [r['cells'] for r in rows]==[4096,8192,16384]
        assert F(rows[2]['price_bound_upper_exact'])<F(rows[1]['price_bound_upper_exact'])<F(rows[0]['price_bound_upper_exact'])
    for run in ledger['Asian_beta_score_bound_summary']['runs']:
        assert len(run['rows'])==4
        for row in run['rows']:
            lo,hi=map(F,row['beta_Asian_signed_enclosure']['exact_interval'])
            assert lo<=0<=hi and hi==F(row['absolute_score_bound']['exact_interval'][1]) and lo==-hi
    for name in ('path-diagnostics.json','asian-beta-diagnostic.json'):
        assert 'DIAGNOSTIC' in read(ROOT/'code/results'/name)['status']

    point=read(ROOT/'code/results/point-v004-result.json')
    assert point['status']=='COMPLETE_NEW_STOCHASTIC_HESTON_POINT_CERTIFICATE'
    assert point['input']['theta']==['3','9/200','23/100','-11/20','1/25']
    row=point['six_component_exact_width_ledger'];lo,hi=map(F,point['principal_bias_Q_minus_P']['exact_interval'])
    assert lo<=hi and hi-lo==F(row['interval_width']['exact_rational'])
    assert len(row['components'])==6 and sum(F(x['exact_rational']) for x in row['components'].values())==hi-lo
    assert row['passes_original_0025_absolute_target']
    coupled=read(ROOT/'code/results/coupling-v004-result.json')
    assert coupled['status']=='CLOSED_LOGNORMAL_COUPLING_REMAINDER_ENCLOSURE_COMPLETE'
    assert coupled['scope']['xi']=='0' and coupled['scope']['v0']=='1/25'
    assert coupled['source_sha256']==sha(ROOT/'code/experiments/coupling_example.py')
    assert [r['precision_bits'] for r in coupled['precision_runs']]==[384,512]
    for run in coupled['precision_runs']:
        results=run['results'];dl,du=map(F,results['direct_nonlinear_width']['exact_interval']);sl,su=map(F,results['separate_law_nonlinear_width']['exact_interval'])
        assert 0<=dl<=du<sl<=su
        assert F(results['width_ratio_direct_over_separate']['exact_interval'][1])<F('0.005731')
        assert results['strict_improvement_proved_by_disjoint_width_bounds'] and run['closed_pair_moment_identity_checks']==459

    runs=ROOT/'code/runs';runs.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='evidence-',dir=runs) as directory:
        work=Path(directory)
        assert work.resolve().is_relative_to(runs.resolve())
        out=work/'check.json'
        proc=subprocess.run([sys.executable,str(ROOT/'code/verification/read_evidence.py'),'--directory',str(work/'data'),'--output',str(out)],capture_output=True,text=True)
        if proc.returncode:raise RuntimeError(proc.stdout+'\n'+proc.stderr)
        evidence=read(out)
        assert 'PASS' in evidence['status']

    links=0
    for name in m['files']:
        if not name.endswith('.md'):continue
        p=ROOT/name;text=p.read_text(encoding='utf8')
        assert not re.search(r'\brevision\b|round[ -]?2|26 October 2026|2026-10-26|Research timeline',text,re.I),name
        for href in re.findall(r'\]\(([^)]+)\)',text):
            if href.startswith(('http:','https:','mailto:','#')):continue
            target=href.split('#')[0]
            assert (p.parent/target).exists(),name+': '+href
            links+=1
    print(json.dumps({'status':'PASS_PUBLICATION_AND_EXACT_LEDGER','publication_files':len(m['files']),'complete_step_certificates':complete,'analytical_guard_cases':1,'posterior_grid_rows':len(grids),'deterministic_coupling_precisions':2,'relative_links_checked':links,'evidence':evidence,'pdf_article_identity':'PASS'}))
if __name__=='__main__':main()
