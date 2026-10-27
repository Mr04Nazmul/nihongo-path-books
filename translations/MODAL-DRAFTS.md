# Modal translation preparation

`python scripts/modal_translation_drafts.py plan --limit 10` emits pending field
identities, Japanese/context source and source/previous-translation hashes as
JSONL. It selects only fields without matching semantic-review evidence and does
not change any project data. The draft validation helper marks output as
unreviewed and flags empty or non-Bengali output; these are not semantic checks.

GPU execution is intentionally disabled. The account dashboard reported $1 of
$30 monthly free credits available, with a payment method required for the rest.
An account-side hard spending limit, current GPU prices and secure runtime
credentials have not been verified. A timeout or batch size alone cannot
prevent charges. The code is a preparation tool, not a working inference
pipeline; no model has been selected, downloaded, evaluated or run. Before
execution, confirm that remaining applicable credits cover the run and evaluate a properly
licensed Japanese–Bengali model on representative examples. Persist drafts
outside the review ledger and check source/translation hashes again on import.
Do not mark generated text as reviewed or silently replace verified text.
