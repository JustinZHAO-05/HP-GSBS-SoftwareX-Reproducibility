#!/usr/bin/env python3
"""Run a new CPU fit on the public frozen EEG matrix and compare saved outputs."""
import os
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMBA_NUM_THREADS'):
    os.environ[name] = '1'
import argparse
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Choose a new output directory.')
    from hpgsbs import fit, GSBSConfig, __version__
    if __version__ != '0.2.0':
        raise RuntimeError('Use the fixed HP-GSBS 0.2.0 release.')
    with np.load(ROOT / 'figure_sources/figure3/data/0_full_reference.npz', allow_pickle=False) as ref:
        x = np.array(ref['x'], copy=True)
        meta = json.loads(str(ref['metadata']))
        cfg = GSBSConfig(**meta['algorithm'], dtype='float64', q_strategy='full',
                         candidate_backend='streaming', td_backend='prefix2d',
                         blas_threads=1, numba_threads=1)
        result = fit(x, cfg, backend='cpu-fast')
        if result.metadata.get('backend') != 'cpu-fast' or result.metadata.get('fallback_reason'):
            raise RuntimeError('The requested CPU backend did not execute.')
        np.testing.assert_array_equal(result.all_bounds, ref['all_bounds'])
        assert int(result.nstates) == int(ref['nstates'])
        np.testing.assert_allclose(result.tdists, ref['tdists'], atol=1e-8, rtol=1e-8)
        report = {'passed': True, 'software_version': __version__, 'backend': 'cpu-fast',
                  'selected_K': int(result.nstates), 'all_boundaries_equal': True,
                  'max_absolute_tdistance_error': float(np.max(np.abs(result.tdists-ref['tdists']))),
                  'scope': 'New CPU execution compared with archived full-record reference'}
    args.output.mkdir(parents=True)
    np.savez_compressed(args.output / 'outputs.npz', all_bounds=result.all_bounds,
                        nstates=result.nstates, tdists=result.tdists)
    (args.output / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
