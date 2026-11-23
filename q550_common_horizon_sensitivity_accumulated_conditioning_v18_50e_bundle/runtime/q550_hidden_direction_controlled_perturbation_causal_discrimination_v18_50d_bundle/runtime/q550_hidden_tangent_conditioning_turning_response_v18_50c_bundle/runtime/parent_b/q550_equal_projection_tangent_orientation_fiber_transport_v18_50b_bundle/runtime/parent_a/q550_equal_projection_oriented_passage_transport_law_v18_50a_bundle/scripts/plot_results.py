#!/usr/bin/env python3
"""Produce event-domain figures from authentic v18.50a numerical outputs."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path(__file__).resolve().parents[1]/'results'
def rows(f):
 p=R/f
 if not p.exists():return []
 with p.open() as h:return list(csv.DictReader(h))
P=rows('oriented_equal_projection_passages.csv')
if not P:raise RuntimeError('No oriented passages to plot')
fig,axs=plt.subplots(1,2,figsize=(11,4.8))
for kind in sorted(set(z['kappa_kind'] for z in P)):
 d=[z for z in P if z['kappa_kind']==kind]; col=['signed_area_x_theta1','signed_area_x_theta2']
 for ax,field in zip(axs,col):
  a=ax.scatter([float(z['delta_xi']) for z in d],[float(z[field]) for z in d],label=kind,alpha=.9,s=42)
for ax,title in zip(axs,['Channel θ₁','Channel θ₂']):
 ax.axhline(0,ls='--',c='grey',lw=.8)
 ax.set(xlabel='Passage separation Δξ (model coordinate)',ylabel='Signed projected area [x·radians]',title=title)
 ax.grid(alpha=.2);ax.legend()
fig.suptitle('v18.50a — Oriented equal-x passages; zero is NOT imposed')
fig.tight_layout();fig.savefig(R/'oriented_passage_areas.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(8.7,5.5))
for kind in sorted(set(z['kappa_kind'] for z in P)):
 d=[z for z in P if z['kappa_kind']==kind]
 ax.scatter([float(z['triad_projector_gap']) for z in d],[float(z['area_vector_norm']) for z in d],label=kind,s=42)
ax.set(xlabel='Triad projector gap ||Pout−Pin||F',ylabel='Norm of signed projected area vector',title='Different geometric diagnostics at exactly equal x')
ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(R/'area_vs_triad_gap.png',dpi=160);plt.close(fig)
T=rows('selected_passage_trace.csv')
if T:
 fig,ax=plt.subplots(figsize=(8.7,5.7))
 for kind in sorted(set(z['kappa_kind'] for z in T)):
  d=[z for z in T if z['kappa_kind']==kind and abs(float(z['ramp_xi'])-.24)<1e-10 and z['shape']=='beta:2:2']
  if not d:continue
  ax.plot([float(z['x']) for z in d],[float(z['theta1']) for z in d],label=kind)
  ax.scatter([float(d[0]['x']),float(d[-1]['x'])],[float(d[0]['theta1']),float(d[-1]['theta1'])],s=30)
 ax.set(xlabel='x projection',ylabel='θ₁ [radians]',title='Selected oriented passage in projected (x, θ₁) plane')
 ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(R/'sample_projected_passage.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5.4))
for kind in sorted(set(z['kappa_kind'] for z in P)):
 d=[z for z in P if z['kappa_kind']==kind]
 ax.scatter([float(z['delta_xi']) for z in d],
            [float(z['signed_area_x_theta2'])/float(z['signed_area_x_theta1']) for z in d],
            label=kind,s=46,alpha=.8)
ax.set(xlabel='Passage interval Δξ (model coordinate)',ylabel='Ratio Aθ₂/Aθ₁',title='Candidate two-channel co-transport ratio — descriptive only')
ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(R/'co_transport_ratio.png',dpi=160);plt.close(fig)
print('v18.50a FIGURES_DONE')
