#!/usr/bin/env python3
"""Independently verify all frozen EEG inputs and FP64 outputs; never fit a model."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/eeg'
EXACT = ('x', 'all_bounds', 'nstates', 'bounds', 'deltas', 'states', 'state_durations_samples')
FLOAT = ('tdists', 'state_patterns', 'strengths')

def require(ok, message):
    if not ok:
        raise AssertionError(message)

def array_sha(a, dtype):
    return hashlib.sha256(np.asarray(a, dtype=dtype).tobytes(order='C')).hexdigest()

def npy_sha(a):
    stream = io.BytesIO()
    np.save(stream, a, allow_pickle=False)
    return hashlib.sha256(stream.getvalue()).hexdigest()

def load(path):
    with np.load(ROOT/path, allow_pickle=False) as z:
        return {k:z[k] for k in z.files if k != 'trace'}

def compare(fit, reference):
    for key in EXACT:
        np.testing.assert_array_equal(fit[key], reference[key], err_msg=key)
    for key in FLOAT:
        require(fit[key].shape == reference[key].shape, f'Shape: {key}')
        np.testing.assert_array_equal(np.isfinite(fit[key]), np.isfinite(reference[key]))
        require(np.isfinite(fit[key]).all(), f'Nonfinite values: {key}')
        np.testing.assert_allclose(fit[key], reference[key], rtol=1e-8, atol=1e-8, equal_nan=False, err_msg=key)
    return {key:float(np.max(np.abs(fit[key]-reference[key]))) for key in FLOAT}

def verify():
    provenance = json.loads((DATA/'provenance.json').read_text())
    hashes = json.loads((DATA/'file_hashes.json').read_text())
    for name, expected in hashes.items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected, f'File hash: {name}')
    records=[]
    for r in provenance['records']:
        source=load(r['input']); x=source['x'].astype(np.float64);times=source['times']
        require(list(x.shape)==r['shape'], 'Input shape')
        require(str(source['x'].dtype)==r['input_stored_dtype'], 'Stored dtype')
        require(np.isfinite(x).all() and np.isfinite(times).all(), 'Finite input/time')
        require(times.shape==(len(x),) and np.all(np.diff(times)>0), 'Monotonic time map')
        np.testing.assert_allclose(np.diff(times),1/r['sampling_frequency_hz'],rtol=0,atol=1e-12)
        np.testing.assert_allclose([times[0],times[-1]], [r['bin_center_start_s'],r['bin_center_end_s']],rtol=0,atol=1e-12)
        require(array_sha(x,'<f8')==r['hashes']['fit_array_float64_C_sha256'], 'Fit value hash')
        require(array_sha(x,'<f4')==r['hashes']['fixture_array_float32_C_sha256'], 'Fixture value hash')
        require(array_sha(times,'<f8')==r['hashes']['times_array_float64_C_sha256'], 'Time value hash')
        require(npy_sha(x.astype('<f4'))==r['hashes']['fixture_npy_file_sha256'], 'Reconstructed source NPY hash')
        require(npy_sha(times)==r['hashes']['times_npy_file_sha256'], 'Reconstructed source time NPY hash')
        reference=load(r['comparison_reference']);backends={}
        for backend, path in r['outputs'].items():
            fit=load(path);meta=json.loads(str(fit['metadata']))
            require(meta['algorithm']==r['gsbs_parameters'], 'Algorithm settings')
            require(meta['precision']=='float64' and fit['x'].dtype==np.float64, 'FP64 output')
            require(meta['status']=='success', 'Archived execution status')
            np.testing.assert_array_equal(x,fit['x'])
            require(fit['all_bounds'].shape==(r['gsbs_parameters']['kmax']+2,len(x)), 'Boundary history shape')
            k=int(fit['nstates'])
            require(k==r['selected_K'] and k==int(np.argmax(fit['tdists'])), 'Selected K')
            require(fit['state_patterns'].shape==(k,x.shape[1]), 'State-pattern shape')
            require(fit['bounds'].shape==fit['deltas'].shape==fit['states'].shape==fit['strengths'].shape==(len(x),), 'Time-series shape')
            edges=np.r_[0,np.flatnonzero(fit['deltas']),len(x)]
            np.testing.assert_array_equal(np.diff(edges),fit['state_durations_samples'])
            require(len(edges)-1==k, 'Number of state intervals')
            np.testing.assert_array_equal(fit['all_bounds'][k],fit['bounds'])
            errors=compare(fit,reference)
            backends[backend]=dict(passed=True,reference_type=r['comparison_reference_type'],max_abs_errors=errors,
                                   boundary_histories_exact=True,selected_K=k)
        pipeline=load(r['historical_pipeline_output'])
        compare(pipeline,reference)
        np.testing.assert_array_equal(times,pipeline['times'])
        np.testing.assert_array_equal(times[pipeline['deltas'].astype(bool)],pipeline['boundary_timestamps'])
        for old in r['historical_validation']:
            require(old['report']['passed'] is True, 'Historical validation receipt')
            require(old['input_sha256']==r['hashes']['fit_array_float64_C_sha256'], 'Historical input identity')
            # The public table is rounded; the stored receipt preserves full precision.
            measured=backends[old['backend']]['max_abs_errors']['tdists']
            require(abs(measured-old['report']['max_t_error'])<=1e-15, 'Historical t-distance error')
        records.append(dict(fixture_id=r['fixture_id'],recording_id=r['recording_id'],shape=r['shape'],
                            selected_K=r['selected_K'],input_and_time_hashes_passed=True,
                            historical_pipeline_passed=True,backends=backends))
    return dict(passed=True,scope='Four frozen processed EEG inputs and historical saved FP64 outputs',
                file_hashes_checked=len(hashes),gsbs_fits_executed=0,atol=1e-8,rtol=1e-8,records=records)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    report=verify(); text=json.dumps(report,indent=2)+'\n'
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(text)
    print(text,end='')

if __name__=='__main__':
    main()
