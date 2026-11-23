#!/usr/bin/env python3
"""Recreate all v18.50d visuals from reproducible CSVs."""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
with (OUT/'controlled_intervention_responses.csv').open() as f: rows=list(csv.DictReader(f))
small=min(float(x['epsilon']) for x in rows)
orig=[v for v in rows if v['kind']=='original' and v['shape']=='beta:2:2' and abs(float(v['epsilon'])-small)<1e-12]
colors={'x_logit_kick':'C0','theta1_kick':'C1','compensated_drive_pulse':'C2'}
labels={'x_logit_kick':'x logit state kick','theta1_kick':r'$\theta_1$ state kick','compensated_drive_pulse':'compensated drive pulse'}
fig,ax=plt.subplots(figsize=(8.5,5.1))
for key in colors:
 dat=sorted([r for r in orig if r['intervention']==key],key=lambda z:float(z['ramp_xi']))
 ax.plot([float(z['ramp_xi']) for z in dat],[float(z['direction_gain']) for z in dat],marker='o',color=colors[key],label=labels[key])
ax.set(yscale='log',xlabel=r'Ramp duration $r$',ylabel=r'Finite-difference gain $\|\partial_\epsilon \hat v_h\|$',title='Controlled hidden-direction response across ramp duration')
ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(OUT/'controlled_hidden_direction_gain.png',dpi=175);plt.close(fig)
fig,ax=plt.subplots(figsize=(8.5,5.1))
for key in colors:
 dat=sorted([r for r in orig if r['intervention']==key],key=lambda z:float(z['ramp_xi']))
 ax.plot([float(z['ramp_xi']) for z in dat],[100*float(z['rate_direction_fraction']) for z in dat],marker='o',color=colors[key],label=labels[key])
ax.set(xlabel=r'Ramp duration $r$',ylabel=r'Response sensitivity in angular-rate part (%)',ylim=(0,101),title='Decomposition of the hidden-direction sensitivity')
ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(OUT/'hidden_sensitivity_coordinate_partition.png',dpi=175);plt.close(fig)
fig,ax=plt.subplots(figsize=(8.5,5.1))
for key in colors:
 dat=sorted([r for r in orig if r['intervention']==key],key=lambda z:float(z['ramp_xi']))
 dirs=[np.array(json.loads(z['response_dir_components']),float) for z in dat]
 ramps=[float(z['ramp_xi']) for z in dat]
 ang=[0.]
 for u,v in zip(dirs[:-1],dirs[1:]):
  ang.append(float(np.degrees(np.arccos(np.clip(np.dot(u,v)/(np.linalg.norm(u)*np.linalg.norm(v)),-1,1)))))
 ax.plot(ramps,ang,marker='o',color=colors[key],label=labels[key])
ax.set(xlabel=r'Ramp duration $r$',ylabel='Angle of sensitivity vector versus previous ramp (degrees)',title='Does the response direction reorganize over the scanned range?')
ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(OUT/'sensitivity_vector_direction_continuation.png',dpi=175);plt.close(fig)
fig,ax=plt.subplots(figsize=(8.5,5.1))
for kind,mark in [('original','o'),('autonomous','s')]:
 dat=[r for r in rows if r['kind']==kind and abs(float(r['ramp_xi'])-.24)<1e-10 and r['intervention']=='x_logit_kick']
 for shape,c in [('beta:2:2','C0'),('beta:3:3','C3')]:
  v=sorted((z for z in dat if z['shape']==shape),key=lambda z:float(z['epsilon']))
  ax.plot([float(z['epsilon']) for z in v],[float(z['direction_gain']) for z in v],marker=mark,color=c,label=kind+' '+shape)
ax.set(xscale='log',xlabel=r'Perturbation amplitude $|\epsilon|$',ylabel='Centered response gain',title='Local linear-response test at r=0.24')
ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(OUT/'amplitude_and_shape_sensitivity.png',dpi=175);plt.close(fig)
print('Generated 4 v18.50d figures')
