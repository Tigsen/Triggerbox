"""Convert a Word (.docx) guide into Markdown that Claude can read quickly.

Usage: python3 tools/docx_to_md.py <input.docx> <output.md>
Images are extracted to an "images" folder next to the output file.
The original .docx is never modified.
"""
import sys, re, shutil, os, tempfile, zipfile, xml.etree.ElementTree as ET
docx, out_md = sys.argv[1:3]
img_rel = 'images'
img_dir = os.path.join(os.path.dirname(os.path.abspath(out_md)), img_rel)
src = tempfile.mkdtemp()
with zipfile.ZipFile(docx) as z:
    for m in z.namelist():
        if m.startswith('word/') and '..' not in m:
            z.extract(m, src)
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
A='{http://schemas.openxmlformats.org/drawingml/2006/main}'
R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
rels={r.get('Id'):r.get('Target') for r in ET.parse(src+'/word/_rels/document.xml.rels').getroot()}
# numbering: numId -> ilvl -> fmt
num=ET.parse(src+'/word/numbering.xml').getroot()
absfmt={}
for a in num.findall(W+'abstractNum'):
    absfmt[a.get(W+'abstractNumId')]={l.get(W+'ilvl'):l.find(W+'numFmt').get(W+'val') for l in a.findall(W+'lvl') if l.find(W+'numFmt') is not None}
numfmt={n.get(W+'numId'):absfmt.get(n.find(W+'abstractNumId').get(W+'val'),{}) for n in num.findall(W+'num')}
HEAD={'Title':'#','Heading1':'#','Heading2':'##','Heading3':'###','Heading4':'###','Heading5':'###','Heading6':'####'}
def on(rpr,tag):
    if rpr is None: return False
    e=rpr.find(W+tag); return e is not None and e.get(W+'val') not in ('0','false')
os.makedirs(img_dir,exist_ok=True)
lines=[]; counters={}; imgn=0
body=ET.parse(src+'/word/document.xml').getroot().find(W+'body')
for p in body.iter(W+'p'):
    ppr=p.find(W+'pPr'); style=''; numid=None; ilvl=0
    if ppr is not None:
        s=ppr.find(W+'pStyle'); style=s.get(W+'val') if s is not None else ''
        n=ppr.find(W+'numPr')
        if n is not None and n.find(W+'numId') is not None:
            numid=n.find(W+'numId').get(W+'val'); ilvl=int(n.find(W+'ilvl').get(W+'val')) if n.find(W+'ilvl') is not None else 0
            if numid=='0': numid=None
    segs=[]; imgs=[]; allbold=True; hastext=False
    for r in p.iter(W+'r'):
        rpr=r.find(W+'rPr'); b=on(rpr,'b'); i=on(rpr,'i')
        for c in r:
            if c.tag==W+'t' and c.text:
                t=c.text
                if t.strip(): hastext=True; allbold&=b
                segs.append((t,b,i))
            elif c.tag in (W+'br',W+'cr'): segs.append(('\n',False,False))
            elif c.tag==W+'tab': segs.append((' ',False,False))
        for bl in r.iter(A+'blip'):
            tgt=rels[bl.get(R+'embed')]; imgn+=1
            name=os.path.basename(tgt); shutil.copy(src+'/word/'+tgt, img_dir+'/'+name); imgs.append(name)
    # build text with inline emphasis, merge adjacent same-format segments
    merged=[]
    for t,b,i in segs:
        if merged and merged[-1][1:]==(b,i) and t!='\n' and merged[-1][0]!='\n': merged[-1]=(merged[-1][0]+t,b,i)
        else: merged.append((t,b,i))
    heading=HEAD.get(style)
    pseudo = not heading and numid is None and hastext and allbold
    parts=[]
    for t,b,i in merged:
        if t=='\n': parts.append('\n'); continue
        if heading or pseudo or not t.strip(): parts.append(t); continue
        lead=t[:len(t)-len(t.lstrip())]; trail=t[len(t.rstrip()):]; core=t.strip()
        if b: core='**'+core+'**'
        if i and not b: core='*'+core+'*'
        parts.append(lead+core+trail)
    text=''.join(parts)
    chunks=[c.strip() for c in text.split('\n')]
    chunks=[re.sub(r'  +',' ',c) for c in chunks if c]
    if heading:
        for c in chunks: lines+=['',heading+' '+c,'']
    elif chunks:
        if numid is not None:
            fmt=numfmt.get(numid,{}).get(str(ilvl),'bullet')
            key=(numid,ilvl); 
            if fmt=='decimal':
                counters[key]=counters.get(key,0)+1; mark=f'{counters[key]}.'
            else: mark='-'
            ind='   '*ilvl
            lines.append(f'{ind}{mark} {chunks[0]}')
            for c in chunks[1:]: lines.append(f'{ind}   {c}')
        else:
            for c in chunks:
                lines+=['', f'**{c}**' if pseudo else c, '']
    for name in imgs:
        lines+=['',f'![Screenshot]({img_rel}/{name})','']
md='\n'.join(lines)
md=re.sub(r'\n{3,}','\n\n',md).strip()+'\n'
open(out_md,'w').write(md)
shutil.rmtree(src)
print(f'Wrote {out_md} ({imgn} images)')
