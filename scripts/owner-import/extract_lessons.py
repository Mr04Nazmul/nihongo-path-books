from decode_pdf import Reader,ROOT
import json,re,unicodedata
from pathlib import Path
OCR=Path(__file__).parent/'ocr';UPLOAD=ROOT.parent/'upload';OUT=ROOT/'dist/data'
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff]')
BN=re.compile(r'[\u0980-\u09ff]')

def clean(s):
 s=unicodedata.normalize('NFC',s).replace('্্','্').replace('\u200b','').replace('\x00','।')
 s=re.sub(r' +([,;।!?])',r'\1',s)
 return re.sub(r'[ \t]+',' ',s).strip()

def lines(items):
 groups=[]
 for t,x,y in sorted(items,key=lambda x:(x[2],x[1])):
  near=next((g for g in groups[-3:] if abs(g[0]-y)<5),None)
  if near:near[1].append((x,t))
  else:groups.append([y,[(x,t)]])
 return [clean(' '.join(t for x,t in sorted(g))) for y,g in groups]

class Source(Reader):
 def ocr(self,n,rect):
  p=OCR/(Path(self.doc.name).stem+'-'+str(n)+'.json')
  if not p.exists():return None
  ws=json.loads(p.read_text());x0,y0,x1,y1=rect
  return [w for w in ws if x0<=w['x']+w['w']/2<x1 and y0<=w['y']+w['h']/2<y1]
 def bn(self,n,rect):
  ws=self.ocr(n,rect)
  if ws is not None:return clean(' '.join(lines([(w['text'],w['x'],w['y']+w['h']-2) for w in ws])))
  return clean(' '.join(self.text(n,rect).splitlines()))
 def jp(self,n,rect):
  x0,y0,x1,y1=rect
  return lines([(p['text'],p['x'],p['y']) for p in self.pieces(n) if x0<=p['x']<x1 and y0<=p['y']<y1 and JA.search(p['text']) and ('JP' in p['font'] or 'Droid' in p['font'])])
 def rich(self,n,rect):
  ws=self.ocr(n,rect)
  if ws is None:return self.text(n,rect)
  x0,y0,x1,y1=rect;items=[(w['text'],w['x'],w['y']+w['h']-2) for w in ws if BN.search(w['text'])]
  for tr in self.doc[n].get_texttrace():
   mapping=self.fonts.get(tr['font']) or self.fonts.get(tr['font'].replace(' ','').replace('-',''));run=[]
   def flush():
    if run:
     items.append((''.join(z[0] for z in run),run[0][1],run[0][2]));run.clear()
   for uni,gid,origin,bbox in tr['chars']:
    text=mapping.get(gid,'') if mapping else (chr(uni) if uni>=0 else '')
    if gid<0 or BN.search(text) or not(x0<=origin[0]<x1 and y0<=origin[1]<y1):flush();continue
    if run and abs(origin[1]-run[-1][2])>4:flush()
    run.append((text,origin[0],origin[1]))
   flush()
  return '\n'.join(lines(items))

def anchors(page,x0,x1,miny=80,digits=None):
 return sorted([w for w in page.get_text('words') if x0<=w[0]<=x1 and w[1]>miny and w[1]<790 and re.fullmatch(r'\d{'+str(digits)+'}' if digits else r'\d{1,4}',w[4])],key=lambda w:w[1])

def record(level,kind,serial,**kw):
 return dict(id=f'own-{level.lower()}-{kind}-{serial:04d}',level=level,source_type='owner-text',**kw)

books={l:{k:[] for k in ['grammar','vocab','kanji']} for l in ['N5','N4','N3','N2']};example_words=[];audit=[]
def add(level,kind,source,serial,**data):
 e=record(level,kind,len(books[level][kind])+1,**data);books[level][kind].append(e);audit.append(dict(id=e['id'],file=source,serial=serial));return e

