# Bengali semantic review

Only hash-matched per-field evidence in `review-ledger.jsonl` counts as checked. Bengali meanings, formations, guidance and example translations are independently gated in the UI by `dist/data/review-status.json`. Unreviewed Bengali drafts remain in the committed corpus for further correction, but are not displayed to learners. English source fallback is labeled pending.

Run `python scripts/build_data.py` after source/override/ledger changes. It reapplies durable amendments, rejects stale evidence, regenerates review status and reports exact pending scope. It does no translation and no semantic review. Do not stamp fields merely because authored overrides, model output or tests exist.

Review original Japanese and reading first, then English and Bengali; Japanese takes priority if English disagrees. Inspect tense, polarity, roles, comparisons, numbers/calendar dates, kinship and polysemy. Keep precise bases and hashes. Retain unresolved items rather than claiming native review.

The inherited Bengali ledger plus this session's corrections covers N5 vocabulary meanings and early examples and grammar indices 0–33. Source fixes include 半分 read はんぶん → half, not half minute, and せっけん → soap, not economy. One-month ひとつき, left/right, dressing/undressing, lower-body clothing, holidays, transitives/intransitives and many unrelated machine outputs were corrected. Exact checked fields, rather than approximate index ranges, are authoritative.

Native-speaker or teacher review has not been performed. N4–N1 Bengali remains largely unreviewed and safely uses English fallback. Do not advertise zero errors or full Bengali completion.

## N3/N2 display change

At the owner’s request, N3/N2 now display existing Bengali drafts alongside English. Unchecked fields use an explicit Bengali draft/pending-review badge; this does not count as checked or alter the ledger. Other levels retain the evidence gate. The first 20 vocabulary and kanji meanings per requested level, ten example translations and two detailed grammar guides were corrected in this change; full semantic review remains unfinished.

## Meaning and grammar review checkpoint

A further 158 N3/N2 vocabulary meanings were compared against the Japanese and supplied English, including the counterexamples around cousin, latitude, a well, room vacancies, negation and different readings of 命. The first eight grammar entries of each level now have rewritten meanings, formations, usage guidance and all 47 Japanese examples translated into Bengali. Exact hashes in the ledger record 253 inspected fields: N3 128; N2 125. There are 13,901 N3/N2 fields in total, so the full requested review is not complete. No uninspected field was stamped as reviewed.

## Vocabulary 100–129 checkpoint

Reviewed 60 further N3/N2 meanings and all 107 associated example translations. Corrected the English source where it disagreed with Japanese and replaced unrelated うがい and homophone-confused 写る examples with explicitly authored sentences, retaining original examples in source overrides. This adds 167 checked fields; cumulative N3/N2 review coverage is 420 of 13,901 fields. The remaining 13,481 fields are not claimed as checked.

## Vocabulary positions 130–229, N3 and N2

Authored and checked 200 Bengali meanings and 366 individual example translations (566 fields). Fixed source glosses and homophone examples, preserving inherited originals. Cumulative N3/N2 checked fields: 986 of 13,901; remaining: 12,915. This is an AI semantic pass, not a native-speaker certification. The requested 5,000-field batch is not complete.

## Vocabulary positions 230–259, N3 and N2

Authored and checked 60 meanings and 113 example translations (173 fields). Clarified exchanges/replacements, shade/shadow, amount/frame and adjustment/health senses. Corrected source glosses; two authored replacement examples retain original examples. Cumulative N3/N2 checked fields: 1,159 of 13,901; 12,742 remain pending. Full review and the requested 5,000-field batch remain incomplete.

## Vocabulary meanings, positions 260–359, N3 and N2

Authored and checked 200 additional meanings. Examples in this range remain independently pending. Corrected conflated readings and misleading glosses, including 方々, 学級 and 生地. Cumulative N3/N2 checked fields: 1,359 of 13,901; remaining: 12,542. Full review and the 5,000-field target remain incomplete.

## Vocabulary examples, positions 260–309, N3 and N2

Authored and checked 184 examples. Corrected negation, quantities, pronouns and source English mismatches. The inherited 方々 example with the ほうぼう reading was replaced with an attributed かたがた example, with its original preserved. Cumulative N3/N2 checked fields: 1,543 of 13,901; remaining: 12,358. Full review and the 5,000-field target remain incomplete.

## Vocabulary examples, positions 310–359, N3 and N2

Authored and checked 182 examples. Fixed polarity, numbers, time and agency; corrected English source mismatches. Attributed replacement examples demonstrate the intended headwords, with originals preserved. Cumulative N3/N2 checked fields: 1,725 of 13,901; remaining: 12,176. The full semantic review and 5,000-field target remain incomplete.

## Current N3/N2 checkpoint: 4,025 / 13,901 fields

Starting from main `25cb8e64c9e9edbd67616876f4c438c1a1fbcfd8`, independently
recounted 1,841 checked and 12,060 pending N3/N2 fields. Added 2,184 inspected
fields: 800 vocabulary meanings (positions 380–779 in both books), 365 individual
vocabulary examples (positions 380–479), 234 grammar fields (entries 8–27 in both
books), and all 785 kanji meanings. These are field counts, not word counts.

Current checked: N3 2,049; N2 1,976. Pending: 9,876. The 5,000-field N3/N2
milestone and the full requested semantic review are NOT complete. The larger
all-level review total includes N5 and must not be presented as that milestone.

Corrections include polarity, tense, agent/patient roles, numeric comparisons,
calendar times, younger/older siblings, and reading-sensitive glosses. For
example ささえる is support, not the つかえる obstruction sense; じかに is
directly; かねない remains an undesirable possibility, not inability. Formation
and guidance were rewritten with attachment rules and relevant contrasts.
Incorrect English was amended in durable source overrides. Three attributed
replacement sentences replace mismatched readings/parts of speech; inherited
originals remain in source-overrides.json. No existing checked field changed.

`n3-n2-field-inventory.json` preserves the original 13,901 field identities and
the hashes of the checkpoint's 1,841 checked fields. `audit_review.py` verifies
missing/extra/duplicate fields, duplicate/stale evidence and protected fields.
`n3-n2-pending.jsonl` lists EVERY remaining ID/field with its current source hash.
This structural audit does not claim semantic completion. All advertising
remains disabled.

No attached translation ZIP was available in this session or found in Library;
no old /tmp path or other Work process was assumed. See TRANSLATION-TOOLS.md for
the actual GitHub tool checks, successful MyMemory smoke test and unchecked cache.

## N5 example checkpoint: 35 additional fields

Reviewed 35 N5 example translations against their Japanese sentences and supplied
context. Corrections include negation, the number of objects, clothing, spatial
relationships, politeness, and tense. Total all-level AI semantic-checked fields:
5,531 of 39,589; 34,058 pending. These are independent translation fields, not
word counts. No native-speaker or teacher verification is claimed. The 102 Modal
machine drafts are stored separately on the draft pilot branch, not treated as
reviewed in these totals.

## N5 example checkpoint: 30 additional fields

Reviewed 30 more N5 examples against Japanese, checking negation, numbers,
relative positions, grammatical person and time. Total all-level AI semantic
review is 5,561 of 39,589 fields, leaving 34,028 pending. Human review has
not been performed.
