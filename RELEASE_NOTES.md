# v1.1.0 — Complete EEG/fMRI research materials (2026-10-22)

Archived automatically at [10.5281/zenodo.23573202](https://doi.org/10.5281/zenodo.23573202), GitHub release commit `126043d11050368dbbcffae8f512eda65e6c4648`. The actual DOI was added to main after archival; the release tag remains fixed.

- Adopted the journal-neutral title **HP-GSBS: Reproducibility Materials for Neural-State Segmentation and Performance Evaluation**, with the repository URL retained.
- Consolidated all four frozen BBBD EEG matrices, time maps, saved FP64 outputs and provenance. Recording 1 includes the original complete reference output; Recordings 2–4 retain the historically official-validated CPU reference chain.
- Added the complete Sherlock group/16-participant application: 17 saved segmentations, configuration, fit times, selected boundaries, state-count curves, 120-pair alignment and 1,000 circular-shift scores.
- Added public input acquisition/checking and new-fit scripts for the versioned Figshare source; Figure 6 and its compact cache; the six-figure renderer; fMRI and complete-file manifest checks.
- Included the current author manuscript and Online Resource 1 prepared for Neuroinformatics. Figure 3 retains the high-contrast state boxes; Figures 5 and 6 retain the approved figure/body layout in the manuscript.
- Retained the controlled benchmark observations and historical performance values. fMRI application times have a separate scope from official-comparison speedups. Existing resource measurements retain their original release-development settings.
- Updated citation/archive metadata, dataset access notes, transformations and MIT/CC BY 4.0 attribution. Algorithm software remains **HP-GSBS 0.2.0**, commit `b86b409169aa173d4a361d8cbcc633add1bfacf6`, DOI `10.5281/zenodo.23422148`.
- Previous release tags and the v1.0.1 DOI `10.5281/zenodo.23457342` retain their original files and title. Use the v1.1.0 release or exact commit for this expanded collection; version-specific Zenodo metadata is tracked in `docs/ZENODO.md`.

# Four-record EEG addition — development history (2026-10-22)

- Added the remaining three frozen BBBD Experiment 3 inputs and time maps, complete historical FP64 CPU/PyTorch CUDA/Triton outputs and pipeline outputs. Recording 1 reuses the existing Figure 3 files.
- Added per-record provenance, immutable source identities, distinct file/value/pipeline hashes, parameters, historical validation receipts and offline verification of all four records at atol=rtol=1e-8.
- Added an optional HP-GSBS 0.2.0 rerun script for any or all four inputs, with separate output directories. No official or HP fits were executed to prepare this addition.
- Updated source attribution, processing and public data scope. Complete official reference output remains available for Recording 1; Recordings 2–4 retain the historically validated CPU reference chain.
- Original software release, reproducibility tags and Zenodo v1.0.1 remain unchanged. At this development stage, the addition was identified by its fixed Git commit and was outside the v1.0.1 DOI.

# v1.0.1 — Zenodo integration release

Updates citation and archive metadata to version 1.0.1 and points the archive identity to the v1.0.1 tag. Published after enabling the repository in Zenodo, so its GitHub release can be archived automatically with an independent DOI. Scientific input arrays, recorded observations and reproduction scripts are unchanged from v1.0.0. The existing validation receipt remains applicable.

# v1.0.0 — Paper reproducibility materials

First public snapshot for “HP-GSBS: Accelerating greedy state boundary search with reusable interval statistics.”

- Five figure sources and PDF/PNG previews, benchmark observations and supplementary-table generator.
- Deterministic synthetic input generation with recorded hashes and numerical consistency checks.
- CC BY 4.0 Sherlock-derived and BBBD-derived analysis examples, with explicit original-source credit, license checks, transformations and acquisition instructions.
- Portable CPU/CUDA benchmark scripts fixed to HP-GSBS 0.2.0, plus frozen EEG verification and CPU rerun.
- SHA-256 file manifest, validation receipt, citation metadata and Zenodo archive instructions.

Algorithm software is maintained and versioned separately at https://github.com/JustinZHAO-05/HP-GSBS (software DOI https://doi.org/10.5281/zenodo.23422148).

Original code is MIT licensed; data, derived examples, figures and documentation are CC BY 4.0, with third-party attribution retained. This archive does not include full upstream datasets or stimulus videos.
