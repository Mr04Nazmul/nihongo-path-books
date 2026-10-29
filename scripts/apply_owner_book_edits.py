"""Apply the owner's PDF review to the same stable lesson IDs and subjects.

This never replaces a level with only its long-expression subset, changes the
number/order of lessons, or touches grammar/N1/Extra/listening.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def apply():
    review=json.loads((ROOT/'translations/owner-books/reading-edits.json').read_text())
    for level,subjects in review['levels'].items():
        path=ROOT/f'dist/data/lessons-{level}.json'
        data=json.loads(path.read_text())
        assert {k:len(v) for k,v in data.items()}==review['source_counts'][level],f'Changed source inventory: {level}'
        for kind,edits in subjects.items():
            assert kind in ('vocab','kanji')
            assert set(edits)=={e['id'] for e in data[kind]},f'Missing or unexpected IDs: {level}/{kind}'
            for e in data[kind]:
                e.update(edits[e['id']])
        path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
if __name__=='__main__':apply()
