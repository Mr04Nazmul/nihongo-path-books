#!/bin/bash
# Use a dedicated ephemeral macOS runner. Never enable shell xtrace here.
set -euo pipefail
umask 077
: "${NIHONGO_IOS_P12_FILE:?Path to Apple Distribution p12 is required}"
: "${NIHONGO_IOS_P12_PASSWORD:?p12 password is required}"
: "${NIHONGO_IOS_PROFILE_FILE:?Path to distribution mobileprovision is required}"
: "${NIHONGO_IOS_TEAM_ID:?Apple developer team ID is required}"
NIHONGO_IOS_EXPORT_METHOD="${NIHONGO_IOS_EXPORT_METHOD:-app-store-connect}"
[[ "$(uname -s)" == Darwin ]] || { echo 'Run on macOS with Xcode 26+.' >&2; exit 1; }
command -v xcodegen >/dev/null
project_root="$(cd "$(dirname "$0")/.." && pwd)"
task_sign_dir="$(mktemp -d)"
task_keychain="$task_sign_dir/signing.keychain-db"
task_keychain_password="$(openssl rand -hex 24)"
installed_profile=''
task_original_keychains=()
while IFS= read -r item; do task_original_keychains+=("$item"); done < <(python3 -c 'import subprocess,shlex; print(chr(10).join(shlex.split(subprocess.check_output(["security","list-keychains","-d","user"],text=True))))')
cleanup() {
  if [[ ${#task_original_keychains[@]} -gt 0 ]]; then security list-keychains -d user -s "${task_original_keychains[@]}" >/dev/null 2>&1 || true; fi
  security delete-keychain "$task_keychain" >/dev/null 2>&1 || true
  if [[ -n "$installed_profile" ]]; then rm -f "$installed_profile"; fi
  rm -rf "$task_sign_dir"
}
trap cleanup EXIT
security cms -D -i "$NIHONGO_IOS_PROFILE_FILE" > "$task_sign_dir/profile.plist"
python3 "$project_root/scripts/signing_options.py" "$task_sign_dir/profile.plist" "$NIHONGO_IOS_TEAM_ID" "$NIHONGO_IOS_EXPORT_METHOD" "$task_sign_dir/ExportOptions.plist"
profile_uuid="$(/usr/libexec/PlistBuddy -c 'Print UUID' "$task_sign_dir/profile.plist")"
security create-keychain -p "$task_keychain_password" "$task_keychain"
security list-keychains -d user -s "$task_keychain" "${task_original_keychains[@]}"
security set-keychain-settings -lut 21600 "$task_keychain"
security unlock-keychain -p "$task_keychain_password" "$task_keychain"
security import "$NIHONGO_IOS_P12_FILE" -P "$NIHONGO_IOS_P12_PASSWORD" -A -t cert -f pkcs12 -k "$task_keychain" >/dev/null
security set-key-partition-list -S apple-tool:,apple:,codesign: -k "$task_keychain_password" "$task_keychain" >/dev/null
mkdir -p "$HOME/Library/MobileDevice/Provisioning Profiles"
installed_profile="$HOME/Library/MobileDevice/Provisioning Profiles/$profile_uuid.mobileprovision"
[[ ! -e "$installed_profile" ]] || { echo 'A profile with this UUID already exists; use an ephemeral runner.' >&2; installed_profile=''; exit 1; }
cp "$NIHONGO_IOS_PROFILE_FILE" "$installed_profile"
cd "$project_root"
xcodegen generate
xcodebuild -project NihongoPath.xcodeproj -scheme NihongoPath -configuration Release -destination 'generic/platform=iOS' -archivePath build/NihongoPath-Signed.xcarchive CODE_SIGNING_ALLOWED=YES CODE_SIGN_STYLE=Manual DEVELOPMENT_TEAM="$NIHONGO_IOS_TEAM_ID" CODE_SIGN_IDENTITY='Apple Distribution' PROVISIONING_PROFILE_SPECIFIER="$profile_uuid" OTHER_CODE_SIGN_FLAGS="--keychain $task_keychain" archive
xcodebuild -exportArchive -archivePath build/NihongoPath-Signed.xcarchive -exportOptionsPlist "$task_sign_dir/ExportOptions.plist" -exportPath build/signed-ipa
codesign --verify --deep --strict build/NihongoPath-Signed.xcarchive/Products/Applications/NihongoPath.app
printf 'Signed export is in %s/build/signed-ipa\n' "$project_root"
