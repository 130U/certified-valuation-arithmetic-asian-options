"""Inventory the current publication files, preserving original evidence hashes."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--git', default=shutil.which('git'))
a=ap.parse_args()
assert a.git, 'Put Git on PATH or pass --git.'
names=subprocess.check_output([a.git,'ls-files','-z','--cached','--others','--exclude-standard'],cwd=ROOT).decode('utf8').split('\0')
files={}
for name in sorted(set(names)):
    p=ROOT/name
    if name=='REVISION-MANIFEST.json' or not p.is_file():continue
    assert p.resolve().is_relative_to(ROOT.resolve()), name
    files[name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
archives={name:files[name] for name in ['code/revision/results/evidence.zip','code/revision/round2/results/evidence-point-v004.zip']}
assert archives['code/revision/results/evidence.zip']['sha256']=='d6af35332a1d3a91d0d575b815926e92c98bc8e84c740af4b80346dfe02bbb8a'
assert archives['code/revision/round2/results/evidence-point-v004.zip']['sha256']=='338964eadb54b51fc1b0ff027df61da870cb2f4ae304421e7f1788bd47310db3'
record={
    'publication_tag':'paper',
    'scope':'All tracked and publishable new files in this checkout, excluding this manifest itself. Ignored local runs and build caches are excluded.',
    'baseline_commit':'5bc72cf6036fdd73fea9c8bc6c85f85fd474b79a',
    'historical_data_commits':['cf0d242f1590c7ca07ab8ca7afb57da5a583032b','1959f8f078e1fedd590000d6166cb20429ff31db'],
    'package_manifest':'code/MANIFEST.json',
    'package_manifest_sha256':hashlib.sha256((ROOT/'code/MANIFEST.json').read_bytes()).hexdigest(),
    'numerical_baseline':'code/verification/numerical-baseline.json',
    'original_package_manifest_sha256':'33eaee125bc49f5755ec74ab24fa9bf655afaab5f884decf1576687eacdbf0c2',
    'evidence_archives':archives,
    'files':files,
}
(ROOT/'REVISION-MANIFEST.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf8',newline='\n')
print(json.dumps({'status':'PASS_PUBLICATION_INVENTORY','files':len(files),'preserved_evidence_archives':2}))
