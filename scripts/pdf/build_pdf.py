"""Typeset the complete verified manuscript with ReportLab and vector mathematics."""
from pathlib import Path
import re,json,hashlib,html,subprocess,sys,shutil,argparse,tarfile
from collections import Counter
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT,TA_CENTER,TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,Flowable,Table,TableStyle,ListFlowable,ListItem,Preformatted
from reportlab.platypus.tableofcontents import TableOfContents
from vector_math import MathCanvas
from extract_math_inputs import canonical
from cjk_line_break import break_lines_cjk

class Paragraph(Paragraph):
    def breakLinesCJK(self, maxWidths):
        # ReportLab 4.4.9 treats an inline image as an empty string, then
        # calls ord() on it at a CJK line break. The object marker carries
        # the callback's existing width; the image/anchor callback draws
        # the object, so the marker itself is never printed.
        for frag in self.frags:
            if hasattr(frag, 'cbDefn') and not frag.text:
                frag.text = '\ufffc'
        return break_lines_cjk(self, maxWidths)

ROOT=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--language',choices=['en','zh'],default='en')
ap.add_argument('--node',default=shutil.which('node'))
ap.add_argument('--output',type=Path)
ARGS=ap.parse_args()
assert ARGS.node, 'Supply --node or put Node.js on PATH.'
LANG=ARGS.language
SRC=ROOT/'manuscript'
BUILD=ROOT/'.build/pdf';BUILD.mkdir(parents=True,exist_ok=True)
CACHE=BUILD/'math'
OUT=ARGS.output or ROOT/'paper'/('paper.pdf' if LANG=='en' else 'paper-zh.pdf')
NODE=ARGS.node
archive=Path(__file__).parent/'vendor/mathjax-full-3.2.2.tgz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='d8f080d2e4bdfb75284aac34d5eff155002eca47798b1d4e4bde31453e653f87'
if not (BUILD/'vendor/package/js/mathjax.js').exists():
    (BUILD/'vendor').mkdir(exist_ok=True)
    with tarfile.open(archive) as t:
        for member in t:
            parts=Path(member.name).parts
            assert parts and parts[0]=='package' and '..' not in parts and not Path(member.name).is_absolute()
            assert member.isfile() or member.isdir(), 'Only regular files and directories are accepted.'
            target=BUILD/'vendor'/member.name
            if member.isdir():target.mkdir(parents=True,exist_ok=True)
            else:
                target.parent.mkdir(parents=True,exist_ok=True)
                with t.extractfile(member) as source, target.open('wb') as output:shutil.copyfileobj(source,output)
DATA=json.loads((SRC/'report.json').read_text(encoding='utf8'))
if LANG=='zh':
    DATA['metadata'].update(title='算术亚式期权的认证估值',subtitle='共同高斯平滑与投影 Euler 误差界')
