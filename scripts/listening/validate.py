"""Fail closed before publishing MLC audio or derivative lessons."""
import hashlib,json,subprocess
from pathlib import Path
REQUIRED_RIGHTS=('audioRedistribution','transcriptRedistribution','translations','publicWebsite','publicRepository')
def permission_accepted(rights):
 evidence=rights.get('evidence') or {}
 return rights.get('verified') is True or (rights.get('ownerAttested') is True and evidence.get('method')=='owner-reported-phone-permission' and bool(evidence.get('reference')) and bool(evidence.get('recordedAt')))
def validate(data,root):
 errors=[];rows=data.get('lessons',[]);rights=data.get('rights',{})
 if not rows:
  if rights.get('verified'):errors.append('Empty collection cannot claim verified rights')
  return errors
 if not permission_accepted(rights) or any(rights.get(k) is not True for k in REQUIRED_RIGHTS):errors.append('Permission does not cover all required uses')
 if rights.get('advertisingEnabled') and not rights.get('commercialUse'):errors.append('Advertising requires commercial permission')
 evidence=rights.get('evidence',{});evidence=evidence if isinstance(evidence,dict) else {}
 for k in ('reference','grantor','grantee','scope')+ (('verifiedBy','verifiedAt') if rights.get('verified') else ('recordedAt',)):
  if not isinstance(evidence.get(k),str) or not evidence[k].strip():errors.append('Missing permission evidence: '+k)
 ids=set();hashes=set();numbers=set()
 for e in rows:
  name=e.get('id','unknown');prefix=name+': '
  if name in ids:errors.append(prefix+'duplicate id')
  ids.add(name)
  pair=(e.get('series'),e.get('number'))
  if pair in numbers:errors.append(prefix+'duplicate lesson number')
  numbers.add(pair)
  if e.get('level')!='N5' or pair[0] not in [1,2] or not isinstance(pair[1],int) or not 1<=pair[1]<=50:errors.append(prefix+'invalid level/number')
  practice=e.get('publicationMode')=='source-practice'
  unavailable=e.get('availability')=='audio-unavailable'
  required=('sourceAssociation',) if unavailable else ('decodable','sourceAssociation')
  if not practice:required+=('semanticAudioMatch','translationReviewed','quizReviewed')
  if any(e.get('verification',{}).get(k) is not True for k in required):errors.append(prefix+'review incomplete')
  if practice and (not e.get('reviewStatus') or e.get('translationStatus') not in ['pending','draft','reviewed']):errors.append(prefix+'missing review status')
  if any(not isinstance(e.get(k),str) or not e[k].strip() for k in ('transcript','exercise','source','title')):errors.append(prefix+'missing source content')
  if not e.get('source','').startswith('https://www.mlcjapanese.co.jp/'):errors.append(prefix+'invalid attribution URL')
  if not (practice and e.get('translationStatus')=='pending') and any(not isinstance(e.get('translations',{}).get(k),str) or not e['translations'][k].strip() for k in ['bn','en']):errors.append(prefix+'missing translation')
  if not isinstance(e.get('ruby'),list) or not e.get('ruby'):errors.append(prefix+'missing Japanese reading segments')
  for q in e.get('quiz',[]):
   choices=q.get('choices',[]);answer=q.get('answer')
   if len(choices)<2 or not isinstance(answer,int) or isinstance(answer,bool) or not 0<=answer<len(choices):errors.append(prefix+'invalid quiz answer')
   for text in [q.get('prompt',{}),*choices]:
    if any(not isinstance(text.get(lang),str) or not text[lang].strip() for lang in ['bn','en']):errors.append(prefix+'incomplete quiz translations')
   if len({json.dumps(c,sort_keys=True) for c in choices})!=len(choices):errors.append(prefix+'duplicate quiz choices')
  if not e.get('quiz'):errors.append(prefix+'no quiz')
  if unavailable:
   if e.get('audio') or e.get('sha256') or e.get('verification',{}).get('decodable'):errors.append(prefix+'unavailable audio must not expose a broken player')
   continue
  rel=e.get('audio','');p=(root/rel).resolve()
  if not rel.startswith('audio/listening/n5/') or not p.is_relative_to(root.resolve()):errors.append(prefix+'unsafe audio path');continue
  if not p.is_file():errors.append(prefix+'missing audio');continue
  digest=hashlib.sha256(p.read_bytes()).hexdigest()
  if digest!=e.get('sha256'):errors.append(prefix+'audio hash mismatch')
  if digest in hashes:errors.append(prefix+'duplicate audio')
  hashes.add(digest)
  result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(p)],capture_output=True,text=True)
  try:duration=float(json.loads(result.stdout)['format']['duration'])
  except (ValueError,KeyError):duration=0
  if result.returncode or duration<=0:errors.append(prefix+'unplayable audio')
 return errors
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]/'dist');a=p.parse_args()
 data=json.loads((a.root/'data/listening-n5.json').read_text());errors=validate(data,a.root)
 if errors:raise SystemExit('\n'.join(errors))
 print(f"Listening manifest valid: {len(data['lessons'])} entries, {sum(e.get('availability')!='audio-unavailable' for e in data['lessons'])} playable")
