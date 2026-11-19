"""Verify the article, its complete equation reference and publication links."""
from pathlib import Path
from collections import Counter
import hashlib
import html
import json
import re
import sys
from urllib.parse import urlsplit

if sys.flags.optimize:
    raise RuntimeError('Run verification without -O or PYTHONOPTIMIZE; assertions are required.')

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'manuscript'
MATH_PATTERN = re.compile(r'<img src="(math/formula-m[0-9a-f]{20})-light\.svg" width="\d+" alt="([^"]*)">|\$`(.*?)`\$', re.S)
PAGE_BUDGET = 2000
UNDRAWN = re.compile(r'\\(?:mathbb|mathcal|mathbf|boldsymbol|mathfrak|mathsf|tag|boxed)(?![A-Za-z])')
REVIEWED = {'display_math': 197, 'inline_math': 939, 'equation_tags': 118, 'tables': 14, 'figures': 4, 'references': 35}


def compact(tex):
    return re.sub(r'\s+', ' ', tex.strip())


def extract_formula_sequence(md):
    """Return ordered (type, compact TeX) pairs, including table unescaping.

    A display is a vector image whose alt text holds its TeX; an inline formula is a GitHub math span.
    """
    # Table delimiters require escaping literal pipes in Markdown, including
    # code spans. GitHub removes that escape before passing the span to math.
    actual = []
    for match in MATH_PATTERN.finditer(md):
        if match.group(1) is not None:
            actual.append(('display', compact(html.unescape(match.group(2)))))
        else:
            tex = match.group(3)
            line_start = md.rfind('\n', 0, match.start()) + 1
            if md[line_start:match.start()].lstrip().startswith('|'):
                tex = tex.replace(r'\|', '|')
            actual.append(('inline', compact(tex)))
    return actual


def formula_sequence_sha256(sequence):
    encoded = json.dumps(sequence, ensure_ascii=False, separators=(',', ':')).encode('utf8')
    return hashlib.sha256(encoded).hexdigest()


def numbered_formulas(sequence):
    numbered = {}
    for kind, tex in sequence:
        if kind == 'display':
            for tag in re.findall(r'\\tag\*?\{([^}]+)\}', tex):
                numbered[tag] = tex
    return numbered


