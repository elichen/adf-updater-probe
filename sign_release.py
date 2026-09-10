"""Create a synthetic release. Supply an external experiment-only RSA private key."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import secrets
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('version')
parser.add_argument('--private-key', required=True)
args = parser.parse_args()
if not re.fullmatch(r'v[1-9][0-9]{0,8}', args.version):
    raise SystemExit('Invalid version')
root = Path(__file__).parent
marker = secrets.token_hex(16)
runtime = ('import json\nprint(json.dumps(' + repr({'runtime_version': args.version, 'verification_marker': marker}) + '))\n').encode()
digest = hashlib.sha256(runtime).hexdigest()
payload = json.dumps({'version': args.version, 'sha256': digest}, sort_keys=True, separators=(',', ':')).encode()
signature = subprocess.run(['openssl', 'dgst', '-sha256', '-sign', args.private_key], input=payload, capture_output=True, check=True).stdout
(root / 'signed-releases' / (digest + '.py')).write_bytes(runtime)
(root / 'signed-channel.json').write_text(json.dumps({'payload': base64.b64encode(payload).decode(), 'signature': base64.b64encode(signature).decode()}) + '\n')
print(json.dumps({'version': args.version, 'sha256': digest, 'verification_marker': marker}))
