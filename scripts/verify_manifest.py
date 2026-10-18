#!/usr/bin/env python3
"""Validate SHA-256 hashes of the released source and data snapshot."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    count = 0
    failures = []
    for line in (ROOT / 'SHA256SUMS.txt').read_text().splitlines():
        expected, name = line.split('  ', 1)
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            failures.append(name)
        count += 1
    if failures:
        raise AssertionError('Missing or modified release files: ' + ', '.join(failures))
    print(f'All {count} release file hashes match.')


if __name__ == '__main__':
    main()
