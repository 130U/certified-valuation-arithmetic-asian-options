"""Verify both public PDFs against their frozen inputs and fresh build logs.

Run after scripts/build_report.py and scripts/pdf/build_pdf.py --language en/zh.
The check reads PDFs and logs; it does not certify native LaTeX compilation or
replace the separately recorded visual review.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import importlib.metadata
import json
import platform
import re
import shutil
import subprocess
import sys

from pypdf import PdfReader
from pypdf.generic import ContentStream

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'en': ('paper/paper.pdf', 'manuscript/report-source.tex'),
    'zh': ('paper/paper-zh.pdf', 'manuscript/report-source-zh.tex'),
}
FK_URL = 'https://openaccess.city.ac.uk/id/eprint/13241/1/AsianBound_FK.pdf'
REQUIRED_INPUTS = {
    'scripts/build_report.py', 'scripts/pdf/build_pdf.py',
    'scripts/pdf/vector_math.py', 'scripts/pdf/render_math.cjs',
    'scripts/pdf/cjk_line_break.py',
    'scripts/pdf/extract_math_inputs.py', 'scripts/pdf/requirements.txt',
    'scripts/pdf/vendor/mathjax-full-3.2.2.tgz',
    'manuscript/report-source.tex', 'manuscript/report-source-zh.tex',
    'manuscript/report.json', 'manuscript/report.tex',
    'manuscript/translation-verification.json',
    *('assets/fonts/' + name for name in (
        'cmr10.ttf', 'cmb10.ttf', 'cmti10.ttf', 'cmtt10.ttf',
        'DejaVuSerif.ttf', 'NotoSerifSC-Regular.ttf', 'NotoSerifSC-Bold.ttf')),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_path(value):
    require(isinstance(value, str), 'Record path must be a string')
    path = Path(value)
    require(not path.is_absolute() and not re.match(r'^[A-Za-z]:', value) and
            '\\' not in value and '..' not in path.parts,
            'Record path is not a portable repository path: ' + value)
    resolved = (ROOT / path).resolve()
    require(resolved.is_relative_to(ROOT), 'Record path leaves the repository: ' + value)
    return resolved


def verify_file(row):
    path = public_path(row['path'])
    require(path.is_file(), 'Recorded file is missing: ' + row['path'])
    require(isinstance(row['bytes'], int) and path.stat().st_size == row['bytes'],
            'Recorded byte count differs: ' + row['path'])
    require(sha256(path) == row['sha256'], 'Recorded SHA-256 differs: ' + row['path'])
    return path


def check_dependencies(record, node):
    dependencies = record['dependencies']
    require(dependencies.get('python') == '3.12', 'The recorded Python series must be 3.12')
    require(sys.version_info[:2] == (3, 12), 'Build verification requires Python 3.12')
    require(str(dependencies.get('node')) == '24', 'The recorded Node.js major must be 24')
    require(node, 'Supply --node or put Node.js 24 on PATH')
    node_version = subprocess.run([str(node), '--version'], check=True, capture_output=True,
                                  text=True, timeout=15).stdout.strip()
    require(re.fullmatch(r'v24\.\d+\.\d+', node_version), 'Build verification requires Node.js 24')
    requirements = {}
    for line in (ROOT / 'scripts/pdf/requirements.txt').read_text(encoding='utf8').splitlines():
        if line.strip() and not line.lstrip().startswith('#'):
            name, version = line.strip().split('==')
            requirements[name.lower()] = version
    actual = {}
    recorded = {key.lower(): str(value) for key, value in dependencies.items()}
    for name, version in requirements.items():
        require(recorded.get(name) == version, 'Dependency record differs from the lock: ' + name)
        actual[name] = importlib.metadata.version(name)
        require(actual[name] == version, 'Installed dependency differs from the lock: ' + name)
    return {'python': platform.python_version(), 'node': node_version, **actual}


def vector_and_search_layer(reader, formulas, table_header_tex):
    stats = {'forms': 0, 'image_xobjects': 0, 'vector_path_operations': 0,
             'invisible_text_show_operations': 0, 'hidden_tex_text_show_operations': 0}
    seen = set()
    hidden = Counter()

    def visit(stream, resources):
        mode = 0
        for arguments, operation in ContentStream(stream, reader).operations:
            if operation == b'Tr':
                mode = int(arguments[0])
            if operation in (b'm', b'l', b'c', b'f', b'f*'):
                stats['vector_path_operations'] += 1
            if operation in (b'Tj', b'TJ') and mode == 3:
                stats['invisible_text_show_operations'] += 1
                require(operation == b'Tj', 'Unexpected formula search-layer encoding')
                hidden[re.sub(r'\s+', ' ', str(arguments[0])).strip()] += 1
                if '\\' in str(arguments):
                    stats['hidden_tex_text_show_operations'] += 1
            if operation == b'Do':
                value = resources['/XObject'][arguments[0]]
                obj = value.get_object()
                reference = getattr(obj, 'indirect_reference', None)
                key = (reference.idnum, reference.generation) if reference else id(obj)
                if key in seen:
                    continue
                seen.add(key)
                if obj.get('/Subtype') == '/Image':
                    stats['image_xobjects'] += 1
                elif obj.get('/Subtype') == '/Form':
                    stats['forms'] += 1
                    visit(obj, obj.get('/Resources', resources))

    for page in reader.pages:
        visit(page.get_contents(), page.get('/Resources', {}))
    require(stats['forms'] > 0 and stats['vector_path_operations'] > 0,
            'Visible vector mathematics is missing')
    require(stats['image_xobjects'] == 0, 'A raster image replaced vector mathematics')
    # A split table repeats its header, so the Chinese PDF can have additional
    # formula occurrences. Compare each original TeX string and multiplicity;
    # duplicates cannot compensate for an absent or altered source formula.
    expected = Counter(re.sub(r'\s+', ' ', formula).strip() for formula in formulas)
    require(not (expected - hidden), 'A source formula is absent from the TeX search layer')
    extra = hidden - expected
    headers = {re.sub(r'\s+', ' ', formula).strip() for formula in table_header_tex}
    require(set(extra) <= headers, 'An extra search-layer formula is not a repeated table header')
    stats['repeated_table_header_formula_occurrences'] = sum(extra.values())
    require(stats['hidden_tex_text_show_operations'] > 0, 'The TeX search layer is incomplete')
    return stats


def verify_output(row, logs, report):
    language = row['language']
    require(language in EXPECTED, 'Unexpected PDF language')
    pdf_name, source_name = EXPECTED[language]
    require(row['path'] == pdf_name and row['source']['path'] == source_name,
            'PDF/source pair differs from the public entry point')
    pdf = verify_file(row)
    source = public_path(source_name)
    require(sha256(source) == row['source']['sha256'], 'PDF source SHA-256 differs')
    reader = PdfReader(pdf)
    require(len(reader.pages) == row['pages'], 'PDF page count differs: ' + pdf_name)
    log_path = logs / ('pdf-build-' + language + '.json')
    inputs_path = logs / ('math-inputs-' + language + '.json')
    log = json.loads(log_path.read_text(encoding='utf8'))
    math_inputs = json.loads(inputs_path.read_text(encoding='utf8'))
    require(log['source_sha256'] == row['source']['sha256'] and
            log['pdf_sha256'] == row['sha256'] and log['pdf_path'] == pdf_name,
            'Fresh build log is not bound to the recorded PDF/source')
    require(log['math_source_occurrences'] == len(math_inputs) == 694,
            'Expected 694 source formula occurrences')
    tags = sorted({tag for entry in math_inputs for tag in entry['tags']})
    require(log['numbered_equations'] == tags and len(tags) == 95,
            'Expected 95 unchanged equation tags')
    require(len(log['tables']) == 14, 'Expected fourteen tables')
    require(not log['unknown_commands'], 'Unknown TeX commands remain')
    require(log['display_placements'] and
            all(entry['font_pt'] >= 9.5 for entry in log['display_placements']),
            'A display was reduced below the audited size')
    rendering = log['math_render_summary']
    require(rendering['status'] == 'PASS' and not rendering['errors'] and
            rendering['mathjax'] == '3.2.2' and rendering['runtime_network_calls'] == 0,
            'MathJax build failed or was not offline')
    require(rendering['renderer_sha256'] == sha256(ROOT / 'scripts/pdf/render_math.cjs') and
            rendering['input_sha256'] == sha256(inputs_path) and rendering['occurrences'] == 694,
            'MathJax log is not bound to the executed renderer/input')

    # Re-extract the formula input in the builder's source order. Importing the
    # small canonicalizer performs no rendering or subprocess execution.
    sys.path.insert(0, str(ROOT / 'scripts/pdf'))
    from extract_math_inputs import canonical
    text = source.read_text(encoding='utf8')
    abstract = text.split('\\begin{abstract}', 1)[1].split('\\end{abstract}', 1)[0]
    body = text.split('\\end{abstract}', 1)[1].split('\\begin{thebibliography}', 1)[0]
    formulas = []
    searchable_tex = []
    for part in (abstract, body):
        for match in re.finditer(r'\\\[(.*?)\\\]|\\\((.*?)\\\)', part, re.S):
            display = match.group(1) is not None
            tex = match.group(1) if display else match.group(2)
            ident, clean, formula_tags = canonical(tex, display)
            formulas.append({'id': ident, 'tex': tex, 'display': display, 'tags': formula_tags})
            searchable_tex.append(clean)
    require(math_inputs == formulas, 'Fresh formula input differs from the public TeX source')

    pages = [page.extract_text() or '' for page in reader.pages]
    extracted = '\n'.join(pages)
    compact = re.sub(r'\s+', ' ', extracted)
    for email in report['metadata']['emails']:
        require(email in pages[0], 'Author email missing from the first PDF page')
    uris = {str(annotation.get_object().get('/A', {}).get('/URI', ''))
            for page in reader.pages for annotation in page.get('/Annots', [])}
    require(all('mailto:' + email in uris for email in report['metadata']['emails']),
            'Author email annotations are missing')
    require(FK_URL in extracted and FK_URL in uris, 'Accepted Fusai–Kyriakou PDF link is missing')
    reference = extracted[extracted.rfind('[4] Fusai'):]
    require(reference and FK_URL in reference.split('[5] Heston', 1)[0],
            'The accepted manuscript URL is not in reference 4')
    require(not re.search(r'\bA0[12]\b', extracted), 'Internal review labels remain in the PDF')
    require(not re.search(r'Proposition\s+H\.1|\(H\.1\)', extracted),
            'The coupling statement still has the superseded H.1 number')
    require('\\frac' in extracted and '\\sigma' in extracted,
            'The original TeX is not searchable')
    headings = ('Appendix H. Research timeline', 'Appendix I. A direct coupled-remainder inequality') \
        if language == 'en' else ('附录 H. 研究时间线', '附录 I. 直接耦合余项不等式')
    for heading in headings:
        require(heading in compact, 'Appendix H/I heading is missing: ' + heading)
    require('Proposition I.1' in compact if language == 'en' else '命题 I.1' in compact,
            'The coupling proposition is not numbered I.1')
    commands = [line.strip() for block in re.findall(
        r'\\begin\{verbatim\}(.*?)\\end\{verbatim\}', text, re.S)
        for line in block.splitlines() if line.strip()]
    require(commands and all(command in extracted for command in commands),
            'A literal public computation command was altered in the PDF')
    require(not re.search(r'(?<!-)\-(?:module|independent|run|directory|output)\b', extracted),
            'A command flag lost a hyphen')
    def header_formulas(nodes):
        for node in nodes:
            if node['type'] == 'math':
                yield node['tex']
            yield from header_formulas(node.get('inlines', []))

    header_tex = [formula for table in report['blocks'] if table['type'] == 'table'
                  for header in table['rows'][:table['header_rows']] for cell in header
                  for formula in header_formulas(cell['inlines'])]
    stats = vector_and_search_layer(reader, searchable_tex, header_tex)
    return {'language': language, 'path': pdf_name, 'sha256': row['sha256'],
            'bytes': row['bytes'], 'pages': row['pages'], 'source': row['source'],
            'math_occurrences': 694, 'numbered_equations': 95, 'tables': 14,
            'literal_commands': len(commands), 'vector_search_layer': stats,
            'build_log_sha256': sha256(log_path)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, default=ROOT / 'paper/build-record.json')
    parser.add_argument('--logs', type=Path, default=ROOT / '.build/pdf')
    parser.add_argument('--node', default=shutil.which('node'))
    parser.add_argument('--output', type=Path, default=ROOT / '.build/pdf/build-verification.json')
    args = parser.parse_args(argv)
    record_bytes = args.record.read_bytes()
    record = json.loads(record_bytes)
    record_sha256 = hashlib.sha256(record_bytes).hexdigest()
    require(record['status'] == 'PASS' and record['builder'] == 'ReportLab / MathJax',
            'The build record is incomplete')
    require(record['native_latex']['status'] == 'UNVERIFIED',
            'Native LaTeX status must remain explicitly unverified')
    paths = [row['path'] for row in record['inputs']]
    require(len(paths) == len(set(paths)), 'Build inputs contain duplicate paths')
    require(REQUIRED_INPUTS <= set(paths), 'Essential builder/source/font inputs are not frozen')
    require('paper/build-record.json' not in paths, 'The build record cannot hash itself')
    for row in record['inputs']:
        verify_file(row)
    dependencies = check_dependencies(record, args.node)
    outputs = record['outputs']
    require(len(outputs) == 2 and {row['language'] for row in outputs} == {'en', 'zh'},
            'Both public PDF languages must be recorded once')
    report = json.loads((ROOT / 'manuscript/report.json').read_text(encoding='utf8'))
    verified = [verify_output(row, args.logs, report) for row in outputs]
    require(sha256(args.record) == record_sha256, 'Build record changed during verification')
    for row in [*record['inputs'], *outputs]:
        verify_file(row)
    receipt = {'status': 'PASS_FROZEN_PDF_INPUTS_AND_FRESH_BUILD',
               'build_record_sha256': record_sha256, 'inputs_verified': len(paths),
               'dependencies': dependencies, 'outputs': verified,
               'scope': 'Exact file identities, source/formula/log consistency, vector/search layer, '
                        'links and literal commands. Visual review is separate; native LaTeX is unverified.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n',
                           encoding='utf8', newline='\n')
    print(json.dumps(receipt, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
