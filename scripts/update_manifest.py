"""Regenerate complete-file SHA-256 entries after staging release files."""
from pathlib import Path
import hashlib
import subprocess

ROOT=Path(__file__).resolve().parents[1]
names=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
rows=[]
for name in sorted(set(names)-{'','SHA256SUMS.txt'}):
    path=ROOT/name
    rows.append(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+name)
(ROOT/'SHA256SUMS.txt').write_text('\n'.join(rows)+'\n')
print(f'Wrote {len(rows)} release file hashes.')
