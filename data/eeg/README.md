# Four frozen BBBD EEG recordings

This directory supplies the four processed inputs used in the paper's EEG comparisons, their exact settings, historical FP64 CPU/PyTorch CUDA/Triton outputs, and an offline verifier. No private repository or GPU is needed to inspect or verify them. All files are part of the public Git checkout; no separate download is required. The existing Figure 3 files are reused for Recording 1.

| Fixture ID (filenames) | Paper recording | Source label | BBBD experiment | Time × features | Kmax | Selected K |
|---|---|---|---|---|---|---|
| 0 | 1 | sub-01_ses-01_stim01 | Not recorded | 1336 × 64 | 131 | 126 |
| 1 | 2 | sub-02_ses-01_stim02 | 3 | 1857 × 32 frontal | 121 | 120 |
| 2 | 3 | sub-03_ses-02_stim03 | 3 | 1754 × 64 | 172 | 173 |
| 3 | 4 | sub-04_ses-02_stim06 | 3 | 1374 × 64 | 135 | 131 |

All inputs are at **5.12 Hz**. Settings are `dmin=5`, `statewise_detection=True`, `finetune=1`, `finetune_order=True`, `blocksize=50`, with recording-specific `kmax`. Double insertion can produce Kmax+1 states; Recording 3 retains that historical output.

## Verify the saved results

From the repository root, with Python 3.10+ and NumPy:

```bash
python scripts/verify_eeg.py
# Equivalent direct entry point; optionally save a new report outside the archive:
python data/eeg/verify_eeg_all.py --report new_eeg_check/report.json
```

The verifier checks file hashes; matrix dimensions, dtype and finite values; strictly increasing sample-center times; reconstruction of original NPY hashes; exact input identity, complete boundary histories, selected K and interval durations; and `tdists`, `state_patterns`, and `strengths` at **atol=rtol=1e-8**. It also checks the historical pipeline output and boundary timestamps. `verification_report.json` is the report from preparing this package. These commands do not run GSBS.

`provenance.json` provides every public path and its immutable source commit, source blob and SHA-256. Paths resolve from the repository root. `recordings.csv` is a compact index; `file_hashes.json` covers the numerical files and source metadata. The repository-wide `SHA256SUMS.txt` additionally covers code and documentation.

## Files and reference levels

- Recording 1 input/time map: `figure_sources/figure3/data/sub-01_ses-01_stim01__all64__5.12hz__d5__k131.npz` (`x`, `times`). Its four output paths also remain in `figure_sources/figure3/data/`.
- Recordings 2–4: `data/eeg/inputs/recording_1.npz` through `recording_3.npz`, containing original float32 `x` and float64 `times`. Cast `x` to float64 for fitting.
- Their `outputs/recording_*_full_cpu.npz`, `*_torch-cuda_float64.npz`, and `*_triton-cuda_float64.npz` are byte-identical historical files. Each includes `x`, `all_bounds`, `nstates`, `tdists`, `bounds`, `deltas`, `states`, `state_patterns`, `strengths`, durations, configuration metadata, and the saved trace.
- `*_historical_pipeline_cpu.npz` additionally preserves the full input, time map and boundary timestamps from the historical analysis pipeline. Its metadata identifies **cpu-fast**, including for files formerly described informally as “official full-fit outputs.”

Recording 1 has a complete unchanged official `statesegmentation==0.0.6` reference output. Recordings 2–4 use their historical CPU outputs previously checked against official results; the GPU comparisons use that CPU reference chain. CPU self-comparisons are identity checks. `validation_history.json` preserves the separate HP-GSBS 0.2.0 validation receipts and compute configurations. The original saved NPZ files do not consistently identify the HP distribution version, so their version is not inferred from the later validation. No new official or HP fits were executed for this data release.

## Optionally compute new outputs

Install `requirements-rerun.txt`, then:

```bash
python scripts/run_eeg_all.py --output new_eeg_all
# Select a zero-based fixture or a GPU backend if available:
python scripts/run_eeg_all.py --recordings 1 2 3 --backend torch-cuda --output new_eeg_cuda
```

The script uses **HP-GSBS 0.2.0**, FP64 Full-Q, streaming candidates and Prefix2D, saves complete outputs and compares all scientific arrays with the archived reference. New results go into a fresh directory and are separate from manuscript measurements. It never calls the official GSBS fitting backend. The legacy `run_eeg_example.py` remains a Recording 1 CPU example.

## Source, processing and credit

Original creators: **Jens Madsen, Nikhil Kuppa and Lucas C. Parra**. Dataset: *The Brain, Body, and Behavior Dataset (BBBD): Multimodal Recordings during Educational Videos*.

- [Official site and raw data access](https://bbbd.pythonanywhere.com/)
- [Dataset paper](https://doi.org/10.1038/s41597-026-07215-1)
- [Experiment 1–3 paper](https://doi.org/10.1073/pnas.2016980118)
- [Official preprocessing code](https://github.com/madjens/bbbd-dataset)
- [Official license statement](https://bbbd.pythonanywhere.com/about-page), checked 2026-10-22
- [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

The historical local pipeline records event cropping, explicit artifact masks, nonoverlapping 25-sample block means from 128 Hz to 5.12 Hz, and within-recording channel z-scoring using the valid-bin sample SD. One fixture selects 32 frontal features; the others retain 64. Values are dimensionless standardized EEG. Times are video-time bin centers, beginning at 0.09765625 s with step 0.1953125 s. This public package introduces no further filtering, artifact treatment or source reconstruction.

For Recordings 2–4 the historical notes identify Experiment 3, the subject, session and stimulus labels above. Session 01 is attentive intentional learning; session 02 is rewatching with silent serial subtraction. Recording 1's experiment is not specified in the preserved metadata. The 32-feature fixture's exact indices into the 64-channel base are not retained in that manifest; its frozen column order is supplied directly. The original artifact masks and full preprocessing project are not included. The supplied inputs allow exact reproduction starting from the processed matrices.

The exact upstream download version has **not been independently established**. The historical dataset DOI `10.5281/zenodo.19241964` and the current [v1.1 access reference](https://zenodo.org/records/22968459) are retained as source/access pointers; the latter is not asserted to have generated these arrays. File hashes, array-value hashes, raw acquisition hashes (unavailable), and historical base-matrix identifiers have separate meanings. In particular, the frontal fixture's base hash describes the 64-channel precursor, not its 32-column view.

These processed inputs and data derivatives retain **CC BY 4.0** attribution. Cite the dataset creators, source and license; describe the processing changes above when redistributing. Repository scripts are MIT licensed. No stimulus videos, demographic tables or questionnaires are included.
