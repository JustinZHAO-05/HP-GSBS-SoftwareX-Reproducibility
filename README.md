# HP-GSBS: Reproducibility materials

Data and scripts accompanying **“HP-GSBS: Accelerating greedy state boundary search with reusable interval statistics”**, by Yanzhe Zhao and Yongzhang Ji.

This repository reconstructs the five paper figures and supplementary tables from archived observations, and supplies portable scripts for new experiments. The algorithm itself is maintained in [HP-GSBS](https://github.com/JustinZHAO-05/HP-GSBS), fixed here to **0.2.0**, [software DOI: 10.5281/zenodo.23422148](https://doi.org/10.5281/zenodo.23422148). This reproducibility repository has its own version series; the last Zenodo integration release is **v1.0.1**. The current Git branch additionally includes all four frozen EEG inputs and saved FP64 results in [data/eeg](data/eeg/README.md). Those additions are not part of the older v1.0.1 DOI; use the exact Git commit until a new version is archived.

**Reproducibility archive, version 1.0.1:** [10.5281/zenodo.23457342](https://doi.org/10.5281/zenodo.23457342).

**All versions:** [10.5281/zenodo.23457341](https://doi.org/10.5281/zenodo.23457341). Use the version DOI to cite the exact paper materials.

## Reproduce the paper figures and tables

Python 3.10+; no GPU, HP-GSBS installation or private repository access is needed for these commands:

```bash
python -m pip install -r requirements-figures.txt
python scripts/verify_manifest.py
python scripts/verify_data.py
python scripts/generate_inputs.py
python scripts/verify_eeg.py
python scripts/make_figures.py
python scripts/make_supplement_tables.py
```

Rendered figures are written to `figures/`, and LaTeX table rows to `tables/`. Figure-specific scripts also write intermediate renderings beside their source. PDF/SVG/PNG formats can be rebuilt; the initial repository includes PDF/PNG previews. Re-rendering can change file bytes across plotting-library versions without changing the data. `requirements-figures-frozen.txt` records the environment used to validate this public package.

| Figure | Content | Supplied source |
|---|---|---|
| 1 | Interval reuse, candidate search and t-distance mechanism | Sherlock-derived 120-TR angular-gyrus mean, saved trace and plotting scripts |
| 2 | Synthetic signal and numerical agreement | Recorded synthetic input and backend outputs |
| 3 | Full-record EEG segmentation and state-count selection | Frozen BBBD-derived matrix, time map and four saved outputs |
| 4 | Controlled paired runtime and speedup | Per-input, timed-run and aggregate CSVs |
| 5 | Ablation, memory and throughput | Recorded component, memory and throughput CSVs |

The primary paired benchmark has **14 configuration/seed cases, 10 distinct matrices and 140 timed observations**. The seven configurations each use two seeds; Kmax scaling reuses the same inputs. The original 42 optimized warm-ups are excluded from the timing CSV. Observed min–max ranges summarize the recorded inputs. Historical extended-workload comparisons are kept in their own table.

## Run new fits

Install the fixed software and reference dependencies:

```bash
python -m pip install -r requirements-rerun.txt
python scripts/run_consistency_example.py --output new_consistency
python scripts/run_eeg_example.py --output new_eeg
python figure_sources/figure1/reproduce_analysis.py
python scripts/run_paired_benchmark.py --output new_cpu_benchmark --backends official cpu-fast --only T1 T2
```

Omit `--only T1 T2` to run all seven CPU benchmark configurations. Results from new runs are separate from archived manuscript measurements; timings depend on the machine. The recorded experiment environment is in `data/environment.json`.

For all four routes, install compatible CUDA PyTorch and Triton following the [software installation instructions](https://github.com/JustinZHAO-05/HP-GSBS/tree/v0.2.0), then run:

```bash
python scripts/run_paired_benchmark.py --output new_four_route_benchmark
python scripts/run_consistency_example.py --output new_all_route_consistency --backends cpu-fast torch-cuda triton-cuda
```

## Data access and licensing

**Both source datasets explicitly permit reuse under CC BY 4.0.** The derived inputs needed for Figures 1 and 3 and **all four EEG comparison recordings** are included with attribution, transformations and source links. The package does not contain stimulus videos, the complete original datasets, questionnaires or participant demographic tables. See [DATA_SOURCES.md](DATA_SOURCES.md) for upstream acquisition instructions and [data/eeg/README.md](data/eeg/README.md) for all EEG inputs, settings, reference levels and verification commands. `python scripts/verify_eeg.py` verifies all four recordings without fitting; `python scripts/run_eeg_all.py --output new_eeg_all` optionally computes new HP-only fits.

- Original repository code: **MIT**; see [LICENSE](LICENSE).
- Data, derived examples, figures and documentation: **CC BY 4.0**; see [LICENSE-DATA](LICENSE-DATA) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Third-party dataset authors retain their attribution; this repository does not relicense their work as MIT.

## Citation and credits

Use `CITATION.cff` for this reproducibility package. The reproducibility archive DOI is **10.5281/zenodo.23457342** (version 1.0.1); the software DOI above identifies the algorithm software. See [docs/ZENODO.md](docs/ZENODO.md) for archive setup and metadata. Cite the original GSBS papers and the datasets when using them; BibTeX entries are provided in `references.bib`.

**Yanzhe Zhao** — main contributor and maintainer; algorithm implementation, experiments, data preparation, figures and manuscript. **Yongzhang Ji** — contributed theoretical/methodological analysis and manuscript review. Paper contribution statements remain in the manuscript.

Contact: justinzhaoyz@outlook.com
