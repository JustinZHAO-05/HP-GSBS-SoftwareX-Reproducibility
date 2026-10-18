#!/usr/bin/env python3
"""CPU example: fit, inspect, save/reload, and independently batch two inputs."""
from pathlib import Path
import tempfile
import numpy as np
from hpgsbs import GSBSConfig, GSBSResult, fit, fit_many

def main():
    rng=np.random.default_rng(19)
    x=np.repeat(rng.normal(size=(4,16)),20,axis=0)+0.05*rng.normal(size=(80,16))
    cfg=GSBSConfig(kmax=12,dmin=1,n_jobs=1)
    result=fit(x,cfg,backend='cpu-fast')
    bounds=result.get_bounds(result.nstates)
    curve=result.tdists
    out=Path(tempfile.mkdtemp(prefix='hpgsbs-workflow-'))/'recording.npz'
    result.save(out)
    restored=GSBSResult.load(out)
    assert np.array_equal(restored.all_bounds,result.all_bounds)
    assert np.allclose(restored.tdists,curve,equal_nan=True)
    batch=fit_many([x,x.copy()],cfg,backend='cpu-fast')
    assert len(batch)==2
    assert all(np.array_equal(r.all_bounds,result.all_bounds) for r in batch)
    print(f'Selected states: {result.nstates}; boundaries: {np.flatnonzero(bounds).tolist()}')
    print(f'Save/load and two-record CPU batch verified. Result: {out}')
if __name__=='__main__':
    main()