def vocab_table(file,level,style='n5',example=False):
 s=Source(UPLOAD/file)
 for n,p in enumerate(s.doc):
  if style=='n5':
   if 'Japanese & Reading' not in p.get_text():continue
   if not example and 'Kanji & Reading' in p.get_text():continue
   aa=anchors(p,36,38,95);cols=[(60,235),(239,409),(414,565)]
  elif style=='n4':
   aa=anchors(p,47,49,55,4);cols=[(80,232),(235,332),(335,560)]
  else:aa=anchors(p,44,59,35);cols=[(69,140),(141,217),(218,299),(301,423),(425,559)]
  for i,a in enumerate(aa):
   y0=a[1]-6;y1=(aa[i+1][1]-6) if i+1<len(aa) else min(805,p.rect.height-30)
   if style=='n4':
    word=' '.join(s.jp(n,(*cols[0][:1],0,0,0))) if False else ' '.join(s.jp(n,(80,y0,232,y1)));reading=' '.join(s.jp(n,(235,y0,332,y1)));meaning=s.bn(n,(335,y0,560,y1));en=''
   elif style=='n5':
    jp=s.jp(n,(60,y0,235,y1));word=jp[0] if jp else '';reading=' '.join(jp[1:]);meaning=s.bn(n,(239,y0,409,y1));en=clean(s.text(n,(414,y0,565,y1)).replace('\n',' '))
   else:
    word=' '.join(s.jp(n,(69,y0,140,y1)));read=s.jp(n,(141,y0,217,y1));reading=' '.join(read);meaning=s.bn(n,(425,y0,559,y1));en=clean(s.text(n,(301,y0,423,y1)).replace('\n',' '))
   if not word:word=clean(s.text(n,(cols[0][0],y0,cols[0][1],y1)).replace('\n',' '))
   if not word:continue
   data=dict(word=word,reading=reading,meaning=meaning,english=en)
   if example:example_words.append(data)
   else:add(level,'vocab',file,int(a[4]),**data)

vocab_table('N5_Vocabulary_New_Typed_List(1).pdf','N5')
vocab_table('N4_Vocabulary_Bangla(1).pdf','N4','n4')
for f in ['JLPT_N2_Vocab_Vol1_Verbs_and_Nouns.pdf','JLPT_N2_Vocab_Vol2_Adverbs_and_Adjectives.pdf','JLPT_N2_Vocab_Vol3_Business_and_Society_Nouns.pdf']:vocab_table(f,'N2','n2')
# N3 source uses two independent columns of word cards.
f='N3_Vocabulary_Bangla_Typed.pdf';s=Source(UPLOAD/f)
for n,p in enumerate(s.doc):
 for b in p.get_text('blocks'):
  m=re.match(r'^(\d{4})\s*·',b[4])
  if not m:continue
  x0=33 if b[0]<300 else 303;x1=x0+258;y0=b[1]-3;y1=min(y0+78,800)
  jp=s.jp(n,(x0,y0,x1,y1));word=' '.join(jp);meaning=s.bn(n,(x0,y0+22,x1,y1))
  if word:add('N3','vocab',f,int(m[1]),word=word,reading=word if not re.search(r'[\u3400-\u9fff]',word) else '',meaning=meaning,english='')
# Sort N3 card source by its printed serial, rather than geometric column order.
serials={x['id']:x['serial'] for x in audit};books['N3']['vocab'].sort(key=lambda x:serials[x['id']])

# N5 grammar: table rows, only the actual teaching cells.
f='N5_Grammar_Bangla(1).pdf';s=Source(UPLOAD/f)
for n,p in enumerate(s.doc):
 aa=anchors(p,47,49,120,3)
 for i,a in enumerate(aa):
  y0=a[1]-6;y1=aa[i+1][1]-6 if i+1<len(aa) else 790
  pattern=clean(s.text(n,(80,y0,222,y1)).replace('\n',' '));meaning=s.bn(n,(225,y0,358,y1));jp=s.jp(n,(360,y0,560,y1));bn=s.bn(n,(360,y0,560,y1))
  add('N5','grammar',f,int(a[4]),pattern=pattern,meaning=meaning,formation=pattern,explanation=meaning,examples=[dict(ja=' '.join(jp),bn=bn)] if jp else [])
# N4 grammar: a pattern, paragraph, English gloss, example and Bengali translation per card.
f='N4_Grammar_Lessons_26_50_Typed(1).pdf';s=Source(UPLOAD/f)
for n,p in enumerate(s.doc):
 blocks=p.get_text('blocks');aa=[b for b in blocks if re.match(r'^\d{3}\u3000',b[4])]
 for i,a in enumerate(aa):
  m=re.match(r'^(\d{3})\u3000',a[4]);y0=a[1]-2;y1=aa[i+1][1]-6 if i+1<len(aa) else 790
  inner=[b for b in blocks if b[1]>a[1]+6 and b[1]<y1]
  pattern=clean(a[4][m.end():].replace('\n',' '))
  jpblocks=[b for b in inner if '。' in b[4] and JA.search(b[4])]
  ex=jpblocks[-1] if jpblocks else None
  if ex:
   explanation=clean(s.rich(n,(40,a[3]+1,555,ex[1]-3)).replace('\n',' '));jp=' '.join(s.jp(n,(40,ex[1]-2,555,ex[3]+1)));bn=s.bn(n,(40,ex[3]+1,555,y1));examples=[dict(ja=jp,bn=bn)]
  else:explanation=clean(s.rich(n,(40,a[3]+1,555,y1)).replace('\n',' '));examples=[]
  meaning=explanation.split('।')[0]+'।' if explanation else pattern
  add('N4','grammar',f,int(m[1]),pattern=pattern,meaning=meaning,formation=pattern,explanation=explanation,examples=examples)
