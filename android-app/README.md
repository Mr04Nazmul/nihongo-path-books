# Nihongo Path Books — native Android application

Independent Android project; the live website is not edited by the app build. Its reader shell is downloaded directly from https://devnazu.online/ by `scripts/sync_website.py`, with an origin and SHA-256 manifest; repository curriculum files are not used as the content source. Kotlin native dashboard, login/profile, rewards, histories and settings surround the existing book animation/reader in a restricted Android WebView. Free basics are bundled offline. Protected lessons, PDFs and audio are **not in the APK** and are fetched by the native HTTP client after server authorization. Native Japanese TTS replaces browser speech for vocabulary.

## Current delivery boundaries

The Neon PostgreSQL database and Neon Function API are now deployed and connected to the Android build. See [LIVE_DEPLOYMENT.md](LIVE_DEPLOYMENT.md) for the public endpoints and actual verification. Login, profile, credits, access and protected website retrieval use the live service. No database credential is in the APK. Google sample advertisements remain the development default; a sample ad's client callback alone never grants credits.

Existing content snapshot: N5–N2 owner text lessons and original PDF editions; N1 existing legacy text; free hiragana/katakana/numbers; original animations, practice, search and reader progress. The Android-only build removes the website's hardcoded N1 lock and lets the new server policy decide access. Website remains unchanged. Only N5 listening exists in the source. N4–N1 listening shows the existing unavailable state; no lessons are fabricated. Listening rights metadata has `commercialUse: false`; resolve permission for advertising-supported use before production monetization. Attribution/license files are retained.

## Local build

Requires JDK 17, Android SDK 35, Python 3, Node 22 and Internet for dependencies and the website snapshot. Set BOOKS_SNAPSHOT_DIR only to explicitly use a previously downloaded website snapshot for an offline rebuild.

```sh
cd android-app
# Public HTTPS API origin, never a database URL or credential:
export BOOKS_API_URL=https://br-royal-poetry-ao0544wq-booksapi.compute.c-2.ap-southeast-1.aws.neon.tech
./gradlew testDebugUnitTest lintDebug assembleDebug
# APK: app/build/outputs/apk/debug/app-debug.apk
./gradlew connectedDebugAndroidTest  # attached Android device/emulator
```

All builds currently use Google's official test App ID and rewarded unit ID. There is intentionally no production-ad switch in this initial version. Google UMP is queried at launch and must permit ad requests. Ads are requested only on a user tap; unfinished/no-fill/failed ads grant nothing and deduct nothing. The device reward callback never writes a credit.

## Neon backend

Neon PostgreSQL is supported through `pg`; application SQL is portable PostgreSQL (also suitable for a dedicated Supabase PostgreSQL database). This edition uses server-side email/password authentication with salted scrypt hashes and opaque 30-day sessions, not Supabase Auth. That avoids requiring two database providers when Neon is selected. Tokens are hashed on the server and encrypted with Android Keystore on-device; backups and WebView debugging are disabled. Neon does not make AdMob verification automatic: a public HTTPS API is still needed.

```sh
cd android-app/backend
cp .env.example .env  # fill privately; Node can read it with --env-file
npm ci
node --env-file=.env src/migrate.mjs
node --env-file=.env src/server.mjs
# From repository root, build self-contained API image:
docker build -f android-app/backend/Dockerfile -t nihongo-books-api .
# Supply private env to hosting provider. Do not publish dist on this API host.
```

Use a dedicated Neon project/branch. Migration requires permission to create roles. It grants restricted `books_app` and `books_service` roles to the migration identity; if the runtime login differs, grant these roles to that runtime login with a privileged SQL connection. Never put `DATABASE_URL` in Gradle, repository variables, APK, JavaScript or public admin page. Keep the DB connection encrypted and validate host certificates according to the hosting provider. Runtime SQL enters restricted roles per transaction. RLS is enabled and forced on all tables; student policies only expose their own balances/unlocks/reward/redemption history. API always derives user ID from a valid session. Admin role is read from the DB, never client claims.

Promote your own account using a privileged migration connection, once:

```sql
update books.users set role='admin' where email='YOUR-VERIFIED-OWNER-EMAIL';
```

Open `https://YOUR-API/admin`, sign in. Tokens stay in memory, no CDN scripts or public admin data. Dashboard edits credit thresholds, duration seconds and tier availability, pauses rewards, and shows verified ad count, credits issued/redeemed, active access and access/security events. Ad unit allowlists are server environment configuration so a client/admin UI cannot turn on arbitrary publisher ads. No admin can manufacture verified impressions through an endpoint.

## Reward protocol

