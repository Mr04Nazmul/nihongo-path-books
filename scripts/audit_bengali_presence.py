"""Report Bengali-script presence, separately from hash-based semantic review.

This heuristic cannot establish translation correctness or completeness. It never
changes the datasets, review ledger, or website. Japanese examples are sources,
not Bengali translation fields.
"""
import collections
import json
import re
from build_data import fields, key, ROOT

BENGALI = re.compile(r'[\u0980-\u09ff]')

def classify(value):
    if not isinstance(value, str) or not value.strip():
        return 'empty_or_non_string'
    if not BENGALI.search(value):
        return 'no_bengali_script'
    return 'contains_bengali_script'

def main():
    checked = json.loads((ROOT / 'dist/data/review-status.json').read_text())
    totals = collections.Counter()
    by_level = collections.defaultdict(collections.Counter)
    flagged = []
    for f in fields():
        status = classify(f['translation'])
        totals[status] += 1
        by_level[f['level']][status] += 1
        if status != 'contains_bengali_script':
            flagged.append({'field': key(f), 'issue': status, 'reviewed': bool(checked.get(key(f)))})
    print(json.dumps({'total_fields': sum(totals.values()), 'presence': dict(totals),
                      'by_level': {k: dict(v) for k, v in sorted(by_level.items())},
                      'flagged_fields': flagged,
                      'note': 'Script presence is not a semantic or completeness check.'},
                     ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
