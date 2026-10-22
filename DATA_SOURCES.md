# Data sources, public access and reuse

License pages checked on **2026-10-19 (Asia/Shanghai)**; BBBD's [explicit license statement](https://bbbd.pythonanywhere.com/about-page) rechecked **2026-10-22** for the four-record EEG addition. Decisions below use the official dataset pages, rather than inferring redistribution rights from public download access.

| Material | Official source and permission | Public-package decision |
|---|---|---|
| Sherlock angular-gyrus fMRI | [Figshare dataset](https://figshare.com/articles/dataset/Sherlock_data_for_OHBM/12436955), explicitly CC BY 4.0 | Include the small averaged 120-TR derivative and its analysis trace, with attribution and transformations |
| BBBD EEG | [Official BBBD site, Usage Notes](https://bbbd.pythonanywhere.com/), explicitly CC BY 4.0 for downloadable files | Include the frozen analysis matrix, time map and four saved outputs required for Figure 3, with attribution and transformations |
| Other three frozen EEG examples | BBBD Experiment 3; same CC BY 4.0 source | Include all three frozen matrices, time maps, historical CPU/GPU FP64 outputs and pipeline outputs in `data/eeg/`; retain aggregate comparisons in `data/eeg_consistency.csv` |
| Synthetic signals and benchmark observations | Author-generated experiments | Include exact saved synthetic example, all supplied CSV summaries and paired timed observations, and deterministic input generator |
| Stimulus video, full physiological collections, questionnaires and demographic data | Separate source materials, not needed for these figures | Not redistributed; use the upstream dataset site to obtain needed material under its applicable terms |

## Sherlock: obtain the upstream data

1. Open [Figshare version 1](https://doi.org/10.6084/m9.figshare.12436955.v1) and download `Sherlock_AG_movie.npy` (file ID 22927253).
2. The supplied original-file MD5 is `f80dde9a451e140c39b98c2e5214d93c` and original shape is `(16, 946, 4230)`.
3. Average across the subject axis, then retain the first 120 consecutive TRs and all voxels. No additional filtering was applied for Figure 1. The packaged analysis matrix is `figure_sources/figure1/data/Sherlock_AG_120TR.npz`, key `x`, shape `(120, 4230)`.
4. The original input SHA-256 is recorded in `figure_sources/figure1/data/provenance.json`. `reproduce_analysis.py` reruns HP-GSBS and the installed reference against the supplied matrix. The figure renderer recomputes interval/correlation matrices directly from this input.

## BBBD: obtain the upstream data

Use the [official site and its Download menu](https://bbbd.pythonanywhere.com/), [dataset DOI](https://doi.org/10.15387/fcp_indi.retro.bbbd), and [official preprocessing code](https://github.com/madjens/bbbd-dataset). The source site separates experiments and supplies BIDS recordings and documentation. Consult the source site's recording index when locating a subject/session/stimulus; those labels are not globally unique across experiments.

The supplied study label is `sub-01_ses-01_stim01`, representation `broadband_all64_5p12_blockmean_zscore_v1`. The saved metadata does not name the source experiment, so this package does not invent an experiment mapping. **Exact input-to-figure reproduction uses the included frozen matrix**, rather than claiming that an unspecified raw EEG file will recreate it.

The shared `figure_sources/figure3/data/` contains:

- `sub-01_ses-01_stim01__all64__5.12hz__d5__k131.npz`: frozen study input, time map and saved output;
- `0_full_reference.npz`: historical official full-record output;
- `0_full_cpu.npz`, `0_torch-cuda_float64.npz`, `0_triton-cuda_float64.npz`: saved optimized outputs on the same input.

Each matrix has 1,336 samples and 64 channels; sampling rate is 5.12 Hz and the full record is approximately 260.94 s. The stored inputs use block-mean reduction and z-scoring and were converted to FP64 for fits. The reproduction package applies no additional filtering, artifact processing or source reconstruction. Original channel names, algorithm settings and source identifiers remain in the NPZ metadata. `scripts/verify_eeg.py` checks the saved agreement; `scripts/run_eeg_example.py` makes a new CPU fit.

### All four EEG recordings

[data/eeg/README.md](data/eeg/README.md) and [provenance.json](data/eeg/provenance.json) identify all four public inputs and every saved output. Recording 1 reuses the files listed above. Recordings 2–4 add the Experiment 3 inputs `sub-02_ses-01_stim02` (1857 × 32 frontal), `sub-03_ses-02_stim03` (1754 × 64), and `sub-04_ses-02_stim06` (1374 × 64), their 5.12-Hz time maps and full FP64 outputs. Their historical metadata identifies the additional pipeline outputs as CPU outputs, rather than complete official reference fits.

The recorded preprocessing includes event cropping, explicit artifact masks, 25-sample block means from 128 Hz to 5.12 Hz, and channel z-scoring with valid-bin sample SD. The exact upstream download version is not independently established; [the current v1.1 access page](https://zenodo.org/records/22968459) does not establish how the frozen local arrays were created. Exact reproduction begins with the included processed matrices. The original raw files, artifact masks and full preprocessing project are separate upstream/local materials.

`data/eeg/provenance.json` retains immutable source commit/blob identifiers, file hashes and value hashes, together with original pipeline identifiers. These identify different byte domains and are not treated as interchangeable. No private repository is needed to use the packaged data. The filenames retain anonymized study-style IDs, without demographic or clinical tables. Run `python scripts/verify_eeg.py` for independent offline checks and consult `data/eeg/README.md` for optional HP-GSBS 0.2.0 reruns.

## Reuse conditions

Include source credit, the dataset URL/DOI and the [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/), and indicate changes when redistributing adaptations. Both reviewed source licenses allow the derivatives supplied here. For future additions with unclear or restrictive terms, add only reusable aggregate statistics or synthetic examples and upstream acquisition instructions until permission is established.
