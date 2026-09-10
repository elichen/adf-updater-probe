#!/usr/bin/env python3
"""Experimental signed release bootstrap, using OpenSSL rather than custom crypto."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

BASE = 'https://raw.githubusercontent.com/elichen/adf-updater-probe/main/'
LIMIT = 1024 * 1024


def download(path):
    request = urllib.request.Request(BASE + path, headers={'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError('Download exceeds probe size limit')
    return data


def verified_manifest(envelope, negative_test):
    payload = base64.b64decode(envelope['payload'], validate=True)
    signature = base64.b64decode(envelope['signature'], validate=True)
    if negative_test == 'signature':
        signature = bytes([signature[0] ^ 1]) + signature[1:]
    with tempfile.TemporaryDirectory(prefix='adf-signature-') as directory:
        location = Path(directory)
        (location / 'payload').write_bytes(payload)
        (location / 'signature').write_bytes(signature)
        result = subprocess.run([
            'openssl', 'dgst', '-sha256', '-verify',
            str(Path(__file__).with_name('release-public.pem')),
            '-signature', str(location / 'signature'), str(location / 'payload'),
        ], capture_output=True, timeout=10)
    if result.returncode:
        raise ValueError('Release signature rejected')
    manifest = json.loads(payload)
    if set(manifest) != {'version', 'sha256'}:
        raise ValueError('Unexpected manifest fields')
    if not isinstance(manifest['version'], str) or not re.fullmatch(r'v[1-9][0-9]{0,8}', manifest['version']):
        raise ValueError('Invalid release version')
    if not isinstance(manifest['sha256'], str) or not re.fullmatch(r'[a-f0-9]{64}', manifest['sha256']):
        raise ValueError('Invalid artifact hash')
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--negative-test', choices=['signature', 'artifact'])
    args = parser.parse_args()
    if not shutil.which('openssl'):
        raise ValueError('OpenSSL executable is required; no dependencies installed')
    start = time.monotonic()
    manifest = verified_manifest(json.loads(download('signed-channel.json')), args.negative_test)
    root = Path(os.environ.get('ADF_SIGNED_PROBE_STATE_DIR', str(Path.home() / '.cache' / 'adf-signed-probe-726491')))
    if args.negative_test:
        root = root.with_name(root.name + '-negative-' + args.negative_test)
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    digest = manifest['sha256']
    target = root / (digest + '.py')
    cached = target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == digest
    if not cached or args.negative_test == 'artifact':
        data = download('signed-releases/' + digest + '.py')
        if args.negative_test == 'artifact':
            data += b'\n# deliberately altered probe artifact\n'
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError('Runtime hash mismatch rejected')
        fd, temporary = tempfile.mkstemp(prefix='download-', dir=root)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data)
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    print(json.dumps({
        'launcher_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'public_key_sha256': hashlib.sha256(Path(__file__).with_name('release-public.pem').read_bytes()).hexdigest(),
        'selected_version': manifest['version'], 'signature_verified': True,
        'artifact_sha256': digest, 'cache_hit': cached,
        'state_dir': str(root), 'elapsed_ms': round((time.monotonic() - start) * 1000),
    }), flush=True)
    subprocess.run([sys.executable, str(target)], check=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        sys.exit(1)
