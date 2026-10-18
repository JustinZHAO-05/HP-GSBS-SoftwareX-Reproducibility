#!/usr/bin/env python3
"""Rerun the paper's paired benchmark on a new machine into a NEW directory.

This is a portable reimplementation of the recorded measurement protocol,
not a remeasurement used in the supplied manuscript. It never overwrites
archived observations. The full four-route run requires NVIDIA CUDA/Triton.
"""
from __future__ import annotations
import os
for _key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
             'NUMBA_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_key] = '1'
import argparse
from contextlib import ExitStack
from dataclasses import asdict
import importlib.metadata
import json
from pathlib import Path
import platform
from time import perf_counter
from typing import Any
import numpy as np
from generate_inputs import make_input, fingerprint

CONDITIONS = [('T1',256,32,20), ('T2',512,32,20), ('T3',768,32,20),
              ('P1',512,8,20), ('P2',512,64,20), ('K1',512,32,10), ('K2',512,32,40)]
ROUTES = ('official','cpu-fast','torch-cuda','triton-cuda')
SEEDS = (20261017, 20261018)

def array_outputs(result: Any) -> dict[str, np.ndarray]:
    return {name:np.array(getattr(result,name),copy=True) for name in
            ('all_bounds','nstates','tdists','state_patterns','strengths')}

def compare_outputs(ref: dict, candidate: dict) -> dict:
    report: dict[str, Any] = {}
    for key in ('all_bounds','nstates'):
        report[key+'_equal'] = bool(np.array_equal(ref[key],candidate[key]))
    for key in ('tdists','state_patterns','strengths'):
        a,b = ref[key],candidate[key]
        if a.shape != b.shape:
            report[key+'_close'] = False
            report[key+'_max_abs_error'] = None
            continue
        valid = np.isfinite(a)&np.isfinite(b)
        nonfinite_equal = all(np.array_equal(f(a),f(b)) for f in
                              (np.isnan,np.isposinf,np.isneginf))
        report[key+'_close'] = bool(nonfinite_equal and np.allclose(a,b,atol=1e-8,rtol=1e-8,equal_nan=True))
        report[key+'_max_abs_error'] = float(np.max(np.abs(a[valid]-b[valid]))) if valid.any() else None
    report['passed'] = all(report[k] for k in report if k.endswith(('_equal','_close')))
    return report

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--only',nargs='*',choices=[x[0] for x in CONDITIONS])
    p.add_argument('--backends',nargs='+',choices=ROUTES,default=list(ROUTES))
    a=p.parse_args()
    if 'official' not in a.backends:
        p.error('The paired protocol requires the official reference.')
    if a.output.exists():
        raise FileExistsError('Choose a new output directory; archived data will not be replaced.')
    import hpgsbs
    from hpgsbs import GSBSConfig,fit
    from statesegmentation import GSBS
    from threadpoolctl import threadpool_limits
    import numba
    if hpgsbs.__version__!='0.2.0' or importlib.metadata.version('statesegmentation')!='0.0.6':
        raise RuntimeError('Install HP-GSBS 0.2.0 and statesegmentation 0.0.6 for this protocol.')
    need_gpu=any(r.endswith('cuda') for r in a.backends)
    torch=None
    if need_gpu:
        import torch
        if not torch.cuda.is_available():
            raise RuntimeError('CUDA unavailable; select --backends official cpu-fast for a partial CPU run.')
        if 'triton-cuda' in a.backends:
            import triton  # noqa: F401
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)
        torch.backends.cuda.matmul.allow_tf32=False
        torch.backends.cudnn.allow_tf32=False
    numba.set_num_threads(1)
    def synchronize():
        if torch is not None: torch.cuda.synchronize()
    def configuration(k):
        return GSBSConfig(kmax=k,statewise_detection=True,finetune=1,finetune_order=True,
                          blocksize=50,dmin=1,dtype='float64',q_strategy='full',
                          candidate_backend='streaming',td_backend='prefix2d',
                          blas_threads=1,numba_threads=1,trace=False)
    def invoke(x,c,route):
        if route=='official':
            model=GSBS(x=x,**c.algorithm())
            model.fit(showProgressBar=False)
            return model
        r=fit(x,c,backend=route)
        if r.metadata.get('backend')!=route or r.metadata.get('fallback_reason'):
            raise RuntimeError('Requested route fell back; record separately from primary timing.')
        return r
    a.output.mkdir(parents=True)
    versions={n:importlib.metadata.version(n) for n in
              ('numpy','scipy','numba','statesegmentation','hpgsbs')}
    if torch is not None: versions.update(torch=torch.__version__,cuda=torch.version.cuda)
    protocol=dict(versions=versions,platform=platform.platform(),python=platform.python_version(),
                  routes=a.backends,seeds=SEEDS,threads=1,tf32=False,
                  scope='New execution; not part of archived manuscript measurements',
                  official_repeats=1,hp_warmups=1,hp_timed_repeats=3,
                  timer='Constructor/public fit plus computation and transfers; validation and I/O excluded')
    (a.output/'protocol.json').write_text(json.dumps(protocol,indent=2))
    rows=[]
    def save():
        tmp=a.output/'trials.tmp'
        tmp.write_text(json.dumps(rows,indent=2))
        tmp.replace(a.output/'trials.json')
    with threadpool_limits(1):
        # Independent initialization input, outside the measured observations.
        x0=make_input(80,16,20261016)
        for route in a.backends: invoke(x0,configuration(8),route)
        for ci,(name,T,P,K) in enumerate(CONDITIONS):
            if a.only and name not in a.only: continue
            for si,seed in enumerate(SEEDS):
                x=make_input(T,P,seed);c=configuration(K)
                order=list(ROUTES);offset=(ci+2*si)%4
                order=order[offset:]+order[:offset]
                order=[r for r in order if r in a.backends]
                ref=None;pending=[]
                try:
                    for route in order:
                        for iteration in range(1 if route=='official' else 4):
                            synchronize();start=perf_counter();result=invoke(x,c,route)
                            synchronize();elapsed=perf_counter()-start
                            outputs=array_outputs(result)
                            row=dict(condition=name,T=T,P=P,Kmax=K,seed=seed,backend=route,
                                     iteration=iteration,warmup=route!='official' and iteration==0,
                                     wall_s=elapsed,input_sha256=fingerprint(x))
                            rows.append(row);pending.append((row,outputs));save()
                            if route=='official':ref=outputs
                    assert ref is not None
                    for row,output in pending:
                        row['comparison']=compare_outputs(ref,output)
                        if not row['comparison']['passed']:
                            save();raise AssertionError(f'Numerical mismatch: {name}, seed {seed}, {row["backend"]}')
                    save();print(name,seed,'all outputs agree',flush=True)
                except Exception as exc:
                    rows.append(dict(condition=name,seed=seed,status='failed',error=repr(exc)))
                    save();raise
    print(f'New results saved to {a.output.resolve()}')

if __name__=='__main__':
    main()
