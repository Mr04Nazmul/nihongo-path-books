import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from audit_machine_drafts import inspect
from build_data import digest

class MachineDraftAudit(unittest.TestCase):
 def setUp(self):
  self.f={'source':{'ja':'３個を食べません。'},'translation':'পুরনো'}
  self.row={'key':'k','source_sha256':digest(self.f['source']),'previous_translation_sha256':digest(self.f['translation']),'draft':'আমি ৩টি খাই না।'}
 def test_safe_draft_not_verified(self):
  self.assertEqual(inspect(self.row,{'k':self.f},{}),[])
 def test_flags_meaning_risks_and_protects_reviewed(self):
  self.row['draft']='আমি ৪টি фрукты খাই।'
  self.row['source_sha256']='stale'
  flags=inspect(self.row,{'k':self.f},{'k':True})
  for flag in ('stale_source','already_reviewed_do_not_overwrite','unexpected_cyrillic','possible_negation_loss','possible_digit_mismatch'):
   self.assertIn(flag,flags)
 def test_unknown_and_empty(self):
  self.assertIn('unknown_field',inspect(self.row,{},{}))
  self.row['draft']=''
  self.assertIn('empty_draft',inspect(self.row,{'k':self.f},{}))
