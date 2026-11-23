#!/usr/bin/env python3
"""Plots generated only from numerical audit CSV outputs."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
with (R/'results/phase_resolved_gauge_covariant_triad.csv').open() as f: rows=list(csv.DictReader(f))
series={}
for v in rows:series.setdefault((v['kappa_kind'],v['ramp_xi']),[]).append(v)
fig,ax=plt.subplots(figsize=(10,5.7))
for (kind,r),data in series.items():
 if float(r) not in (.327375,.33):continue
 x=[float(v['q']) for v in data]
 y=[100*float(v['cross_fraction']) for v in data]
 ax.plot(x,y,label=f'{kind}, r={float(r):.6f}')
ax.set(xlabel='Phase q',ylabel='Cross-subspace share of ||K||² [%]',title='Q550 v18.49r — Movement of the 6–7–8 subspace')
ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(R/'results/cross_subspace_share.png',dpi=155);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,5.7))
for (kind,r),data in series.items():
 if float(r) not in (.327375,.33):continue
 x=[float(v['q']) for v in data]
 y=[float(v['chi_comm_K68']) if v['chi_comm_K68']!='' else float('nan') for v in data]
 ax.plot(x,y,label=f'{kind}, r={float(r):.6f}')
ax.set(xlabel='Phase q',ylabel='Gauge-invariant normalized bracket alignment',title='Commutator–6–8 alignment (algebraically constrained to ±1)')
ax.legend(fontsize=8);ax.set_ylim(-1.15,1.15);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(R/'results/gauge_invariant_commutator_alignment.png',dpi=155);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,5.7))
for (kind,r),data in series.items():
 if float(r) not in (.327375,.33):continue
 x=[float(v['q']) for v in data]
 y=[float(v['cross_block_volume']) for v in data]
 ax.plot(x,y,label=f'{kind}, r={float(r):.6f}')
ax.set(xlabel='Phase q',ylabel='Product of three cross-block singular values',title='Cross-block coupling volume (nonnegative and gauge independent)')
ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(R/'results/cross_block_volume.png',dpi=155);plt.close(fig)
print('Plots saved',flush=True)

fig,ax=plt.subplots(figsize=(10,5.7))
for (kind,r),data in series.items():
 if float(r) not in (.327375,.33):continue
 x=[float(v['q']) for v in data]
 y=[float(v['relative_triad_rotation_deg']) for v in data]
 ax.plot(x,y,label=f'{kind}, r={float(r):.6f}')
ax.set(xlabel='Phase q',ylabel='Relative triad rotation from q=0.63 [degrees]',
       title='SO(3) relative triad orientation after cross-subspace parallel transport')
ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout()
fig.savefig(R/'results/phase_resolved_triad_orientation.png',dpi=155);plt.close(fig)
