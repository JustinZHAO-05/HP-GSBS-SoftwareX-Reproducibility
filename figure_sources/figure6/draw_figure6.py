"""Figure 6 from frozen derived arrays; no GSBS fits or network access."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[2]
d = np.load(ROOT / 'data/fmri/figure6_data.npz', allow_pickle=False)
plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':9,
    'axes.labelsize':9, 'xtick.labelsize':8.5, 'ytick.labelsize':8.5,
    'axes.linewidth':.65, 'pdf.fonttype':42, 'svg.fonttype':'none'})
blue, gray, ink = '#0072B2', '#8B969F', '#263746'
fig = plt.figure(figsize=(7.1, 6.6), facecolor='white')
def axes(rect):
    a=fig.add_axes(rect)
    a.spines[['top','right']].set_visible(False)
    a.tick_params(length=2.5, width=.6)
    return a
def heading(y, letter, title, x=.035):
    fig.text(x,y,letter,fontsize=12,weight='bold',color=ink)
    fig.text(x+.035,y,title,fontsize=10,weight='bold',color=ink)

heading(.975,'a','Group response')
a=axes([.10,.762,.81,.175])
im=a.imshow(d['display_z'].T,aspect='auto',origin='lower',interpolation='nearest',
            extent=(0,1419,.5,72.5),cmap='RdBu_r',vmin=-3,vmax=3,rasterized=True)
a.set(yticks=[1,36,72],ylabel='Voxel',xlim=(0,1419))
a.tick_params(axis='x',bottom=False,labelbottom=False)
r=fig.add_axes([.10,.94,.81,.015]);r.set(xlim=(0,1419),ylim=(0,1));r.axis('off')
r.vlines(d['group__boundary_indices']*1.5,0,1,color=blue,lw=.7)
cb=fig.colorbar(im,cax=fig.add_axes([.93,.762,.012,.175]),ticks=[-3,0,3])
cb.ax.set_title('z',fontsize=9,pad=3);cb.ax.tick_params(labelsize=8.5,length=2)

heading(.717,'b','Selected boundaries')
b=axes([.10,.43,.81,.256])
prefixes=['group__']+[f'subject_{i:02d}__' for i in range(16)]
for row, pre in enumerate(prefixes):
    b.hlines(row,0,1419,color='#E8ECEF',lw=.45,zorder=0)
    b.vlines(d[pre+'boundary_indices']*1.5,row-.34,row+.34,
             color=blue if row==0 else gray,lw=.75)
b.set(xlim=(0,1419),ylim=(16.6,-.6),xticks=[0,300,600,900,1200],
      yticks=[0,1,4,8,12,16],yticklabels=['Group','1','4','8','12','16'],
      xlabel='Time (s)',ylabel='Participant')
b.tick_params(axis='y',length=0)

heading(.337,'c','State-count curves')
heading(.337,'d','Boundary alignment',x=.57)
c=axes([.10,.079,.37,.218])
for pre in prefixes[1:]:
    ks=d[pre+'evaluated_K_indices']; ys=d[pre+'tdists'][ks]
    c.plot(ks,ys,color=gray,alpha=.55,lw=.65)
    k=int(d[pre+'selected_K']);c.plot(k,d[pre+'tdists'][k],'o',color=gray,ms=2.7)
ks=d['group__evaluated_K_indices']
c.plot(ks,d['group__tdists'][ks],color=blue,lw=1.5)
k=int(d['group__selected_K']);c.plot(k,d['group__tdists'][k],'o',color=blue,ms=4)
c.axvline(60,color=ink,ls=':',lw=.7)
c.set(xlim=(1,63),xticks=[2,20,40,60],xlabel='State-count index $K$',ylabel='t-distance')
c.legend(handles=[Line2D([],[],color=blue,label='Group'),Line2D([],[],color=gray,label='Participants')],
         frameon=False,fontsize=8.5,loc='upper left',handlelength=1.4)
e=axes([.635,.079,.32,.218])
obs=float(d['observed_f1']);null=d['null_scores']
e.hist(null,bins=26,color='#6AA9CE',edgecolor='white',lw=.35)
e.axvline(obs,color=blue,lw=1.5)
e.text(obs-.003,e.get_ylim()[1]*.9,'Observed',rotation=90,ha='right',va='top',fontsize=8.5,color=blue)
e.set(xlim=(.30,.425),xlabel='Mean pairwise $F_1$',ylabel='Null draws',xticks=[.30,.35,.40])
for ext in ('pdf','svg','png'):
    fig.savefig(ROOT/'figures'/f'figure6_fmri.{ext}',dpi=600,facecolor='white')
plt.close(fig)
print('Figure 6: 17 curves, 16 participant boundary trains, 1000 null scores.')
