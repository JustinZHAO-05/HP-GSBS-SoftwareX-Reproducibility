# Sherlock angular-gyrus fMRI application

This collection supplies the group response and 16 participant segmentations from the first movie half in the version-1 Sherlock angular-gyrus derivative. All 946 TRs and 4,230 voxels are retained for fitting. TR = 1.5 s; the segment spans 1,419 s (23.65 min). Participant filenames use zero-based indices 00–15, corresponding to Participants 1–16 in the article.

Source: Christopher Baldassano (2020), *Sherlock data for OHBM*, Figshare version 1, https://doi.org/10.6084/m9.figshare.12436955.v1, **CC BY 4.0**, from Chen et al. (2017), https://doi.org/10.1038/nn.4450. Changes: FP64 conversion; group mean; neural-state segmentation; boundary statistics; display-only voxel selection and spatial standardization. [provenance.json](provenance.json) records source identity, processing, configuration and paths.

## Saved materials

- `*_segmentation.npz`: 17 compact results, each containing exactly `selected_K`, `boundary_indices`, `evaluated_K_indices`, `all_bounds`, `tdists`.
- `manifest.json`, `results.json`: source identity, scientific configuration, per-fit times, curves, selected boundaries and 1,000 circular-shift cohort scores.
- `fit_summary.csv`, `boundary_times.csv`: complete cohort fit and boundary-time tables.
- `summary.json`: article summary statistics, with the separate pilot explicitly identified.
- `figure6_data.npz`: 72-voxel display matrix, all state-count curves and selected boundaries, observed F1 and null scores.

Analysis uses HP-GSBS 0.2.0 CPU, FP64 Full-Q/Prefix2D, streaming candidates, latency mode, one BLAS/Numba thread, Kmax=60, dmin=1, statewise detection, finetune=1, ordered refinement and blocksize=50. Each participant matrix is converted to FP64. The group matrix accumulates each FP64 participant array divided by 16. Saved evaluated indices retain accepted Kmax+1 slots from double insertion.

Boundary alignment uses maximum one-to-one matching within ±3 TR (±4.5 s), averaged over 120 participant pairs. The null independently shifts each boundary train by an offset from 1–945 modulo 946, then matches on the linear time axis. The 1,000 draws use seed 20261020. Mean observed F1 is 0.4140970; the null mean is 0.3248678; the Monte Carlo probability is 1/1001. The 17 recorded fit times total 213.1028 s. These application timings are separate from the controlled implementation speedups.

## Check and reproduce

Run from the repository root:

```bash
python scripts/verify_fmri.py
python figure_sources/figure6/draw_figure6.py
```

An optional `python scripts/verify_fmri.py --recompute-null` reconstructs all seeded null scores from saved boundaries. These checks and plotting use the supplied compact arrays.

For a new fit, install `requirements-rerun.txt` in a separate environment and retrieve the versioned source:

```bash
python scripts/download_sherlock.py --output external/Sherlock_AG_movie.npy
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 \
python scripts/run_sherlock.py \
    --input external/Sherlock_AG_movie.npy \
    --output new_sherlock_results --kmax 60 \
    --subjects all --perm 1000 --tolerance 3 --null-seed 20261020
```

The source has 256,101,248 bytes, float32 shape `(16, 946, 4230)`, MD5 `f80dde9a451e140c39b98c2e5214d93c`; its full SHA-256 is in the provenance. The helper verifies existing files and supports `--check-only`. The source is downloaded from https://ndownloader.figshare.com/files/22927253. Group mean, individual fits and null statistics can be recomputed using public inputs and software. See Online Resource 1, Section S8, for the complete protocol.
