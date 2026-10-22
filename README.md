# HP-GSBS: Reproducibility Materials for Neural-State Segmentation and Performance Evaluation

Data and scripts for **HP-GSBS: Accelerating greedy state boundary search with reusable interval statistics**, by Yanzhe Zhao and Yongzhang Ji. This independent research package reconstructs six main figures and the accompanying numerical tables, supplies four frozen BBBD EEG analysis inputs and saved outputs, and provides the complete Sherlock angular-gyrus application for a group response and 16 participants.

**Research-material version: 1.1.0 · [DOI 10.5281/zenodo.23573202](https://doi.org/10.5281/zenodo.23573202).** The [algorithm software](https://github.com/JustinZHAO-05/HP-GSBS) remains fixed to **0.2.0**, release commit `b86b409169aa173d4a361d8cbcc633add1bfacf6`, [software DOI 10.5281/zenodo.23422148](https://doi.org/10.5281/zenodo.23422148).

The [current author manuscript and Online Resource 1](manuscript/README.md) are prepared for *Neuroinformatics*. The [arXiv preprint](https://arxiv.org/abs/2610.25898) supplies the current persistent article identifier. See [release notes](RELEASE_NOTES.md) and [archive identities](docs/ZENODO.md) for the research-material version history.

## Resources

| Resource | Contents |
|---|---|
| [Current manuscript](manuscript/HP_GSBS_Neuroinformatics_Main.pdf) · [Online Resource 1](manuscript/ESM_1.pdf) | Computational formulation, numerical and neuroscience applications; Sections S1–S8 with full protocols and tables |
| [BBBD EEG](data/eeg/README.md) | Four frozen time × channel matrices, 5.12-Hz time maps, configurations, FP64 results and reference-chain history |
| [Sherlock fMRI](data/fmri/README.md) | Seventeen saved segmentations, fit times, 120-pair alignment analysis, 1,000 null scores and public-input acquisition/rerun commands |
| [Figure sources](figure_sources/) · [Rendered figures](figures/) | Six figures, including the full-length Sherlock application; shared captions in `figure_sources/captions.tex` |
| [Controlled observations](data/) · [Tables](tables/) | All 140 timed observations and the recorded ablation, memory, throughput and recovery results |
| [Data sources](DATA_SOURCES.md) · [Attribution](THIRD_PARTY_NOTICES.md) | Dataset identities, processing, acquisition and per-material licensing |

## Rebuild figures and tables

Python 3.10+; these commands read supplied arrays and run on CPU with the plotting dependencies:

```bash
python -m pip install -r requirements-figures.txt
python scripts/verify_manifest.py
python scripts/verify_data.py
python scripts/make_figures.py
python scripts/make_supplement_tables.py
```

Run the manifest check before regeneration, since PDF metadata and rendering-library versions can change output file bytes. Figures are written to `figures/`, and LaTeX table rows to `tables/`. All six figures can be rebuilt without fitting GSBS, downloading the full Sherlock input or accessing private repositories. The recorded plotting environment is in `requirements-figures-frozen.txt`.

For targeted checks, use `python scripts/verify_eeg.py` for all four EEG records and `python scripts/verify_fmri.py` for the 17 fMRI outputs and saved alignment statistics. The optional `--recompute-null` flag reconstructs the seeded circular-shift scores from saved boundaries. `scripts/generate_inputs.py` independently reproduces the controlled synthetic input identities.

| Figure | Content | Numerical input |
|---|---|---|
| 1 | Interval reuse, candidate search and t-distance | Sherlock 120-TR group-response excerpt and saved search trace |
| 2 | Synthetic numerical agreement | Recorded illustrative signal and backend outputs |
| 3 | BBBD EEG segmentation | Recording 1, time map and complete saved outputs |
| 4 | Controlled runtime and paired speedup | Timed observations and per-input/aggregate CSVs |
| 5 | Ablation, memory and throughput | Archived component and resource measurements |
| 6 | Naturalistic fMRI and intersubject analysis | Seventeen segmentations, display cache and circular-shift statistics |

The controlled benchmark contains seven configurations with two seeds: **14 configuration/seed cases, 10 distinct input matrices and 140 timed observations**. The 42 optimized warm-ups are recorded in the protocol, separately from the timing CSV. Observed ranges summarize the recorded inputs or repetitions. Historical cross-session comparisons and release-development resource measurements retain their original measurement scopes. The fMRI fit times describe the separate application and use their own table.

## Run new analyses

Install the fixed release and reference dependencies in a separate environment:

```bash
python -m pip install -r requirements-rerun.txt
python scripts/research_workflow.py
python scripts/run_eeg_all.py --backend cpu-fast --output new_eeg_cpu
python scripts/download_sherlock.py --output external/Sherlock_AG_movie.npy
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 \
python scripts/run_sherlock.py \
    --input external/Sherlock_AG_movie.npy \
    --output new_sherlock_results --kmax 60 \
    --subjects all --perm 1000 --tolerance 3 --null-seed 20261020
```

The Sherlock download helper checks byte count, MD5, array shape and dtype. The analysis retains all 946 TRs and 4,230 voxels. [The fMRI README](data/fmri/README.md) and Online Resource 1, Section S8 specify the processing, parameters, output schema and statistics. New runs use a new output directory and retain their own machine-specific times.

The original synthetic and paired-benchmark commands remain available:

```bash
python scripts/run_consistency_example.py --output new_consistency
python scripts/run_paired_benchmark.py --output new_cpu_benchmark --backends official cpu-fast --only T1 T2
```

CUDA reruns additionally require compatible PyTorch/Triton installations following the [software documentation](https://github.com/JustinZHAO-05/HP-GSBS/tree/v0.2.0). EEG and synthetic rerun scripts accept `torch-cuda` and `triton-cuda` as appropriate. The historical measurement environment is recorded in `data/environment.json`.

## Licenses and citation

Original repository code is **MIT** ([LICENSE](LICENSE)). Source datasets and applicable derived inputs, numerical materials, figures and documentation retain **CC BY 4.0** attribution ([LICENSE-DATA](LICENSE-DATA), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)). The source collection and dataset credit remain with the BBBD and Sherlock creators.

Cite this package using [DOI 10.5281/zenodo.23573202](https://doi.org/10.5281/zenodo.23573202), the exact [release](https://github.com/JustinZHAO-05/HP-GSBS-SoftwareX-Reproducibility/releases/tag/v1.1.0) or Git commit and `CITATION.cff`. The research archive series is [10.5281/zenodo.23457341](https://doi.org/10.5281/zenodo.23457341); the earlier **v1.0.1** archive remains [10.5281/zenodo.23457342](https://doi.org/10.5281/zenodo.23457342). Version-specific archive identities are maintained in [docs/ZENODO.md](docs/ZENODO.md). Cite HP-GSBS 0.2.0, the original GSBS papers and the datasets when using them; BibTeX source entries are in `references.bib`.

**Yanzhe Zhao** — main contributor and maintainer; algorithm implementation, experiments, data preparation, figures and manuscript. **Yongzhang Ji** — theoretical/methodological analysis and manuscript review. Contact: justinzhaoyz@outlook.com.
