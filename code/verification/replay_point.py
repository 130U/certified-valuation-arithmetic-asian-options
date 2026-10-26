"""Read back the saved v0=1/25 certificate from the verified execution archive.

The current capsule reader recomputes exact rational arithmetic. Source hashes
identify the actual saved execution, independently of the current reader.
"""
from pathlib import Path
import argparse, importlib.util, json, os, sys, tempfile

CODE=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj

def main(directory,output,verified_inventory=None):
    if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):
        raise RuntimeError('Optimized Python is prohibited; assertions enforce the certificate checks.')
    ev=module('evidence_helpers',CODE/'verification'/'read_evidence.py')
    inv=verified_inventory if verified_inventory is not None else ev.verify_inventory(directory,ev.read(CODE/'evidence'/'receipt.json'))
    run=directory/'execution'/'asian-v004';r=ev.read(run/'receipt.json');cap=ev.read(run/'result-capsule.json')
    checks=ev.verify_asian(run,768)
    assert cap['receipt_sha256']==ev.sha(run/'receipt.json')
    assert cap['preflight_sha256']==ev.sha(run/'preflight.json')==r['preflight_sha256']
    generator_hash=cap['capsule_generator_sha256'];assert generator_hash==r['generator_sha256']
    assert ev.sha(directory/inv['source_objects'][generator_hash])==generator_hash
    assert ev.without_locations(cap)==ev.without_locations(ev.read(CODE/'results'/'point-v004-result.json'))
    saved_audit=ev.read(directory/'checks'/'parameter-point.json')
    audit_path=directory/inv['source_objects'][saved_audit['review_script_sha256']]
    with tempfile.TemporaryDirectory(prefix='parameter-readback-',dir=directory) as temporary:
        scratch=Path(temporary).resolve();assert scratch.is_relative_to(directory.resolve())
        audit=module('executed_parameter_audit',audit_path)
        audit.CODE=CODE;audit.RUN=run;audit.OUT=scratch/'parameter-audit-readback.json';audit.main()
        assert saved_audit==ev.read(audit.OUT)
        # The archived execution identity is checked above. The active reader has
        # its own hash; comparing its arithmetic does not assign it to the old run.
        generator=module('current_parameter_capsule_reader',CODE/'experiments'/'asian_parameter_point.py')
        rebuilt=scratch/'parameter-capsule-readback.json'
        generator.capsule(run,rebuilt)
        current=ev.read(rebuilt)
        assert current['capsule_generator_sha256']==ev.sha(generator.__file__)
        current.pop('capsule_generator_sha256');expected=dict(cap);expected.pop('capsule_generator_sha256')
        assert ev.without_locations(current)==ev.without_locations(expected)
    result={'status':'PASS_PARAMETER_POINT_EXACT_READBACK',
      'scope':'Saved execution identities and exact arithmetic, without pricing-kernel reruns.',
      **checks,'independent_math_and_literal_source_replay':'PASS',
      'capsule_all_numerical_and_scope_fields_equal':True,'exact_six_component_width_reconciliation':'PASS',
      'executed_generator_sha256':generator_hash,'current_capsule_reader_sha256':ev.sha(generator.__file__),
      'bias_outward24':cap['principal_bias_Q_minus_P']['outward24'],
      'width_outward24_upper':cap['six_component_exact_width_ledger']['interval_width']['outward_decimal_upper'],
      'replay_script_sha256':ev.sha(__file__)}
    ev.write(output,result);print(json.dumps(result,indent=2));return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,required=True,help='Directory produced by read_evidence.py.')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();main(args.directory.resolve(),args.output.resolve())