DATA['keywords_plain']='; '.join(DATA['metadata']['keywords'])
for ref in DATA['references']:ref.update(plain=ref['text'],url=ref['url'])
MARGIN=70.866;PAGE_W,PAGE_H=A4;WIDTH=PAGE_W-2*MARGIN
FONT=10.909;LEADING=13.55
FONTDIR=ROOT/'assets/fonts'
for name,file in [('TimesR','cmr10.ttf'),('TimesB','cmb10.ttf'),('TimesI','cmti10.ttf'),('TimesBI','cmti10.ttf'),('GeorgiaB','cmr10.ttf'),('Mono','cmtt10.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONTDIR/file)))
pdfmetrics.registerFont(TTFont('Accent',str(FONTDIR/'DejaVuSerif.ttf')))
if LANG=='zh':
    for name,file in [('SongR','NotoSerifSC-Regular.ttf'),('SongB','NotoSerifSC-Bold.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(FONTDIR/file)))
    pdfmetrics.registerFontFamily('SongR',normal='SongR',bold='SongB',italic='SongR',boldItalic='SongB')
pdfmetrics.registerFontFamily('TimesR',normal='TimesR',bold='TimesB',italic='TimesI',boldItalic='TimesBI')
pdfmetrics.registerFontFamily('Mono',normal='Mono',bold='Mono',italic='Mono',boldItalic='Mono')

def style(name,**kw):
    base=dict(fontName='TimesR',fontSize=FONT,leading=LEADING,textColor=colors.black,spaceAfter=0,firstLineIndent=10.909,alignment=TA_JUSTIFY,allowWidows=0,allowOrphans=0,autoLeading='max')
    base.update(kw)
    if LANG=='zh':
        base['wordWrap']='CJK'
        base['fontName']='SongB' if base['fontName']=='TimesB' else 'SongR' if base['fontName']=='TimesR' else base['fontName']
        base['leading']=max(base['leading'],base['fontSize']*1.48)
    return ParagraphStyle(name,**base)
ST={
 'body':style('body'),
 'h1':style('h1',fontName='TimesB',fontSize=14.35,leading=18,firstLineIndent=0,spaceBefore=17,spaceAfter=9,alignment=TA_LEFT,keepWithNext=True),
 'h2':style('h2',fontName='TimesB',fontSize=11.96,leading=15,firstLineIndent=0,spaceBefore=14,spaceAfter=7,alignment=TA_LEFT,keepWithNext=True),
 'title':style('title',fontName='TimesR',fontSize=17.215,leading=21,firstLineIndent=0,spaceAfter=6.36,alignment=TA_CENTER),
 'subtitle':style('subtitle',fontSize=11.955,leading=14.5,firstLineIndent=0,alignment=TA_CENTER,spaceAfter=15.72),
 'author':style('author',fontName='TimesR',fontSize=11.955,leading=14.5,firstLineIndent=0,alignment=TA_CENTER,spaceAfter=1),
 'meta':style('meta',fontSize=9.963,leading=12,firstLineIndent=0,alignment=TA_CENTER,spaceAfter=1),
 'abstract':style('abstract',fontSize=9.963,leading=12,firstLineIndent=10,rightIndent=27.273,leftIndent=27.273,spaceAfter=0),
 'keywords':style('keywords',fontSize=9.0,leading=12,firstLineIndent=0,leftIndent=27.273,rightIndent=27.273,alignment=TA_LEFT,spaceAfter=0),
 'table':style('table',fontSize=9.4,leading=12.4,firstLineIndent=0,alignment=TA_LEFT,spaceAfter=0),
 'tablehead':style('tablehead',fontName='TimesB',fontSize=9.4,leading=12.4,firstLineIndent=0,alignment=TA_LEFT,spaceAfter=0),
 'reference':style('reference',fontSize=10.909,leading=13.55,alignment=TA_LEFT,leftIndent=23,firstLineIndent=-23,spaceAfter=5),
 'theorem':style('theorem',spaceBefore=7,spaceAfter=7),
 'toc':style('toc',fontSize=11,leading=16,alignment=TA_LEFT,spaceBefore=6,spaceAfter=3,leftIndent=0,rightIndent=22),
}

source_path=SRC/('report-source.tex' if LANG=='en' else 'report-source-zh.tex')
main=source_path.read_text(encoding='utf8')
body=main.split('\\end{abstract}',1)[1].split('\\begin{thebibliography}',1)[0]
body=re.sub(r'\\(?:thispagestyle|pagestyle)\{[^}]*\}', '',body)
body=re.sub(r'\\markright\{.*?\}\s*\n','',body)
abstract=main.split('\\begin{abstract}',1)[1].split('\\end{abstract}',1)[0]
math_inputs=[]
for s in [abstract,body]:
    for m in re.finditer(r'\\\[(.*?)\\\]|\\\((.*?)\\\)',s,re.S):
        display=m.group(1) is not None; tex=m.group(1) if display else m.group(2)
        ident,clean,tags=canonical(tex,display)
        math_inputs.append(dict(id=ident,tex=tex,display=display,tags=tags))
inputpath=BUILD/('math-inputs-'+LANG+'.json')
inputpath.write_text(json.dumps(math_inputs,ensure_ascii=False,indent=2),encoding='utf8')
# cached math reused
subprocess.run([str(NODE),str(Path(__file__).with_name('render_math.cjs')),str(inputpath),str(CACHE)],check=True,stdout=subprocess.DEVNULL)
MATH={x['id']:x for x in json.loads((CACHE/'metadata.json').read_text(encoding='utf8'))}
MathCanvas.math_meta=MATH;MathCanvas.math_dir=CACHE
for ident in MATH:
    p=CACHE/(ident+'.png')
    if not p.exists():Image.new('RGBA',(1,1),(0,0,0,0)).save(p)
CITES={r['key']:r['number'] for r in DATA['references']}
LOG=dict(unknown_commands=[],math_occurrences=[],displays=[],headings=[],tables=[],prose=[],source_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest())

def balanced(s,start):
    if s[start]!='{':raise ValueError('Expected opening brace')
    depth=1;i=start+1
    while i<len(s) and depth:
        if s[i]=='\\' and i+1<len(s) and s[i+1] in '{}':i+=2;continue
        if s[i]=='{':depth+=1
        elif s[i]=='}':depth-=1
        i+=1
    if depth:raise ValueError('Unbalanced argument')
    return s[start+1:i-1],i

def markup(s,font=FONT,literal=False):
    result=[];i=0
    while i<len(s):
        if s.startswith('\\(',i):
            j=s.index('\\)',i+2);tex=s[i+2:j];ident,_,_=canonical(tex,False);m=MATH[ident]
            suffix=re.match(r'[.,;:!?)\]]+|-[A-Za-z]+',s[j+2:])
            trailing=suffix.group(0) if suffix else ''
            image_id=ident
            if trailing:
                image_id=ident+'s'+hashlib.sha256(trailing.encode()).hexdigest()[:8]
                if image_id not in MATH:
                    asc,desc=pdfmetrics.getAscentDescent('TimesR',1000)
                    asc=max(asc,m['ascentUnits']);dep=max(-desc,m['depthUnits'])
                    width=m['widthUnits']+pdfmetrics.stringWidth(trailing,'TimesR',1000)
                    MATH[image_id]=dict(base=ident,suffix=trailing,suffix_font='TimesR',widthUnits=width,heightUnits=asc+dep,ascentUnits=asc,depthUnits=dep,viewBox=[0,-asc,width,asc+dep])
                    Image.new('RGBA',(1,1),(0,0,0,0)).save(CACHE/(image_id+'.png'))
                m=MATH[image_id]
            w=m['widthUnits']*font/1000;h=m['heightUnits']*font/1000;depth=m['depthUnits']*font/1000
            if w>WIDTH:raise ValueError('Inline equation wider than page '+tex)
            result.append(f'<img src="{CACHE/(image_id+".png")}" width="{w:.5f}" height="{h:.5f}" valign="{-depth:.5f}"/>')
            LOG['math_occurrences'].append(ident);i=j+2+len(trailing);continue
        if s[i]=='\\':
            m=re.match(r'\\([A-Za-z]+|.)',s[i:]);cmd=m.group(1);i+=len(m.group(0))
            if cmd in ('textbf','textit','emph','texttt','cite','url','href'):
                while i<len(s) and s[i].isspace():i+=1
                arg,i=balanced(s,i)
                if cmd=='cite':
                    nums=[CITES[k.strip()] for k in arg.split(',')]
                    result.append('['+', '.join(f'<link href="#ref-{n}" color="#0000ff">{n}</link>' for n in nums)+']')
                elif cmd=='url': result.append(f'<link href="{html.escape(arg,quote=True)}" color="#0000ff">{html.escape(arg)}</link>')
                elif cmd=='href':
                    label,i=balanced(s,i);result.append(f'<link href="{html.escape(arg,quote=True)}">{markup(label,font)}</link>')
                else:
                    tag={'textbf':'b','textit':'i','emph':'i','texttt':'font name="Mono"'}[cmd];end=tag.split()[0]
                    result.append(f'<{tag}>{markup(arg,font,literal=cmd=="texttt")}</{end}>')
            elif cmd in ('%','&','_','#','$','{','}'):result.append(html.escape(cmd))
            elif cmd=='hfill':result.append(' ')
            elif cmd=='\\':result.append('<br/>')
            elif cmd in ('^','"'):
                if i<len(s) and s[i]=='{':arg,i=balanced(s,i)
                else:arg=s[i];i+=1
                accents={('^','o'):'ô',('^','a'):'â',('"','o'):'ö',('"','u'):'ü'}
                result.append('<font name="Accent">'+accents.get((cmd,arg),arg)+'</font>')
            else:LOG['unknown_commands'].append(cmd);raise ValueError('Unknown prose command '+cmd+' in '+s[:100])
            continue
        if s[i] in '{}':i+=1;continue
        if s[i] in ('–','—'):result.append('<font name="Accent">'+s[i]+'</font>')
        elif not literal and s.startswith('---',i):result.append('<font name="Accent">—</font>');i+=3;continue
        elif not literal and s.startswith('--',i):result.append('<font name="Accent">–</font>');i+=2;continue
        elif s[i]=='~':result.append(' ')
        elif s[i]=='\n':result.append(' ')
        else:result.append(html.escape(s[i]))
        i+=1
    return ''.join(result)

class Display(Flowable):
    def __init__(self,tex):
        super().__init__();self.ident,self.tex,self.tags=canonical(tex,True);self.row=MATH[self.ident];self.spaceBefore=8;self.spaceAfter=8
        if 'F.3' in self.tags or 'L_0=' in tex or 'a_{m,j}' in tex:self.keepWithNext=True
        LOG['math_occurrences'].append(self.ident)
    def wrap(self,availW,availH):
        room=availW-(45 if self.tags else 0);self.fs=min(10.909,room*1000/self.row['widthUnits'])
        self.w=self.row['widthUnits']*self.fs/1000;self.h=self.row['heightUnits']*self.fs/1000
        self.width=availW;self.height=self.h+3
        return self.width,self.height
    def draw(self):
        room=self.width-(45 if self.tags else 0);x=(room-self.w)/2
        self.canv.math(self.ident,x,1.5,self.w,self.h)
        for tag in self.tags:
            key='eq-'+tag.replace('.','-');self.canv.bookmarkHorizontalAbsolute(key,self.canv.absolutePosition(0,self.height)[1])
            self.canv.setFont('TimesR',10.2);self.canv.drawRightString(self.width,1.5+(self.h-10.2)/2,'('+tag+')')
        LOG['displays'].append(dict(id=self.ident,tags=self.tags,font_pt=round(self.fs,3),width_pt=round(self.w,3),height_pt=round(self.h,3),page=self.canv.getPageNumber()))

def paragraphs(text,sty='body'):
    text=re.sub(r'^%.*$','',text,flags=re.M)
    text=re.sub(r'\\(?:begingroup|endgroup|small)\b','',text)
    text=re.sub(r'\\noindent\b','',text)
    text=re.sub(r'\\(?:begin|end)\{center\}','',text)
    text=re.sub(r'\\setlength\{\\tabcolsep\}\{[^}]*\}|\\renewcommand\{\\arraystretch\}\{[^}]*\}','',text)
    out=[]
    for p in re.split(r'\n\s*\n',text):
        p=p.strip()
        if not p:continue
        if p in ('\\clearpage',):out.append(PageBreak());continue
        LOG['prose'].append(p)
        ps=ST['theorem'] if re.match(r'\\textbf\{(?:Lemma|Theorem|Proposition|Corollary)',p) else ST[sty]
        par=Paragraph(markup(p,ps.fontSize),ps)
        if p.startswith(r'\noindent\textbf{Table') or p.startswith(r'\textbf{Table'):
            par.keepWithNext=True
        if len(p)<200 and re.search(r'(?:use|gives|so|following)\s*$|:\s*$',p):par.keepWithNext=True
        out.append(par)
    return out

def table_flow(source):
    content=source[source.index('\n')+1:source.rindex('\\end{tabularx}')]
    content=re.sub(r'\\(?:toprule|midrule|bottomrule|addlinespace)\b','',content)
    rows=[];row=[];cell='';i=0;inmath=False
    while i<len(content):
        if content.startswith('\\(',i):inmath=True;cell+='\\(';i+=2;continue
        if content.startswith('\\)',i):inmath=False;cell+='\\)';i+=2;continue
        if not inmath and content.startswith('\\\\',i):
            row.append(cell.strip());rows.append(row);row=[];cell='';i+=2;continue
        if not inmath and content[i]=='&':row.append(cell.strip());cell='';i+=1;continue
        cell+=content[i];i+=1
    if cell.strip():raise ValueError('Unexpected last table cell '+cell)
    cols=len(rows[0]);index=len(LOG['tables'])
    widths=([WIDTH*.28,WIDTH*.72] if cols==2 else [WIDTH*.23,WIDTH*.385,WIDTH*.385] if cols==3 else [88,56,31,135,34,WIDTH-344] if cols==6 else [WIDTH/cols]*cols)
    cells=[]
    for ri,row in enumerate(rows):
        if len(row)!=cols:raise ValueError('Table ragged row')
        sty=ST['tablehead'] if ri==0 else ST['table']
        cells.append([Paragraph(markup(c,8.7 if cols==6 else sty.fontSize),sty) for c in row])
        LOG['prose'].extend(row)
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEABOVE',(0,0),(-1,0),.65,colors.black),('LINEBELOW',(0,0),(-1,0),.4,colors.black),('LINEBELOW',(0,-1),(-1,-1),.65,colors.black)]))
    t.spaceBefore=7;t.spaceAfter=10
    LOG['tables'].append(dict(rows=len(rows),columns=cols,widths=widths))
    return t

def tokenize(s):
    pat=re.compile(r'\\\[|\\begin\{(?:tabularx|enumerate|verbatim)\}|\\(?:section\*?|subsection)\{|\\appendix\b')
    pos=0
    while True:
        m=pat.search(s,pos)
        if not m:
            if s[pos:].strip():yield 'prose',s[pos:]
            break
        if s[pos:m.start()].strip():yield 'prose',s[pos:m.start()]
        marker=m.group(0)
        if marker=='\\[':
            end=s.index('\\]',m.end());yield 'display',s[m.end():end];pos=end+2
        elif marker.startswith('\\begin'):
            env=next(e for e in ('tabularx','enumerate','verbatim') if e in marker);end=s.index('\\end{'+env+'}',m.end())+len('\\end{'+env+'}')
            yield env,s[m.start():end];pos=end
        elif marker=='\\appendix':yield 'appendix','';pos=m.end()
        else:
            title,end=balanced(s,m.end()-1);yield ('sectionstar' if '*' in marker else 'subsection' if 'subsection' in marker else 'section'),title;pos=end

class Manuscript(BaseDocTemplate):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw);self.seen={};self.current_section=None
        frame=Frame(MARGIN,MARGIN,WIDTH,PAGE_H-2*MARGIN,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='academic',frames=[frame],onPage=self.decorate))
    def decorate(self,c,doc):
        c.saveState();page=doc.page
        c.setFillColor(colors.black);c.setFont('TimesR',10.909);c.drawCentredString(MARGIN+WIDTH/2,41.1107,str(page));c.restoreState()
    def afterFlowable(self,f):
        if getattr(f,'heading_key',None):
            key=f.heading_key;level=f.heading_level;text=f.getPlainText()
            self.canv.bookmarkPage(key);self.canv.addOutlineEntry(text,key,level=level,closed=(level>0))
            self.notify('TOCEntry',(level,text,self.page,key))

story=[]
meta=DATA['metadata']
story.append(Spacer(1,37.15))
story.append(Paragraph(html.escape(meta['title']),ST['title']))
story.append(Paragraph(html.escape(meta['subtitle']),ST['subtitle']))
story.append(Paragraph(meta['author'],ST['author']))
story.append(Spacer(1,8.89))
for email in meta['emails']:
    story.append(Paragraph('<link href="mailto:'+email+'">'+email+'</link>',ST['author']))
story.append(Spacer(1,26.75))
story.append(Paragraph('<b>'+('Abstract' if LANG=='en' else '摘要')+'</b>',style('abstract-title',fontName='TimesB',fontSize=9.963,leading=12,firstLineIndent=0,alignment=TA_CENTER,spaceAfter=5,keepWithNext=True)))
for kind,text in tokenize(abstract):
    if kind=='display':story.append(Display(text))
    elif kind=='prose':story.extend(paragraphs(text,'abstract'))
    else:raise ValueError('Unexpected abstract token')
story.append(Spacer(1,12))
toc_heading=style('toc-heading',fontName='TimesB',fontSize=14.35,leading=18,alignment=TA_LEFT,firstLineIndent=0,spaceBefore=17,spaceAfter=3.3,keepWithNext=False)
story.append(Paragraph('Contents' if LANG=='en' else '目录',toc_heading))
toc=TableOfContents()
toc.tableStyle=TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)])
toc.levelStyles=[style('toc-main',fontName='TimesB',fontSize=10.909,leading=13.55,alignment=TA_LEFT,firstLineIndent=0,spaceBefore=10,leftIndent=0,textColor=colors.blue),
                 style('toc-sub',fontName='TimesR',fontSize=10.909,leading=13.55,alignment=TA_LEFT,firstLineIndent=0,spaceBefore=0,leftIndent=16,textColor=colors.blue)]
