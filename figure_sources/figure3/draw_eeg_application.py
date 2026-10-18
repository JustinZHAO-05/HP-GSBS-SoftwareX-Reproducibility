#!/usr/bin/env python3
"""Render the EEG application figure from saved fits; no GSBS fit is run."""
from pathlib import Path
import json
import hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
FILES = {
    'official': '0_full_reference.npz',
    'cpu': '0_full_cpu.npz',
    'torch': '0_torch-cuda_float64.npz',
    'triton': '0_triton-cuda_float64.npz',
}
PIPELINE = 'sub-01_ses-01_stim01__all64__5.12hz__d5__k131.npz'
COLORS = {'official': '#333333', 'cpu': '#0072B2', 'torch': '#D55E00', 'triton': '#009E73'}
LABELS = {'official': 'Official', 'cpu': 'HP CPU', 'torch': 'HP PyTorch', 'triton': 'HP Triton'}
MARKERS = {'official': 'o', 'cpu': 's', 'torch': '^', 'triton': 'D'}
STATE_COLORS = ['#DDD5EC', '#EADCB8']
FOCUS = '#6B587F'
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 8, 'axes.labelsize': 8,
    'axes.titlesize': 9, 'xtick.labelsize': 7, 'ytick.labelsize': 7,
    'axes.linewidth': .6, 'pdf.fonttype': 42, 'ps.fonttype': 42,
    'svg.fonttype': 'none', 'svg.hashsalt': 'hpgsbs-eeg-application',
    'savefig.facecolor': 'white',
})


