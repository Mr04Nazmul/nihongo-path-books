# Implementation verification — 2026-10-29

This is a test release, not a completed production launch. Source commit b355bf173208e20f1dfc3e99be9566e3221ffd02 starts Android workflow run 40874524165. Its backend job passed. APK compilation and unit tests passed, but lint detected an old transitive Fragment dependency for the new activity-result file picker. Fragment1.8.9 is now explicitly pinned; the follow-up build must verify that fix.

## Passed

- Local backend suite: 21 tests, 19 passed, zero failures, two PostgreSQL-dependent tests skipped locally. The actual PostgreSQL GitHub backend job passed.
- Approved Supabase project vjygltfnrmyghlwyjtwu: private app schema deployed; Edge nihongo-books-v1 version6 active. Existing website and other app tables preserved. Admin snapshots/revisions/private audio bucket deployed; bucket is not public; anon/authenticated cannot execute privileged asset RPC.
- Real Supabase password login with a freshly created confirmed disposable test identity, opaque app session and student identity isolation passed. Test account/app records cleaned up; zero remaining diagnostic Auth identities. Owner's password/auth role untouched; app-only owner admin granted to confirmed owner.
- Live unauthorized access denied; student admin API denied; N1 content/ad sessions denied; forged client credit field stripped; cross-user state isolated; logout-all invalidates prior token; app-only deletion invalidates session without deleting shared global Auth identity.
- Test-only temporary entitlements fetched all twelve active text categories and N5 MP3 bytes. After expiry the same protected content returned403. No fake earned ad credits were granted.
- Google AdMob existing rewarded unit SSV URL saved to this Supabase endpoint; Google's console reported verified. Actual Google-signed synthetic probe returns200 and credited0. Both raw and form-urlencoded signed bytes have regression tests; duplicates/tampering rejected. This is not an earned advertisement event.
- Immutable manual-reviewed publication pipeline tested locally: students and incomplete reviews denied, snapshots survive draft edits, unpublish retains history. Private audio drafts require reviewed distribution/hosting/advertising rights before serving.
- Earlier Android CI builds passed unit/lint/APK/signature and API23/29/33/35 launch/FLAG_SECURE assertions. New1.3 actual capture-output test and native admin compile are awaiting this run.
- Original website files unchanged; prior13 website/reader regression tests passed.

## Inventory

|Level|Vocabulary|Grammar|Kanji|Listening|
|---|---:|---:|---:|---|
|N5|1052|110|110|100 records,99 MP3s|
|N4|1128|113|200|Absent|
|N3|1260|144|336|Absent|
|N2|1197|208|400|Absent|
|N1|Locked|Locked|Locked|Absent|

Free Hiragana, Katakana and basic numbers are provided. Counts describe source entries, not exhaustive or teacher-certified JLPT coverage. Full Japanese/Bengali lexical review remains incomplete; pending notices stay visible and existing translations are preserved.

## Remaining unverified or blocked

- Real Android test-ad load/display and earned SSV-to-credit round trip. Sample ad completion does not mint client-side credits. Production advertisements remain disabled.
- Missing N5 mlc-n5-l2-30 MP3; full physical listening output/attribution and app-distribution/audio-hosting/advertising rights scope. Owner phone attestation is not independent rights verification. No public listening publication/monetization until resolved.
- New native admin UI/device interaction, animations, actual screenshot/recording output on physical hardware; FLAG_SECURE cannot protect modified OS or external cameras.
- Recovery email deep-link allowlist/delivery and native reset device test. Password reset changes the shared Supabase identity. Offline retry queue and simultaneous-device merge are not implemented (last-write-wins).
- Live upload/publish administrator interaction has not been exercised; local publication tests passed and live overview passed.
- Release signing credentials, Play account/store listing/Data Safety/content rating/Ads declaration, physical device matrix, production policy/rights review and explicit public-publishing approval. AAB without supplied signing secrets is unsigned.

No paid resources, public Play publication, production ads or live website deployment were performed. Remaining items are not represented as passed.
