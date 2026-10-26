import hashlib,json,pathlib,subprocess,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_data import fields,key,valid
class Books(unittest.TestCase):
 def test_all_levels_and_languages(self):
  expected={5:(697,221,84),4:(637,214,169),3:(1722,223,387),2:(1793,296,398),1:(7288,376,1345)}
  for n,counts in expected.items():
   d=json.loads((ROOT/f'dist/data/n{n}.json').read_text());self.assertEqual(tuple(len(d[k]) for k in ['vocab','grammar','kanji']),counts)
   for rows in d.values():
    self.assertEqual(len(rows),len({e['id'] for e in rows}))
    for e in rows:
     self.assertEqual(set(e['locales']),{'bn'})
     self.assertEqual(len(e['examples']),len(e['locales']['bn']['examples']))
 def test_evidence_matches_and_only_checked_fields_get_badges(self):
  lookup={key(f):f for f in fields()};records=[json.loads(l) for l in (ROOT/'translations/review-ledger.jsonl').read_text().splitlines()]
  statuses=json.loads((ROOT/'dist/data/review-status.json').read_text())
  self.assertEqual(set(statuses),{key(r) for r in records})
  for r in records:
   self.assertEqual(r['language'],'bn');self.assertTrue(r['basis'].strip());self.assertTrue(valid(r,lookup[key(r)]))
  self.assertNotIn('N5:vocab:03d7b15720:bn:meaning',statuses)
  self.assertNotIn('N5:vocab:9d648d38ad:bn:examples.0',statuses)
  r=records[0];f=lookup[key(r)];self.assertFalse(valid(r,{**f,'translation':'changed'}))
 def test_rebuild_does_not_change_corpus(self):
  paths=[ROOT/f'dist/data/n{n}.json' for n in range(1,6)]
  before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
  subprocess.run([sys.executable,str(ROOT/'scripts/build_data.py')],check=True,capture_output=True)
  self.assertEqual(before,[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])
 def test_shared_pages_assets_and_ad_settings(self):
  for page in ['index','n5','n4','n3','n2','n1','lessons','review','progress','sources']:
   s=(ROOT/f'dist/{page}.html').read_text()
   for script in ['ads-config.js','ads.js','speech.js','app.js?v=books-1']:self.assertIn('src="'+script+'"',s)
   self.assertIn('<option value="bn">',s);self.assertIn('<option value="en">',s);self.assertNotIn('value="ne"',s)
  self.assertIn("slot:'2007625275'",(ROOT/'dist/ads-config.js').read_text())
  self.assertIn('ca-pub-3728341118830943',(ROOT/'dist/ads-config.js').read_text())
 def test_bundled_audio_and_draft_gates(self):
  manifest=json.loads((ROOT/'dist/audio/manifest.json').read_text())
  for path in manifest.values():self.assertTrue((ROOT/'dist/audio'/path).is_file(),path)
  s=(ROOT/'dist/app.js').read_text();self.assertIn("checked(e,'examples.'+i)",s);self.assertIn("state.lang==='bn'&&checked(e,field,k)",s)
  self.assertIn("localStorage.getItem('nihongo-path')",s)
  self.assertIn('prefers-reduced-motion',(ROOT/'dist/styles.css').read_text())
if __name__=='__main__':unittest.main()