toc.dotsMinLevel=1
story.append(toc);story.append(PageBreak())
section=0;sub=0;appendix=False
tokens=list(tokenize(body))
for ti,(kind,text) in enumerate(tokens):
    if kind=='appendix':appendix=True;section=0;continue
    if kind in ('section','sectionstar','subsection'):
        if kind=='section':section+=1;sub=0;num=chr(64+section) if appendix else str(section);label=((('Appendix ' if LANG=='en' else '附录 ')+num+'. ') if appendix else num+'  ')+text;level=0;key='section-'+num
        elif kind=='subsection':sub+=1;num=(chr(64+section) if appendix else str(section))+'.'+str(sub);label=num+' '+text;level=1;key='section-'+num
        else:label=text;level=0;key='acknowledgments'
        p=Paragraph(markup(label,14.35 if level==0 else 11.96),ST['h1'] if level==0 else ST['h2']);p.heading_key=key;p.heading_level=level
        LOG['headings'].append(dict(text=label,key=key,level=level));story.append(p)
    elif kind=='display':story.append(Display(text))
    elif kind=='prose':
        pars=paragraphs(text)
        if pars and isinstance(pars[-1],Paragraph) and ti+1<len(tokens) and tokens[ti+1][0]=='display':
            last_para=re.split(r'\n\s*\n',text.strip())[-1]
            if len(last_para)<450:pars[-1].keepWithNext=True
        story.extend(pars)
    elif kind=='tabularx':story.append(table_flow(text))
    elif kind=='verbatim':
        code=text[len('\\begin{verbatim}'):-len('\\end{verbatim}')].strip('\n')
        sty=style('code',fontName='Mono',fontSize=7.5,leading=10,alignment=TA_LEFT,firstLineIndent=0,spaceBefore=5,spaceAfter=7)
        assert all(pdfmetrics.stringWidth(line,'Mono',7.5)<=WIDTH for line in code.splitlines()),'Code line exceeds text width'
        story.append(Preformatted(code,sty))
    elif kind=='enumerate':
        inner=text[len('\\begin{enumerate}'):-len('\\end{enumerate}')]
        items=[x.strip() for x in inner.split('\\item')[1:]]
        for i,x in enumerate(items,1):story.append(Paragraph(str(i)+'. '+markup(x),style('list',leftIndent=17,firstLineIndent=-17,spaceAfter=5)))
    else:raise ValueError(kind)
