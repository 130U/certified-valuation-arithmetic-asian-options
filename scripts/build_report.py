"""Build GitHub Markdown and structured mathematical content from the public TeX source.

Uses only the Python standard library. Run from the repository root:
    python scripts/build_report.py
An initial import can supply --source MAIN.tex --abstract ABSTRACT.tex.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'manuscript'
META = {
    'title': 'Certified Valuation of Arithmetic Asian Options via Common Gaussian Smoothing',
    'subtitle': 'Computable Error Bounds for Projected Euler, Joint Weak Expansions, and Posterior Quantile Transfer',
    'author': 'Theodore Ouyang',
    'affiliation': 'Duke University',
    'emails': ['10@alumni.duke.edu', 'theodore.oy2025@gmail.com'],
    'keywords': ['Arithmetic Asian options', 'Heston model', 'projected Euler', 'conditional Gaussian smoothing', 'computable error bounds', 'weak error expansions', 'posterior quantiles'],
}

DOMAIN = r'''\section{Domain of validity}

The main theorem provides sufficient conditions through the common Gaussian
structure and finite verification inputs. Its scope consists of model classes for
which those inputs can be established. Section~5 verifies a deterministic-variance
class and the specified stochastic-variance model and projected kernel. Comparisons
with other Asian bounds depend on their respective hypotheses and numerical inputs.

The complete small-error Heston Asian certificate applies to the specified
\(\theta_*\), step size, and fixing dates. A uniform certificate on a parameter
neighborhood or an entire domain requires uniform moment, transform, projection,
and tail inequalities. The five-dimensional box with small positive \(\xi\) in
Section~7 is a separately certified region of positive volume, with a
volatility-of-volatility range distinct from that of \(\theta_*\).

The ten-payoff expansion holds on the deterministic-variance family \(\xi=0\).
A corresponding expansion for positive \(\xi\) would require higher-order
regularity and integrable remainders for the combined effects of the projection
kernel and the payoff kinks. For the Asian leading coefficient, the established
conclusion consists of an exact score representation and an effective absolute
bound. High-precision scalar evaluation and nonvanishing of that component are
separate assertions. When \(v_0\ne\bar v\), the nine put components establish
nonvanishing of the ten-dimensional leading coefficient vector. The vector result
expresses the common density construction; each component retains its stated
scalar error budget.

The posterior quantile-displacement certificates use the three-dimensional prior
(7.5) and the synthetic quotes in Appendix~F. They compare two true target
distributions at every quantile level. Determination of the absolute locations of
specified quantiles is a separate valuation task. A quantile-displacement
certificate on the five-dimensional parameter domain
\[
[2,4]\times[.03,.06]\times[.18,.28]\times[-.8,-.3]\times[.03,.06]
\]
requires forward-error and posterior-transport inputs valid throughout that domain.
The synthetic-quote application establishes the stated mathematical transfer under
its specified inputs. Use with market quotes additionally calls for empirical
assessment of quote quality, model fit, transaction costs, and strategy performance.

Conditioning, geometric-average reference variables, Fourier bounds, Gaussian
scores, and posterior approximation have established literatures
\cite{Curran1994,RogersShi1995,Thompson2002,FusaiKyriakou2016,Lee2004,TalayTubaro1990,MickelNeuenkirch2022,CotterDashtiStuart2010}.
The contribution here is their effective combination for the specified kernel,
the payoff-level argument weighted by first-period integrated variance, the
complete finite error budget, and the resulting model-specific quantitative
certificates. Numerical validity uses the enclosure semantics of the stated
interval-arithmetic library. The accompanying independent implementations provide
reproducible comparisons of the finite arithmetic inputs and bounds.

'''


def balanced(s, i):
    if s[i] != '{':
        raise ValueError('Expected opening brace: ' + s[i:i + 60])
    depth, j = 1, i + 1
    while j < len(s) and depth:
        if s[j] == '\\' and j + 1 < len(s) and s[j + 1] in '{}':
            j += 2
            continue
        if s[j] == '{':
            depth += 1
        elif s[j] == '}':
            depth -= 1
        j += 1
    if depth:
        raise ValueError('Unbalanced TeX argument')
    return s[i + 1:j - 1], j


def math_rows(s):
    return [('display' if m.group(1) is not None else 'inline',
             m.group(1) if m.group(1) is not None else m.group(2))
            for m in re.finditer(r'\\\[(.*?)\\\]|\\\((.*?)\\\)', s, re.S)]


def compact_space(s):
    return re.sub(r'\s+', ' ', s)


def github_tex(s):
    # Equivalent base macros avoid HTML parsing and optional extension filters.
    s = s.replace(r'\xRightarrow{\ \Phi\ }', r'\overset{\ \Phi\ }{\Longrightarrow}')
    s = re.sub(r'\\operatorname\{(Var|Re|Im|TV)\}',
               lambda m: r'\mathop{\mathrm{' + m.group(1) + r'}}\nolimits', s)
    return re.sub(r'(?<!\\)[<>]', lambda m: r'\lt ' if m.group() == '<' else r'\gt ', s)


def github_display_tex(s):
    s = github_tex(s.strip())
    # A row container keeps tagged expressions horizontal in native MathML.
    tag = re.search(r'\\tag\*?\{[^}]*\}\s*$', s)
    if tag and not s.startswith(r'\begin{'):
        return (r'\begin{gathered}' + '\n' + s[:tag.start()].strip() + '\n'
                + r'\end{gathered}' + '\n' + tag.group().strip())
    return s


def inlines(s, citations):
    result, buf, i = [], [], 0

    def flush():
        if buf:
            text = compact_space(''.join(buf)).replace('---', '—').replace('--', '–')
            if text:
                result.append({'type': 'text', 'text': text})
            buf.clear()

    while i < len(s):
        if s.startswith(r'\(', i):
            flush()
            j = s.index(r'\)', i + 2)
            result.append({'type': 'math', 'tex': s[i + 2:j]})
            i = j + 2
            continue
        if s[i] == '\\':
            flush()
            m = re.match(r'\\([A-Za-z]+|.)', s[i:])
            cmd = m.group(1)
            i += len(m.group(0))
            if cmd in ('textbf', 'textit', 'emph', 'texttt', 'cite', 'url', 'href'):
                while i < len(s) and s[i].isspace():
                    i += 1
                arg, i = balanced(s, i)
                if cmd == 'cite':
                    result.append({'type': 'citation', 'numbers': [citations[k.strip()] for k in arg.split(',')]})
                elif cmd == 'url':
                    result.append({'type': 'link', 'url': arg, 'inlines': [{'type': 'text', 'text': arg}]})
                elif cmd == 'href':
                    label, i = balanced(s, i)
                    result.append({'type': 'link', 'url': arg, 'inlines': inlines(label, citations)})
                elif cmd == 'texttt':
                    result.append({'type': 'code', 'text': arg.replace(r'\_', '_')})
                else:
                    result.append({'type': 'strong' if cmd == 'textbf' else 'emphasis', 'inlines': inlines(arg, citations)})
            elif cmd in ('%', '&', '_', '#', '$', '{', '}'):
                buf.append(cmd)
            elif cmd in ('hfill', '\\'):
                buf.append(' ')
            elif cmd in ('^', '"'):
                if i < len(s) and s[i] == '{':
                    arg, i = balanced(s, i)
                else:
                    arg, i = s[i], i + 1
                buf.append({('^', 'o'): 'ô', ('^', 'a'): 'â', ('"', 'o'): 'ö', ('"', 'u'): 'ü'}.get((cmd, arg), arg))
            else:
                raise ValueError('Unhandled prose command: ' + cmd + ' in ' + s[:100])
            continue
        if s[i] in '{}':
            i += 1
            continue
        buf.append(' ' if s[i] == '~' else s[i])
        i += 1
    flush()
    return result


def inline_md(nodes):
    out = []
    for n in nodes:
        kind = n['type']
        if kind == 'text':
            out.append(n['text'])
        elif kind == 'math':
            out.append('$`' + compact_space(github_tex(n['tex'])) + '`$')
        elif kind == 'code':
            out.append('`' + n['text'] + '`')
        elif kind == 'strong':
            out.append('**' + inline_md(n['inlines']) + '**')
        elif kind == 'emphasis':
            out.append('*' + inline_md(n['inlines']) + '*')
        elif kind == 'link':
            out.append('[' + inline_md(n['inlines']) + '](' + n['url'] + ')')
        elif kind == 'citation':
            out.append('[' + ', '.join('[' + str(k) + '](#ref-' + str(k) + ')' for k in n['numbers']) + ']')
        else:
            raise ValueError(kind)
    return ''.join(out)


def tokenize(s):
    pat = re.compile(r'\\\[|\\begin\{tabularx\}|\\begin\{enumerate\}|\\(?:section\*?|subsection)\{|\\appendix\b')
    pos = 0
    while True:
        m = pat.search(s, pos)
        if not m:
            if s[pos:].strip():
                yield 'prose', s[pos:]
            return
        if s[pos:m.start()].strip():
            yield 'prose', s[pos:m.start()]
        marker = m.group(0)
        if marker == r'\[':
            end = s.index(r'\]', m.end())
            yield 'display', s[m.end():end]
            pos = end + 2
        elif marker.startswith(r'\begin'):
            env = 'tabularx' if 'tabularx' in marker else 'enumerate'
            end = s.index(r'\end{' + env + '}', m.end()) + len(r'\end{' + env + '}')
            yield env, s[m.start():end]
            pos = end
        elif marker == r'\appendix':
            yield 'appendix', ''
            pos = m.end()
        else:
            title, end = balanced(s, m.end() - 1)
            yield ('sectionstar' if '*' in marker else 'subsection' if 'subsection' in marker else 'section'), title
            pos = end


def clean_prose(s):
    s = re.sub(r'^%.*$', '', s, flags=re.M)
    s = re.sub(r'\\(?:begingroup|endgroup|small)\b', '', s)
    s = re.sub(r'\\(?:begin|end)\{center\}', '', s)
    s = re.sub(r'\\setlength\{\\tabcolsep\}\{[^}]*\}|\\renewcommand\{\\arraystretch\}\{[^}]*\}', '', s)
    return s


def table_rows(source, citations):
    content = source[source.index('\n') + 1:source.rindex(r'\end{tabularx}')]
    content = re.sub(r'\\(?:toprule|midrule|bottomrule|addlinespace)\b', '', content)
    rows, row, cell, i, inmath = [], [], '', 0, False
    while i < len(content):
        if content.startswith(r'\(', i):
            inmath = True
            cell += r'\('
            i += 2
        elif content.startswith(r'\)', i):
            inmath = False
            cell += r'\)'
            i += 2
        elif not inmath and content.startswith('\\\\', i):
            row.append({'inlines': inlines(cell.strip(), citations)})
            rows.append(row)
            row, cell = [], ''
            i += 2
        elif not inmath and content[i] == '&':
            row.append({'inlines': inlines(cell.strip(), citations)})
            cell = ''
            i += 1
        else:
            cell += content[i]
            i += 1
    assert not cell.strip() and rows
    assert all(len(r) == len(rows[0]) for r in rows)
    return rows


def make_blocks(s, citations, abstract=False):
    blocks, section, sub, appendix = [], 0, 0, False
    for kind, text in tokenize(s):
        if kind == 'appendix':
            appendix, section = True, 0
            continue
        if kind in ('section', 'subsection', 'sectionstar'):
            if kind == 'section':
                section += 1
                sub = 0
                number = chr(64 + section) if appendix else str(section)
                label = ('Appendix ' + number if appendix else number) + '. '
                ident = 'section-' + number.lower()
                level = 2
            elif kind == 'subsection':
                sub += 1
                number = (chr(64 + section) if appendix else str(section)) + '.' + str(sub)
                label, ident, level = number + ' ', 'section-' + number.lower().replace('.', '-'), 3
            else:
                number, label, ident, level = None, '', 'author-note', 2
            ns = inlines(text, citations)
            b = {'type': 'heading', 'id': ident, 'level': level, 'number': number,
                 'appendix': appendix, 'inlines': ns,
                 'markdown': '#' * level + ' ' + label + inline_md(ns)}
        elif kind == 'display':
            tags = re.findall(r'\\tag\*?\{([^}]*)\}', text)
            b = {'type': 'display_math', 'id': 'eq-' + tags[0].lower().replace('.', '-') if tags else 'display-' + hashlib.sha256(text.encode()).hexdigest()[:12],
                 'tex': text, 'tags': tags, 'markdown': '```math\n' + github_display_tex(text) + '\n```'}
        elif kind == 'prose':
            for p in re.split(r'\n\s*\n', clean_prose(text)):
                p = p.strip()
                if not p:
                    continue
                if p == r'\clearpage':
                    continue
                ns = inlines(p, citations)
                blocks.append({'type': 'paragraph', 'inlines': ns, 'markdown': inline_md(ns)})
            continue
        elif kind == 'enumerate':
            inner = text[len(r'\begin{enumerate}'):-len(r'\end{enumerate}')]
            items = [{'inlines': inlines(x.strip(), citations)} for x in inner.split(r'\item')[1:]]
            b = {'type': 'ordered_list', 'items': items,
                 'markdown': '\n'.join(str(i) + '. ' + inline_md(x['inlines']) for i, x in enumerate(items, 1))}
        elif kind == 'tabularx':
            rows = table_rows(text, citations)
            mdrows = ['| ' + ' | '.join(inline_md(c['inlines']).replace('|', r'\|') for c in r) + ' |' for r in rows]
            mdrows.insert(1, '| ' + ' | '.join('---' for c in rows[0]) + ' |')
            b = {'type': 'table', 'rows': rows, 'header_rows': 1, 'markdown': '\n'.join(mdrows)}
        else:
            raise ValueError(kind)
        blocks.append(b)
    return blocks


def references(source):
    source = source.split(r'\begin{thebibliography}{12}', 1)[1].split(r'\end{thebibliography}', 1)[0]
    refs = []
    for i, m in enumerate(re.finditer(r'\\bibitem\{([^}]+)\}\s*(.*?)(?=\\bibitem|\Z)', source, re.S), 1):
        key, text = m.groups()
        url = re.search(r'\\url\{([^}]+)\}', text).group(1)
        prose = re.sub(r'\\url\{[^}]+\}\.?', '', text).strip()
        prose = re.sub(r'\.\.(?=\s|$)', '.', prose)
        ns = inlines(prose, {})
        refs.append({'number': i, 'key': key, 'inlines': ns, 'text': inline_md(ns), 'url': url})
    assert len(refs) == 12
    return refs


def sanitize_body(body):
    body = re.sub(r'\\(?:thispagestyle|pagestyle)\{[^}]*\}', '', body)
    body = re.sub(r'\\markright\{.*?\}\s*\n', '', body)
    body = re.sub(r'\\section\{(?:Scope and limitations|Domain of validity)\}.*?(?=\\section\{Conclusion\})', lambda m: DOMAIN, body, flags=re.S)
    body = re.sub(r'\\section\*\{Acknowledgments and author\x27s note\}.*?(?=\\appendix)', '', body, flags=re.S)
    body = body.replace('Section~9 specifies the limits of applicability.', 'Section~9 specifies the domain of validity.')
    body = body.replace('the frozen input file', 'the reference input file')
    body = body.replace('frozen reference results', 'reference results')
    body = body.replace('The frozen environment is', 'The reference environment is')
    body = body.replace('their audited versions unchanged', 'their reference versions')
    return body.strip() + '\n'


def walk_inline(nodes):
    for n in nodes:
        if n['type'] == 'math':
            yield n['tex']
        yield from walk_inline(n.get('inlines', []))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, default=OUT / 'report-source.tex')
    ap.add_argument('--abstract', type=Path)
    args = ap.parse_args()
    src = args.source.read_text(encoding='utf8')
    if r'\begin{document}' in src:
        abstract = args.abstract.read_text(encoding='utf8') if args.abstract else None
        if abstract is None:
            raise ValueError('Initial import requires --abstract')
        body = src.split(r'\begin{document}', 1)[1].rsplit(r'\clearpage', 1)[0]
    else:
        abstract = src.split(r'\begin{abstract}', 1)[1].split(r'\end{abstract}', 1)[0].strip() + '\n'
        body = src.split(r'\end{abstract}', 1)[1].split(r'\begin{thebibliography}', 1)[0]
    original_math = math_rows(abstract + body)
    refs = references(src)
    citations = {r['key']: r['number'] for r in refs}
    body = sanitize_body(body)
    replacement_g = OUT / 'implementation-section.tex'
    if replacement_g.exists():
        body = body.split(r'\section{Reproducible implementation}', 1)[0] + replacement_g.read_text(encoding='utf8').strip() + '\n'
    assert original_math == math_rows(abstract + body), 'Math changed or reordered during public editing'
    blocks = [{'type': 'heading', 'id': 'abstract', 'level': 2, 'number': None, 'appendix': False,
               'inlines': [{'type': 'text', 'text': 'Abstract'}], 'markdown': '## Abstract'}]
    blocks += make_blocks(abstract, citations, abstract=True)
    blocks += make_blocks(body, citations)
    blocks.append({'type': 'heading', 'id': 'references', 'level': 2, 'number': None, 'appendix': False,
                   'inlines': [{'type': 'text', 'text': 'References'}], 'markdown': '## References'})
    for r in refs:
        blocks.append({'type': 'reference', 'id': 'ref-' + str(r['number']), **r,
                       'markdown': '<a id="ref-' + str(r['number']) + '"></a>\n\n' + str(r['number']) + '. ' + r['text'] + ' [Source](' + r['url'] + ')'})
    inline = []
    for b in blocks:
        inline.extend(walk_inline(b.get('inlines', [])))
        for row in b.get('rows', []):
            for cell in row:
                inline.extend(walk_inline(cell['inlines']))
        for item in b.get('items', []):
            inline.extend(walk_inline(item['inlines']))
    displays = [b['tex'] for b in blocks if b['type'] == 'display_math']
    tags = [t for b in blocks for t in b.get('tags', [])]
    assert Counter(('display', x) for x in displays) + Counter(('inline', x) for x in inline) == Counter(original_math)
    heads = [b for b in blocks if b['type'] == 'heading' and b.get('number') and b['level'] == 2]
    counts = {'main_sections': sum(not b['appendix'] for b in heads), 'appendices': sum(b['appendix'] for b in heads),
              'display_math': len(displays), 'inline_math': len(inline), 'equation_tags': len(tags), 'unique_tags': len(set(tags)),
              'tables': sum(b['type'] == 'table' for b in blocks), 'references': len(refs)}
    assert counts == {'main_sections': 10, 'appendices': 7, 'display_math': 147, 'inline_math': 373, 'equation_tags': 88, 'unique_tags': 88, 'tables': 4, 'references': 12}, counts
    document = {'schema_version': 1, 'metadata': META, 'counts': counts, 'blocks': blocks, 'references': refs}
    title = '# ' + META['title'] + '\n\n' + META['subtitle'] + '\n\n**' + META['author'] + '** · ' + META['affiliation'] + '\n\n'
    title += ' · '.join('[' + e + '](mailto:' + e + ')' for e in META['emails']) + '\n\n'
    title += '**Keywords:** ' + '; '.join(META['keywords']) + '.\n\n'
    md = title + '\n\n'.join(b['markdown'] for b in blocks) + '\n'
    bib = src.split(r'\begin{thebibliography}{12}', 1)[1].split(r'\end{thebibliography}', 1)[0]
    public_source = '% Public mathematical manuscript source.\n\\begin{abstract}\n' + abstract.strip() + '\n\\end{abstract}\n\n' + body + '\n\\begin{thebibliography}{12}' + bib + '\\end{thebibliography}\n'
    for name, data in [('report.md', md), ('report.json', json.dumps(document, ensure_ascii=False, indent=2) + '\n'), ('report-source.tex', public_source)]:
        leak = re.search(r'20(?:23|26)|(?<![A-Za-z])[A-Za-z]:[/\\]+[A-Za-z]|completion date|internal review|review package', data, re.I)
        assert not leak, (name, data[max(0, leak.start()-50):leak.end()+70] if leak else '')
        (OUT / name).write_text(data, encoding='utf8', newline='\n')
    verification = {'status': 'PASS', 'counts': counts, 'formula_multiset_exactly_preserved': True,
                    'formula_sequence_exactly_preserved': True,
                    'forbidden_provenance_strings_absent': True,
                    'artifacts': {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in ('report.md', 'report.json', 'report-source.tex')}}
    (OUT / 'content-verification.json').write_text(json.dumps(verification, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps(verification))


if __name__ == '__main__':
    main()
