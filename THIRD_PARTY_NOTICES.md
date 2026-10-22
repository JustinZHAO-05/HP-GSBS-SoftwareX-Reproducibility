# Third-party attribution

## Sherlock-derived fMRI example

Christopher Baldassano (2020), *Sherlock data for OHBM*, Figshare, version 1.
https://doi.org/10.6084/m9.figshare.12436955.v1

License: **Creative Commons Attribution 4.0 International**.
https://creativecommons.org/licenses/by/4.0/

The original `Sherlock_AG_movie.npy` contains angular-gyrus data derived from the Sherlock study. This package averages the 16 subjects and selects the first 120 TRs (TR = 1.5 s), retaining all 4,230 voxels for fitting. Plots display selected voxels and computed statistics. The NPZ, search trace, derived statistics and rendered Figure 1 are adaptations; no movie footage is included. See `figure_sources/figure1/data/provenance.json` and `data_references.bib`.

Original study: Chen et al. (2017), *Shared memories reveal shared structure in neural activity across individuals*, Nature Neuroscience. https://doi.org/10.1038/nn.4450

## Four BBBD-derived EEG examples

Jens Madsen, Nikhil Kuppa and Lucas C. Parra, *The Brain, Body, and Behavior Dataset (BBBD): Multimodal Recordings during Educational Videos*.
Data: https://doi.org/10.15387/fcp_indi.retro.bbbd
Data paper: https://doi.org/10.1038/s41597-026-07215-1
Official site: https://bbbd.pythonanywhere.com/

The official site states that its downloadable files are **CC BY 4.0**.
https://creativecommons.org/licenses/by/4.0/

The four study-derived EEG inputs are frozen 32- or 64-channel matrices at 5.12 Hz. The recorded local processing includes event cropping, explicit artifact masks, 25-sample block means from 128 Hz, channel z-scoring using valid-bin sample SD, and one frontal-channel view; values are converted to FP64 for fits. Figure 3 uses the first recording. All four inputs, time maps and corresponding saved FP64 outputs are publicly supplied; their segmentation, t-distance curves and rendered figures are derived materials. The original data acquisition, collection and source-dataset credit remain with the dataset authors. No participant questionnaires, demographics or stimulus videos are included. See `data/eeg/provenance.json` for each source and modification, and `data/eeg/README.md` for download-version and reference-chain information. The [official CC BY 4.0 statement](https://bbbd.pythonanywhere.com/about-page) was rechecked on 2026-10-22.

## Reference software and method

HP-GSBS: Yanzhe Zhao (2026), version 0.2.0. https://doi.org/10.5281/zenodo.23422148 — MIT.

Original GSBS method: Geerligs et al. (2021), https://doi.org/10.1016/j.neuroimage.2021.118085; Geerligs et al. (2022), https://doi.org/10.7554/eLife.77430.

Reference implementation: https://github.com/lgeerligs/statesegmentation (`statesegmentation==0.0.6`). Install it as a dependency; no copy of its source is vendored in this repository.
