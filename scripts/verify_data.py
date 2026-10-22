#!/usr/bin/env python3
"""Check the delivered numerical tables against recorded observations; no fits."""
from __future__ import annotations
import json
import runpy
from pathlib import Path
import numpy as np
import pandas as pd
from generate_inputs import check_inputs, fingerprint

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    D = ROOT/'data'
    raw = pd.read_csv(D/'paired_timed_runs.csv')
    per = pd.read_csv(D/'paired_per_input.csv')
    runtime = pd.read_csv(D/'paired_runtime.csv')
    speed = pd.read_csv(D/'paired_speedup.csv')
    assert len(raw) == 140 and len(per) == 56
    assert raw.wall_s.gt(0).all()
    assert sum(raw.backend.eq('official')) == 14
    for row in per.itertuples():
        values = raw[(raw.condition == row.condition) & (raw.seed == row.seed) &
                     (raw.backend == row.backend)].wall_s.to_numpy()
        assert len(values) == (1 if row.backend == 'official' else 3)
        np.testing.assert_allclose(np.median(values), row.median_s, rtol=2e-13, atol=1e-13)
        ref = raw[(raw.condition == row.condition) & (raw.seed == row.seed) &
                  raw.backend.eq('official')].wall_s.iloc[0]
        np.testing.assert_allclose(ref/np.median(values), row.speedup, rtol=2e-13)
    for row in runtime.itertuples():
        a = per[(per.condition == row.condition) & (per.backend == row.backend)].median_s
        np.testing.assert_allclose([a.median(), a.min(), a.max()],
                                   [row.median_s, row.min_s, row.max_s], rtol=2e-13, atol=1e-13)
    for row in speed.itertuples():
        a = per[(per.condition == row.condition) & (per.backend == row.backend)].speedup
        np.testing.assert_allclose([a.median(), a.min(), a.max()],
                                   [row.median, row.min, row.max], rtol=2e-13)
    n_inputs = check_inputs()
    with np.load(D/'synthetic_figure_data.npz', allow_pickle=False) as a:
        assert fingerprint(a['x']) == '70fd8c633b9eb0e9188e7339910a7f417f726074aaaa1943849cf16ba7f485f6'
        reference = a['official__tdists']
        errors = {}
        for route in ('cpu-fast', 'torch-cuda', 'triton-cuda'):
            errors[route] = float(np.max(np.abs(a[route+'__tdists']-reference)))
            assert int(a[route+'__nstates']) == 4
            if route+'__all_bounds' in a.files:
                np.testing.assert_array_equal(a[route+'__all_bounds'], a['official__all_bounds'])
        assert max(errors.values()) < 1.6e-11
    eeg = runpy.run_path(str(ROOT/'data/eeg/verify_eeg_all.py'))['verify']()
    fmri = runpy.run_path(str(ROOT/'scripts/verify_fmri.py'))['verify']()
    print(json.dumps(dict(passed=True, eeg_recordings_verified=len(eeg['records']), timed_observations=len(raw),
        configuration_seed_cases=14, distinct_inputs=n_inputs,
        synthetic_max_abs_tdistance_errors=errors,fmri=fmri,
        scope='Arithmetic and input-identity checks on supplied records; no model refit'), indent=2))

if __name__ == '__main__':
    main()
