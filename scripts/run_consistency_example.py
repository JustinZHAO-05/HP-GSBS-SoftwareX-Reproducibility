#!/usr/bin/env python3
"""Run the small recorded example and compare complete search/move traces.

CPU is the portable default. Choose --backends cpu-fast torch-cuda triton-cuda
on a suitable CUDA system to execute all three optimized routes.
"""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMBA_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import numpy as np

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--backends',nargs='+',choices=['cpu-fast','torch-cuda','triton-cuda'],default=['cpu-fast'])
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('Choose a new result directory.')
    from hpgsbs import fit,GSBSConfig,__version__
    from hpgsbs.validation import compare
    if __version__!='0.2.0':raise RuntimeError('This example targets HP-GSBS 0.2.0.')
    rng=np.random.default_rng(19)
    means=rng.normal(size=(4,16))
    x=np.repeat(means,20,axis=0)+0.05*rng.normal(size=(80,16))
    c=GSBSConfig(kmax=12,dmin=1,trace=True)
    ref=fit(x,c,backend='reference')
    outputs={'x':x,'state_means':means,'true_boundaries':np.array([20,40,60])}
    for key in ('all_bounds','nstates','tdists','state_patterns','strengths','deltas','bounds'):
        outputs['official__'+key]=np.asarray(getattr(ref,key))
    checks={}
    for route in a.backends:
        r=fit(x,c,backend=route)
        checks[route]=compare(ref,r,level='finetune-move-trace')
        if not checks[route]['passed']:raise AssertionError(checks[route])
        for key in ('all_bounds','nstates','tdists','state_patterns','strengths','deltas','bounds'):
            outputs[route+'__'+key]=np.asarray(getattr(r,key))
    a.output.mkdir(parents=True)
    np.savez_compressed(a.output/'synthetic_example.npz',**outputs)
    (a.output/'parity.json').write_text(json.dumps(checks,indent=2))
    print(json.dumps(dict(selected_K=int(ref.nstates),boundaries=np.flatnonzero(ref.deltas).tolist(),
                         all_trace_comparisons_passed=True),indent=2))

if __name__=='__main__':
    main()
