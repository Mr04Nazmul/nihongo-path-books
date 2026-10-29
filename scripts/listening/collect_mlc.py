from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from lxml import html
import json,hashlib,subprocess,time
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
ROOT=args.output.resolve();ROOT.mkdir(parents=True,exist_ok=True)
if ROOT.is_relative_to(Path(__file__).resolve().parents[2]):raise SystemExit('Use a private output directory outside the public repository')
BASE='https://www.mlcjapanese.co.jp/'
def fetch(url):
 for attempt in range(3):
  try:
   with urlopen(Request(url,headers={'User-Agent':'NihongoPathContentAudit/1.0'}),timeout=35) as r:return r.read()
  except Exception:
   if attempt==2:raise
   time.sleep(1)
def page(pair):
 level,part=pair;url=f'{BASE}n5_listening_{level}_{part}.html'
 cache=ROOT/f'page-{level}-{part}.html'
 raw=cache.read_bytes() if cache.exists() else fetch(url);cache.write_bytes(raw)
 doc=html.fromstring(raw);out=[]
 for a in doc.xpath('//audio'):
  box=a.getparent(); title=''.join(box.itertext()).strip();number=int(title.split('.')[0]); sibling=box.getnext()
  if sibling is None:raise ValueError(title)
  scripts=sibling.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," column-body ")]')
  if not scripts:raise ValueError('No script '+title)
  def lines(el):
   for br in el.xpath('.//br'):br.tail='\n'+(br.tail or '')
   return '\n'.join(x.strip() for x in el.text_content().splitlines() if x.strip())
  script=lines(scripts[0]); paragraphs=sibling.xpath('./p')
  question=lines(paragraphs[0]) if paragraphs else ''
  audio=urljoin(url,a.get('src'));dest=ROOT/'audio'/f'level-{level}'/f'{number:02}.mp3';dest.parent.mkdir(parents=True,exist_ok=True)
  try:
   data=dest.read_bytes() if dest.exists() else fetch(audio);dest.write_bytes(data)
  except Exception as error:
   out.append(dict(id=f'mlc-n5-l{level}-{number:02}',level='N5',series=level,number=number,title=title,source=url,audioSource=audio,transcript=script,exercise=question,translations={},quiz=[],verification={'decodable':False,'sourceAssociation':True,'semanticAudioMatch':False,'translationReviewed':False},error=str(error)))
   continue
  probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(dest)],capture_output=True,text=True)
  info=json.loads(probe.stdout) if probe.returncode==0 else {}
  out.append(dict(id=f'mlc-n5-l{level}-{number:02}',level='N5',series=level,number=number,title=title,source=url,audioSource=audio,audio=f'audio/listening/n5/level-{level}/{number:02}.mp3',sha256=hashlib.sha256(data).hexdigest(),duration=float(info.get('format',{}).get('duration',0)),transcript=script,exercise=question,translations={},quiz=[],verification={'decodable':probe.returncode==0,'sourceAssociation':True,'semanticAudioMatch':False,'translationReviewed':False}))
 (ROOT/f'lessons-{level}-{part}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 print(level,part,len(out),flush=True);return out
if __name__=='__main__':
 rows=[]
 with ThreadPoolExecutor(max_workers=5) as pool:
  for result in pool.map(page,[(l,p) for l in [1,2] for p in range(1,6)]):rows+=result
 (ROOT/'collected.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 print('Total',len(rows),'Decodable',sum(x['verification']['decodable'] for x in rows),flush=True)
