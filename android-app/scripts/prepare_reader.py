"""Build an Android-only reader shell. Never edits dist or bundles paid curriculum."""
import json,re,shutil,hashlib,subprocess,sys,os
from pathlib import Path
root=Path(__file__).resolve().parents[2]
if not os.environ.get('BOOKS_SNAPSHOT_DIR'):subprocess.run([sys.executable,str(root/'android-app/scripts/sync_website.py')],check=True)
source=Path(os.environ.get('BOOKS_SNAPSHOT_DIR',str(root/'android-app/build/website-snapshot')));out=root/'android-app/app/build/generated/study-assets/reader'
if out.exists():shutil.rmtree(out)
out.mkdir(parents=True)
allowed_html=['index.html','lessons.html','n5.html','n4.html','n3.html','n2.html','n1.html','extra.html','review.html','progress.html','settings.html','sources.html','listening.html']
files=[p for p in source.iterdir() if p.suffix in ['.css','.js','.mjs'] and not p.name.startswith(('adsterra','n3-word-list'))]
files += [source/n for n in allowed_html]
for name in ['fonts','vendor','basics']:
 shutil.copytree(source/name,out/name)
for p in files:shutil.copy2(p,out/p.name)
(out/'data').mkdir()
for name in ['index.json','owner-index.json','book-inventory.json','review-status.json','NOTICE.md','LICENSE','SUPPLEMENT-ATTRIBUTION.md','HANABIRA-ATTRIBUTION.md']:
 if (source/'data'/name).exists():shutil.copy2(source/'data'/name,out/'data'/name)
# The app unlocks existing N1 text using the new server policy; the website stays unchanged.
# Server gates both JSON and PDFs; shell does not embed any curriculum.
for p in out.rglob('*.html'):
 s=p.read_text();s=re.sub(r'<script[^>]*src=["\'][^"\']*adsterra[^"\']*["\'][^>]*>.*?</script>','',s,flags=re.S)
 s=s.replace('href="basics/"','href="basics/index.html"')
 p.write_text(s)
# Use native Japanese TTS for word playback; original listening player remains unchanged.
(out/'speech.js').write_text('''window.NihongoSpeech={play:(text,button)=>{if(window.StudyNative)StudyNative.speak(String(text));},stop:()=>{if(window.StudyNative)StudyNative.stopSpeech();}};''')
# Never allow legacy embedded word-list pages into the app package.
assert not (out/'pdfs').exists() and not (out/'audio').exists()
manifest={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
(out.parent/'source-manifest.json').write_text(json.dumps(manifest,indent=2))
print(f'Reader shell prepared: {len(list(out.rglob("*")))} paths; protected JSON, PDF and audio excluded')

p=out/'app.js'
s=p.read_text()
s=s.replace("if(n==='N1'){db[n]={vocab:[],grammar:[],kanji:[]};return}","")
s=s.replace("if(state.level==='N1'){lockedN1();return}","")
s=s.replace("const locked=n==='N1'", "const locked=false")
s=s.replace("if(state.level==='N1'&&page!=='level')state.level='N2';", "")
s=s.replace("LEVELS.filter(n=>n!=='N1')", "LEVELS")
s=s.replace("data/${['N5','N4','N3','N2'].includes(n)?'lessons-':''}${n.toLowerCase()}.json", "data/${['N5','N4','N3','N2'].includes(n)?(new URLSearchParams(location.search).get('edition')==='pdf'?'owner-':'lessons-'):''}${n.toLowerCase()}.json")
p.write_text(s)
