"""Layout executed by draw_figure1.py after its data and graphics helpers."""
def label(x,y,s,color=ink,size=20): tx(x,y,s,size,color=color,weight='bold')
def chip(x,y,w,h,s,col=teal):
    box(x,y,w,h,fc='white',ec=col,lw=.85)
    tx(x+w/2,y+h/2,s,18,color=col,ha='center',va='center')
def hardware(x,y,col):
    box(x,y,28,25,ec=col,lw=.85)
    box(x+7,y+6,14,13,fc=col,ec='none')
    for p in [5,12,19]:
        ln(x-4,y+p,x,y+p,color=col,lw=.7);ln(x+28,y+p,x+32,y+p,color=col,lw=.7)
    for p in [6,14,22]:
        ln(x+p,y-4,x+p,y,color=col,lw=.7);ln(x+p,y+25,x+p,y+29,color=col,lw=.7)

# A — activity, state templates, and selection of state count.
head(24,'A','Neural state segmentation','GSBS')
label(70,83,'Multivoxel activity')
a=heat(70,120,380,151,X[:,show].T,extent=(0,T,0,len(show)))
a.set(xticks=[0,60,120],yticks=[])
a.set_ylabel('Voxels',fontsize=9)
for b in edges[1:-1]:a.axvline(b,color='white',lw=.55,alpha=.7)
a.add_patch(Rectangle((aa,0),bb-aa,64,fill=False,edgecolor=orange,lw=1.35))
strip(70,303,380,20,edges)
tx(260,337,'Time',17,ha='center')
cbar(70,378,90,6,'RdBu_r',-3,3,[-3,0,3],'BOLD')
tx(450,337,'States',16,color=gray,ha='right')

label(600,83,'State templates')
statepattern(600,120,353,110,[0,39,56,85,111,120],(39,85))
# A real parent-interval mean pattern, connected to the highlighted input block.
v=X[aa:bb,show].mean(0)
a=heat(512,137,24,117,v[:,None]);clean(a)
arr(466,160,503,188,color=orange,lw=.8)
arr(466,236,503,188,color=orange,lw=.8)
tx(524,274,'Mean',16,ha='center',color=gray)
arr(548,187,584,187,color=orange)

a=ax(600,284,353,70)
a.plot(candidates,gains,color=blue,lw=1.5)
a.fill_between(candidates,gains.min(),gains,color=blue,alpha=.07)
a.scatter(ii,gains[candidates==ii],color=orange,s=24,zorder=5)
a.axvline(ii,color=orange,ls=':',lw=.85)
a.set(xlim=(aa,bb),ylim=(0,.103),xticks=[aa,ii,bb],xticklabels=['a','i','b'],yticks=[])
a.tick_params(labelsize=8,length=2)
a.set_ylabel('Score gain',fontsize=8.5,labelpad=6)
tx(600,257,'Boundary search',17,color=gray)
tx(777,383,'Candidate boundary',17,ha='center')
arr(976,186,1038,186)

label(1085,83,'State count')
a=ax(1085,126,285,225)
kk=np.arange(2,31)
a.plot(kk,D['tdists'][kk],color=ink,lw=1.6)
a.scatter(K,D['tdists'][K],color=teal,s=32,zorder=5)
a.axvline(K,color=teal,ls=':',lw=.8)
a.annotate(r'$K^*$',xy=(K,D['tdists'][K]),xytext=(K+3,D['tdists'][K]+3),fontsize=11,color=teal)
a.set(xticks=[2,15,30],yticks=[0,60],ylim=(0,80))
a.tick_params(labelsize=8,length=2);a.set_ylabel('t-distance',fontsize=9)
tx(1228,383,'Number of states, K',17,ha='center')
ln(28,427,1410,427)

# B — original reconstruction is a comparison, not a step of HP-GSBS.
head(451,'B','Interval score reuse','HP-GSBS · FULL-Q')
box(52,513,266,235,fc='#f6f8fa',ec='none').set_zorder(-1)
label(70,522,'Original GSBS',color=gray,size=19)
for yy,cut in [(562,48),(619,56),(676,74)]:
    a=statepattern(70,yy,215,35,[0,39,cut,85,111,120])
    a.axvspan(0,39,color='white',alpha=.62);a.axvspan(85,120,color='white',alpha=.62)
    a.axvline(cut,color=orange,lw=1.1)
