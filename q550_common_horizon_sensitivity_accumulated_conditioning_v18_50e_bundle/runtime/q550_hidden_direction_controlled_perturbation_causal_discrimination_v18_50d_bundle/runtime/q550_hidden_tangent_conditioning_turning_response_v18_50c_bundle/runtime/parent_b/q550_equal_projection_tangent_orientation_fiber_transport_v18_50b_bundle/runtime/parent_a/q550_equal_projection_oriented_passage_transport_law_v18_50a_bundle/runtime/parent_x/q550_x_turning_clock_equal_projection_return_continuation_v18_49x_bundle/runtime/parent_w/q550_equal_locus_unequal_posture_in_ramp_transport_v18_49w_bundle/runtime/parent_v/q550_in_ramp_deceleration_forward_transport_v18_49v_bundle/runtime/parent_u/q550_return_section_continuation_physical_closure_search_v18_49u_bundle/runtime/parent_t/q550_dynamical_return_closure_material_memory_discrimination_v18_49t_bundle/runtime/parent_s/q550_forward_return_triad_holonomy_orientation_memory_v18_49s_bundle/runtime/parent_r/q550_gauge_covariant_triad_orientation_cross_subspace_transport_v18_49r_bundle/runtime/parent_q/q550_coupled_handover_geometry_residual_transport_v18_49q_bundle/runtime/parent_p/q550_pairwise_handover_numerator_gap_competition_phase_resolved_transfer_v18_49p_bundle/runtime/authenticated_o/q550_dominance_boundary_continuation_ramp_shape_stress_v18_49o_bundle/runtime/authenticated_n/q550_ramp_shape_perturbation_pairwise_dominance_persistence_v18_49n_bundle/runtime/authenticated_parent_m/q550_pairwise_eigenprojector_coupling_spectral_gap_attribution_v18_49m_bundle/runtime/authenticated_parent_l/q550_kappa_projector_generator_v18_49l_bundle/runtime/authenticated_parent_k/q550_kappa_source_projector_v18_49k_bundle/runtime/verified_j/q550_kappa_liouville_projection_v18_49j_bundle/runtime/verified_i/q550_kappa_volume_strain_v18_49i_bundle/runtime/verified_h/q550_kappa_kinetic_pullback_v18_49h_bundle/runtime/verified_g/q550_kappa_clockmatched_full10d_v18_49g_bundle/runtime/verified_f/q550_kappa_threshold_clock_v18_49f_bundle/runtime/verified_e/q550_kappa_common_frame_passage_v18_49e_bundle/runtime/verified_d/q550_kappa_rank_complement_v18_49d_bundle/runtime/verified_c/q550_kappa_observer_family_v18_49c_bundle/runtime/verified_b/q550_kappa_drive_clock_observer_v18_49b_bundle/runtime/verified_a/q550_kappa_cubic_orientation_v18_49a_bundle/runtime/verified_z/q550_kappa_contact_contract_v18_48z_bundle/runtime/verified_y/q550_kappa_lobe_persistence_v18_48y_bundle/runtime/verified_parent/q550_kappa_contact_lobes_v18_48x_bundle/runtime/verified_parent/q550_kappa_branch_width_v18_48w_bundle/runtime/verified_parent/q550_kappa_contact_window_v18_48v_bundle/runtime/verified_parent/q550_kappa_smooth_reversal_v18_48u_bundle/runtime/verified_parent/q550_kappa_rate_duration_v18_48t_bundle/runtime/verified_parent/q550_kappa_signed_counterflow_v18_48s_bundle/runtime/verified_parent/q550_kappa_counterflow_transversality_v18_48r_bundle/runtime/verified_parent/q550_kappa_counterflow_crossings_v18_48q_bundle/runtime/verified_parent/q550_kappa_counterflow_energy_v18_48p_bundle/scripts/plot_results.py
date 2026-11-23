#!/usr/bin/env python3
"""Render figures using numerical source CSV, not schematic trajectories."""
import csv,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path(__file__).resolve().parents[1]
D=R/'results'
def read(filename):
    with (D/filename).open(newline='') as f:return list(csv.DictReader(f))
T=read('trajectory_samples.csv');B=read('energy_balance.csv');S=read('protocol_summary.csv')
colors={'mathematical_inverse':'#6C7E90','reverse_drive':'#C45F66',
        'reverse_drive_velocity_flip':'#348E8D','forward_drive_continuation':'#A17EB5'}
labels={'mathematical_inverse':'Same ODE backward in time',
        'reverse_drive':'Reverse Theta drive',
        'reverse_drive_velocity_flip':'Reverse Theta + velocity flip',
        'forward_drive_continuation':'Forward Theta control'}
for family in ('phaseblind','phasecov'):
    rows=[r for r in T if str(r['family']).startswith(family) and r['branch']=='0' and r['kappa_kind']=='original']
    fig,(a,b,c)=plt.subplots(3,1,figsize=(10,10),sharex=True,constrained_layout=True)
    for mode in colors:
        ps=sorted((r for r in rows if r['protocol']==mode),key=lambda r:float(r['return_fraction']))
        xx=np.array([float(r['return_fraction']) for r in ps])
        a.plot(xx,[float(r['physical_shape_distance']) for r in ps],color=colors[mode],label=labels[mode],lw=2)
        b.plot(xx,[float(r['x']) for r in ps],color=colors[mode],lw=1.7)
        c.plot(xx,[float(r['energy'])-float(ps[0]['energy']) for r in ps],color=colors[mode],lw=1.7)
    ref=sorted((r for r in rows if r['protocol']=='mathematical_inverse'),key=lambda r:float(r['return_fraction']))
    b.plot([float(r['return_fraction']) for r in ref],[float(r['x']) for r in ref],'--',color='#333333',alpha=.7,label='Reverse reference path x')
    a.set_ylabel('Shape separation (log rho1, log rho2, x)')
    b.set_ylabel('State x = logistic(z)')
    c.set_ylabel('E(t) - E(0) (defined mechanical E)')
    c.set_xlabel('Return protocol progress (xi units)')
    a.set_title(f'Q550 v18.48p | {family} branch 0 | original kappa | genuine counter-drive IVPs')
    a.legend(loc='best',fontsize=8); b.legend(loc='best',fontsize=8)
    for ax in (a,b,c):ax.grid(alpha=.2)
    fig.savefig(D/f'{family}_branch0_counterflow.png',dpi=175);plt.close(fig)
fig,axs=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
for ax,case in zip(axs.flat,['reverse_drive','reverse_drive_velocity_flip','forward_drive_continuation','mathematical_inverse']):
    rows=[r for r in B if r['protocol']==case]
    keys=['drive_work','radial_dissipation','x_dissipation','nonconservative_x_work']
    names=['Drive work','Radial loss','x loss','Active x work']
    vals=np.array([[float(r[k]) for k in keys] for r in rows])
    av=np.median(vals,axis=0)
    ax.barh(np.arange(4),av,color=['#9165AC','#AD645E','#708BB8','#488F89'])
    ax.set_yticks(np.arange(4),names);ax.axvline(0,color='black',lw=.8)
    ax.set_title(labels[case]+' (medians of 8 runs)')
    ax.set_xlabel('Signed integral per xi traversal')
    ax.grid(axis='x',alpha=.15)
fig.savefig(D/'protocol_mechanical_power_components.png',dpi=175);plt.close(fig)
print('Rendered 3 original-data figures')
