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

ROOT=Path(__file__).resolve().parent
D=ROOT/'data'; OUT=ROOT; OUT.mkdir(exist_ok=True)
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

def fig3():
 r=pd.read_csv(D/'paired_per_input.csv');summ=pd.read_csv(D/'paired_runtime.csv');sp=pd.read_csv(D/'paired_speedup.csv')
 fig=plt.figure(figsize=(7.2,4.9));gs=fig.add_gridspec(2,3,left=.09,right=.985,bottom=.095,top=.88,wspace=.36,hspace=.51,height_ratios=[1.15,1])
 settings=[(['T1','T2','T3'],'T','Time samples $T$',r'$P=32,\ K_{max}=20$'),(['P1','T2','P2'],'P','Features $P$',r'$T=512,\ K_{max}=20$'),(['K1','T2','K2'],'Kmax','Maximum state count $K_{max}$',r'$T=512,\ P=32$')]
 for j,(conds,key,xlab,title) in enumerate(settings):
  ax=fig.add_subplot(gs[0,j]);bx=fig.add_subplot(gs[1,j])
  for b in C:
   sr=summ[(summ.condition.isin(conds))&(summ.backend==b)].set_index('condition').loc[conds]
   xx=sr[key].to_numpy();yy=sr.median_s.to_numpy()
   ax.errorbar(xx,yy,yerr=[yy-sr.min_s,sr.max_s-yy],color=C[b],marker=M[b],ms=3.8,lw=1.15,capsize=2,capthick=.7,mew=.7,mfc='white')
   for seed in sorted(r.seed.unique()):
    t=r[(r.condition.isin(conds))&(r.backend==b)&(r.seed==seed)].set_index('condition').loc[conds]
    ax.scatter(xx,t.median_s,s=8,color=C[b],alpha=.6,zorder=4)
   if b!='official':
    s=sp[(sp.condition.isin(conds))&(sp.backend==b)].set_index('condition').loc[conds]
    y=s['median'].to_numpy();bx.errorbar(xx,y,yerr=[y-s['min'],s['max']-y],color=C[b],marker=M[b],ms=3.8,lw=1.15,capsize=2,capthick=.7,mew=.7,mfc='white')
  ax.set_yscale('log');ax.set_ylim(.04,350);ax.set_yticks([.1,1,10,100]);ax.yaxis.set_major_formatter(ScalarFormatter());ax.yaxis.set_minor_locator(NullLocator())
  ax.set_xticks(xx);ax.set_xlabel(xlab);ax.grid(axis='y',which='major',color='#E8EAEC',lw=.5)
  bx.set_xticks(xx);bx.set_xlabel(xlab);bx.set_ylim(0,2100);bx.set_yticks([0,500,1000,1500,2000]);bx.grid(axis='y',color='#E8EAEC',lw=.5)
  if j==0:ax.set_ylabel('Complete-fit time (s, log scale)');bx.set_ylabel('Same-input speedup (×)')
  style(ax,chr(65+j),title);style(bx,chr(68+j),'Paired speedup' if j==0 else '')
  if j==1:
   centre=summ[summ.condition=='T2'].set_index('backend')
   ax.text(.20,.655,r'$P=32$ · complete-fit time',transform=ax.transAxes,fontsize=7.0,color='#444444')
   for row,b in enumerate(C):
    yy=.565-row*.079
    name={'official':'Official','cpu-fast':'HP CPU','torch-cuda':'PyTorch','triton-cuda':'Triton'}[b]
    value=centre.loc[b,'median_s']
    label=f'{value:.1f} s' if b=='official' else f'{value:.3f} s'
    ax.text(.20,yy,name,transform=ax.transAxes,fontsize=7.3,color=C[b],va='center')
    ax.text(.90,yy,label,transform=ax.transAxes,fontsize=7.3,color='#333333',ha='right',va='center')
  if j==0:
   peak=sp[(sp.condition=='T3')&(sp.backend=='torch-cuda')]['median'].iloc[0]
   bx.annotate(f'≈{peak:,.0f}×',xy=(768,peak),xytext=(.25,.84),textcoords='axes fraction',
    fontsize=10,fontweight='medium',color=C['torch-cuda'],ha='left',va='center',
    arrowprops=dict(arrowstyle='-',color=C['torch-cuda'],lw=.7,shrinkA=4,shrinkB=6,
     connectionstyle='angle,angleA=0,angleB=90,rad=3'))
 handles=[Line2D([0],[0],color=C[b],marker=M[b],mfc='white',ms=4,label=L[b]) for b in C]
 fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.53,1.005),ncol=4,frameon=False,columnspacing=1.5)
 save(fig,'Figure3_HP_GSBS')


if __name__=='__main__':
 fig3()
