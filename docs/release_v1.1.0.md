HP-GSBS: Reproducibility Materials for Neural-State Segmentation and Performance Evaluation — version 1.1.0.

This release supplies the complete six-figure research collection for **HP-GSBS: Accelerating greedy state boundary search with reusable interval statistics**, by Yanzhe Zhao and Yongzhang Ji.

- Four frozen BBBD EEG analysis inputs, time maps, saved FP64 outputs, configurations and provenance.
- Complete Sherlock angular-gyrus application for a group response and 16 participants: 17 segmentations, fit times, curves, selected boundaries, observed alignment and 1,000 circular-shift scores.
- Six figure sources and previews, complete controlled benchmark tables, public-input acquisition/rerun scripts and saved-data/hash verifiers.
- Current author manuscript and Online Resource 1 prepared for Neuroinformatics.

The original controlled benchmark observations and historical performance values retain their measurement scopes. Recording 1 includes a complete original EEG reference output; Recordings 2–4 retain the historically official-validated CPU reference chain. fMRI fit times describe the separate HP-GSBS application.

Algorithm software remains HP-GSBS **0.2.0**, commit `b86b409169aa173d4a361d8cbcc633add1bfacf6`, DOI https://doi.org/10.5281/zenodo.23422148.

Research archive series: https://doi.org/10.5281/zenodo.23457341. Previous v1.0.1 archive: https://doi.org/10.5281/zenodo.23457342. The current version DOI is maintained in `docs/ZENODO.md` after automatic archival.

Original code: MIT. Source data and applicable derived materials: CC BY 4.0 with BBBD/Sherlock creator credit, source links and processing changes in `DATA_SOURCES.md` and `THIRD_PARTY_NOTICES.md`.

Download Source code (zip) for the complete release. From a clean checkout, install `requirements-figures.txt`, then run `scripts/verify_manifest.py`, `scripts/verify_data.py`, `scripts/make_figures.py` and `scripts/make_supplement_tables.py`.
