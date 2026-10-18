#!/usr/bin/env python3
"""Check archived full-record EEG outputs; no fitting or raw-data download."""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'figure_sources/figure3/data'
FILES = {
    'official': '0_full_reference.npz',
    'cpu-fast': '0_full_cpu.npz',
    'torch-cuda': '0_torch-cuda_float64.npz',
    'triton-cuda': '0_triton-cuda_float64.npz',
}


def main():
    with np.load(DATA / FILES['official'], allow_pickle=False) as ref:
        assert ref['x'].shape == (1336, 64)
        assert int(ref['nstates']) == 126
        results = {}
        for backend, filename in FILES.items():
            with np.load(DATA / filename, allow_pickle=False) as fit:
                for key in ('x', 'all_bounds', 'nstates', 'bounds', 'states', 'deltas'):
                    np.testing.assert_array_equal(ref[key], fit[key])
                for key in ('tdists', 'state_patterns', 'strengths'):
                    np.testing.assert_allclose(ref[key], fit[key], rtol=1e-8, atol=1e-8, equal_nan=True)
                results[backend] = {
                    'all_boundaries_equal': True,
                    'selected_K': int(fit['nstates']),
                    'max_absolute_tdistance_error': float(np.max(np.abs(ref['tdists'] - fit['tdists']))),
                }
        path = DATA / 'sub-01_ses-01_stim01__all64__5.12hz__d5__k131.npz'
        with np.load(path, allow_pickle=False) as pipeline:
            np.testing.assert_array_equal(ref['x'], pipeline['x'])
            np.testing.assert_allclose(np.diff(pipeline['times']), 1 / 5.12)
            np.testing.assert_array_equal(pipeline['times'][np.flatnonzero(ref['bounds'])], pipeline['boundary_timestamps'])
    print(json.dumps({'passed': True, 'scope': 'Saved full-record outputs and time map', 'backends': results}, indent=2))


if __name__ == '__main__':
    main()
