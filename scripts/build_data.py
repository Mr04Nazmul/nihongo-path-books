"""Reapply durable Bengali/source overrides to the committed corpus, without MT.
The committed JSON is the source baseline. Stable IDs and source attribution stay
intact. Review badges are derived ONLY from matching source/translation hashes.
"""
import collections,datetime,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def key(f):return ':'.join(f[x] for x in ['level','kind','id','language','field'])
def fields():
 for n in [5,4,3,2,1]:
  for kind,rows in json.loads((ROOT/f'dist/data/n{n}.json').read_text()).items():
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
def build():
 meanings=load_tsv('entry-overrides.tsv',2);examples=load_tsv('example-entry-overrides.tsv',3)
 grammar={}
 for p in (ROOT/'translations').glob('grammar-n*.tsv'):grammar.update(load_tsv(p.name,2))
 details=json.loads((ROOT/'translations/grammar-details.json').read_text());sources=json.loads((ROOT/'translations/source-overrides.json').read_text());index={}
 for n in [5,4,3,2,1]:
  p=ROOT/f'dist/data/n{n}.json';d=json.loads(p.read_text());index[f'N{n}']={k:len(v) for k,v in d.items()};index[f'N{n}']['extra_vocab']=sum(e.get('curriculum_status')=='supplementary' for e in d['vocab'])
  for kind,rows in d.items():
   for e in rows:
    e.update(sources.get(f'N{n}:{kind}:'+e['id'],{}));l=e['locales']['bn'];e['locales']={'bn':l}
    if (e['id'],) in grammar and kind=='grammar':l['meaning']=grammar[(e['id'],)]
    if (e['id'],) in meanings:l['meaning']=meanings[(e['id'],)]
    l.update(details.get(e['id'],{}).get('bn',{}))
    for i in range(len(e.get('examples',[]))):
     if (e['id'],str(i)) in examples:l['examples'][i]=examples[(e['id'],str(i))]
  p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
 (ROOT/'dist/data/index.json').write_text(json.dumps(index,separators=(',',':')))
 ledger=[json.loads(l) for l in (ROOT/'translations/review-ledger.jsonl').read_text().splitlines() if l.strip()];records={key(r):r for r in ledger};all_fields=list(fields());checked={key(f):True for f in all_fields if key(f) in records and valid(records[key(f)],f)}
 stale=[k for k,r in records.items() if k not in checked];pending=[{k:f[k] for k in ['level','kind','id','language','field']} for f in all_fields if key(f) not in checked]
 result={'status':'in-progress' if pending else 'ai-semantic-pass-complete','total_bengali_fields':len(all_fields),'ai_semantic_checked_fields':len(checked),'pending_fields':len(pending),'stale_evidence_fields':len(stale),'checked_by_level':dict(collections.Counter(k.split(':')[0] for k in checked)),'native_speaker_review':'not performed','next_unreviewed_fields':pending[:30]}
 (ROOT/'dist/data/review-status.json').write_text(json.dumps(checked,separators=(',',':')))
 for p in [ROOT/'translations/review-progress.json',ROOT/'dist/data/review-progress.json']:p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False))
 if stale:raise ValueError('Stale or invalid ledger fields: '+str(stale[:10]))
if __name__=='__main__':build()
