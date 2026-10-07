"""Freeze all executed sources, outputs, contracts and logs for ledger replay."""
from pathlib import Path
import argparse,hashlib,json,zipfile
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main(numerical,base_run,out):
    assert numerical.is_dir() and base_run.is_dir() and not out.exists()
    base=json.loads((base_run/'run-receipt.json').read_text(encoding='utf8'))
    assert base['status']=='COMPLETE'
    for name in ('asian-384-enclosure','asian-1536-enclosure','posterior-8192','posterior-16384'):
        rec=json.loads((numerical/name/'receipt.json').read_text(encoding='utf8'));assert rec['status']=='COMPLETE'
    for N in (384,768,1536):
        for mode in ('author','independent'):
            assert (numerical/f'weighted-{N}-{mode}.json').is_file()
    files=[]
    for prefix,root in (('execution',numerical),('execution/base-run',base_run)):
        for p in sorted(root.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
                files.append((p,prefix+'/'+p.relative_to(root).as_posix()))
    assert len({name for p,name in files})==len(files)
    inventory={'schema_version':1,'contents':'Completed and stopped execution archives; exact executed sources, results, resources, logs and metadata retained.',
       'files':{name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p,name in files},'packer_sha256':sha(__file__)}
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p,name in files:z.write(p,name)
        z.writestr('EVIDENCE-INVENTORY.json',json.dumps(inventory,indent=2)+'\n')
    receipt={'status':'FROZEN_COMPLETE_EXECUTION_ARCHIVE','archive_name':out.name,'sha256':sha(out),'bytes':out.stat().st_size,
      'files':len(files),'uncompressed_bytes':sum(p.stat().st_size for p,name in files),'packer_sha256':sha(__file__),
      'readback':'Extract to a fresh directory; verify every EVIDENCE-INVENTORY file hash, run baseline check against execution/base-run, and run read_budget.py with execution as execution-root.'}
    out.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--numerical-root',type=Path,required=True);p.add_argument('--base-run',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();main(a.numerical_root.resolve(),a.base_run.resolve(),a.output.resolve())