# N3/N2 grammar editions contain explicit teaching units with two examples.
for level,f in [('N3','N3_Grammar_Bangla.pdf'),('N2','N2_Grammar_Bangla.pdf')]:
 s=Source(UPLOAD/f)
 for n,p in enumerate(s.doc):
  blocks=p.get_text('blocks');aa=[b for b in blocks if re.match(r'^UNIT \d{3}',b[4])]
  for i,a in enumerate(aa):
   serial=int(re.search(r'UNIT (\d{3})',a[4])[1]);y1=aa[i+1][1]-5 if i+1<len(aa) else 790
   text=s.text(n,(35,a[3]+1,565,y1));parts=text.splitlines();pattern=' '.join(line for line in a[4].splitlines()[1:] if JA.search(line)) or (parts.pop(0) if parts else '');text='\n'.join(parts)
   formation=re.search(r'গঠন\s*:\s*(.*?)(?=ব্যবহার\s*:|$)',text,re.S)
   usage=re.search(r'ব্যবহার\s*:\s*(.*?)(?=①|$)',text,re.S)
   meaning=clean(text.split('গঠন')[0].replace('\n',' '));examples=[]
   for seg in re.split('[①②]',text)[1:]:
    ls=seg.strip().splitlines();ja=[];bn=[]
    for line in ls:
     (ja if JA.search(line) and not BN.search(line) else bn).append(line)
    examples.append(dict(ja=clean(' '.join(ja)),bn=clean(' '.join(bn))))
   add(level,'grammar',f,serial,pattern=pattern,meaning=meaning,formation=clean(formation[1].replace('\n',' ')) if formation else pattern,explanation=clean(usage[1].replace('\n',' ')) if usage else meaning,examples=examples)
# N2 master supplement: retain its actual supplied rows, not the cover's advertised count.
f='JLPT_N2_Complete_Grammar_Master_Book.pdf';s=Source(UPLOAD/f)
for n,p in enumerate(s.doc):
 aa=anchors(p,44,59,40)
 for i,a in enumerate(aa):
  y0=a[1]-5;y1=aa[i+1][1]-5 if i+1<len(aa) else 810
  pattern=' '.join(s.jp(n,(69,y0,170,y1)));middle=s.rich(n,(173,y0,300,y1));example=' '.join(s.jp(n,(302,y0,560,y1)));bn=s.bn(n,(302,y0,560,y1));meaning=s.bn(n,(173,y0,300,y1))
  formation=re.search(r'Form:\s*(.*?)(?=ENG:|বাংলা|$)',middle,re.S)
  if pattern:add('N2','grammar',f,int(a[4]),pattern=pattern,meaning=clean(re.sub(r'.*?বাংলা\s*:\s*','',meaning)),formation=clean(formation[1].replace('\n',' ')) if formation else pattern,explanation=clean(re.sub(r'.*?বাংলা\s*:\s*','',meaning)),examples=[dict(ja=example,bn=clean(re.sub(r'^বাংলা\s*:\s*','',bn)))] if example else [])

# N5 core kanji table; the source's following word table supplies examples.
f='N5_Kanji_New_Typed_List(1).pdf';s=Source(UPLOAD/f)
for n,p in enumerate(s.doc):
 if 'Kanji & Reading' not in p.get_text():continue
 aa=anchors(p,36,38,80)
 for i,a in enumerate(aa):
  y0=a[1]-5;y1=aa[i+1][1]-5 if i+1<len(aa) else 805
  ls=s.jp(n,(60,y0,235,y1));char=ls[0] if ls else '';on=[];kun=[]
  for line in ls[1:]:
   if '音' in line:on=[re.sub(r'^.*?音[：:]?','',line).strip()]
   elif '訓' in line:kun=[re.sub(r'^.*?訓[：:]?','',line).strip()]
  if char:add('N5','kanji',f,int(a[4]),character=char,meaning=s.bn(n,(239,y0,409,y1)),onyomi=on,kunyomi=kun,examples=[])
