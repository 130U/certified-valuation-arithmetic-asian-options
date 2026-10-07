"""Read commands from the exported PDF and check the real CLI parser.

This verifies the copyable text, not a fresh kernel calculation. An optional
--run-directory also rechecks an actual completed original-kernel execution.
The unchanged code/run.py is imported and its computation call is intercepted
only for the parser test. No PDF token is corrected or normalized.
"""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json,re,shlex,sys
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
PREFIX='./.venv/Scripts/python.exe'

def actual_parser_namespace(path,tokens):
    """Execute the source's parser prefix, stopping before numerical dispatch."""
    tree=ast.parse(path.read_text(encoding='utf8'))
    entries=[node for node in tree.body if isinstance(node,ast.If) and '__name__' in ast.unparse(node.test)]
    assert len(entries)==1,'Unique CLI entry absent: '+str(path)
    entry=entries[0];body=entry.body
    namespace={'argparse':argparse,'Path':Path,'sys':sys,'__doc__':ast.get_docstring(tree),'__file__':str(path)}
    # Newer runners dispatch to main(); the coupler declares argparse directly
    # under the module entry guard. Follow the actual entry's main call only.
    calls_main=any(isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='main'
        for statement in entry.body for node in ast.walk(statement))
    if calls_main:
        functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='main']
        assert len(functions)==1,'Unique main() declaration absent: '+str(path)
        function=functions[0];body=function.body
        args=function.args.posonlyargs+function.args.args
        assert len(args)==len(function.args.defaults),'Required main() parameters are unsupported: '+str(path)
        for argument,default in zip(args,function.args.defaults):namespace[argument.arg]=ast.literal_eval(default)
        for argument,default in zip(function.args.kwonlyargs,function.args.kw_defaults):
            assert default is not None,'Required main() keyword parameter is unsupported: '+str(path)
            namespace[argument.arg]=ast.literal_eval(default)
    declarations=[];parsed_name=None
    for node in body:
        declarations.append(node)
        if isinstance(node,ast.Assign) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and node.value.func.attr=='parse_args':
            assert len(node.targets)==1 and isinstance(node.targets[0],ast.Name),'Unsupported parse_args assignment: '+str(path)
            parsed_name=node.targets[0].id;break
        if isinstance(node,ast.AnnAssign) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and node.value.func.attr=='parse_args':
            assert isinstance(node.target,ast.Name),'Unsupported parse_args assignment: '+str(path)
            parsed_name=node.target.id;break
    assert parsed_name is not None,'CLI parse_args entry absent: '+str(path)
    module=ast.Module(body=declarations,type_ignores=[])
    previous=sys.argv[:]
    try:
        sys.argv=tokens[1:]
        exec(compile(module,str(path),'exec'),namespace)
    finally:sys.argv=previous
    assert isinstance(namespace[parsed_name],argparse.Namespace),'CLI did not return an argparse Namespace'
    namespace['_parsed_args_name']=parsed_name
    return namespace

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pdf',type=Path,required=True)
    ap.add_argument('--run-directory',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    pages=[p.extract_text() or '' for p in PdfReader(args.pdf).pages]
    appendix='\n'.join(pages)
    expected=[PREFIX+' code/run.py verify',
              PREFIX+' code/run.py run --module asian --independent',
              PREFIX+' code/run.py check --run code/runs/run-ID']
    copied=[]
    for command in expected:
        assert command in appendix,'The exact command is absent or damaged in the exported PDF: '+command
        copied.append(next(line.strip() for line in appendix.splitlines() if line.strip()==command))
    assert not re.search(r'(?<!-)\-(?:module|independent|run)\b',appendix),'A single-hyphen CLI parameter remains'
    assert 'cf0d242f1590c7ca07ab8ca7afb57da5a583032b' in appendix
    assert '1959f8f078e1fedd590000d6166cb20429ff31db' in appendix
    extra=[PREFIX+' code/revision/round2/asian_parameter_point.py prepare --directory new-point',
           PREFIX+' code/revision/round2/asian_parameter_point.py run --directory new-point',
           PREFIX+' code/revision/round2_coupling_example.py --output coupling.json']
    additional=[]
    for command in extra:
        assert command in appendix,'New computation command damaged in PDF: '+command
        copied_line=next(line.strip() for line in appendix.splitlines() if line.strip()==command)
        tokens=shlex.split(copied_line);path=ROOT/tokens[1]
        # Execute the actual source's CLI declaration through parse_args only.
        # The source, numerical imports and calculation functions are not copied
        # into a test implementation or invoked by this parser-only check.
        namespace=actual_parser_namespace(path,tokens)
        additional.append({'command':copied_line,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'arguments':vars(namespace[namespace['_parsed_args_name']])})
    # Bibliographic typography is rendered from semantic inline nodes.
    refs=appendix[appendix.rfind('References'):]
    assert not re.search(r'\*(?:Management Science|Journal|The Review|Mathematics|SIAM|IEEE)',refs)
    spec=importlib.util.spec_from_file_location('pdf_original_runner',ROOT/'code/run.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    rawhash=hashlib.sha256((ROOT/'code/run.py').read_bytes()).hexdigest()
    original_run=runner.run;original_check=runner.check_run
    seen={}
    def parsed_run(modules,independent):
        seen['modules']=modules;seen['independent']=independent;return 0
    def parsed_check(directory):
        seen['run_placeholder']=directory;return {'status':'PARSED_CHECK_COMMAND'}
    runner.run=parsed_run;runner.check_run=parsed_check
    oldargv=sys.argv[:]
    try:
        for command in copied:
            tokens=shlex.split(command)
            assert tokens[:2]==[PREFIX,'code/run.py']
            sys.argv=tokens[1:]
            runner.main()
    finally:
        sys.argv=oldargv;runner.run=original_run;runner.check_run=original_check
    assert seen=={'modules':['asian'],'independent':True,'run_placeholder':'code/runs/run-ID'}
    assert hashlib.sha256((ROOT/'code/run.py').read_bytes()).hexdigest()==rawhash
    actual=None
    if args.run_directory:
        actual=runner.check_run(args.run_directory)
        assert actual['status']=='PASS_EXACT_MATHEMATICAL_PAYLOAD'
    receipt={'status':'PASS_EXPORTED_PDF_COMMANDS_AND_REAL_ARGUMENT_PARSER',
             'pdf_sha256':hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
             'copied_commands':copied,'parsed_arguments':seen,'original_runner_sha256':rawhash,
             'additional_actual_source_parser_checks':additional,
             'placeholder_rule':'Replace run-ID with the directory printed by a real completed run.',
             'completed_run_recheck_status':actual['status'] if actual else None,
             'completed_run_jobs':len(actual['jobs']) if actual else None,
             'scope':'Exact PDF text and real argparse acceptance; completed-result recheck is separate from fresh execution.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,indent=2,default=str)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(receipt,default=str))

if __name__=='__main__':main()
