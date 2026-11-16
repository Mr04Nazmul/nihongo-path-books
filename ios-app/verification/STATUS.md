# Verification status — 2026-11-16

Native validation runs on GitHub macOS, using Xcode 26 or later.

- Passed: iPhone simulator compilation.
- Passed: native UI test opens N5 vocabulary through the real WKWebView/native resource bridge and opens its Bengali detail.
- Passed: native UI test opens N5 kanji and handwriting board through the real native bridge.
- Passed previously: 10 JavaScript syntax checks, all preview JSON parses, project YAML/privacy manifest parses, 40 bundled stroke JSON checks across N2–N5.
- The unsigned iPhone archive is built by the same workflow after the UI tests pass.

Validated source commit: 99401e7f747c6c485cc0611f43b59aba953d23fd.
Build/test run: https://github.com/Mr04Nazmul/nihongo-path-books/actions/runs/43885381856

Not validated: physical iPhone installation, email/Google sign-in against a live user account, server unlock expiry and cloud progress synchronization. Apple signing access has not been supplied. No signed IPA, Apple submission, Uptodown submission or app publication is completed.

Rewarded ads, listening/mock tests, referral UI, streak and notifications are not implemented in this initial iOS port. These remain release scope, not completed features.
