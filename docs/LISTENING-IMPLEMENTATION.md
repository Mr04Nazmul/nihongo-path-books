# Listening publication update — 2026-10-29

The owner explicitly reconfirmed phone permission to add all material directly and waive visible source credit in favor of the site publisher identity. This is recorded as owner-attested permission, not independently verified permission. The site retains its established publisher, Hossain Najmul; no original authorship claim is made. Technical provenance is retained in lesson metadata.

100 source entries are included; 99 have locally hosted playable audio. Level 2 lesson 30 remains unavailable and has no player URL. Audio playback, hashing, source association, file presence, quiz structure and duplicate validation remain required. The owner requested immediate source-practice publication: semantic review flags remain false and the UI displays review status. Ten bilingual translations are drafts; the other 90 show explicit pending states. No claim of a completed translation or fully verified curriculum is made.

CI accepts either independently verified permission or the documented owner attestation, runs all checks and deploys source-practice lessons only with explicit status labels. Reviewed-mode publication still requires complete semantic and translation checks. The remainder below documents original intake and the first, held deployment. Its original counts/status are historical.

---

# Books and Listening rebuild

Base and rollback: `2848604e8f654bf7bf84d79c536ecb3142ceea32`, also retained on `backup/pre-listening-20261029`.
Implementation is committed to main. CI always rebuilds and tests; its separate deployment job is held until the validated listening manifest has verified permission and at least one reviewed lesson. No new public deployment is made before that gate passes. The older `nihongo-path` repository is not used.

## Architecture

Static HTML shell with `app.js`, existing reader/motion code, generated route shells, and GitHub Pages. The home and legacy collection URL now show two adjacent collections matching the supplied sketch. Both have N5, N4, N3, N2, N1 and Extra. Navigation is Listening / Books / Quiz / Settings. N1 remains locked for books, practice, and listening. Existing subject data, IDs, PDF files, translations and the `nihongo-path` storage key are unchanged.

`listening.js` supplies a separate listening reader and `nihongo-path-listening-v1` progress store. Native audio provides play/pause/seek, with replay and speed controls, transcript/ruby, both translations, fill-in exercises, adapted MC questions, answers, completion, resume time, keyboard and button navigation. N4–N1 and Extra have explicit unavailable states. No synthetic teaching lessons are shipped.

## Collection and verification

The ten source pages are `https://www.mlcjapanese.co.jp/n5_listening_{level}_{page}.html`, with level 1–2 and page 1–5. Each holds ten exercises. Raw source snapshots, scripts and downloaded audio remain in a private staging package, outside this public repository.

- 100 exercises, Japanese scripts and exercise texts collected.
- 99 unique original audio files downloaded, with SHA-256 and duration recorded.
- All 99 pass full ffmpeg decoding, not merely file-extension or HTTP checks.
- Level 2, exercise 30 returns HTTP 404 at `/Download/50SD/BP1-12/MTR30.mp3`. No replacement is fabricated.
- 91 answer sets align exactly after Unicode/spacing normalization. Nine were compared manually with their full source scripts; source discrepancies are retained and flagged.
- 100 MC quiz sets are draft adaptations of fill-in-the-blank tasks, not claimed to be original MLC MC questions.
- Full Bengali and English draft translations exist for Level 1 exercises 1–10. The remaining 90 are incomplete. No translation is marked independently reviewed.
- Semantic audio/script review remains incomplete for all lessons. A source-page association and successful decoding do not establish an exact spoken match.
- Public lesson/audio uploads: **0**. New public deployment: **none**.

## Permission gate

The owner reports permission, but no grant specifying scope was supplied. The source index is not such a grant. Before publication, verify the grantor and grantee, included recordings/scripts, permission to translate/adapt, public website hosting and public GitHub redistribution, required credits, limits and expiry. If material cannot be redistributed in a public repository, choose storage whose access matches the grant rather than setting `publicRepository` to true. Advertising requires commercial permission if enabled; advertising remains disabled.

`docs/listening-permission.template.json` is a blank evidence record, not permission. Do not mark flags true without evidence. Do not place private correspondence or personal details in public GitHub; use an evidence reference and a minimal verified scope summary.

`publish.py` validates a complete temporary tree before copying any staged material into `dist/`. Validation requires recorded rights, complete bilingual text, reading segments, reviewed quizzes, exact audio hashes, actual ffprobe duration, no duplicates and semantic review flags. CI runs the validator again. The shipped manifest is intentionally empty and unverified.

## Reproduce private intake

Install ffmpeg/ffprobe and `pip install -r scripts/listening/requirements.txt`.

```bash
python scripts/listening/collect_mlc.py --output /absolute/private/mlc
python scripts/listening/prepare_drafts.py --output /absolute/private/mlc
```

The collector caches downloads and writes per-page checkpoints. Network errors are explicit records. Automatic answer extraction produces drafts only. Preserve authored translations and manual corrections separately; do not overwrite `prepared.json` with raw intake.

After completing permission and content review:

```bash
python scripts/listening/publish.py --collection /private/mlc/reviewed.json --permission /private/mlc/permission.json --audio-root /private/mlc/audio
python scripts/listening/validate.py
python scripts/build_data.py
python scripts/audit_review.py --check
python build-pages.py
python -m unittest discover -s tests
node --test tests/*.test.cjs
```

The empty-manifest regression assertion must be updated deliberately when an authorized collection is actually published. Never disable the validator to satisfy tests.

Browser integration QA is `tests/listening-browser.cjs`, using Playwright and an installed Chromium (`NIHONGO_CHROME` can specify its executable). It starts its own loopback server. Test-only intercepted responses supply synthetic fixtures; these are never deployed or counted as MLC lessons. Real audio decoding is audited separately. Existing book data must remain byte-identical to the backup.

## Fonts and browser checks

Bengali and Japanese Noto fonts are bundled locally as static WOFF2 subsets, with their SIL OFL licenses. Source fonts: Google Fonts `ofl/notosansbengali/NotoSansBengali[wdth,wght].ttf` and `ofl/notosansjp/NotoSansJP[wght].ttf`. FontTools instantiated default weight/width and retained characters in current site text, all collected scripts, hiragana/katakana and the Bengali Unicode block. Regenerate these subsets if future lessons introduce additional kanji. This avoids relying on third-party font requests.

Verification: 14 Python tests, 29 Node tests, and Playwright integration at 320, 390, 768 and 1440 pixels pass. All 99 downloaded originals also load and play through Chromium native audio and support seeking. Full ffmpeg decoding passes for the same 99. Browser fixtures used for quiz and progress interactions are test-only. Safari/iOS device testing and semantic listening review have not been performed.
