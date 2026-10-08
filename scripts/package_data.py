#!/usr/bin/env python3
"""Reproducible independent draft data package and SHA-256 inventory."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '2026.10.08-draft.1'

def manifest():
    files = sorted(p for p in (ROOT / 'data').rglob('*') if p.is_file() and p.name != 'VERSION.json')
    return {'dataset_version':VERSION, 'compatible_engine':'0.1.0', 'status':'draft',
            'verified_rules':0, 'verified_feasible_routes':0, 'license':'CC-BY-4.0',
            'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--write-manifest',action='store_true');args=parser.parse_args()
    path=ROOT/'data/VERSION.json';expected=json.dumps(manifest(),ensure_ascii=False,indent=2)+'\n'
    if args.write_manifest: path.write_text(expected)
    if not path.is_file() or path.read_text()!=expected:raise SystemExit('Data version manifest drift: explicitly version/review data before updating')
    if args.check: print('Draft data manifest hashes verified');return
    out=ROOT/'dist';out.mkdir(exist_ok=True);buf=io.BytesIO()
    with tarfile.open(fileobj=buf,mode='w') as tar:
        for name in sorted([*manifest()['files'], 'data/VERSION.json','LICENSE-DATA','THIRD_PARTY_NOTICES.md','licenses/CC-BY-4.0.txt']):
            body=(ROOT/name).read_bytes();info=tarfile.TarInfo(name);info.size=len(body);info.mode=0o644;info.mtime=0;tar.addfile(info,io.BytesIO(body))
    dest=out/f'petwaymark-data-{VERSION}.tar.gz'
    with dest.open('wb') as f:
        with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as gz:gz.write(buf.getvalue())
    (out/'SHA256SUMS').write_text(hashlib.sha256(dest.read_bytes()).hexdigest()+'  '+dest.name+'\n')
    print(dest)
if __name__=='__main__':main()
