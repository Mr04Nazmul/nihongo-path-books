# Signed IPA preparation

The unsigned app has compiled and passed the two N5 reader UI tests. Apple signing has not run. This script prepares a signed export on a dedicated ephemeral macOS runner; it does not upload to Apple, publish to Uptodown, or purchase any membership.

Required private inputs:

- Apple Distribution identity exported as `.p12`, including its private key, and its password.
- Unexpired distribution provisioning profile for the explicit bundle ID `online.devnazu.books.NihongoPath` and the same Apple developer team.
- Apple team ID.

Store credentials in a secure secret manager or GitHub repository/environment secrets. Never place them in source, commits, issues, pull-request comments or chat. Secret access has not been configured in this project.

On macOS with Xcode 26+ and XcodeGen installed, set these environment variables from the secret manager:

```
NIHONGO_IOS_P12_FILE
NIHONGO_IOS_P12_PASSWORD
NIHONGO_IOS_PROFILE_FILE
NIHONGO_IOS_TEAM_ID
NIHONGO_IOS_EXPORT_METHOD
```

`NIHONGO_IOS_EXPORT_METHOD` is `app-store-connect` (default) or `release-testing` (registered-device distribution). A registered-device profile must already contain each tester's device. A signed App Store export is for Apple distribution, not arbitrary website installation.

Run `bash ios-app/scripts/export_signed_ipa.sh`. It validates profile team, bundle, expiry and distribution type before importing credentials into a temporary keychain, then archives, exports and verifies the signature. It restores the keychain search list and removes its imported profile/keychain when finished. IPA output is under `ios-app/build/signed-ipa`.

Validation performed here: shell syntax and six profile-validation fixture checks passed. An actual signed export is **not tested** because signing credentials are unavailable. Xcode must still verify that the supplied p12 matches the profile's distribution certificate.

Public release remains blocked on signing access, production iOS AdMob setup and the other feature/review gates listed in README.md. Uptodown publication needs a supported distribution URL/process; an unsigned archive cannot satisfy that requirement.

References:
- https://help.apple.com/xcode/mac/current/en.lproj/devcac6ab5b3.html
- https://docs.github.com/en/actions/how-tos/deploy/deploy-to-third-party-platforms/sign-xcode-applications
