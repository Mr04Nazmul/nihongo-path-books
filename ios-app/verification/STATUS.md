# Verification status — 2026-11-16

- Passed: 10 JavaScript syntax checks covering standalone and inline reader scripts.
- Passed: all bundled JSON parses, privacy manifest XML/plist parse and project YAML parse.
- Passed: N2–N5 lesson previews contain vocabulary, grammar and kanji; each level's first ten kanji has a bundled parseable stroke JSON (40 total).
- Not run: Swift/iOS compilation. Xcode/macOS is unavailable locally. GitHub upload required to run the added macOS workflow was rejected by automatic approval review because the payload includes Drive-derived source going to a public repository.
- Not run: native iPhone/simulator runtime, login/Google sign-in, protected server content, unlock expiry, voice and progress synchronization.
- Browser smoke attempted but did not run: Chromium launch blocked by process socket restrictions. No successful browser or screenshot claim is made.
- No IPA, Apple signing, Apple submission, Uptodown submission or publication completed.

The source is an initial port. Rewarded ads, listening/mock tests, referral UI, streak and notifications remain outside this implemented version. Release gates are in README.md.
