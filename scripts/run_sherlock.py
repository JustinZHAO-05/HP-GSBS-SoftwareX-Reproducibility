#!/usr/bin/env python3
"""Prospective full-length Sherlock fMRI application for pinned HP-GSBS v0.2.0.

No official GSBS fits or official GSBS timings are performed.  The original
Figshare angular-gyrus array is required; nothing is fabricated or imputed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from time import perf_counter

import numpy as np

EXPECTED_SHAPE = (16, 946, 4230)
EXPECTED_MD5 = "f80dde9a451e140c39b98c2e5214d93c"
TR_SECONDS = 1.5
FIGSHARE = "https://doi.org/10.6084/m9.figshare.12436955.v1"


def checksum(path: Path, algo: str = "md5") -> str:
    h = hashlib.new(algo)
    with path.open("rb") as f:
        while True:
            b = f.read(8 * 1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def group_mean(data: np.ndarray) -> np.ndarray:
    """Incremental FP64 across subjects; avoid an extra 256-MB temporary."""
    result = np.zeros(data.shape[1:], dtype=np.float64)
    for idx in range(data.shape[0]):
        result += np.asarray(data[idx], dtype=np.float64) / data.shape[0]
    return result


def matching_f1(a: np.ndarray, b: np.ndarray, tolerance: int = 3) -> float:
    """One-to-one tolerant boundary matching; symmetric event-count F1."""
    a, b = np.sort(np.asarray(a, int)), np.sort(np.asarray(b, int))
    i = j = matches = 0
    while i < len(a) and j < len(b):
        if abs(int(a[i]) - int(b[j])) <= tolerance:
            matches += 1
            i += 1
            j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    denom = len(a) + len(b)
    return (2.0 * matches / denom) if denom else np.nan


def pairwise_mean_f1(boundaries: list[np.ndarray], tolerance: int) -> float:
    scores = [matching_f1(boundaries[i], boundaries[j], tolerance)
              for i in range(len(boundaries)) for j in range(i + 1, len(boundaries))]
    return float(np.nanmean(scores)) if scores else np.nan


def circular_shift_null(boundaries: list[np.ndarray], T: int, tolerance: int,
                        n_perm: int, seed: int) -> dict:
    """Shift each entire boundary sequence once per permutation.

    The global pairwise score is the unit of inference: we do NOT treat
    all subject-pairs as independent biological replicates.
    """
    if len(boundaries) < 2:
        return {"status": "not_run", "reason": "at least two subjects required"}
    rng = np.random.default_rng(seed)
    observed = pairwise_mean_f1(boundaries, tolerance)
    surrogate = np.empty(n_perm, dtype=float)
    for k in range(n_perm):
        offsets = rng.integers(1, T, size=len(boundaries))
        shifted = [np.sort((np.asarray(b, dtype=int) + int(off)) % T)
                   for b, off in zip(boundaries, offsets)]
        surrogate[k] = pairwise_mean_f1(shifted, tolerance)
    p = (1 + np.count_nonzero(surrogate >= observed)) / (1 + n_perm)
    return {"status": "complete", "observed_pairwise_mean_f1": observed,
            "null_mean": float(np.mean(surrogate)),
            "null_min": float(np.min(surrogate)),
            "null_max": float(np.max(surrogate)),
            "monte_carlo_p": float(p),
            "n_permutations": n_perm,
            "n_subjects": len(boundaries),
            "n_subject_pairs": len(boundaries) * (len(boundaries) - 1) // 2,
            "tolerance_TR": tolerance,
            "seed": seed,
            "null_scores": surrogate.tolist()}


def plot_figure(out: Path, group_x: np.ndarray, group: dict,
                subject_rows: list[dict], null_result: dict, selected_voxels: int = 72):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    T, P = group_x.shape
    idx = np.linspace(0, P - 1, min(selected_voxels, P), dtype=int)
    # For display only: spatially standardize, without modifying analysis input.
    X = group_x[:, idx]
    row_sd = X.std(axis=1, ddof=1, keepdims=True)
    z = np.divide(X - X.mean(axis=1, keepdims=True), row_sd,
                  out=np.zeros_like(X), where=row_sd > 0)
    z = np.clip(z, -3, 3)
    time = np.arange(T) * TR_SECONDS / 60
    fig, axes = plt.subplots(4, 1, figsize=(12.0, 10.2), gridspec_kw={"height_ratios": [1.5, 1.15, 1.0, 1.0]})
    ax = axes[0]
    im = ax.imshow(z.T, extent=[time[0], time[-1], len(idx), 0], aspect="auto", cmap="RdBu_r", vmin=-3, vmax=3)
    for b in group["boundary_indices"]:
        ax.axvline(b * TR_SECONDS / 60, color="k", lw=0.3, alpha=0.45)
    ax.set_ylabel("Selected AG voxels")
    ax.set_title("A  Full-length group-mean Sherlock fMRI and HP-GSBS boundaries", loc="left")
    fig.colorbar(im, ax=ax, fraction=.016, pad=.008, label="display z score")

    ax = axes[1]
    for j, row in enumerate(subject_rows):
        bs = np.asarray(row["boundary_indices"], dtype=int)
        ax.vlines(bs * TR_SECONDS / 60, j + .15, j + .85, lw=.6)
    ax.set_ylim(0, max(1, len(subject_rows)))
    ax.set_ylabel("Participant index")
    ax.set_title("B  Independently fitted subject-level boundary timelines", loc="left")

    ax = axes[2]
    k = np.asarray(group["evaluated_K_indices"], dtype=int)
    ax.plot(k, np.asarray(group["tdists"])[k], label="Group mean", linewidth=2.0)
    for j, row in enumerate(subject_rows):
        kk = np.asarray(row["evaluated_K_indices"], dtype=int)
        ax.plot(kk, np.asarray(row["tdists"])[kk], alpha=.20, linewidth=.8,
                label="Individual subjects" if j == 0 else None)
    ax.axvline(group["selected_K"], linestyle="--", linewidth=.8)
    ax.set_xlabel("State-count index K")
    ax.set_ylabel("t-distance")
    ax.legend(frameon=False)
    ax.set_title("C  State-count selection across group and individuals", loc="left")

    ax = axes[3]
    if null_result.get("status") == "complete":
        vals = np.asarray(null_result["null_scores"])
        ax.hist(vals, bins=35, density=True, alpha=.65, label="Circular-shift null")
        ax.axvline(null_result["observed_pairwise_mean_f1"], color="black", linewidth=1.5,
                   label="Observed pairwise matching")
        ax.set_xlabel("Mean pairwise boundary matching F1")
        ax.set_ylabel("Null density")
        ax.legend(frameon=False)
        ax.set_title("D  Descriptive intersubject boundary alignment", loc="left")
    else:
        ax.text(.5, .5, "At least two subject fits required", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()

    axes[0].set_xlabel("Time in scanner run (min)")
    axes[1].set_xlabel("Time in scanner run (min)")
    fig.tight_layout()
    fig.savefig(out / "sherlock_fmri_application.pdf", bbox_inches="tight")
    fig.savefig(out / "sherlock_fmri_application.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fit_one(label: str, x: np.ndarray, out: Path, cfg, software_version: str) -> dict:
    from hpgsbs import fit
    from hpgsbs.core.interval_scores import conditioning_reason

    if not np.isfinite(x).all():
        raise ValueError(f"{label}: nonfinite source input; do not impute")
    sd = x.std(axis=1, ddof=1)
    if np.any(sd == 0) or not np.isfinite(sd).all():
        raise ValueError(f"{label}: row spatial variance invalid; do not impute")
    if conditioning_reason(x, "float64") is not None:
        raise ValueError(f"{label}: ill-conditioned; aborted BEFORE HP-GSBS, to avoid official fallback")

    t0 = perf_counter()
    r = fit(x, cfg, backend="cpu-fast")  # NEVER call reference or official benchmark
    elapsed = perf_counter() - t0
    if r.metadata.get("backend") != "cpu-fast" or r.metadata.get("status") != "success":
        raise RuntimeError(f"{label}: non-CPU result or unsuccessful computation; refusing to report")
    K = int(r.nstates)
    bounds = np.flatnonzero(r.get_bounds(K) > 0).astype(int)
    bounds = bounds[(bounds > 0) & (bounds < len(x))]

    if np.unique(bounds).size != bounds.size:
        raise RuntimeError(f"{label}: duplicate boundary positions")
    if len(bounds) + 1 != K:
        raise RuntimeError(f"{label}: selected K and boundary count disagree")

    # Omit uncomputed padded t-distance slots (including the optional Kmax+1 slot).
    evaluated_k = np.flatnonzero(np.count_nonzero(np.asarray(r.all_bounds), axis=1) > 0)
    evaluated_k = evaluated_k[evaluated_k >= 2]
    payload = dict(label=label, shape=list(x.shape), selected_K=K,
                   boundary_indices=bounds.tolist(), evaluated_K_indices=evaluated_k.tolist(),
                   tdists=np.asarray(r.tdists).tolist(),
                   elapsed_s=float(elapsed), backend="cpu-fast", software_version=software_version,
                   analysis_dtype="float64")
    # Compact saved output; original source input can be retrieved and verified from Figshare.
    np.savez_compressed(out / f"{label}_segmentation.npz",
                        selected_K=np.array(K), boundary_indices=bounds,
                        evaluated_K_indices=evaluated_k,
                        all_bounds=np.asarray(r.all_bounds), tdists=np.asarray(r.tdists))
    return payload


def main() -> None:
    p = argparse.ArgumentParser(description="Full-length fMRI application; NO original GSBS fits")
    p.add_argument("--input", type=Path, required=True, help="Original Sherlock_AG_movie.npy from Figshare")
    p.add_argument("--output", type=Path, required=True, help="A new, nonexistent output directory")
    p.add_argument("--kmax", type=int, default=60)
    p.add_argument("--subjects", default="all", help="all, none, or comma-separated zero-based indices")
    p.add_argument("--perm", type=int, default=1000)
    p.add_argument("--tolerance", type=int, default=3)
    p.add_argument("--null-seed", type=int, default=20261020)
    p.add_argument("--skip-md5", action="store_true", help="Only for independently verified sources")
    args = p.parse_args()
    if args.output.exists():
        p.error("Output already exists: choose a new directory to preserve existing measurements")
    if not args.input.is_file():
        p.error("Input not found; download the original NPY file from the linked Figshare dataset")
    digest = checksum(args.input)
    if digest != EXPECTED_MD5 and not args.skip_md5:
        p.error(f"Source MD5 mismatch: {digest} (expected {EXPECTED_MD5}); refuse to analyze")
    data = np.load(args.input, mmap_mode="r", allow_pickle=False)
    if tuple(data.shape) != EXPECTED_SHAPE or data.dtype.kind not in "f":
        p.error(f"Expected float {EXPECTED_SHAPE} source, got shape={data.shape}, dtype={data.dtype}")
    if args.kmax < 2 or args.kmax >= EXPECTED_SHAPE[1]:
        p.error("Require 2 <= Kmax < 946")
    if args.subjects == "all":
        subjects = list(range(data.shape[0]))
    elif args.subjects == "none":
        subjects = []
    else:
        subjects = sorted({int(x) for x in args.subjects.split(",")})
        if not subjects or min(subjects) < 0 or max(subjects) >= data.shape[0]:
            p.error("Invalid subjects indices")
    if args.perm < 1 or args.tolerance < 0:
        p.error("Require positive permutations and nonnegative boundary tolerance")

    from hpgsbs import GSBSConfig, __version__
    if __version__ != "0.2.0":
        raise RuntimeError(f"Pin hpgsbs==0.2.0, found {__version__}")
    cfg = GSBSConfig(kmax=args.kmax, dmin=1, statewise_detection=True,
                     finetune=1, finetune_order=True, blocksize=50,
                     dtype="float64", q_strategy="full", td_backend="prefix2d",
                     candidate_backend="streaming", mode="latency")
    args.output.mkdir(parents=True)

    manifest = dict(dataset=FIGSHARE, input_file=args.input.name,
                    source_md5=digest, input_shape=list(data.shape),
                    HP_GSBS_version=__version__, reference_fits_run=False,
                    original_GSBS_timing_run=False, GSBS_config=cfg.algorithm(),
                    subject_indices=subjects, number_permutations=args.perm,
                    boundary_match_tolerance_TR=args.tolerance, scan_TR_seconds=TR_SECONDS)
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    group_x = group_mean(data)
    group = fit_one("group_mean", group_x, args.output, cfg, __version__)
    rows = []
    for idx in subjects:
        x = np.asarray(data[idx], dtype=np.float64)
        row = fit_one(f"subject_{idx:02d}", x, args.output, cfg, __version__)
        row["subject_zero_based"] = idx
        rows.append(row)
        print(f"Subject {idx + 1:02d}: K={row['selected_K']}, {row['elapsed_s']:.2f}s", flush=True)
    null = circular_shift_null([np.asarray(r["boundary_indices"]) for r in rows],
                               T=data.shape[1], tolerance=args.tolerance,
                               n_perm=args.perm, seed=args.null_seed)
    plot_figure(args.output, group_x, group, rows, null)
    report = dict(manifest=manifest, group_mean=group, subject_results=rows, null_test=null)
    (args.output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    with (args.output / "fit_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["label", "selected_K", "n_boundaries", "elapsed_s"])
        writer.writeheader()
        for r in [group, *rows]:
            writer.writerow(dict(label=r["label"], selected_K=r["selected_K"],
                                 n_boundaries=len(r["boundary_indices"]), elapsed_s=r["elapsed_s"]))
    print(f"Completed {1 + len(rows)} HP-GSBS CPU fits; zero official GSBS fits. Output: {args.output}")


if __name__ == "__main__":
    main()
