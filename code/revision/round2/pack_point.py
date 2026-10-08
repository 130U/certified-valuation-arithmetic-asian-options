"""Freeze the completed new point without touching the first-round archive."""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile

ROOT=Path(__file__).resolve().parents[3]
ROUND=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf8')

def main(run):
    receipt=read(run/'receipt.json');assert receipt['status']=='COMPLETE' and len(receipt['jobs'])==5
    results=ROUND/'results';results.mkdir(exist_ok=True)
    for src,name in [('result-capsule.json','point-v004-result.json'),('receipt.json','point-v004-receipt.json'),('preflight.json','point-v004-preflight.json')]:
        target=results/name;assert not target.exists();shutil.copyfile(run/src,target)
    theory=ROOT.parent/'round2-theory'
    audit=read(theory/'new-point-independent-receipt.json')
    assert audit['status']=='ANALYTICAL_SOURCE_AND_COMPLETED_RESULT_READBACK_PASS'
    assert audit['completed_receipt_sha256']==sha(run/'receipt.json')
    files={}
    for p in sorted(run.rglob('*')):
        if p.is_file():files['repository/code/revision/round2/runs/point-v004/'+p.relative_to(run).as_posix()]=p
    for name in ('asian_parameter_point.py','replay_point.py','pack_point.py','README.md'):
        p=ROUND/name;files['repository/code/revision/round2/'+name]=p
    for name in ('point-v004-result.json','point-v004-receipt.json','point-v004-preflight.json'):
        files['repository/code/revision/round2/results/'+name]=results/name
    for name in ('read_budget.py',):files['repository/code/revision/'+name]=ROOT/'code'/'revision'/name
    for name in ('asian-remainder-certificate.py','asian-linear-certificate.py','check-asian-remainder.py','check-asian-linear.py','resource_limits.py'):
        files['repository/code/core/'+name]=ROOT/'code'/'core'/name
    for name in ('WORKING_GUIDE.md','SCOPE.md','ENVIRONMENT.md','configuration.json','MANIFEST.json'):
        files['repository/code/'+name]=ROOT/'code'/name
    for name in ('audit-new-point.py','new-point-independent-receipt.json','new-point-review.md'):
        files['round2-theory/'+name]=theory/name
        copy=results/name;assert not copy.exists();shutil.copyfile(theory/name,copy)
    inventory={'scope':'Complete second stochastic-Heston point: actual sources, original-source evidence, all five results and traces, preflight and independent source/math audit.',
        'files':{name:{'bytes':p.stat().st_size,'sha256':sha(p)} for name,p in sorted(files.items())}}
    invbytes=(json.dumps(inventory,indent=2)+'\n').encode('utf8')
    archive=results/'evidence-point-v004.zip';assert not archive.exists()
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,p in sorted(files.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,10,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes())
        info=zipfile.ZipInfo('inventory.json',date_time=(2026,10,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,invbytes)
    result={'status':'COMPLETE_SECOND_POINT_EVIDENCE_FROZEN','archive':archive.name,'archive_sha256':sha(archive),
        'archive_bytes':archive.stat().st_size,'inventory_sha256':hashlib.sha256(invbytes).hexdigest(),
        'inventory_file_count':len(files),'capsule_sha256':sha(results/'point-v004-result.json'),
        'execution_receipt_sha256':sha(results/'point-v004-receipt.json'),'independent_audit_receipt_sha256':sha(theory/'new-point-independent-receipt.json'),
        'old_evidence_archive_untouched':True,'pack_script_sha256':sha(__file__)}
    write(results/'archive-receipt.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);a=p.parse_args();main(a.directory.resolve())
