"""Reapply durable Bengali/source overrides to the committed corpus, without MT.
The committed JSON is the source baseline. Stable IDs and source attribution stay
intact. Review badges are derived ONLY from matching source/translation hashes.
"""
import collections,datetime,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
BOOK_FILES=[(f'N{n}',f'n{n}.json') for n in [5,4,3,2,1]]+[('EXTRA','extra.json')]
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def key(f):return ':'.join(f[x] for x in ['level','kind','id','language','field'])
def fields():
 for book,filename in BOOK_FILES:
  for kind,rows in json.loads((ROOT/'dist/data'/filename).read_text()).items():
   for e in rows:
    for name in ['meaning','formation','guidance']:
     if name not in e['locales']['bn']:continue
     source={'word':e.get('word',e.get('pattern')),'reading':e.get('reading'),'meaning':e.get('meaning',e.get('meanings'))}
     if name!='meaning':source.update(formation=e.get('formation'),notes=e.get('notes'))
     yield dict(level=e['level'],kind=kind,id=e['id'],language='bn',field=name,source=source,translation=e['locales']['bn'][name])
    for i,x in enumerate(e.get('examples',[])):
     yield dict(level=e['level'],kind=kind,id=e['id'],language='bn',field=f'examples.{i}',source={'ja':x['ja'],'en':x['en']},translation=e['locales']['bn']['examples'][i])
def valid(r,f):return r.get('status')=='ai-semantic-checked' and r.get('source_sha256')==digest(f['source']) and r.get('translation_sha256')==digest(f['translation'])
def load_tsv(name,parts):
 result={}
 for line in (ROOT/'translations'/name).read_text().splitlines():
  a=line.split('\t');assert len(a)==parts,(name,line)
  result[tuple(a[:-1])]=a[-1]
 return result
def split_extra_book():
 """One-time migration is idempotent; canonical level and IDs never change."""
 p=ROOT/'dist/data/n1.json';n1=json.loads(p.read_text());extra_path=ROOT/'dist/data/extra.json'
 extra=json.loads(extra_path.read_text()) if extra_path.exists() else {'vocab':[],'grammar':[],'kanji':[]}
 by_id={e['id']:e for e in extra['vocab']}
 for e in n1['vocab']:
  if e.get('curriculum_status')=='supplementary':
   if e['id'] in by_id and by_id[e['id']]!=e:raise ValueError('Conflicting duplicate extra entry '+e['id'])
   by_id[e['id']]=e
 n1['vocab']=[e for e in n1['vocab'] if e.get('curriculum_status')!='supplementary']
 extra['vocab']=list(by_id.values())
 p.write_text(json.dumps(n1,ensure_ascii=False,separators=(',',':')))
 extra_path.write_text(json.dumps(extra,ensure_ascii=False,separators=(',',':')))
def audit_inventory():
 """Compare every canonical entry identity with the immutable pre-split corpus."""
 baseline=json.loads((ROOT/'translations/corpus-inventory.json').read_text())
 expected={f'{kind}:{level}:{entry_id}' for level,kinds in baseline['books'].items() for kind,ids in kinds.items() for entry_id in ids}
 actual=[];books={};counts={};misplaced=[]
 for book,filename in BOOK_FILES:
  d=json.loads((ROOT/'dist/data'/filename).read_text());books[book]={k:[e['id'] for e in rows] for k,rows in d.items()};counts[book]={k:len(rows) for k,rows in d.items()}
  for kind,rows in d.items():
   for e in rows:
    identity=f"{kind}:{e['level']}:{e['id']}";actual.append(identity)
    if (e.get('curriculum_status')=='supplementary') != (book=='EXTRA'):misplaced.append(identity)
 duplicates=[k for k,v in collections.Counter(actual).items() if v>1]
 missing=sorted(expected-set(actual));unexpected=sorted(set(actual)-expected)
 result={'source_commit':baseline['source_commit'],'book_counts':counts,'total_vocabulary':sum(c['vocab'] for c in counts.values()),'total_grammar':sum(c['grammar'] for c in counts.values()),'total_kanji':sum(c['kanji'] for c in counts.values()),'missing_entries':missing,'unexpected_entries':unexpected,'duplicate_entries':duplicates,'misplaced_extra_entries':misplaced,'all_original_entries_preserved':not(missing or unexpected or duplicates or misplaced)}
 (ROOT/'dist/data/book-inventory.json').write_text(json.dumps({'source_commit':baseline['source_commit'],'books':books},ensure_ascii=False,separators=(',',':')))
 (ROOT/'dist/data/book-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 if not result['all_original_entries_preserved']:raise ValueError('Book inventory mismatch: '+json.dumps(result,ensure_ascii=False))
 return result
def build():
 split_extra_book()
 meanings=load_tsv('entry-overrides.tsv',2);examples=load_tsv('example-entry-overrides.tsv',3)
 grammar={}
 for p in (ROOT/'translations').glob('grammar-n*.tsv'):grammar.update(load_tsv(p.name,2))
 details=json.loads((ROOT/'translations/grammar-details.json').read_text());sources=json.loads((ROOT/'translations/source-overrides.json').read_text());index={}
 for book,filename in BOOK_FILES:
  p=ROOT/'dist/data'/filename;d=json.loads(p.read_text());index[book]={k:len(v) for k,v in d.items()};index[book]['extra_vocab']=sum(e.get('curriculum_status')=='supplementary' for e in d['vocab'])
  for kind,rows in d.items():
   for e in rows:
    e.update(sources.get(e['level']+f':{kind}:'+e['id'],{}));l=e['locales']['bn'];e['locales']={'bn':l}
    if (e['id'],) in grammar and kind=='grammar':l['meaning']=grammar[(e['id'],)]
    if (e['id'],) in meanings:l['meaning']=meanings[(e['id'],)]
    l.update(details.get(e['id'],{}).get('bn',{}))
    for i in range(len(e.get('examples',[]))):
     if (e['id'],str(i)) in examples:l['examples'][i]=examples[(e['id'],str(i))]
  p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
 audit_inventory()
 (ROOT/'dist/data/index.json').write_text(json.dumps(index,separators=(',',':')))
 ledger=[json.loads(l) for l in (ROOT/'translations/review-ledger.jsonl').read_text().splitlines() if l.strip()];records={key(r):r for r in ledger};all_fields=list(fields());checked={key(f):True for f in all_fields if key(f) in records and valid(records[key(f)],f)}
 stale=[k for k,r in records.items() if k not in checked];pending=[{k:f[k] for k in ['level','kind','id','language','field']} for f in all_fields if key(f) not in checked]
 result={'status':'in-progress' if pending else 'ai-semantic-pass-complete','total_bengali_fields':len(all_fields),'ai_semantic_checked_fields':len(checked),'pending_fields':len(pending),'stale_evidence_fields':len(stale),'checked_by_level':dict(collections.Counter(k.split(':')[0] for k in checked)),'native_speaker_review':'not performed','next_unreviewed_fields':pending[:30]}
 (ROOT/'dist/data/review-status.json').write_text(json.dumps(checked,separators=(',',':')))
 for p in [ROOT/'translations/review-progress.json',ROOT/'dist/data/review-progress.json']:p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False))
 if stale:raise ValueError('Stale or invalid ledger fields: '+str(stale[:10]))
if __name__=='__main__':build()
