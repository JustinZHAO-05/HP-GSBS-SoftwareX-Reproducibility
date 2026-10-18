# Archive this package with an independent DOI

This is a separate research output from the algorithm software DOI
`10.5281/zenodo.23422148`. Do not upload it as a new version of the algorithm record.

## GitHub integration

1. Sign in to [Zenodo](https://zenodo.org/) using the account connected to your GitHub profile.
2. Open the profile menu → **GitHub**, click **Sync now**, find `JustinZHAO-05/HP-GSBS-SoftwareX-Reproducibility` and enable its toggle. Enabling only this public repository is sufficient.
3. New GitHub releases published after enabling the integration are automatically archived. Metadata is prepared in `.zenodo.json` and `CITATION.cff`.
4. If `v1.0.0` was already published before the repository was enabled, the simplest route is to publish the next real release after enabling it. For the exact existing `v1.0.0` snapshot, use the manual route below rather than moving its tag or assuming Zenodo will import it retroactively.
5. Open the resulting record and copy its **version DOI**. Add it to the README, `CITATION.cff` and the paper's code/data availability statement. The all-versions DOI can also be used as a stable project-level reference.

Official guides: [Enable a repository](https://help.zenodo.org/docs/github/enable-repository/) · [Archive a GitHub release](https://help.zenodo.org/docs/github/archive-software/github-upload/).

## Archive the existing v1.0.0 manually

1. Download **Source code (zip)** from this repository's `v1.0.0` GitHub Release.
2. In Zenodo choose **New upload** to create a separate record, and upload that ZIP.
3. Use the title **HP-GSBS: SoftwareX reproducibility materials**, resource type **Software**, version **1.0.0**, creators **Yanzhe Zhao (Tianjin University)** and **Yongzhang Ji (Southwest University)**. Preserve that order.
4. Description: use the description in `.zenodo.json`. State that code is MIT and data/figures/documentation are CC BY 4.0. List **MIT** and **CC BY 4.0** as licenses where supported; the per-file scope remains specified in the archive.
5. Add the GitHub tag URL as an identical-version reference; relate the algorithm DOI as software used by this package. Include the upstream dataset references from `.zenodo.json`. Let Zenodo assign a **new DOI**; do not reuse the algorithm DOI.
6. Check the uploaded file and creators, then publish. Update the paper and repository with the actual new DOI. Keep the version tag fixed; a README-only metadata update on `main` can record the newly assigned DOI.

Do not fill in a journal DOI or arXiv identifier before one has actually been assigned.
