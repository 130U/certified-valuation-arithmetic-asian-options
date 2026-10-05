"""Build an offline-readable academic website from the structured manuscript."""
from pathlib import Path
import hashlib,html,json,os,re,subprocess,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs';BUILD=ROOT/'.build';CACHE=BUILD/'math'
DOCS.mkdir(exist_ok=True);BUILD.mkdir(exist_ok=True)
REPORT=json.loads((ROOT/'manuscript/report.json').read_text(encoding='utf8'))
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS);ET.register_namespace('xlink','http://www.w3.org/1999/xlink')
items=[]
def collect(nodes):
    for n in nodes:
        if n['type']=='math':items.append({'tex':n['tex'],'display':False})
        if 'inlines' in n:collect(n['inlines'])
for b in REPORT['blocks']:
    if b['type']=='display_math':items.append({'tex':b['tex'],'display':True})
    if 'inlines' in b:collect(b['inlines'])
    for item in b.get('items',[]):collect(item['inlines'])
    for row in b.get('rows',[]):
        for cell in row:collect(cell['inlines'])
assert len(items)==520
(BUILD/'math-inputs.json').write_text(json.dumps(items,ensure_ascii=False),encoding='utf8')
subprocess.run([os.environ.get('NODE_BINARY','node'),str(ROOT/'scripts/render_math.cjs'),str(BUILD/'math-inputs.json'),str(CACHE)],check=True,stdout=subprocess.DEVNULL)
META=json.loads((CACHE/'metadata.json').read_text(encoding='utf8'))
summary=json.loads((CACHE/'render-summary.json').read_text(encoding='utf8'))
assert summary['status']=='PASS'
glyphs={};svgcache={}
for m in META:
    e=ET.parse(CACHE/m['svg']).getroot()
    for parent in e.iter():
        for i,child in enumerate(list(parent)):
            if child.tag==f'{{{NS}}}path' and child.get('data-c'):
                d=child.get('d');key='glyph-'+hashlib.sha256(d.encode()).hexdigest()[:16]
                if key not in glyphs:glyphs[key]=ET.Element(f'{{{NS}}}path',{'id':key,'d':d})
                at=dict(child.attrib);at.pop('d');at['href']='#'+key
                parent.remove(child);parent.insert(i,ET.Element(f'{{{NS}}}use',at))
    e.set('width',f"{m['widthUnits']/1000:.5f}em");e.set('height',f"{m['heightUnits']/1000:.5f}em")
    e.set('style',f"vertical-align:{-m['depthUnits']/1000:.5f}em")
    e.set('aria-hidden','true');e.attrib.pop('role',None)
    svgcache[(m['display'],m['tex'])]=ET.tostring(e,encoding='unicode')

def clean(tex,display=False):
    return re.sub(r'\\tag\*?\s*\{[^}]*\}','',tex).strip() if display else tex.strip()
def formula(tex,display=False):
    source=clean(tex,display);svg=svgcache[(display,source)]
    return '<span class="math" role="math" aria-label="'+html.escape(source,quote=True)+'">'+svg+'</span>'
def link_url(url):
    if url.startswith(('#','https://','http://','mailto:')):return url
    if url.startswith('../'):url=url[3:]
    return 'https://github.com/130U/certified-valuation-arithmetic-asian-options/blob/main/'+url.lstrip('/')

def inlines(nodes):
    result=[]
    for n in nodes:
        t=n['type']
        if t=='text':result.append(html.escape(n['text']))
        elif t=='math':result.append(formula(n['tex']))
        elif t in ('strong','emphasis'):
            tag='strong' if t=='strong' else 'em';result.append(f'<{tag}>'+inlines(n['inlines'])+f'</{tag}>')
        elif t=='code':result.append('<code>'+html.escape(n['text'])+'</code>')
        elif t=='link':result.append('<a href="'+html.escape(link_url(n['url']),quote=True)+'">'+inlines(n['inlines'])+'</a>')
        elif t=='citation':result.append('<span class="citation">['+', '.join(f'<a href="#ref-{i}" aria-label="Reference {i}">{i}</a>' for i in n['numbers'])+']</span>')
        else:raise ValueError(t)
    return ''.join(result)

