"""Validate a decoded Apple profile and write manual export options; no network."""
import datetime
import plistlib
import sys
import uuid
import re
from pathlib import Path

BUNDLE = 'online.devnazu.books.NihongoPath'

def options(profile, team, method, now=None):
    if method not in ('app-store-connect', 'release-testing'):
        raise ValueError('Choose app-store-connect or release-testing')
    if not re.fullmatch(r'[A-Z0-9]{10}', team):
        raise ValueError('Invalid Apple team ID')
    uuid.UUID(profile.get('UUID', ''))
    if team not in profile.get('TeamIdentifier', []):
        raise ValueError('Apple team does not match provisioning profile')
    entitlements = profile.get('Entitlements', {})
    if entitlements.get('application-identifier') != team + '.' + BUNDLE:
        raise ValueError('Use an explicit profile for ' + BUNDLE)
    if entitlements.get('get-task-allow', False):
        raise ValueError('A distribution profile is required, not development')
    expiry = profile.get('ExpirationDate')
    if not isinstance(expiry, datetime.datetime):
        raise ValueError('Profile has no valid expiration date')
    expiry = expiry.replace(tzinfo=expiry.tzinfo or datetime.timezone.utc)
    if expiry <= (now or datetime.datetime.now(datetime.timezone.utc)):
        raise ValueError('Provisioning profile has expired')
    if profile.get('ProvisionsAllDevices'):
        raise ValueError('Enterprise distribution is not supported by this script')
    devices = profile.get('ProvisionedDevices', [])
    if (method == 'release-testing') != bool(devices):
        raise ValueError('Export method does not match App Store / registered-device profile')
    if not profile.get('UUID') or not profile.get('DeveloperCertificates'):
        raise ValueError('Profile certificate or UUID is missing')
    return {'method': method, 'teamID': team, 'signingStyle': 'manual',
            'signingCertificate': 'Apple Distribution', 'destination': 'export',
            'provisioningProfiles': {BUNDLE: profile['UUID']}}

if __name__ == '__main__':
    profile_path, team, method, output_path = sys.argv[1:]
    result = options(plistlib.loads(Path(profile_path).read_bytes()), team, method)
    Path(output_path).write_bytes(plistlib.dumps(result))