def markup_from_inlines(nodes):
    out=[]
    for n in nodes:
        kind=n['type']
        if kind in ('text','code'):
            escaped=html.escape(n['text'])
            for dash in ('–','—'):escaped=escaped.replace(dash,'<font name="Accent">'+dash+'</font>')
            out.append(escaped)
        elif kind in ('strong','emphasis'):
            tag='b' if kind=='strong' else 'i'
            out.append(f'<{tag}>'+markup_from_inlines(n['inlines'])+f'</{tag}>')
        elif kind=='link':out.append('<link href="'+html.escape(n['url'],quote=True)+'" color="#0000ff">'+markup_from_inlines(n['inlines'])+'</link>')
        else:raise ValueError('Unexpected bibliography inline '+kind)
    return ''.join(out)

p=Paragraph('References' if LANG=='en' else '参考文献',ST['h1']);p.heading_key='references';p.heading_level=0;story.append(p)
for ref in DATA['references']:
    text=f'<a name="ref-{ref["number"]}"/>[{ref["number"]}] '+markup_from_inlines(ref['inlines'])
    story.append(Paragraph(text,ST['reference']))
OUT.parent.mkdir(parents=True,exist_ok=True)
doc=Manuscript(str(OUT),pagesize=A4,title=meta['title'],author=meta['author'],subject=meta['subtitle'],pageCompression=1,initialFontName='TimesR',initialFontSize=FONT)
doc.multiBuild(story,canvasmaker=MathCanvas)
# ReportLab uses multiple passes to resolve contents; keep final display placements only.
last={}
for d in LOG['displays']:last[(d['id'],tuple(d['tags']))]=d
LOG['display_placements']=list(last.values());LOG['math_source_occurrences']=len(math_inputs)
LOG['numbered_equations']=sorted({tag for x in math_inputs for tag in x['tags']})
LOG['pdf_path']=OUT.relative_to(ROOT).as_posix() if OUT.is_relative_to(ROOT) else OUT.name;LOG['pdf_sha256']=hashlib.sha256(OUT.read_bytes()).hexdigest();LOG['math_render_summary']=json.loads((CACHE/'render-summary.json').read_text(encoding='utf8'))
(BUILD/('pdf-build-'+LANG+'.json')).write_text(json.dumps(LOG,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'pdf':str(OUT.resolve()),'bytes':OUT.stat().st_size,'math_occurrences':len(math_inputs),'display_occurrences':sum(x['display'] for x in math_inputs),'numbered':len(LOG['numbered_equations']),'tables':len(LOG['tables']),'small_displays':[d for d in LOG['display_placements'] if d['font_pt']<9.5]},indent=2))
