import hashlib,json,pathlib,subprocess,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_data import fields,key,valid,audit_inventory
class Books(unittest.TestCase):
 def test_all_levels_and_languages(self):
  expected={5:(697,221,84),4:(637,214,169),3:(1722,223,387),2:(1793,296,398),1:(3179,376,1345)}
  for book,counts in [*[(f'n{n}',v) for n,v in expected.items()],('extra',(4109,0,0))]:
   d=json.loads((ROOT/f'dist/data/{book}.json').read_text());self.assertEqual(tuple(len(d[k]) for k in ['vocab','grammar','kanji']),counts)
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
  paths=[*[ROOT/f'dist/data/n{n}.json' for n in range(1,6)],ROOT/'dist/data/extra.json',ROOT/'dist/data/book-inventory.json',ROOT/'dist/data/book-audit.json']
  before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
  subprocess.run([sys.executable,str(ROOT/'scripts/build_data.py')],check=True,capture_output=True)
  self.assertEqual(before,[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])
 def test_shared_pages_assets_and_ad_settings(self):
  for page in ['index','n5','n4','n3','n2','n1','lessons','review','progress','sources','extra','settings']:
   s=(ROOT/f'dist/{page}.html').read_text()
   for script in ['speech.js','app.js','motion.js']:self.assertRegex(s,'src="'+script.replace('.','\\.')+r'(?:\?[^"]*)?"')
   self.assertIn('<option value="bn">',s);self.assertIn('<option value="en">',s);self.assertNotIn('value="ne"',s)
   self.assertNotIn('adPlacement',s);self.assertNotIn('google-adsense-account',s)
  for path in (ROOT/'dist').glob('*.html'):
   self.assertNotIn('adsbygoogle',path.read_text());self.assertNotIn('ca-pub-',path.read_text())
  self.assertFalse((ROOT/'dist/ads.js').exists());self.assertFalse((ROOT/'dist/ads-config.js').exists())
 def test_no_entry_missing_or_duplicated_after_separating_extra(self):
  baseline=json.loads((ROOT/'translations/corpus-inventory.json').read_text())['books']
  expected={f'{kind}:{level}:{entry_id}' for level,kinds in baseline.items() for kind,ids in kinds.items() for entry_id in ids}
  actual=[]
  for filename in [*[f'n{n}.json' for n in range(1,6)],'extra.json']:
   d=json.loads((ROOT/'dist/data'/filename).read_text())
   for kind,rows in d.items():
    for e in rows:
     actual.append(f"{kind}:{e['level']}:{e['id']}")
     self.assertEqual(e.get('curriculum_status')=='supplementary',filename=='extra.json')
  self.assertEqual(set(actual),expected)
  self.assertEqual(len(actual),len(set(actual)))
  extra=json.loads((ROOT/'dist/data/extra.json').read_text())
  self.assertTrue(all(e['level']=='N1' for e in extra['vocab']))
  report=audit_inventory();self.assertTrue(report['all_original_entries_preserved']);self.assertEqual(report['total_vocabulary'],12137)
 def test_all_included_primary_and_reference_source_entries_remain(self):
  catalog={}
  for filename in [*[f'n{n}.json' for n in range(1,6)],'extra.json']:
   for kind,rows in json.loads((ROOT/'dist/data'/filename).read_text()).items():
    for e in rows:catalog.setdefault((e['level'],kind),set()).add(e['id'])
  coverage=json.loads((ROOT/'dist/data/coverage.json').read_text())
  for level,kinds in coverage['primary_inventory'].items():
   for kind,ids in kinds.items():self.assertTrue(set(ids).issubset(catalog[(level,kind)]))
  for name in ['coverage','reference-audit']:
   audit=json.loads((ROOT/f'dist/data/{name}.json').read_text())
   for source_kind,kind in [('vocabulary','vocab'),('grammar','grammar')]:
    for e in audit[source_kind]:
     if e['status']=='excluded':continue
     self.assertIn(e['id'],catalog[(e.get('at_level',e.get('level')),kind)])
 def test_bundled_audio_and_draft_gates(self):
  manifest=json.loads((ROOT/'dist/audio/manifest.json').read_text())
  for path in manifest.values():self.assertTrue((ROOT/'dist/audio'/path).is_file(),path)
  s=(ROOT/'dist/app.js').read_text();self.assertIn("checked(e,'examples.'+i)",s);self.assertIn("state.lang==='bn'&&checked(e,field,k)",s)
  self.assertIn("localStorage.getItem('nihongo-path')",s)
  self.assertIn('prefers-reduced-motion',(ROOT/'dist/styles.css').read_text())
if __name__=='__main__':unittest.main()
