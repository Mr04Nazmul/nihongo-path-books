# Nihongo Path Books handoff — 26 October 2026

## Open-book reader revision

Base commit: `d47fa3cc42efc5e32a0fa3b296248a886d402b95`. Six physically separate books now replace the mixed N1/Extra collection. N5–N1 vocabulary counts: 697, 637, 1,722, 1,793, 3,179 (8,028 total); Extra has 4,109. The immutable pre-split corpus inventory and rebuild audit prove all 12,137 vocabulary entries plus all grammar/kanji identities survive with zero missing, duplicate, unexpected or misplaced entries. Canonical Extra IDs and N1 bookmark identities are retained. All included primary/reference source inventory records are also tested. This proves retention of the existing source collection, not an official exhaustive JLPT word list.

Level pages now open an actual two-facing-page reader, with physical front/back 3D leaf turns, cover entrance, page numbers, previous/next, direct entry jump, keyboard arrows and touch swipe. Mobile pages flow vertically without hiding examples; reduced-motion mode immediately changes the actual entry. Search/contents remains collapsible below the reader. Extra has its own route, practice and membership-based progress. Bengali review coverage is unchanged.

Local checks pass: 7 Python tests and 14 JavaScript tests, including every forward boundary through all 4,109 Extra entries, exact entry-ID unions, source inventory retention, bookmark identity and progress separation, actual lesson movement under reduced motion, translation gates and audio behavior. Reader implementation commit `a20d8f6aa0f817c4b0f150692e942501729cec57` deployed successfully in GitHub Actions run `40257214613`. Live checks confirmed six separate shelf volumes, N1=3,179 and Extra=4,109, facing-page content, actual forward leaf animation (DOM animation name `turnLeafForward`), and keyboard forward/reverse lesson changes. A direct-jump interaction discovered during live QA now has an explicit Go button and Enter handler, with a regression test; reader-3 cache version is used. Final runtime commit `8a3af91a773aeae5e9ace0b6d888d2611ec165ab` deployed successfully in Actions run `40257767842`. All 22 checked live assets exactly match the checkout, including all six datasets and all six book HTML pages. Live Go-button navigation reached Extra lesson 4,109 / 4,109 (ウェア, Next disabled) and core N1 lesson 3,179 / 3,179 (世論). Search synchronized the actual N5 book to ひとつき (one matching entry). Native mobile swipe is implemented, but physical-device QA remains outstanding. Facing-page screenshot: `docs/live-open-book-20261026.jpg`. Earlier evidence below describes the previous grid-reader deployment.


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
