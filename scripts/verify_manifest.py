#!/usr/bin/env python3
"""Validate SHA-256 hashes of the released source and data snapshot."""
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    count = 0
    failures = []
    names = set()
    for line in (ROOT / 'SHA256SUMS.txt').read_text().splitlines():
        expected, name = line.split('  ', 1)
        if name in names:
            raise AssertionError('Duplicate manifest entry: ' + name)
        names.add(name)
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            failures.append(name)
        count += 1
    if failures:
        raise AssertionError('Missing or modified release files: ' + ', '.join(failures))
    if (ROOT/'.git').exists():
        tracked = set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')) - {'','SHA256SUMS.txt'}
        if tracked != names:
            raise AssertionError('Manifest coverage differs from tracked files: ' + repr(sorted(tracked ^ names)))
    print(f'All {count} release file hashes match.')


if __name__ == '__main__':
    main()
