# Reading review, 2026-10-29

N5–N2 retain their original subject inventories and stable entry order: 4,637 vocabulary entries and 1,046 kanji entries. The reviewed PDF data is applied by stable ID using `scripts/apply_owner_book_edits.py` after the normal data build. Grammar, N1 and listening content are outside this patch.

1,037 longer vocabulary entries include separate Japanese/reading/Bengali component tables. Kanji display separate kun/on readings and example words. Confirmed Bengali spelling corrections include the reported কমিকস, ঔপন্যাসিক and গল্পের প্রধান চরিত্র entries. The durable edits are in `translations/owner-books/reading-edits.json`; the exact token correction reference is `spelling-tokens.json`.

Vocabulary pagination accounts for expanded tables; kanji pages contain two entries. Index links use actual page membership. Entry numbers remain their original list positions, while page numbers describe the current website layout, not printed source-PDF folios. The URL preserves the current subject and page.

Validation: Python unit suite, Node suite, syntax checks, rebuild checks, lesson count/order comparisons and browser inspection of vocabulary tables, page jumps/reload and kanji readings. All known confirmed spelling substitutions were applied. This is not a certification that every Japanese/Bengali definition has received independent native-speaker semantic review.
