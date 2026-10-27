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
prevent charges. The selector is a preparation tool; the experimental inference pilot below has not been run or evaluated. Before
execution, confirm that remaining applicable credits cover the run and evaluate a properly
licensed Japanese–Bengali model on representative examples. Persist drafts
outside the review ledger and check source/translation hashes again on import.
Do not mark generated text as reviewed or silently replace verified text.

## Experimental inference pilot

`scripts/modal_inference.py` adds an experimental L4 pilot using Qwen2.5-7B-Instruct (Apache-2.0). It has not been run on Modal or evaluated for Bengali quality. It accepts at most ten fields per invocation, retries once, writes each result to a local JSONL checkpoint as unreviewed, and scales down after inactivity. It only searches the first 1,000 pending fields and is not a complete corpus pipeline. Model revision currently tracks `main`; pin and evaluate before production. Source/past-translation hashes must be checked again before any import. The pilot does not write corpus or review ledger and does not provide semantic validation. A time limit is not a cost guarantee. Secure CLI authentication and remaining applicable credit verification are required before running it.