arr(292,582,292,694,color=gray,rad=-.65,lw=.7)
tx(70,723,'Rebuild for each candidate',15,color=gray)
ln(339,522,339,741,color=soft)

label(383,522,'Temporal prefixes')
for yy,mat,lab in [(569,Ap,'A'),(662,Bp,'B')]:
    z=mat[:,smallshow].T;lim=np.quantile(np.abs(z),.99)
    a=heat(398,yy,230,49,z,extent=(0,T+1,0,len(smallshow)),vmin=-lim,vmax=lim);clean(a)
    for end,col in [(aa,gray),(bb,teal)]:a.axvline(end,color=col,lw=1.2)
    tx(381,yy+24,lab,18,ha='right',va='center',weight='bold')
    for end,lab,col in [(aa,'a',gray),(bb,'b',teal)]:tx(398+230*end/121,yy+55,lab,15,ha='center',color=col)

label(702,522,'Interval vectors')
vals=[Ap[bb,vecshow],Ap[aa,vecshow],Ap[bb,vecshow]-Ap[aa,vecshow]]
lim=max(np.max(np.abs(v)) for v in vals)
for xx,v,lab in zip([708,785,862],vals,[r'$A_b$',r'$A_a$',r'$\Delta A$']):
    a=heat(xx,574,29,126,v[:,None],vmin=-lim,vmax=lim);clean(a)
    for row in range(1,8):a.axhline(row,color='white',lw=.6)
    tx(xx+14.5,714,lab,18,ha='center')
tx(760,630,'−',25,ha='center');tx(837,630,'=',25,ha='center')
arr(648,633,687,633,color=teal)
arr(922,633,982,633,color=teal)

label(1031,522,'Interval table Q')
qax=heat(1031,562,296,177,Q,extent=(0,T+1,0,T+1),cmap=cmapq,vmin=0,vmax=np.nanmax(Q),origin='upper')
qax.set(xticks=[ii,jj,bb],xticklabels=['i','j','b'],yticks=[aa,ii],yticklabels=['a','i'])
qax.tick_params(labelsize=8,length=2)
qax.set_xlabel('End',fontsize=8,labelpad=1);qax.set_ylabel('Start',fontsize=8,labelpad=1)
entries=[(aa,bb,ink),(aa,ii,teal),(ii,bb,orange),(ii,jj,blue),(jj,bb,purple)]
for ra,cb,col in entries:qax.scatter(cb+.5,ra+.5,s=25,facecolor='white',edgecolor=col,lw=1.15,zorder=6)

# One visible lookup: table entry -> score tile. Other tiles share interval colours.
fig.add_artist(ConnectionPatch(xyA=(ii+.5,aa+.5),coordsA=qax.transData,
    xyB=(1070/CW,1-799/CH),coordsB=fig.transFigure,
    arrowstyle='-|>',mutation_scale=8,color=teal,lw=.8,
    connectionstyle='angle,angleA=0,angleB=90,rad=5'))
chip(1030,800,80,29,r'$F(a,i)$',teal)
tx(1140,808,'Lookup & reuse',16,color=teal)
ln(1030,814,723,814,color=teal,lw=.65)
arr(723,814,723,838,color=teal,lw=.65)

# Candidate timelines and symbolic sums; no numerical worked results.
def intervalbar(x,y,ed,cols):
    width=424
    for l,r,c in zip(ed[:-1],ed[1:],cols):
        box(x+width*(l-aa)/(bb-aa),y,width*(r-l)/(bb-aa),22,fc=c,ec='white',lw=.6)
    for end,lab in zip(ed,['a','i','b'] if len(ed)==3 else ['a','i','j','b']):
        tx(x+width*(end-aa)/(bb-aa),y+27,lab,15,ha='center',color=gray)
def sumtiles(y,cols):
    x=701
    for k,c in enumerate(cols):
        box(x,y,43,22,fc=c,ec='none');x+=43
        tx(x+12,y+11,'+',21,ha='center',va='center',color=gray) if k<len(cols)-1 else None
        x+=27 if k<len(cols)-1 else 0
    tx(x+16,y+11,'−',22,ha='center',va='center',color=gray)
    box(x+34,y,60,22,fc='none',ec=ink,lw=1)
    tx(x+64,y+11,'parent',12,ha='center',va='center',color=ink)
