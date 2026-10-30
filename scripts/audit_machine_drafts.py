"""Triage machine drafts without changing the corpus or review evidence.

Heuristics only flag potential problems; absence of flags is not verification.
Run: python scripts/audit_machine_drafts.py path/to/drafts.jsonl
"""
import argparse
import collections
import json
import re
from build_data import fields, key, digest

BENGALI = re.compile(r'[\u0980-\u09ff]')
CYRILLIC = re.compile(r'[\u0400-\u052f]')
JP_NEG = re.compile(r'(ない|なかった|ません|ませんでした|ぬ|ず)(?:[。！？!?、]|$)')
BN_NEG = re.compile(r'(?:না|নেই|নয়|নি|নেইন|না\s*কি)')
DIGITS = str.maketrans('০১২৩৪৫৬৭৮৯０１２３４５６７８９','01234567890123456789')

def numbers(text):
    return set(re.findall(r'\d+', text.translate(DIGITS)))

def inspect(row, lookup, reviewed):
    issues = []
    f = lookup.get(row.get('key'))
    if not f:
        return ['unknown_field']
    if row.get('source_sha256') != digest(f['source']):
        issues.append('stale_source')
    if row.get('previous_translation_sha256') != digest(f['translation']):
        issues.append('stale_previous_translation')
    if row.get('key') in reviewed:
        issues.append('already_reviewed_do_not_overwrite')
    d = row.get('draft')
    if not isinstance(d, str) or not d.strip():
        return issues + ['empty_draft']
    if not BENGALI.search(d): issues.append('missing_bengali')
    if CYRILLIC.search(d): issues.append('unexpected_cyrillic')
    source = f['source'].get('ja', '')
    if source and JP_NEG.search(source) and not BN_NEG.search(d):
        issues.append('possible_negation_loss')
    if source and numbers(source) and not numbers(source).issubset(numbers(d)):
        issues.append('possible_digit_mismatch')
    if source and ('?' in source or '？' in source) and '?' not in d and '？' not in d:
        issues.append('possible_question_loss')
    return issues

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path')
    args = parser.parse_args()
    lookup = {key(f): f for f in fields()}
    from build_data import ROOT
    reviewed = json.loads((ROOT/'dist/data/review-status.json').read_text())
    rows = [json.loads(line) for line in open(args.path, encoding='utf-8') if line.strip()]
    counts = collections.Counter(r['key'] for r in rows)
    items = []
    for r in rows:
        flags = inspect(r, lookup, reviewed)
        if counts[r['key']] > 1: flags.append('duplicate_field')
        items.append({'key':r['key'], 'flags':flags, 'status':'unreviewed'})
    summary = collections.Counter(flag for item in items for flag in item['flags'])
    print(json.dumps({'total':len(items), 'flagged':sum(bool(i['flags']) for i in items),
        'unreviewed':len(items), 'flags':dict(summary), 'items':items,
        'note':'No flags does not establish semantic accuracy.'},ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
