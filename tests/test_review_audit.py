import copy, json, pathlib, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from audit_review import audit, rendered
from build_data import digest, key
from translation_drafts import cache_key

class ReviewAudit(unittest.TestCase):
    def test_resume_manifest_is_exact_and_current(self):
        report, rendered_report, pending = rendered()
        self.assertTrue(report['structural_audit_passed'])
        self.assertEqual(report['total_fields'], 13901)
        self.assertEqual(report['checked_fields'] + report['pending_fields'], 13901)
        self.assertEqual((ROOT / 'translations/n3-n2-audit.json').read_text(), rendered_report)
        self.assertEqual((ROOT / 'translations/n3-n2-pending.jsonl').read_text(), pending)
        self.assertEqual(report['semantic_review_complete'], report['pending_fields'] == 0)

    def test_duplicate_stale_and_protected_changes_are_rejected(self):
        f = dict(level='N3', kind='vocab', id='test', language='bn', field='meaning',
                 source={'word': '霧'}, translation='কুয়াশা')
        r = {k: f[k] for k in ['level','kind','id','language','field']}
        r.update(status='ai-semantic-checked', source_sha256=digest(f['source']),
                 translation_sha256=digest(f['translation']))
        inv = {'source_commit': 'test', 'fields': [key(f)], 'checked_at_checkpoint':
               {key(f): {k: r[k] for k in ['source_sha256','translation_sha256']}}}
        self.assertTrue(audit([f], [r], inv)[0]['structural_audit_passed'])
        self.assertFalse(audit([f], [r, r], inv)[0]['structural_audit_passed'])
        changed = {**f, 'translation': 'অন্ধকার'}
        report, _ = audit([changed], [r], inv)
        self.assertEqual(report['stale_evidence'], [key(f)])
        self.assertEqual(report['changed_previously_checked_fields'], [key(f)])
        self.assertEqual(audit([], [r], inv)[0]['missing_fields'], [key(f)])

    def test_draft_cache_is_engine_and_source_specific(self):
        self.assertEqual(cache_key('mymemory', '霧'), cache_key('mymemory', '霧'))
        self.assertNotEqual(cache_key('google', '霧'), cache_key('mymemory', '霧'))
        self.assertNotEqual(cache_key('mymemory', '霧'), cache_key('mymemory', '雨'))

if __name__ == '__main__':
    unittest.main()