label(70,781,'Candidate splits',size=19)
tx(701,781,'Score gain',17,color=gray)
tx(70,851,'Single',17,color=gray,va='center');intervalbar(210,840,[aa,ii,bb],[teal,orange]);sumtiles(840,[teal,orange])
tx(70,917,'Double',17,color=gray,va='center');intervalbar(210,906,[aa,ii,jj,bb],[teal,blue,purple]);sumtiles(906,[teal,blue,purple])
for start,yy in [(908,851),(978,917)]:
    ln(start,yy,997,yy,color=gray,lw=.8)
    arr(997,yy,1048,yy,color=gray,lw=.8)
ln(1048,851,1048,917,color=gray,lw=.8)
arr(1048,884,1076,884,color=gray,lw=.8)
chip(1085,868,127,32,'Select by TD',teal)
arr(1220,884,1250,884,color=teal)
tx(1303,919,'Refine',17,ha='center',color=gray)
ln(1256,884,1350,884,color=gray,lw=.7)
ln(1291,871,1291,899,color=orange,lw=1,ls=':')
ln(1310,871,1310,899,color=teal,lw=1.3)
arr(1285,861,1318,861,color=teal,lw=.8,style='<->')
ln(28,973,1410,973)

# C — full symmetric R for context; statistics still use the original pair mask.
head(997,'C','Prefix-based t-distance','HP-GSBS · PREFIX2D')
label(70,1060,'Pattern correlations')
a=heat(70,1102,320,278,R,extent=(0,T,0,T),vmin=-1,vmax=1,origin='upper')
a.set(xticks=[0,60,120],yticks=[0,60,120]);a.set_ylabel('Time',fontsize=9);a.set_xlabel('Time',fontsize=9,labelpad=1)
# Slightly inset both classes of outline so shared edges remain separately visible.
outline_inset=.9
for l,r in zip(edges[:-1],edges[1:]):
    a.add_patch(Rectangle((l+outline_inset,l+outline_inset),r-l-2*outline_inset,r-l-2*outline_inset,fill=False,edgecolor=teal,lw=1.4))
for l,r,c in zip(edges[:-2],edges[1:-1],edges[2:]):
    a.add_patch(Rectangle((r+outline_inset,l+outline_inset),c-r-2*outline_inset,r-l-2*outline_inset,fill=False,edgecolor=orange,lw=1.4))
qa,qb,qc,qd=39,56,56,64
cbar(70,1435,80,6,'RdBu_r',-1,1,[-1,0,1],'r')
tx(232,1431,'Within',16,color=teal);tx(315,1431,'Adjacent',16,color=orange)
box(244,1454,30,12,ec=teal,lw=1.6)
box(335,1454,30,12,ec=orange,lw=1.6)
arr(412,1192,455,1192,color=teal)

label(479,1060,'2D prefix statistics')
prefix_axes=[]
for xx,table,lab in zip([479,614,749],Pi,['Count','Sum r','Sum r²']):
    a=heat(xx,1102,108,94,table,extent=(0,T+1,0,T+1),cmap=cmapq,vmin=table.min(),vmax=table.max(),origin='upper');clean(a);prefix_axes.append(a)
    tx(xx+54,1206,lab,17,ha='center',bbox={'facecolor':'white','edgecolor':'none','pad':1.5})
query_color='#ffd34f'
prefix_axes[1].add_patch(Rectangle((qc,qa),qd-qc,qb-qa,fill=False,edgecolor=query_color,lw=1.8,zorder=6))

# True local prefix field with signed inclusion–exclusion at its four corners.
qax=heat(479,1276,180,139,Pi[1][30:66,45:75],extent=(45,75,30,66),cmap=cmapq,
         vmin=Pi[1][30:66,45:75].min(),vmax=Pi[1][30:66,45:75].max(),origin='upper');clean(qax)
