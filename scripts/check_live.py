"""Compare deployed public assets against this checkout; no browser state access."""
import concurrent.futures,hashlib,json,pathlib,sys,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
base=sys.argv[1] if len(sys.argv)>1 else 'https://mr04nazmul.github.io/nihongo-path-books/'
paths=[f'data/n{n}.json' for n in range(1,6)]+['data/extra.json','data/book-inventory.json','data/book-audit.json',*[f'n{n}.html' for n in range(1,6)],'extra.html']+['data/review-status.json','data/review-progress.json','data/index.json','app.js','styles.css','speech.js','audio/manifest.json','adsterra.js','adsterra-config.js','adsterra-banner-desktop.html','adsterra-banner-mobile.html']
def check(path):
 with urllib.request.urlopen(base+path,timeout=45) as r:data=r.read();status=r.status
 local=(ROOT/'dist'/path).read_bytes();assert data==local,path
 return {'path':path,'http':status,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'matches_checkout':True}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:result=list(pool.map(check,paths))
print(json.dumps({'base':base,'assets':result},indent=2))
