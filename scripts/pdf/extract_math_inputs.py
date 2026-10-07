"""Extract every display and inline formula without changing internal whitespace."""
from pathlib import Path
import argparse,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_SOURCE=ROOT.parent/'english-overleaf-20261005'

def strip_tags(source):
    out=[];tags=[];cursor=0
    for match in re.finditer(r'\\tag\*?\s*\{',source):
        start=match.start()
        if start<cursor:continue
        slashes=0;k=start-1
        while k>=0 and source[k]=='\\':slashes+=1;k-=1
        if slashes%2:continue
        arg_start=match.end();depth=1;k=arg_start
        while k<len(source) and depth:
            if source[k]=='\\' and k+1<len(source) and source[k+1] in '{}':k+=2;continue
            if source[k]=='{':depth+=1
            elif source[k]=='}':depth-=1
            k+=1
        if depth:raise ValueError('Unbalanced tag')
        out.append(source[cursor:start]);tags.append(source[arg_start:k-1]);cursor=k
    out.append(source[cursor:])
    return ''.join(out).strip(),tags

def canonical(tex,display):
    clean,tags=strip_tags(tex) if display else (tex.strip(),[])
    ident='m'+hashlib.sha256((('D' if display else 'I')+'\0'+clean).encode()).hexdigest()[:20]
    return ident,clean,tags

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=DEFAULT_SOURCE)
    parser.add_argument('--output',type=Path,default=ROOT/'math-inputs.json')
    args=parser.parse_args();rows=[];sources=[]
    files=[args.source/'abstract.tex',*sorted((args.source/'parts').glob('*.tex'))]
    for p in files:
        s=p.read_text(encoding='utf8');sources.append({'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        for match in re.finditer(r'\\\[(.*?)\\\]|\\\((.*?)\\\)',s,re.S):
            display=match.group(1) is not None
            tex=match.group(1) if display else match.group(2)
            ident,clean,tags=canonical(tex,display)
            rows.append({'id':ident,'tex':tex,'display':display,'tags':tags,
                'source':p.name,'line':s[:match.start()].count('\n')+1})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    report={'input_path':str(args.output.resolve()),'input_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
        'sources':sources,'occurrences':len(rows),'displays':sum(r['display'] for r in rows),
        'inline':sum(not r['display'] for r in rows),'unique':len({r['id'] for r in rows}),
        'id_rule':"m + sha256((display ? 'D' : 'I') + NUL + cleanTex)[:20]",'cleaning':'Strip outer whitespace and display tags only; retain internal whitespace.'}
    args.output.with_suffix('.extraction.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report))

if __name__=='__main__':main()
