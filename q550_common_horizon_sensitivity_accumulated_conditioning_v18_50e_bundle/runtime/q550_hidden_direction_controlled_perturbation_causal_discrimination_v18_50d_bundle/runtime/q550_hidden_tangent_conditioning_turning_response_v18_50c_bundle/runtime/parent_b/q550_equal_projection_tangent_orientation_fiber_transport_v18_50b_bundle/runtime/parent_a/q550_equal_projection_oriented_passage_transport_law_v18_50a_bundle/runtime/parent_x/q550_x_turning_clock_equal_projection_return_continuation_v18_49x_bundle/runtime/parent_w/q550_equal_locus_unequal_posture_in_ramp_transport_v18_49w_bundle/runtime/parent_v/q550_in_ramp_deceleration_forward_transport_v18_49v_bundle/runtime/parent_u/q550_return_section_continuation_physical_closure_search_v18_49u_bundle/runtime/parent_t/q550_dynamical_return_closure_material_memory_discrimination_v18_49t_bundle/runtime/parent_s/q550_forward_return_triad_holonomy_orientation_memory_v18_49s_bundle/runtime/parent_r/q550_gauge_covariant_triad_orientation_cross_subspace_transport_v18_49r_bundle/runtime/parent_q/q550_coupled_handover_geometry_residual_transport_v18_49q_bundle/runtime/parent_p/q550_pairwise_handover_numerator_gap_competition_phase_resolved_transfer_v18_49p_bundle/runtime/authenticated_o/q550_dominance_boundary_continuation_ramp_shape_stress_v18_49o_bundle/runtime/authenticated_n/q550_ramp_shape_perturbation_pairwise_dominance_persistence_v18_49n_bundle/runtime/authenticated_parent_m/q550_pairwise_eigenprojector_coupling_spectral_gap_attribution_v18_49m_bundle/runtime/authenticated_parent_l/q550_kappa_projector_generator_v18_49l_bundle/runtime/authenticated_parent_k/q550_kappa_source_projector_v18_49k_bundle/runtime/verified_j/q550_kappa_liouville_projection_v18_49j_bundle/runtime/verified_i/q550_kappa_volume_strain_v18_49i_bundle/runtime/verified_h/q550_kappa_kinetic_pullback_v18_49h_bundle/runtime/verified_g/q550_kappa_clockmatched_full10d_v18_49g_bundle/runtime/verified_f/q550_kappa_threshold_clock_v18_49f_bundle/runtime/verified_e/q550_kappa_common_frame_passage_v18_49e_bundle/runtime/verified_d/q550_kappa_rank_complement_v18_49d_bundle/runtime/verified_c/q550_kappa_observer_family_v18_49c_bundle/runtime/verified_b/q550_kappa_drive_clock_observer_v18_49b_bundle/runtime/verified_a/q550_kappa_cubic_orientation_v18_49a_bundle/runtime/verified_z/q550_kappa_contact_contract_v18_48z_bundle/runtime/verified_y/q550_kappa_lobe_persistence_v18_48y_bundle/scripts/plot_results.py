#!/usr/bin/env python3
"""Regenerate all figures strictly from actual numerical CSV output."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'results'
def rows(name):
    with (out/name).open() as f:return list(csv.DictReader(f))
B=rows('barrier_height_curvature.csv'); C=rows('critical_threshold_curve.csv');P=rows('threshold_persistence_components.csv')
fig,ax=plt.subplots(figsize=(9.4,6.1))
for k,mark in [('original','o'),('autonomous','s')]:
    vals=sorted((r for r in C if r['kappa_kind']==k),key=lambda r:float(r['threshold']))
    q=np.array([float(r['threshold']) for r in vals]);t=np.array([float(r['secant_interpolated_ramp']) for r in vals])
    ax.plot(t,q,marker=mark,label=f'kappa0 {k} (secant interpolation)')
    for r in vals:
        y=float(r['threshold'])
        ax.plot([float(r['left_ramp']),float(r['right_ramp'])],[y,y],linewidth=3,alpha=.32)
ax.set(xlabel='Ramp duration r (xi)',ylabel='Critical shape-distance threshold',
       title='Q550 v18.48y | Lobe-merger threshold curve (genuine IVP brackets)')
ax.grid(alpha=.25);ax.legend(fontsize=9);fig.tight_layout();fig.savefig(out/'lobe_threshold_critical_curve.png',dpi=180);plt.close(fig)
fig,(a,b)=plt.subplots(2,1,figsize=(9.3,8),sharex=True)
for k in ('original','autonomous'):
    vals=sorted((r for r in B if r['kappa_kind']==k),key=lambda r:float(r['ramp_duration_xi']))
    t=np.array([float(z['ramp_duration_xi']) for z in vals]);
    a.plot(t,[float(z['barrier_distance_3D']) for z in vals],'.-',label=k)
    b.plot(t,[float(z['barrier_curvature_q2_richardson']) for z in vals],'.-',label=k)
a.set(ylabel='Inter-lobe barrier d3',title='Original 11D replay | Barrier height and phase curvature')
a.axhline(.01,linestyle='--',alpha=.5,label='Historical 0.01 threshold')
b.set(xlabel='Ramp duration r (xi)',ylabel='d²(d3)/dq² at barrier maximum')
for z in (a,b):z.grid(alpha=.25);z.legend(fontsize=8)
fig.tight_layout();fig.savefig(out/'barrier_height_and_curvature.png',dpi=180);plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(12,5.2),sharex=True,sharey=True)
for ax,k in zip(axes,('original','autonomous')):
    vals=[z for z in P if z['kappa_kind']==k];
    ramps=sorted({float(z['ramp_duration_xi']) for z in vals});levels=sorted({float(z['threshold_d3']) for z in vals})
    Z=np.array([[int(next(z['components'] for z in vals if abs(float(z['ramp_duration_xi'])-r)<1e-8 and abs(float(z['threshold_d3'])-th)<1e-8)) for r in ramps] for th in levels])
    im=ax.imshow(Z,origin='lower',aspect='auto',interpolation='nearest',extent=[min(ramps),max(ramps),min(levels),max(levels)],vmin=1,vmax=2,cmap='viridis')
    ax.set(xlabel='Ramp duration r (xi)',title=f'{k} | Connected regions')
    ax.grid(alpha=.08)
axes[0].set_ylabel('Strict contact threshold')
cb=fig.colorbar(im,ax=axes,shrink=.8,ticks=[1,2]);cb.set_label('Component count (within 0.10 ≤ q ≤ 0.90)')
fig.subplots_adjust(top=.89,bottom=.15,left=.07,right=.90,wspace=.14)
fig.suptitle('Phase-locked contact-lobe persistence across thresholds')
fig.savefig(out/'contact_lobe_threshold_persistence.png',dpi=180);plt.close(fig)
fig,(a,b)=plt.subplots(2,1,figsize=(9.5,7.5),sharex=True)
for k in ('original','autonomous'):
    vals=sorted((r for r in B if r['kappa_kind']==k),key=lambda r:float(r['ramp_duration_xi']))
    t=[float(z['ramp_duration_xi']) for z in vals]
    a.plot(t,[float(z['barrier_full11d_distance']) for z in vals],'.-',label=k)
    b.plot(t,[float(z['barrier_energy_difference']) for z in vals],'.-',label=k)
a.set(ylabel='Full wrapped 11D state distance',title='The projected-lobe merger is not a material-state recurrence')
b.set(xlabel='Ramp duration r (xi)',ylabel='Return - forward mechanical energy')
for ax in (a,b):ax.grid(alpha=.25);ax.legend(fontsize=8)
fig.tight_layout();fig.savefig(out/'full_state_and_energy_separation.png',dpi=180);plt.close(fig)

G=rows('quadratic_gap_scaling_check.csv')
fig,ax=plt.subplots(figsize=(7.5,6.5))
for k,marker in [('original','o'),('autonomous','s')]:
    rr=[z for z in G if z['kappa_kind']==k]
    x=[float(z['quadratic_predicted_gap_q']) for z in rr]
    y=[float(z['observed_between_lobes_gap_q']) for z in rr]
    ax.scatter(x,y,marker=marker,label=k)
limit=max(max(float(z['observed_between_lobes_gap_q']) for z in G),max(float(z['quadratic_predicted_gap_q']) for z in G))*1.05
ax.plot([0,limit],[0,limit],linestyle='--',color='gray',label='Exact agreement')
ax.set(xlim=(0,limit),ylim=(0,limit),aspect='equal',
       xlabel='Gap predicted by quadratic barrier curvature [q]',
       ylabel='Gap measured from genuine IVP threshold roots [q]',
       title='Near-merger square-root gap law: local Taylor diagnostic')
ax.grid(alpha=.25);ax.legend();fig.tight_layout()
fig.savefig(out/'quadratic_barrier_gap_prediction.png',dpi=180);plt.close(fig)
print('Rendered 5 numerical figures strictly from verified Q550 CSV results')
