#!/usr/bin/env python3
"""Regenerate the four manuscript figures from supplied data; no GSBS fits run."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib.ticker import ScalarFormatter, NullLocator

ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'data'; OUT=ROOT/'figures'; OUT.mkdir(exist_ok=True)
C={'official':'#333333','cpu-fast':'#0072B2','torch-cuda':'#D55E00','triton-cuda':'#009E73'}
L={'official':'Official GSBS','cpu-fast':'HP CPU','torch-cuda':'HP PyTorch','triton-cuda':'HP Triton'}
M={'official':'o','cpu-fast':'s','torch-cuda':'^','triton-cuda':'D'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.labelsize':8,
 'axes.titlesize':9,'legend.fontsize':7,'xtick.labelsize':7,'ytick.labelsize':7,
 'axes.linewidth':.6,'lines.linewidth':1.3,'pdf.fonttype':42,'ps.fonttype':42,
 'svg.fonttype':'none','svg.hashsalt':'hpgsbs-softwarex','savefig.facecolor':'white'})

def save(fig,stem):
 for ext in ('pdf','svg','png'):
  fig.savefig(OUT/f'{stem}.{ext}',dpi=350,bbox_inches='tight',pad_inches=.035,
   metadata={'Creator':'HP-GSBS manuscript figure scripts'} if ext=='pdf' else None)
 plt.close(fig)

def style(ax,label,title):
 ax.spines[['top','right']].set_visible(False)
 ax.tick_params(width=.6,length=3)
 ax.set_title(title,loc='left',pad=9,fontweight='medium')
 ax.text(-.14,1.055,label,transform=ax.transAxes,fontweight='bold',fontsize=10,va='bottom')

def fig2():
 a=np.load(D/'synthetic_figure_data.npz');x=a['x'];ks=np.arange(2,len(a['official__tdists']))
 fig=plt.figure(figsize=(7.2,4.9));gs=fig.add_gridspec(2,2,left=.08,right=.98,bottom=.10,top=.91,wspace=.36,hspace=.65,height_ratios=[1,1])
 ax=fig.add_subplot(gs[0,0]);v=np.max(np.abs(x));im=ax.imshow(x.T,aspect='auto',origin='lower',extent=[0,80,.5,16.5],cmap='RdBu_r',vmin=-v,vmax=v,interpolation='nearest')
 for t in a['true_boundaries']:ax.axvline(t,color='white',lw=.9,ls='--')
 ax.set(xlabel='Time (samples)',ylabel='Feature',xticks=[0,20,40,60,80],yticks=[1,8,16]);style(ax,'A','Piecewise-stationary input')
 cb=fig.colorbar(im,ax=ax,fraction=.033,pad=.023);cb.ax.tick_params(labelsize=6,length=2);cb.ax.set_title('a.u.',fontsize=6,pad=4)
 ax=fig.add_subplot(gs[0,1]);names=['Ground truth',*L.values()]
 for j,b in enumerate(['truth','official','cpu-fast','torch-cuda','triton-cuda']):
  values=(a['true_boundaries'] if b=='truth' else np.flatnonzero(a[b+'__bounds']) if b+'__bounds' in a.files else np.flatnonzero(a[b+'__all_bounds'][int(a[b+'__nstates'])]))
  ax.hlines(j,0,80,color='#DEE3E6',lw=.6)
  ax.scatter(values,np.full(len(values),j),marker='|',s=210,linewidths=1.6,color='#8C6D31' if b=='truth' else C[b])
 ax.set(xlim=(0,80),ylim=(4.5,-.7),yticks=range(5),yticklabels=names,xticks=[0,20,40,60,80],xlabel='Boundary position (samples)');ax.tick_params(axis='y',length=0)
 style(ax,'B','Shared boundaries and selected $K=4$')
 ax=fig.add_subplot(gs[1,0]);
 for b in C:
  ax.plot(ks,a[b+'__tdists'][ks],color=C[b],marker=M[b],ms=3.7,lw=1 if b!='official' else 2.8,mfc='white' if b!='official' else C[b],mew=.75,label=L[b],alpha=.9)
 ax.axvline(4,color='#888888',ls=':',lw=.7)
 ax.annotate('Selected $K=4$',(4,a['official__tdists'][4]),xytext=(5.2,300),fontsize=7.5,arrowprops=dict(arrowstyle='-',lw=.6))
 ax.set(xlabel='State-count index $K$',ylabel='Welch t-distance',xticks=[2,4,6,8,10,12,13],xlim=(1.7,13.3),ylim=(-10,375));style(ax,'C','Complete state-count curve')
 ax=fig.add_subplot(gs[1,1]);
 for b in list(C)[1:]:
  err=np.abs(a[b+'__tdists'][ks]-a['official__tdists'][ks])*1e11
  ax.plot(ks,err,color=C[b],marker=M[b],ms=3.6,mfc='white',mew=.8,lw=1,label=L[b])
 ax.set(xlabel='State-count index $K$',ylabel='Absolute TD difference',xticks=[2,4,6,8,10,12,13],xlim=(1.7,13.3),ylim=(-.06,1.7));style(ax,'D','Floating-point differences'); ax.text(.99,.99,r'$\times 10^{-11}$',transform=ax.transAxes,ha='right',va='top',fontsize=7)
 handles=[Line2D([0],[0],color=C[b],marker=M[b],mfc='white' if b!='official' else C[b],ms=4,label=L[b]) for b in C]
 fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.53,1.008),ncol=4,frameon=False,columnspacing=1.6)
 save(fig,'figure2_consistency')


if __name__ == '__main__':
 fig2()
