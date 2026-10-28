"""Recover actual Bengali Unicode from embedded shaped glyphs, preserving reading order."""
import fitz,re,unicodedata,io,json
from fontTools.ttLib import TTFont
from fontTools.agl import toUnicode
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def font_map(font):
 names=font.getGlyphOrder();maps={v:chr(k) for k,v in (font.getBestCmap() or {}).items()}
 # Explicit Unicode glyph names remain useful when PDFs subset away cmap entries.
 for name in names:
  stem=name.split('.')[0];m=re.match(r'uni((?:[0-9A-Fa-f]{4})+)$',stem)
  if m:maps[name]=''.join(chr(int(x,16)) for x in re.findall('.{4}',m[1]))
  elif stem in maps:maps[name]=maps[stem]
  elif (u:=toUnicode(stem)):maps[name]=u
  if 'raphala' in name.lower():maps[name]='্র'
  if 'baphala' in name.lower():maps[name]='্ব'
  if 'reph' in name.lower():maps[name]='র্'
  if name.startswith('uni09AF.pstf'):maps[name]='্য'
 # GSUB tables map shaped conjuncts back to their Unicode components.
 if 'GSUB' in font:
  lookups=font['GSUB'].table.LookupList.Lookup
  for _ in range(12):
   changed=0
   for lookup in lookups:
    for sub in lookup.SubTable:
     if hasattr(sub,'ExtSubTable'):sub=sub.ExtSubTable
     for a,b in getattr(sub,'mapping',{}).items():
      if isinstance(b,str) and a in maps and b not in maps:maps[b]=maps[a];changed+=1
     for a,values in getattr(sub,'alternates',{}).items():
      if a in maps:
       for b in values:
        if b not in maps:maps[b]=maps[a];changed+=1
     for a,ligs in getattr(sub,'ligatures',{}).items():
      for lig in ligs:
       parts=[a]+lig.Component
       if lig.LigGlyph not in maps and all(x in maps for x in parts):maps[lig.LigGlyph]=''.join(maps[x] for x in parts);changed+=1
   if not changed:break
 return {i:maps.get(n,'') for i,n in enumerate(names)}

class Reader:
 def __init__(self,path):
  self.doc=fitz.open(path);self.fonts={};self.cache={}
  modern=fitz.open(ROOT/'dist/pdfs/n5-vocabulary-new-typed-list.pdf')
  self.modern=font_map(TTFont(io.BytesIO(modern.extract_font(6)[3])))
  self.old=font_map(TTFont('/tmp/NotoSansBengali-old.ttf'))
  for page in self.doc:
   for f in page.get_fonts(full=True):
    name=f[3].split('+')[-1]
    if name in self.fonts or not ('Bengali' in name or name.startswith('BN')):continue
    raw=self.doc.extract_font(f[0])[3]
    if not raw:continue
    font=TTFont(io.BytesIO(raw));mapping=font_map(font)
    # Retained GIDs in subset Bengali fonts match these full official fonts.
    if name.startswith('BN'):mapping={**self.modern,**{k:v for k,v in mapping.items() if v}}
    elif name.startswith('Noto-Sans-Bengali'):mapping={**self.old,**{k:v for k,v in mapping.items() if v}}
    self.fonts[name]=mapping;self.fonts[name.replace(' ','').replace('-','')]=mapping
 def pieces(self,n):
  if n in self.cache:return self.cache[n]
  rows=[]
  for tr in self.doc[n].get_texttrace():
   font=tr['font'];mapping=self.fonts.get(font) or self.fonts.get(font.replace(' ','').replace('-',''));chars=[];segments=[];last_y=None
   for uni,gid,origin,bbox in tr['chars']:
    if mapping and gid<0:continue
    text=mapping.get(gid,'') if mapping else chr(uni) if 0<=uni<=0x10ffff else ''
    if not text:text=chr(uni) if uni!=65533 and uni>=32 else ''
    x,y=origin
    if last_y is not None and abs(y-last_y)>4 and chars:segments.append(chars);chars=[]
    chars.append((text,x,y,bbox));last_y=y
   if chars:segments.append(chars)
   for chars in segments:
    text=''.join(c[0] for c in chars)
    text=unicodedata.normalize('NFC',text.replace('ো','ো').replace('ৌ','ৌ')).replace('\u200b','')
    if not text.strip():continue
    xs=[c[3][0] for c in chars];ys=[c[3][1] for c in chars];xe=[c[3][2] for c in chars];ye=[c[3][3] for c in chars]
    rows.append(dict(text=text,x=min(xs),y=sorted(c[2] for c in chars)[len(chars)//2],rect=(min(xs),min(ys),max(xe),max(ye)),font=font,size=tr['size'],seq=tr['seqno']))
  self.cache[n]=rows;return rows
 def text(self,n,rect=None):
  rows=self.pieces(n)
  if rect:
   x0,y0,x1,y1=rect;rows=[r for r in rows if x0<=r['x']<x1 and y0<=r['y']<y1]
  lines=[]
  for r in sorted(rows,key=lambda r:(round(r['y']/3),r['x'],r['seq'])):
   if lines and abs(lines[-1][0]-r['y'])<3:
    lines[-1][1].append(r)
   else:lines.append([r['y'],[r]])
  return '\n'.join(' '.join(r['text'].strip() for r in sorted(line,key=lambda r:r['x'])) for y,line in lines)
if __name__=='__main__':
 import sys
 r=Reader(sys.argv[1]);print(r.text(int(sys.argv[2]) if len(sys.argv)>2 else 1))
