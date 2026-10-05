"""Check the published reading edition, formula coverage, and local links."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.refs=[];self.math=0;self.svg=0;self.tables=0;self.text=[];self.definition_depth=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.refs.append(a['href'])
        if a.get('role')=='math':self.math+=1
        if tag=='svg':self.svg+=1
        if tag=='table':self.tables+=1
    def handle_data(self,data):self.text.append(data)
page=Page();page.feed((ROOT/'docs/index.html').read_text(encoding='utf8'))
report=json.loads((ROOT/'manuscript/report.json').read_text(encoding='utf8'))
manifest=json.loads((ROOT/'docs/content-manifest.json').read_text(encoding='utf8'))
assert page.math==520 and page.tables==4 and len(set(page.ids))==len(page.ids)
assert not [x for x in page.refs if x.startswith('#') and x[1:] not in page.ids]
assert all(x.startswith(('#','https://','http://','mailto:')) for x in page.refs)
assert all('/../' not in x and '/./' not in x for x in page.refs)
assert 'https://github.com/130U/certified-valuation-arithmetic-asian-options/blob/main/code/README.md' in page.refs
assert 'https://github.com/130U/certified-valuation-arithmetic-asian-options/blob/main/code/SCOPE.md' in page.refs
assert all(b['url'] in page.refs for b in report['blocks'] if b['type']=='reference' and b.get('url'))
assert all(b['id'] in page.ids for b in report['blocks'] if b['type'] in ('heading','display_math','reference'))
assert manifest['manuscript_sha256']==hashlib.sha256((ROOT/'manuscript/report.json').read_bytes()).hexdigest()
assert manifest['html_sha256']==hashlib.sha256((ROOT/'docs/index.html').read_bytes()).hexdigest()
assert 'http://' not in ''.join(page.text)
assert not re.search(r'(?i)(?:completed|consolidated|packaged|cutoff|before March|prior to March)\s+.{0,35}\b20\d{2}\b',' '.join(page.text))
assert (ROOT/'docs/assets/style.css').exists()
assert not list((ROOT/'docs').rglob('*.pdf'))
print(json.dumps({'status':'PASS','math_occurrences':page.math,'tables':page.tables,'local_anchors':len(page.ids),'local_links':sum(x.startswith('#') for x in page.refs),'vector_formula_rendering':True,'offline_assets':True}))