content=[];toc=[];equations=[]
for b in REPORT['blocks']:
    t=b['type']
    if t=='heading':
        number=b.get('number');title=inlines(b['inlines']);prefix=('Appendix '+number+'. ' if b.get('appendix') and b['level']==2 else number+'. ' if number else '')
        level=b['level'];ident=b['id'];content.append(f'<h{level} id="{ident}">{html.escape(prefix)}{title}<a class="anchor" href="#{ident}" aria-label="Link to section">#</a></h{level}>')
        if level==2:
            plain=''.join(n.get('text','') for n in b['inlines']);toc.append((ident,prefix+plain,bool(b.get('appendix'))))
    elif t=='paragraph':
        rendered=inlines(b['inlines']);klass='statement' if re.match(r'<strong>(?:Lemma|Theorem|Corollary|Proposition)',rendered) else ''
        content.append(f'<p class="{klass}">{rendered}</p>')
    elif t=='display_math':
        ident=b['id'];tags=b['tags'];equations.extend(tags)
        tag=''.join('<span class="equation-number">('+html.escape(x)+')</span>' for x in tags)
        content.append(f'<div class="equation" id="{ident}"><div class="equation-scroll">'+formula(b['tex'],True)+'</div>'+tag+'</div>')
    elif t=='ordered_list':content.append('<ol>'+''.join('<li>'+inlines(x['inlines'])+'</li>' for x in b['items'])+'</ol>')
    elif t=='table':
        rows=[]
        for i,row in enumerate(b['rows']):
            celltag='th' if i<b['header_rows'] else 'td'
            rows.append('<tr>'+''.join(f'<{celltag}>'+inlines(c['inlines'])+f'</{celltag}>' for c in row)+'</tr>')
        content.append('<div class="table-scroll"><table>'+''.join(rows)+'</table></div>')
    elif t=='reference':
        source=' <a class="reference-source" href="'+html.escape(b['url'],quote=True)+'">Source ↗</a>' if b.get('url') else ''
        content.append(f'<p class="reference" id="{b["id"]}"><span class="ref-number">[{b["number"]}]</span>'+inlines(b['inlines'])+source+'</p>')
    else:raise ValueError(t)

defs='<svg class="glyph-definitions" aria-hidden="true" xmlns="'+NS+'"><defs>'+''.join(ET.tostring(e,encoding='unicode') for e in glyphs.values())+'</defs></svg>'
mainnav=''.join(f'<a href="#{i}">{html.escape(t)}</a>' for i,t,a in toc if not a)
appendixnav=''.join(f'<a href="#{i}">{html.escape(t)}</a>' for i,t,a in toc if a)
meta=REPORT['metadata'];repo='https://github.com/130U/certified-valuation-arithmetic-asian-options'
page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Theodore Ouyang's rigorous study of arithmetic Asian valuation: common Gaussian smoothing, complete projected Euler error certificates, joint weak expansions, and posterior quantile transfer.">
<title>{html.escape(meta['title'])} | Theodore Ouyang</title><link rel="stylesheet" href="assets/style.css">
</head><body>{defs}<a class="skip-link" href="#paper">Skip to paper</a>
<header class="site-header"><a class="wordmark" href="#top">Theodore Ouyang<span>Mathematical finance</span></a><nav aria-label="Project navigation"><a href="#paper">Paper</a><a href="{repo}/tree/main/code">Code</a><a href="{repo}">Repository ↗</a></nav></header>
<div class="layout" id="top"><aside class="contents"><p class="contents-label">IN THIS PAPER</p><nav aria-label="Paper contents">{mainnav}<details><summary>Proof appendices</summary>{appendixnav}</details></nav><a class="return-top" href="#top">Back to top ↑</a></aside>
<main><section class="hero" aria-labelledby="paper-title"><p class="eyebrow">PRICING THEORY · VERIFIED NUMERICS</p><h1 id="paper-title">{html.escape(meta['title'])}</h1><p class="subtitle">{html.escape(meta['subtitle'])}</p><p class="byline"><strong>{meta['author']}</strong> · {meta['affiliation']}</p><div class="hero-links"><a href="{repo}/blob/main/manuscript/report.md">GitHub reading edition ↗</a><a href="{repo}/tree/main/code">Reproduce the results ↗</a></div>
<div class="result-summary"><p class="summary-label">COMPLETE CERTIFICATE AT THE SPECIFIED HESTON POINT</p><div class="result-line"><span class="result-value">0.011025</span><span class="result-description">upper bound on absolute Euler–continuous pricing bias</span></div><p>One-year arithmetic Asian call spread · 12 monthly observations · step size 1/768 · initial stock price 100. Parameter definitions and the signed enclosure are stated in the paper.</p></div></section>
<article id="paper">{''.join(content)}</article>
<footer class="site-footer"><p><strong>Theodore Ouyang</strong><br><a href="mailto:10@alumni.duke.edu">10@alumni.duke.edu</a> · <a href="mailto:theodore.oy2025@gmail.com">theodore.oy2025@gmail.com</a></p><a href="{repo}">Research code and sources ↗</a></footer></main></div></body></html>'''
(DOCS/'index.html').write_text(page,encoding='utf8',newline='\n')
(DOCS/'.nojekyll').write_text('',encoding='utf8')
manifest={'title':meta['title'],'author':meta['author'],'manuscript_sha256':hashlib.sha256((ROOT/'manuscript/report.json').read_bytes()).hexdigest(),'html_sha256':hashlib.sha256((DOCS/'index.html').read_bytes()).hexdigest(),'counts':REPORT['counts'],'math_rendering':{'engine':'MathJax','version':'3.2.2','occurrences':summary['occurrences'],'unique_expressions':summary['unique'],'errors':len(summary['errors']),'svg_glyph_definitions':len(glyphs)},'equation_tags':equations,'network_at_read_time':False}
(DOCS/'content-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({'html_bytes':(DOCS/'index.html').stat().st_size,'math':summary['occurrences'],'tags':len(equations),'glyphs':len(glyphs),'status':'PASS'}))
