#!/usr/bin/env python3
"""Harmless updater experiment: only runs either of two bundled, pinned hashes."""
import argparse,hashlib,json,os,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path
BASE='https://raw.githubusercontent.com/elichen/adf-updater-probe/main/'
HASHES={'v1': 'd41f0ac81d66863c6410fa2959fda3048ca564b0e0a40a665b66c54948342613', 'v2': '53945c8fd3b7a1dfc3f230176a4d5fb29a292d6fb79aa93a4dd891d0ed644768'}
parser=argparse.ArgumentParser()
parser.add_argument('--channel',choices=['live','v1','v2'],default='live')
args=parser.parse_args()
start=time.monotonic()
root=Path(os.environ.get('ADF_PROBE_STATE_DIR',str(Path.home()/'.cache'/'adf-updater-probe-726491')))
root.mkdir(parents=True,exist_ok=True)
def download(path):
    with urllib.request.urlopen(BASE+path,timeout=30) as response:
        return response.read()
version=json.loads(download('channel.json'))['version'] if args.channel=='live' else args.channel
if version not in HASHES: raise SystemExit('Unknown release rejected')
target=root/(version+'.py')
cached=target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==HASHES[version]
if not cached:
    data=download('releases/'+version+'.py')
    if hashlib.sha256(data).hexdigest()!=HASHES[version]: raise SystemExit('Release hash mismatch rejected')
    fd,tmp=tempfile.mkstemp(prefix='download-',dir=root)
    with os.fdopen(fd,'wb') as stream: stream.write(data)
    os.replace(tmp,target)
print(json.dumps({'launcher_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'selected_version':version,'cache_hit':cached,'state_dir':str(root),'elapsed_ms':round((time.monotonic()-start)*1000)}),flush=True)
subprocess.run([sys.executable,str(target)],check=True)
