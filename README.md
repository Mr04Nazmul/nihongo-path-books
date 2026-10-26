# Nihongo Path Books

A new book-inspired Bengali/English edition of [Nihongo Path](https://github.com/Mr04Nazmul/nihongo-path), preserving the original stable curriculum IDs, source licenses, bookmarks/progress storage key and bundled Japanese audio. Independent cream-paper/book-cover interface with responsive pages, gentle animations, reduced-motion support, vocabulary/grammar/kanji search, lesson book dialogs, flashcards, quizzes and progress export/import.

## Included collection

| Level | Vocabulary | Grammar | Kanji |
|---|---:|---:|---:|
| N5 | 697 | 221 | 84 |
| N4 | 637 | 214 | 169 |
| N3 | 1,722 | 223 | 387 |
| N2 | 1,793 | 296 | 398 |
| N1 | 7,288 | 376 | 1,345 |

Total: 12,137 vocabulary entries, 1,330 grammar entries and 2,383 kanji entries. The N1 browsing collection includes 4,109 unclassified extra-practice words, explicitly labeled. This is a broad community collection, not an official exhaustive JLPT specification.

## Translation integrity

Only Bengali and English are selectable. Japanese original text remains visible. **Unreviewed Bengali machine drafts are not displayed:** the English source appears with a Bengali-review-pending label. Review status is checked independently for meaning, formation, guidance and every example. Authorship alone never qualifies a field as reviewed.

`translations/review-ledger.jsonl` retains per-field stable IDs, language, source/translation SHA-256 hashes and specific semantic evidence. `scripts/build_data.py` re-applies the Bengali/source override files and exports badges only for currently matching evidence. It does not translate or perform semantic review. Native-speaker review has not been performed, and English/community sources may also contain errors. No zero-error claim is made.

Current measured coverage is in `translations/review-progress.json`; unresolved kinship issues and the next work are in `translations/HANDOFF.md`.

## Run and verify

No package installation, translation model, private cache, paid service or build dependency is required. Python and Node are sufficient:

```sh
python scripts/build_data.py
python build-pages.py
python -m unittest discover -s tests
node --test tests/*.test.cjs
node --check dist/app.js
node --check dist/speech.js
python -m http.server 8080 --directory dist
```

The committed corpus JSON is the source baseline; authored amendments live in `translations/`. Rebuild is idempotent and tested. GitHub Pages deploys `dist/` after the checks.

## Sources and attribution

Original source revisions, inclusion/exclusion audits and licenses remain in `dist/data/`. Source project baseline: `Mr04Nazmul/nihongo-path` at `69b7ecd53a6ca36d82d0511cfcd87e29a5fe1186`, plus the hash-bound semantic correction batch recorded in this repository. Data attribution and CC BY-SA/CC BY notices are preserved.

The new interface is independently implemented. Circle-reveal theme transition inspiration: [Skiper UI Theme Toggle #26](https://skiper-ui.com/v1/skiper26), a free documented interaction, with required attribution. No paid component or subscription was used.

AdSense publisher, responsive slot and auto-ad settings are copied unchanged. Ad eligibility remains controlled by Google. Audio playback depends on browser support; physical iPhone testing is outstanding.
