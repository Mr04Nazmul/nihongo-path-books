# Nihongo Path Books Android — 1.1.0 test edition

Native Kotlin Android application with a restricted WebView book reader, Google Mobile Ads rewarded test ads and UMP consent. The website is preserved. Android-only commits do not trigger the Pages workflow. The old `nihongo-path` repository is not used.

## What this release changes

- Active N5–N2 vocabulary, grammar and kanji; N5 listening only. Free basics.
- N1 Coming Soon in native library. N1 is denied by the server even if a stale database entitlement exists. No N1 reward sessions or redemption; legacy data retained. Enabling N1 requires a future reviewed app/backend release, as well as the administrator level setting.
- Supabase Auth sign-up/sign-in adapter and Supabase PostgreSQL configuration. Previous Neon deployment is historical, **not the backend for this edition**. No API origin is built in by default: set `BOOKS_API_URL` to the new HTTPS API after deployment. An unconfigured APK provides free basics and a clear setup message; secure books/rewards cannot operate until backend configuration.
- Cloud study-state storage for bookmarks, learned entries, settings and next/previous page positions. Latest save replaces the prior snapshot; simultaneous device edits are last-write-wins. Automatic sync failures currently require another save/retry; there is no offline queue.
- Admin level controls, reward thresholds, durations, balances, unlock/redemption views, events, chapter/audio JSON draft editing. Draft publication and audio uploading are **not complete**; editor saves drafts and refuses publication until a reviewed publishing pipeline is implemented.

## Build and install

JDK 17, Android SDK 35, Python 3, Node 22, Gradle wrapper and network dependency access are required.

```sh
cd android-app
export BOOKS_API_URL=https://YOUR-BOOKS-API
./gradlew testDebugUnitTest lintDebug assembleDebug assembleDebugAndroidTest
adb install app/build/outputs/apk/debug/app-debug.apk
./gradlew connectedDebugAndroidTest
```

`BOOKS_SNAPSHOT_DIR=/absolute/path/to/dist` explicitly uses a previously reviewed local website snapshot; default build downloads the reader shell from devnazu.online and records hashes. Protected lesson JSON/PDF/audio is excluded from APK assets. Google test IDs are compiled in; no production ad switch is provided.

GitHub Actions `.github/workflows/android.yml` runs PostgreSQL integration tests, Android unit tests/lint, APK signature/alignment checks and API 23/29/33/35 emulator checks. Debug APK artifact: `Nihongo-Path-Books-debug-APK`. Signed release bundle requires repository secrets `ANDROID_KEYSTORE_BASE64`, `ANDROID_STORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`; the workflow builds but does not publish it. Keep the same release signing identity for updates.

## Supabase deployment — not applied to connected projects

Discovered projects were a general project and NAZU Cloud Staging, neither established as this app's project. No remote schemas, users, data, advertisements or services were changed. Select a dedicated Supabase project and provide backend hosting credentials before deployment. Do not copy existing users or overwrite production data.

1. Configure Supabase Auth email/password, confirmation, SMTP and password recovery policy. Keep email confirmation enabled.
2. Set backend-only environment from `backend/.env.example`: `AUTH_PROVIDER=supabase`, `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SERVICE_ROLE_KEY` (account deletion only), `DATABASE_URL` and `MIGRATION_DATABASE_URL` from the **same** Supabase project's Postgres connection/pooler. Use the provider's verified TLS setup. Never put these database/secret credentials in Android, repository variables or browser scripts.
3. Run `npm ci` in `backend`, then `npm run migrate` against a fresh dedicated database. Migrations create private `books` schema, roles, RLS and seed exact thresholds; they need a migration identity allowed to grant roles. They have been tested in PostgreSQL-compatible PGlite; verify role grants on the chosen Supabase project before launch. Do not expose `books` through the public Data API. Android uses the authenticated HTTPS API, not raw table writes.
4. Deploy `backend/Dockerfile` to a Node 22 HTTPS host; `CONTENT_ROOT=https://devnazu.online/`. Hosting selection and any paid provisioning require approval. The API uses Supabase PostgreSQL for all persistent state.
5. Supabase Auth validates email/password and `/auth/v1/user`; backend then issues a random opaque 30-day app session, stores only its SHA-256 hash, and encrypts the token on Android with Keystore. This is an API session bridge, **not native Supabase JWT refresh on Android**. App logout revokes the app session. Revoke all `books.sessions` for an account when handling compromised accounts; Supabase logout alone does not revoke these app sessions. Password recovery and cross-provider revocation are release blockers.
6. Assign administrator role using a privileged DB connection only: `update books.users set role='admin' where email='YOUR_CONFIRMED_OWNER_EMAIL';`. Role never comes from user-editable metadata. Open `/admin` on the API host. The Android client does not yet embed the admin editor.
7. Set repository variable `BOOKS_API_URL`, build again, and run real device tests. Existing old deployment URLs in historical `LIVE_DEPLOYMENT.md` do not prove this edition deployed.

