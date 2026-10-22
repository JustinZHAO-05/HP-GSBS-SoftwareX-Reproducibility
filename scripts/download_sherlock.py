"""Retrieve and verify the version-1 Sherlock angular-gyrus analysis input."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
import numpy as np

URL = 'https://ndownloader.figshare.com/files/22927253'
SIZE = 256101248
MD5 = 'f80dde9a451e140c39b98c2e5214d93c'

def check(path):
    if path.stat().st_size != SIZE:
        raise ValueError('Source byte count differs from the versioned input.')
    digest = hashlib.md5()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    if digest.hexdigest() != MD5:
        raise ValueError('Source MD5 differs from the versioned input.')
    data = np.load(path, mmap_mode='r', allow_pickle=False)
    if data.shape != (16, 946, 4230) or data.dtype != np.dtype('float32'):
        raise ValueError('Source shape or dtype differs from the versioned input.')
    return dict(bytes=SIZE, md5=MD5, shape=list(data.shape), dtype=str(data.dtype))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    if not args.output.exists() and not args.check_only:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_suffix('.download')
        try:
            with urllib.request.urlopen(URL, timeout=60) as source, temporary.open('wb') as dest:
                for chunk in iter(lambda: source.read(8 * 1024 * 1024), b''):
                    dest.write(chunk)
            check(temporary)
            temporary.replace(args.output)
        finally:
            temporary.unlink(missing_ok=True)
    print(json.dumps(check(args.output), indent=2))
