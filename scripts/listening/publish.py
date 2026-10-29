"""Validate the complete staging tree before any files enter public dist/."""
import argparse,json,shutil,tempfile
from pathlib import Path
from validate import validate
p=argparse.ArgumentParser();p.add_argument('--collection',type=Path,required=True);p.add_argument('--permission',type=Path,required=True);p.add_argument('--audio-root',type=Path,required=True);p.add_argument('--dist',type=Path,default=Path(__file__).resolve().parents[2]/'dist');a=p.parse_args()
rows=json.loads(a.collection.read_text());rights=json.loads(a.permission.read_text());data={'schemaVersion':1,'level':'N5','status':'reviewed','rights':rights,'lessons':rows}
with tempfile.TemporaryDirectory() as d:
 stage=Path(d)
 for e in rows:
  rel=e.get('audio','')
  if not rel.startswith('audio/listening/n5/') or '..' in Path(rel).parts:raise SystemExit('Unsafe path')
  src=a.audio_root/f"level-{e['series']}"/f"{e['number']:02}.mp3"
  if src.exists():
   dest=stage/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 errors=validate(data,stage)
 if errors:raise SystemExit('\n'.join(errors))
 for e in rows:
  target=a.dist/e['audio'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(stage/e['audio'],target)
 dest=a.dist/'data/listening-n5.json';tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2));tmp.replace(dest)
print('Published to local dist:',len(rows),'lessons. Run all checks before deploying.')
