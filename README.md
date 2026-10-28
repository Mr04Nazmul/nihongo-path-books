N2–N5 curriculum cleared at owner request on 2026-10-28; awaiting replacement PDFs. N1 and Extra retained. Prior content remains in Git history.

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

## N3 source reader removed

The owner requested removal of the original scan/OCR reader. Its HTML route and links from both Bengali word-list pages have been removed. The replacement Word-based vocabulary and practice remain available.

## Owner supplied N3 vocabulary replacement

The active N3 vocabulary book and its practice now use the three owner-supplied Word lists from PDF pages 1–232: 2,195 vocabulary/short-phrase entries. The complete searchable list at `n3-bangla-words.html` and `n3-bangla-book.html` preserves all 2,363 source rows, with 166 full sentences and two incomplete source notes separated from vocabulary practice. Counts include repeated headwords and must not be described as unique words.

The source-baseline counts above and the immutable corpus/review audit continue to describe the original licensed collection. That baseline is preserved for attribution and evidence; it is replaced at runtime for the N3 vocabulary book. N3 grammar/kanji and other books are unchanged. Imported entries have separate stable IDs so prior progress cannot be attached to different vocabulary. See `translations/n3-word-import.md`.

## Owner PDF replacement, 2026-10-28

N5–N2 now load owner-supplied editions inside the existing level books and subject tabs. The 15 original PDFs (648 pages) are bundled unchanged; `dist/data/owner-pdfs.json` records their SHA-256 hashes. Ordered facing-page records live in `owner-n5.json` through `owner-n2.json`; `owner-index.json` supplies the page counts. No third-party curriculum is mixed into these four editions. N1 and Extra retain their existing data.

The existing page-turn reader renders both original pages into its paper/ink palette, with chapter search, bookmarks, learned markers and an enlarged-page dialog. The source page artwork preserves Bengali and Japanese glyphs; search uses the PDF text layer, whose encoded Bengali can vary. Quiz generation is not synthesized from page images. PDF.js is bundled locally with its code license; PDF content ownership is separate from the rendering library.
