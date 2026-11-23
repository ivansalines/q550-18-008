#!/usr/bin/env python3
"""Graphs regenerated from numerical Q550 output, without imposing an external clock."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path(__file__).resolve().parents[1]/'results'
def rows(n):
 p=R/n
 if not p.exists():return []
 with p.open() as f:return list(csv.DictReader(f))
def f(z,k):return float(z[k])
C=[z for z in rows('turning_event_continuation.csv') if z['shape']=='beta:2:2' and z['turn_xi']]
fig,axs=plt.subplots(1,2,figsize=(11.5,4.6))
for kind in sorted(set(z['kappa_kind'] for z in C)):
 a=sorted([z for z in C if z['kappa_kind']==kind],key=lambda z:f(z,'ramp_xi'))
 axs[0].plot([f(z,'ramp_xi') for z in a],[f(z,'turn_xi') for z in a],marker='o',label=f'{kind} turning')
 axs[1].plot([f(z,'ramp_xi') for z in a],[f(z,'turn_sigma') for z in a],marker='o',label=kind)
rr=np.linspace(min(f(z,'ramp_xi') for z in C),max(f(z,'ramp_xi') for z in C),101)
axs[0].plot(rr,rr/2,ls='--',color='grey',label='drive zero ξ=r/2')
axs[0].set(xlabel='Ramp duration r',ylabel='Model evolution coordinate ξ',title='Turning event versus prescribed drive zero')
axs[1].axhline(.5,ls='--',color='grey',label='drive zero')
axs[1].set(xlabel='Ramp duration r',ylabel='Normalized ramp coordinate σ',title='Moving event clock in the ramp')
for ax in axs:ax.grid(alpha=.18);ax.legend(fontsize=8)
fig.tight_layout();fig.savefig(R/'turning_event_two_clocks.png',dpi=165);plt.close(fig)
D=[z for z in rows('in_ramp_state_rate_curves.csv') if z['kappa_kind']=='original' and z['shape']=='beta:2:2']
fig,ax=plt.subplots(figsize=(9,5.4))
for r in sorted(set(f(z,'ramp_xi') for z in D)):
 z=[d for d in D if abs(f(d,'ramp_xi')-r)<1e-10]
 ax.plot([f(v,'xi') for v in z],[f(v,'x') for v in z],label=f'r={r:g}')
ax.set(xlabel='Model evolution coordinate ξ (not physical time)',ylabel='x',title='x turning under duration variation');ax.legend();ax.grid(alpha=.2)
fig.tight_layout();fig.savefig(R/'turning_x_curves_unfixed_clock.png',dpi=165);plt.close(fig)
P=rows('equal_projection_return_pairs.csv')
if P:
 fig,ax=plt.subplots(figsize=(9,5.4))
 for kind in sorted(set(z['kappa_kind'] for z in P)):
  z=[d for d in P if d['kappa_kind']==kind and d['triad_projector_frobenius_gap'] not in ('','None')]
  ax.scatter([f(d,'locus_3d_span_scaled_gap') for d in z],[f(d,'triad_projector_frobenius_gap') for d in z],
       s=42,alpha=.8,label=kind)
 ax.set(xlabel='Span-scaled full 3D locus gap',ylabel='Triad projector Frobenius gap',title='Equal projected x does not imply closed triad or locus')
 ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(R/'equal_x_posture_and_projector_gap.png',dpi=165);plt.close(fig)
 fig,ax=plt.subplots(figsize=(9,5.4))
 for kind in sorted(set(z['kappa_kind'] for z in P)):
  z=[d for d in P if d['kappa_kind']==kind]
  ax.scatter([f(d,'xi_in') for d in z],[f(d,'xi_out') for d in z],label=kind,s=37,alpha=.8)
 ax.set(xlabel='Earlier event coordinate ξin',ylabel='Later equal-x return ξout',title='Exact root-matched equal-projection passages')
 ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(R/'exact_equal_x_return_event_map.png',dpi=165);plt.close(fig)
print('FIGURES_DONE',flush=True)
