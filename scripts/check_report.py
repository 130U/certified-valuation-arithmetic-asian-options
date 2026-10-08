"""Verify the online Markdown paper against its preserved formula sequence."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'manuscript'
SOURCE_COMMIT = 'f431e2789dd6a725211c7ba48e6b77d02a9db334'
MATH_PATTERN = re.compile(r'^```math\n(.*?)\n```$|\$`(.*?)`\$', re.M | re.S)
TIMELINE = (
    'Research began in the second half of 2023.',
    'The initial manuscript was written in the first half of 2024.',
    'The project was published on GitHub in 2026.',
)


def compact(tex):
    return re.sub(r'\s+', ' ', tex.strip())


def extract_formula_sequence(md):
    """Return ordered (type, compact TeX) pairs, including table unescaping."""
    # Table delimiters require escaping literal pipes in Markdown, including
    # code spans. GitHub removes that escape before passing the span to math.
    actual = []
    for match in MATH_PATTERN.finditer(md):
        if match.group(1) is not None:
            actual.append(('display', compact(match.group(1))))
        else:
            tex = match.group(2)
            line_start = md.rfind('\n', 0, match.start()) + 1
            if md[line_start:match.start()].lstrip().startswith('|'):
                tex = tex.replace(r'\|', '|')
            actual.append(('inline', compact(tex)))
    return actual


def formula_sequence_sha256(sequence):
    encoded = json.dumps(sequence, ensure_ascii=False, separators=(',', ':')).encode('utf8')
    return hashlib.sha256(encoded).hexdigest()


def main():
    md = (PAPER / 'report.md').read_text(encoding='utf8')
    receipt = json.loads((PAPER / 'content-verification.json').read_text(encoding='utf8'))
    assert receipt['status'] == 'PASS'
    assert receipt['source_commit'] == SOURCE_COMMIT
    counts = receipt['counts']
    assert {key: counts[key] for key in ('display_math', 'inline_math', 'equation_tags', 'tables', 'references')} == {
        'display_math': 176, 'inline_math': 518, 'equation_tags': 95, 'tables': 14, 'references': 13}
    actual = extract_formula_sequence(md)
    digest = formula_sequence_sha256(actual)
    assert digest == receipt['formula_sequence_sha256'], 'The preserved mathematical sequence changed'
    assert Counter(kind for kind, _ in actual) == {'display': counts['display_math'], 'inline': counts['inline_math']}
    for _, tex in actual:
        assert not re.search(r'(?<!\\)[<>]', tex), 'Use TeX comparison macros in rendered formulas'
        assert r'\operatorname' not in tex, 'Use a base operator macro in rendered formulas'
        assert not re.search(r'\\nolimits[A-Za-z]', tex), 'A macro needs a token separator'
    tags = re.findall(r'\\tag\*?\{([^}]+)\}', md)
    assert len(tags)==len(set(tags))==counts['equation_tags']
    baseline=json.loads((ROOT/'scripts/baseline-equation-tags.json').read_text(encoding='utf8'))
    assert set(baseline).issubset(set(tags)), 'An original numbered equation was removed'
    assert '$$' not in md and MATH_PATTERN.sub('', md).count('$') == 0
    assert md.count('\n| ---') == counts['tables']
    references = re.findall(r'^<a id="ref-(\d+)"></a>$', md, re.M)
    assert references == [str(i) for i in range(1, counts['references'] + 1)]
    assert set(receipt['artifacts']) == {'report.md'}
    for filename, artifact_digest in receipt['artifacts'].items():
        assert hashlib.sha256((PAPER / filename).read_bytes()).hexdigest() == artifact_digest
    assert receipt['formula_sequence_exactly_preserved']

    readme = (ROOT / 'README.md').read_text(encoding='utf8')
    for sentence in TIMELINE:
        assert sentence in md and sentence in readme, 'The approved research timeline is missing'
    assert 'Research timeline' in md
    assert not re.search(r'(?<![A-Za-z0-9])V[1-5](?![A-Za-z0-9])|\*\*Version:', md + readme, re.I)
    assert 'planned for release' not in md.lower()
    for text, base in ((md, PAPER), (readme, ROOT)):
        for href in re.findall(r'\]\(([^)]+)\)', text):
            path = urlsplit(href).path
            own_remote = href.startswith(('https://github.com/130U/certified-valuation-arithmetic-asian-options/',
                                          'https://raw.githubusercontent.com/130U/certified-valuation-arithmetic-asian-options/'))
            if not href.startswith(('https://', 'http://', 'mailto:', '#')) or own_remote:
                assert not path.lower().endswith('.tex'), 'An author typesetting-source link remains: ' + href
                if path.lower().endswith('.pdf'):
                    assert path.endswith('/paper/paper.pdf') or path == 'paper/paper.pdf', 'Unexpected author PDF: ' + href
            if href.startswith(('https://', 'http://', 'mailto:', '#')):
                continue
            assert (base / path).exists(), 'Missing repository link: ' + href
    print(json.dumps({'status': 'PASS', 'display_math': counts['display_math'], 'inline_math': counts['inline_math'],
                      'equation_tags': len(tags), 'mathematical_sequence_preserved': True,
                      'formula_sequence_sha256': digest, 'source_commit': SOURCE_COMMIT,
                      'research_timeline': list(TIMELINE), 'repository_links': 'PASS',
                      'author_pdf_entry': 'paper/paper.pdf', 'author_tex_download_links': 'ABSENT'}))


if __name__ == '__main__':
    main()