def main():
    md = (PAPER / 'report.md').read_text(encoding='utf8')
    receipt = json.loads((PAPER / 'content-verification.json').read_text(encoding='utf8'))
    assert receipt['status'] == 'PASS'
    assert receipt['publication_year'] == 2026
    counts = receipt['counts']
    assert {key: counts[key] for key in REVIEWED} == REVIEWED
    actual = extract_formula_sequence(md)
    digest = formula_sequence_sha256(actual)
    assert digest == receipt['formula_sequence_sha256'], 'The reviewed mathematical sequence changed'
    assert Counter(kind for kind, _ in actual) == {'display': counts['display_math'], 'inline': counts['inline_math']}
    for _, tex in actual:
        assert not re.search(r'(?<!\\)[<>]', tex), 'Use TeX comparison macros in rendered formulas'
        assert r'\operatorname' not in tex, 'Use a base operator macro in rendered formulas'
        assert not re.search(r'\\nolimits[A-Za-z]', tex), 'A macro needs a token separator'
    # GitHub draws an inline formula as MathML. A page has a budget of one unit per formula and one per
    # opening brace, and letter variants are written as Unicode characters.
    inline = [tex for kind, tex in actual if kind == 'inline']
    assert sum(1 + tex.count('{') for tex in inline) <= PAGE_BUDGET, 'Inline formulas exceed the page budget'
    for tex in inline:
        assert not UNDRAWN.search(tex), 'An inline formula uses a macro GitHub does not draw: ' + tex
    images = set()
    for match in MATH_PATTERN.finditer(md):
        if match.group(1) is not None:
            for theme in ('light', 'dark'):
                name = match.group(1) + '-' + theme + '.svg'
                assert (PAPER / name).is_file() and name in md, name
                images.add(name)
    assert {'math/' + path.name for path in (PAPER / 'math').glob('*.svg')} == images, 'Display images and article differ'
    assert '```math' not in md
    tags = re.findall(r'\\tag\*?\{([^}]+)\}', md)
    assert len(tags) == len(set(tags)) == counts['equation_tags']
    sections = {}
    for tag in tags:
        head, tail = tag.split('.')
        sections.setdefault(head, []).append(int(tail))
    for head, tails in sections.items():
        assert tails == list(range(1, len(tails) + 1)), 'Equation numbers in section ' + head + ' are not consecutive'
    equations = json.loads((PAPER / 'equations.json').read_text(encoding='utf8'))
    numbered = numbered_formulas(actual)
    assert numbered == equations['equations'], 'A numbered formula differs from the reviewed reference'
    assert len(numbered) == REVIEWED['equation_tags']
    assert '$$' not in md and MATH_PATTERN.sub('', md).count('$') == 0
    assert md.count('\n| ---') == counts['tables']
    figures = re.findall(r'^!\[Figure (\d+)\. [^\]]*\]\((figures/[a-z-]+\.png)\)$', md, re.M)
    assert [number for number, _ in figures] == [str(i) for i in range(1, counts['figures'] + 1)]
    for number, path in figures:
        assert (PAPER / path).is_file(), path
        assert md.count('**Figure ' + number + '. ') == 1, 'Figure ' + number + ' needs one caption'
    references = re.findall(r'^<a id="ref-(\d+)"></a>$', md, re.M)
    assert references == [str(i) for i in range(1, counts['references'] + 1)]
    cited = set(re.findall(r'\]\(#ref-(\d+)\)', md))
    assert cited == set(references), 'Every reference is cited and every citation resolves'
    assert set(receipt['artifacts']) == {'report.md'}
    for filename, artifact_digest in receipt['artifacts'].items():
        assert hashlib.sha256((PAPER / filename).read_bytes()).hexdigest() == artifact_digest
    assert receipt['source_to_output_formula_sequence_preserved']

    readme = (ROOT / 'README.md').read_text(encoding='utf8')
    assert '**Letao (Theodore) Ouyang**' in md and '\n\n2026\n\n' in md
    assert not re.search(r'\brevision\b|round[ -]?2|26 October 2026|2026-10-26|Research timeline', md + readme, re.I)
    for text, base in ((md, PAPER), (readme, ROOT)):
        for href in re.findall(r'\]\(([^)]+)\)', text):
            path = urlsplit(href).path
            own_remote = href.startswith(('https://github.com/130U/RESEARCH-Certified-Valuation-of-Arithmetic-Asian-Options/',
                                          'https://raw.githubusercontent.com/130U/RESEARCH-Certified-Valuation-of-Arithmetic-Asian-Options/'))
            if not href.startswith(('https://', 'http://', 'mailto:', '#')) or own_remote:
                assert not path.lower().endswith('.tex'), 'An author typesetting-source link remains: ' + href
                if path.lower().endswith('.pdf'):
                    assert path.endswith('/paper/paper.pdf') or path == 'paper/paper.pdf', 'Unexpected author PDF: ' + href
            if href.startswith(('https://', 'http://', 'mailto:', '#')):
                continue
            assert (base / path).exists(), 'Missing repository link: ' + href
    print(json.dumps({'status': 'PASS', 'display_math': counts['display_math'], 'inline_math': counts['inline_math'],
                      'equation_tags': len(tags), 'reviewed_formula_sequence_verified': True,
                      'numbered_formula_reference_verified': len(numbered), 'figures': len(figures),
                      'formula_sequence_sha256': digest, 'publication_year': 2026,
                      'repository_links': 'PASS',
                      'author_pdf_entry': 'paper/paper.pdf', 'author_tex_download_links': 'ABSENT'}))


if __name__ == '__main__':
    main()
