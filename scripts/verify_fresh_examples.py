"""Compare fresh Windows targeted examples with every frozen mathematical field.

Source identity and mathematical guards are checked by the actual workers and
the revision manifest. This comparison ignores only declared execution metadata.
"""
from pathlib import Path
import argparse,json

ROOT=Path(__file__).resolve().parents[1]
METADATA={'worker_seconds','elapsed_seconds','seconds','outer_seconds',
          'envelope_worker_seconds','full_linear_time_estimate',
          'recorded_five_job_seconds','core_path','execution_receipt','python_version'}

def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def payload(x):
    if isinstance(x,dict):
        return {k:payload(v) for k,v in x.items() if not k.endswith('sha256') and k not in METADATA}
    if isinstance(x,list):return [payload(v) for v in x]
    return x

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--point',type=Path,required=True)
    ap.add_argument('--coupling',type=Path,required=True)
    a=ap.parse_args();reference=ROOT/'code/revision/round2/results'
    for actual,name in [(a.point,'point-v004-result.json'),(a.coupling,'coupling-v004-result.json')]:
        assert payload(read(actual))==payload(read(reference/name)),name+' mathematical payload differs'
    print(json.dumps({'status':'PASS_FRESH_TARGETED_EXAMPLES_EXACT_MATHEMATICAL_PAYLOAD',
        'fields':'Every field and array except hashes and the explicitly listed execution metadata.',
        'metadata_exclusions':sorted(METADATA),'comparison':'Exact equality; no tolerances or midpoint substitutions.'}))

if __name__=='__main__':main()
