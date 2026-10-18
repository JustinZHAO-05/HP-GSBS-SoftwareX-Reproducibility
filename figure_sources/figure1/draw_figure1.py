"""HP-GSBS Figure 1. All numeric layers use the public Sherlock fMRI excerpt.
Rebuild: python draw_figure1.py
Inputs, provenance and full caption accompany this editable scientific figure.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy.stats import ttest_ind
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyArrowPatch,ConnectionPatch
from matplotlib.colors import Normalize,LinearSegmentedColormap
from matplotlib.cm import ScalarMappable

ROOT=Path(__file__).resolve().parent
D=np.load(ROOT/'data/Sherlock_AG_120TR.npz')
X=D['x'];T,P=X.shape;K=int(D['nstates'])
Z=(X-X.mean(1,keepdims=True))/X.std(1,ddof=1,keepdims=True)
Ap=np.vstack([np.zeros(P),(X-X.mean(1,keepdims=True)).cumsum(0)])
Bp=np.vstack([np.zeros(P),Z.cumsum(0)])
def score(a,b):
    da=Ap[b]-Ap[a];db=Bp[b]-Bp[a]
    return da@db/(T*np.sqrt(P-1)*np.linalg.norm(da))
Q=np.full((T+1,T+1),np.nan)
for a in range(T):
    for b in range(a+1,T+1):Q[a,b]=score(a,b)
R=np.corrcoef(X);M=np.triu(np.ones((T,T),bool),1)
Pi=[np.pad(v.cumsum(0).cumsum(1),((1,0),(1,0))) for v in (M,M*R,M*R**2)]
def rect(p,a,b,c,d):return p[b,d]-p[a,d]-p[b,c]+p[a,c]
edges=np.r_[0,np.flatnonzero(D['deltas']),T]
sid=np.searchsorted(edges[1:],np.arange(T),side='right')
W=R[M&(sid[:,None]==sid[None,:])]
N=R[M&((sid[None,:]-sid[:,None])==1)]
sw=np.sum([[rect(p,a,b,a,b) for p in Pi] for a,b in zip(edges[:-1],edges[1:])],axis=0)
sn=np.sum([[rect(p,a,b,b,c) for p in Pi] for a,b,c in zip(edges[:-2],edges[1:-1],edges[2:])],axis=0)
def td(w,n):
    vw=(w[2]-w[1]**2/w[0])/(w[0]-1);vn=(n[2]-n[1]**2/n[0])/(n[0]-1)
    return (w[1]/w[0]-n[1]/n[0])/np.sqrt(vw/w[0]+vn/n[0])
assert np.allclose(td(sw,sn),D['tdists'][K],rtol=1e-10,atol=1e-10)
assert np.allclose(td(sw,sn),ttest_ind(W,N,equal_var=False).statistic,rtol=1e-10)
aa,bb,ii,jj=39,85,56,74
candidates=np.arange(aa+1,bb)
gains=np.array([score(aa,i)+score(i,bb)-score(aa,bb) for i in candidates])
assert candidates[gains.argmax()]==ii
trace=json.load(open(ROOT/'data/search_trace.json'))
ex=next(t for t in trace if t['k']==5)
assert ex['single']==56 and ex['double']==[56,74]
assert any(m['deleted']==85 and m['winner']==86 for m in ex['finetune_moves'])
show=np.linspace(0,P-1,64,dtype=int)
smallshow=np.linspace(0,P-1,24,dtype=int)
vecshow=np.linspace(0,P-1,8,dtype=int)
def template(ed):
    out=np.empty_like(X)
    for a,b in zip(ed[:-1],ed[1:]):out[a:b]=X[a:b].mean(0)
    return out

CW,CH=1440,1600
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,
 'mathtext.fontset':'dejavusans','svg.fonttype':'none','pdf.fonttype':42,
 'axes.linewidth':.65,'xtick.major.width':.6,'ytick.major.width':.6,
 'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#23364b',
 'xtick.color':'#546577','ytick.color':'#546577'})
fig=plt.figure(figsize=(10,CH/144),facecolor='white')
ink='#23364b';gray='#687b8b';soft='#dbe4e9';teal='#008b82';orange='#d6812f';blue='#367ab1';purple='#8a6ab0'
statecols=['#5f95b7','#daa766','#6caa99','#9c8cb8','#d18279','#88a7bd','#b7b17d','#8aa78d','#b59bb5','#cfb39c']
cmapq=LinearSegmentedColormap.from_list('Q',['#f5f9fc','#bcd8e6','#4d91ba','#174c79'])
def ax(x,y,w,h):return fig.add_axes([x/CW,1-(y+h)/CH,w/CW,h/CH])
def tx(x,y,s,size=19,color=ink,ha='left',va='top',weight=None,**kw):
    return fig.text(x/CW,1-y/CH,s,fontsize=size/2,color=color,ha=ha,va=va,weight=weight,**kw)
def ln(x1,y1,x2,y2,color=soft,lw=.8,ls='-'):
    fig.add_artist(plt.Line2D([x1/CW,x2/CW],[1-y1/CH,1-y2/CH],transform=fig.transFigure,color=color,lw=lw,ls=ls))
def box(x,y,w,h,fc='none',ec=soft,lw=.7,ls='-'):
    r=Rectangle((x/CW,1-(y+h)/CH),w/CW,h/CH,transform=fig.transFigure,facecolor=fc,edgecolor=ec,lw=lw,ls=ls)
    fig.add_artist(r);return r
def arr(x1,y1,x2,y2,color=gray,lw=.9,style='-|>',rad=0):
    p=FancyArrowPatch((x1/CW,1-y1/CH),(x2/CW,1-y2/CH),transform=fig.transFigure,
      arrowstyle=style,mutation_scale=9,color=color,lw=lw,connectionstyle=f'arc3,rad={rad}')
    fig.add_artist(p);return p
def head(y,letter,title,tag):
    tx(28,y,letter,34,weight='bold');tx(69,y+3,title,27,weight='bold')
    tx(1400,y+10,tag,16,color=gray,ha='right')
def sub(x,y,num,s):
    tx(x,y,num,18,color=teal,weight='bold');tx(x+25,y,s,20,weight='bold')
def heat(x,y,w,h,data,extent=None,cmap='RdBu_r',vmin=-3,vmax=3,origin='lower'):
    a=ax(x,y,w,h)
    if extent is None: extent=(0,data.shape[1],0,data.shape[0])
    nx,ny=data.shape[1],data.shape[0]
    a.pcolormesh(np.linspace(extent[0],extent[1],nx+1),np.linspace(extent[2],extent[3],ny+1),data,
      shading='flat',cmap=cmap,vmin=vmin,vmax=vmax,linewidth=.06,edgecolors='face',antialiased=False,rasterized=False)
    a.set(xlim=extent[:2],ylim=extent[2:])
    if origin=='upper':a.invert_yaxis()
    a.tick_params(labelsize=8,length=2,pad=3)
    return a

# Continued below: publication layout; every heatmap and curve is data-derived.
def clean(a):a.set_xticks([]);a.set_yticks([]);a.set_frame_on(False)
def cbar(x,y,w,h,cmap,vmin,vmax,ticks,label):
    c=fig.colorbar(ScalarMappable(norm=Normalize(vmin,vmax),cmap=cmap),cax=ax(x,y,w,h),orientation='horizontal',ticks=ticks)
    if c.solids is not None: c.solids.set_rasterized(False)
    c.outline.set_visible(False);c.ax.tick_params(labelsize=7,length=2,pad=2)
    tx(x+w+13,y+h/2,label,14,va='center',color=gray)
def strip(x,y,w,h,ed,colours=None,labels=False):
    a=ax(x,y,w,h);a.set(xlim=(0,T),ylim=(0,1));a.axis('off')
    for j,(l,r) in enumerate(zip(ed[:-1],ed[1:])):
        col=(colours or statecols)[j%len(colours or statecols)]
        a.add_patch(Rectangle((l,0),r-l,1,facecolor=col,edgecolor='white',lw=.6))
        if labels:a.text((l+r)/2,.5,str(j+1),ha='center',va='center',fontsize=6,color='white')
    return a
def statepattern(x,y,w,h,ed,local=None):
    a=heat(x,y,w,h,template(ed)[:,show].T,extent=(0,T,0,len(show)))
    clean(a)
    for b in ed[1:-1]:a.axvline(b,color='white',lw=.6)
    if local:
        l,r=local;a.add_patch(Rectangle((l,0),r-l,len(show),fill=False,edgecolor=orange,lw=1.2))
    return a


exec(compile((ROOT/'layout.py').read_text(), str(ROOT/'layout.py'), 'exec'))
