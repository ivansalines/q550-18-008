#!/usr/bin/env python3
"""Reproducible figures of authentic v18.49w data, no interpolated physical claims."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'results'
def rows(n):
 with (O/n).open() as f:return list(csv.DictReader(f))
def take(filename,kind='original',r=.24):
 return [x for x in rows(filename) if x['kappa_kind']==kind and abs(float(x['ramp_xi'])-r)<1e-10]
def f(v,k):return float(v[k])
D=take('sampled_states_11d_projection.csv')
fig,ax=plt.subplots(figsize=(8.6,5));
ax.plot([f(z,'sigma') for z in D],[f(z,'x') for z in D],label='local x (logistic)')
ax.axvline(.5,ls='--',color='gray',label='drive zero')
ax.set(xlabel='Normalized in-ramp time σ',ylabel='Local reduced coordinate x',title='Q550 v18.49w — x can revisit a value during the ramp')
ax.legend();fig.tight_layout();fig.savefig(O/'x_revisit_during_ramp.png',dpi=155);plt.close(fig)
P=take('all_separated_pairs.csv')
x=np.array([f(z,'x_abs_gap') for z in P]);theta=np.array([f(z,'posture_theta_pair_gap_rad') for z in P]);rad=np.array([f(z,'locus_xyz_scaled_gap') for z in P])
fig,ax=plt.subplots(figsize=(8.6,5.2))
sc=ax.scatter(np.maximum(x,1e-12),theta,c=rad,s=12,alpha=.75)
ax.set_xscale('log');ax.set(xlabel='Absolute difference in x (log scale)',ylabel='Angular-posture difference (rad)',title='Near-equal x need not imply equal posture or equal 3D locus')
fig.colorbar(sc,ax=ax,label='Normalized 3D locus gap')
fig.tight_layout();fig.savefig(O/'near_x_unequal_posture_scatter.png',dpi=155);plt.close(fig)
Q=take('equal_clock_phase_mirror_pairs.csv',r=.327375)
fig,ax=plt.subplots(figsize=(8.6,5))
ax.plot([f(z,'sigma_a') for z in Q],[f(z,'posture_theta_pair_gap_rad') for z in Q],label='Posture angle difference (rad)')
ax.plot([f(z,'sigma_a') for z in Q if z['triad_projector_frobenius_gap']],[f(z,'triad_projector_frobenius_gap') for z in Q if z['triad_projector_frobenius_gap']],label='Triad projector Frobenius difference')
ax.set(xlabel='Earlier mirror point σ (later = 1 − σ)',ylabel='Difference in declared coordinates / projector norm',title='Same imposed drive phase does not close full dynamic state')
ax.legend();fig.tight_layout();fig.savefig(O/'equal_drive_phase_unequal_state.png',dpi=155);plt.close(fig)
C=rows('case_summary.csv')
fig,ax=plt.subplots(figsize=(8.6,5))
for kind in ['original','autonomous']:
 z=sorted([d for d in C if d['kappa_kind']==kind],key=lambda d:f(d,'ramp_xi'))
 ax.plot([f(d,'ramp_xi') for d in z],[f(d,'closest_3d_locus_locus_xyz_scaled_gap') for d in z],marker='o',label=kind)
ax.axhline(.2,ls='--',color='gray',label='Declared near-3D threshold')
ax.set(xlabel='Ramp duration r',ylabel='Smallest scaled 3D locus gap, Δσ ≥ 0.2',title='No near-3D locus return within the finite search')
ax.legend();fig.tight_layout();fig.savefig(O/'strict_locus_minimum_by_ramp.png',dpi=155);plt.close(fig)