## Rewards and secure access

| Level | 5 hours | 24 hours | 3 days | 7 days |
|---|---:|---:|---:|---:|
| N5 | 2 | 5 | 10 | 20 |
| N4 | 3 | 8 | 12 | 24 |
| N3 | 4 | 10 | 16 | 30 |
| N2 | 5 | 12 | 20 | 36 |
| N1 | Disabled | Disabled | Disabled | Disabled |

Each signed and verified Google reward adds one non-transferable credit for its server-created ad session's level. Credits persist until redeemed/account deleted. No cash value, transfers or client grant endpoint. Every ad is optional; disclosure precedes the user action. Users can close an ad without losing credits. Ads may be unavailable.

Redemption uses a user row lock, server DB time and a persisted request UUID. **While a level is active, redemption is rejected without deduction**. After expiry a new period starts from server time; existing time is never replaced. Each protected file fetch rechecks entitlement, level availability and expiry. The reader closes at server-derived expiry and revalidates on resume. This is not DRM: content still public on the preserved website can be accessed outside the app.

Google SSV validates ECDSA signatures, allowed units, session/user/timestamp association, transaction and session uniqueness, then credits atomically. Shared Google sample ad units cannot be configured with your own SSV callback: sample-ad completion does **not** automatically credit. Cryptographic fixture tests prove local verification, not real Google delivery. End-to-end testing requires your own AdMob unit configured in test-device mode and callback `/ssv`; production ads remain disabled pending explicit approval and consent/policy checks.

## Content and listening

`reports/content-audit.json` gives reproducible structural inventory, no dictionary/teacher certification. N5: 1052 vocabulary, 110 grammar, 110 kanji. N4: 1128/113/200. N3: 1260/144/336. N2: 1197/208/400. Counts are source entries, not an assertion of exhaustive JLPT coverage. Readings, Bengali spelling/meaning and lesson order still require full review; uncertain content has a review-pending notice. Verified source translations were not replaced.

N5 metadata has 100 lessons; current local checkout contains 99 final MP3s. App-distribution/audio-hosting/advertising rights are not independently verified; owner phone attestation exists but `commercialUse=false` and `verified=false`. Do not publicly publish or monetize listening until scope and attribution are resolved. Original attribution/license files remain. N4–N2 listening is neither offered in native library nor served by backend. N1 source retained.

## Verification and Play release

See `reports/IMPLEMENTATION_REPORT.md` for current results and limits. FLAG_SECURE is set on the activity, including protected screens. Emulator instrumentation checks the window flag; a physical screenshot/recording test is still required. Modified OS/devices and external cameras cannot be fully prevented.

Before Play submission: dedicated Supabase/backend deployment and role/security advisors; account verification/recovery and compromised-session revocation; Google test-device SSV round trip; physical device login/no-fill/expiry/resume/playback/capture tests; full content review and missing audio; rights/attribution confirmation; admin publishing/upload pipeline; privacy/support/account-deletion public URLs; Play developer account; signing backup/Play App Signing; store graphics, audience/content rating, Ads declaration and accurate Data Safety form. Public publishing, production ads and charges require explicit approval.
