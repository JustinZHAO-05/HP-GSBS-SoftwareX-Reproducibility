# Research-material archive identities

The research package uses its own versions, independently of HP-GSBS 0.2.0.

| Resource | Identifier | Scope |
|---|---|---|
| Current research materials | [GitHub v1.1.0](https://github.com/JustinZHAO-05/HP-GSBS-SoftwareX-Reproducibility/releases/tag/v1.1.0) | Six figures, four EEG recordings, complete Sherlock application, manuscript and Online Resource 1 |
| Research archive series | [10.5281/zenodo.23457341](https://doi.org/10.5281/zenodo.23457341) | All archived research-material versions |
| Earlier research archive | [10.5281/zenodo.23457342](https://doi.org/10.5281/zenodo.23457342), version 1.0.1 | The fixed original five-figure package |
| Algorithm software | [10.5281/zenodo.23422148](https://doi.org/10.5281/zenodo.23422148), version 0.2.0 | Independently versioned algorithm implementation |

The v1.1.0 GitHub release fixes the expanded collection. Its own Zenodo version DOI is recorded here after automatic archival. The earlier v1.0.1 DOI identifies the earlier five-figure archive. Use an exact release/commit for the current collection until its version DOI is listed.

`CITATION.cff` supplies the current research title, authors and version, and identifies the archive series. `.zenodo.json` records the current version, source datasets, relationship to v1.0.1 and the separate software DOI. A journal DOI will be added when available; the current article identifier is [arXiv:2610.25898](https://arxiv.org/abs/2610.25898).

## Retained archive record

The [v1.0.1 archive record](ZENODO_v1.0.1.md) preserves the original archive verification and title. Its tag points to `c5b8713f6c8008ab106c717ee486e3c68211b5b2`; the recorded 94-file verification remains part of that historical record.

## Archival and citation

GitHub–Zenodo integration creates version-specific records from published releases while retaining the archive series. After a new record appears, add its actual DOI to `CITATION.cff` and this page, and update `SHA256SUMS.txt` on main. The release tag and archived source remain fixed. Future `.zenodo.json` versions retain per-material license and source relationships.

Original code is MIT; source datasets and applicable derived inputs, outputs, figures and documentation retain CC BY 4.0 attribution. See `LICENSE`, `LICENSE-DATA`, `DATA_SOURCES.md` and `THIRD_PARTY_NOTICES.md`.
