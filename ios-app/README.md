# Nihongo Path Books for iOS

Native SwiftUI iPhone/iPad client, iOS 16+. Reader UI and licensed previews are ported from the owner's Drive backup `Nihongo-Path-1.19.3-Maintenance-Backup.zip`, including its original Bengali corrections, KanjiVG animation, handwriting practice and fonts. This is an initial iOS port, not yet a signed production release.

## Implemented

- Bengali library, vocabulary/grammar details, search, saved/learned entries, kanji animation and handwriting using the existing reader.
- N5–N2 books; N1 remains Coming Soon.
- Native Japanese speech; appearance settings; app icon adapted from the existing Android book vector.
- Email registration/login and Google PKCE login using the existing backend. Session token stored in device-only Keychain; no service key bundled.
- Existing server unlocks and protected content, free offline previews, progress upload/restoration, logout and app-data deletion.
- Native resource bridge keeps bearer tokens out of JavaScript, blocks other levels/external fetches, confines local reads to the reader bundle.

## Build

On macOS with Xcode: install XcodeGen (`brew install xcodegen`), run `xcodegen generate`, open `NihongoPath.xcodeproj`, select the NihongoPath scheme. Choose an Apple development team before installing to a phone. The repository workflow compiles simulator and unsigned iPhone archive. An unsigned archive is not an installable IPA.

## Remaining release gates

1. Compile and run the iOS build in simulator and on an iPhone. Verify login, Google callback, server unlock expiry, reading, stroke playback, drawing, speech, settings and account data deletion against the live service. Linux checks do not certify these flows.
2. Apple Developer account, signing certificate/profile and distribution method. Never commit signing secrets. No membership purchase is authorized by this implementation.
3. Production iOS AdMob app/unit and approved server-side verification allowlist. No Android ad unit is reused, no simulated ad earns credits. The current iOS app explicitly shows that rewarded ads are pending.
4. For App Store submission with Google sign-in, review Apple's equivalent-login requirements and implement Sign in with Apple unless a documented exception applies. App-data deletion currently preserves the shared Supabase identity, matching Android backend behavior; review account-deletion compliance before App Store submission.
5. Listening/mock-test sections, referral UI, streak and native notifications have not been ported in this initial version.
6. Uptodown's observed Evri iOS listing redirects downloads to an external site. Its existence does not establish support for uploading an installable IPA. Confirm publication eligibility with Uptodown and supply a valid Apple distribution URL before claiming publication.

## Provenance

Source backup: Drive file `1FpkkwUJwOe2ycK-tjgf4eIdJfgrsazZ_`, version 1.19.3/code33, November 7, 2026. The backup describes reconstructed Java/Gradle from 1.19.1/code31; this iOS app ports the reader resources and API contract, not the reconstructed Android Java. Original license files are preserved under Resources/reader.
