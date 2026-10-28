# N3 vocabulary replacement

The owner supplied three Word lists covering PDF pages 1–232 and requested replacing the prior N3 vocabulary display. `dist/data/n3-word-import.json` preserves all 2,363 sequential source rows, including original PDF page references.

The active vocabulary/practice list contains 2,195 words and short phrases. 166 full sentences are available separately in the searchable full list. Two incomplete continuation labels, source rows 917 and 927, are retained as notes and excluded from vocabulary practice. Counts are source entries, not unique dictionary words; repeated headwords and homophones are retained. No new semantic-review badges or native-review claims are added.

The original N3 corpus remains as the immutable attribution/review baseline used by the original inventory audit. The frontend replaces its vocabulary with this owner-supplied collection; N3 grammar and kanji and all other levels continue to use their existing data. Imported IDs use the `n3-pdf-` namespace, so prior learned/bookmarked IDs are not silently assigned to different words.

Regeneration: `python scripts/build_n3_words.py` produces the legacy list pages from the committed JSON. The three DOCX SHA-256 hashes and filenames are recorded in that JSON.
