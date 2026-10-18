#!/usr/bin/env python3
"""Regenerate the recorded synthetic inputs, without running a GSBS fit."""
from __future__ import annotations
import argparse
import csv
import hashlib
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

def make_input(T: int, P: int, seed: int) -> np.ndarray:
    """Exactly the eight-state input recipe used in the source experiment."""
    if T < 8 or not 2 <= P <= 64:
        raise ValueError('Require T >= 8 and 2 <= P <= 64')
    rng = np.random.default_rng(seed)
    means = rng.normal(size=(8, 64))
    edges = np.rint(np.linspace(0, T, 9)).astype(int)
    labels = np.repeat(np.arange(8), np.diff(edges))
    x64 = means[labels] + 0.8 * rng.normal(size=(T, 64))
    return np.ascontiguousarray(x64[:, :P], dtype=np.float64)

def fingerprint(x: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(x, dtype='<f8').tobytes()).hexdigest()

def check_inputs(output: Path | None = None) -> int:
    if output is not None:
        output.mkdir(parents=True, exist_ok=True)
    seen: set[tuple[int, int, int]] = set()
    with (ROOT/'data/paired_inputs.csv').open(newline='') as handle:
        for row in csv.DictReader(handle):
            T, P, seed = (int(row[k]) for k in ('T', 'P', 'seed'))
            x = make_input(T, P, seed)
            if fingerprint(x) != row['input_sha256']:
                raise AssertionError(f"Input hash mismatch: {row['condition']}, seed={seed}")
            key = (T, P, seed)
            if output is not None and key not in seen:
                path = output/f'input_T{T}_P{P}_seed{seed}.npy'
                if path.exists():
                    existing = np.load(path, allow_pickle=False)
                    if fingerprint(existing) != fingerprint(x):
                        raise FileExistsError(f'Refusing to replace different input: {path}')
                else:
                    np.save(path, x, allow_pickle=False)
            seen.add(key)
    return len(seen)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional directory for regenerated NPY inputs')
    args = parser.parse_args()
    count = check_inputs(args.output)
    print(f'All 14 configuration/seed identities match ({count} distinct matrices).')

if __name__ == '__main__':
    main()
