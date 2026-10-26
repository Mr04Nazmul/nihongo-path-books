# Optional draft translation tools

The GitHub plugin was used to find and inspect
[nidhaloff/deep-translator](https://github.com/nidhaloff/deep-translator)
at `fa67ada6c5d17617628fb13447de5457a5158dc6` (package version 1.11.4).
Its client code is Apache-2.0; see the upstream LICENSE. Provider service terms,
quotas, model licenses and translation rights are separate from that code license.
No third-party code or weights are bundled into the learner website.

Actual environment checks on 2026-10-26:

- The direct Google translation endpoint and the client's Google backend returned
  HTTP 429. They are not reliable for bulk use here.
- MyMemory rejected `bn-BD`. Its supported Bengali code is `bn-IN`.
- MyMemory with `ja-JP` → `bn-IN` successfully translated
  `ここでの喫煙は許可されていません。` as
  `এখানে ধূমপান অনুমোদিত নয় ।`.
- The result is retained in `tool-drafts.jsonl` as **unreviewed**, independently of
  the reviewed translation for that sentence. A cache hit was then exercised.
- Argos Translate's client license is MIT/CC0, but an individual model's license
  must also be checked before using it.
- The NLLB-200-distilled-600M model card says CC-BY-NC-4.0. No new NLLB output was
  used for this change. A machine output alone never supplies semantic evidence.

Install the optional helper in a separate environment:

```sh
python -m venv .venv-mt
.venv-mt/bin/pip install -r scripts/requirements-mt.txt
.venv-mt/bin/python scripts/translation_drafts.py \
  --field N3:vocab:9fe814581c:bn:examples.0
```

The helper reuses an engine/source-text cache. It only writes `tool-drafts.jsonl`;
it never changes corpus, overrides, review badges or ledger. Select exact pending
example keys from `n3-n2-pending.jsonl` rather than translating a whole corpus
again. Keep provider requests within their limits. An absent previous cache is
not evidence that previous drafts were reviewed.
