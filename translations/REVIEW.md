# Bengali semantic review

Only hash-matched per-field evidence in `review-ledger.jsonl` counts as checked. Bengali meanings, formations, guidance and example translations are independently gated in the UI by `dist/data/review-status.json`. Unreviewed Bengali drafts remain in the committed corpus for further correction, but are not displayed to learners. English source fallback is labeled pending.

Run `python scripts/build_data.py` after source/override/ledger changes. It reapplies durable amendments, rejects stale evidence, regenerates review status and reports exact pending scope. It does no translation and no semantic review. Do not stamp fields merely because authored overrides, model output or tests exist.

Review original Japanese and reading first, then English and Bengali; Japanese takes priority if English disagrees. Inspect tense, polarity, roles, comparisons, numbers/calendar dates, kinship and polysemy. Keep precise bases and hashes. Retain unresolved items rather than claiming native review.

The inherited Bengali ledger plus this session's corrections covers N5 vocabulary meanings and early examples and grammar indices 0–33. Source fixes include 半分 read はんぶん → half, not half minute, and せっけん → soap, not economy. One-month ひとつき, left/right, dressing/undressing, lower-body clothing, holidays, transitives/intransitives and many unrelated machine outputs were corrected. Exact checked fields, rather than approximate index ranges, are authoritative.

Native-speaker or teacher review has not been performed. N4–N1 Bengali remains largely unreviewed and safely uses English fallback. Do not advertise zero errors or full Bengali completion.

## N3/N2 display change

At the owner’s request, N3/N2 now display existing Bengali drafts alongside English. Unchecked fields use an explicit Bengali draft/pending-review badge; this does not count as checked or alter the ledger. Other levels retain the evidence gate. The first 20 vocabulary and kanji meanings per requested level, ten example translations and two detailed grammar guides were corrected in this change; full semantic review remains unfinished.
