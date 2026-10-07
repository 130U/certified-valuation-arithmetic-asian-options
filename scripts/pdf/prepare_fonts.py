"""Subset fixed Noto Serif SC instances for the manuscript's Chinese characters.

The PDF builder uses the checked-in subsets and does not need this tool.
Regenerate them after adding characters to the Chinese source.
"""
from pathlib import Path
import argparse,hashlib,json
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset

ROOT=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--source-font',type=Path,required=True)
ap.add_argument('--expected-sha256',required=True)
a=ap.parse_args()
assert hashlib.sha256(a.source_font.read_bytes()).hexdigest()==a.expected_sha256
texts=''.join(p.read_text(encoding='utf8') for p in (ROOT/'manuscript').glob('*.tex'))
texts+='算术亚式期权的认证估值共同高斯平滑与投影误差界摘要目录附录参考文献'
unicodes={ord(c) for c in texts}|set(range(32,127))|{0x2013,0x2014,0x2212}
out=ROOT/'assets/fonts';out.mkdir(parents=True,exist_ok=True)
files=[]
for label,weight in [('Regular',400),('Bold',700)]:
    font=TTFont(a.source_font)
    missing=sorted(unicodes-set(font.getBestCmap()))
    # TeX control whitespace is never rendered as a glyph.
    missing=[c for c in missing if not chr(c).isspace()]
    assert not missing, missing
    opt=subset.Options();opt.name_IDs=['*'];opt.name_legacy=True;opt.name_languages=['*']
    sub=subset.Subsetter(options=opt);sub.populate(unicodes=unicodes);sub.subset(font)
    font=instantiateVariableFont(font,{'wght':weight},inplace=True)
    font['head'].modified=font['head'].created
    p=out/('NotoSerifSC-'+label+'.ttf');font.save(p)
    files.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'weight':weight})
receipt={'source_sha256':a.expected_sha256,'fonttools':'4.61.1','unicode_count':len(unicodes),'files':files}
(out/'noto-subset.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps(receipt))
