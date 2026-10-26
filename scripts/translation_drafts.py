"""Cache optional MT suggestions; this script NEVER writes overrides or evidence.

Install deep-translator==1.11.4 separately. Select exact pending example keys
with --field; repeated source sentences reuse the cache. Provider terms and
quotas are separate from the Apache-2.0 client library license.
"""
import argparse, hashlib, json, pathlib
from build_data import ROOT, fields, key
CACHE = ROOT / 'translations/tool-drafts.jsonl'

def cache_key(engine, text):
    return engine + ':ja:bn:' + hashlib.sha256(text.encode()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=['mymemory', 'google'], default='mymemory')
    parser.add_argument('--field', action='append', required=True)
    parser.add_argument('--cache', type=pathlib.Path, default=CACHE)
    args = parser.parse_args()
    lookup = {key(f): f for f in fields()}
    requests_to_make = []
    for selected in args.field:
        if selected not in lookup or not lookup[selected]['field'].startswith('examples.'):
            parser.error('Select an existing example field: ' + selected)
        requests_to_make.append(lookup[selected])
    cache = {}
    if args.cache.exists():
        for line in args.cache.read_text().splitlines():
            row = json.loads(line)
            cache[cache_key(row['engine'], row['ja'])] = row
    # Optional imports are isolated: rebuilds and audits require no MT package.
    translator = None
    for f in requests_to_make:
        text = f['source']['ja']
        identity = cache_key(args.engine, text)
        if identity not in cache:
            if translator is None:
                import requests
                from deep_translator import MyMemoryTranslator, GoogleTranslator
                original_get = requests.get
                def bounded_get(*a, **kw):
                    kw.setdefault('timeout', 20)
                    return original_get(*a, **kw)
                requests.get = bounded_get
                translator = (MyMemoryTranslator(source='ja-JP', target='bn-IN')
                              if args.engine == 'mymemory' else
                              GoogleTranslator(source='ja', target='bn'))
            result = translator.translate(text)
            if not isinstance(result, str) or not result.strip():
                raise RuntimeError('Provider returned no draft for ' + key(f))
            cache[identity] = {'engine': args.engine, 'ja': text, 'bn': result,
                               'status': 'unreviewed-machine-draft'}
            args.cache.parent.mkdir(parents=True, exist_ok=True)
            tmp = args.cache.with_suffix('.tmp')
            tmp.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in cache.values()))
            tmp.replace(args.cache)
        print(json.dumps({'field': key(f), **cache[identity]}, ensure_ascii=False))

if __name__ == '__main__':
    main()
