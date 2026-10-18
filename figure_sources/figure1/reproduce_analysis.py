"""Re-run the real-data figure example without overwriting the supplied results."""
from pathlib import Path
import os,json
for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMBA_NUM_THREADS']:
    os.environ[name]='1'
import numpy as np
from hpgsbs import fit,GSBSConfig,__version__
ROOT=Path(__file__).resolve().parent
assert __version__=='0.2.0',__version__
d=np.load(ROOT/'data/Sherlock_AG_120TR.npz')
cfg=GSBSConfig(kmax=30,dmin=1,trace=True)
hp=fit(d['x'],cfg,backend='cpu-fast')
ref=fit(d['x'],cfg,backend='reference')
assert np.array_equal(hp.all_bounds,ref.all_bounds)
assert np.array_equal(hp.all_bounds,d['all_bounds'])
assert np.allclose(hp.tdists,ref.tdists,atol=1e-8,rtol=1e-8)
np.savez_compressed(ROOT/'data/recomputed_outputs.npz',all_bounds=hp.all_bounds,tdists=hp.tdists,deltas=hp.deltas,nstates=hp.nstates)
print(json.dumps({'selected_K':int(hp.nstates),'boundaries':np.flatnonzero(hp.deltas).tolist(),
 'all_boundaries_equal':True,'max_absolute_td_error':float(np.max(np.abs(hp.tdists-ref.tdists)))},indent=2))
