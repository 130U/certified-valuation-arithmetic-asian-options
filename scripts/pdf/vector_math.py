"""Draw MathJax SVG glyph outlines as native PDF paths (no raster formulas)."""
from pathlib import Path
import re, xml.etree.ElementTree as ET
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor

NUM=r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?'

def draw_path(c,d):
    tok=re.findall(r'[A-Za-z]|'+NUM,d); i=0; cmd=None; x=y=0.; sx=sy=0.; prev=None; cp=None
    p=c.beginPath()
    while i<len(tok):
        if tok[i].isalpha(): cmd=tok[i];i+=1
        if cmd is None: raise ValueError('Missing SVG path command')
        op=cmd.upper(); rel=cmd.islower()
        if op=='Z':
            p.close();x,y=sx,sy;prev=op;cp=None;cmd=None;continue
        n={'M':2,'L':2,'H':1,'V':1,'C':6,'S':4,'Q':4,'T':2}.get(op)
        if n is None: raise ValueError('Unsupported SVG path command '+cmd)
        a=list(map(float,tok[i:i+n]));i+=n
        if rel:
            if op=='H': a[0]+=x
            elif op=='V': a[0]+=y
            else:
                for k in range(0,n,2):a[k]+=x;a[k+1]+=y
        if op=='M':
            x,y=a;p.moveTo(x,y);sx,sy=x,y;cmd='l' if rel else 'L';cp=None
        elif op=='L': x,y=a;p.lineTo(x,y);cp=None
        elif op=='H': x=a[0];p.lineTo(x,y);cp=None
        elif op=='V': y=a[0];p.lineTo(x,y);cp=None
        elif op=='C':
            p.curveTo(*a);x,y=a[-2:];cp=tuple(a[2:4])
        elif op=='S':
            c1=(2*x-cp[0],2*y-cp[1]) if prev in ('C','S') and cp else (x,y)
            p.curveTo(*c1,*a);x,y=a[-2:];cp=tuple(a[:2])
        elif op in ('Q','T'):
            if op=='Q': qx,qy,nx,ny=a
            else:
                qx,qy=(2*x-cp[0],2*y-cp[1]) if prev in ('Q','T') and cp else (x,y)
                nx,ny=a
            p.curveTo(x+2*(qx-x)/3,y+2*(qy-y)/3,nx+2*(qx-nx)/3,ny+2*(qy-ny)/3,nx,ny)
            x,y=nx,ny;cp=(qx,qy)
        prev=op
    c.drawPath(p,stroke=0,fill=1)

def transform(c,s):
    for name,args in re.findall(r'(\w+)\s*\(([^)]*)\)',s):
        a=list(map(float,re.findall(NUM,args)))
        if name=='translate':c.translate(a[0],a[1] if len(a)>1 else 0)
        elif name=='scale':c.scale(a[0],a[1] if len(a)>1 else a[0])
        elif name=='matrix':c.transform(*a)
        elif name=='rotate':
            if len(a)==3:c.translate(a[1],a[2]);c.rotate(a[0]);c.translate(-a[1],-a[2])
            else:c.rotate(a[0])
        else:raise ValueError('Unsupported SVG transform '+name)

def walk(c,e,root=False):
    tag=e.tag.split('}')[-1]
    if tag in ('title','desc','defs'):return
    c.saveState()
    if e.get('transform'):transform(c,e.get('transform'))
    if e.get('stroke-width') is not None:c.setLineWidth(float(e.get('stroke-width')))
    if e.get('stroke') not in (None,'none','currentColor'):c.setStrokeColor(HexColor(e.get('stroke')))
    if tag=='svg' and not root:
        x=float(e.get('x',0));y=float(e.get('y',0));w=float(e.get('width'));h=float(e.get('height'))
        c.translate(x,y)
        clip=c.beginPath();clip.rect(0,0,w,h);c.clipPath(clip,stroke=0,fill=0)
        vx,vy,vw,vh=map(float,e.get('viewBox').split());c.scale(w/vw,h/vh);c.translate(-vx,-vy)
    fill=e.get('fill')
    if fill and fill not in ('none','currentColor'): c.setFillColor(HexColor(fill))
    if tag=='path':draw_path(c,e.attrib['d'])
    elif tag=='rect':c.rect(float(e.get('x',0)),float(e.get('y',0)),float(e.get('width')),float(e.get('height')),stroke=int(e.get('stroke') not in (None,'none') or e.get('fill')=='none'),fill=int(e.get('fill')!='none'))
    elif tag=='line':c.line(float(e.get('x1',0)),float(e.get('y1',0)),float(e.get('x2',0)),float(e.get('y2',0)))
    elif tag not in ('svg','g'):raise ValueError('Unsupported SVG element '+tag)
    for child in e:walk(c,child)
    c.restoreState()

class MathCanvas(Canvas):
    math_meta={};math_dir=None
    def __init__(self,*args,**kwargs):
        kwargs['invariant']=1
        super().__init__(*args,**kwargs)
    def _form(self,ident):
        name='math_'+ident
        if not self.hasForm(name):
            row=self.math_meta[ident];x,y,w,h=row['viewBox']
            if row.get('base'):
                base=self.math_meta[row['base']];baseform=self._form(row['base'])
                self.beginForm(name,0,0,w,h)
                self.saveState();self.translate(0,row['depthUnits']-base['depthUnits']);self.doForm(baseform);self.restoreState()
                self.setFillColorRGB(0,0,0);self.setFont(row['suffix_font'],1000)
                self.drawString(base['widthUnits'],row['depthUnits'],row['suffix'])
                self.endForm();return name
            self.beginForm(name,0,0,w,h)
            self.setFillColorRGB(0,0,0)
            self.translate(0,h);self.scale(1,-1);self.translate(-x,-y)
            walk(self,ET.parse(Path(self.math_dir)/(ident+'.svg')).getroot(),root=True)
            self.endForm()
        return name
    def math(self,ident,x,y,w,h):
        row=self.math_meta[ident];name=self._form(ident)
        self.saveState();self.translate(x,y);self.scale(w/row['widthUnits'],h/row['heightUnits']);self.doForm(name);self.restoreState()
        # The visible formula remains a vector outline. A separate invisible TeX
        # text layer supports searching and copying the original mathematical input.
        base=self.math_meta.get(row.get('base'),row)
        tex=base.get('tex','')
        if tex:
            tex=re.sub(r'\s+',' ',tex).strip()
            self.saveState()
            t=self.beginText(x,y+row['depthUnits']*h/row['heightUnits'])
            t.setFont('Helvetica',10.909);t.setTextRenderMode(3)
            t.setHorizScale(100*w/max(pdfmetrics.stringWidth(tex,'Helvetica',10.909),1))
            t.textLine(tex);t.setTextRenderMode(0);self.drawText(t)
            self.restoreState()
    def drawImage(self,image,x,y,width=None,height=None,**kwargs):
        file=getattr(image,'fileName',image)
        if isinstance(file,(str,Path)):
            ident=Path(file).stem
            if ident in self.math_meta:
                self.math(ident,x,y,width,height);return (width,height)
        return super().drawImage(image,x,y,width=width,height=height,**kwargs)
