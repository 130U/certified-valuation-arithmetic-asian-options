"""Check completed-run integrity and historical-manifest compatibility offline."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

CODE = Path(__file__).resolve().parents[1]
LEGACY = '33eaee125bc49f5755ec74ab24fa9bf655afaab5f884decf1576687eacdbf0c2'
ARCHIVE_SHA256 = 'd6af35332a1d3a91d0d575b815926e92c98bc8e84c740af4b80346dfe02bbb8a'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2)+'\n', encoding='utf8')


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def load_runner():
    spec = importlib.util.spec_from_file_location('publication_integrity_runner', CODE/'run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_fixture(destination):
    archive = CODE/'revision/results/evidence.zip'
    require(hashlib.sha256(archive.read_bytes()).hexdigest() == ARCHIVE_SHA256,
            'Frozen execution archive identity changed')
    prefix = 'execution/base-run/'
    count = 0
    with zipfile.ZipFile(archive) as bundle:
        for info in bundle.infolist():
            if not info.filename.startswith(prefix) or info.is_dir():
                continue
            relative = info.filename[len(prefix):]
            target = (destination/relative).resolve()
            require(target.is_relative_to(destination.resolve()), 'Unsafe archive path')
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(info) as source, target.open('wb') as output:
                shutil.copyfileobj(source, output)
            count += 1
    require(count > 0 and (destination/'run-receipt.json').is_file(),
            'No completed reference run in the archive')


def change_numeric_leaf(value, runner):
    if isinstance(value, dict):
        for key, item in value.items():
            if key.endswith('sha256') or key in runner.META_KEYS:
                continue
            if isinstance(item, (int, float)) and not isinstance(item, bool):
                value[key] = item + 1
                return True
            if isinstance(item, str) and re.fullmatch(r'-?\d+(?:\.\d+)?', item):
                value[key] = item + '1' if '.' in item else str(int(item)+1)
                return True
            if change_numeric_leaf(item, runner):
                return True
    elif isinstance(value, list):
        for index, item in enumerate(value):
            if isinstance(item, (int, float)) and not isinstance(item, bool):
                value[index] = item + 1
                return True
            if change_numeric_leaf(item, runner):
                return True
    return False


def parser_check(runner):
    original_argv = sys.argv
    original_run = runner.run
    captured = {}
    def capture(modules, independent):
        captured.update(modules=modules, independent=independent)
        return 0
    try:
        runner.run = capture
        sys.argv = ['code/run.py', 'run', '--module', 'asian', '--independent']
        require(runner.main() == 0 and captured == {'modules': ['asian'], 'independent': True},
                'Current argument parser rejected the published run command')
    finally:
        runner.run = original_run
        sys.argv = original_argv


def main(reference=None):
    runner = load_runner()
    package = runner.verify()
    parser_check(runner)
    config = read(CODE/'configuration.json')
    runs = CODE/'runs'
    runs.mkdir(exist_ok=True)
    rows = []
    with tempfile.TemporaryDirectory(prefix='integrity-', dir=runs) as temporary:
        working = Path(temporary).resolve()
        require(working.is_relative_to(runs.resolve()), 'Test workspace must stay within code/runs')
        fixture = working/'fixture'
        if reference is None:
            fixture.mkdir()
            extract_fixture(fixture)
        else:
            source = Path(reference).resolve()
            require(source.is_dir() and not source.is_relative_to(working), 'Invalid reference run directory')
            shutil.copytree(source, fixture)
        original = read(fixture/'run-receipt.json')
        require(original['status'] == 'COMPLETE' and original['jobs'], 'Reference run must be complete')
        expected = runner.expected_jobs(config, original['modules'], original['independent_checks'])
        require({job['id'] for job in original['jobs']} == set(expected), 'Reference run job set is incomplete')

        def case(name, mutate=None, success=False, allow_running=False):
            folder = working/name
            shutil.copytree(fixture, folder)
            output = folder/'mathematical-check.json'
            if output.exists():
                output.unlink()
            rec = read(folder/'run-receipt.json')
            if mutate is not None:
                mutate(folder, rec)
            write(folder/'run-receipt.json', rec)
            if allow_running:
                try:
                    result = runner.check_run(folder, allow_running=True)
                    accepted = result['status'] == 'PASS_EXACT_MATHEMATICAL_PAYLOAD'
                except Exception:
                    accepted = False
                returncode = 0 if accepted else 1
            else:
                result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(CODE/'run.py'),
                                         'check', '--run', str(folder)],
                                        capture_output=True, text=True, timeout=45)
                returncode = result.returncode
                accepted = returncode == 0
                if not success:
                    require('"status": "STOPPED"' in result.stdout, name+': missing STOPPED record')
            require(accepted == success, name+': unexpected acceptance or rejection')
            require(output.is_file() == success, name+': incorrect mathematical-check output')
            rows.append({'case': name, 'expected': 'accept' if success else 'reject',
                         'returncode': returncode, 'mathematical_check_written': output.is_file()})

        def set_value(key, value):
            return lambda folder, rec: rec.update({key: value})

        case('current-manifest', set_value('manifest_sha256', package['manifest_sha256']), success=True)
        case('historical-manifest', set_value('manifest_sha256', LEGACY), success=True)
        case('internal-running', set_value('status', 'RUNNING'), success=True, allow_running=True)
        case('unknown-manifest', set_value('manifest_sha256', '0'*64))
        case('empty-jobs', set_value('jobs', []))
        case('missing-job', lambda folder, rec: rec['jobs'].pop())
        case('duplicate-job', lambda folder, rec: rec['jobs'].append(dict(rec['jobs'][0])))
        case('extra-job', lambda folder, rec: rec['jobs'].append({'id': 'undeclared-job', 'status': 'COMPLETE'}))
        case('stopped-receipt', set_value('status', 'STOPPED'))
        case('external-running', set_value('status', 'RUNNING'))
        case('stopped-job', lambda folder, rec: rec['jobs'][0].update(status='STOPPED'))
        case('source-hash-mismatch', lambda folder, rec: rec['jobs'][0].update(source_sha256='0'*64))

        def missing_result(folder, rec):
            key = rec['jobs'][0]['id']
            (folder/'work/core'/config['jobs'][key][3]).unlink()
        case('missing-result', missing_result)

        def changed_source(folder, rec):
            key = rec['jobs'][0]['id']
            path = folder/'work/core'/config['jobs'][key][0]
            path.write_bytes(path.read_bytes()+b'\n# Integrity-test mutation.\n')
        case('source-byte-mismatch', changed_source)

        def changed_result(folder, rec):
            key = rec['jobs'][0]['id']
            path = folder/'work/core'/config['jobs'][key][3]
            value = read(path)
            require(change_numeric_leaf(value, runner), 'No numeric field available for rejection test')
            write(path, value)
        case('mathematical-payload-mismatch', changed_result)

    result = {'status': 'PASS_RUN_INTEGRITY_AND_HISTORICAL_COMPATIBILITY',
              'cases': rows, 'current_argument_parser': 'PASS',
              'frozen_archive_modified': False, 'numerical_kernels_executed': False}
    print(json.dumps(result, ensure_ascii=True))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path,
                        help='Optional completed run to copy into isolated integrity-test directories.')
    arguments = parser.parse_args()
    main(arguments.reference)