vocab_table(f,'N5',example=True)
# N4: four full-width teaching cards per page, each already includes two example words.
f='N4_Kanji_Onyomi_Kunyomi_Bangla.pdf';s=Source(UPLOAD/f)
for n,p in enumerate(s.doc):
 aa=anchors(p,39,41,40,3)
 for i,a in enumerate(aa):
  y0=a[1]-32;y1=aa[i+1][1]-32 if i+1<len(aa) else 790
  pieces=[z for z in s.pieces(n) if y0<=z['y']<y1];jps=[z for z in pieces if JA.search(z['text']) and 'Droid' in z['font']];large=[z for z in jps if z['size']>25]
  if not large:continue
  char=large[0]['text'];jp=s.jp(n,(85,a[1]+15,560,a[1]+75));on=jp[:1];kun=jp[1:2];meaning=clean(s.text(n,(115,y0,560,a[1]+20)).replace('\n',' '));ex=[]
  for yy in [a[1]+84,a[1]+113]:
   j=s.jp(n,(40,yy-8,560,yy+15));b=s.bn(n,(150,yy-8,560,yy+15))
   if len(j)>=1:
    # Different font sizes distinguish the example word and its kana reading.
    js=[z for z in jps if yy-8<=z['y']<yy+15];js.sort(key=lambda z:z['x']);word=js[0]['text'] if js else '';reading=js[1]['text'] if len(js)>1 else ''
    if word:ex.append(dict(word=word,reading=reading,meaning=b))
  add('N4','kanji',f,int(a[4]),character=char,meaning=meaning,onyomi=on,kunyomi=kun,examples=ex)
# N3: eight vertical kanji records per lesson page.
f='N3_Kanji_Bangla_Onyomi_Kunyomi.pdf';s=Source(UPLOAD/f)
for n,p in enumerate(s.doc):
 if 'strokes' not in p.get_text():continue
 aa=[w for w in anchors(p,42,44,125,3) if any('strokes' in b[4] and abs(b[1]-w[1])<3 for b in p.get_text('blocks'))]
 for i,a in enumerate(aa):
  y0=a[1]-2;y1=aa[i+1][1]-2 if i+1<len(aa) else 790
  char=' '.join(s.jp(n,(40,y0,100,y1)));on=s.jp(n,(150,y0+28,560,y0+47));kun=s.jp(n,(150,y0+46,560,y1));meaning=s.bn(n,(100,y0,560,y0+20))
  if char:add('N3','kanji',f,int(a[4]),character=char,meaning=meaning,onyomi=on,kunyomi=kun,examples=[])
# N2: two columns, four rows; source cells contain readings and meanings.
f='N2_Kanji_400_Bangla.pdf';s=Source(UPLOAD/f)
for n,p in enumerate(s.doc):
 for b in p.get_text('blocks'):
  m=re.fullmatch(r'(\d{3}) / 400\n',b[4])
  if not m:continue
  x0=42 if b[0]<300 else 303;x1=x0+250;y0=b[1]-22;y1=y0+165
  js=[z for z in s.pieces(n) if x0<=z['x']<x1 and y0<=z['y']<y1 and 'JP' in z['font'] and JA.search(z['text'])];large=[z for z in js if z['size']>20]
  if not large:continue
  char=large[0]['text'];on=s.jp(n,(x0,b[1]+60,x1,b[1]+78));kun=s.jp(n,(x0,b[1]+78,x1,b[1]+98));meaning=s.bn(n,(x0,b[1]+28,x1,b[1]+60))
  add('N2','kanji',f,int(m[1]),character=char,meaning=meaning,onyomi=on,kunyomi=kun,examples=[])

for level,data in books.items():
 for kind,rows in data.items():
  for e in rows:
   for key in ['meaning','formation','explanation','word','pattern','reading']:
    if key in e:e[key]=clean(e[key])
 (OUT/f'lessons-{level.lower()}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
(Path(__file__).parent/'extraction-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
(Path(__file__).parent/'example-words.json').write_text(json.dumps(example_words,ensure_ascii=False,indent=2))
print(json.dumps({l:{k:len(v) for k,v in d.items()} for l,d in books.items()},indent=2))