qax.add_patch(Rectangle((qc,qa),qd-qc,qb-qa,fill=False,edgecolor=query_color,lw=1.8))
for rr,cc,sign in [(qa,qc,'+'),(qa,qd,'−'),(qb,qc,'−'),(qb,qd,'+')]:
    qax.scatter(cc,rr,color='white',edgecolor=query_color,s=38,lw=1.3,zorder=5)
    qax.text(cc+(-3 if cc==qc else 3),rr,sign,color=ink,ha='center',va='center',fontsize=12,weight='bold')
for p1,p2 in [((qc,qa),(479,1276)),((qd,qb),(659,1276))]:
    fig.add_artist(ConnectionPatch(xyA=p1,coordsA=prefix_axes[1].transData,xyB=(p2[0]/CW,1-p2[1]/CH),coordsB=fig.transFigure,color=gray,lw=.55,alpha=.65))
tx(569,1433,'Four-corner query',17,ha='center',color=teal)
arr(677,1344,714,1344,color=teal)
for yy,lab in [(1278,'n'),(1329,r'$\sum r$'),(1380,r'$\sum r^2$')]:
    chip(732,yy,71,31,lab,teal)
    arr(815,yy+15,881,1344,color=teal,lw=.65)
tx(875,1374,'Aggregate',16,ha='center',color=gray)
arr(888,1344,976,1344,color=teal)

label(1030,1060,'Within vs adjacent')
a=ax(1030,1124,340,181)
bins=np.linspace(-1,1,33)
a.hist(N,bins=bins,weights=np.ones(len(N))/len(N),color=orange,alpha=.65,histtype='stepfilled',linewidth=.8,edgecolor=orange)
a.hist(W,bins=bins,weights=np.ones(len(W))/len(W),color=teal,alpha=.5,histtype='stepfilled',linewidth=.8,edgecolor=teal)
a.axvline(N.mean(),color=orange,lw=.8,ls=':');a.axvline(W.mean(),color=teal,lw=.8,ls=':')
a.set(xlim=(-1,1),xticks=[-1,0,1],yticks=[]);a.tick_params(labelsize=8,length=2)
a.set_ylabel('Fraction',fontsize=8.5);a.set_xlabel('Pattern correlation',fontsize=8.5,labelpad=1)
tx(1064,1094,'Adjacent',16,color=orange);tx(1298,1094,'Within',16,color=teal)
chip(1040,1383,185,39,'t-distance',teal)
arr(1201,1351,1156,1375,color=gray,lw=.75)
arr(986,1344,1031,1399,color=teal,lw=.8)

# Shared architecture: three interchangeable backends, one common controller.
ln(28,1478,1410,1478)
for xx,lab in [(55,'CPU'),(249,'PyTorch CUDA'),(443,'Triton')]:
    box(xx,1503,174,48,fc='none',ec=soft,lw=.85)
    hardware(xx+14,1515,teal)
    tx(xx+53,1527,lab,16,va='center',color=teal)
    ln(xx+87,1551,xx+87,1566,color=gray,lw=.7)
ln(142,1566,654,1566,color=gray,lw=.7)
ln(654,1566,654,1527,color=gray,lw=.7)
arr(654,1527,695,1527,color=teal)
box(707,1506,302,43,fc='#f0f7f6',ec='none')
tx(858,1527,'Shared search + refinement',17,ha='center',va='center')
arr(1027,1527,1071,1527,color=teal)
tx(1091,1514,'States',16,color=gray,va='center')
strip(1178,1507,190,14,edges)
tx(1091,1546,'TD(K)',16,color=gray,va='center')
a=ax(1178,1534,190,30)
a.plot(kk,D['tdists'][kk],color=teal,lw=1)
a.set(xlim=(0,30),ylim=(0,80),xticks=[],yticks=[])
a.set_xlabel('K',fontsize=7.5,labelpad=2)
for side in ['left','bottom']: a.spines[side].set_color(gray);a.spines[side].set_linewidth(.6)

for ext in ['svg','pdf','png']:
    fig.savefig(ROOT/f'Figure1_HP_GSBS.{ext}',dpi=300,facecolor='white')
plt.close(fig)
query=[float(rect(p,qa,qb,qc,qd)) for p in Pi]
assert np.allclose(R,R.T,rtol=0,atol=1e-14)
print('Rendered SVG / PDF / PNG; full correlation matrix; existing TD parity passed.')
