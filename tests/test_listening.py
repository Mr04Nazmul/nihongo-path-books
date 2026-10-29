import importlib.util,json,pathlib,tempfile,unittest
from unittest.mock import patch
from types import SimpleNamespace
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('listening_validate',ROOT/'scripts/listening/validate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ListeningGate(unittest.TestCase):
 def test_empty_pending_collection_is_valid(self):
  d=json.loads((ROOT/'dist/data/listening-n5.json').read_text());self.assertEqual(m.validate(d,ROOT/'dist'),[])
 def test_permission_and_missing_reviews_never_publish(self):
  d={'rights':{'verified':False},'lessons':[{'id':'missing','audio':'audio/listening/n5/missing.mp3'}]}
  errors=m.validate(d,ROOT/'dist');self.assertTrue(any('Permission' in s for s in errors));self.assertTrue(any('review incomplete' in s for s in errors));self.assertTrue(any('missing audio' in s for s in errors))
 def test_traversal_is_rejected_before_probe(self):
  d={'rights':{},'lessons':[{'id':'unsafe','audio':'audio/listening/n5/../../../../etc/passwd'}]}
  with patch.object(m.subprocess,'run') as probe:
   self.assertTrue(any('unsafe audio path' in s for s in m.validate(d,ROOT/'dist')));probe.assert_not_called()
 def test_duplicate_audio_and_changed_hash_are_rejected(self):
  import hashlib
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);folder=root/'audio/listening/n5';folder.mkdir(parents=True)
   for name in ['a','b']:(folder/(name+'.mp3')).write_bytes(b'audio-test')
   rights={k:True for k in m.REQUIRED_RIGHTS};rights.update(verified=True,evidence={k:'test' for k in ('reference','grantor','grantee','verifiedBy','verifiedAt','scope')})
   e={'level':'N5','series':1,'number':1,'title':'test','source':'https://www.mlcjapanese.co.jp/test','transcript':'test','exercise':'test','translations':{'en':'test','bn':'পরীক্ষা'},'ruby':[['test']],'verification':{k:True for k in ('decodable','sourceAssociation','semanticAudioMatch','translationReviewed','quizReviewed')},'quiz':[{'prompt':{'en':'test','bn':'পরীক্ষা'},'choices':[{'en':'one','bn':'এক'},{'en':'two','bn':'দুই'}],'answer':0}]}
   sha=hashlib.sha256(b'audio-test').hexdigest();rows=[dict(e,id='a',audio='audio/listening/n5/a.mp3',sha256=sha),dict(e,id='b',number=2,audio='audio/listening/n5/b.mp3',sha256='changed')]
   with patch.object(m.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='{"format":{"duration":"1.0"}}')):
    errors=m.validate({'rights':rights,'lessons':rows},root)
   self.assertTrue(any('duplicate audio' in s for s in errors));self.assertTrue(any('hash mismatch' in s for s in errors))
