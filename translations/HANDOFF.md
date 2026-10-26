# Nihongo Path Books handoff — 26 October 2026

## Repository checkpoint

New repository: `Mr04Nazmul/nihongo-path-books`. Verified implementation commit: `22887f99a056fa9433fb8ef8f64eab50a7b06ee0` (main); this evidence-only follow-up records the deployed implementation without changing runtime assets. Initial repository commit: `720e6187e9bdc72d8d288a27cfb8df7330296113`. This implementation imports the original corpus at `Mr04Nazmul/nihongo-path@69b7ecd53a6ca36d82d0511cfcd87e29a5fe1186` and the corrected hash-bound review batch. The old repository is not deleted; permanent deletion requires a separate final confirmation. Resolve `git rev-parse HEAD` to obtain this handoff's exact containing commit.

## Implemented

Book-themed independent responsive UI, separate N5–N1 and utility pages, Bengali/English only, Japanese originals, full existing corpus (12,137 vocabulary, 1,330 grammar, 2,383 kanji), bookmarks/learned progress, flashcards/quiz, speech and 159 MP3 clips, export/import, source/license attribution, unchanged AdSense identifiers and settings. Skiper UI #26-inspired native theme reveal; no paid component.

Bengali text is only displayed for exact hash-valid reviewed fields. Pending translations use labeled English fallback. Shared GitHub Pages origin and original localStorage key preserve existing browser progress. No native-speaker certification or zero-error claim.

## Verified translation scope

`review-progress.json` is generated from the corpus and ledger: 1,293 checked Bengali fields out of 39,589; 38,296 pending, zero stale evidence. Per-entry scope and bases are in the ledger. This includes prior valid reviews plus newly reviewed N5 meanings 250–678, examples 135–199 (except uncertain uncle wording), examples 450–459, and grammar 5–33. Fields from proposed follow-on batches that were never inspected are not marked checked.

## Unresolved and pending

- `unresolved-kinship.json`: aunt entry `03d7b15720` and uncle example `9d648d38ad:examples.0`. Japanese does not identify parental side or all marriage relationships; current compact drafts narrow the source. Their Bengali fields remain hidden/unreviewed.
- N5 meanings 679–696 need homograph/sense verification (e.g. コップ cup/police, ボタン button/peony). N5 later examples, grammar 34 onward and kanji remain pending unless the ledger says otherwise.
- N4–N1 Bengali semantic review is outstanding. English community source texts may also contain errors.
- Physical iPhone audio and mobile-device testing remains outstanding.

## Rebuild and tests

`python scripts/build_data.py`, `python build-pages.py`, `python -m unittest discover -s tests`, `node --test tests/*.test.cjs`, `node --check dist/app.js`, `node --check dist/speech.js` pass locally. Five Python tests and eight JavaScript behavior/audio tests cover inventory/IDs/locales, exact ledger hashes/invalidation, cacheless idempotent rebuild, pages/ads, audio manifest and draft display gates. GitHub Actions run `40255661842` succeeded, including rebuild/tests and Pages deployment. Live URL: https://mr04nazmul.github.io/nihongo-path-books/. All 13 checked live assets (all five complete datasets, review files, index, app/CSS/speech/ads config/audio manifest) exactly match the checkout; hashes are in `tests/live-assets-result.json`. Live browser checks passed: Bengali/English switch, reading-sensitive ひとつき search, lesson modal and independently pending examples, bookmarking and learned counts across navigation, flashcard reveal, correct quiz feedback, grammar formation/roles/examples, N1 kanji readings and English fallback, and dark/light transition. Test-only bookmark/learned markers were removed. Homepage capture: `docs/live-preview-20261026.jpg`. Local browser preview could not reach executor loopback; no replacement browser was installed.

## Exact next review action

Run `python scripts/build_data.py`; inspect `translations/review-progress.json:next_unreviewed_fields`. Resolve kinship with explicit neutral descriptions or retain unresolved. Continue first unreviewed N5 vocabulary examples, then remaining N5 grammar/kanji, then N4 → N3 → N2 → N1. For each actual check, amend the relevant Bengali/source override, rebuild, bind evidence to final source/translation hashes, rerun tests, publish using expected-head safeguards. Never rerun machine translation and call it review. Never duplicate valid ledger work.
