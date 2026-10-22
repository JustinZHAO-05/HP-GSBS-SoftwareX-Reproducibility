# Figure 6: Sherlock fMRI application

From the repository root, run `python figure_sources/figure6/draw_figure6.py`. The script reads `data/fmri/figure6_data.npz` and writes PDF/SVG/PNG to `figures/figure6_fmri.*`. It uses the supplied saved outputs and display cache.

Panels show the group response (72 displayed voxels; 4,230 fitted), group and participant boundaries, all evaluated state-count curves, and 1,000 circular-shift cohort statistics. Source attribution and display transformations are in `data/fmri/README.md`, `data/fmri/provenance.json` and `THIRD_PARTY_NOTICES.md`. The article caption is retained in `caption.tex` and the shared `figure_sources/captions.tex`.
