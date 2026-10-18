"""Figure 4: render the existing release-development measurements, no fitting."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parent
ab=pd.read_csv(ROOT/'data/ablation.csv')
mem=pd.read_csv(ROOT/'data/memory_long.csv')
thr=pd.read_csv(ROOT/'data/throughput.csv')
blue='#0072B2';orange='#D55E00';green='#009E73';grey='#A5ADB3'
ink='#23364B';muted='#647582';grid='#E5EAEE'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,
    'axes.labelsize':8,'axes.titlesize':8,'xtick.labelsize':7,'ytick.labelsize':7,
    'axes.linewidth':.65,'lines.linewidth':1.25,'pdf.fonttype':42,'svg.fonttype':'none',
    'svg.hashsalt':'hpgsbs-figure4-enhanced','axes.labelcolor':ink,
    'xtick.color':muted,'ytick.color':muted,'text.color':ink,'axes.edgecolor':muted})
fig=plt.figure(figsize=(7.6,5.45),facecolor='white')
def txt(x,y,s,**kw):return fig.text(x,y,s,**kw)
def header(x,y,letter,title):
    txt(x,y,letter,fontsize=12,weight='bold',va='center')
    txt(x+.043,y,title,fontsize=10,weight='bold',va='center')
def axis(rect,grid_y=False):
    a=fig.add_axes(rect)
    a.spines[['top','right']].set_visible(False)
    a.tick_params(width=.6,length=2.5,pad=3)
    a.set_axisbelow(True)
    if grid_y:a.grid(axis='y',color=grid,lw=.5)
    return a

# A: same stages, values and observed ranges as in the supplied Figure 4.
header(.035,.965,'A','Computation reuse')
a=axis([.165,.632,.23,.255])
y=np.arange(len(ab))
a.barh(y,ab.median_s,color=[grey,blue,'#4A99C8','#7EB5D6'],height=.53,zorder=2)
a.errorbar(ab.median_s,y,xerr=[ab.median_s-ab.min_s,ab.max_s-ab.median_s],
           fmt='none',ecolor=ink,elinewidth=.8,capsize=2,zorder=3)
for i,v in enumerate(ab.median_s):a.text(v+.11,i,f'{v:.2f}',va='center',fontsize=7.7)
a.set(yticks=y,yticklabels=['Materialized','Streaming','+ Window','+ Cache'],
      ylim=(3.6,-.6),xlim=(0,4),xticks=[0,1,2,3,4],xlabel='Complete-fit time (s)')

# B: paired memory/runtime comparisons and independent long-input measurements.
header(.443,.965,'B','Long-input efficiency')
handles=[Line2D([],[],marker='s',lw=0,color=c,markersize=5,label=s)
         for c,s in [(grey,'Full-Q'),(blue,'Low-memory')]]
fig.legend(handles=handles,loc='center left',bbox_to_anchor=(.467,.924),
           ncol=2,frameon=False,fontsize=7,handletextpad=.4,columnspacing=1.1)
txt(.584,.889,r'$T=5{,}000,\ P=8$',fontsize=7.4,color=muted,ha='center')
m=mem[mem.scope=='memory comparison'].set_index('mode')
rss_ratio=m.loc['Materialized','peak_rss_MiB']/m.loc['Low-memory','peak_rss_MiB']
time_ratio=m.loc['Materialized','median_s']/m.loc['Low-memory','median_s']

def comparison_bars(rect,col,lim,ticks,labels,title,errors=False):
    a=axis(rect)
    values=[m.loc['Materialized',col],m.loc['Low-memory',col]]
    a.bar([0,1],values,width=.62,color=[grey,blue],zorder=2)
    for i,(mode,v,lab) in enumerate(zip(['Materialized','Low-memory'],values,labels)):
        top=v
        if errors:
            q=m.loc[mode]
            a.errorbar(i,v,yerr=[[v-q.min_s],[q.max_s-v]],fmt='none',
                       ecolor=ink,elinewidth=.65,capsize=1.7,zorder=3)
            top=q.max_s
        a.annotate(lab,(i,top),xytext=(0,4),textcoords='offset points',
                   ha='center',fontsize=7.1,color=ink)
    a.set(xlim=(-.65,1.65),ylim=lim,yticks=ticks,xticks=[])
    a.tick_params(axis='y',labelsize=6.7,pad=2)
    a.set_title(title,fontsize=7.4,pad=8)
comparison_bars([.465,.635,.085,.21],'peak_rss_MiB',(0,2000),[0,800,1600],
                ['1,598','190.6'],'Peak RSS (MiB)')
comparison_bars([.617,.635,.085,.21],'median_s',(0,12),[0,5,10],
                ['9.754','0.110'],'Runtime (s)',errors=True)

long=mem[mem.scope=='long recording'].sort_values('T')
a=axis([.795,.635,.18,.255],grid_y=True)
x=np.arange(len(long));a.plot(x,long.peak_rss_MiB,'o-',color=blue,markersize=4,lw=1.25)
for xx,v in zip(x,long.peak_rss_MiB):
    a.annotate(f'{v:.1f}',(xx,v),xytext=(0,7),textcoords='offset points',ha='center',fontsize=7.2)
a.set(xlim=(-.55,3.45),ylim=(0,550),yticks=[0,250,500],xticks=x,
      xticklabels=['5k\n× 8','10k\n× 16','20k\n× 32','50k\n× 64'],
      xlabel='Input size (T × P)',ylabel='Peak RSS (MiB)')
a.tick_params(axis='x',labelsize=6.6)
a.set_title('Low-memory workloads',fontsize=8,pad=8)

# C/D: separate CPU and GPU parameter axes; shared y-range within each workload.
colours={'cpu-fast':blue,'torch-cuda':orange,'triton-cuda':green}
markers={'cpu-fast':'s','torch-cuda':'o','triton-cuda':'^'}
def trend(a,rows,colx,backend):
    q=rows[rows.backend==backend].sort_values(colx)
    v=q.median_fits_min
    a.errorbar(q[colx],v,yerr=[v-q.min_fits_min,q.max_fits_min-v],
               color=colours[backend],marker=markers[backend],markersize=3.6,lw=1.2,
               capsize=2,elinewidth=.7,markeredgewidth=.6,zorder=3)
    return q
for wl,x0,letter,title,desc,ylim,yticks,gpu_ticks,cpu_w,gpu_w in [
    ('Small',.087,'C','Short inputs',r'450 time points × 16 features, $K_{\max}=20$',2000,[0,1000,2000],[1,8,32,64],.145,.185),
    ('High-K',.582,'D',r'High-$K$ input',r'1336 time points × 64 features, $K_{\max}=131$',180,[0,50,100,150],[1,4,8],.145,.174)]:
    header(x0-.052,.509,letter,title)
    txt(x0-.009,.472,desc,fontsize=7.4,color=muted)
    q=thr[thr.workload==wl]
    cpu=axis([x0,.12,cpu_w,.285],grid_y=True)
    gpu=axis([x0+.219,.12,gpu_w,.285],grid_y=True)
    trend(cpu,q,'workers','cpu-fast')
    for b in ['torch-cuda','triton-cuda']:trend(gpu,q,'batch',b)
    cpu.set(xlim=(.6,8.4),xticks=[1,2,4,8],ylim=(0,ylim),yticks=yticks,
            xlabel='Workers',ylabel='Throughput (fits/min)')
    gpu.set(xlim=(0,max(gpu_ticks)*1.045),xticks=gpu_ticks,ylim=(0,ylim),yticks=yticks,
            xlabel='Batch size',yticklabels=[])
    gpu.spines['left'].set_visible(False);gpu.tick_params(axis='y',length=0)
    cpu.set_title('CPU scaling',pad=9);gpu.set_title('GPU batching',pad=9)

legend=[Line2D([],[],color=colours[b],marker=markers[b],lw=1.2,markersize=4,label=s)
        for b,s in [('cpu-fast','CPU'),('torch-cuda','PyTorch CUDA'),('triton-cuda','Triton')]]
fig.legend(handles=legend,loc='center',bbox_to_anchor=(.53,.026),ncol=3,
           frameon=False,fontsize=8,handlelength=2,columnspacing=2.8)

for ext in ['pdf','svg','png']:
    fig.savefig(ROOT/f'Figure4_HP_GSBS.{ext}',dpi=350,facecolor='white')
plt.rcParams['svg.fonttype']='path'
fig.savefig(ROOT/'Figure4_HP_GSBS_outlined.svg',facecolor='white')
plt.close(fig)
summary={'data_source':'Existing submission-package release-development measurements',
         'new_benchmarks_run':False,'ablation_rows':len(ab),'throughput_points':len(thr),
         'direct_comparison_RSS_ratio':float(rss_ratio),'direct_comparison_speedup':float(time_ratio),
         'long_input_RSS_MiB':long.peak_rss_MiB.tolist(),
         'CPU_workers':[1,2,4,8],'GPU_batches_short':[1,8,32,64],'GPU_batches_high_K':[1,4,8],
         'error_bars':'observed minimum–maximum over three timed runs or batches; no RSS error bars'}
(ROOT/'figure_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
