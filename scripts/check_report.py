"""Verify the Markdown paper, mathematical content, links, and artifact identities."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
from build_report import github_tex

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'manuscript'


def compact(tex):
    return re.sub(r'\s+', ' ', tex.strip())


def inline_math(nodes):
    for node in nodes:
        if node['type'] == 'math':
            yield ('inline', compact(github_tex(node['tex'])))
        if 'inlines' in node:
            yield from inline_math(node['inlines'])


def main():
    report = json.loads((PAPER / 'report.json').read_text(encoding='utf8'))
    md = (PAPER / 'report.md').read_text(encoding='utf8')
    receipt = json.loads((PAPER / 'content-verification.json').read_text(encoding='utf8'))
    expected = []
    for block in report['blocks']:
        if block['type'] == 'display_math':
            expected.append(('display', compact(github_tex(block['tex']))))
        expected.extend(inline_math(block.get('inlines', [])))
        for item in block.get('items', []):
            expected.extend(inline_math(item['inlines']))
        for row in block.get('rows', []):
            for cell in row:
                expected.extend(inline_math(cell['inlines']))

    # Table delimiters require escaping literal pipes in Markdown, including
    # code spans. GitHub removes that escape before passing the span to math.
    pattern = re.compile(r'^```math\n(.*?)\n```$|\$`(.*?)`\$', re.M | re.S)
    actual = []
    for match in pattern.finditer(md):
        if match.group(1) is not None:
            actual.append(('display', compact(match.group(1))))
        else:
            tex = match.group(2)
            line_start = md.rfind('\n', 0, match.start()) + 1
            if md[line_start:match.start()].lstrip().startswith('|'):
                tex = tex.replace(r'\|', '|')
            actual.append(('inline', compact(tex)))
    assert actual == expected, 'Markdown formulas differ from the structured source'
    assert Counter(kind for kind, _ in actual) == {'display': 147, 'inline': 373}
    tags = re.findall(r'\\tag\*?\{([^}]+)\}', md)
    assert len(tags) == 88 and len(set(tags)) == 88
    assert '$$' not in md and re.sub(pattern, '', md).count('$') == 0
    assert md.count('\n| ---') == 4
    for filename, digest in receipt['artifacts'].items():
        assert hashlib.sha256((PAPER / filename).read_bytes()).hexdigest() == digest
    assert receipt['formula_sequence_exactly_preserved']

    readme = (ROOT / 'README.md').read_text(encoding='utf8')
    assert readme.count('Independent research originating in 2024.') == 1
    assert not re.search(r'20(?:23|26)', md + readme)
    assert not re.search(r'HTML reading edition|research website|docs/index|GitHub Pages', md + readme, re.I)
    for text, base in ((md, PAPER), (readme, ROOT)):
        for href in re.findall(r'\]\(([^)]+)\)', text):
            if href.startswith(('https://', 'http://', 'mailto:', '#')):
                continue
            assert (base / href).exists(), 'Missing repository link: ' + href
    assert not list(ROOT.glob('docs/**/*.html'))
    assert not (ROOT / '.github/workflows/pages.yml').exists()
    print(json.dumps({'status': 'PASS', 'display_math': 147, 'inline_math': 373,
                      'equation_tags': 88, 'mathematical_sequence_preserved': True,
                      'source_year': 2024, 'repository_links': 'PASS'}))


if __name__ == '__main__':
    main()