def clean(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(width=.6, length=3)


def heading(fig, x, y, letter, title):
    fig.text(x, y, letter, fontsize=11, fontweight='bold', va='baseline')
    fig.text(x + .035, y, title, fontsize=9, va='baseline', fontweight='medium')


def state_strip(ax, edges, time_edges, window):
    for i, (a, b) in enumerate(zip(edges[:-1], edges[1:])):
        if time_edges[b] <= window[0] or time_edges[a] >= window[1]:
            continue
        ax.add_patch(Rectangle((time_edges[a], 0), time_edges[b]-time_edges[a], 1,
                              facecolor=STATE_COLORS[i % 2], edgecolor='white', linewidth=.30))
    ax.set(xlim=window, ylim=(0, 1), yticks=[])
    ax.tick_params(axis='x', length=3, width=.6)
    for s in ax.spines.values():
        s.set_visible(False)


def load_and_check():
    fits = {k: np.load(DATA / v, allow_pickle=False) for k, v in FILES.items()}
    pipeline = np.load(DATA / PIPELINE, allow_pickle=False)
    ref = fits['official']
    x = ref['x']
    meta = json.loads(str(ref['metadata']))
    times = pipeline['times']
    dt = 1 / meta['source_spec']['sfreq']
    assert x.shape == (1336, 64)
    assert np.isfinite(x).all()
    assert np.array_equal(x, pipeline['x'])
    assert np.allclose(np.diff(times), dt)
    # Original timestamps are centres of contiguous 5.12-Hz bins.
    time_edges = np.r_[times-dt/2, times[-1]+dt/2]
    selected = int(ref['nstates'])
    boundary_idx = np.flatnonzero(ref['bounds'])
    assert np.array_equal(ref['bounds'], ref['all_bounds'][selected])
    assert np.allclose(times[boundary_idx], pipeline['boundary_timestamps'])
    edges = np.r_[0, boundary_idx, len(x)]
    assert np.array_equal(np.diff(edges), ref['state_durations_samples'])
    # Preserve actual search indices, including repeated double-insertion slots.
    # Slot 132 is allocated padding, not an evaluated partition.
    ks = np.flatnonzero(np.any(ref['all_bounds'] != 0, axis=1))
    assert ks[0] == 2 and ks[-1] == 131
    assert ks[np.argmax(ref['tdists'][ks])] == selected
    checks = {}
    for name, fit in fits.items():
        checks[name] = {
            'input_equal': bool(np.array_equal(x, fit['x'])),
            'selected_K': int(fit['nstates']),
            'boundary_history_equal': bool(np.array_equal(ref['all_bounds'], fit['all_bounds'])),
            'selected_boundaries_equal': bool(np.array_equal(ref['bounds'], fit['bounds'])),
            'state_patterns_equal': bool(np.array_equal(ref['state_patterns'], fit['state_patterns'])),
            'max_abs_tdistance_difference': float(np.max(np.abs(ref['tdists'][ks]-fit['tdists'][ks]))),
        }
        assert checks[name]['input_equal'] and checks[name]['boundary_history_equal']
        assert checks[name]['selected_boundaries_equal'] and checks[name]['selected_K'] == selected
    # Fixed 20-s window centred on the recording midpoint, snapped to bin edges.
    start = int(round((len(x) * dt / 2 - 10) / dt))
    stop = start + int(round(20 / dt))
    window = (float(time_edges[start]), float(time_edges[stop]))
    z = x[start:stop] - x[start:stop].mean(axis=1, keepdims=True)
    z = z / z.std(axis=1, ddof=1, keepdims=True)
    z = z - z.mean(axis=1, keepdims=True)
    similarity = z @ z.T / (x.shape[1]-1)
    assert np.allclose(similarity, np.corrcoef(x[start:stop]))
    summary = {
        'recording': 'Recording 1', 'shape': list(x.shape),
        'sampling_rate_Hz': 1/dt, 'duration_s': float(time_edges[-1]-time_edges[0]),
        'representation': meta['source_spec']['row']['representation_id'],
        'channel_names': meta['source_spec']['row']['channel_names'].split('|'),
        'algorithm': meta['algorithm'], 'selected_K': selected,
        'boundary_count': len(boundary_idx), 'evaluated_K_indices': ks.tolist(),
        'unused_trailing_slot': 132, 'display_window_samples': [start, stop],
        'display_window_seconds': list(window),
        'window_selection': 'Fixed 20 s about the full-record midpoint, rounded to sample bins; no refitting.',
        'time_axis': 'Original sample-bin edges; saved boundary timestamps identify the centre of the first bin of each new state.',
        'heatmap_color_limits': [-3, 3], 'heatmap_scale': 'Existing standardized input; no new normalization.',
        'comparison': checks,
        'file_sha256': {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in DATA.glob('*.npz')},
    }
    (ROOT/'figure_data_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    return fits, x, time_edges, edges, ks, selected, start, stop, window, similarity, summary


def main():
    fits, x, t, edges, ks, selected, start, stop, window, similarity, summary = load_and_check()
    fig = plt.figure(figsize=(7.2, 7.1))
    # A: all input samples and all selected states.
    heading(fig, .035, .955, 'A', 'Full-record segmentation')
    fig.text(.925, .956, '64 channels · 5.12 Hz', fontsize=7.2, ha='right', color='#555555')
    a = fig.add_axes([.105, .775, .805, .150])
    im = a.imshow(x.T, origin='lower', aspect='auto', interpolation='nearest',
                  extent=[t[0], t[-1], .5, 64.5], cmap='RdBu_r', vmin=-3, vmax=3)
    a.set(yticks=[1, 32, 64], ylabel='Channel', xlim=(t[0], t[-1]))
    a.tick_params(axis='x', bottom=False, labelbottom=False)
    clean(a)
    a.add_patch(Rectangle((window[0], .5), window[1]-window[0], 64, facecolor='none',
                         edgecolor=FOCUS, linewidth=1.25,
                         path_effects=[pe.Stroke(linewidth=2.2, foreground='white'), pe.Normal()]))
    a.text(np.mean(window), 66.5, 'B–C', color=FOCUS, fontsize=7, ha='center', va='bottom')
    cb = fig.colorbar(im, cax=fig.add_axes([.932, .775, .012, .150]), ticks=[-3, 0, 3], extend='both')
    cb.ax.tick_params(labelsize=6.5, width=.5, length=2)
    cb.ax.set_title('z', fontsize=8, pad=4)
    sa = fig.add_axes([.105, .742, .805, .019])
    state_strip(sa, edges, t, (t[0], t[-1]))
    sa.set_xticks([0, 60, 120, 180, 240])
    sa.set_xlabel('Time (s)', labelpad=2)
    sa.text(-.018, .5, 'States', transform=sa.transAxes, ha='right', va='center', fontsize=7)

    # B: one fixed central window, shared with C. Four compact boundary rows.
    heading(fig, .035, .658, 'B', 'Boundary agreement · zoom')
    b = fig.add_axes([.125, .485, .390, .145])
    b.imshow(x[start:stop].T, origin='lower', aspect='auto', interpolation='nearest',
             extent=[window[0], window[1], .5, 64.5], cmap='RdBu_r', vmin=-3, vmax=3)
    for at in t[edges[1:-1]]:
        if window[0] < at < window[1]:
            b.axvline(at, color='#222222', lw=.55,
                      path_effects=[pe.Stroke(linewidth=1.15, foreground='white'), pe.Normal()])
    b.set(yticks=[1, 32, 64], ylabel='Channel', xlim=window)
    b.tick_params(axis='x', bottom=False, labelbottom=False)
    clean(b)
    sb = fig.add_axes([.125, .461, .390, .014])
    state_strip(sb, edges, t, window)
    sb.set_xticks([])
    sb.text(-.025, .5, 'States', transform=sb.transAxes, ha='right', va='center', fontsize=6.8)
    br = fig.add_axes([.125, .371, .390, .078])
    for row, name in enumerate(FILES):
        bt = t[np.flatnonzero(fits[name]['bounds'])]
        bt = bt[(bt >= window[0]) & (bt <= window[1])]
        br.hlines(row, *window, color='#E4E7EA', lw=.5)
        br.scatter(bt, np.full(len(bt), row), marker='|', s=34, linewidths=1.25, color=COLORS[name])
    br.set(xlim=window, ylim=(3.6, -.6), yticks=range(4), yticklabels=list(LABELS.values()),
           xticks=[125, 130, 135, 140], xlabel='Time (s)')
    br.tick_params(axis='y', length=0, labelsize=6.4, pad=4)
    br.tick_params(axis='x', length=2, labelsize=7)
    br.spines[['top', 'right', 'left']].set_visible(False)

    # C: full symmetric, unmasked correlation matrix for precisely the B window.
    heading(fig, .585, .658, 'C', 'Temporal pattern similarity')
    c = fig.add_axes([.650, .375, .255, .255*7.2/7.1])
    ci = c.imshow(similarity, origin='lower', aspect='equal', interpolation='nearest',
                  extent=[*window, *window], cmap='RdBu_r', vmin=-1, vmax=1)
    for i, (left, right) in enumerate(zip(edges[:-1], edges[1:])):
        lo, hi = max(t[left], window[0]), min(t[right], window[1])
        if hi <= lo:
            continue
        c.add_patch(Rectangle((lo, lo), hi-lo, hi-lo, facecolor='none', edgecolor='#282828',
                             linewidth=.75,
                             path_effects=[pe.Stroke(linewidth=1.6, foreground='white'), pe.Normal()]))
    c.set(xlim=window, ylim=window, xlabel='Time (s)', ylabel='Time (s)',
          xticks=[125, 130, 135, 140], yticks=[125, 130, 135, 140])
    c.tick_params(labelsize=6.5, width=.6, length=2)
    cc = fig.colorbar(ci, cax=fig.add_axes([.927, .375, .012, .255*7.2/7.1]), ticks=[-1, 0, 1])
    cc.ax.tick_params(labelsize=6.5, width=.5, length=2)
    cc.ax.set_title('r', fontsize=8, pad=4)
    # D: all evaluated TD slots, no padded endpoint or re-indexing.
    heading(fig, .035, .285, 'D', 'State-count selection')
    d = fig.add_axes([.105, .075, .805, .180])
    for offset, name in enumerate(FILES):
        # Stagger marker positions only; curves and their coordinates are unchanged.
        d.plot(ks, fits[name]['tdists'][ks], color=COLORS[name],
               lw=1.5 if name=='official' else .85, marker=MARKERS[name],
               ms=3.0, mfc='white', mew=.75, markevery=(offset*3, 16),
               zorder=2+offset, alpha=.95)
    peak = float(fits['official']['tdists'][selected])
    d.axvline(selected, ymin=.20, color='#737373', ls=':', lw=.7, zorder=1)
    d.annotate(r'$K^*='+str(selected)+'$', xy=(selected, peak), xytext=(97, 11.5),
               fontsize=8, ha='left', va='center',
               arrowprops=dict(arrowstyle='-', lw=.65, color='#555555', shrinkA=3, shrinkB=4))
    d.set(xlim=(0, 134), ylim=(-.3, 12.7), xticks=[2, 25, 50, 75, 100, 125],
          yticks=[0, 4, 8, 12], xlabel='State-count index $K$', ylabel='t-distance')
    d.grid(axis='y', color='#ECEEF0', lw=.45)
    clean(d)
    max_error = max(v['max_abs_tdistance_difference'] for v in summary['comparison'].values())
    mantissa, exponent = f'{max_error:.2e}'.split('e')
    error_label = r'Max. $|\Delta\mathrm{TD}|='+mantissa+r'\times10^{'+str(int(exponent))+'}$'
    d.text(.025, .91, error_label,
           transform=d.transAxes, fontsize=7.2, va='top', color='#333333')
    handles = [Line2D([0],[0], color=COLORS[k], marker=MARKERS[k],
                      ms=3.3, mfc='white', mew=.7, lw=1, label=LABELS[k]) for k in FILES]
    d.legend(handles=handles, loc='lower right', bbox_to_anchor=(1, .01), ncol=4,
             frameon=False, fontsize=6.8, handlelength=1.5, columnspacing=1.2, borderpad=.2)
    for ext in ('pdf', 'svg', 'png'):
        fig.savefig(ROOT/f'Figure_EEG_application.{ext}', dpi=400, facecolor='white')
    plt.close(fig)
    print(json.dumps({k: summary[k] for k in ['shape', 'selected_K', 'display_window_seconds', 'comparison']}, indent=2))


if __name__ == '__main__':
    main()
