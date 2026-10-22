from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];D=R/'data';O=R/'tables';O.mkdir(exist_ok=True)
order=['T1','T2','T3','P1','P2','K1','K2'];runtime=pd.read_csv(D/'paired_runtime.csv');speed=pd.read_csv(D/'paired_speedup.csv')
def write(name,lines): (O/name).write_text('\n'.join(lines)+'\n')
rows=[]
for co in order:
 r=runtime[runtime.condition==co].set_index('backend');s=r.iloc[0]
 cols=[f"{s['T']:.0f}",f"{s['P']:.0f}",f"{s['Kmax']:.0f}"]
 for b in ['official','cpu-fast','torch-cuda','triton-cuda']:
  v=r.loc[b];cols.append(f"{v.median_s:.3f} [{v.min_s:.3f}, {v.max_s:.3f}]")
 rows.append(' & '.join(cols)+r' \\')
write('runtime_rows.tex',rows)
rows=[]
for co in order:
 r=speed[speed.condition==co].set_index('backend');s=runtime[runtime.condition==co].iloc[0]
 cols=[f"{s['T']:.0f}",f"{s['P']:.0f}",f"{s['Kmax']:.0f}"]
 for b in ['cpu-fast','torch-cuda','triton-cuda']:
  v=r.loc[b];cols.append(f"{v['median']:.1f} [{v['min']:.1f}, {v['max']:.1f}]")
 rows.append(' & '.join(cols)+r' \\')
write('speedup_rows.tex',rows)
rows=[]
for _,v in pd.read_csv(D/'paired_per_input.csv').groupby(['condition','seed'],sort=False):
 row=v.iloc[0];vals=v.set_index('backend');cols=[f"{row['T']}",f"{row['P']}",f"{row['Kmax']}",str(row['seed'])]
 for b in ['official','cpu-fast','torch-cuda','triton-cuda']:cols.append(f"{vals.loc[b].median_s:.4f}")
 rows.append(' & '.join(cols)+r' \\')
write('perinput_rows.tex',rows)
rows=[]
for _,v in pd.read_csv(D/'throughput.csv').iterrows():
 b={'cpu-fast':'CPU','torch-cuda':'PyTorch','triton-cuda':'Triton'}[v.backend]
 rows.append(f"{v.workload} & {b} & {v.workers} & {v.batch} & {v.median_fits_min:.1f} [{v.min_fits_min:.1f}, {v.max_fits_min:.1f}]"+r' \\')
write('throughput_rows.tex',rows)

# Separate cross-session historical release comparisons.
import ast
hist = pd.read_csv(R/'data/historical_extended.csv')
rows = []
for workload, group in hist.groupby('workload', sort=False):
    q = group.set_index('backend')
    T, P = ast.literal_eval(q.loc['reference', 'shape'])
    vals = [f"{q.loc[b, 'seconds']:.3f} ({q.loc[b, 'speedup']:,.0f}x)" for b in ['cpu-fast', 'torch-cuda', 'triton-cuda']]
    name = 'EEG' if workload == 'BBBD0' else workload
    rows.append(f"{name} & ${T}\\times{P}$ & {int(q.loc['reference', 'kmax'])} & {q.loc['reference', 'seconds']:.1f} & " + ' & '.join(vals) + r" \\")
(O/'extended_rows.tex').write_text('\n'.join(rows)+'\n')

# Complete cohort application table, separate from controlled timing comparisons.
rows=[]
for _, v in pd.read_csv(D/'fmri/fit_summary.csv').iterrows():
    label='Group mean' if v.label=='group_mean' else f'Participant {int(v.label.split("_")[1])+1}'
    rows.append(f'{label} & {v.selected_K} & {v.n_boundaries} & {v.elapsed_s:.4f}'+r' \\')
write('fmri_fit_rows.tex',rows)
