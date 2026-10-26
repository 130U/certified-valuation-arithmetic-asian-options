"""Inventory the paper, numerical sources and evidence in this publication."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys

if sys.flags.optimize:
    raise RuntimeError('Run inventory creation without -O or PYTHONOPTIMIZE; assertions are required.')

ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--git',default=shutil.which('git'))
    a=ap.parse_args()
    assert a.git,'Put Git on PATH or pass --git.'
    names=subprocess.check_output([a.git,'ls-files','-z','--cached','--others','--exclude-standard'],cwd=ROOT).decode('utf8').split('\0')
    files={}
    for name in sorted(set(names)):
        p=ROOT/name
        if name=='PUBLICATION-MANIFEST.json' or not p.is_file():continue
        assert p.resolve().is_relative_to(ROOT.resolve()),name
        files[name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    record={'publication_year':2026,'publication_tag':'paper',
        'scope':'All publication files, excluding this manifest itself and ignored local outputs.',
        'package_manifest':'code/MANIFEST.json','evidence_archive':'code/evidence/executions.zip',
        'files':files}
    (ROOT/'PUBLICATION-MANIFEST.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({'status':'PASS_PUBLICATION_INVENTORY','files':len(files)}))
if __name__=='__main__':main()
