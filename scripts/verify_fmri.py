"""Check archived Sherlock segmentations and boundary statistics without fitting."""
from pathlib import Path
import argparse
import importlib.util
import json
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

ROOT=Path(__file__).resolve().parents[1]

def verify(recompute_null=False):
    folder=ROOT/'data/fmri'
    results=json.loads((folder/'results.json').read_text())
    summary=json.loads((folder/'summary.json').read_text())
    cache=np.load(folder/'figure6_data.npz',allow_pickle=False)
    records=[results['group_mean']]+results['subject_results']
    assert len(records)==17 and len(results['subject_results'])==16
    for row in records:
        with np.load(folder/f"{row['label']}_segmentation.npz",allow_pickle=False) as saved:
            assert set(saved.files)=={'selected_K','boundary_indices','evaluated_K_indices','all_bounds','tdists'}
            prefix='group__' if row['label']=='group_mean' else row['label']+'__'
            for key in ['boundary_indices','evaluated_K_indices','tdists','selected_K']:
                np.testing.assert_array_equal(saved[key],row[key])
                np.testing.assert_array_equal(saved[key],cache[prefix+key])
            k=int(saved['selected_K'])
            assert k==len(saved['boundary_indices'])+1==int(np.nanargmax(saved['tdists']))
            np.testing.assert_array_equal(np.flatnonzero(saved['all_bounds'][k]),saved['boundary_indices'])
            assert saved['all_bounds'].shape==(62,946)
    null=np.asarray(results['null_test']['null_scores'])
    assert null.shape==(1000,) and np.isfinite(null).all()
    np.testing.assert_array_equal(null,cache['null_scores'])
    boundaries=[np.asarray(r['boundary_indices']) for r in results['subject_results']]
    pairs=[]
    for i in range(16):
        for j in range(i+1,16):
            matches=maximum_bipartite_matching(csr_matrix(np.abs(boundaries[i][:,None]-boundaries[j][None,:])<=3),perm_type='column')
            pairs.append(2*np.count_nonzero(matches>=0)/(len(boundaries[i])+len(boundaries[j])))
    observed=float(np.mean(pairs));probability=float((1+np.count_nonzero(null>=observed))/1001)
    np.testing.assert_allclose(observed,cache['observed_f1'],rtol=0,atol=1e-15)
    np.testing.assert_allclose([observed,float(np.mean(null)),probability],
        [summary['observed_F1'],summary['null_mean'],summary['monte_carlo_p']],rtol=0,atol=1e-15)
    np.testing.assert_allclose(np.quantile(null,[.025,.975]),summary['null_empirical_95_interval'],rtol=0,atol=1e-15)
    total=sum(r['elapsed_s'] for r in records)
    np.testing.assert_allclose(total,summary['full_cohort_total_fit_s'],rtol=0,atol=1e-10)
    if recompute_null:
        spec=importlib.util.spec_from_file_location('sherlock_protocol',ROOT/'scripts/run_sherlock.py')
        protocol=importlib.util.module_from_spec(spec);spec.loader.exec_module(protocol)
        rebuilt=protocol.circular_shift_null(boundaries,T=946,tolerance=3,n_perm=1000,seed=20261020)
        np.testing.assert_array_equal(rebuilt['null_scores'],null)
    return dict(passed=True,segmentations=17,participant_pairs=120,null_scores=1000,
                observed_F1=observed,null_mean=float(np.mean(null)),monte_carlo_p=probability,
                total_fit_s=total,seeded_null_recomputed=recompute_null,GSBS_fits_executed=0)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recompute-null',action='store_true')
    args=parser.parse_args()
    print(json.dumps(verify(args.recompute_null),indent=2))
