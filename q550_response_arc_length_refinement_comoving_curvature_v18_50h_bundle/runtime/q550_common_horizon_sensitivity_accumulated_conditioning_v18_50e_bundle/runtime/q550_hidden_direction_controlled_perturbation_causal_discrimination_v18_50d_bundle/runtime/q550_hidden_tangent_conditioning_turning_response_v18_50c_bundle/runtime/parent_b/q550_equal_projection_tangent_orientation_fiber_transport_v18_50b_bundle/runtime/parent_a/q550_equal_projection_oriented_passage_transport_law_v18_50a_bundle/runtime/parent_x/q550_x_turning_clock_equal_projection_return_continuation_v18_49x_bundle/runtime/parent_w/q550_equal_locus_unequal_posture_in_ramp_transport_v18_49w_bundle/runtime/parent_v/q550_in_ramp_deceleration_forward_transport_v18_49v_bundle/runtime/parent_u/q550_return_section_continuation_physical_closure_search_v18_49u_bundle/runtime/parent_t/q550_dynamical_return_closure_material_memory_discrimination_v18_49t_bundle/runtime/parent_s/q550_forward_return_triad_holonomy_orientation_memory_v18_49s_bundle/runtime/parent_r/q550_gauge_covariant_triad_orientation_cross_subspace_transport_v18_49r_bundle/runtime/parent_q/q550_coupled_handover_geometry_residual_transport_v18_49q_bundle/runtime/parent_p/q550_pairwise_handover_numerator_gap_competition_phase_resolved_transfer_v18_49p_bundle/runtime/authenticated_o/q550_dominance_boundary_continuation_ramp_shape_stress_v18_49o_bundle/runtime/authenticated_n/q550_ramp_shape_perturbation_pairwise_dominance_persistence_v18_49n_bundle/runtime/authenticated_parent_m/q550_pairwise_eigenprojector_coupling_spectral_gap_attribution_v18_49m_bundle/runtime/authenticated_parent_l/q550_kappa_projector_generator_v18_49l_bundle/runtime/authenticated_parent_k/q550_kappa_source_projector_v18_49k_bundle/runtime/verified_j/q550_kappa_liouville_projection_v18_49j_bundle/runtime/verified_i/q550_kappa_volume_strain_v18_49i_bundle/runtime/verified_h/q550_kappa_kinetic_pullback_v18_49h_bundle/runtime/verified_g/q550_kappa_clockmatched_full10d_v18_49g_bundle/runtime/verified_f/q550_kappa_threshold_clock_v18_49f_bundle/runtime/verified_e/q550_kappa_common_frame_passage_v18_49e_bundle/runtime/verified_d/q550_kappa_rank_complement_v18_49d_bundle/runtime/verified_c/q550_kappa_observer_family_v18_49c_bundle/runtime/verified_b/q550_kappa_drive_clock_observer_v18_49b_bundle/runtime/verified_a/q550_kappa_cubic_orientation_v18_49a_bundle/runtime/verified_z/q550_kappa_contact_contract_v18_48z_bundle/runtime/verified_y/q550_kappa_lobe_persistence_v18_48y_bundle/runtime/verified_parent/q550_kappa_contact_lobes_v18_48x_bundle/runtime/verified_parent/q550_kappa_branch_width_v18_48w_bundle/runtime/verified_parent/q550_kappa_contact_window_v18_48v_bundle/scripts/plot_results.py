#!/usr/bin/env python3
"""Plots from regenerated numerical CSV only (never synthetic curve samples)."""
import csv
from pathlib import Path
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'results'
def read(filename):
    with (R/filename).open(newline='') as f:return list(csv.DictReader(f))
contacts=read('fine_ramp_contacts.csv');fixed=read('fixed_phase_energy_history.csv')
fig,ax=plt.subplots(figsize=(9.7,5.8))
for family in sorted({r['family'] for r in contacts}):
    for kind in ('original','autonomous'):
        sub=[x for x in contacts if x['family']==family and x['kappa_kind']==kind and float(x['alpha'])==1.]
        rr=sorted({float(r['ramp_duration_xi']) for r in sub})
        vals=[float(np.median([float(r['minimum_3D_gap']) for r in sub if float(r['ramp_duration_xi'])==v])) for v in rr]
        ax.semilogy(rr,vals,marker='o',ms=3,lw=1.2,label=f'{family} / {kind}')
ax.set(xlabel='Smooth reversal ramp duration [xi]',ylabel='Median optimized geometric gap (3D)',
       title='Q550 v18.48v — Fine ramp scan, alpha = 1 (sampled durations)')
ax.grid(alpha=.23);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(R/'ramp_window_fine_scan.png',dpi=170);plt.close(fig)
fig,ax=plt.subplots(figsize=(9.7,5.8))
for family in sorted({r['family'] for r in contacts}):
    sub=[r for r in contacts if r['family']==family and r['alpha']=='1.0']
    rr=sorted({float(x['ramp_duration_xi']) for x in sub})
    med=[float(np.median([float(x['contact_total_q_0p01']) for x in sub if float(x['ramp_duration_xi'])==t])) for t in rr]
    ax.plot(rr,med,marker='o',ms=3,label=family)
ax.set(xlabel='Smooth reversal ramp duration [xi]',ylabel='Median phase width with shape gap < 0.01 [q]',
       title='Q550 v18.48v — Contact persistence is not just a minimum')
ax.legend();ax.grid(alpha=.23);fig.tight_layout();fig.savefig(R/'phase_contact_window_width.png',dpi=170);plt.close(fig)
fig,ax=plt.subplots(figsize=(9.7,5.8))
for q in (.35,.50,.65):
    sub=[x for x in fixed if x['alpha']=='1.0' and abs(float(x['common_phase_q'])-q)<1e-10]
    ramps=sorted({float(x['ramp_duration_xi']) for x in sub})
    e=[float(np.median([float(x['energy_gap']) for x in sub if float(x['ramp_duration_xi'])==r])) for r in ramps]
    ax.plot(ramps,e,marker='o',ms=3,label=f'fixed phase q={q}')
ax.axhline(0,lw=.9,color='gray');ax.grid(alpha=.23);ax.legend()
ax.set(xlabel='Smooth reversal ramp duration [xi]',ylabel='Median signed return-minus-forward model energy',
       title='Q550 v18.48v — Phase-locked energy history, alpha=1')
fig.tight_layout();fig.savefig(R/'fixed_phase_energy_history.png',dpi=170);plt.close(fig)
print('v18.48v plots regenerated from measured files')
