import json,re
from pathlib import Path
P=Path(__file__).parent;D=P.parents[1]/'dist/data'
books={l:json.loads((D/f'lessons-{l}.json').read_text()) for l in ['n5','n4','n3','n2']}
for l in ['n5','n4']:
 for line in (P/f'{l}-grammar.tsv').read_text().splitlines():
  n,meaning,explanation=line.split('\t');e=books[l]['grammar'][int(n)-1];e.update(meaning=meaning,explanation=explanation)
words=[dict(e,level=l) for l,b in books.items() for e in b['vocab']]+json.loads((P/'example-words.json').read_text())
manual={}
for line in (P/'kanji-examples.tsv').read_text().splitlines():
 c,w,r,m=line.split('\t');manual[c]=dict(word=w,reading=r,meaning=m)
for l,b in books.items():
 for e in b['kanji']:
  c=e['character'];options=[x for x in words if c in x['word'] and x.get('reading') and x.get('meaning')]
  options.sort(key=lambda x:(x.get('level')!=l,len(x['word'])>6,len(x['word'])))
  if c in manual:example=manual[c]
  elif e['examples']:example=e['examples'][0]
  elif options:example={k:options[0][k] for k in ['word','reading','meaning']}
  else:raise ValueError('Missing example '+c)
  e['examples']=[example]
  e['onyomi']=[x for r in e['onyomi'] for x in re.split('[ ・、/]+',r) if x and x!='—']
  e['kunyomi']=[x for r in e['kunyomi'] for x in re.split('[、/]+',r) if x.strip() and x.strip()!='—']
 for kind,rows in b.items():
  for e in rows:
   for key in ['formation','explanation']:
    if key in e:e[key]=e[key].replace('�',' / ' if key=='formation' else '। ')
 (D/f'lessons-{l}.json').write_text(json.dumps(b,ensure_ascii=False,separators=(',',':')))
index={l.upper():dict({k:len(v) for k,v in b.items()},owner=True) for l,b in books.items()}
(D/'owner-index.json').write_text(json.dumps(index))
print(index)
