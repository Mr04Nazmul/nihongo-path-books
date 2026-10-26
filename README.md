# Nihongo Path Books

[Live website](https://mr04nazmul.github.io/nihongo-path-books/)

A new book-inspired Bengali/English edition of [Nihongo Path](https://github.com/Mr04Nazmul/nihongo-path), preserving the original stable curriculum IDs, source licenses, bookmarks/progress storage key and bundled Japanese audio. Independent open-book interface with a physical 3D page-turn, two facing paper pages, next/previous navigation, keyboard arrows and touch swipes, reduced-motion support, vocabulary/grammar/kanji search, lesson book dialogs, flashcards, quizzes and progress export/import.

## Included collection

| Level | Vocabulary | Grammar | Kanji |
|---|---:|---:|---:|
| N5 | 697 | 221 | 84 |
| N4 | 637 | 214 | 169 |
| N3 | 1,722 | 223 | 387 |
| N2 | 1,793 | 296 | 398 |
| N1 | 3,179 | 376 | 1,345 |
| Extra vocabulary | 4,109 | 0 | 0 |

Total: 12,137 vocabulary entries, 1,330 grammar entries and 2,383 kanji entries. The five level books contain 8,028 vocabulary entries. The separate Extra book contains 4,109 unclassified extra-practice words. Extras retain canonical N1 IDs for saved-progress compatibility, but are not presented as N1 exam vocabulary. This is a broad community collection, not an official exhaustive JLPT specification.

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

`translations/corpus-inventory.json` is the immutable pre-split ID inventory. Every rebuild compares all original identities with the six books and fails for missing, duplicate, unexpected or misplaced Extra entries; `dist/data/book-audit.json` publishes the result.

The committed corpus JSON is the source baseline; authored amendments live in `translations/`. Rebuild is idempotent and tested. GitHub Pages deploys `dist/` after the checks.

## Sources and attribution

Original source revisions, inclusion/exclusion audits and licenses remain in `dist/data/`. Source project baseline: `Mr04Nazmul/nihongo-path` at `69b7ecd53a6ca36d82d0511cfcd87e29a5fe1186`, plus the hash-bound semantic correction batch recorded in this repository. Data attribution and CC BY-SA/CC BY notices are preserved.

The new interface is independently implemented. Circle-reveal theme transition inspiration: [Skiper UI Theme Toggle #26](https://skiper-ui.com/v1/skiper26), a free documented interaction, with required attribution. No paid component or subscription was used.

Google advertising scripts, publisher tags and empty ad slots have been removed at the owner’s request. Adsterra remains enabled, including the five-second book-entry dialog. Audio playback depends on browser support; physical iPhone testing is outstanding.

## Reading studio and domain

The custom domain `devnazu.online` is assigned in GitHub Pages settings (Actions-based publishing). Onamae DNS uses the four GitHub Pages apex A records and www CNAME to `mr04nazmul.github.io`. The prior Travel domain assignment was released; Travel remains a separate project.

Settings offers Folio and Origami page turns, Calm mode, larger lesson text, an interactive animation preview and the owner-confirmed WhatsApp contact. Preferences are stored locally. Progress on the old github.io origin can be exported and imported using Progress when moving to the custom domain.

## Advertising incident response

All third-party advertising and the five-second book gate are disabled following a deceptive security-warning advertisement report. Generated pages omit ad loaders. Legacy banner URLs are inert and use a restrictive CSP, so direct visits cannot load an ad or redirect. Re-enabling monetization requires a separate review of provider creative controls and frame isolation.
