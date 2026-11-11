import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
import modal_translation_drafts as drafts
from build_data import fields, key, ROOT
import json

class DraftSafetyTest(unittest.TestCase):
    def test_selection_excludes_valid_reviewed_fields(self):
        selected = drafts.pending_items(50)
        reviewed = json.loads((ROOT / 'dist/data/review-status.json').read_text())
        self.assertEqual(len(selected), 50)
        self.assertTrue(all(not reviewed.get(row['key']) for row in selected))
        actual = {key(f): f for f in fields()}
        self.assertTrue(all(row['source_sha256'] == drafts.digest(actual[row['key']]['source']) for row in selected))
    def test_offset_selects_nonoverlapping_pending_fields(self):
        first = drafts.pending_items(10)
        second = drafts.pending_items(10, 10)
        self.assertEqual(len(second), 10)
        self.assertFalse({x['key'] for x in first} & {x['key'] for x in second})
        self.assertEqual(first + second, drafts.pending_items(20))
        with self.assertRaises(ValueError):
            drafts.pending_items(1, -1)
    def test_drafts_never_mark_reviewed(self):
        item = drafts.pending_items(1)[0]
        self.assertEqual(drafts.validate_draft(item, 'বাংলা')['status'], 'unreviewed-machine-draft')
        self.assertIn('no_bengali_script', drafts.validate_draft(item, 'English')['flags'])
        self.assertIn('empty', drafts.validate_draft(item, '')['flags'])

if __name__ == '__main__': unittest.main()
