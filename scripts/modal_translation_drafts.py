"""Experimental Modal draft generator. Never writes corpus or review evidence.

Run `python scripts/modal_translation_drafts.py plan --limit 10` without Modal.
GPU execution is deliberately disabled until a verified account-side hard spend
limit is available. See translations/MODAL-DRAFTS.md.
"""
import argparse
import json
import pathlib
import re
import sys
from build_data import ROOT, digest, fields, key, valid

BENGALI = re.compile(r'[\u0980-\u09ff]')

def pending_items(limit, offset=0):
    if limit < 1 or offset < 0:
        raise ValueError("limit must be positive and offset nonnegative")
    ledger = {}
    for line in (ROOT / 'translations/review-ledger.jsonl').read_text().splitlines():
        if line.strip():
            item = json.loads(line)
            ledger[key(item)] = item
    result = []
    skipped = 0
    for f in fields():
        if key(f) in ledger and valid(ledger[key(f)], f):
            continue
        if skipped < offset:
            skipped += 1
            continue
        result.append({'key': key(f), 'source': f['source'],
                       'source_sha256': digest(f['source']),
                       'previous_translation_sha256': digest(f['translation']),
                       'field': f['field'], 'status': 'pending-generation'})
        if len(result) == limit:
            break
    return result

def validate_draft(item, result):
    issues = []
    if not isinstance(result, str) or not result.strip():
        issues.append('empty')
    elif not BENGALI.search(result):
        issues.append('no_bengali_script')
    # These checks are merely triage: no result becomes semantically verified.
    return {'key': item['key'], 'source_sha256': item['source_sha256'],
            'previous_translation_sha256': item['previous_translation_sha256'],
            'draft': result, 'status': 'unreviewed-machine-draft', 'flags': issues}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    plan = sub.add_parser('plan', help='Print pending field records without network access')
    plan.add_argument('--limit', type=int, default=10)
    plan.add_argument('--offset', type=int, default=0)
    sub.add_parser('run', help='Blocked until the inference backend is implemented and tested')
    args = parser.parse_args()
    if args.command == 'run':
        parser.error('GPU execution disabled: inference backend and secure runtime authentication are not ready.')
    if not 1 <= args.limit <= 1000:
        parser.error('--limit must be between 1 and 1000')
    if args.offset < 0:
        parser.error('--offset must be nonnegative')
    for item in pending_items(args.limit, args.offset):
        print(json.dumps(item, ensure_ascii=False))

if __name__ == '__main__':
    main()