1. User selects a JLPT level and taps Watch Ad. Authenticated server creates a single-use UUID ad session tied to that user/level, with a two-hour signed-event window.
2. Native AdMob receives `user_id` and `custom_data=ad-session-UUID` via ServerSideVerificationOptions.
3. Google calls `/ssv`. API verifies the ECDSA-SHA256 signature over the URI-decoded query in its original parameter order, obtains Google's rotating public keys, checks allowed unit and signed time/session/user association.
4. In one DB transaction, insert the unique Google transaction ID and unique ad-session ID, consume the session, and add exactly one credit. Retries are idempotent; another transaction cannot reuse the session. No client credit grant endpoint exists.
5. User chooses a duration and confirms redeem. The server serializes per user, re-reads enabled tier, atomically deducts credits and creates expiry with DB time. A persisted request UUID makes uncertain network retries safe. Active access cannot be replaced/restarted. Expiry only closes access; unused credits remain.
6. Each protected data/PDF/audio fetch checks session and expiry. Reader countdown uses server time plus monotonic device elapsed time, closes/destroys the WebView at expiry and revalidates on resume. Client clocks cannot authorize content.

Initial costs are seeded exactly:

| Level | 5 hours | 24 hours | 3 days | 7 days |
|---|---:|---:|---:|---:|
| N5 | 2 | 5 | 10 | 20 |
| N4 | 3 | 8 | 12 | 24 |
| N3 | 4 | 10 | 16 | 30 |
| N2 | 5 | 12 | 20 | 36 |
| N1 | 6 | 15 | 25 | 45 |

## SSV testing and production setup

Google's shared test ad unit cannot be configured in your publisher console with your own callback. It demonstrates native test-ad loading/display; it does **not** justify fabricating server credits. Cryptographically signed test fixtures exercise the callback and the DB integration test exercises duplicate rewards/redemption. For an end-to-end device/Google callback test, register your own rewarded unit, configure its public HTTPS SSV URL `/ssv`, register the test device in AdMob, and use test mode. Only after that passes and production policy/consent review is complete should a reviewed code change select real production IDs. Shared test-ad completions may remain pending rather than minting unverified credits.

## GitHub Actions and release signing

Workflow `Android app · build and verify` runs only on Android changes. Existing Pages workflow ignores Android-only commits, preventing a site deployment from app work. Jobs:

- PostgreSQL 16 migration and integration/security tests.
- JDK 17 + Android SDK build, unit tests/lint, debug APK and test APK.
- Emulator launch/FLAG_SECURE instrumentation test.
- Signed release AAB only when keystore secrets exist.

Download `Nihongo-Path-Books-debug-APK` from the successful workflow run's Artifacts area. GitHub requires login to download artifacts. APK is debug signed and targets Android 6.0+ (API 23+); use the AAB for Play after signing setup.

Repository variable: `BOOKS_API_URL` (public HTTPS API origin).
Repository secrets: `ANDROID_KEYSTORE_BASE64`, `ANDROID_STORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`. Protect/backup the keystore outside Git. Never send secret values in chat. AAB is only generated with signing configured.

## Tests and limits

```sh
cd android-app/backend
npm ci
TEST_DATABASE_URL=postgresql://... npm test   # disposable migrated PostgreSQL database
TEST_DATABASE_URL=pglite npm test           # embedded PostgreSQL WASM; same SQL/logic
```

Tests cover authentication, invalid sessions/passwords, cross-user RLS, unfinished sessions, concurrent duplicate grants, session reuse, signed timestamp rejection, insufficient credits, idempotent redeem, active unlock preservation, expiry, unused credits and persistence across server connections. Crypto tests reject tampered signatures, duplicated callback parameters and wrong ad units. Android unit tests cover origin restrictions and time arithmetic; instrumentation asserts FLAG_SECURE at launch. An emulator flag test is not a claim that every vendor's recording implementation was tested.

FLAG_SECURE blocks ordinary screenshots/recording where Android supports it. External cameras, modified devices and extraction of material that is already public on the existing website cannot be fully prevented. This project does not alter or privatize the live site. Content held in reader memory after a valid request is cleared when the reader is destroyed, but Android app security is not DRM against a hostile OS.

Before public launch: deploy API/DB; run Google SSV device test; verify listening commercial rights and any target-audience requirements; publish an app-specific privacy URL and support/account-deletion webpage; add account recovery/email verification and production auth abuse monitoring; complete Play Data Safety/ads declarations; test Japanese TTS, PDF workers, real login/ad no-fill/offline/resume/expiry and capture behavior on physical Android devices. Review a production release separately. No successful external setup or physical-device result is claimed by source code alone.

## Device compatibility

Version 1.0.2 lowers the OS floor to API 23, the minimum supported by the selected Google Mobile Ads v24 SDK. No CPU ABI or screen-size filter is configured. The app uses native Kotlin/JVM code; packaging checks verify APK signatures and alignment. CI installs and launches the app on API 23 (32-bit x86), API 29 and API 35 (64-bit x86_64), including FLAG_SECURE assertions. These emulators do not prove compatibility with every physical device or ARM chipset.

Keep Android System WebView/Chrome updated for the book reader. Google ad availability depends on Google services, consent, region and fill; missing ads must not block free study or remove credits. Android versions below 6.0 are unsupported. Installation failure must be diagnosed from Package Installer/ADB output, rather than assumed to be an OS or CPU problem. Debug, local release and Play-signed packages may have different signing certificates; they cannot replace each other without matching signatures. Preserve the same release signing key for updates. Uninstalling an app clears its local data, so do not recommend uninstall as a silent repair.
