#!/usr/bin/env python3
"""Optionally refit selected public EEG inputs using HP-GSBS 0.2.0; never run official GSBS."""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMBA_NUM_THREADS'):
    os.environ[name]='1'
import argparse
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recordings',type=int,nargs='+',choices=range(4),default=list(range(4)),help='Zero-based fixture IDs')
    parser.add_argument('--backend',choices=['cpu-fast','torch-cuda','triton-cuda'],default='cpu-fast')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Choose a new output directory.')
    from hpgsbs import fit,GSBSConfig,__version__
    if __version__!='0.2.0':
        raise RuntimeError('Install the fixed HP-GSBS 0.2.0 release.')
    provenance=json.loads((ROOT/'data/eeg/provenance.json').read_text())
    args.output.mkdir(parents=True)
    reports=[]
    for r in provenance['records']:
        if r['fixture_id'] not in args.recordings:
            continue
        with np.load(ROOT/r['input'],allow_pickle=False) as inp:
            x=inp['x'].astype(np.float64);times=inp['times']
        cfg=GSBSConfig(**r['gsbs_parameters'],dtype='float64',q_strategy='full',
                       candidate_backend='streaming',td_backend='prefix2d',blas_threads=1,numba_threads=1)
        result=fit(x,cfg,backend=args.backend)
        if result.metadata.get('backend')!=args.backend or result.metadata.get('fallback_reason'):
            raise RuntimeError('The requested backend did not execute.')
        target=args.output/f"recording_{r['fixture_id']}_{args.backend}.npz"
        result.save(target,times=times)
        with np.load(ROOT/r['comparison_reference'],allow_pickle=False) as ref, np.load(target,allow_pickle=False) as actual:
            for key in ('x','all_bounds','nstates','bounds','deltas','states','state_durations_samples'):
                np.testing.assert_array_equal(actual[key],ref[key])
            for key in ('tdists','state_patterns','strengths'):
                np.testing.assert_allclose(actual[key],ref[key],atol=1e-8,rtol=1e-8,equal_nan=False)
            reports.append(dict(fixture_id=r['fixture_id'],passed=True,backend=args.backend,software_version=__version__,
                                selected_K=int(actual['nstates']),reference_type=r['comparison_reference_type'],
                                max_absolute_tdistance_error=float(np.max(np.abs(actual['tdists']-ref['tdists'])))))
    report=dict(passed=True,scope='New HP-only executions, separate from historical measurements',records=reports)
    (args.output/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()
