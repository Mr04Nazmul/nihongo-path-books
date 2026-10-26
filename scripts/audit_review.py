"""Audit the N3/N2 review against an immutable per-field inventory.

This validates structure and evidence, never the semantic correctness of text.
Run --write after reviewed changes; --check verifies committed resume artifacts.
"""
import argparse, collections, json, pathlib
from build_data import ROOT, fields, key, digest, valid
INVENTORY = ROOT / 'translations/n3-n2-field-inventory.json'
REPORT = ROOT / 'translations/n3-n2-audit.json'
PENDING = ROOT / 'translations/n3-n2-pending.jsonl'

def audit(all_fields, ledger, inventory):
    target = [f for f in all_fields if f['level'] in ('N3', 'N2')]
    actual = [key(f) for f in target]
    lookup = {key(f): f for f in all_fields}
    counts = collections.Counter(key(r) for r in ledger)
    records = {key(r): r for r in ledger}
    checked = {k for k, r in records.items() if k in lookup and valid(r, lookup[k])}
    protected_changes = [k for k, hashes in inventory['checked_at_checkpoint'].items()
                         if k not in lookup or
                         hashes['source_sha256'] != digest(lookup[k]['source']) or
                         hashes['translation_sha256'] != digest(lookup[k]['translation'])]
    pending = [{**{name: f[name] for name in ('level', 'kind', 'id', 'language', 'field')},
                'source_sha256': digest(f['source'])}
               for f in target if key(f) not in checked]
    errors = {
        'missing_fields': sorted(set(inventory['fields']) - set(actual)),
        'unexpected_fields': sorted(set(actual) - set(inventory['fields'])),
        'duplicate_fields': sorted(k for k, n in collections.Counter(actual).items() if n > 1),
        'duplicate_evidence': sorted(k for k, n in counts.items() if n > 1),
        'stale_evidence': sorted(set(records) - checked),
        'changed_previously_checked_fields': sorted(protected_changes),
    }
    result = {
        'inventory_commit': inventory['source_commit'],
        'structural_audit_passed': not any(errors.values()),
        'semantic_review_complete': not pending and not any(errors.values()),
        'total_fields': len(target),
        'checked_fields': len(target) - len(pending),
        'pending_fields': len(pending),
        'checked_by_level': dict(collections.Counter(f['level'] for f in target if key(f) in checked)),
        'pending_by_kind_and_field': dict(sorted(collections.Counter(
            f["kind"] + ':' + f['field'].split('.')[0] for f in pending).items())),
        **errors,
        'native_speaker_review': 'not performed',
    }
    return result, pending

def rendered():
    inventory = json.loads(INVENTORY.read_text())
    ledger = [json.loads(line) for line in (ROOT / 'translations/review-ledger.jsonl').read_text().splitlines() if line.strip()]
    result, pending = audit(list(fields()), ledger, inventory)
    return result, json.dumps(result, ensure_ascii=False, indent=2) + '\n', ''.join(json.dumps(f, ensure_ascii=False, separators=(',', ':')) + '\n' for f in pending)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--write', action='store_true')
    group.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result, report, pending = rendered()
    if not result['structural_audit_passed']:
        raise SystemExit(report)
    if args.write:
        REPORT.write_text(report)
        PENDING.write_text(pending)
    if args.check and (REPORT.read_text() != report or PENDING.read_text() != pending):
        raise SystemExit('Resume artifacts are stale. Run python scripts/audit_review.py --write.')
    print(report, end='')

if __name__ == '__main__':
    main()
